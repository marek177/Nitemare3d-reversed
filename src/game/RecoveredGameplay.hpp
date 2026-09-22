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

// Direct runtime/save evidence. These correct older provisional 80/98-byte guesses.
inline constexpr std::uint16_t kRecoveredObjectStride = 28;
inline constexpr std::uint16_t kRecoveredGuardStride = 26;
inline constexpr std::uint16_t kRecoveredObjectCapacity = 350;
inline constexpr std::uint16_t kRecoveredGuardCapacity = 100;
inline constexpr std::uint16_t kRecoveredPlayerHalfExtent = 27;
inline constexpr std::uint16_t kRecoveredUseInputBit = 0x0200;
inline constexpr std::uint8_t kRecoveredPainState = 0x15;

} // namespace nitemare3d::game
