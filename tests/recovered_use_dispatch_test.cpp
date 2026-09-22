#include "game/RecoveredUseDispatch.hpp"

#include <cassert>

using namespace nitemare3d::re;

int main() {
    // A door wins even if a panel or warp class is also present in the cell.
    assert(useRoute(0x08, 0x19, 0x03) == UseRoute::Door);
    assert(useRoute(0, 0x09, 0x03) == UseRoute::LevelExit);
    assert(useRoute(0, 0x0A, 0x00) == UseRoute::LevelExit);
    assert(useRoute(0, 0x19, 0x03) == UseRoute::Warp);
    assert(useRoute(0, 0x00, 0x03) == UseRoute::Panel);
    assert(useRoute(0, 0x05, 0x28) == UseRoute::Wall05);
    assert(useRoute(0, 0x00, 0x28) == UseRoute::Push);
    assert(useRoute(0, 0x00, 0x00, 0x08) == UseRoute::ObjectFlagged);
    assert(useRoute(0, 0x00, 0x00) == UseRoute::None);

    assert(doorUseGate(0x33, 2, 0, 4) == DoorUseGate::MissingColourKey);
    assert(doorUseGate(0x38, 2, 4, 0) == DoorUseGate::Activate);
    assert(doorUseGate(0x39, 2, 4, 0) == DoorUseGate::MissingIdCard);
    assert(doorUseGate(0x3A, 2, 0, 4) == DoorUseGate::Activate);
    assert(doorUseGate(0x3B, 0, 0xFF, 0xFF) == DoorUseGate::RemoteOnly);
    assert(doorUseGate(0x3C, 0, 0xFF, 0xFF) == DoorUseGate::RemoteOnly);
    assert(doorUseGate(0x33, 8, 0xFF, 0xFF) == DoorUseGate::InvalidKeyIndex);
    assert(doorUseGate(0x32, 8, 0, 0) == DoorUseGate::Activate);

    assert(warpFamily(0x0D) == WarpFamily::Paired);
    assert(warpFamily(0x15) == WarpFamily::Special);
    assert(warpFamily(0x19) == WarpFamily::ColourKey);
    assert(warpFamily(0x24) == WarpFamily::Elevator);
    assert(warpFamily(0x2C) == WarpFamily::Reserved);
    assert(warpFamily(0x2D) == WarpFamily::None);
    assert(colourWarpUnlocked(0x19, 0x01));
    assert(colourWarpUnlocked(0x1C, 0x08));
    assert(!colourWarpUnlocked(0x1C, 0x04));
    assert(!colourWarpUnlocked(0x18, 0xFF));
    assert(!otherSidePortalUnlocked(0x15, 0x07));
    assert(otherSidePortalUnlocked(0x15, 0x0F));
    assert(!otherSidePortalUnlocked(0x16, 0x0F));
}
