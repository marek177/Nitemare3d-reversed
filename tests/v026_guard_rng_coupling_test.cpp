#include "re/N3DV026GuardRngCoupling.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v026;

    static_assert(kDos20RngCoupling.size() == 20);
    static_assert(countAssignedConsumers() == 7);
    static_assert(countConfirmedCouplings() == 3);

    constexpr auto* anim = couplingFor(0x2478);
    static_assert(anim != nullptr);
    static_assert(anim->consumer == RngConsumer::AnimationVariant);
    static_assert(anim->drawCount == DrawCountModel::VariableRejectionLoop);
    static_assert(anim->confidence == Confidence::Confirmed);

    constexpr auto* blocked = couplingFor(0x525E);
    static_assert(blocked != nullptr);
    static_assert(blocked->consumer == RngConsumer::GuardBlockedAxisFlip);
    static_assert(blocked->confidence == Confidence::Confirmed);
    static_assert(isStateBound(0x525E, 0x06));
    static_assert(isExactlyOneDraw(0x525E));

    constexpr auto* s13 = couplingFor(0x58A7);
    static_assert(s13 != nullptr);
    static_assert(s13->consumer == RngConsumer::GuardState13Timer);
    static_assert(isStateBound(0x58A7, 0x13));
    static_assert(isExactlyOneDraw(0x58A7));

    constexpr auto* planner = couplingFor(0x5666);
    static_assert(planner != nullptr);
    static_assert(planner->consumer == RngConsumer::GuardPlanner);
    static_assert(planner->confidence == Confidence::Strong);

    constexpr auto* unknown = couplingFor(0xB276);
    static_assert(unknown != nullptr);
    static_assert(unknown->consumer == RngConsumer::Unassigned);
    static_assert(unknown->confidence == Confidence::Open);

    assert(couplingFor(0x1234) == nullptr);
    return 0;
}
