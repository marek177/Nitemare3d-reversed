#include "game/CombatSystem.hpp"
#include "game/DifficultySystem.hpp"
#include "game/InventoryRuntime.hpp"
#include "game/RecoveredAnimatedWalls.hpp"
#include "game/RecoveredRuntime.hpp"
#include "game/RecoveredTriggerControl.hpp"
#include "game/RecoveredInteractionFacts.hpp"

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

    // USE / interaction closure facts.
    static_assert(kSafeObjectClass == 0x26);
    static_assert(kTrunkObjectClass == 0x27);
    static_assert(kPushObjectClass == 0x28);
    static_assert(kActionObjectClass == 0x29);
    static_assert(kRadioObjectIdEpisode1 == 0x45);
    static_assert(kCancelAction == 0x19);
    static_assert(kFloorSelectAction == 0x1A);
    static_assert(kClimbUpAction == 0x1B);
    static_assert(kClimbDownAction == 0x1C);
    static_assert(kGoDownAction == 0x1D);
    static_assert(climbActionRawWallDelta(kClimbUpAction) == 1);
    static_assert(climbActionRawWallDelta(kClimbDownAction) == -1);
    static_assert(climbActionRawWallDelta(kGoDownAction) == -1);
    static_assert(climbActionRawWallDelta(kCancelAction) == 0);
    static_assert(trunkRewardCode(0) == static_cast<std::uint8_t>(ContainerReward::Health));
    static_assert(trunkRewardCode(1) == static_cast<std::uint8_t>(ContainerReward::Ammo));
    static_assert(trunkRewardCode(2) == static_cast<std::uint8_t>(ContainerReward::MagicEye));
    static_assert(trunkRewardCode(3) == static_cast<std::uint8_t>(ContainerReward::CrystalBall));
    static_assert(trunkRewardCode(4) == static_cast<std::uint8_t>(ContainerReward::RedKey));
    static_assert(safeRewardCode(0) == static_cast<std::uint8_t>(ContainerReward::RedKey));
    static_assert(safeRewardCode(3) == static_cast<std::uint8_t>(ContainerReward::YellowKey));
    static_assert(safeRewardCode(4) == static_cast<std::uint8_t>(ContainerReward::RedIdCard));
    static_assert(safeRewardCode(5) == static_cast<std::uint8_t>(ContainerReward::YellowIdCard));
    static_assert(trunkRewardCode(5) == 0);
    static_assert(safeRewardCode(6) == 0);
    static_assert(isColoredKeyDoorClass(0x33) && isColoredKeyDoorClass(0x38));
    static_assert(!isColoredKeyDoorClass(0x39));
    static_assert(isIdCardDoorClass(0x39) && isIdCardDoorClass(0x3A));
    static_assert(isRemoteDoorClass(0x3B) && isRemoteDoorClass(0x3C));

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
