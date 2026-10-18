#include "re/N3DV045WeaponSwitchFrameOrder.hpp"
#include <cassert>

using namespace n3d::re::v045;

int main() {
    static_assert(stageBefore(DirectFrameStage::WeaponHudUpdate,
                              DirectFrameStage::ProjectilePoolUpdate));
    static_assert(stageBefore(DirectFrameStage::ProjectilePoolUpdate,
                              DirectFrameStage::GameplayInput));
    static_assert(kWeaponRequestBeforeFireInSameInputCall);
    static_assert(!kNewProjectileMovesInSameDirectParentFrame);

    {
        WeaponSwitchState s{};
        s.cadenceCounter = 7;
        auto n = requestWeapon(s, 2);
        assert(n.current == 2);
        assert(n.fireMode == 1);
        assert(n.phase == HudPhase::Raise);
        assert(n.cadenceCounter == 7);
        assert(switchPreservesCadenceCounter(s, n));
        assert(sameInputWeaponSeenByFire(0xFF, 2) == 2);
    }

    {
        WeaponSwitchState s{0,0xFF,2,HudPhase::Idle,9,5};
        auto n = requestWeapon(s, 3);
        assert(n.current == 0);
        assert(n.pending == 3);
        assert(n.phase == HudPhase::Lower);
        assert(n.cadenceCounter == 5);
        assert(sameInputWeaponSeenByFire(0, 3) == 0);
    }

    {
        WeaponSwitchState s{0,1,2,HudPhase::Lower,3,9};
        auto n = requestWeapon(s, 2);
        assert(n.pending == 2);
        assert(n.phase == HudPhase::Lower);
        n = requestWeapon(n, 0); // same as current: pending remains 2
        assert(n.pending == 2);
        assert(n.current == 0);
    }

    {
        WeaponSwitchState s{2,3,1,HudPhase::Lower,1,4};
        auto n = lowerOne(s);
        assert(n.hudPos == 0);
        assert(n.current == 3);
        assert(n.fireMode == 2);
        assert(n.phase == HudPhase::Raise);
        assert(n.cadenceCounter == 4);
        assert(weapon3CanFireOnCommitFrame(true, n.cadenceCounter));
    }

    {
        WeaponSwitchState s{3,0xFF,2,HudPhase::Raise,8,2};
        auto n = raiseOne(s, 9);
        assert(n.hudPos == 9);
        assert(n.phase == HudPhase::Idle);
    }

    assert(!weapon3CanFireOnCommitFrame(false, 10));
    assert(!weapon3CanFireOnCommitFrame(true, 0));

    return 0;
}
