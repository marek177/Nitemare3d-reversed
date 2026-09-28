#include "game/CombatSystem.hpp"
#include "game/DifficultySystem.hpp"
#include "game/InventoryRuntime.hpp"
#include "game/RecoveredAnimatedWalls.hpp"
#include "game/RecoveredRuntime.hpp"
#include "game/RecoveredTriggerControl.hpp"

#include <cassert>
#include <cstdint>

using namespace nitemare3d::game;

int main() {
    // Wall-property/class facts recovered from the executable and data tables.
    static_assert(nitemare3d::re::kWallDynamicDoor == 0x08);
    static_assert(kWallPropertyExplodable == 0x10);
    static_assert(n3d::recovered::kWallPropertyTrigger == 0x40);
    static_assert(static_cast<std::uint8_t>(RecoveredWallClass::ExplodableWall1) == 0x2E);
    static_assert(static_cast<std::uint8_t>(RecoveredWallClass::ExplodableWall2) == 0x2F);
    static_assert(static_cast<std::uint8_t>(n3d::recovered::TriggerWallClass::Trigger1) == 0x47);
    static_assert(static_cast<std::uint8_t>(n3d::recovered::TriggerWallClass::Trigger2) == 0x48);

    // Inventory, key gates, and the credential for the SECRET panel.
    static_assert(kAllPentagramsMask == 0x0F);
    static_assert(kWarpKeyClassBase == 0x19);
    static_assert(kWarpKeyClassLast == 0x1C);
    assert(warpKeyBitForClass(0x19) == 0);
    assert(warpKeyBitForClass(0x1C) == 3);
    assert((1u << warpKeyBitForClass(0x19)) == 0x01);
    assert((1u << warpKeyBitForClass(0x1C)) == 0x08);
    static_assert(kSecretPanelObjectClass == 0x03);
    static_assert(kSecretPanelObjectId == 0x62);
    static_assert(kSecretPanelRequiredIdCardObjectId == 0x09);
    assert(hasSecretPanelCredential(0x01));
    assert(!hasSecretPanelCredential(0x02));
    assert(hasIdCard(0x02, IdCardBit::Yellow));

    // Player/combat globals.
    static_assert(nitemare3d::re::kPlayerWorldXGlobal == 0x4BF6);
    static_assert(nitemare3d::re::kPlayerWorldYGlobal == 0x4BF8);
    static_assert(kActiveWeaponGlobal == 0x4C23);
    static_assert(kDifficultyGlobal == 0x4C14);
    static_assert(kNormalAmmoCap == 100);
    static_assert(kSignedAmmoPositiveMax == 127);

    // Difficulty transforms: 0=easier, 1=baseline, 2=harder.
    assert(scalePlayerDamageByDifficulty(10, Difficulty::Easier) == 20);
    assert(scalePlayerDamageByDifficulty(10, Difficulty::Baseline) == 10);
    assert(scalePlayerDamageByDifficulty(10, Difficulty::Harder) == 5);
    assert(scaleEnemyDamageByDifficulty(10, Difficulty::Easier) == 5);
    assert(scaleEnemyDamageByDifficulty(10, Difficulty::Baseline) == 10);
    assert(scaleEnemyDamageByDifficulty(10, Difficulty::Harder) == 20);

    return 0;
}
