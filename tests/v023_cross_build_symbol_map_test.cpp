#include "re/N3DV023CrossBuildSymbolMap.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v023;

    static_assert(hasAddress(BehaviorId::HandlePlayerUse, BuildId::DosV20));
    static_assert(!hasAddress(BehaviorId::HandlePlayerUse, BuildId::Win16V110));

    constexpr auto* useDos =
        symbolFor(BehaviorId::HandlePlayerUse, BuildId::DosV20);
    static_assert(useDos != nullptr);
    static_assert(useDos->address.segment == 0x1000);
    static_assert(useDos->address.offset == 0x0704);
    static_assert(useDos->confidence == Confidence::Confirmed);

    constexpr auto* guardWin =
        symbolFor(BehaviorId::GuardStateDispatch, BuildId::Win16V110);
    static_assert(guardWin != nullptr);
    static_assert(guardWin->address.segment == 0x0003);
    static_assert(guardWin->address.offset == 0x7B55);
    static_assert(guardWin->confidence == Confidence::Confirmed);

    constexpr auto* guardDos =
        symbolFor(BehaviorId::GuardStateDispatch, BuildId::DosV20);
    static_assert(guardDos != nullptr);
    static_assert(guardDos->address.offset == 0x59F0);
    static_assert(guardDos->confidence == Confidence::Strong);

    static_assert(needsCrossBuildPairing(BehaviorId::GuardStateDispatch));
    static_assert(needsCrossBuildPairing(BehaviorId::HandlePlayerUse));
    static_assert(needsCrossBuildPairing(BehaviorId::HudDispatch));

    static_assert(!isConfirmedPair(BehaviorId::GuardStateDispatch));
    static_assert(!isConfirmedPair(BehaviorId::HandlePlayerUse));

    const auto* missing =
        symbolFor(BehaviorId::MenuDispatch, BuildId::DosV20);
    assert(missing == nullptr);

    return 0;
}
