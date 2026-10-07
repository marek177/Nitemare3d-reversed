#include "re/N3DV021SubsystemEvidence.hpp"

#include <array>
#include <cassert>

int main() {
    using namespace n3d::re::v021;

    static_assert(classifySubsystemAddress(0x5F26) == Subsystem::Guard);
    static_assert(classifySubsystemAddress(0x6914) == Subsystem::Player);
    static_assert(classifySubsystemAddress(0x8230) == Subsystem::Projectile);
    static_assert(classifySubsystemAddress(0x89A2) == Subsystem::InputAction);
    static_assert(classifySubsystemAddress(0x0AEA) == Subsystem::SecretPanel);
    static_assert(classifySubsystemAddress(0x0E50) ==
                  Subsystem::ObjectCandidate);
    static_assert(classifySubsystemAddress(0x7777) == Subsystem::Unknown);

    static_assert(confidenceForAddress(0x8230) == Confidence::Confirmed);
    static_assert(confidenceForAddress(0x5F26) == Confidence::Strong);
    static_assert(confidenceForAddress(0x0E50) == Confidence::Open);

    static_assert(kProjectilePool.base == 0x41B6);
    static_assert(kProjectilePool.size == 0x0150);
    static_assert(kSecretPanelRecord.size == 0x000E);

    constexpr std::array<std::uint16_t, 5> goodTrace{
        0xC150, 0x8230, 0x8142, 0x89A2, 0x8F12
    };
    const auto good = verifyRelativeOrder(
        goodTrace.data(), goodTrace.size(), 0x8230, 0x89A2);
    assert(good.decisive());
    assert(good.orderSatisfied);

    constexpr std::array<std::uint16_t, 4> badTrace{
        0xC150, 0x89A2, 0x8230, 0xC1A8
    };
    const auto bad = verifyRelativeOrder(
        badTrace.data(), badTrace.size(), 0x8230, 0x89A2);
    assert(bad.decisive());
    assert(!bad.orderSatisfied);

    constexpr std::array<std::uint16_t, 2> incompleteTrace{
        0xC150, 0x8230
    };
    const auto incomplete = verifyRelativeOrder(
        incompleteTrace.data(), incompleteTrace.size(), 0x8230, 0x89A2);
    assert(!incomplete.decisive());

    static_assert(kProjectileBeforeFire.confidence == Confidence::Strong);
    static_assert(kObjectMutationOrder.confidence == Confidence::Open);
    static_assert(kExactFastMainOrder.confidence == Confidence::Open);

    return 0;
}
