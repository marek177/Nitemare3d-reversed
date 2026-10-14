#include "formats/DefinitionTable.hpp"
#include "formats/MapArchive.hpp"
#include "game/LevelState.hpp"

#include <cassert>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <string>
#include <system_error>

namespace {

struct TemporaryDefinitions {
    std::filesystem::path directory;

    TemporaryDefinitions() {
        const auto stamp = std::chrono::steady_clock::now().time_since_epoch().count();
        directory = std::filesystem::temp_directory_path() /
                    ("n3d_push_blocked_" + std::to_string(stamp));
        std::filesystem::create_directories(directory);
        std::ofstream(directory / "objects.txt")
            << "01 START START START\n"
            << "18 PUSH PUSH PUSH\n"
            << "19 BLOCK BLOCK SOLID\n";
        std::ofstream(directory / "walls.txt")
            << "01 FLOOR FLOOR FLOOR\n"
            << "02 WALL WALL WALL\n";
    }
    ~TemporaryDefinitions() {
        std::error_code ignored;
        std::filesystem::remove_all(directory, ignored);
    }
    n3d::DefinitionTable objects() const {
        return n3d::DefinitionTable::load(directory / "objects.txt");
    }
    n3d::DefinitionTable walls() const {
        return n3d::DefinitionTable::load(directory / "walls.txt");
    }
};

n3d::LevelState makeWorld(const TemporaryDefinitions& defs) {
    n3d::LevelMap map{};
    for (auto& cell : map.cells) cell.wall = 1;
    map.cells[1 + 64].object = 1; // player start
    map.cells[10 + 10 * 64].object = 0x18;
    return n3d::LevelState::create(map, defs.objects(), defs.walls());
}

} // namespace

int main() {
    const TemporaryDefinitions defs;

    // A dynamic blocker arriving while a push is moving must not be overwritten.
    auto world = makeWorld(defs);
    assert(world.beginPush(10, 10, 1, 0));
    for (int tick = 0; tick < 3; ++tick) world.tickPushables();
    const auto previousX = world.pushables().front().fixedX;
    const auto previousRemaining = world.pushables().front().ticksRemaining;
    assert(previousRemaining == 5);
    world.at(11, 10).object = 0x19;
    world.tickPushables();
    assert(world.pushables().front().fixedX == previousX);
    assert(world.pushables().front().ticksRemaining == previousRemaining);
    assert(world.at(10, 10).object == 0x18);
    assert(world.at(11, 10).object == 0x19);

    world.at(11, 10).object = 0;
    for (int tick = 0; tick < 5; ++tick) world.tickPushables();
    assert(world.pushables().front().ticksRemaining == 0);
    assert(world.pushables().front().fixedX == 11 * 64 + 32);
    assert(world.at(10, 10).object == 0);
    assert(world.at(11, 10).object == 0x18);

    // Reopening a dynamically closed target restores the *same* 8-step push.
    auto wallWorld = makeWorld(defs);
    assert(wallWorld.beginPush(10, 10, 0, 1));
    wallWorld.at(10, 11).wall = 2;
    wallWorld.tickPushables();
    assert(wallWorld.pushables().front().ticksRemaining == 8);
    assert(wallWorld.pushables().front().fixedY == 10 * 64 + 32);
    wallWorld.at(10, 11).wall = 1;
    for (int tick = 0; tick < 8; ++tick) wallWorld.tickPushables();
    assert(wallWorld.at(10, 11).object == 0x18);
    assert(wallWorld.pushables().front().ticksRemaining == 0);

    // A same-ID foreign object is not permission to replace the target cell.
    auto sameIdWorld = makeWorld(defs);
    assert(sameIdWorld.beginPush(10, 10, 1, 0));
    sameIdWorld.at(11, 10).object = 0x18;
    sameIdWorld.tickPushables();
    assert(sameIdWorld.pushables().front().ticksRemaining == 8);
    assert(sameIdWorld.at(11, 10).object == 0x18);

    // If another event has removed the mapped PUSH object, do not resurrect it.
    auto removedWorld = makeWorld(defs);
    assert(removedWorld.beginPush(10, 10, 1, 0));
    removedWorld.at(10, 10).object = 0;
    removedWorld.tickPushables();
    assert(removedWorld.pushables().front().ticksRemaining == 8);
    assert(removedWorld.pushables().front().fixedX == 10 * 64 + 32);
    return 0;
}
