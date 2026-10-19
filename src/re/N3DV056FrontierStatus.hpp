#pragma once
#include <cstdint>

namespace n3d::re::v056 {

struct ClosureSnapshot {
    bool dos20StaticStructuralClosed{};
    bool dos12Guard41DeathOutcomeClosed{};
    bool dos20TimerRngBranchClosed{};
    bool dos20BasicProjectileLifecycleClosedControlled{};
    bool win16AllFiveReachE1M1{};
    bool dosHudReindexClosedStatic{};
    bool win110WeaponClass36ClosedStatic{};
    bool demoSeedGateClosedStatic{};
    bool crossBuildMarkerAbEffectObserved{};
};

inline constexpr ClosureSnapshot kRecentClosures{
    true,true,true,true,true,true,true,true,true
};

struct OpenFrontier {
    bool fullDemoRngLedger{};
    bool demoEofExact{};
    bool naturalE2M10ProjectileAba{};
    bool saveLoadFirstPostLoadFrame{};
    bool framebufferPaletteZeroDiff{};
    bool win16GameplayTimingParity{};
    bool exactAudioParity{};
    bool strictOriginalVsPortAcceptance{};
};

inline constexpr OpenFrontier kOpen{
    false,false,false,false,false,false,false,false
};

constexpr bool noStrictParityClaim() noexcept {
    return !kOpen.strictOriginalVsPortAcceptance &&
           !kOpen.framebufferPaletteZeroDiff &&
           !kOpen.fullDemoRngLedger;
}

} // namespace n3d::re::v056
