#include "re/N3DV041LatestStaticEvidence.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::v041;

int main() {
    {
        const MapCell before{0xB7, 0x91};
        const auto after = clearRadioWallOnly(before);
        assert(after.wallId == 0);
        assert(after.objectId == 0x91);
    }

    {
        const auto torn = projectileRearmDeadline(0xFFFFu, 0x0002u, 50u);
        const auto coherent = static_cast<std::uint32_t>(0x00020000u + 50u);
        assert(torn == 0x00030031u);
        assert(coherent == 0x00020032u);
        assert(torn - coherent == 65535u);
    }

    {
        const auto tail = commitOuterTailAfterNested(13u, 100u);
        assert(tail.nextFrame == 14u);
        assert(tail.legacyEpoch == 100u);
    }

    static_assert(kE2M10TwentiethHitOrder[0] == E2M10Stage::PaletteEffect7);
    static_assert(kE2M10TwentiethHitOrder[1] == E2M10Stage::HitCounterIncrement);
    static_assert(kE2M10TwentiethHitOrder[4] == E2M10Stage::NestedScheduler);

    assert(preClassDamageScalar(101, 100, 0) == 8);
    assert(preClassDamageScalar(100, 100, 24) == 24);
    assert(hitscanGenerationMatches(77, 77));
    assert(!hitscanGenerationMatches(76, 77));
    assert(projectileProximityAccepts(9, -9));
    assert(!projectileProximityAccepts(10, 0));

    static_assert(kWorldObjectPool.capacity == 350);
    static_assert(kWorldObjectPool.sourceMaximum == 323);
    static_assert(kGuardPool.capacity == 100 && kGuardPool.sourceMaximum == 99);
    static_assert(kDoorControllerPool.capacity == 64 && kDoorControllerPool.sourceMaximum == 62);
    static_assert(kSecretPanelPool.capacity == 32 && kSecretPanelPool.sourceMaximum == 32);
    static_assert(kSecretPanelPool.reserve == 0);
    static_assert(kPushPool.capacity == 12 && kPushPool.sourceMaximum == 11);

    static_assert(kE2M10DoorControllerCandidates == 60);
    static_assert(kE2M10DoorControllerReserve == 4);
    static_assert(kE3M8SecretPanels == 32);
    static_assert(kSecretPanel64MovementCalls == 32);
    static_assert(kSecretPanel64CleanupCall == 33);

    static_assert(kE1M9InitialGroups.frankenstein == 17);
    static_assert(kE1M9InitialGroups.skeleton == 9);
    static_assert(kE1M9InitialGroups.mrsH == 5);
    static_assert(kE1M9InitialGroups.dancers == 12);

    static_assert(kE1M1ObjectByteDifferencesDosVsWin == 20);
    static_assert(kE1M1PlacedGuardCountDos == 33);
    static_assert(kE1M1PlacedGuardCountWin == 39);
    for (const auto& bank : kDosWinImgAliasBanks) {
        assert(bank.mismatchedAliasPairs == 0);
    }

    return 0;
}
