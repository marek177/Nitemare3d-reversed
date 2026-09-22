#include "game/GuardSystem.hpp"

#include <cassert>
#include <cstddef>

int main() {
    using namespace nitemare3d::game;

    static_assert(sizeof(GuardRuntimeRecord) == 26);
    static_assert(kGuardCapacity == 100);
    static_assert(kGuardSaveSize == 2600);
    static_assert(offsetof(GuardRuntimeRecord, stateTimer) == 0x06);
    static_assert(offsetof(GuardRuntimeRecord, objectSlot) == 0x08);
    static_assert(offsetof(GuardRuntimeRecord, strategy) == 0x0A);
    static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
    static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
    static_assert(offsetof(GuardRuntimeRecord, strength) == 0x10);
    static_assert(offsetof(GuardRuntimeRecord, octant) == 0x11);
    static_assert(offsetof(GuardRuntimeRecord, resultOctant) == 0x12);
    static_assert(kFreshGuardStrength == 0xFF);
    static_assert(kGuardStateCount == 22);
    static_assert(static_cast<unsigned>(GuardState::PainReaction) == 0x15);

    // Original score switch anchors.
    assert(guardScoreForObjectClass(0x08) == 25);    // Bat
    assert(guardScoreForObjectClass(0x11) == 0);     // Dracula
    assert(guardScoreForObjectClass(0x15) == -1000); // Penelope
    assert(guardScoreForObjectClass(0x16) == 1000);  // Dr. Hamerstein
    assert(guardScoreForObjectClass(0x1B) == 100);   // Goldie
    assert(guardScoreForObjectClass(0x1C) == 100);   // Greenie
    assert(guardScoreForObjectClass(0x1D) == 250);   // Demon
    assert(guardScoreForObjectClass(0x20) == 50);    // GUARD25 unknown

    // Classes outside GUARD1..25 use the default score path.
    assert(guardScoreForObjectClass(0x07) == 0);
    assert(guardScoreForObjectClass(0x21) == 0); // includes GUARD26/Dancers path
}
