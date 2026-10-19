#pragma once

#include <array>
#include <cstdint>

namespace n3d::re::v049 {

constexpr std::uint32_t nextRngState(std::uint32_t state) noexcept {
    return state * 214013u + 2531011u;
}

constexpr std::uint16_t rng15(std::uint32_t stateAfter) noexcept {
    return static_cast<std::uint16_t>((stateAfter >> 16u) & 0x7FFFu);
}

struct RngWitness {
    std::uint8_t ordinal{};
    std::uint32_t before{};
    std::uint32_t after{};
    std::uint16_t result{};
    bool postObserved{};
};

inline constexpr RngWitness kRng11{11, 0xDF90722Bu, 0x1649B442u, 5705, true};
inline constexpr RngWitness kRng12{12, 0x1649B442u, 0x6DF109FDu, 28145, true};
inline constexpr RngWitness kRng15{15, 0xC1BBB05Fu, 0xA6E9C9A6u, 9961, true};
inline constexpr RngWitness kRng16{16, 0xA6E9C9A6u, 0x81EB59D1u, 491, true};
inline constexpr RngWitness kRng17Prediction{17, 0x81EB59D1u, 0x0BB31550u, 2995, false};

struct GuardDeathWitness {
    std::uint8_t guardIndex{};
    std::uint16_t hpBefore{};
    std::uint16_t hpAfter{};
    std::uint16_t damage{};
};

inline constexpr GuardDeathWitness kGuard41Death{41, 111, 0, 165};

struct Dos20TraceSummary {
    std::uint32_t instructions{};
    std::uint32_t vramEvents{};
    std::uint32_t vgaRegisterSnapshots{};
    std::uint32_t frameHashEvents{};
    std::uint16_t mainUpdateExecutions{};
    std::uint16_t conditionalTailCalls{};
    std::uint16_t schedulerRecords{};
    std::uint16_t dispatcherCalls{};
    std::uint16_t state7Dispatches{};
    std::uint16_t state8Dispatches{};
    std::uint32_t vramAddressMismatches{};
    std::uint32_t vramColorMismatches{};
};

inline constexpr Dos20TraceSummary kDos20E1M1Trace{
    3775835, 289190, 7315, 3, 12, 2, 33, 396, 372, 24, 0, 0
};

struct ProjectileLifecycleWitness {
    std::uint8_t stateAfterFire{};
    std::uint8_t stateAtImpact{};
    std::uint8_t stateAfterExpiry{};
    std::uint16_t x{};
    std::uint16_t yFirst{};
    std::uint16_t yImpact{};
    std::uint8_t ammoBefore{};
    std::uint8_t ammoAfter{};
};

inline constexpr ProjectileLifecycleWitness kDos20ControlledProjectile{
    1, 2, 0, 1440, 3596, 3263, 64, 63
};

constexpr std::uint16_t e2m10WaitQuotient(
    std::uint16_t word0,
    std::uint16_t word2,
    std::uint16_t divisor) noexcept {
    const auto lowProduct = static_cast<std::uint16_t>(
        static_cast<std::uint32_t>(word0) * static_cast<std::uint32_t>(word2));
    return divisor == 0 ? 0 : static_cast<std::uint16_t>(lowProduct / divisor);
}

inline constexpr bool kE2M10RepeatedOuterSchedulerBackedgeStatic = true;
inline constexpr bool kNaturalProjectileAbaObserved = false;

constexpr std::uint16_t win110PaletteCopyCount(bool reserveSystemPaletteEnds) noexcept {
    return reserveSystemPaletteEnds ? 236 : 256;
}

inline constexpr std::uint8_t kWin110SystemPaletteReserveAtEachEnd = 10;
inline constexpr bool kWin16GameWindowObservedInCurrentLab = false;
inline constexpr std::uint8_t kWin16BuildsTriedInCurrentLab = 5;

} // namespace n3d::re::v049
