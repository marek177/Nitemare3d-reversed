#pragma once

#include <cstdint>

namespace nitemare3d::re {

// Consolidated runtime/global address map recovered from NITE3W.EXE.
// Only addresses with direct executable evidence are listed here.
// Semantic names remain conservative where full reader/writer behavior is not yet closed.

// Player position / state
inline constexpr std::uint16_t kPlayerX = 0x4BF6;
inline constexpr std::uint16_t kPlayerY = 0x4BF8;
inline constexpr std::uint16_t kOmnipotentFlag = 0x4BE5;

// Difficulty / weapon / ammo
inline constexpr std::uint16_t kDifficulty = 0x4C14;
inline constexpr std::uint16_t kSilverAmmo = 0x4C1F;
inline constexpr std::uint16_t kLaserAmmo = 0x4C20;
inline constexpr std::uint16_t kActiveWeapon = 0x4C23;
inline constexpr std::uint16_t kColoredKeyMask = 0x4C28;
inline constexpr std::uint16_t kIdCardMask = 0x4C29;
inline constexpr std::uint16_t kWeaponJamFlag = 0x4C2E;
inline constexpr std::uint16_t kWandAmmo = 0x4C44;
inline constexpr std::uint16_t kPentagramMask = 0x4C45;

// Runtime tables / counters
inline constexpr std::uint16_t kWallPropertyTable = 0x7E94;
inline constexpr std::uint16_t kGuardCount = 0x7E5E;
inline constexpr std::uint16_t kHamersteinGate = 0x7E52;
inline constexpr std::uint16_t kWallClassTable = 0x8196;

// Runtime record bases
inline constexpr std::uint16_t kDoorArray = 0x9DD6;
inline constexpr std::uint16_t kPanelArray = 0xA356;
inline constexpr std::uint16_t kPushArray = 0xA616;
inline constexpr std::uint16_t kGuardArray = 0x93AE;

// Record sizes / capacities verified from executable loops.
inline constexpr std::uint16_t kObjectRecordSize = 0x1C;
inline constexpr std::uint16_t kGuardRecordSize = 0x1A;
inline constexpr std::uint16_t kDoorRecordSize = 0x16;
inline constexpr std::uint16_t kPanelRecordSize = 0x16;
inline constexpr std::uint16_t kPushRecordSize = 0x06;

inline constexpr std::uint16_t kGuardCapacity = 100;
inline constexpr std::uint16_t kDoorCapacity = 64;
inline constexpr std::uint16_t kPanelCapacity = 32;
inline constexpr std::uint16_t kPushCapacity = 12;

} // namespace nitemare3d::re
