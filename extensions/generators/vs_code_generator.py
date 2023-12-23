# Copyright 2023 Bram de Greve
#
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of
#    conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list
#    of conditions and the following disclaimer in the documentation and/or other
#    materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be
#    used to endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

import json
import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import CppInfo


class VSCodeCCppProperties:
    name: str
    include_path: list[str]
    defines: list[str]
    compiler_args: list[str]
    cpp_standard: str
    intellisense_mode: str
    configuration_provider: str | None
    compile_commands: str | None

    def __init__(self, conanfile: ConanFile, *, cmake: bool = True):
        self._conanfile = conanfile

        self.name = f"conan-{str(conanfile.settings.build_type).lower()}"

        cpp_info = CppInfo(conanfile)
        cpp_info.merge(conanfile.cpp.source)
        cpp_info.set_relative_base_folder(conanfile.source_folder)
        cpp_info.merge(conanfile.cpp.build)
        cpp_info.set_relative_base_folder(conanfile.build_folder)
        deps = conanfile.dependencies.host.topological_sort
        for dep in reversed(deps.values()):
            cpp_info.merge(dep.cpp_info.aggregated_components())

        self.include_path = cpp_info.includedirs
        self.defines = cpp_info.defines
        self.compiler_args = cpp_info.cxxflags

        cppstd = conanfile.settings.get_safe("compiler.cppstd")
        self.cpp_standard = f"c++{cppstd.replace('gnu', '')}"

        os_ = str(conanfile.settings.os).lower()
        compiler = str(conanfile.settings.compiler).lower()
        if compiler == "visual studio":  # old compiler setting in Conan 1
            compiler = "msvc"
        arch = str(conanfile.settings.arch)
        if arch == "x86":
            pass
        elif arch == "x86_64":
            arch = "x64"
        elif arch.startswith("arm64"):
            arch = "arm64"
        elif match := re.match(r"armv(\d+)", arch):
            if int(match.group(1)) < 8:
                arch = "arm"
            else:
                arch = "arm64"
        else:
            raise ConanInvalidConfiguration(f"Unsupported architecture {arch}")
        self.intellisense_mode = f"{os_}-{compiler}-{arch}"

        if cmake:
            self.configuration_provider = "ms-vscode.cmake-tools"
            self.compile_commands = (
                os.path.join(conanfile.build_folder, "compile_commands.json")
                if compiler != "msvc"
                else None
            )
        else:
            self.configuration_provider = None
            self.compile_commands = None

    def generate(self):
        vscode_folder = os.path.join(self._conanfile.source_folder, ".vscode")
        c_cpp_properties = os.path.join(vscode_folder, "c_cpp_properties.json")

        try:
            with open(c_cpp_properties) as fp:
                data = json.load(fp)
        except FileNotFoundError:
            data = {
                "configurations": [],
                "version": 4,
            }

        configuration = {
            "name": self.name,
            "includePath": self.include_path,
            "defines": self.defines,
            "compilerArgs": self.compiler_args,
            "cppStandard": self.cpp_standard,
            "intelliSenseMode": self.intellisense_mode,
        }
        if self.configuration_provider:
            configuration["configurationProvider"] = self.configuration_provider
        if self.compile_commands:
            configuration["compileCommands"] = self.compile_commands

        for index, config in enumerate(data["configurations"]):
            if config["name"] == configuration["name"]:
                data["configurations"][index] = configuration
                break
        else:
            data["configurations"].append(configuration)

        os.makedirs(vscode_folder, exist_ok=True)
        with open(c_cpp_properties, "w") as fp:
            json.dump(data, fp, indent=2)
