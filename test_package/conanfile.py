from conan import ConanFile
from conan.tools.layout import basic_layout


class Test(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        basic_layout(self)

    def test(self):
        mod = self.python_requires["bramz-conan-tools"].module
        props = mod.VSCodeCCppProperties(self)
        props.generate()
