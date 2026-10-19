#pragma once
#include <cstdint>

namespace n3d::re::v050 {

constexpr std::uint32_t nextRngState(std::uint32_t state) noexcept {
    return state * 214013u + 2531011u;
}
constexpr std::uint16_t rng15(std::uint32_t stateAfter) noexcept {
    return static_cast<std::uint16_t>((stateAfter >> 16u) & 0x7FFFu);
}

struct DeathRngAttempt {
    std::uint8_t ordinal{};
    std::uint32_t before{};
    std::uint32_t after{};
    std::uint16_t result{};
    std::uint8_t mod7{};
    bool accepted{};
};

inline constexpr DeathRngAttempt kRng16{16,0xA6E9C9A6u,0x81EB59D1u,491,1,false};
inline constexpr DeathRngAttempt kRng17{17,0x81EB59D1u,0x0BB31550u,2995,6,false};
inline constexpr DeathRngAttempt kRng18{18,0x0BB31550u,0xAEA69ED3u,11942,0,true};

struct Guard41DeathOutcome {
    std::uint8_t guardIndex{};
    std::uint16_t hpBefore{};
    std::uint16_t hpAfter{};
    std::uint16_t scoreBefore{};
    std::uint16_t scoreAfter{};
    std::uint8_t mapMarkerBefore{};
    std::uint8_t mapMarkerAfter{};
    std::uint8_t stateBefore{};
    std::uint8_t stateAfter{};
    std::uint8_t nextStateBefore{};
    std::uint8_t nextStateAfter{};
    std::uint16_t timerBefore{};
    std::uint16_t timerAfter{};
};

inline constexpr Guard41DeathOutcome kGuard41{
    41,111,0,0,100,0xA5,0x00,0x06,0x00,0x05,0x09,2,3
};

struct TraceSummary {
    std::uint32_t cpuInstructions{};
    std::uint32_t memoryReads{};
    std::uint32_t memoryWrites{};
    std::uint32_t totalEvents{};
    bool userStop{};
};

inline constexpr TraceSummary kDeathTrace{3642,8198,867,12707,true};

} // namespace n3d::re::v050
