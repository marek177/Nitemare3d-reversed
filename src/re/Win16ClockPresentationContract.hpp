#pragma once

#include <cstdint>

namespace n3d::re::win16::presentation {

// Bounded static contract, NOT a complete Windows 3.11/WinG emulator.
// Sources: Win16 1.0, 1.8 and 1.10 Ghidra C exports; see
// docs/WIN16_CLOCK_PRESENTATION_STATIC_AUDIT_20261019.md.
enum class Build : std::uint8_t { Win10, Win13, Win16, Win18, Win110 };
enum class ClockBackend : std::uint8_t { GetTickCount, TimeGetTime };

// Win16 NE logical addresses, recovered by cross-build static decompilation
// and pinned import-relocation evidence. These are not DOS real-mode CS values.
constexpr std::uint16_t clockBackendFlagOffset(Build build) noexcept {
    switch (build) {
        case Build::Win10:
        case Build::Win13: return 0x45F2;
        case Build::Win16: return 0x46A2;
        case Build::Win18:
        case Build::Win110: return 0x46B2;
    }
    return 0;
}

constexpr std::uint16_t timerInitializeEntry(Build build) noexcept {
    switch (build) {
        case Build::Win10: return 0xD43E;
        case Build::Win13: return 0xD44A;
        case Build::Win16:
        case Build::Win18: return 0xD5BE;
        case Build::Win110: return 0xD66C;
    }
    return 0;
}

constexpr std::uint16_t timerReadEntry(Build build) noexcept {
    switch (build) {
        case Build::Win10: return 0xD498;
        case Build::Win13: return 0xD4A4;
        case Build::Win16:
        case Build::Win18: return 0xD618;
        case Build::Win110: return 0xD6C6;
    }
    return 0;
}

constexpr std::uint16_t calibrationEntry(Build build) noexcept {
    switch (build) {
        case Build::Win10: return 0xD5A2;
        case Build::Win13: return 0xD5AE;
        case Build::Win16:
        case Build::Win18: return 0xD722;
        case Build::Win110: return 0xD7D0;
    }
    return 0;
}


// In v1.8 the local SS:[BP-2] read was independently checked against
// SHA-pinned original EXE bytes. In v1.10 the same FF 76 FE instruction,
// direct 0/1 callers and full function body were recovered from an earlier
// SHA-gated v0.61 Ghidra archive (see docs/WIN16_V110_TIMER_ARCHIVED_BYTE_CLOSURE_20261020.md).
// Today's local environment has NOT independently rehashed the v1.10 original.
// Never translate the historical uninitialized stack read into C++ undefined
// behavior. Distinguish archived ASM from fresh binary verification.
enum class TimerCleanupArgumentEvidence : std::uint8_t {
    OriginalBytesNotYetChecked,
    StackLocalBpMinus2NotInitialized,
    ArchivedWin110GhidraListingBpMinus2NotInitialized
};

constexpr TimerCleanupArgumentEvidence timerCleanupArgumentEvidence(
    Build build) noexcept {
    switch (build) {
        case Build::Win18:
            return TimerCleanupArgumentEvidence::StackLocalBpMinus2NotInitialized;
        case Build::Win110:
            return TimerCleanupArgumentEvidence::ArchivedWin110GhidraListingBpMinus2NotInitialized;
        default:
            return TimerCleanupArgumentEvidence::OriginalBytesNotYetChecked;
    }
}

// Exact direct caller offsets and imported cleanup calls in NE logical segment 3.
inline constexpr std::uint16_t kWin18TimerInitCaller = 0x0EE8;
inline constexpr std::uint16_t kWin18TimerEndCaller = 0x0F24;
inline constexpr std::uint16_t kWin18TimerEndImportedCall = 0xD610;
inline constexpr std::uint16_t kWin110TimerInitCaller = 0x0F34;
inline constexpr std::uint16_t kWin110TimerEndCaller = 0x0F70;
inline constexpr std::uint16_t kWin110TimerEndImportedCall = 0xD6BE;
inline constexpr std::uint16_t kWin110TimerEndLocalRead = 0xD6BB;

constexpr bool multimediaCapabilitiesSucceeded(std::uint16_t mmResult) noexcept {
    return mmResult == 0; // TIMERR_NOERROR, not timeBeginPeriod success
}

constexpr std::uint16_t requestedTimerPeriodMs(
    std::uint16_t minimumPeriodMs) noexcept {
    return minimumPeriodMs < 10 ? 10 : minimumPeriodMs;
}

constexpr ClockBackend backendFromStoredFlag(bool useMultimediaClock) noexcept {
    return useMultimediaClock ? ClockBackend::TimeGetTime
                              : ClockBackend::GetTickCount;
}

// These modes are parameter values passed to the original Win16 mode selector,
// not public SDL sizes and not a claim of runtime reachability in every state.
enum class ModeKind : std::uint8_t {
    Windowed,
    FullscreenDisplayDib,
    RestoreStoredWindowSize,
    Unknown
};

struct Mode {
    ModeKind kind;
    std::uint16_t width;
    std::uint16_t height;
};

constexpr Mode modeForSelector(Build build, std::uint16_t selector) noexcept {
    if (selector == 0) return {ModeKind::Windowed, 320, 200};
    if (selector == 1) return {ModeKind::Windowed, 640, 400};
    if (build == Build::Win110) {
        if (selector == 2) return {ModeKind::Windowed, 960, 600};
        if (selector == 3) return {ModeKind::FullscreenDisplayDib, 320, 200};
        if (selector == 4) return {ModeKind::RestoreStoredWindowSize, 0, 0};
    } else {
        if (selector == 2) return {ModeKind::FullscreenDisplayDib, 320, 200};
        if (selector == 3) return {ModeKind::RestoreStoredWindowSize, 0, 0};
    }
    return {ModeKind::Unknown, 0, 0};
}

// Native Win16 MFC Size x1/x2/x3 COMMAND IDs (Win16 1.10).
// DOS Mode (0x8005) and Alt+Enter (0x8016) use distinct dispatch paths.
constexpr int windowSizeSelectorFromMenuCommand(
    std::uint16_t commandId) noexcept {
    switch (commandId) {
        case 0x8003: return 0;
        case 0x8004: return 1;
        case 0x8017: return 2;
        default: return -1;
    }
}

// Original Win16 keyboard path interprets the high bit as key release:
// VK_MENU=0x12 writes ALT into modifier bit 0; VK_RETURN=0x0D key-down
// with ALT held requests an alternate presentation mode.
// This is a local static input contract, not proof of OS accelerator delivery.
struct AltEnterKeyTransition {
    bool altHeld;
    int requestedModeSelector; // -1 means no display-mode request
};

constexpr AltEnterKeyTransition altEnterKeyTransition(
    Build build, std::uint16_t virtualKey, std::uint16_t keyStateWord,
    bool altHeld, bool fullscreenActive) noexcept {
    const bool keyDown = (keyStateWord & 0x8000U) == 0U;
    if (virtualKey == 0x12U) return {keyDown, -1};
    if (virtualKey != 0x0DU || !keyDown || !altHeld)
        return {altHeld, -1};
    const int enterMode = (build == Build::Win110) ? 3 : 2;
    return {altHeld, fullscreenActive ? enterMode + 1 : enterMode};
}

// Callsite/callee split is important. In v1.0 the caller invokes calibration
// only with game screen=1, game state=1 and scheduler mode=0.
// In v1.8 and v1.10 the keyboard caller always invokes the routine after
// Alt+Enter, but the routine itself accepts scheduler modes 0, 1, or 3.
constexpr bool invokesCalibrationAfterAltEnter(
    Build build, std::uint16_t screenState,
    std::uint16_t gameState, std::uint16_t schedulerMode) noexcept {
    if (build != Build::Win10) return true;
    return screenState == 1U && gameState == 1U && schedulerMode == 0U;
}

constexpr bool performsCalibrationAfterAltEnter(
    Build build, std::uint16_t screenState,
    std::uint16_t gameState, std::uint16_t schedulerMode) noexcept {
    if (screenState != 1U || gameState != 1U) return false;
    if (build == Build::Win10) return schedulerMode == 0U;
    return schedulerMode == 0U || schedulerMode == 1U ||
           schedulerMode == 3U;
}

enum class WinGBlit : std::uint8_t { BitBlt, StretchBlt };

constexpr WinGBlit windowBlitForSize(
    std::uint16_t width, std::uint16_t height) noexcept {
    return (width == 320 && height == 200) ? WinGBlit::BitBlt
                                           : WinGBlit::StretchBlt;
}

constexpr std::uint8_t vgaDacComponent(std::uint8_t rgb8) noexcept {
    return static_cast<std::uint8_t>(rgb8 >> 2);
}

inline constexpr std::uint16_t kDisplayDibEnterFlags = 0x8200;
inline constexpr std::uint16_t kDisplayDibExitFlags = 0x4040;

} // namespace n3d::re::win16::presentation
