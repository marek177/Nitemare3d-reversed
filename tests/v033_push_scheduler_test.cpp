#include "re/N3DV033PushScheduler.hpp"
#include "re/N3DV021SubsystemEvidence.hpp"
#include "re/N3DV022VersionEvidenceRegistry.hpp"
#include "re/N3DV029SchedulerEvidence.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>

using namespace n3d::re::v033;

int main() {
    static_assert(kDos20PushUpdate == 0x0E50);
    static_assert(kWin16PushUpdateSeg3 == 0x2210);
    static_assert(kCrossBuildUpdaterBytes == 292);
    static_assert(kCrossBuildDifferingOperandBytes == 20);
    static_assert(kPushRecordStride == 6);
    static_assert(kObjectRecordStride == 28);
    static_assert(kPushStartCountdown == 8);

    static_assert(startPushPassesWallFlag(0x00));
    static_assert(startPushPassesWallFlag(0x04));
    static_assert(!startPushPassesWallFlag(0x02));
    static_assert(!startPushPassesWallFlag(0x03));
    static_assert(updatePushCanEnter(true, 0xFF));
    static_assert(updatePushCanEnter(false, 0x00));
    static_assert(updatePushCanEnter(false, 0x01));
    static_assert(!updatePushCanEnter(false, 0x02));
    static_assert(!updatePushCanEnter(false, 0x04));
    static_assert(!updatePushCanEnter(false, 0x06));
    static_assert(!updatePushCanEnter(false, 0xFF));

    static_assert(advanceWorldWord(0, -1) == 0xFFFF);
    static_assert(advanceWorldWord(0xFFFF, 1) == 0);
    static_assert(dos20MapByteOffset(0, 0) == kDos20MapByteBase);
    static_assert(dos20MapByteOffset(32, 63) == kDos20MapByteBase);
    static_assert(dos20MapByteOffset(63, 0) == kDos20MapByteBase);
    static_assert(dos20MapByteOffset(64, 0) == kDos20MapByteBase + 2);
    static_assert(dos20MapByteOffset(0, 64) == kDos20MapByteBase + 128);
    static_assert(dos20MapByteOffset(64, 64) == kDos20MapByteBase + 130);

    constexpr std::array<std::uint16_t, 8> sampleYs{0,31,32,63,64,127,255,4095};
    for (auto y : sampleYs) {
        for (int x = 0; x < 4096; ++x) {
            const auto byteOffset = dos20MapByteOffset(
                static_cast<std::uint16_t>(x), y);
            const auto expected = static_cast<std::uint16_t>(
                kDos20MapByteBase + 2 * (x / 64) + 128 * (y / 64));
            assert(byteOffset == expected);
        }
    }

    constexpr PushStepInput inactive {
        32, 32, 8, 0, 0, 0x12340010u, 0x12340010u, 0xFF
    };
    constexpr auto idle = planPushUpdate(inactive);
    static_assert(idle.disposition == PushDisposition::Inactive);
    static_assert(idle.committedWorldX == 32);
    static_assert(!idle.invokeSpatialIndexReorder);

    constexpr PushStepInput stayInCell {
        32, 32, 8, 0, 8, 0x12340010u, 0x12340010u, 0x06
    };
    constexpr auto stay = planPushUpdate(stayInCell);
    static_assert(stay.disposition == PushDisposition::AcceptedSameCell);
    static_assert(stay.committedWorldX == 40);
    static_assert(stay.remainingAfter == 7);
    static_assert(!stay.transferObjectLayer);
    static_assert(stay.invokeSpatialIndexReorder);

    constexpr PushStepInput blocked {
        56, 32, 8, 0, 5, 0x12340010u, 0x12340012u, 0x04
    };
    constexpr auto deny = planPushUpdate(blocked);
    static_assert(deny.disposition == PushDisposition::BlockedByObjectProperty);
    static_assert(deny.committedWorldX == 56);
    static_assert(deny.remainingAfter == 5);
    static_assert(!deny.transferObjectLayer);
    static_assert(!deny.invokeSpatialIndexReorder);

    constexpr PushStepInput traversable {
        56, 32, 8, 0, 5, 0x12340010u, 0x12340012u, 0x01
    };
    constexpr auto advance = planPushUpdate(traversable);
    static_assert(advance.disposition == PushDisposition::AcceptedNewCell);
    static_assert(advance.committedWorldX == 64);
    static_assert(advance.candidateDosMapByteOffset == kDos20MapByteBase + 2);
    static_assert(advance.remainingAfter == 4);
    static_assert(advance.transferObjectLayer);
    static_assert(advance.invokeSpatialIndexReorder);

    // Source byte transfer intentionally can overwrite a *nonblocking* object.
    std::uint8_t oldLayer = 0x18;
    std::uint8_t targetLayer = 0x01;
    transferAcceptedPushObjectByte(oldLayer, targetLayer);
    assert(oldLayer == 0);
    assert(targetLayer == 0x18);

    static_assert(sortedIndexAdjustment(8, 200, 199, true) ==
                  SpatialSwap::WithNext);
    static_assert(sortedIndexAdjustment(-8, 200, 201, true) ==
                  SpatialSwap::WithPrevious);
    static_assert(sortedIndexAdjustment(8, 200, 200, true) ==
                  SpatialSwap::None);
    static_assert(sortedIndexAdjustment(-8, 200, 200, true) ==
                  SpatialSwap::None);
    static_assert(sortedIndexAdjustment(8, 200, 199, false) ==
                  SpatialSwap::None);
    static_assert(sortedIndexAdjustment(0, 200, 199, true) ==
                  SpatialSwap::None);

    // 0E50 is statically reclassified as PUSH, not generic OBJECT scheduler.
    namespace v021 = n3d::re::v021;
    namespace v022 = n3d::re::v022;
    namespace v029 = n3d::re::v029;
    static_assert(v021::classifySubsystemAddress(0x0E50) ==
                  v021::Subsystem::Push);
    static_assert(v021::confidenceForAddress(0x0E50) ==
                  v021::Confidence::Confirmed);
    static_assert(v022::mayPromoteToImplementation(
                  v022::FactId::Dos20PushUpdater0E50));
    static_assert(!v022::mayPromoteToImplementation(
                  v022::FactId::Dos20ObjectRuntime0E50));
    static_assert(v029::finding("push_update_0e50") != nullptr);
    static_assert(v029::finding("push_update_0e50")->evidence ==
                  v029::Evidence::VerifiedStatic);
    static_assert(!v029::runtimeConfirmed("push_update_0e50"));
}
