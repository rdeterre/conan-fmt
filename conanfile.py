from conans import ConanFile, CMake, tools
import os


class FmtConan(ConanFile):
    name = "fmt"
    version = "3.0.1"
    license = "BSD"
    url = "https://github.com/memsharded/conan-fmt"
    build_policy = "missing"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "header_only": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "header_only=False", "fPIC=True"
    generators = "cmake"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def configure(self):
        if self.options.header_only:
            self.settings.clear()
            self.options.remove("shared")
            self.options.remove("fPIC")
        else:
            self.build_policy = None

    def source(self):
        tools.download("https://github.com/fmtlib/fmt/releases/download/{}/fmt-{}.zip".format(
            self.version, self.version), "fmt.zip")
        tools.unzip("fmt.zip")
        os.unlink("fmt.zip")
        os.rename("fmt-{}".format(self.version), "fmt")
        tools.replace_in_file("fmt/CMakeLists.txt",
                              "project(FMT)", """project(FMT)
        include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
        conan_basic_setup()""")

    def build(self):
        if self.options.header_only:
            return
        cmake = CMake(self.settings)
        flags = "-DBUILD_SHARED_LIBS=ON" if self.options.shared else ""
        flags += " -DFMT_TEST=OFF -DFMT_INSTALL=OFF -DFMT_DOCS=OFF"
        if self.settings.os != "Windows" and self.options.fPIC:
            flags += " -DCMAKE_POSITION_INDEPENDENT_CODE=TRUE"
        self.run('cmake fmt %s %s' % (cmake.command_line, flags))
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include/fmt", src="fmt/fmt")
        self.copy("*.h", dst="include/cppformat", src="cppformat")
        if self.options.header_only:
            self.copy("*.cc", dst="include/fmt", src="fmt/fmt")
        else:
            self.copy("*.lib", dst="lib", keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
            self.copy("*.so", dst="lib", keep_path=False)
            self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        if self.options.header_only:
            self.cpp_info.defines.append("FMT_HEADER_ONLY")
        else:
            self.cpp_info.libs.append("fmt")
