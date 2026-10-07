#include "re/N3DV024GuardStateGraph.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v024;

    static_assert(kWin16Dispatcher.firstState == 0x00);
    static_assert(kWin16Dispatcher.lastState == 0x15);
    static_assert(kWin16V110States.size() == 22);

    constexpr auto* s0 = win16State(0x00);
    static_assert(s0 != nullptr);
    static_assert(s0->handlerOffset == 0x7BA2);
    static_assert(returnsViaNextState(0x00));

    static_assert(hasFixedTransition(0x01, 0x02));
    static_assert(hasFixedTransition(0x06, 0x03));
    static_assert(hasFixedTransition(0x10, 0x0F));
    static_assert(hasFixedTransition(0x11, 0x07));

    static_assert(returnsViaNextState(0x12));
    static_assert(returnsViaNextState(0x15));

    constexpr auto* s15 = win16State(0x15);
    static_assert(s15 != nullptr);
    static_assert(s15->handlerOffset == 0x807E);
    static_assert(s15->controlFlowConfidence == Confidence::Confirmed);
    static_assert(s15->semanticConfidence == Confidence::Confirmed);

    constexpr auto* s03 = win16State(0x03);
    static_assert(s03 != nullptr);
    static_assert(s03->semanticConfidence == Confidence::Partial);
    static_assert(!semanticNameSafeToAssign(0x03));
    static_assert(semanticNameSafeToAssign(0x15));

    assert(win16State(0x16) == nullptr);

    static_assert(kDos20Dispatcher.offset == 0x59F0);
    static_assert(kDos20Dispatcher.confidence == Confidence::Strong);

    return 0;
}
