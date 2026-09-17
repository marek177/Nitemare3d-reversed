#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

// Clean-room runtime layout scaffold recovered from NITE3W.EXE.
//
// Evidence status:
//   VERIFIED_EXE: record stride 0x1A, state +0x0B,
//                 next_state +0x0C, object id +0x0D.
//   UNKNOWN: all remaining bytes until their executable semantics are traced.
//
// Do not assign guessed HP/speed/position meanings to the unknown bytes.
#pragma pack(push, 1)
struct GuardRuntimeRecord {
    std::uint8_t unknown00_0A[0x0B];
    std::uint8_t state;       // +0x0B, VERIFIED_EXE
    std::uint8_t nextState;   // +0x0C, VERIFIED_EXE
    std::uint8_t objectId;    // +0x0D, VERIFIED_EXE (o_id diagnostic)
    std::uint8_t unknown0E_19[0x0C];
};
#pragma pack(pop)

static_assert(sizeof(GuardRuntimeRecord) == 0x1A,
              "Original Nitemare-3D GUARD runtime record is 26 bytes");
static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
static_assert(offsetof(GuardRuntimeRecord, objectId) == 0x0D);

// State numeric meanings are intentionally not enumerated yet. The original
// executable's transition dispatch still needs to be traced before assigning
// semantic enum names to individual values.

} // namespace nitemare3d::game
