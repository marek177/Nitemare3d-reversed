#include "game/RemoteDoorRuntime.hpp"

#include <array>
#include <cassert>
#include <cstdint>

using namespace nitemare3d::game;

int main() {
    std::array<RemoteDoor, 6> doors{{
        {0x3B, 2, 1, 0}, {0x3C, 2, 3, 0}, {0x3B, 2, 0, 0},
        {0x3B, 3, 1, 0}, {0x33, 2, 1, 0}, {0x3C, 2, 4, 0},
    }};
    std::uint16_t bits = 0;
    auto open = applyRemoteDoorCommand(0x1E, 2, doors, bits);
    assert(open.selected == 2 && open.changed == 2);
    assert(open.openSounds == 2 && open.closeSounds == 0);
    assert(doors[0].state == 2 && doors[0].soundFlag == 1);
    assert(doors[1].state == 2 && doors[1].soundFlag == 1);
    assert(doors[2].state == 0 && doors[3].state == 1);
    assert(doors[4].state == 1 && doors[5].state == 4);
    assert(bits == 4 && open.groupBitToggled);

    auto close = applyRemoteDoorCommand(0x1F, 2, doors, bits);
    assert(close.selected == 3 && close.changed == 3 && close.closeSounds == 3);
    assert(doors[0].state == 3 && doors[0].soundFlag == 0);
    assert(doors[1].state == 3 && doors[2].state == 3);
    assert(bits == 0);

    // The command toggles the menu bit even when no eligible door exists.
    auto empty = applyRemoteDoorCommand(0x1E, 7, doors, bits);
    assert(empty.selected == 0 && empty.changed == 0 && bits == 0x80);

    // Global transition block leaves the caller's flag write in place.
    auto blocked = applyRemoteDoorCommand(0x1E, 2, doors, bits, true);
    assert(blocked.selected == 3 && blocked.changed == 0 && blocked.openSounds == 0);
    assert(doors[0].state == 3 && doors[0].soundFlag == 1);
    assert(bits == 0x84);

    auto invalid = applyRemoteDoorCommand(0x20, 2, doors, bits);
    assert(!invalid.groupBitToggled && bits == 0x84);
    invalid = applyRemoteDoorCommand(0x1E, 16, doors, bits);
    assert(!invalid.groupBitToggled && bits == 0x84);
}
