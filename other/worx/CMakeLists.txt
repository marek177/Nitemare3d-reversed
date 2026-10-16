cmake_minimum_required(VERSION 3.16)
project(n3d_worx21_reference LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
# WORX source is deliberately isolated in /worx. Tests and docs in /other.
set(WORX_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../worx")
add_library(worx21_reference STATIC
    "${WORX_ROOT}/src/compat.cpp"
    "${WORX_ROOT}/src/int63_leaf.cpp"
    "${WORX_ROOT}/src/int08_gate.cpp"
    "${WORX_ROOT}/src/int08_audio.cpp"
    "${WORX_ROOT}/src/audio_inner.cpp")
target_include_directories(worx21_reference PUBLIC "${WORX_ROOT}/include")
include(CTest)
if(BUILD_TESTING)
    add_executable(worx21_audio_inner_test tests/test_audio_inner.cpp)
    target_link_libraries(worx21_audio_inner_test PRIVATE worx21_reference)
    add_test(NAME worx21_audio_inner COMMAND worx21_audio_inner_test)
endif()
