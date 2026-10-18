#include "re/N3DV043RuntimeClosure.hpp"
#include <cassert>
using namespace n3d::re::v043;

int main() {
    {
        const auto oldDancers = guardInit(GuardInitFamily::Old19, 0x21, false);
        const auto newDancers = guardInit(GuardInitFamily::New26, 0x21, false);
        assert(oldDancers.state == 7 && oldDancers.nextState == 2);
        assert(newDancers.state == 0 && newDancers.nextState == 0);
        const auto alienOld = guardInit(GuardInitFamily::Old19, 0x1F, false);
        const auto alienNew = guardInit(GuardInitFamily::New26, 0x1F, false);
        assert(alienOld.state == 7 && alienOld.nextState == 2);
        assert(alienNew.state == 7 && alienNew.nextState == 2);
    }

    {
        const auto wake = areaWake(0, 3, 3, 7, true, 29);
        assert(wake.accepted && wake.rngConsumed && wake.timer == 5 && wake.state == 1);
        assert(!areaWake(0, 3, 4, 7, true, 29).accepted);
        assert(!areaWake(0, 3, 3, 0, true, 29).accepted);
    }

    assert(guardContactDamage(0x08, 5, 1, 0, 1, 7) == 7);
    assert(guardContactDamage(0x09, 5, 1, 0, 1, 31) == 15);
    assert(guardContactDamage(0x0B, 5, 1, 0, 1, 0) == 5);
    assert(guardContactDamage(0x16, 5, 1, 0, 1, 0) == 33);
    assert(guardContactDamage(0x16, 5, 3, 0, 1, 0) == 100);
    assert(guardContactDamage(0x21, 5, 1, 0, 1, 0) == 10);
    assert(guardContactDamage(0x19, 5, 1, 0, 2, 0) == 200);

    static_assert(kDos12E1M1DoorUse.recordIndex == 8);
    static_assert(kDos12E1M1DoorUse.stateBefore == 1);
    static_assert(kDos12E1M1DoorUse.stateAfter == 2);
    static_assert(kDos12E1M1DoorUse.flagBefore == 0);
    static_assert(kDos12E1M1DoorUse.flagAfter == 1);

    static_assert(kPitDivisorObserved == 65535);
    static_assert(kExitBsfDecodedBytes == 474);
    static_assert(kExitBsfXorPeriod == 52);
    static_assert(kExitBsfPrintedBytes == 473);
    static_assert(kNormalDosExitCode == 0);
    static_assert(kLateBsfOpenErrorExitCode == 1);
    static_assert(kObservedNormalDosShutdown.front() == ShutdownStage::SetVideoMode3);
    static_assert(kObservedNormalDosShutdown.back() == ShutdownStage::DosExit0);

    return 0;
}
