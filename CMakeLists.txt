cmake_minimum_required(VERSION 3.24)
project(Nitemare3D_Reconstructed VERSION 0.12.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(N3D_ENABLE_SDL3 "Build the SDL3 runtime/viewer" ON)
option(N3D_FETCH_SDL3 "Fetch SDL3 automatically when not installed" OFF)

add_library(n3d_core
    src/formats/BinaryIO.cpp
    src/formats/DatArchive.cpp
    src/formats/DefinitionTable.cpp
    src/formats/DemoFile.cpp
    src/formats/FliFile.cpp
    src/formats/ImgArchive.cpp
    src/formats/MapArchive.cpp
    src/formats/Pcx8.cpp
    src/app/GameData.cpp
    src/game/LevelState.cpp
    src/game/CheatSystem.cpp
    src/game/HazardSystem.hpp
    src/ui/MenuModel.cpp
    src/ui/InstructionsData.cpp
    src/renderer/Framebuffer.cpp
    src/renderer/Raycaster.cpp
)

target_include_directories(n3d_core PUBLIC src)
target_compile_features(n3d_core PUBLIC cxx_std_20)

if(MSVC)
    target_compile_options(n3d_core PRIVATE /W4 /permissive-)
else()
    target_compile_options(n3d_core PRIVATE -Wall -Wextra -Wpedantic)
endif()

add_executable(n3d_inspect tools/n3d_inspect.cpp)
target_link_libraries(n3d_inspect PRIVATE n3d_core)

add_executable(n3d_pushable_test tests/pushable_test.cpp)
target_link_libraries(n3d_pushable_test PRIVATE n3d_core)

add_executable(n3d_menu_cheat_test tests/menu_cheat_test.cpp)
target_link_libraries(n3d_menu_cheat_test PRIVATE n3d_core)

add_executable(n3d_hazard_test tests/hazard_test.cpp)
target_link_libraries(n3d_hazard_test PRIVATE n3d_core)

add_executable(n3d_episode3_level_data_test tests/episode3_level_data_test.cpp)
target_link_libraries(n3d_episode3_level_data_test PRIVATE n3d_core)

add_executable(n3d_renderer_facts_test tests/renderer_facts_test.cpp)
target_link_libraries(n3d_renderer_facts_test PRIVATE n3d_core)

add_executable(n3d_win16_wall_raster_core_test tests/win16_wall_raster_core_test.cpp)
target_link_libraries(n3d_win16_wall_raster_core_test PRIVATE n3d_core)

add_executable(n3d_guard_facts_test tests/guard_facts_test.cpp)
target_link_libraries(n3d_guard_facts_test PRIVATE n3d_core)

add_executable(n3d_guard_save_block_test tests/guard_save_block_test.cpp)
target_link_libraries(n3d_guard_save_block_test PRIVATE n3d_core)

add_executable(n3d_object_runtime_facts_test tests/object_runtime_facts_test.cpp)
target_link_libraries(n3d_object_runtime_facts_test PRIVATE n3d_core)

add_executable(n3d_unknown_systems_audit_test tests/unknown_systems_audit_test.cpp)
target_link_libraries(n3d_unknown_systems_audit_test PRIVATE n3d_core)

add_executable(n3d_recovered_runtime_facts_test tests/recovered_runtime_facts_test.cpp)
target_link_libraries(n3d_recovered_runtime_facts_test PRIVATE n3d_core)

add_executable(n3d_projectile_runtime_test tests/projectile_runtime_test.cpp)
target_link_libraries(n3d_projectile_runtime_test PRIVATE n3d_core)

add_executable(n3d_runtime_layout_test tests/runtime_layout_test.cpp)
target_link_libraries(n3d_runtime_layout_test PRIVATE n3d_core)

add_executable(n3d_img_archive_layout_test tests/img_archive_layout_test.cpp)
target_link_libraries(n3d_img_archive_layout_test PRIVATE n3d_core)

add_executable(n3d_demo_file_test tests/demo_file_test.cpp)
target_link_libraries(n3d_demo_file_test PRIVATE n3d_core)

add_executable(n3d_win16_mfc_memory_test tests/win16_mfc_memory_test.cpp)
target_link_libraries(n3d_win16_mfc_memory_test PRIVATE n3d_core)

add_executable(n3d_win16_mfc_addresses_test tests/win16_mfc_addresses_test.cpp)
target_link_libraries(n3d_win16_mfc_addresses_test PRIVATE n3d_core)

add_executable(n3d_win16_mfc_coverage_test tests/win16_mfc_coverage_test.cpp)
target_link_libraries(n3d_win16_mfc_coverage_test PRIVATE n3d_core)

add_executable(n3d_handle_registry_test tests/handle_registry_test.cpp)
target_link_libraries(n3d_handle_registry_test PRIVATE n3d_core)

add_executable(n3d_native_handle_wrapper_test tests/native_handle_wrapper_test.cpp)
target_link_libraries(n3d_native_handle_wrapper_test PRIVATE n3d_core)

add_executable(n3d_window_wrapper_test tests/window_wrapper_test.cpp)
target_link_libraries(n3d_window_wrapper_test PRIVATE n3d_core)

add_executable(n3d_window_registry_test tests/window_registry_test.cpp)
target_link_libraries(n3d_window_registry_test PRIVATE n3d_core)

add_executable(n3d_runtime_safety_test tests/runtime_safety_test.cpp)
target_link_libraries(n3d_runtime_safety_test PRIVATE n3d_core)

add_executable(n3d_player_reconstruction_test tests/player_reconstruction_test.cpp)
target_link_libraries(n3d_player_reconstruction_test PRIVATE n3d_core)

add_executable(n3d_projectile_save_block_test tests/projectile_save_block_test.cpp)
target_link_libraries(n3d_projectile_save_block_test PRIVATE n3d_core)

add_executable(n3d_win16_recovered_facts_20260925_test tests/win16_recovered_facts_2026_09_25_test.cpp)
target_link_libraries(n3d_win16_recovered_facts_20260925_test PRIVATE n3d_core)

include(cmake/RegressionTests.cmake)

if(N3D_ENABLE_SDL3)
    find_package(SDL3 CONFIG QUIET)

    if(NOT SDL3_FOUND AND N3D_FETCH_SDL3)
        include(FetchContent)
        FetchContent_Declare(
            SDL3
            GIT_REPOSITORY https://github.com/libsdl-org/SDL.git
            GIT_TAG release-3.2.22
            GIT_SHALLOW TRUE
        )
        FetchContent_MakeAvailable(SDL3)
    endif()

    if(TARGET SDL3::SDL3)
        add_executable(nitemare3d
            src/main.cpp
            src/platform/sdl/SDLVideo.cpp
        )
        target_link_libraries(nitemare3d PRIVATE n3d_core SDL3::SDL3)
        target_compile_definitions(nitemare3d PRIVATE N3D_USE_SDL3=1)
    else()
        message(WARNING "SDL3 was not found. n3d_inspect will still be built. Install SDL3 or set N3D_FETCH_SDL3=ON to build nitemare3d.")
    endif()
endif()
