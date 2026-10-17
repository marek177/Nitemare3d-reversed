#include "re/N3DV040ProjectileReentryClosure.hpp"

#include <cassert>

using namespace n3d::re::v040;

int main() {
    {
        const auto noHit = visitFlyingSlot(false);
        assert(noHit.state == ProjectileState::Flying);
        assert(!noHit.canFallThroughToImpactExpiry);
        assert(!allocatorCanReuse(noHit.state));
    }

    {
        const auto hit = visitFlyingSlot(true);
        assert(hit.state == ProjectileState::Impact);
        assert(!hit.canFallThroughToImpactExpiry);
        assert(!allocatorCanReuse(hit.state));
    }

    {
        const auto twentieth = e2m10CounterStep(19);
        assert(twentieth.after == 20);
        assert(twentieth.entersNestedWait);

        const auto twentyFirst = e2m10CounterStep(20);
        assert(twentyFirst.after == 21);
        assert(!twentyFirst.entersNestedWait);
    }

    {
        const auto noHit = oneLevelE2M10SelfReentry(false);
        assert(noHit.stateAfterNestedPool == ProjectileState::Flying);
        assert(!noHit.sameNestedInvocationCanFree);
        assert(!noHit.sameNestedInvocationCanReallocate);
        assert(noHit.counterAfterNestedCollision == 21);
        assert(!noHit.sameProperty40HitImmediatelyNestsAgain);
        assert(!directOneLevelAbaPossible(false));
    }

    {
        const auto hit = oneLevelE2M10SelfReentry(true);
        assert(hit.stateAfterNestedPool == ProjectileState::Impact);
        assert(!hit.sameNestedInvocationCanFree);
        assert(!hit.sameNestedInvocationCanReallocate);
        assert(hit.counterAfterNestedCollision == 21);
        assert(!hit.sameProperty40HitImmediatelyNestsAgain);
        assert(!directOneLevelAbaPossible(true));
    }

    assert(allocatorCanReuse(ProjectileState::Free));
    return 0;
}
