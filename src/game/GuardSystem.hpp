#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

inline constexpr std::size_t kGuardCapacity = 100;          // VERIFIED_EXE + SAVE layout
inline constexpr std::size_t kGuardRecordSize = 0x1A;      // VERIFIED_EXE
inline constexpr std::size_t kGuardSaveOffset = 0xB43B;    // VERIFIED_SAVE_LAYOUT correlation
inline constexpr std::size_t kGuardSaveSize = 0x0A28;      // 100 * 0x1A

// Clean-room runtime layout scaffold recovered from NITE3W.EXE.
// VERIFIED_EXE: stride 0x1A, state +0x0B, next_state +0x0C, o_id +0x0D.
// Remaining bytes stay unnamed until their executable semantics are traced.
#pragma pack(push, 1)
struct GuardRuntimeRecord {
    std::uint8_t unknown00_0A[0x0B];
    std::uint8_t state;       // +0x0B, VERIFIED_EXE
    std::uint8_t nextState;   // +0x0C, VERIFIED_EXE
    std::uint8_t objectId;    // +0x0D, VERIFIED_EXE
    std::uint8_t unknown0E_19[0x0C];
};
#pragma pack(pop)

static_assert(sizeof(GuardRuntimeRecord) == kGuardRecordSize);
static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
static_assert(offsetof(GuardRuntimeRecord, objectId) == 0x0D);
static_assert(kGuardCapacity * sizeof(GuardRuntimeRecord) == kGuardSaveSize);

// State numeric meanings and HP/speed/position/timer fields are intentionally
// not guessed. They will be named only after direct EXE/save correlation.

} // namespace nitemare3d::game
