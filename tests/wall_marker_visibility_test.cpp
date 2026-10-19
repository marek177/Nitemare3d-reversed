#include "game/LevelState.hpp"
#include "renderer/Raycaster.hpp"

#include <cassert>
#include <filesystem>
#include <fstream>

namespace {
n3d::LevelMap makeMap() {
    n3d::LevelMap map{};
    // A room enclosed by synthetic WALL 5, transparent floor 0xC0.
    for (auto& cell : map.cells) cell.wall = 5;
    for (int y = 2; y <= 8; ++y)
        for (int x = 2; x <= 9; ++x)
            map.cells[y * 64 + x].wall = 0xC0;
    map.cells[4 * 64 + 4].object = 2; // Player looks east.
    return map;
}
}

int main() {
    const auto path = std::filesystem::temp_directory_path() /
                      "n3d_preview_nonvisual_wall_markers.def";
    {
        std::ofstream f(path);
        f << "0005 5 solid WALL Normal wall\n"
          << "00c0 c0 NULL FLOOR Walkable floor\n"
          << "00e6 e6 NULL RETREAT AI retreat\n"
          << "00ee ee NULL TURN AI turn\n"
          << "00f0 f0 NULL FLEE AI flee\n"
          << "00f1 f1 NULL SAFESPOT Safe metadata\n";
        assert(f.good());
    }
    const auto defs = n3d::DefinitionTable::load(path);
    std::filesystem::remove(path);
    const auto plain = n3d::LevelState::create(makeMap(), {}, defs);
    assert(!plain.wallObscuresView(0xC0));
    assert(plain.wallObscuresView(5));
    assert(plain.wallObscuresView(0x77));  // Unknown IDs stay diagnostic.
    n3d::Framebuffer baseline(96, 64);
    n3d::Raycaster ray;
    ray.render(baseline, plain);
    for (auto marker : {0xE6, 0xEE, 0xF0, 0xF1}) {
        auto map = makeMap();
        map.cells[4 * 64 + 5].wall = static_cast<std::uint8_t>(marker);
        const auto world = n3d::LevelState::create(map, {}, defs);
        assert(!world.wallObscuresView(static_cast<std::uint8_t>(marker)));
        assert(!world.wallAllowsMovement(static_cast<std::uint8_t>(marker)));
        n3d::Framebuffer frame(96, 64);
        ray.render(frame, world);
        assert(frame.indices() == baseline.indices());
    }
    // Background fill: the empty field must keep the video-reference palette.
    n3d::LevelMap emptyMap{};
    for (auto& cell : emptyMap.cells) cell.wall = 0xC0;
    emptyMap.cells[4 * 64 + 4].object = 2;
    const auto emptyWorld = n3d::LevelState::create(emptyMap, {}, defs);
    n3d::Framebuffer emptyFrame(96, 64);
    ray.render(emptyFrame, emptyWorld);
    assert(emptyFrame.indices()[0] == 7);
    assert(emptyFrame.indices()[63 * 96] == 2);
    return 0;
}
