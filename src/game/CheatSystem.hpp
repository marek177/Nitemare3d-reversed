#pragma once

#include "game/GameEdition.hpp"

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d {

enum class CheatMode : std::uint8_t {
    Omniscient = 0,
    Omnipotent = 1,
    Omnificent = 2,
    Omnifarious = 3,
};

struct CheatDescriptor {
    CheatMode mode;
    std::string_view label;
    std::uint16_t originalDataOffset;
    std::uint8_t originalControlId;
    char originalStatusLetter;
};

struct CheatAffectedState {
    std::uint8_t health{};
    std::array<std::uint8_t, 3> weaponResources{};
    std::uint8_t magicEyePower{};
    std::uint8_t crystalBallPower{};
    std::uint8_t weaponMask{};
    std::uint8_t keyMask{};
    std::uint8_t idCardMask{};
    std::uint8_t pentagramMask{};
    std::uint8_t specialUseCharges{};
};

// CONFIG.SAV is exactly the contiguous 20-byte runtime block at 1048:4BD4.
// The four cheat bytes occupy the final four positions.
inline constexpr std::size_t kConfigSaveSize = 20;
inline constexpr std::size_t kConfigOmniscientOffset = 0x10;
inline constexpr std::size_t kConfigOmnipotentOffset = 0x11;
inline constexpr std::size_t kConfigOmnifariousOffset = 0x12;
inline constexpr std::size_t kConfigOmnificentOffset = 0x13;

inline constexpr std::uint8_t kGuardPassiveState = 0x07;
inline constexpr std::uint8_t kGuardMovingPassiveState = 0x08;
inline constexpr std::uint8_t kGuardWakeCountdownState = 0x01;
inline constexpr std::uint8_t kGuardActiveEntryState = 0x02;
inline constexpr std::uint8_t kOmnificentWakeCacheSize = 64;

struct AcceptedFireWakeProbe {
    std::uint8_t playerSelector{};
    std::uint8_t guardSelector{};
    std::uint8_t guardStrategy{};
    std::uint8_t guardState{};
    bool selectorAlreadyWoken{};
};

// FUN_1010_7664. This wake gate is independent of the Omnificent flag itself;
// it is the accepted-fire path that lets eligible passive guards leave states
// whose autonomous acquisition is otherwise suppressed by Omnificent.
constexpr bool acceptedFireWakesGuard(const AcceptedFireWakeProbe& p) noexcept {
    if (p.playerSelector == 0 || p.selectorAlreadyWoken) return false;
    if (p.guardStrategy != 0 || p.guardSelector != p.playerSelector) return false;
    return p.guardState == kGuardPassiveState ||
           p.guardState == kGuardMovingPassiveState;
}

constexpr std::uint16_t acceptedFireWakeDelay(std::uint16_t randomValue) noexcept {
    return static_cast<std::uint16_t>(randomValue % 8u);
}

class CheatSystem {
public:
    explicit CheatSystem(GameEdition edition) : edition_(edition) {}
    static const std::array<CheatDescriptor, 4>& descriptors();
    bool menuAvailable() const { return hasCompleteTrilogy(edition_); }
    static constexpr std::array<std::string_view, 3> lockedMessage() {
        return {
            "Cheat modes are only available",
            "when you purchase the complete",
            "trilogy.  Please see 'Instructions'",
        };
    }
    bool enabled(CheatMode mode) const;
    bool set(CheatMode mode, bool value);
    void clear();
    void applyLevelStart(CheatAffectedState& state) const;
    bool consumeWeaponResource(std::uint8_t& amount) const;
    void applyPlayerDamage(CheatAffectedState& state, std::uint8_t damage) const;
    void drainMappingPower(std::uint8_t& amount) const;

    // Exact Win16 1.10 Omnificent acquisition gates:
    // state 7 always suppresses autonomous LOS acquisition;
    // state 8 does so only on the branch whose saved/next state is 2.
    bool suppressesAutonomousGuardAcquisition(std::uint8_t guardState,
                                              std::uint8_t nextState) const {
        if (!enabled(CheatMode::Omnificent)) return false;
        return guardState == kGuardPassiveState ||
               (guardState == kGuardMovingPassiveState &&
                nextState == kGuardActiveEntryState);
    }

    bool omnificentEnabled() const { return enabled(CheatMode::Omnificent); }

    // Compatibility/UI predicate only. Do not use this as an AI decision:
    // already-active, scripted and accepted-fire-woken guards can still act.
    bool enemiesIgnorePlayer() const { return omnificentEnabled(); }
private:
    GameEdition edition_;
    std::array<bool, 4> flags_{};
    static std::size_t index(CheatMode mode) { return static_cast<std::size_t>(mode); }
};

} // namespace n3d
