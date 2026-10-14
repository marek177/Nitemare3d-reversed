#include "re/N3DV029SchedulerEvidence.hpp"

#include <array>
#include <cassert>
#include <span>

using namespace n3d::re::v029;

int main() {
    static_assert(kDos20FastTick == 0xC150);
    static_assert(kDos20OuterScheduler == 0xC1A8);
    static_assert(expectedFastDirectCount(7) == 10);
    static_assert(expectedFastDirectCount(8) == 11);
    static_assert(expectedFastDirectCount(16) == 11);
    static_assert(kDos20FastDirectCalls[5].offset == 0x0E50);
    static_assert(kDos20FastDirectCalls[10].gate == CallGate::TickLowThreeBitsZero);

    static_assert(finding("door_blocked_retry_four") != nullptr);
    static_assert(finding("door_state4_pair_sync")->build == BuildId::DosV12);
    static_assert(finding("door_state4_early_return")->build == BuildId::DosV20);
    static_assert(!runtimeConfirmed("fast_direct_call_order"));
    static_assert(!runtimeConfirmed("e2m10_twentieth_special_hit_reentry"));
    static_assert(!runtimeConfirmed("demo_seed1_full_rng_order"));
    static_assert(!runtimeConfirmed("does_not_exist"));

    // Synthetic normalized direct calls, NOT a capture from the original game.
    constexpr std::array<CapturedCall, 14> trace {{
        {7, 0xC150, 0xC51A},
        {7, 0xC51A, 0x1234}, // nested helper, not a direct C150 child
        {7, 0xC150, 0x0A40},
        {7, 0xC150, 0x5F26},
        {99, 0xC150, 0xFFFF}, // different FAST invocation: do not interleave
        {7, 0xC150, 0xA19A},
        {7, 0xC150, 0xA4A2},
        {7, 0xC150, 0x0E50},
        {7, 0xC150, 0xA4AC},
        {7, 0xC150, 0xA0CC},
        {7, 0xC150, 0x89A2},
        {7, 0x9026, 0x6666}, // another nested call
        {7, 0xC150, 0x9026},
        {7, 0xC150, 0x89A2}
    }};
    constexpr auto match = checkFastDirectCalls(trace, 7, 8);
    static_assert(match.matches());
    static_assert(match.observedCount == 11);

    // Without the conditional call this exact sequence is a normal tick.
    static_assert(checkFastDirectCalls(
        std::span<const CapturedCall>(trace.data(), trace.size()-1), 7, 3).matches());
    static_assert(checkFastDirectCalls(
        std::span<const CapturedCall>(trace.data(), trace.size()-1), 7, 8).verdict == Verdict::Incomplete);
    static_assert(checkFastDirectCalls(trace, 7, 3).verdict == Verdict::Divergent);
    static_assert(checkFastDirectCalls(trace, 444, 3).verdict == Verdict::Missing);

    constexpr std::array<CapturedCall, 3> swapped {{
        {7, 0xC150, 0xC51A},
        {7, 0xC150, 0x5F26},
        {7, 0xC150, 0x0A40}
    }};
    constexpr auto divergent = checkFastDirectCalls(swapped, 7, 5);
    static_assert(divergent.verdict == Verdict::Divergent);
    static_assert(divergent.firstDifference == 1);
    static_assert(divergent.expectedOffset == 0x0A40);
    static_assert(divergent.observedOffset == 0x5F26);
    assert(match.matches());
}
