#pragma once
#include <cstdint>

namespace n3d::re::v048 {

struct DemoHeaderWitness {
    std::uint16_t field0{};
    std::uint16_t field1{};
    std::uint16_t field2{};
};

struct DemoRecordWitness {
    std::uint16_t key{};
    std::uint16_t inputMask{};
    std::uint32_t counter{};
};

inline constexpr DemoHeaderWitness kDemo1Header{15,7,30};
inline constexpr DemoRecordWitness kDemo1FirstRecord{0x48E0,0x0002,8};
inline constexpr std::uint8_t kDemo1Episode = 1;
inline constexpr std::uint8_t kDemo1MapIndex = 10;
inline constexpr std::uint16_t kDemoModeLoading = 3;
inline constexpr std::uint16_t kDemoModePlayback = 4;

constexpr bool shouldApplyRecord(std::uint32_t renderCounter,
                                 std::uint32_t recordCounter) noexcept {
    return renderCounter >= recordCounter;
}

constexpr bool alternateDemoUpdateParity(std::uint32_t renderCounter) noexcept {
    return (renderCounter & 1u) != 0u;
}

constexpr std::uint32_t nextRngState(std::uint32_t state) noexcept {
    return state * 214013u + 2531011u;
}

constexpr std::uint16_t rng15(std::uint32_t stateAfter) noexcept {
    return static_cast<std::uint16_t>((stateAfter >> 16u) & 0x7FFFu);
}

constexpr std::uint32_t seedFromDemoStart(std::uint16_t seed) noexcept {
    return static_cast<std::uint32_t>(seed);
}

struct FirstMovementWitness {
    std::uint16_t angle{};
    std::uint16_t step{};
    std::uint16_t xBefore{};
    std::uint16_t yBefore{};
    std::uint16_t xAfter{};
    std::uint16_t yAfter{};
    std::uint16_t cellXBefore{};
    std::uint16_t cellYBefore{};
    std::uint16_t cellXAfter{};
    std::uint16_t cellYAfter{};
};

inline constexpr FirstMovementWitness kDemo1FirstMovement{
    90,15,1056,3168,1071,3168,16,49,16,49
};

struct SchedulerCheckpoint {
    std::uint16_t mode{};
    std::uint32_t renderCounter{};
    std::uint16_t updateArgument{};
};

inline constexpr SchedulerCheckpoint kMode3Checkpoint{3,1,1};
inline constexpr SchedulerCheckpoint kMode4Checkpoint{4,3,2};

} // namespace n3d::re::v048
