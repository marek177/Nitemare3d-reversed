#include "game/CombatSystem.hpp"
#include "game/GuardSystem.hpp"
#include "game/ObjectSystem.hpp"
#include "game/ProjectileRuntime.hpp"
#include "re/N3DV017RecoveredFacts.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::game;

    // Verified class x weapon resistance matrix.
    static_assert(damageTransformFor(0x1A, WeaponSelector::MagicWand) ==
                  DamageTransformKind::Divide2);
    static_assert(damageTransformFor(0x1A, WeaponSelector::SilverPistol) ==
                  DamageTransformKind::Immune);
    static_assert(damageTransformFor(0x1E, WeaponSelector::MagicWand) ==
                  DamageTransformKind::Immune);
    static_assert(damageTransformFor(0x18, WeaponSelector::SilverPistol) ==
                  DamageTransformKind::Divide16);
    static_assert(damageTransformFor(0x0F, WeaponSelector::SingleShotLaser) ==
                  DamageTransformKind::Divide256);

    assert(playerDamageAfterResistanceAndDifficulty(
               80, 0x0C, WeaponSelector::SingleShotLaser,
               Difficulty::Baseline) == 10);
    assert(playerDamageAfterResistanceAndDifficulty(
               80, 0x0C, WeaponSelector::SingleShotLaser,
               Difficulty::Easier) == 20);
    assert(playerDamageAfterResistanceAndDifficulty(
               80, 0x0C, WeaponSelector::SingleShotLaser,
               Difficulty::Harder) == 5);
    assert(playerDamageAfterResistanceAndDifficulty(
               100, 0x16, WeaponSelector::MagicWand,
               Difficulty::Baseline, 3) == 3);
    assert(playerDamageAfterResistanceAndDifficulty(
               100, 0x16, WeaponSelector::MagicWand,
               Difficulty::Baseline, 2) == 0);

    const auto ignored = receiveGuardDamage(255, 0, 3);
    assert(ignored.strength == 255 &&
           ignored.disposition == GuardHitDisposition::Ignored);
    const auto pain = receiveGuardDamage(255, 10, 3);
    assert(pain.strength == 245 && pain.resultOctant == 8 &&
           pain.disposition == GuardHitDisposition::Pain);
    const auto lethal = receiveGuardDamage(10, 10, 3);
    assert(lethal.strength == 0 &&
           lethal.disposition == GuardHitDisposition::Lethal);

    static_assert(kDraculaPhase2Reset.objectClass == 0x14);
    static_assert(kDraculaPhase2Reset.strength == 0xFF);
    static_assert(kDraculaPhase2Reset.state == 0x08);
    static_assert(kDraculaPhase2Reset.nextState == 0x02);
    static_assert(kDraculaPhase2Reset.timer == 1);

    const std::uint8_t flags =
        kObjectRuntimePresent | kObjectBlocksMovement | kObjectCreatesGuard;
    assert(objectRuntimePresent(flags));
    assert(objectBlocksMovement(flags));
    assert(objectCreatesGuard(flags));
    assert(!objectHasSpecialTouch(flags));

    const auto hit = projectileGuardCollisionDecision(9, -9, 0, 0);
    assert(hit.hitGuard && hit.enterImpactState);
    const auto miss = projectileGuardCollisionDecision(10, 0, 0, 0);
    assert(!miss.hitGuard && !miss.enterImpactState);
    static_assert(projectileImpactStateValue() ==
                  static_cast<std::uint8_t>(ProjectileSlotState::Impact));

    static_assert(n3d::re::v017::kProjectileSlots == 8);
    static_assert(n3d::re::v017::kProjectileStride == 42);
    return 0;
}
