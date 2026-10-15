#include "re/N3DV026GuardRngCoupling.hpp"

#include <cassert>
#include <cstdint>
#include <initializer_list>

int main() {
    using namespace n3d::re::v026;

    static_assert(kDos20RngCoupling.size() == 22);
    static_assert(countAssignedConsumers() == 22);
    static_assert(countConfirmedCouplings() == 18);

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

    constexpr auto* wake = couplingFor(0x5582);
    static_assert(wake != nullptr);
    static_assert(wake->consumer == RngConsumer::GuardWakeTimer);
    static_assert(wake->confidence == Confidence::Confirmed);
    static_assert(isExactlyOneDraw(0x5582));
    for (auto caller : {0x8860, 0x886C, 0x887C}) {
        const auto* entry = couplingFor(static_cast<std::uint16_t>(caller));
        assert(entry != nullptr);
        assert(entry->consumer == RngConsumer::IncomingDamageMasked);
        assert(entry->drawCount == DrawCountModel::ExactlyOne);
        assert(entry->confidence == Confidence::Confirmed);
    }
    constexpr auto* projected = couplingFor(0xB276);
    static_assert(projected != nullptr);
    static_assert(projected->consumer == RngConsumer::ProjectedAnimationVariant);
    static_assert(projected->drawCount == DrawCountModel::VariableRejectionLoop);
    static_assert(projected->confidence == Confidence::Confirmed);
    static_assert(!isExactlyOneDraw(0xB276));
    static_assert(couplingFor(0x9FE3)->drawCount == DrawCountModel::VariableRejectionLoop);
    static_assert(couplingFor(0xA047)->consumer == RngConsumer::ResourceTableVariant);
    static_assert(couplingFor(0x9C98)->consumer == RngConsumer::GuardSfxVariant);
    static_assert(couplingFor(0x9CC2)->consumer == RngConsumer::GuardSfxVariant);
    static_assert(couplingFor(0x9D6E)->consumer == RngConsumer::GuardSfxVariant);
    static_assert(couplingFor(0x9F0C)->consumer == RngConsumer::GuardSfxVariant);
    static_assert(couplingFor(0x9F36)->consumer == RngConsumer::GuardSfxVariant);
    static_assert(couplingFor(0x9A68)->consumer == RngConsumer::SceneEffectPosition);
    static_assert(couplingFor(0x9A77)->consumer == RngConsumer::SceneEffectPosition);
    static_assert(couplingFor(0xA12B)->consumer == RngConsumer::SceneEffectTimer);

    assert(couplingFor(0x1234) == nullptr);
    return 0;
}
