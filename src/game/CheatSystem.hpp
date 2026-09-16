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
    std::uint8_t benefitMask{};
};

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
    bool enemiesIgnorePlayer() const { return enabled(CheatMode::Omnificent); }
private:
    GameEdition edition_;
    std::array<bool, 4> flags_{};
    static std::size_t index(CheatMode mode) { return static_cast<std::size_t>(mode); }
};

} // namespace n3d
