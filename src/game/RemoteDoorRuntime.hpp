#pragma once

#include "game/RecoveredInteractionFacts.hpp"

#include <cstddef>
#include <cstdint>
#include <span>

namespace nitemare3d::game {

// Logical view of the fields read by the Win16 remote-door command. The
// original 22-byte record and its object pointer are decoded elsewhere.
struct RemoteDoor {
    std::uint8_t objectClass{}; // runtime object +0x06
    std::uint8_t group{};       // runtime object +0x01
    std::uint16_t state{};      // door record +0x0C
    std::uint8_t soundFlag{};   // door record +0x14
};

struct RemoteDoorCommandResult {
    std::size_t selected{};
    std::size_t changed{};
    std::size_t openSounds{};  // request SFX 0x25
    std::size_t closeSounds{}; // request SFX 0x26
    bool groupBitToggled{};
};

// Reconstructs the record-level portion of Win16 FUN_1018_27de and
// FUN_1010_188a. A state change is conditional on the global 0x51AB blocker;
// the menu's group bit is toggled independently of how many doors moved.
inline RemoteDoorCommandResult applyRemoteDoorCommand(
    std::uint8_t command, std::uint8_t group, std::span<RemoteDoor> doors,
    std::uint16_t& menuGroupBits, bool transitionsBlocked = false) noexcept {
    RemoteDoorCommandResult result;
    if ((command != kRemoteOpenCommand && command != kRemoteCloseCommand) || group >= 16)
        return result;

    for (auto& door : doors) {
        if (!isRemoteDoorClass(door.objectClass) || door.group != group) continue;
        const bool selected = command == kRemoteOpenCommand
            ? (door.state == 1 || door.state == 3)
            : (door.state == 0 || door.state == 2);
        if (!selected) continue;
        ++result.selected;
        door.soundFlag = 1; // caller writes +0x14 before transition helper
        if (transitionsBlocked) continue; // 0x51AB blocks the helper

        if (command == kRemoteOpenCommand) {
            door.state = 2;
            ++result.openSounds;
            // The open path retains +0x14.
        } else {
            door.state = 3;
            ++result.closeSounds;
            door.soundFlag = 0; // cleared by the close path
        }
        ++result.changed;
    }
    menuGroupBits ^= static_cast<std::uint16_t>(1u << group);
    result.groupBitToggled = true;
    return result;
}

} // namespace nitemare3d::game
