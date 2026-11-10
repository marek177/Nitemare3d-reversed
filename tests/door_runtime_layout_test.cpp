#include "re/DoorRuntimeLayout_2026_09_28.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>

int main() {
    using namespace n3d::re::door20260928;

    static_assert(kDoorRuntimeBase == 0x9DD6);
    static_assert(kDoorRuntimeStride == 22);
    static_assert(kDoorRuntimeCapacity == 64);
    static_assert(kDoorRuntimeSaveBytes == 0x580);
    static_assert(kDoorMotionStep == 2);
    static_assert(kDoorOpenCountdown == 32);
    static_assert(kDoorObstructedRetryCountdown == 4);
    static_assert(kDoorOpenSfx == 0x25);
    static_assert(kDoorCloseSfx == 0x26);

    static_assert(sizeof(DoorRuntimeRecord) == 22);
    static_assert(offsetof(DoorRuntimeRecord, movingWallA) == 0x00);
    static_assert(offsetof(DoorRuntimeRecord, movingWallB) == 0x04);
    static_assert(offsetof(DoorRuntimeRecord, mapCell) == 0x08);
    static_assert(offsetof(DoorRuntimeRecord, state) == 0x0C);
    static_assert(offsetof(DoorRuntimeRecord, autoCloseTimer) == 0x0E);
    static_assert(offsetof(DoorRuntimeRecord, anchorX) == 0x10);
    static_assert(offsetof(DoorRuntimeRecord, anchorY) == 0x12);
    static_assert(offsetof(DoorRuntimeRecord, soundLatch) == 0x14);
    static_assert(offsetof(DoorRuntimeRecord, unusedPadding) == 0x15);

    assert(allowsPlayerPassage(DoorControllerState::Open));
    assert(allowsPlayerPassage(DoorControllerState::CorpseHoldOpen));
    assert(!allowsPlayerPassage(DoorControllerState::Closed));
    assert(!allowsPlayerPassage(DoorControllerState::Opening));
    assert(!allowsPlayerPassage(DoorControllerState::Closing));

    assert(canManualOrRemoteToggle(DoorControllerState::Open));
    assert(canManualOrRemoteToggle(DoorControllerState::Closed));
    assert(!canManualOrRemoteToggle(DoorControllerState::CorpseHoldOpen));

    assert(autoCloseCountdownRuns(DoorControllerState::Open));
    assert(!autoCloseCountdownRuns(DoorControllerState::Closed));
    return 0;
}
