#include "re/N3DV052Dos20RngTimer.hpp"
#include <cassert>
using namespace n3d::re::v052;

int main() {
    static_assert(nextRngState(kDos20Timer.rngBefore) == kDos20Timer.rngAfter);
    static_assert(rng15(kDos20Timer.rngAfter) == kDos20Timer.result);
    static_assert(randomCountdown(kDos20Timer.result) == kDos20Timer.countdownAfter);
    static_assert(kDos20Timer.phaseBefore == 1 && kDos20Timer.phaseAfter == 0);
    static_assert(kDos20Timer.countdownBefore == 0xFFFF);
    static_assert(kLongTrace.countdown0 == 201);
    static_assert(kLongTrace.countdown1 == 200);
    static_assert(kLongTrace.countdown2 == 199);
    static_assert(kLongTrace.tick3 - kLongTrace.tick0 == 3);
    static_assert(kTopLevelActorTraversalCallsite < kTopLevelRandomEffectsCallsite);
    static_assert(kRandomEffectsAfterActorTraversalInMeasuredOrder);
    static_assert(!kSeedInitializationWriterObservedInThisCapture);
    assert(kLongTrace.instructions == 805890);
    return 0;
}
