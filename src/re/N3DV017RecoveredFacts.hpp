#pragma once

#include "game/CombatSystem.hpp"
#include "game/GuardSystem.hpp"
#include "game/ObjectSystem.hpp"
#include "game/ProjectileRuntime.hpp"

#include <cstdint>

namespace n3d::re::v017 {

inline constexpr std::uint16_t kDosGetObjectKillScore = 0x84FE;
inline constexpr std::uint16_t kDosCalculateWeaponDamageAgainstObject = 0x8590;
inline constexpr std::uint16_t kDosDamageReceiverCluster = 0x87D8;

inline constexpr std::uint8_t kDraculaPhase1Class =
    nitemare3d::game::kDraculaPhase1Class;
inline constexpr std::uint8_t kDraculaPhase2Class =
    nitemare3d::game::kDraculaBatPhase2Class;

inline constexpr std::size_t kProjectileSlots =
    nitemare3d::game::kProjectilePoolCapacity;
inline constexpr std::size_t kProjectileStride =
    nitemare3d::game::kProjectileRecordStride;

} // namespace n3d::re::v017
