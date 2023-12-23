# bramz-conan-tools

Collection of extra utilities for [Conan](https://conan.io/).

## VSCodeCCppProperties Generator

Generates a configuration in [`.vscode/c_cpp_properties.json` configuration file](https://code.visualstudio.com/docs/cpp/c-cpp-properties-schema-reference)
for [Visual Studio Code](https://code.visualstudio.com/) with include paths of all
dependencies and other settings based on the Conan profile.

## How to Use?

To [install the extensions globally](https://docs.conan.io/2.0/reference/extensions/custom_generators.html#using-global-custom-generators), use following command:

```
conan config install https://github.com/bdegreve/bramz-conan-tools.git
```

Then you can use the generator in your recipe by name, or on the commandline:
```
conan install --requires=zlib/1.2.13 -g VSCodeCCppProperties
```