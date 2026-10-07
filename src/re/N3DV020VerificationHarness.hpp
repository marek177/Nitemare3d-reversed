#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace n3d::re::v020 {

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Open
};

struct AddressAnchor {
    std::uint16_t offset;
    Confidence confidence;
};

inline constexpr AddressAnchor kIrq8{0xBCC2, Confidence::Confirmed};
inline constexpr AddressAnchor kClock{0xBE74, Confidence::Confirmed};
inline constexpr AddressAnchor kSlowBucket{0xBEB4, Confidence::Confirmed};
inline constexpr AddressAnchor kFrameBucket{0xBEF4, Confidence::Confirmed};
inline constexpr AddressAnchor kFastTick{0xC150, Confidence::Confirmed};
inline constexpr AddressAnchor kOuterScheduler{0xC1A8, Confidence::Confirmed};
inline constexpr AddressAnchor kMainUpdate{0xC0D8, Confidence::Confirmed};

// Candidate from the open-gaps audit. Do not treat as a closed scheduler identity.
inline constexpr AddressAnchor kObjectRuntimeCandidate{0x0E50, Confidence::Open};

inline constexpr std::array<std::uint16_t, 20> kDos20DirectRngCallsites = {
    0x2478, 0x525E, 0x5582, 0x5666, 0x56A6,
    0x573F, 0x58A7, 0x85AD, 0x887C, 0x9A68,
    0x9A77, 0x9C98, 0x9CC2, 0x9D6E, 0x9F0C,
    0x9F36, 0x9FE3, 0xA047, 0xA12B, 0xB276
};

struct RngTraceEntry {
    std::uint16_t caller;
    std::uint32_t stateBefore;
    std::uint32_t stateAfter;
    std::uint16_t result;
};

struct RngTraceValidation {
    bool callerKnown;
    bool stateTransitionValid;
    bool resultValid;

    constexpr bool valid() const noexcept {
        return callerKnown && stateTransitionValid && resultValid;
    }
};

constexpr std::uint32_t rngNextState(std::uint32_t state) noexcept {
    return state * UINT32_C(214013) + UINT32_C(2531011);
}

constexpr std::uint16_t rngResult(std::uint32_t stateAfter) noexcept {
    return static_cast<std::uint16_t>((stateAfter >> 16) & UINT32_C(0x7FFF));
}

constexpr bool isKnownDirectRngCallsite(std::uint16_t caller) noexcept {
    for (const auto value : kDos20DirectRngCallsites) {
        if (value == caller) {
            return true;
        }
    }
    return false;
}

constexpr RngTraceValidation validateRngTraceEntry(
    const RngTraceEntry& entry) noexcept {
    return {
        isKnownDirectRngCallsite(entry.caller),
        entry.stateAfter == rngNextState(entry.stateBefore),
        entry.result == rngResult(entry.stateAfter)
    };
}

enum class SchedulerEvent : std::uint8_t {
    Irq8,
    Clock,
    SlowBucket,
    FrameBucket,
    FastTick,
    MainUpdate,
    OuterScheduler,
    ObjectRuntimeCandidate,
    Unknown
};

constexpr SchedulerEvent classifySchedulerAddress(std::uint16_t offset) noexcept {
    switch (offset) {
    case 0xBCC2: return SchedulerEvent::Irq8;
    case 0xBE74: return SchedulerEvent::Clock;
    case 0xBEB4: return SchedulerEvent::SlowBucket;
    case 0xBEF4: return SchedulerEvent::FrameBucket;
    case 0xC150: return SchedulerEvent::FastTick;
    case 0xC0D8: return SchedulerEvent::MainUpdate;
    case 0xC1A8: return SchedulerEvent::OuterScheduler;
    case 0x0E50: return SchedulerEvent::ObjectRuntimeCandidate;
    default: return SchedulerEvent::Unknown;
    }
}

struct FirstDivergence {
    std::size_t index;
    std::uint16_t expected;
    std::uint16_t observed;
    bool found;
};

FirstDivergence firstDivergence(const std::uint16_t* expected,
                                std::size_t expectedCount,
                                const std::uint16_t* observed,
                                std::size_t observedCount) noexcept;

}  // namespace n3d::re::v020
