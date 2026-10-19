#include "re/N3DV058GuardState09.hpp"
using namespace n3d::re::v058;
int main() {
    static_assert(kGuard41State09.stateBefore == 9);
    static_assert(kGuard41State09.stateAfter == 10);
    static_assert(kGuard41State09.worldFlagsBefore == kGuard41State09.worldFlagsAfter);
    static_assert(kGuard41State09.worldClass == 0x0F);
    static_assert(kGuard41State09.rngBefore == 0xAEA69ED3u);
    static_assert(kGuard41State09.rngAfter == 0x12DBCE4Au);
    static_assert(kGuard41State09.rngResult == 4827);
    static_assert(kGuard41State09.rngMod3 == 0);
    static_assert(kGuard41State09.cpuInstructions == 4235);
    static_assert(kGuard41State09.allEvents == 34575);
    static_assert(kState0AAnd0BDispatchToCommonEpilogueDos12);
    static_assert(kState0AAnd0BDispatchToCommonEpilogueDos20);
    static_assert(!kDos20NaturalGuard41State09Observed);
    static_assert(!kCompleteDeathPoolCleanupClosed);
    return 0;
}
