#pragma once

#include <cstdint>

namespace n3d::re::v019 {

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Open
};

enum class Axis : std::uint8_t {
    X,
    Y
};

enum class Difficulty : std::uint8_t {
    Easy,
    Medium,
    Hard
};

inline constexpr std::uint16_t kPlayerCollisionFootprint = 0x1B;
inline constexpr std::uint8_t kSecretPanelStepPerUpdate = 2;
inline constexpr std::uint8_t kAutomapDrainIntervalTicks = 16;
inline constexpr std::uint8_t kEnemyDetectorDrainIntervalTicks = 8;

inline constexpr Confidence kPlayerFootprintConfidence = Confidence::Confirmed;
inline constexpr Confidence kSecretPanelStepConfidence = Confidence::Confirmed;
inline constexpr Confidence kGuardBlockedFlipConfidence = Confidence::Confirmed;
inline constexpr Confidence kPlannerTimerConfidence = Confidence::Confirmed;
inline constexpr Confidence kExactSlidingOrderConfidence = Confidence::Open;
inline constexpr Confidence kExactSchedulerInterleaveConfidence = Confidence::Open;
inline constexpr Confidence kProjectilePoolFullAmmoConfidence = Confidence::Strong;

constexpr Axis blockedBothAxisToFlip(std::uint16_t rngResult) noexcept {
    // DOS v2.0 state-06 branch: bit0=1 flips X, bit0=0 flips Y.
    return (rngResult & 1u) != 0u ? Axis::X : Axis::Y;
}

constexpr std::uint8_t plannerBaseTimer(std::uint16_t rngResult) noexcept {
    return static_cast<std::uint8_t>((rngResult % 8u) + 8u);
}

constexpr std::uint8_t plannerTimer(std::uint16_t rngResult,
                                    Difficulty difficulty) noexcept {
    const auto base = plannerBaseTimer(rngResult);
    switch (difficulty) {
    case Difficulty::Easy:
        return static_cast<std::uint8_t>(base * 2u);
    case Difficulty::Hard:
        return static_cast<std::uint8_t>(base / 2u);
    case Difficulty::Medium:
    default:
        return base;
    }
}

constexpr std::uint8_t state13Timer(std::uint16_t rngResult) noexcept {
    return static_cast<std::uint8_t>((rngResult % 80u) + 8u);
}

std::int16_t retractCoordinateToward(std::int16_t firstEndpoint,
                                     std::int16_t secondEndpoint) noexcept;

}  // namespace n3d::re::v019
