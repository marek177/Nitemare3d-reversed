#include "game/GuardSystem.hpp"
#include "game/ObjectSystem.hpp"
#include "re/N3DV013Facts_2026_09_26.hpp"
#include "re/RuntimeAddresses.hpp"

#include <cassert>
#include <cstddef>

int main() {
    namespace game = nitemare3d::game;
    namespace facts = nitemare3d::re::v013_20260926;
    namespace addr = nitemare3d::re;

    static_assert(game::kPushableObjectType == 0x28);
    static_assert(sizeof(game::PushRuntimeRecord) == 6);
    static_assert(game::kPushCapacity == 12);
    static_assert(game::pushDistanceForCompletedMove() == 64);

    static_assert(game::pushDirectionForOctant(0).dx == 0);
    static_assert(game::pushDirectionForOctant(0).dy == -8);
    static_assert(game::pushDirectionForOctant(2).dx == 8);
    static_assert(game::pushDirectionForOctant(4).dy == 8);
    static_assert(game::pushDirectionForOctant(6).dx == -8);

    constexpr game::PushRuntimeRecord idle{0, 0, 0, 0, 0};
    constexpr game::PushRuntimeRecord moving{0, 8, 0, 3, 0};
    static_assert(game::canStartPush(idle, 0x00));
    static_assert(!game::canStartPush(idle, 0x02));
    static_assert(!game::canStartPush(moving, 0x00));

    static_assert(game::guardDirectionalStep(0, 0).dy == -8);
    static_assert(game::guardDirectionalStep(2, 0).dx == 8);
    static_assert(game::guardDirectionalStep(2, 2).dx == 16);
    static_assert(game::guardDirectionalStep(6, 2).dx == -16);

    static_assert(game::guardInitialProfile(0x08).perceptionMode == 0);
    static_assert(game::guardInitialProfile(0x12).strategy == 3);
    static_assert(game::guardInitialProfile(0x15).nextState == 0);
    static_assert(game::guardInitialProfile(0x19).strategy == 4);
    static_assert(game::guardInitialProfile(0x19).state == 0x0E);
    static_assert(game::guardInitialProfile(0x21).state == 0);
    static_assert(game::guardInitialProfile(0x21).nextState == 0);

    static_assert(addr::kPlayerAngle == 0x4BEA);
    static_assert(addr::kPlayerOctant == 0x4BEC);
    static_assert(addr::kPlayerSubsector == 0x4BEE);
    static_assert(addr::kPlayerDirectionMask == 0x4BF0);
    static_assert(addr::kPlayerTrigA == 0x4C46);
    static_assert(addr::kPlayerTrigB == 0x4C48);

    static_assert(facts::kDosDoorRecordSize == 0x12);
    static_assert(facts::kDosPanelRecordSize == 0x0E);
    static_assert(facts::kDosPushRecordSize == 0x06);
    static_assert(facts::frontCellDelta(0) == -64);
    static_assert(facts::frontCellDelta(1) == 1);
    static_assert(facts::pushDistanceUnits() == 64);

    assert(facts::kDos20CoreAnchors.front().offset == 0x0052);
    assert(facts::kDos20CoreAnchors.back().offset == 0x0FBE);
    return 0;
}
