#include "re/N3DV053HudWeaponCrossbuild.hpp"
#include <cassert>
using namespace n3d::re::v053;

int main() {
    static_assert(dos20HudIdFromDos19(0) == 0);
    static_assert(dos20HudIdFromDos19(3) == 3);
    static_assert(dos20HudIdFromDos19(4) == 5);
    static_assert(dos20HudIdFromDos19(8) == 9);
    static_assert(kDos20InsertedDamageHudId == 4);

    constexpr auto seq = damageHudSequence(3);
    static_assert(seq[0] == 4 && seq[1] == 4 && seq[2] == 4 && seq[3] == 3);
    static_assert(kDamageHudRegion.x == 256 && kDamageHudRegion.y == 162);
    static_assert(kDamageHudRegion.width == 62 && kDamageHudRegion.height == 36);

    static_assert(kWin110WeaponPickups.size() == 4);
    static_assert(kWin110WeaponPickups[0].mapHighId == 0x25);
    static_assert(kWin110WeaponPickups[3].mapHighId == 0x28);
    static_assert(kWin110WeaponPickups[0].ammoPool == kWin110WeaponPickups[3].ammoPool);
    static_assert(kWin110WeaponPickups[1].ammoPool != kWin110WeaponPickups[2].ammoPool);
    static_assert(ownershipMaskForVariant(0) == 0x01);
    static_assert(ownershipMaskForVariant(3) == 0x08);

    static_assert(!kDosPickupAlgorithmIdenticalToWin16Proven);
    static_assert(!kDamageHudPixelColorClosed);
    assert(seq[3] == 3);
    return 0;
}
