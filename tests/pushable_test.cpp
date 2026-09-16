#include "app/GameData.hpp"
#include "game/LevelState.hpp"

#include <cassert>
#include <filesystem>
#include <iostream>

int main(int argc, char** argv) {
    const std::filesystem::path root = argc > 1 ? argv[1] : "data/original";
    const auto data = n3d::GameData::loadEpisode(root, 1);
    auto world = n3d::LevelState::create(data.episode().maps.levels().at(5), data.episode().objects, data.episode().walls);
    assert(world.pushables().size() == 1);
    assert(world.at(42, 9).object == 0x18);
    assert(world.at(43, 9).object == 0x00);
    const bool started = world.beginPush(42, 9, 1, 0);
    assert(started);
    assert(world.pushables().front().ticksRemaining == 8);
    for (int i = 0; i < 8; ++i) world.tickPushables();
    assert(world.at(42, 9).object == 0x00);
    assert(world.at(43, 9).object == 0x18);
    assert(world.pushables().front().fixedX == 43 * 64 + 32);
    assert(world.pushables().front().fixedY == 9 * 64 + 32);
    assert(world.pushables().front().ticksRemaining == 0);
    std::cout << "pushable_test: PASS (E1L6 tombstone moved 42,9 -> 43,9 in 8 x 8/64-tile steps)\n";
    return 0;
}
