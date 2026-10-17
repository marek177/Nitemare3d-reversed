# Include after declaring this directory's test executables.
include(CTest)

# Original data is not distributed with this repository. Keep its integration
# test opt-in instead of registering a guaranteed failure on a clean checkout.
set(N3D_TEST_DATA_DIR "" CACHE PATH "Original episode data directory for n3d_pushable_test")
if(BUILD_TESTING AND N3D_TEST_DATA_DIR)
    get_filename_component(n3d_test_data_root "${N3D_TEST_DATA_DIR}" ABSOLUTE
                           BASE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
    if(NOT IS_DIRECTORY "${n3d_test_data_root}")
        message(FATAL_ERROR "N3D_TEST_DATA_DIR is not a directory: ${n3d_test_data_root}")
    endif()
endif()

get_property(n3d_directory_targets DIRECTORY PROPERTY BUILDSYSTEM_TARGETS)
foreach(n3d_test_target IN LISTS n3d_directory_targets)
    if(n3d_test_target MATCHES "^n3d_.*_test$")
        # Existing tests use assert(), including expressions with side effects.
        # Keep these checks active in Release/RelWithDebInfo as well as Debug.
        # This is test-target-only: n3d_core and the game keep their own flags.
        if(MSVC)
            target_compile_options(${n3d_test_target} PRIVATE /UNDEBUG)
        else()
            target_compile_options(${n3d_test_target} PRIVATE -UNDEBUG)
        endif()

        if(BUILD_TESTING)
            if(n3d_test_target STREQUAL "n3d_pushable_test")
                if(N3D_TEST_DATA_DIR)
                    add_test(NAME ${n3d_test_target}
                             COMMAND ${n3d_test_target} "${n3d_test_data_root}")
                    set_tests_properties(${n3d_test_target} PROPERTIES LABELS "original-data")
                else()
                    message(STATUS "n3d_pushable_test not registered: set N3D_TEST_DATA_DIR to enable it")
                endif()
            else()
                add_test(NAME ${n3d_test_target} COMMAND ${n3d_test_target})
                set_tests_properties(${n3d_test_target} PROPERTIES LABELS "reconstruction")
            endif()
        endif()
    endif()
endforeach()

# Evidence corpus checks run without proprietary EXEs. Supplying the original
# builds via N3D_WIN16_BINARIES also enables byte/fixup verification.
if(BUILD_TESTING)
    find_package(Python3 COMPONENTS Interpreter QUIET)
    if(Python3_Interpreter_FOUND)
        add_test(NAME n3d_win16_hidden_entry_v6_test
                 COMMAND "${Python3_EXECUTABLE}"
                         "${CMAKE_CURRENT_SOURCE_DIR}/tests/win16_hidden_entry_v6_test.py")
        set_tests_properties(n3d_win16_hidden_entry_v6_test PROPERTIES LABELS "reverse-engineering")
    else()
        message(STATUS "Win16 hidden-entry evidence test not registered: Python3 unavailable")
    endif()
endif()
