#pragma once

#include <cstdint>

namespace n3d::re::v040 {

enum class ProjectileState : std::uint8_t {
    Free = 0,
    Flying = 1,
    Impact = 2,
};

struct FlyingVisitResult {
    ProjectileState state{};
    bool canFallThroughToImpactExpiry{};
    bool allocatorCanReuseLaterSameOuterInvocation{};
};

// Bounded invariant from the audited 9-build projectile pool:
// a slot that ENTERS one pool visit in state=1 executes the state-1 arm only.
// If no collision occurs it remains state=1. If collision occurs, movement
// writes state=2 after the callback returns. There is no local fall-through
// into the state-2 expiry arm during that same visit.
constexpr FlyingVisitResult visitFlyingSlot(bool collisionAccepted) noexcept {
    return {
        collisionAccepted ? ProjectileState::Impact : ProjectileState::Flying,
        false,
        false,
    };
}

constexpr bool allocatorCanReuse(ProjectileState state) noexcept {
    return state == ProjectileState::Free;
}

struct E2M10CounterStep {
    std::uint16_t after{};
    bool entersNestedWait{};
};

// Original signed-IDIV-by-20 gate. For the direct E2M10 self-reentry argument
// we care about 19->20 (nested wait) and then 20->21 (no immediate second wait).
constexpr E2M10CounterStep e2m10CounterStep(std::uint16_t before) noexcept {
    const auto after = static_cast<std::uint16_t>(before + 1u);
    const auto signedAfter = static_cast<std::int16_t>(after);
    return {after, static_cast<std::int16_t>(signedAfter % 20) == 0};
}

struct OneLevelSelfReentryResult {
    ProjectileState stateAfterNestedPool{};
    bool sameNestedInvocationCanFree{};
    bool sameNestedInvocationCanReallocate{};
    std::uint16_t counterAfterNestedCollision{};
    bool sameProperty40HitImmediatelyNestsAgain{};
};

// Scope: the outer 20th property-0x40 E2M10 hit has already entered one nested
// scheduler while the suspended parent slot is still state=1. If that nested
// pool revisits the same slot through the standard state-1 arm, the slot cannot
// reach state=0 in that same visit. Input/FIRE allocation is later in the same
// nested outer invocation, so the allocator cannot reuse this slot there.
// A same-path nested collision advances 20->21 and does not immediately launch
// a second E2M10 wait/nested scheduler.
//
// This does NOT exclude a second nested scheduler from some other callback,
// an indirect/aliased state writer, SAVE/LOAD, IRQ-driven code or corruption.
constexpr OneLevelSelfReentryResult oneLevelE2M10SelfReentry(
    bool nestedCollisionAccepted) noexcept {
    const auto visit = visitFlyingSlot(nestedCollisionAccepted);
    const auto secondHit = e2m10CounterStep(20);
    return {
        visit.state,
        false,
        allocatorCanReuse(visit.state),
        secondHit.after,
        secondHit.entersNestedWait,
    };
}

constexpr bool directOneLevelAbaPossible(bool nestedCollisionAccepted) noexcept {
    const auto r = oneLevelE2M10SelfReentry(nestedCollisionAccepted);
    return r.sameNestedInvocationCanFree && r.sameNestedInvocationCanReallocate;
}

} // namespace n3d::re::v040
