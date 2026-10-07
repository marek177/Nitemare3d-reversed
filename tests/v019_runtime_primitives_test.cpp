#include "re/N3DV019RuntimePrimitives.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v019;

    static_assert(kPlayerCollisionFootprint == 0x1B);
    static_assert(kSecretPanelStepPerUpdate == 2);
    static_assert(kAutomapDrainIntervalTicks == 16);
    static_assert(kEnemyDetectorDrainIntervalTicks == 8);

    static_assert(blockedBothAxisToFlip(0) == Axis::Y);
    static_assert(blockedBothAxisToFlip(1) == Axis::X);
    static_assert(blockedBothAxisToFlip(2) == Axis::Y);
    static_assert(blockedBothAxisToFlip(3) == Axis::X);

    static_assert(plannerBaseTimer(0) == 8);
    static_assert(plannerBaseTimer(7) == 15);
    static_assert(plannerTimer(0, Difficulty::Easy) == 16);
    static_assert(plannerTimer(7, Difficulty::Easy) == 30);
    static_assert(plannerTimer(0, Difficulty::Medium) == 8);
    static_assert(plannerTimer(7, Difficulty::Medium) == 15);
    static_assert(plannerTimer(0, Difficulty::Hard) == 4);
    static_assert(plannerTimer(7, Difficulty::Hard) == 7);

    static_assert(state13Timer(0) == 8);
    static_assert(state13Timer(79) == 87);

    assert(retractCoordinateToward(10, 20) == 12);
    assert(retractCoordinateToward(19, 20) == 20);
    assert(retractCoordinateToward(20, 10) == 18);
    assert(retractCoordinateToward(11, 10) == 10);
    assert(retractCoordinateToward(10, 10) == 10);

    static_assert(kExactSlidingOrderConfidence == Confidence::Open);
    static_assert(kExactSchedulerInterleaveConfidence == Confidence::Open);
    static_assert(kProjectilePoolFullAmmoConfidence == Confidence::Strong);
    return 0;
}
