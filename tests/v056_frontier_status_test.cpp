#include "re/N3DV056FrontierStatus.hpp"
#include <cassert>
using namespace n3d::re::v056;

int main() {
    static_assert(kRecentClosures.dos20StaticStructuralClosed);
    static_assert(kRecentClosures.dos12Guard41DeathOutcomeClosed);
    static_assert(kRecentClosures.dos20TimerRngBranchClosed);
    static_assert(kRecentClosures.dos20BasicProjectileLifecycleClosedControlled);
    static_assert(kRecentClosures.win16AllFiveReachE1M1);
    static_assert(kRecentClosures.dosHudReindexClosedStatic);
    static_assert(kRecentClosures.win110WeaponClass36ClosedStatic);
    static_assert(kRecentClosures.demoSeedGateClosedStatic);
    static_assert(kRecentClosures.crossBuildMarkerAbEffectObserved);

    static_assert(!kOpen.fullDemoRngLedger);
    static_assert(!kOpen.demoEofExact);
    static_assert(!kOpen.naturalE2M10ProjectileAba);
    static_assert(!kOpen.saveLoadFirstPostLoadFrame);
    static_assert(!kOpen.framebufferPaletteZeroDiff);
    static_assert(!kOpen.win16GameplayTimingParity);
    static_assert(!kOpen.exactAudioParity);
    static_assert(!kOpen.strictOriginalVsPortAcceptance);
    static_assert(noStrictParityClaim());

    assert(noStrictParityClaim());
    return 0;
}
