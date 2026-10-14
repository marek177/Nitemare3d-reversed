#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <string_view>

namespace n3d::re::v029 {

// These are research-evidence records, NOT a replacement game scheduler.
// All code offsets here are scoped to the audited DOS v2.0 image.
enum class BuildId : std::uint8_t { Unknown, DosV12, DosV20, Win16V110 };
enum class Evidence : std::uint8_t {
    ReportedStatic,   // direct/static audit reported; no runtime trace in this update
    StrongInference,  // inference from control flow, pending counterexample testing
    RuntimeOpen,      // no accepted full runtime chronology
    RuntimeConfirmed, // reserved for later evidence-backed promotion
    VerifiedStatic     // original fingerprinted machine-code re-disassembly
};
enum class CallGate : std::uint8_t { Always, TickLowThreeBitsZero };

struct FastDirectTarget {
    std::uint16_t offset;
    CallGate gate;
    std::string_view label;
};

inline constexpr std::uint16_t kDos20FastTick = 0xC150;
inline constexpr std::uint16_t kDos20OuterScheduler = 0xC1A8;

// Reported sequence of DIRECT call targets of 1000:C150, not the full
// transitive execution order. Callbacks/recursive invocations may interleave.
inline constexpr std::array<FastDirectTarget, 11> kDos20FastDirectCalls = {{
    {0xC51A, CallGate::Always, "C51A helper (semantics open)"},
    {0x0A40, CallGate::Always, "door auto-close"},
    {0x5F26, CallGate::Always, "GUARD scheduler"},
    {0xA19A, CallGate::Always, "A19A helper (semantics open)"},
    {0xA4A2, CallGate::Always, "A4A2 helper (semantics open)"},
    {0x0E50, CallGate::Always, "PUSH updater (six-byte pool; original bytes verified)"},
    {0xA4AC, CallGate::Always, "A4AC helper (semantics open)"},
    {0xA0CC, CallGate::Always, "A0CC helper (semantics open)"},
    {0x89A2, CallGate::Always, "action/input pass"},
    {0x9026, CallGate::Always, "weapon/cadence path"},
    {0x89A2, CallGate::TickLowThreeBitsZero, "conditional action/input pass"}
}};

constexpr std::size_t expectedFastDirectCount(std::uint32_t tickAtGate) noexcept {
    return kDos20FastDirectCalls.size() - ((tickAtGate & 7u) != 0u ? 1u : 0u);
}

// A captured direct-call event needs its own FAST invocation ID. A raw
// address stream is insufficient when calls can be nested/reentrant.
struct CapturedCall {
    std::uint32_t fastInvocationId;
    std::uint16_t immediateCallerOffset;
    std::uint16_t targetOffset;
};

enum class Verdict : std::uint8_t { Match, Missing, Divergent, Incomplete };
struct FastTraceCheck {
    Verdict verdict;
    std::size_t firstDifference; // direct-child ordinal within this invocation
    std::size_t observedCount;
    std::size_t expectedCount;
    std::uint16_t expectedOffset; // 0 only when no expected call remains
    std::uint16_t observedOffset; // 0 only when no captured call remains

    constexpr bool matches() const noexcept { return verdict == Verdict::Match; }
};

// tickAtGate is the counter at the conditional branch, NOT assumed to be
// the tick at entry. Nested callbacks could change time between those points.
constexpr FastTraceCheck checkFastDirectCalls(
    std::span<const CapturedCall> capture,
    std::uint32_t fastInvocationId,
    std::uint32_t tickAtGate) noexcept {

    const auto expectedCount = expectedFastDirectCount(tickAtGate);
    std::size_t directCount = 0;
    bool different = false;
    std::size_t firstDifference = 0;
    std::uint16_t expectedOffset = 0;
    std::uint16_t observedOffset = 0;

    for (const auto& call : capture) {
        if (call.fastInvocationId != fastInvocationId ||
            call.immediateCallerOffset != kDos20FastTick) {
            continue;
        }
        if (!different && (directCount >= expectedCount ||
            call.targetOffset != kDos20FastDirectCalls[directCount].offset)) {
            different = true;
            firstDifference = directCount;
            expectedOffset = directCount < expectedCount
                                 ? kDos20FastDirectCalls[directCount].offset : 0;
            observedOffset = call.targetOffset;
        }
        ++directCount;
    }

    if (different) {
        return {Verdict::Divergent, firstDifference, directCount,
                expectedCount, expectedOffset, observedOffset};
    }
    if (directCount == 0) {
        return {Verdict::Missing, 0, 0, expectedCount,
                kDos20FastDirectCalls[0].offset, 0};
    }
    if (directCount < expectedCount) {
        return {Verdict::Incomplete, directCount, directCount, expectedCount,
                kDos20FastDirectCalls[directCount].offset, 0};
    }
    return {Verdict::Match, expectedCount, directCount, expectedCount, 0, 0};
}

struct AuditFinding {
    std::string_view id;
    BuildId build;
    Evidence evidence;
    std::string_view summary;
};

inline constexpr std::array<AuditFinding, 11> kRecentFindings = {{
    {"fast_direct_call_order", BuildId::DosV20, Evidence::ReportedStatic,
     "C150 direct call order only; not complete transitive runtime order"},
    {"demo_fast_odd_frame_route", BuildId::DosV20, Evidence::StrongInference,
     "C1A8/6D04 DEMO branch can route FAST via odd DS:4540 frame count"},
    {"demo_seed1_full_rng_order", BuildId::DosV20, Evidence::RuntimeOpen,
     "No capture of all draws through first gameplay input"},
    {"push_blocked_preserves_progress", BuildId::DosV20, Evidence::VerifiedStatic,
     "0E50: when destination cell differs and object property & 0x06 is nonzero, skip coordinate write, sort helper and timer decrement"},
    {"push_update_0e50", BuildId::DosV20, Evidence::VerifiedStatic,
     "0E50 is 6-byte PUSH updater; masked control-flow bytes identical to Win16 3:2210 (292 bytes)"},
    {"door_blocked_retry_four", BuildId::DosV20, Evidence::ReportedStatic,
     "0A40: obstructed auto-close arms retry timer 4"},
    {"door_state4_pair_sync", BuildId::DosV12, Evidence::StrongInference,
     "state 4 path may synchronize paired wall; compare original v1.2 image"},
    {"door_state4_early_return", BuildId::DosV20, Evidence::StrongInference,
     "state 4 has differing early-return path; do not transfer DOS v1.2"},
    {"e2m10_twentieth_special_hit_reentry", BuildId::Unknown,
     Evidence::StrongInference,
     "20th special-hit branch may enter nested scheduler before collision returns"},
    {"post_load_first_tick_order", BuildId::Win16V110, Evidence::RuntimeOpen,
     "initial buffer alias is mapped; first post-LOAD gameplay tick not traced"},
    {"full_fast_main_order", BuildId::DosV20, Evidence::RuntimeOpen,
     "Nested callbacks, time catch-up and render/RNG chronology unverified"}
}};

constexpr const AuditFinding* finding(std::string_view id) noexcept {
    for (const auto& fact : kRecentFindings) {
        if (fact.id == id) return &fact;
    }
    return nullptr;
}

constexpr bool runtimeConfirmed(std::string_view id) noexcept {
    const auto* fact = finding(id);
    return fact && fact->evidence == Evidence::RuntimeConfirmed;
}

} // namespace n3d::re::v029
