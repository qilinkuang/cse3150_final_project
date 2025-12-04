cmake_minimum_required(VERSION 3.15)
project(bgp_simulator VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable optimizations for Release builds
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

# Enable Link-Time Optimization if available
include(CheckIPOSupported)
check_ipo_supported(RESULT ipo_supported OUTPUT ipo_error)
if(ipo_supported)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION_RELEASE TRUE)
endif()

# Find Python and pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development)

# Use pybind11's CMake helper to find it from Python packages
execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

find_package(pybind11 CONFIG REQUIRED HINTS "${pybind11_DIR}")

# Source files - UPDATED PATHS (removed src/ prefix)
set(SOURCES
    bgp_simulator/cpp/src/announcement.cpp
    bgp_simulator/cpp/src/as.cpp
    bgp_simulator/cpp/src/bgp.cpp
    bgp_simulator/cpp/src/rov.cpp
    bgp_simulator/cpp/src/simulator.cpp
)

# Create Python extension module - UPDATED PATH
pybind11_add_module(_core 
    bgp_simulator/cpp/main.cpp
    ${SOURCES}
)

# Include directories - UPDATED PATH (also fixed 'includes' -> 'include')
target_include_directories(_core PRIVATE
    bgp_simulator/cpp/include
)

# Install the module
install(
    TARGETS _core
    LIBRARY DESTINATION .
)