cmake_minimum_required(VERSION 3.12)
project(n3d_worx21_reference LANGUAGES CXX)
# WORX reconstructed .cpp/.hpp live ONLY in /worx; all other files in /other.
set(WORX_ROOT "${CMAKE_CURRENT_LIST_DIR}/../../worx")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
add_library(worx21_re STATIC "${WORX_ROOT}/src/compat.cpp")
target_include_directories(worx21_re PUBLIC "${WORX_ROOT}/include")
if(MSVC)
    target_compile_options(worx21_re PRIVATE /W4)
else()
    target_compile_options(worx21_re PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
enable_testing()
add_executable(worx21_tests tests/test_compat.cpp)
target_link_libraries(worx21_tests PRIVATE worx21_re)
add_test(NAME abi_and_opl_candidates COMMAND worx21_tests)
find_package(Python3 COMPONENTS Interpreter)
if(Python3_Interpreter_FOUND)
    add_test(NAME python_auditors COMMAND ${Python3_EXECUTABLE} -m unittest discover -s tests -p test_*.py)
    set_tests_properties(python_auditors PROPERTIES WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")
endif()

# v0.11: machine-backed, strict subset, NO simulated success for unknown AH.
target_sources(worx21_re PRIVATE "${WORX_ROOT}/src/int63_leaf.cpp")
add_executable(worx21_leaf_tests tests/test_int63_leaf.cpp)
target_link_libraries(worx21_leaf_tests PRIVATE worx21_re)
add_test(NAME int63_original_leaf_semantics COMMAND worx21_leaf_tests)

# v0.12: additionally audited AH 12/19/29/2E; DOS INT21 boundary explicitly injected.
add_executable(worx21_composed_tests tests/test_int63_composed.cpp)
target_link_libraries(worx21_composed_tests PRIVATE worx21_re)
add_test(NAME int63_original_composed_contracts COMMAND worx21_composed_tests)

# v0.12 exact instruction-derived INT08 entry/scheduling GATE only;
# 4476 parser, 40E7 engine, old IRQ08 handler remain explicit callbacks.
target_sources(worx21_re PRIVATE "${WORX_ROOT}/src/int08_gate.cpp")
add_executable(worx21_int08_gate_tests tests/test_int08_gate.cpp)
target_link_libraries(worx21_int08_gate_tests PRIVATE worx21_re)
add_test(NAME int08_original_gate_and_reentrancy COMMAND worx21_int08_gate_tests)

# v0.12: partial reconstruction of 40E7 private-stack audio scheduler
# content; PCM mixer / MIDI routines remain opaque contracts.
target_sources(worx21_re PRIVATE "${WORX_ROOT}/src/int08_audio.cpp")
add_executable(worx21_int08_audio_tests tests/test_int08_audio.cpp)
target_link_libraries(worx21_int08_audio_tests PRIVATE worx21_re)
add_test(NAME int08_original_audio_service_shell COMMAND worx21_int08_audio_tests)

# v0.13: byte-pinned WORX internal DMA, MIDI control/overflow and PCM arithmetic.
# These are bounded subcontracts; injected 44B3/5F17/actual IRQ hardware remains open.
target_sources(worx21_re PRIVATE "${WORX_ROOT}/src/audio_inner.cpp")
add_executable(worx21_audio_inner_tests tests/test_audio_inner.cpp)
target_link_libraries(worx21_audio_inner_tests PRIVATE worx21_re)
add_test(NAME audio_inner_original_machine_subcontracts COMMAND worx21_audio_inner_tests)

# v0.14: byte-pinned MIDI EOT / track delta gate, XMS far-service refill
# packet, streaming modes 08h and 0Ch.  All indirect callees are explicit.
target_sources(worx21_re PRIVATE "${WORX_ROOT}/src/audio_deep.cpp")
add_executable(worx21_audio_deep_tests tests/test_audio_deep.cpp)
target_link_libraries(worx21_audio_deep_tests PRIVATE worx21_re)
add_test(NAME audio_deep_v014_original_subcontracts COMMAND worx21_audio_deep_tests)

# v0.15: original-byte-pinned running-status + variable-length event pipeline
# and meta-event composition. The 3A4D remaining hardware backend is injected.
target_sources(worx21_re PRIVATE "${WORX_ROOT}/src/audio_events.cpp")
add_executable(worx21_audio_events_v015_tests tests/test_audio_events_v015.cpp)
target_link_libraries(worx21_audio_events_v015_tests PRIVATE worx21_re)
add_test(NAME audio_events_v015_original_machine_shell COMMAND worx21_audio_events_v015_tests)
