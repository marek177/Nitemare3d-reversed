#pragma once

#include <cstddef>
#include <cstdint>

namespace n3d::re::v037 {

// All offsets below are in the fingerprinted original DOS v2.0 unpacked
// MZ LOAD IMAGE, NOT Win16 NE offsets or runtime segment:offset addresses.
inline constexpr std::uint16_t kSlowQuantizer = 0xBEB4;
inline constexpr std::uint16_t kFrameQuantizer = 0xBEF4;
inline constexpr std::uint16_t kOuterScheduler = 0xC1A8;
inline constexpr std::uint16_t kSlowDueGate = 0xC1D2;
inline constexpr std::uint16_t kFrameDueGate = 0xC20C;
inline constexpr std::uint16_t kDemoRenderGenerationGate = 0xC221;
inline constexpr std::uint16_t kNormalFastSite = 0xC1EA;
inline constexpr std::uint16_t kDemoFastSite = 0xC22E;
inline constexpr std::uint16_t kMainSite = 0xC235;
inline constexpr std::uint16_t kRenderSite = 0xC239;
inline constexpr std::uint16_t kSecretPanelSite = 0xC246;
inline constexpr std::uint16_t kProjectileSite = 0xC24B;
inline constexpr std::uint16_t kLegacyClockRecoveryGate = 0xC28F;

// Original BEB4/B EF4 both multiply 32-bit EAX, keeping only the LOW
// 32-bit product before an unsigned divide by 1000. Cached *quotients*
// are compared for inequality, not elapsed quantized-step differences.
constexpr std::uint32_t slowScaledKey(std::uint32_t elapsed) noexcept {
    return (elapsed * UINT32_C(8)) / UINT32_C(1000);
}

constexpr std::uint32_t frameScaledKey(std::uint32_t elapsed,
                                        std::int16_t calibration) noexcept {
    // MOVSX EAX,WORD DS:3CC2; MUL DWORD [BP+06].
    const auto factor = static_cast<std::uint32_t>(
        static_cast<std::int32_t>(calibration));
    return (factor * elapsed) / UINT32_C(1000);
}

struct QuantizedCounter {
    std::uint32_t cachedKey{0};
    std::uint32_t count{0};
};

struct CounterChange {
    QuantizedCounter counter;
    std::uint32_t newKey;
    bool advanced;
};

// BEB4 and BEF4: if quantized current sample != cachedKey, store the
// new value AND increment the counter by precisely ONE (32-bit wrap).
// NO catch-up loop; a time jump of 500 quantized units still increments 1.
constexpr CounterChange advanceQuantizedCounter(QuantizedCounter prior,
                                                std::uint32_t newKey) noexcept {
    if (prior.cachedKey == newKey) return {prior, newKey, false};
    return {{newKey, prior.count + UINT32_C(1)}, newKey, true};
}

struct SchedulerState {
    QuantizedCounter slow;       // DS:16FA key, DS:16F6 32-bit counter
    QuantizedCounter frame;      // DS:1702 key, DS:16FE 32-bit counter
    std::uint32_t nextSlow{0};   // DS:1738 "next allowed slow count"
    std::uint32_t nextFrame{0};  // DS:173C "next allowed frame count"
    std::uint32_t renderGeneration{0}; // DS:4540
    std::uint32_t legacyEpoch{0};      // DS:1734
};

struct SchedulerInput {
    std::uint32_t sampledClock;            // first BE74 result for both dividers
    std::uint32_t sampledLegacyClock;      // entry BDF8 result, independent snapshot
    std::uint32_t resampledLegacyClock;    // BDF8 result only IF recovery runs
    std::int16_t frameCalibration;         // signed DS:3CC2 (usually positive)
    bool demoModeNonzero;
};

struct SchedulerStep {
    SchedulerState after;
    bool slowCounterAdvanced;
    bool frameCounterAdvanced;
    bool slowDue;
    bool frameDue;
    bool normalFastCalled;
    bool demoFastCalled;
    bool mainCalled;
    bool rendered;
    bool panelUpdateCalled;
    bool projectileUpdateCalled;
    bool recoveryHooksCalled;  // BDE4(1), BDE4(0) + new BDF8
    std::uint32_t fastArgument; // slow counter in BOTH FAST paths
    std::uint32_t renderGenerationBefore;
};

// C1A8 local, *direct-child* scheduling model. External subroutine effects,
// interrupt delivery, input callbacks, timer resampling and recursively
// invoked schedulers are deliberately NOT modeled here. In the original:
// 1. update slow counter, if nextSlow<=slow count process ONCE,
//    call FAST only with DEMO mode 0, then nextSlow=slow count+1;
// 2. update frame counter, if nextFrame<=frame count process ONCE,
//    call FAST only with DEMO mode!=0 and PRE-RENDER DS:4540 bit0=1;
// 3. MAIN then BF36 render (+1 generation), panel, projectile, other calls;
//    set nextFrame=frame count+1 and legacyEpoch=entry BDF8 snapshot;
// 4. when unsigned (sampledLegacyClock-legacyEpoch)>500, perform recovery
//    BDE4(1),BDE4(0),BDF8 and replace legacyEpoch.
// Source has no local backward branch around these event handlers.
constexpr SchedulerStep stepOuterScheduler(SchedulerState state,
                                           SchedulerInput in) noexcept {
    SchedulerStep r{state, false, false, false, false, false, false,
                    false, false, false, false, false, 0,
                    state.renderGeneration};
    const auto slow = advanceQuantizedCounter(
        state.slow, slowScaledKey(in.sampledClock));
    r.after.slow = slow.counter;
    r.slowCounterAdvanced = slow.advanced;
    r.slowDue = r.after.nextSlow <= r.after.slow.count;
    if (r.slowDue) {
        if (!in.demoModeNonzero) r.normalFastCalled = true;
        r.after.nextSlow = r.after.slow.count + UINT32_C(1);
    }

    const auto frame = advanceQuantizedCounter(
        state.frame, frameScaledKey(in.sampledClock, in.frameCalibration));
    r.after.frame = frame.counter;
    r.frameCounterAdvanced = frame.advanced;
    r.frameDue = r.after.nextFrame <= r.after.frame.count;
    if (r.frameDue) {
        if (in.demoModeNonzero && (r.after.renderGeneration & 1u) != 0u)
            r.demoFastCalled = true;
        r.mainCalled = true;
        r.rendered = true;
        r.after.renderGeneration += UINT32_C(1);
        r.panelUpdateCalled = true;
        r.projectileUpdateCalled = true;
        r.after.nextFrame = r.after.frame.count + UINT32_C(1);
        r.after.legacyEpoch = in.sampledLegacyClock;
    }

    // Original C286/C28F unsigned 32-bit SUB/CMP/JBE 0x1F4. This
    // check also happens when frameDue is false; a clock rollback may
    // underflow and thus take the recovery path.
    const auto delta = in.sampledLegacyClock - r.after.legacyEpoch;
    if (delta > UINT32_C(500)) {
        r.recoveryHooksCalled = true;
        r.after.legacyEpoch = in.resampledLegacyClock;
    }

    if (r.normalFastCalled || r.demoFastCalled)
        r.fastArgument = r.after.slow.count;

    return r;
}

constexpr bool hasMoreThanOneDirectFastPerOuter(const SchedulerStep& s) noexcept {
    return s.normalFastCalled && s.demoFastCalled;
}

inline constexpr bool kFullTransitiveRuntimeProven = false;
inline constexpr bool kRngOrderingProven = false;
inline constexpr bool kClockSourceAndInterruptsProven = false;

} // namespace n3d::re::v037
