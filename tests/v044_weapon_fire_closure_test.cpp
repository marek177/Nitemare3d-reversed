#include "re/N3DV044WeaponFireClosure.hpp"
#include <cassert>

using namespace n3d::re::v044;

int main() {
    static_assert(kThresholds[0] == 2);
    static_assert(kThresholds[1] == 1);
    static_assert(kThresholds[2] == 3);
    static_assert(kThresholds[3] == 1);
    static_assert(thresholdFor(Build::Dos12, 0xFF) == 0x33);
    static_assert(thresholdFor(Build::Dos20, 0xFF) == 0x65);
    static_assert(thresholdFor(Build::Win110, 0xFF) == 0x03);

    assert(cadenceSlowTick(0xFE) == 0xFF);
    assert(cadenceSlowTick(0xFF) == 0xFF);

    {
        const auto c = cadenceAttempt(Build::Dos20, 3, 1, false);
        assert(c.accepted && c.nextCounter == 0);
    }
    {
        const auto c = cadenceAttempt(Build::Dos20, 0, 2, false);
        assert(!c.accepted && c.nextCounter == 2);
    }

    {
        FireInput in{Build::Dos20,0,2,true,true,2,5,0,false};
        const auto r=attemptFire(in);
        assert(r.reason==FireReason::Jam && r.nextCounter==0 && r.nextAmmo==5);
    }
    {
        FireInput in{Build::Dos20,0,2,true,false,2,0,0,false};
        const auto r=attemptFire(in);
        assert(r.reason==FireReason::NoAmmo && r.nextCounter==0 && r.nextAmmo==0);
        assert(r.ammoHelperCalled);
    }
    {
        FireInput in{Build::Dos20,3,1,false,false,2,5,8,false};
        const auto r=attemptFire(in);
        assert(r.reason==FireReason::PoolFull && r.nextCounter==0);
        assert(r.nextAmmo==5 && !r.ammoHelperCalled);
    }
    {
        FireInput in{Build::Dos20,3,1,false,false,2,5,7,false};
        const auto r=attemptFire(in);
        assert(r.reason==FireReason::ProjectileIssued && r.shotSuccess);
        assert(r.nextAmmo==4 && r.nextOccupiedProjectileSlots==8);
    }
    {
        FireInput in{Build::Dos20,2,3,true,false,1,2,8,false};
        const auto r=attemptFire(in);
        assert(r.reason==FireReason::HitscanIssued && r.shotSuccess);
        assert(r.nextAmmo==1);
    }
    {
        FireInput in{Build::Dos20,1,1,true,false,2,0,0,true};
        const auto r=attemptFire(in);
        assert(r.reason==FireReason::ProjectileIssued);
        assert(r.nextAmmo==0);
    }

    // Build-specific 0xFF overread can change whether cadence is consumed before FIRE rejects.
    {
        FireInput dos{Build::Dos20,0xFF,3,true,false,2,5,0,false};
        const auto r=attemptFire(dos);
        assert(r.reason==FireReason::CadenceDenied && r.nextCounter==3);
    }
    {
        FireInput win{Build::Win110,0xFF,3,true,false,2,5,0,false};
        const auto r=attemptFire(win);
        assert(r.reason==FireReason::NoSelectedWeapon && r.nextCounter==0);
    }

    static_assert(ammoPoolSelector(0)==0);
    static_assert(ammoPoolSelector(3)==0);
    static_assert(ammoPoolSelector(1)==1);
    static_assert(ammoPoolSelector(2)==2);
    static_assert(isAutomaticHeldFireWeapon(3));
    static_assert(!isAutomaticHeldFireWeapon(2));

    return 0;
}
