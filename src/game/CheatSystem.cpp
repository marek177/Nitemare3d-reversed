#include "game/CheatSystem.hpp"

#include <algorithm>

namespace n3d {

const std::array<CheatDescriptor, 4>& CheatSystem::descriptors() {
    static constexpr std::array<CheatDescriptor, 4> kDescriptors{{
        {CheatMode::Omniscient, "Omniscient (all-knowing)", 0x4BE4, 0x22, 'S'},
        {CheatMode::Omnipotent, "Omnipotent (all-powerful)", 0x4BE5, 0x23, 'P'},
        {CheatMode::Omnificent, "Omnificent (all-cunning)", 0x4BE7, 0x24, 'I'},
        {CheatMode::Omnifarious, "Omnifarious (all things)", 0x4BE6, 0x25, 'A'},
    }};
    return kDescriptors;
}

bool CheatSystem::enabled(CheatMode mode) const {
    return flags_.at(index(mode));
}

bool CheatSystem::set(CheatMode mode, bool value) {
    if (!menuAvailable()) {
        clear();
        return false;
    }
    flags_.at(index(mode)) = value;
    return true;
}

void CheatSystem::clear() {
    flags_.fill(false);
}

void CheatSystem::applyLevelStart(CheatAffectedState& state) const {
    if (enabled(CheatMode::Omniscient)) {
        state.magicEyePower = 100;
        state.crystalBallPower = 100;
    }
    if (enabled(CheatMode::Omnipotent)) {
        state.health = 100;
        state.weaponResources.fill(100);
        state.weaponMask = 0x0F;
    }
    if (enabled(CheatMode::Omnifarious)) {
        state.health = 100;
        state.weaponResources.fill(100);
        state.magicEyePower = 100;
        state.crystalBallPower = 100;
        state.weaponMask = 0x0F;
        state.keyMask = 0x0F;
        state.idCardMask = 0x03;
        state.benefitMask = 0x0F;
    }
}

bool CheatSystem::consumeWeaponResource(std::uint8_t& amount) const {
    if (enabled(CheatMode::Omnipotent)) return true;
    if (amount == 0) return false;
    --amount;
    return true;
}

void CheatSystem::applyPlayerDamage(CheatAffectedState& state, std::uint8_t damage) const {
    if (enabled(CheatMode::Omnipotent)) return;
    state.health = damage >= state.health ? 0 : static_cast<std::uint8_t>(state.health - damage);
}

void CheatSystem::drainMappingPower(std::uint8_t& amount) const {
    if (enabled(CheatMode::Omniscient)) return;
    if (amount != 0) --amount;
}

} // namespace n3d
