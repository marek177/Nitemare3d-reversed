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
