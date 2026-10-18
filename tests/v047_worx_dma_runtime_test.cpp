#include "re/N3DV047WorxDmaRuntime.hpp"
#include <cassert>
using namespace n3d::re::v047;
int main() {
    static_assert(activePlaybackStarted());
    static_assert(automaticStopClearsAndMasks());
    static_assert(kNaturalDmaStart.dspPort == 0x022C);
    static_assert(kNaturalDmaStart.dmaMode == 0x59);
    static_assert(kNaturalDmaStart.dmaOffset == 0xDB6E);
    static_assert(kNaturalDmaStart.dmaPage == 0x01);
    static_assert(kNaturalDmaStart.dmaCount == 0x0FFF);
    static_assert(kNaturalAutoStop.laterExplicitStopEnteredAfterClear);
    static_assert(!kActiveShutdownStopObserved);
    static_assert(!kAudibleWaveformParityObserved);
    return 0;
}
