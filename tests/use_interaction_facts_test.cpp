#include "game/RecoveredInteractionFacts.hpp"

#include <cassert>
#include <cstdint>

using namespace nitemare3d::game;

int main() {
    static_assert(kSafeObjectClass == 0x26);
    static_assert(kTrunkObjectClass == 0x27);
    static_assert(kPushObjectClass == 0x28);
    static_assert(kActionObjectClass == 0x29);
    static_assert(kRadioObjectIdEpisode1 == 0x45);

    static_assert(kCancelAction == 0x19);
    static_assert(kFloorSelectAction == 0x1A);
    static_assert(kClimbUpAction == 0x1B);
    static_assert(kClimbDownAction == 0x1C);
    static_assert(kGoDownAction == 0x1D);
    static_assert(kRemoteOpenCommand == 0x1E);
    static_assert(kRemoteCloseCommand == 0x1F);
    static_assert(kRemoteCannonEnableCommand == 0x20);
    static_assert(kRemoteCannonDisableCommand == 0x21);

    static_assert(climbActionRawWallDelta(kClimbUpAction) == 1);
    static_assert(climbActionRawWallDelta(kClimbDownAction) == -1);
    static_assert(climbActionRawWallDelta(kGoDownAction) == -1);
    static_assert(climbActionRawWallDelta(kCancelAction) == 0);

    static_assert(trunkRewardCode(0) == static_cast<std::uint8_t>(ContainerReward::Health));
    static_assert(trunkRewardCode(1) == static_cast<std::uint8_t>(ContainerReward::Ammo));
    static_assert(trunkRewardCode(2) == static_cast<std::uint8_t>(ContainerReward::MagicEye));
    static_assert(trunkRewardCode(3) == static_cast<std::uint8_t>(ContainerReward::CrystalBall));
    static_assert(trunkRewardCode(4) == static_cast<std::uint8_t>(ContainerReward::RedKey));
    static_assert(trunkRewardCode(5) == 0);

    static_assert(safeRewardCode(0) == static_cast<std::uint8_t>(ContainerReward::RedKey));
    static_assert(safeRewardCode(1) == static_cast<std::uint8_t>(ContainerReward::GreenKey));
    static_assert(safeRewardCode(2) == static_cast<std::uint8_t>(ContainerReward::BlueKey));
    static_assert(safeRewardCode(3) == static_cast<std::uint8_t>(ContainerReward::YellowKey));
    static_assert(safeRewardCode(4) == static_cast<std::uint8_t>(ContainerReward::RedIdCard));
    static_assert(safeRewardCode(5) == static_cast<std::uint8_t>(ContainerReward::YellowIdCard));
    static_assert(safeRewardCode(6) == 0);

    static_assert(isColoredKeyDoorClass(0x33));
    static_assert(isColoredKeyDoorClass(0x38));
    static_assert(!isColoredKeyDoorClass(0x39));
    static_assert(isIdCardDoorClass(0x39));
    static_assert(isIdCardDoorClass(0x3A));
    static_assert(isRemoteDoorClass(0x3B));
    static_assert(isRemoteDoorClass(0x3C));
    static_assert(!isRemoteDoorClass(0x3D));

    assert(canOpenRemoteDoor(1));
    assert(canOpenRemoteDoor(3));
    assert(!canOpenRemoteDoor(0));
    assert(canCloseRemoteDoor(0));
    assert(canCloseRemoteDoor(2));
    assert(!canCloseRemoteDoor(1));
    return 0;
}
