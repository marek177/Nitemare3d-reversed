#pragma once
#include <cstdint>

namespace nitemare3d::game {
// Observed in Win16 NITE3W.EXE 1.10; see docs/REMOTE_DOORS_AND_DOS_CROSSCHECK_2026-09-22.md.
// These helpers encode dispatch boundaries only. Door state transitions still
// require the original activation routine and are not represented here.
inline constexpr std::uint8_t kControlWallClass = 0x03;
inline constexpr std::uint8_t kControlObjectClass = 0x03;
inline constexpr std::uint8_t kRemoteDoorVerticalClass = 0x3B;
inline constexpr std::uint8_t kRemoteDoorHorizontalClass = 0x3C;
inline constexpr std::uint8_t kRemoteOpenCommand = 0x1E;
inline constexpr std::uint8_t kRemoteCloseCommand = 0x1F;
inline constexpr std::uint8_t kMovementScriptWallFlag = 0x40;
inline constexpr std::uint8_t kPortalPentagramMask = 0x0F;
inline constexpr std::uint8_t kPortalEntryClass = 0x15;
inline constexpr std::uint8_t kPortalExitClass = 0x16;
inline constexpr std::uint8_t kExplodingWallRuntimeClass = 0x2D;
inline constexpr std::uint8_t kExplodingWallSound = 0x29;

constexpr bool isRemoteDoorClass(std::uint8_t c) noexcept {
  return c == kRemoteDoorVerticalClass || c == kRemoteDoorHorizontalClass;
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
constexpr bool hasAllPentagrams(std::uint8_t mask) noexcept {
  return (mask & kPortalPentagramMask) == kPortalPentagramMask;
}
} // namespace nitemare3d::game
