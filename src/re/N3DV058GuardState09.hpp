#pragma once
#include <cstdint>

namespace n3d::re::v058 {

struct State09Witness {
    std::uint8_t stateBefore;
    std::uint8_t stateAfter;
    std::uint8_t worldFlagsBefore;
    std::uint8_t worldFlagsAfter;
    std::uint8_t worldClass;
    std::uint32_t rngBefore;
    std::uint32_t rngAfter;
    std::uint16_t rngResult;
    std::uint8_t rngMod3;
    std::uint16_t cpuInstructions;
    std::uint32_t readEvents;
    std::uint32_t writeEvents;
    std::uint32_t allEvents;
};

inline constexpr State09Witness kGuard41State09{
    0x09,0x0A,0x0B,0x0B,0x0F,
    0xAEA69ED3u,0x12DBCE4Au,4827,0,
    4235,17665,12675,34575
};

constexpr std::uint32_t nextRngState(std::uint32_t s) noexcept {
    return s * 214013u + 2531011u;
}
constexpr std::uint16_t rng15(std::uint32_t s) noexcept {
    return static_cast<std::uint16_t>((s >> 16u) & 0x7FFFu);
}

inline constexpr bool kState0AAnd0BDispatchToCommonEpilogueDos12 = true;
inline constexpr bool kState0AAnd0BDispatchToCommonEpilogueDos20 = true;
inline constexpr bool kDos20NaturalGuard41State09Observed = false;
inline constexpr bool kCompleteDeathPoolCleanupClosed = false;

static_assert(nextRngState(kGuard41State09.rngBefore) == kGuard41State09.rngAfter);
static_assert(rng15(kGuard41State09.rngAfter) == kGuard41State09.rngResult);

} // namespace n3d::re::v058
