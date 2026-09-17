cmake_minimum_required(VERSION 3.24)
project(Nitemare3D_Reconstructed VERSION 0.9.0 LANGUAGES CXX)

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
