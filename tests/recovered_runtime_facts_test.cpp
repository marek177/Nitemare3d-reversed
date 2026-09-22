#include "game/CombatSystem.hpp"
#include "game/DifficultySystem.hpp"
#include "game/InventoryRuntime.hpp"
#include "game/PlayerRuntime.hpp"
#include "game/RecoveredAnimatedWalls.hpp"
#include "game/RecoveredTriggerControl.hpp"
#include "game/RecoveredWallRuntime.hpp"

#include <cassert>
#include <cstdint>

using namespace nitemare3d::game;

int main() {
    // Wall-property / class facts recovered from NITE3W.EXE.
    static_assert(kWallPropertyDoor == 0x08);
    static_assert(kWallPropertyExplodable == 0x10);
    static_assert(kWallPropertyTrigger == 0x40);
    static_assert(kExplodableWallClass1 == 0x2E);
    static_assert(kExplodableWallClass2 == 0x2F);
    static_assert(kTriggerWallClass1 == 0x47);
    static_assert(kTriggerWallClass2 == 0x48);

    // Inventory / portal masks.
    static_assert(kAllPentagramsMask == 0x0F);
    static_assert(kWarpL1Class == 0x19);
    static_assert(kWarpL4Class == 0x1C);
    assert(warpLRequiredKeyMask(kWarpL1Class) == 0x01);
    assert(warpLRequiredKeyMask(kWarpL4Class) == 0x08);

    // Player/combat globals.
    static_assert(kPlayerXAddress == 0x4BF6);
    static_assert(kPlayerYAddress == 0x4BF8);
    static_assert(kActiveWeaponAddress == 0x4C23);
    static_assert(kDifficultyAddress == 0x4C14);
    static_assert(kNormalAmmoCap == 100);
    static_assert(kSignedAmmoSafeMaximum == 127);

    // Difficulty transforms: 0=easier, 1=baseline, 2=harder.
    assert(scalePlayerToEnemyDamage(10, 0) == 20);
    assert(scalePlayerToEnemyDamage(10, 1) == 10);
    assert(scalePlayerToEnemyDamage(10, 2) == 5);
    assert(scaleEnemyToPlayerDamage(10, 0) == 5);
    assert(scaleEnemyToPlayerDamage(10, 1) == 10);
    assert(scaleEnemyToPlayerDamage(10, 2) == 20);

    return 0;
}
