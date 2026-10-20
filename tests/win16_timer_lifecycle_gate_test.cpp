#include "re/Win16TimerLifecycleGate.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::win16::timer;

// Original DGROUP initial values + one-shot global initializer 3:0E9E.
static_assert(kGlobalInitOneShotFlagOffset == 0x00A2);
static_assert(kClockBackendFlagOffset == 0x46B2);
static_assert(kInitialClockFlagClearWriter == 0x0ED6);
static_assert(kCapsResultClockFlagWriter == 0xD691);
static_assert(kResetRoutineCallFromStartup == 0x1129);
static_assert(kOriginalInitialOneShotFlag == 1);
static_assert(kOriginalInitialClockFlag == 0);
static_assert(planGlobalClockReset(1, true).explicitlyResetMultimediaClockFlag);
static_assert(planGlobalClockReset(1, true).multimediaClockFlagAfter == false);
static_assert(planGlobalClockReset(1, true).oneShotFlagAfter == 0);
static_assert(planGlobalClockReset(0, true).multimediaClockFlagAfter == true);
static_assert(!planGlobalClockReset(0, true).explicitlyResetMultimediaClockFlag);
static_assert(!planGlobalClockReset(0, false).multimediaClockFlagAfter);

// Startup sequence: one-time reset -> audio init -> timeGetDevCaps.
constexpr auto kReset = planGlobalClockReset(kOriginalInitialOneShotFlag, true);
static_assert(!kReset.multimediaClockFlagAfter);
constexpr auto kCapsSucceeded = planInitialization(0, 4);
static_assert(kCapsSucceeded.multimediaClockFlag);
static_assert(kCapsSucceeded.callTimeBeginPeriod);
// If audio init fails before timeGetDevCaps and no other flag writer runs,
// a cleanup request skips multimedia timeEndPeriod.
static_assert(!planCleanup(kReset.multimediaClockFlagAfter).callTimeEndPeriod);

static_assert(kTimerInitEntry == 0xD66C);
static_assert(kTimerInitDirectCaller == 0x0F34);
static_assert(kTimerCleanupDirectCaller == 0x0F70);
static_assert(audioInitializationPrecedesTimerInitialization());
static_assert(audioCleanupPrecedesTimerCleanup());

static_assert(!planInitialization(1, 0).multimediaClockFlag);
static_assert(!planInitialization(1, 0).callTimeBeginPeriod);
static_assert(!planInitialization(1, 0).requestedPeriodIsValid);
static_assert(planInitialization(1, 0).requestedPeriodMilliseconds == 0);

static_assert(planInitialization(0, 0).multimediaClockFlag);
static_assert(planInitialization(0, 0).callTimeBeginPeriod);
static_assert(planInitialization(0, 0).requestedPeriodMilliseconds == 10);
static_assert(planInitialization(0, 9).requestedPeriodMilliseconds == 10);
static_assert(planInitialization(0, 10).requestedPeriodMilliseconds == 10);
static_assert(planInitialization(0, 11).requestedPeriodMilliseconds == 11);
static_assert(planInitialization(0, 0xFFFF).requestedPeriodMilliseconds == 0xFFFF);
static_assert(!planInitialization(0, 10).timeBeginPeriodReturnChecked);

static_assert(!planCleanup(false).callTimeEndPeriod);
static_assert(!planCleanup(false).multimediaClockFlagAfter);
static_assert(planCleanup(true).callTimeEndPeriod);
static_assert(planCleanup(true).multimediaClockFlagAfter);
static_assert(!planCleanup(true).timeEndPeriodReturnChecked);
static_assert(planCleanup(true).argument ==
              CleanupOperand::UnknownResidualStackWordBpMinus2);

// If the original state is not cleared, two hypothetical cleanup entries
// request two API calls. These tests do NOT show either is reachable twice.
static_assert(locallyRequestedEndsIfCalledTwice(false) == 0);
static_assert(locallyRequestedEndsIfCalledTwice(true) == 2);

int main() {
    for (std::uint32_t minimum = 0; minimum <= 65535; ++minimum) {
        const auto init = planInitialization(
            0, static_cast<std::uint16_t>(minimum));
        assert(init.multimediaClockFlag);
        assert(init.callTimeBeginPeriod);
        assert(init.requestedPeriodIsValid);
        assert(init.requestedPeriodMilliseconds ==
               (minimum < 10 ? 10 : minimum));
    }

    for (std::uint16_t result = 1; result < 1000; ++result) {
        const auto init = planInitialization(result, 200);
        assert(!init.multimediaClockFlag);
        assert(!init.callTimeBeginPeriod);
        assert(!init.requestedPeriodIsValid);
    }
    return 0;
}
