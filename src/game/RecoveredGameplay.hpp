#pragma once
#include <array>
#include <cstdint>

namespace nitemare3d::game {

// Verified score dispatch from original NITE3W.EXE: OBJECT class 0x08..0x20.
inline constexpr std::array<int,25> kRecoveredGuardScores = {
  25,75,50,100,250,150,200,100,100,0,150,150,200,-1000,1000,
  100,200,0,25,100,100,250,250,200,50
};
constexpr int recoveredGuardScore(std::uint8_t objectClass) noexcept {
  return objectClass >= 0x08 && objectClass <= 0x20
    ? kRecoveredGuardScores[objectClass - 0x08] : 0;
}

// Direct NITE3W.EXE/runtime/save evidence.
inline constexpr std::uint16_t kRecoveredObjectStride = 28;
inline constexpr std::uint16_t kRecoveredGuardStride = 26;
inline constexpr std::uint16_t kRecoveredObjectCapacity = 350;
inline constexpr std::uint16_t kRecoveredGuardCapacity = 100;
inline constexpr std::uint16_t kRecoveredPlayerHalfExtent = 27;
inline constexpr std::uint16_t kRecoveredUseInputBit = 0x0200;
inline constexpr std::uint8_t kRecoveredPainState = 0x15;
inline constexpr std::uint8_t kRecoveredGuardStateCount = 22;
inline constexpr std::uint8_t kRecoveredGuardInitialStrength = 255;
inline constexpr std::uint8_t kDraculaPhase1ObjectClass = 0x11;
inline constexpr std::uint8_t kDraculaBatPhase2ObjectClass = 0x14;

inline constexpr std::uint16_t kInputForward = 0x0002;
inline constexpr std::uint16_t kInputBackward = 0x0004;
inline constexpr std::uint16_t kInputTurnA = 0x0008;
inline constexpr std::uint16_t kInputTurnB = 0x0010;
inline constexpr std::uint16_t kInputFast = 0x0020;
inline constexpr std::uint16_t kInputFineStep = 0x0040;
inline constexpr std::uint16_t kInputFire = 0x0080;
inline constexpr std::uint16_t kInputStrafe = 0x0100;

inline constexpr std::uint16_t kMaxDoors = 64, kDoorStride = 22;
inline constexpr std::uint16_t kMaxPanels = 32, kPanelStride = 22;
inline constexpr std::uint16_t kMaxPushables = 12, kPushStride = 6;
inline constexpr std::uint16_t kMaxVectors = 1000, kVectorStride = 28;
inline constexpr std::uint16_t kMaxWallSpans = 50, kWallSpanStride = 20;
inline constexpr std::uint16_t kMaxProjectedSprites = 100, kProjectedSpriteStride = 18;

inline constexpr std::uint16_t kDemoHeaderBytes = 6;
inline constexpr std::uint16_t kDemoRecordBytes = 8;
inline constexpr std::uint16_t kNormalAmmoCap = 100;

} // namespace nitemare3d::game
