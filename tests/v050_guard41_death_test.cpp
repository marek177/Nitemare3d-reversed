#include "re/N3DV050GuardDeathOutcome.hpp"
#include <cassert>

using namespace n3d::re::v050;

int main() {
    static_assert(nextRngState(kRng16.before) == kRng16.after);
    static_assert(rng15(kRng16.after) == kRng16.result);
    static_assert(kRng16.result % 7 == kRng16.mod7);
    static_assert(!kRng16.accepted);

    static_assert(nextRngState(kRng17.before) == kRng17.after);
    static_assert(rng15(kRng17.after) == kRng17.result);
    static_assert(kRng17.result % 7 == kRng17.mod7);
    static_assert(!kRng17.accepted);

    static_assert(nextRngState(kRng18.before) == kRng18.after);
    static_assert(rng15(kRng18.after) == kRng18.result);
    static_assert(kRng18.result % 7 == 0);
    static_assert(kRng18.accepted);

    static_assert(kGuard41.guardIndex == 41);
    static_assert(kGuard41.hpBefore == 111 && kGuard41.hpAfter == 0);
    static_assert(kGuard41.scoreBefore == 0 && kGuard41.scoreAfter == 100);
    static_assert(kGuard41.mapMarkerBefore == 0xA5 && kGuard41.mapMarkerAfter == 0);
    static_assert(kGuard41.stateBefore == 0x06 && kGuard41.stateAfter == 0x00);
    static_assert(kGuard41.nextStateBefore == 0x05 && kGuard41.nextStateAfter == 0x09);
    static_assert(kGuard41.timerBefore == 2 && kGuard41.timerAfter == 3);

    assert(kDeathTrace.cpuInstructions == 3642);
    assert(kDeathTrace.totalEvents == 12707);
    assert(kDeathTrace.userStop);
    return 0;
}
