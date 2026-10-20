#pragma once

#include <cstdint>

namespace n3d::re::win16::timer {

// Exact *local* Win16 1.10 logic for NE3:D66C. This is a safe
// evidence model, not an emulator of arbitrary stack residue, Windows
// multimedia API timing, or the entire 16-bit execution environment.
inline constexpr std::uint16_t kTimerInitEntry = 0xD66C;
inline constexpr std::uint16_t kTimerInitDirectCaller = 0x0F34;
inline constexpr std::uint16_t kTimerCleanupDirectCaller = 0x0F70;
inline constexpr std::uint16_t kAudioInitCall = 0x0F2A;
inline constexpr std::uint16_t kTimerInitCall = 0x0F34;
inline constexpr std::uint16_t kAudioCleanupCall = 0x0F66;
inline constexpr std::uint16_t kTimerCleanupCall = 0x0F70;

// MMSYSTEM.604 returns zero for capability success. The original
// function writes DS:[46B2] from this result BEFORE MMSYSTEM.605.
// The later MMSYSTEM.605 return is ignored; a failure does not
// automatically switch the clock reader to GetTickCount.
struct InitPlan {
    bool multimediaClockFlag;
    bool callTimeBeginPeriod;
    std::uint16_t requestedPeriodMilliseconds;
    bool requestedPeriodIsValid;
    bool timeBeginPeriodReturnChecked;
};

constexpr InitPlan planInitialization(std::uint16_t timeGetDevCapsResult,
                                      std::uint16_t minimumPeriodMs) noexcept {
    const bool capabilitiesSucceeded = timeGetDevCapsResult == 0;
    return InitPlan{
        capabilitiesSucceeded,
        capabilitiesSucceeded,
        capabilitiesSucceeded
            ? (minimumPeriodMs < 10U ? static_cast<std::uint16_t>(10U)
                                      : minimumPeriodMs)
            : static_cast<std::uint16_t>(0U),
        capabilitiesSucceeded,
        false
    };
}

// In NE3:D66C(1), cleanup is gated by the stored flag only.
// It reads SS:[BP-2], which this invocation does not initialize;
// the original routine neither resets DS:[46B2] nor examines AX
// returned from MMSYSTEM.606. Never implement the uninitialized
// original read as host-language undefined behavior.
enum class CleanupOperand : std::uint8_t {
    UnknownResidualStackWordBpMinus2
};

struct CleanupPlan {
    bool callTimeEndPeriod;
    bool multimediaClockFlagAfter;
    bool timeEndPeriodReturnChecked;
    CleanupOperand argument;
};

constexpr CleanupPlan planCleanup(bool storedMultimediaClockFlag) noexcept {
    return CleanupPlan{
        storedMultimediaClockFlag,
        storedMultimediaClockFlag,
        false,
        CleanupOperand::UnknownResidualStackWordBpMinus2
    };
}

// Relative call order in original Ghidra NE3:0F14 and NE3:0F64.
// "Precedes" alone is not an execution proof for abnormal exits.
constexpr bool audioInitializationPrecedesTimerInitialization() noexcept {
    return kAudioInitCall < kTimerInitCall;
}

constexpr bool audioCleanupPrecedesTimerCleanup() noexcept {
    return kAudioCleanupCall < kTimerCleanupCall;
}

// Hypothetical repeated calls demonstrate the absence of local
// deactivation. This does NOT establish that user-visible gameplay
// naturally reenters the cleanup wrapper.
constexpr std::uint8_t locallyRequestedEndsIfCalledTwice(
    bool storedMultimediaClockFlag) noexcept {
    const auto first = planCleanup(storedMultimediaClockFlag);
    const auto second = planCleanup(first.multimediaClockFlagAfter);
    return static_cast<std::uint8_t>(
        (first.callTimeEndPeriod ? 1 : 0) +
        (second.callTimeEndPeriod ? 1 : 0));
}

} // namespace n3d::re::win16::timer
