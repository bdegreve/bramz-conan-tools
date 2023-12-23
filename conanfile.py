from conan import ConanFile

from extensions.generators.vs_code_generator import VSCodeCCppProperties

__all__ = ["VSCodeCCppProperties"]


class BramzConanTools(ConanFile):
    name = "bramz-conan-tools"
    version = "1.0.0"
    package_type = "python-require"
    exports = "extensions/*"
