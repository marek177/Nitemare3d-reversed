#include "re/N3DV032StaticClosure.hpp"
#include "re/N3DV025GuardWriterGraph.hpp"
#include "re/N3DV022VersionEvidenceRegistry.hpp"

#include <array>
#include <cassert>
#include <cstdint>

int main() {
    namespace v032 = n3d::re::v032;
    namespace v025 = n3d::re::v025;
    namespace v022 = n3d::re::v022;
    static_assert(v032::kTargetedClosures.size() == 8);
    for (const auto& entry : v032::kTargetedClosures) {
        assert(entry.localStaticClosed);
        assert(!entry.originalRuntimeClosed);
        assert(!v032::canClaimCompleteRuntimeParity(entry.id));
    }
    assert(v032::closure("unmapped") == nullptr);
    static_assert(v032::win16PushPassesWallGate(0x00));
    static_assert(!v032::win16PushPassesWallGate(0x02));
    static_assert(v032::win16PushPassesWallGate(0x01));
    static_assert(!v032::win16PushPassesWallGate(0x03));
    static_assert(v032::kWin16SavedHpOffset == 0x206A);
    static_assert(v032::kWin16GameplayBlockLength == 94);
    std::array<std::uint8_t, v032::kWin16SaveSlotSize> save{};
    save[0] = 0xE7; save[1] = 0xD6;
    save[v032::kWin16SavedHpOffset] = 100;
    assert(v032::win16SavedHp(save) == 100);
    save[v032::kWin16SavedHpOffset] = 0;
    assert(v032::win16SavedHp(save) == 0);
    save[0] = 0;
    assert(!v032::win16SavedHp(save).has_value());
    static_assert(v032::win16InputStep(10, 5, 0).move == 10);
    static_assert(v032::win16InputStep(10, 5, 0x20).move == 20);
    static_assert(v032::win16InputStep(10, 5, 0x20).turn == 10);
    static_assert(v032::win16InputStep(10, 5, 0x40).move == 1);
    static_assert(v032::win16InputStep(10, 5, 0x40).turn == 1);
    static_assert(v032::win16InputStep(10, 5, 0x60).move == 1);
    static_assert(v032::win16InputStep(10, 5, 0x60).turn == 1);
    static_assert(v032::win16InputStep(40000, 5, 0x20).move == 14464);
    static_assert(v032::kDos20DoorBlockedRetry == 4);
    static_assert(v032::kWin16ProjectilePoolSlots == 8);
    static_assert(v025::hasKnownAddress("normal_pain_enter_15"));
    static_assert(v025::writer("normal_pain_save_previous_state")->offset == 0x8290);
    static_assert(v025::writer("dracula_transform_timer")->offset == 0xA184);
    static_assert(v022::hasConfirmedFingerprint(v022::BuildId::DosV10));
    static_assert(v022::hasConfirmedFingerprint(v022::BuildId::DosV19));
    static_assert(v022::hasConfirmedFingerprint(v022::BuildId::DosV20));
    static_assert(v022::hasConfirmedFingerprint(v022::BuildId::Win16Unknown));
    static_assert(!v022::hasConfirmedFingerprint(v022::BuildId::DosV12));
}
