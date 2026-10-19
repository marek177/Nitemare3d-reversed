#pragma once

#include <cstdint>

namespace n3d::re::win16::presentation {

// Bounded static contract, NOT a complete Windows 3.11/WinG emulator.
// Sources: Win16 1.0, 1.8 and 1.10 Ghidra C exports; see
// docs/WIN16_CLOCK_PRESENTATION_STATIC_AUDIT_20261019.md.
enum class Build : std::uint8_t { Win10, Win18, Win110 };
enum class ClockBackend : std::uint8_t { GetTickCount, TimeGetTime };

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
