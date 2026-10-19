#pragma once
#include <array>
#include <cstdint>

namespace n3d::re::v051 {

enum class Win16Build : std::uint8_t { V10, V13, V16, V18, V110 };

struct WingRuntimeWitness {
    Win16Build build;
    bool windowStarted;
    bool e1m1Rendered;
    bool localWingDllConflictRemoved;
};

inline constexpr std::array<WingRuntimeWitness,5> kBuilds{{
    {Win16Build::V10, true, true, false},
    {Win16Build::V13, true, true, false},
    {Win16Build::V16, true, true, false},
    {Win16Build::V18, true, true, false},
    {Win16Build::V110,true, true, true},
}};

constexpr bool allFiveReachE1M1() noexcept {
    for (const auto& b : kBuilds)
        if (!b.windowStarted || !b.e1m1Rendered)
            return false;
    return true;
}

inline constexpr bool kGameplayInputParityMeasured = false;
inline constexpr bool kTimingParityMeasured = false;
inline constexpr bool kPixelZeroDiffMeasured = false;
inline constexpr bool kAudibleAudioParityMeasured = false;

} // namespace n3d::re::v051
