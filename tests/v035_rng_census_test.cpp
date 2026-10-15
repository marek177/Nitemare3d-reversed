#include "re/N3DV035RngCensus.hpp"

#include <array>
#include <cassert>
#include <cstdint>

int main() {
    namespace v = n3d::re::v035;
    namespace old = n3d::re::v020;
    namespace coupled = n3d::re::v026;

    static_assert(v::censusAndConsumersAgree());
    static_assert(old::kDos20DirectRngCallsites.size() == 22);
    static_assert(coupled::kDos20RngCoupling.size() == 22);
    static_assert(coupled::countAssignedConsumers() == 22);
    static_assert(coupled::countConfirmedCouplings() == 18);
    static_assert(old::isKnownDirectRngCallsite(0x8860));
    static_assert(old::isKnownDirectRngCallsite(0x886C));
    static_assert(old::isKnownDirectRngCallsite(0x887C));
    static_assert(!old::isKnownDirectRngCallsite(0x7777));

    static_assert(v::kDamageClassBranchTargets.size() == 23);
    static_assert(v::kDamageClassBranchTargets[0] == 0x8860);
    static_assert(v::kDamageClassBranchTargets[1] == 0x886C);
    static_assert(v::kDamageClassBranchTargets[2] == 0x886C);
    static_assert(v::kDamageClassBranchTargets[9] == 0x887C);
    static_assert(v::kDamageClassBranchTargets[12] == 0x887C);
    static_assert(v::damageClassTarget(0x08) == 0x8860);
    static_assert(v::damageClassTarget(0x1E) == 0x889D);
    static_assert(!v::damageClassTarget(0x07));
    static_assert(!v::damageClassTarget(0x1F));
    static_assert(v::damageRngCallsite(0x08) == 0x8860);
    static_assert(v::damageRngCallsite(0x09) == 0x886C);
    static_assert(v::damageRngCallsite(0x0A) == 0x886C);
    static_assert(v::damageRngCallsite(0x11) == 0x887C);
    static_assert(v::damageRngCallsite(0x14) == 0x887C);
    static_assert(!v::damageRngCallsite(0x0B));
    static_assert(!v::damageRngCallsite(0x15));
    static_assert(v::maskedIncomingDamage(0x08, 0xFFFF) == 7);
    static_assert(v::maskedIncomingDamage(0x09, 0xFFFF) == 15);
    static_assert(v::maskedIncomingDamage(0x0A, 0xFFFF) == 15);
    static_assert(v::maskedIncomingDamage(0x11, 0xFFFF) == 31);
    static_assert(!v::maskedIncomingDamage(0x0C, 0xFFFF));

    static_assert(v::guardCanEnterState1(0, true, 7));
    static_assert(v::guardCanEnterState1(0, true, 8));
    static_assert(!v::guardCanEnterState1(1, true, 7));
    static_assert(!v::guardCanEnterState1(0, true, 6));
    static_assert(!v::guardCanEnterState1(0, false, 7));
    static_assert(v::guardActivationTimer(32767) == 7);
    static_assert(v::guardActivationTimer(8) == 0);
    static_assert(coupled::couplingFor(0x5582)->consumer ==
                  coupled::RngConsumer::GuardWakeTimer);

    static_assert(v::projectedVariantIndex(0) == 0);
    static_assert(v::projectedVariantIndex(0xFFFF) == 7);
    static_assert(v::projectedVariantRejected(0x0000));
    static_assert(v::projectedVariantRejected(0x0007));
    static_assert(!v::projectedVariantRejected(0x0100));
    static_assert(!v::projectedVariantRejected(0xFF01));
    static_assert(coupled::couplingFor(0xB276)->consumer ==
                  coupled::RngConsumer::ProjectedAnimationVariant);
    static_assert(coupled::couplingFor(0xB276)->drawCount ==
                  coupled::DrawCountModel::VariableRejectionLoop);

    static_assert(v::resourceSelectorModulo7(0) == 0);
    static_assert(v::resourceSelectorModulo7(32767) <= 6);
    static_assert(!v::selectorEqualToRejectedSeven(0));
    static_assert(!v::selectorEqualToRejectedSeven(32767));
    static_assert(v::resourceVariantNeedsRedraw(0));
    static_assert(!v::resourceVariantNeedsRedraw(1));
    for (std::uint32_t x = 0; x <= 32767u; ++x) {
        // Exhaustive domain proof: signed IDIV 7 remainder cannot equal 7.
        assert(v::resourceSelectorModulo7(static_cast<std::uint16_t>(x)) < 7);
        assert(!v::selectorEqualToRejectedSeven(static_cast<std::uint16_t>(x)));
    }
    static_assert(!v::kOriginalRuntimeVerified);
    static_assert(!v::kIndirectRngCensusClosed);
    static_assert(!v::kDemoSeed1FullCallOrderClosed);
    return 0;
}
