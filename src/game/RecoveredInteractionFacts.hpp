#pragma once
#include "game/InventoryRuntime.hpp"
#include <cstdint>

namespace nitemare3d::game {
// Observed in Win16 NITE3W.EXE 1.10; see docs/REMOTE_DOORS_AND_DOS_CROSSCHECK_2026-09-22.md.
// These helpers encode dispatch boundaries only. Door state transitions still
// require the original activation routine and are not represented here.
inline constexpr std::uint8_t kControlWallClass = 0x03;
inline constexpr std::uint8_t kControlObjectClass = 0x03;
inline constexpr std::uint8_t kDoorVerticalClass = 0x31;
inline constexpr std::uint8_t kDoorHorizontalClass = 0x32;
inline constexpr std::uint8_t kDoorLockedVerticalClass = 0x33;
inline constexpr std::uint8_t kDoorLockedHorizontalClass = 0x34;
inline constexpr std::uint8_t kDoorLockedVertical2Class = 0x35;
inline constexpr std::uint8_t kDoorLockedHorizontal2Class = 0x36;
inline constexpr std::uint8_t kDoorLockedVertical3Class = 0x37;
inline constexpr std::uint8_t kDoorLockedHorizontal3Class = 0x38;
inline constexpr std::uint8_t kTransportDoorVerticalClass = 0x39;
inline constexpr std::uint8_t kTransportDoorHorizontalClass = 0x3A;
inline constexpr std::uint8_t kRemoteDoorVerticalClass = 0x3B;
inline constexpr std::uint8_t kRemoteDoorHorizontalClass = 0x3C;
inline constexpr std::uint8_t kCurtainDoorVerticalClass = 0x3F;
inline constexpr std::uint8_t kCurtainDoorHorizontalClass = 0x40;
inline constexpr std::uint8_t kCancelAction = 0x19;
inline constexpr std::uint8_t kFloorSelectAction = 0x1A;
inline constexpr std::uint8_t kClimbUpAction = 0x1B;
inline constexpr std::uint8_t kClimbDownAction = 0x1C;
inline constexpr std::uint8_t kGoDownAction = 0x1D;
inline constexpr std::uint8_t kRemoteOpenCommand = 0x1E;
inline constexpr std::uint8_t kRemoteCloseCommand = 0x1F;
inline constexpr std::uint8_t kRemoteCannonEnableCommand = 0x20;
inline constexpr std::uint8_t kRemoteCannonDisableCommand = 0x21;
inline constexpr std::uint8_t kMovementScriptWallFlag = 0x40;
inline constexpr std::uint8_t kPortalPentagramMask = kAllPentagramsMask;
inline constexpr std::uint8_t kPortalEntryClass = 0x15;
inline constexpr std::uint8_t kPortalExitClass = 0x16;
inline constexpr std::uint8_t kExplodingWallRuntimeClass = 0x2D;
inline constexpr std::uint8_t kExplodingWallSound = 0x29;

inline constexpr std::uint8_t kSafeObjectClass = 0x26;
inline constexpr std::uint8_t kTrunkObjectClass = 0x27;
inline constexpr std::uint8_t kPushObjectClass = 0x28;
inline constexpr std::uint8_t kActionObjectClass = 0x29;
inline constexpr std::uint8_t kRadioObjectIdEpisode1 = 0x45;

enum class ContainerReward : std::uint8_t {
  Health = 2,
  Ammo = 3,
  MagicEye = 4,
  CrystalBall = 5,
  RedKey = 6,
  GreenKey = 7,
  BlueKey = 8,
  YellowKey = 9,
  RedIdCard = 10,
  YellowIdCard = 11,
};

constexpr std::uint8_t trunkRewardCode(std::uint8_t subtype) noexcept {
  return subtype <= 4 ? static_cast<std::uint8_t>(subtype + 2) : 0;
}
constexpr std::uint8_t safeRewardCode(std::uint8_t subtype) noexcept {
  return subtype <= 5 ? static_cast<std::uint8_t>(subtype + 6) : 0;
}
constexpr int climbActionRawWallDelta(std::uint8_t action) noexcept {
  return action == kClimbUpAction ? 1 :
         (action == kClimbDownAction || action == kGoDownAction ? -1 : 0);
}

constexpr bool isRemoteDoorClass(std::uint8_t c) noexcept {
  return c == kRemoteDoorVerticalClass || c == kRemoteDoorHorizontalClass;
}
constexpr bool isColoredKeyDoorClass(std::uint8_t c) noexcept {
  return c >= kDoorLockedVerticalClass && c <= kDoorLockedHorizontal3Class;
}
constexpr bool isIdCardDoorClass(std::uint8_t c) noexcept {
  return c == kTransportDoorVerticalClass || c == kTransportDoorHorizontalClass;
}
constexpr bool canOpenRemoteDoor(std::uint8_t state) noexcept {
  return state == 1 || state == 3;
}
constexpr bool canCloseRemoteDoor(std::uint8_t state) noexcept {
  return state == 0 || state == 2;
}
constexpr bool hasCard(std::uint16_t mask, std::uint8_t group) noexcept {
  return group < 16 && ((mask >> group) & 1u) != 0;
}
} // namespace nitemare3d::game
