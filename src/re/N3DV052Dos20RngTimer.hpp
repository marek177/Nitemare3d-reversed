#pragma once
#include <cstdint>

namespace n3d::re::v052 {

constexpr std::uint32_t nextRngState(std::uint32_t state) noexcept {
    return state * 214013u + 2531011u;
}
constexpr std::uint16_t rng15(std::uint32_t stateAfter) noexcept {
    return static_cast<std::uint16_t>((stateAfter >> 16u) & 0x7FFFu);
}
constexpr std::uint16_t randomCountdown(std::uint16_t result) noexcept {
    return static_cast<std::uint16_t>(160u + (result % 240u));
}

struct TimerRngWitness {
    std::uint8_t phaseBefore{};
    std::uint8_t phaseAfter{};
    std::uint16_t countdownBefore{};
    std::uint16_t countdownAfter{};
    std::uint32_t rngBefore{};
    std::uint32_t rngAfter{};
    std::uint16_t result{};
};

inline constexpr TimerRngWitness kDos20Timer{
    1,0,0xFFFF,201,1u,0x0029E2C0u,41
};

struct LongTraceWitness {
    std::uint32_t instructions{};
    std::uint32_t memoryWrites{};
    std::uint16_t countdown0{};
    std::uint16_t countdown1{};
    std::uint16_t countdown2{};
    std::uint32_t tick0{};
    std::uint32_t tick3{};
};

inline constexpr LongTraceWitness kLongTrace{
    805890,181126,201,200,199,85,88
};

inline constexpr std::uint16_t kTopLevelRandomEffectsCallsite = 0x039E;
inline constexpr std::uint16_t kTopLevelActorTraversalCallsite = 0x037D;
inline constexpr bool kRandomEffectsAfterActorTraversalInMeasuredOrder = true;
inline constexpr bool kSeedInitializationWriterObservedInThisCapture = false;

} // namespace n3d::re::v052
