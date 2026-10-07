#include "re/N3DV027ProjectileLifecycle.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v027;

    static_assert(hasConfirmedAnchor(BuildId::DosV20, ProjectilePhase::Allocate));
    static_assert(hasConfirmedAnchor(BuildId::DosV20, ProjectilePhase::FlyingUpdate));
    static_assert(hasConfirmedAnchor(BuildId::DosV20, ProjectilePhase::RenderProject));

    constexpr auto* dosAlloc =
        anchorFor(BuildId::DosV20, ProjectilePhase::Allocate);
    static_assert(dosAlloc != nullptr);
    static_assert(dosAlloc->segment == 0x0800);
    static_assert(dosAlloc->offset == 0x7EDE);

    constexpr auto* winCollision =
        anchorFor(BuildId::Win16V110, ProjectilePhase::Collision);
    static_assert(winCollision != nullptr);
    static_assert(winCollision->offset == 0x9B64);
    static_assert(winCollision->confidence == Confidence::Confirmed);

    constexpr auto* lifecycle = invariant("lifecycle_0_1_2_0");
    static_assert(lifecycle != nullptr);
    static_assert(lifecycle->confidence == Confidence::Confirmed);

    static_assert(implementationSafe("guard_hit_tolerance_9"));
    static_assert(implementationSafe("impact_sets_flag_0x10"));
    static_assert(!implementationSafe("pool_full_preserves_ammo"));
    static_assert(!implementationSafe("stale_projection_cache_affects_damage"));

    const auto* missing =
        anchorFor(BuildId::DosV20, ProjectilePhase::SaveLoad);
    assert(missing == nullptr);

    return 0;
}
