#include "re/N3DV037SchedulerCatchup.hpp"
#include "re/N3DV029SchedulerEvidence.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <initializer_list>

using namespace n3d::re::v037;

int main() {
    static_assert(kSlowQuantizer == 0xBEB4);
    static_assert(kFrameQuantizer == 0xBEF4);
    static_assert(kOuterScheduler == 0xC1A8);
    static_assert(kDemoRenderGenerationGate == 0xC221);
    static_assert(n3d::re::v029::kDos20OuterScheduler == kOuterScheduler);

    static_assert(slowScaledKey(0) == 0);
    static_assert(slowScaledKey(124) == 0);
    static_assert(slowScaledKey(125) == 1);    // 8 Hz quantization
    static_assert(slowScaledKey(249) == 1);
    static_assert(slowScaledKey(250) == 2);
    static_assert(frameScaledKey(125, 8) == 1);
    static_assert(frameScaledKey(125, 16) == 2);
    static_assert(frameScaledKey(249, 8) == 1);
    static_assert(frameScaledKey(250, 8) == 2);
    static_assert(frameScaledKey(250, 0) == 0);
    // 32-bit x86 MUL truncates before division (no unbounded integers).
    static_assert(slowScaledKey(0xFFFFFFFFu) ==
                  static_cast<std::uint32_t>(0xFFFFFFF8u / 1000u));
    static_assert(frameScaledKey(0xFFFFFFFFu, 2) ==
                  static_cast<std::uint32_t>(0xFFFFFFFEu / 1000u));

    constexpr auto noChange = advanceQuantizedCounter({5, 99}, 5);
    static_assert(!noChange.advanced);
    static_assert(noChange.counter.count == 99);
    constexpr auto oneStep = advanceQuantizedCounter({1, 8}, 2000);
    static_assert(oneStep.advanced);
    static_assert(oneStep.counter.cachedKey == 2000);
    static_assert(oneStep.counter.count == 9); // NOT 2007
    constexpr auto wrapped = advanceQuantizedCounter({1, 0xFFFFFFFFu}, 2);
    static_assert(wrapped.advanced && wrapped.counter.count == 0u);
    constexpr auto backwards = advanceQuantizedCounter({100, 30}, 3);
    static_assert(backwards.advanced && backwards.counter.count == 31);

    SchedulerState initial{};
    initial.nextSlow = 1;
    initial.nextFrame = 1;
    constexpr SchedulerInput first{125, 100, 101, 8, false};
    const auto firstStep = stepOuterScheduler(initial, first);
    assert(firstStep.slowCounterAdvanced && firstStep.frameCounterAdvanced);
    assert(firstStep.slowDue && firstStep.frameDue);
    assert(firstStep.normalFastCalled && !firstStep.demoFastCalled);
    assert(firstStep.fastArgument == 1);
    assert(firstStep.mainCalled && firstStep.rendered);
    assert(firstStep.panelUpdateCalled && firstStep.projectileUpdateCalled);
    assert(firstStep.after.renderGeneration == 1);
    assert(firstStep.after.nextSlow == 2);
    assert(firstStep.after.nextFrame == 2);
    assert(firstStep.after.legacyEpoch == 100);
    assert(!firstStep.recoveryHooksCalled);

    // A jump of 1000 milliseconds advances both bucket counters only ONCE:
    // skipped clock intervals are NOT replayed as individual FAST/tick passes.
    const auto jumped = stepOuterScheduler(firstStep.after,
                                           {1125, 101, 102, 8, false});
    assert(jumped.slowCounterAdvanced && jumped.frameCounterAdvanced);
    assert(jumped.after.slow.cachedKey == 9);
    assert(jumped.after.frame.cachedKey == 9);
    assert(jumped.after.slow.count == 2);
    assert(jumped.after.frame.count == 2);
    assert(jumped.normalFastCalled && jumped.mainCalled);
    assert(jumped.fastArgument == 2);
    assert(!hasMoreThanOneDirectFastPerOuter(jumped));
    // Same quantized sample a second time has no newly due update.
    const auto repeated = stepOuterScheduler(jumped.after,
                                             {1125, 101, 102, 8, false});
    assert(!repeated.slowCounterAdvanced);
    assert(!repeated.frameCounterAdvanced);
    assert(!repeated.slowDue && !repeated.frameDue);
    assert(!repeated.normalFastCalled && !repeated.demoFastCalled);
    assert(!repeated.mainCalled && !repeated.rendered);

    // Demo slow bucket still advances, but FAST runs only under the
    // independently due frame bucket + PRE-render generation odd bit.
    SchedulerState demo{};
    demo.nextSlow = 1;
    demo.nextFrame = 1;
    demo.renderGeneration = 1;
    const auto d = stepOuterScheduler(demo, {125, 13, 14, 8, true});
    assert(d.slowDue && d.frameDue);
    assert(!d.normalFastCalled && d.demoFastCalled);
    assert(d.fastArgument == d.after.slow.count);
    assert(d.fastArgument == 1);
    assert(d.renderGenerationBefore == 1);
    assert(d.after.renderGeneration == 2);
    assert(!hasMoreThanOneDirectFastPerOuter(d));

    demo.renderGeneration = 2;
    const auto even = stepOuterScheduler(demo, {125, 13, 14, 8, true});
    assert(even.frameDue && even.slowDue && even.rendered);
    assert(!even.demoFastCalled); // even BEFORE BF36, despite increment to 3
    assert(even.after.renderGeneration == 3);
    demo.nextFrame = 5; // skip render while still processing slow due
    const auto noFrame = stepOuterScheduler(demo, {125, 13, 14, 8, true});
    assert(noFrame.slowDue && !noFrame.frameDue);
    assert(!noFrame.normalFastCalled && !noFrame.demoFastCalled);

    // Both counters may be due but the two FAST callsites are mutually
    // exclusive by DEMO mode in this OUTER invocation; not a global
    // statement about recursive or interrupt-invoked FAST.
    for (const bool active : {false, true}) {
        SchedulerState state{};
        state.nextSlow = state.nextFrame = 1;
        state.renderGeneration = 1;
        const auto test = stepOuterScheduler(state, {125, 125, 125, 8, active});
        assert(test.normalFastCalled != test.demoFastCalled);
        assert(!hasMoreThanOneDirectFastPerOuter(test));
    }

    // No due frame: unsigned time difference >500 causes two BDE4 hooks
    // and a BDF8 resample of the "legacy epoch".
    SchedulerState lag{};
    lag.nextSlow = 99;
    lag.nextFrame = 99;
    lag.legacyEpoch = 100;
    const auto noTimeout = stepOuterScheduler(lag, {0, 600, 777, 0, false});
    assert(!noTimeout.recoveryHooksCalled); // exactly 500 is not greater
    const auto timeout = stepOuterScheduler(lag, {0, 601, 777, 0, false});
    assert(timeout.recoveryHooksCalled);
    assert(timeout.after.legacyEpoch == 777);
    assert(!timeout.frameDue && !timeout.rendered);
    const auto rollback = stepOuterScheduler(lag, {0, 99, 777, 0, false});
    assert(rollback.recoveryHooksCalled); // 32-bit unsigned subtraction wraps

    // When a frame is due, C282 stores the entry BDF8 sample BEFORE
    // comparing the 500 threshold, so an otherwise old epoch is replaced.
    lag.nextFrame = 0;
    lag.legacyEpoch = 1;
    const auto dueAfterGap = stepOuterScheduler(lag, {0, 10000, 99999, 0, false});
    assert(dueAfterGap.frameDue);
    assert(dueAfterGap.after.legacyEpoch == 10000);
    assert(!dueAfterGap.recoveryHooksCalled);

    // A pathological zero calibration freezes new frame bucket increments
    // in this narrow static model; natural use of calibration==0 not claimed.
    SchedulerState zero{};
    zero.nextSlow = zero.nextFrame = 1;
    const auto onlySlow = stepOuterScheduler(zero, {125, 3, 4, 0, false});
    assert(onlySlow.slowDue && !onlySlow.frameDue);
    assert(onlySlow.normalFastCalled && !onlySlow.mainCalled);

    static_assert(!kFullTransitiveRuntimeProven);
    static_assert(!kRngOrderingProven);
    static_assert(!kClockSourceAndInterruptsProven);
}
