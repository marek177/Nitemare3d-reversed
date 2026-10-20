#include "re/Win16ClockPresentationContract.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::win16::presentation;

static_assert(multimediaCapabilitiesSucceeded(0));
static_assert(!multimediaCapabilitiesSucceeded(1));
static_assert(requestedTimerPeriodMs(1) == 10);
static_assert(requestedTimerPeriodMs(9) == 10);
static_assert(requestedTimerPeriodMs(10) == 10);
static_assert(requestedTimerPeriodMs(11) == 11);
static_assert(requestedTimerPeriodMs(100) == 100);
static_assert(backendFromStoredFlag(false) == ClockBackend::GetTickCount);
static_assert(backendFromStoredFlag(true) == ClockBackend::TimeGetTime);

static_assert(modeForSelector(Build::Win10, 0).width == 320);
static_assert(modeForSelector(Build::Win18, 1).height == 400);
static_assert(modeForSelector(Build::Win10, 2).kind ==
              ModeKind::FullscreenDisplayDib);
static_assert(modeForSelector(Build::Win18, 2).kind ==
              ModeKind::FullscreenDisplayDib);
static_assert(modeForSelector(Build::Win18, 3).kind ==
              ModeKind::RestoreStoredWindowSize);
static_assert(modeForSelector(Build::Win110, 2).kind == ModeKind::Windowed);
static_assert(modeForSelector(Build::Win110, 2).width == 960);
static_assert(modeForSelector(Build::Win110, 2).height == 600);
static_assert(modeForSelector(Build::Win110, 3).kind ==
              ModeKind::FullscreenDisplayDib);
static_assert(modeForSelector(Build::Win110, 4).kind ==
              ModeKind::RestoreStoredWindowSize);
static_assert(modeForSelector(Build::Win18, 4).kind == ModeKind::Unknown);
static_assert(modeForSelector(Build::Win110, 5).kind == ModeKind::Unknown);

static_assert(windowSizeSelectorFromMenuCommand(0x8003) == 0);
static_assert(windowSizeSelectorFromMenuCommand(0x8004) == 1);
static_assert(windowSizeSelectorFromMenuCommand(0x8017) == 2);
static_assert(windowSizeSelectorFromMenuCommand(0x8005) == -1);
static_assert(windowSizeSelectorFromMenuCommand(0x8016) == -1);

static_assert(windowBlitForSize(320, 200) == WinGBlit::BitBlt);
static_assert(windowBlitForSize(640, 400) == WinGBlit::StretchBlt);
static_assert(windowBlitForSize(960, 600) == WinGBlit::StretchBlt);
static_assert(windowBlitForSize(320, 201) == WinGBlit::StretchBlt);
static_assert(windowBlitForSize(319, 200) == WinGBlit::StretchBlt);
static_assert(vgaDacComponent(0) == 0);
static_assert(vgaDacComponent(3) == 0);
static_assert(vgaDacComponent(4) == 1);
static_assert(vgaDacComponent(255) == 63);
static_assert(kDisplayDibEnterFlags == 0x8200);
static_assert(kDisplayDibExitFlags == 0x4040);

// Keyboard/recalibration branches recovered from original Win16 C exports.
// VK_MENU uses 0x12, VK_RETURN uses 0x0d; key-state bit 15 marks key-up.
constexpr auto kAltKeyDown =
    altEnterKeyTransition(Build::Win110, 0x12, 0, false, false);
static_assert(kAltKeyDown.altHeld);
static_assert(kAltKeyDown.requestedModeSelector == -1);
constexpr auto kEnterWithAlt =
    altEnterKeyTransition(Build::Win110, 0x0D, 0, kAltKeyDown.altHeld, false);
static_assert(kEnterWithAlt.requestedModeSelector == 3);
static_assert(altEnterKeyTransition(Build::Win110, 0x0D, 0,
                                   true, true).requestedModeSelector == 4);
static_assert(altEnterKeyTransition(Build::Win10, 0x0D, 0,
                                   true, false).requestedModeSelector == 2);
static_assert(altEnterKeyTransition(Build::Win18, 0x0D, 0,
                                   true, true).requestedModeSelector == 3);
static_assert(altEnterKeyTransition(Build::Win110, 0x0D, 0x8000,
                                   true, false).requestedModeSelector == -1);
static_assert(altEnterKeyTransition(Build::Win110, 0x0D, 0,
                                   false, false).requestedModeSelector == -1);
static_assert(altEnterKeyTransition(Build::Win110, 0x12, 0x8000,
                                   true, false).altHeld == false);
static_assert(altEnterKeyTransition(Build::Win110, 0x20, 0,
                                   true, false).requestedModeSelector == -1);

// v1.0: call-site guard for scheduler mode 0 only.
// v1.8/v1.10: unconditional call, then internal guard for modes 0/1/3.
static_assert(invokesCalibrationAfterAltEnter(Build::Win10, 1, 1, 0));
static_assert(!invokesCalibrationAfterAltEnter(Build::Win10, 1, 1, 1));
static_assert(!invokesCalibrationAfterAltEnter(Build::Win10, 10, 1, 0));
static_assert(invokesCalibrationAfterAltEnter(Build::Win18, 10, 0, 2));
static_assert(invokesCalibrationAfterAltEnter(Build::Win110, 10, 0, 2));
static_assert(performsCalibrationAfterAltEnter(Build::Win10, 1, 1, 0));
static_assert(!performsCalibrationAfterAltEnter(Build::Win10, 1, 1, 1));
static_assert(!performsCalibrationAfterAltEnter(Build::Win10, 1, 1, 3));
static_assert(performsCalibrationAfterAltEnter(Build::Win18, 1, 1, 1));
static_assert(performsCalibrationAfterAltEnter(Build::Win18, 1, 1, 3));
static_assert(performsCalibrationAfterAltEnter(Build::Win110, 1, 1, 1));
static_assert(performsCalibrationAfterAltEnter(Build::Win110, 1, 1, 3));
static_assert(!performsCalibrationAfterAltEnter(Build::Win110, 1, 1, 2));
static_assert(!performsCalibrationAfterAltEnter(Build::Win110, 10, 1, 0));
static_assert(!performsCalibrationAfterAltEnter(Build::Win110, 1, 0, 0));

// Complete five-build Win16 timer and presentation selector matrix.
static_assert(clockBackendFlagOffset(Build::Win10) == 0x45F2);
static_assert(clockBackendFlagOffset(Build::Win13) == 0x45F2);
static_assert(clockBackendFlagOffset(Build::Win16) == 0x46A2);
static_assert(clockBackendFlagOffset(Build::Win18) == 0x46B2);
static_assert(clockBackendFlagOffset(Build::Win110) == 0x46B2);
static_assert(timerInitializeEntry(Build::Win10) == 0xD43E);
static_assert(timerInitializeEntry(Build::Win13) == 0xD44A);
static_assert(timerInitializeEntry(Build::Win16) == 0xD5BE);
static_assert(timerInitializeEntry(Build::Win18) == 0xD5BE);
static_assert(timerInitializeEntry(Build::Win110) == 0xD66C);
static_assert(timerReadEntry(Build::Win10) == 0xD498);
static_assert(timerReadEntry(Build::Win13) == 0xD4A4);
static_assert(timerReadEntry(Build::Win16) == 0xD618);
static_assert(timerReadEntry(Build::Win18) == 0xD618);
static_assert(timerReadEntry(Build::Win110) == 0xD6C6);
static_assert(calibrationEntry(Build::Win10) == 0xD5A2);
static_assert(calibrationEntry(Build::Win13) == 0xD5AE);
static_assert(calibrationEntry(Build::Win16) == 0xD722);
static_assert(calibrationEntry(Build::Win18) == 0xD722);
static_assert(calibrationEntry(Build::Win110) == 0xD7D0);
static_assert(modeForSelector(Build::Win13, 2).kind ==
              ModeKind::FullscreenDisplayDib);
static_assert(modeForSelector(Build::Win16, 2).kind ==
              ModeKind::FullscreenDisplayDib);
static_assert(modeForSelector(Build::Win13, 3).kind ==
              ModeKind::RestoreStoredWindowSize);
static_assert(modeForSelector(Build::Win16, 3).kind ==
              ModeKind::RestoreStoredWindowSize);
static_assert(altEnterKeyTransition(Build::Win13, 0x0D, 0,
                                   true, false).requestedModeSelector == 2);
static_assert(altEnterKeyTransition(Build::Win16, 0x0D, 0,
                                   true, false).requestedModeSelector == 2);
static_assert(invokesCalibrationAfterAltEnter(Build::Win13, 5, 0, 2));
static_assert(invokesCalibrationAfterAltEnter(Build::Win16, 5, 0, 2));
static_assert(performsCalibrationAfterAltEnter(Build::Win13, 1, 1, 3));
static_assert(performsCalibrationAfterAltEnter(Build::Win16, 1, 1, 1));
static_assert(!performsCalibrationAfterAltEnter(Build::Win13, 1, 1, 2));
static_assert(!performsCalibrationAfterAltEnter(Build::Win16, 0, 1, 3));

// SHA-pinned Win16 v1.8 original-instruction proof, distinct from inferred
// decompiler semantics for the remaining Windows releases.
static_assert(timerCleanupArgumentEvidence(Build::Win18) ==
              TimerCleanupArgumentEvidence::StackLocalBpMinus2NotInitialized);
static_assert(timerCleanupArgumentEvidence(Build::Win10) ==
              TimerCleanupArgumentEvidence::OriginalBytesNotYetChecked);
static_assert(timerCleanupArgumentEvidence(Build::Win13) ==
              TimerCleanupArgumentEvidence::OriginalBytesNotYetChecked);
static_assert(timerCleanupArgumentEvidence(Build::Win16) ==
              TimerCleanupArgumentEvidence::OriginalBytesNotYetChecked);
static_assert(timerCleanupArgumentEvidence(Build::Win110) ==
              TimerCleanupArgumentEvidence::ArchivedWin110GhidraListingBpMinus2NotInitialized);
static_assert(kWin110TimerInitCaller == 0x0F34);
static_assert(kWin110TimerEndCaller == 0x0F70);
static_assert(kWin110TimerEndImportedCall == 0xD6BE);
static_assert(kWin110TimerEndLocalRead == 0xD6BB);
static_assert(kWin110TimerEndImportedCall - kWin18TimerEndImportedCall == 0xAE);
static_assert(kWin18TimerInitCaller == 0x0EE8);
static_assert(kWin18TimerEndCaller == 0x0F24);
static_assert(kWin18TimerEndImportedCall == 0xD610);

int main() {
    for (std::uint16_t w = 319; w <= 321; ++w) {
        for (std::uint16_t h = 199; h <= 201; ++h) {
            assert((windowBlitForSize(w, h) == WinGBlit::BitBlt) ==
                   (w == 320 && h == 200));
        }
    }
    for (int component = 0; component < 256; ++component) {
        assert(vgaDacComponent(static_cast<std::uint8_t>(component)) ==
               static_cast<std::uint8_t>(component / 4));
    }
    return 0;
}
