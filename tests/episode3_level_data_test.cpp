#include "game/Episode3LevelData.hpp"

#include <cassert>

int main() {
    using namespace n3d;

    static_assert(Episode3Level3Anchors.size() == 11);
    static_assert(E3M3RedKeyObjectId == 0x05);
    static_assert(E3M3GreenKeyObjectId == 0x06);
    static_assert(E3M3BlueKeyObjectId == 0x07);
    static_assert(E3M3YellowIdCardObjectId == 0x0A);

    bool sawGreenKey = false;
    bool sawRedKey = false;
    bool sawYellowCard = false;
    bool sawBlueKey = false;
    bool sawFinalBlueLock = false;

    for (const auto& anchor : Episode3Level3Anchors) {
        if (anchor.kind == LevelAnchorKind::KeyPickup && anchor.x == 36 && anchor.y == 30 &&
            anchor.token == AccessToken::GreenKey) sawGreenKey = true;
        if (anchor.kind == LevelAnchorKind::KeyPickup && anchor.x == 27 && anchor.y == 17 &&
            anchor.token == AccessToken::RedKey) sawRedKey = true;
        if (anchor.kind == LevelAnchorKind::IdCardPickup && anchor.x == 62 && anchor.y == 46 &&
            anchor.token == AccessToken::YellowIdCard) sawYellowCard = true;
        if (anchor.kind == LevelAnchorKind::KeyPickup && anchor.x == 4 && anchor.y == 62 &&
            anchor.token == AccessToken::BlueKey) sawBlueKey = true;
        if (anchor.kind == LevelAnchorKind::KeyLock && anchor.x == 59 && anchor.y == 5 &&
            anchor.token == AccessToken::BlueKey) sawFinalBlueLock = true;
    }

    assert(sawGreenKey);
    assert(sawRedKey);
    assert(sawYellowCard);
    assert(sawBlueKey);
    assert(sawFinalBlueLock);
    return 0;
}
