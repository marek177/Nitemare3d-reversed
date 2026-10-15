#include "re/N3DV034ObjectAnimationEvidence.hpp"
#include "re/N3DV029SchedulerEvidence.hpp"
#include "re/N3DV033PushScheduler.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::v034;

int main() {
    static_assert(kOriginalDirectCalls.size() == 16);
    static_assert(kSpanAnimator == 0x241E);
    static_assert(kProjectedAnimator == 0xB22C);
    static_assert(kDirectionalAnimator == 0xB17E);
    static_assert(kObjectFrameField == 3);
    static_assert(kObjectAnimationDeadlineOffset == 8);
    static_assert(kSpanPoolCount == 0x4D64);
    static_assert(kSpanPoolBase == 0x4D6E);

    static_assert(isDirectTarget(0xC239, 0xBF36)); // frame -> render
    static_assert(isDirectTarget(0xBF40, 0x213E)); // spans
    static_assert(isDirectTarget(0xBF5A, 0x2500)); // span renderer
    static_assert(isDirectTarget(0xBF5F, 0x21F0)); // sorted objects
    static_assert(isDirectTarget(0x2721, 0x241E)); // visible span frame
    static_assert(isDirectTarget(0x2225, 0xB2D4)); // world object projection
    static_assert(isDirectTarget(0x8307, 0xB2D4)); // projectile projection
    static_assert(isDirectTarget(0xB521, 0xB22C)); // regular object frame
    static_assert(isDirectTarget(0xB532, 0xB17E)); // directional object frame
    static_assert(isDirectTarget(0xC246, 0x0AEA)); // panels on outer frame
    static_assert(isDirectTarget(0xC24B, 0x8230)); // projectiles on outer frame
    static_assert(isDirectTarget(0xC172, 0x0E50)); // PUSH on FAST
    static_assert(isDirectTarget(0xC153, 0xC51A)); // RETF no-op
    static_assert(isDirectTarget(0xC1EA, 0xC150)); // normal FAST
    static_assert(isDirectTarget(0xC22E, 0xC150)); // DEMO FAST
    static_assert(!isDirectTarget(0x2721, 0xB22C));
    static_assert(callAt(0x1234) == nullptr);

    // Target is a verified static call graph edge, not a count of per-tick calls.
    for (const auto& edge : kOriginalDirectCalls) {
        assert(edge.targetImageOffset != 0);
        assert(edge.evidence.size() > 4);
        assert(isDirectTarget(edge.site, edge.targetImageOffset));
    }
    for (std::size_t i = 0; i < kOriginalDirectCalls.size(); ++i) {
        for (std::size_t j = i + 1; j < kOriginalDirectCalls.size(); ++j) {
            assert(kOriginalDirectCalls[i].site != kOriginalDirectCalls[j].site);
        }
    }
    static_assert(demoFrameBranchCallsFast(true, true, 1));
    static_assert(!demoFrameBranchCallsFast(true, true, 0));
    static_assert(!demoFrameBranchCallsFast(true, true, 2));
    static_assert(demoFrameBranchCallsFast(true, true, 3));
    static_assert(!demoFrameBranchCallsFast(true, false, 1));
    static_assert(!demoFrameBranchCallsFast(false, true, 1));
    // This predicate takes the BEFORE-BF36 increment count, never "+1".
    static_assert(animationDeadlineDue(7, 7));
    static_assert(animationDeadlineDue(7, 8));
    static_assert(!animationDeadlineDue(8, 7));
    static_assert(!animationDeadlineDue(0xFFFFFFFFu, 0u));

    static_assert(spanAnimationCanRun(true, 1, 7, 7));
    static_assert(!spanAnimationCanRun(true, 0, 7, 7));
    static_assert(!spanAnimationCanRun(false, 1, 7, 7));
    static_assert(!spanAnimationCanRun(true, 1, 9, 7));

    static_assert(projectedRegularAnimationCanRun(true, 0x01, 0x10, 2, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(true, 0, 0x10, 2, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(false, 1, 0x10, 2, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(true, 1, 0x10, 0, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(true, 1, 0x05, 2, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(true, 1, 0x2C, 2, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(true, 1, 0x2D, 2, 7, 7));
    static_assert(!projectedRegularAnimationCanRun(true, 1, 0x10, 2, 9, 7));

    // Directional branch (0x2C/0x2D) bypasses descriptor-interval gate.
    static_assert(projectedDirectionalAnimationCanRun(true, 1, 0x2C, 7, 7));
    static_assert(projectedDirectionalAnimationCanRun(true, 1, 0x2D, 5, 7));
    static_assert(!projectedDirectionalAnimationCanRun(true, 1, 0x2B, 5, 7));
    static_assert(!projectedDirectionalAnimationCanRun(true, 1, 0x2E, 5, 7));
    static_assert(!projectedDirectionalAnimationCanRun(true, 0, 0x2D, 5, 7));
    static_assert(!projectedDirectionalAnimationCanRun(false, 1, 0x2D, 5, 7));
    static_assert(!projectedDirectionalAnimationCanRun(true, 1, 0x2D, 10, 7));

    static_assert(kThreeAnimatorSitesConfidence == Confidence::VerifiedOriginalStatic);
    static_assert(kCompleteObjectWriterCensusConfidence == Confidence::RuntimeOpen);
    static_assert(kExactFastFrameRngChronologyConfidence == Confidence::RuntimeOpen);
    static_assert(!kMonolithicObjectSchedulerIdentified);
    static_assert(n3d::re::v033::kDos20PushUpdate == 0x0E50);
    static_assert(n3d::re::v029::kDos20FastDirectCalls[5].offset == 0x0E50);
    return 0;
}
