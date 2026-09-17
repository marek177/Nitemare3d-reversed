#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

inline constexpr std::size_t kGuardCapacity = 100;          // VERIFIED_EXE + SAVE layout
inline constexpr std::size_t kGuardRecordSize = 0x1A;      // VERIFIED_EXE
inline constexpr std::size_t kGuardSaveOffset = 0xB43B;    // VERIFIED_SAVE_LAYOUT correlation
inline constexpr std::size_t kGuardSaveSize = 0x0A28;      // 100 * 0x1A

// Clean-room runtime layout recovered from NITE3W.EXE.
//
// Strong EXE anchors added in the second GUARD pass:
//   +0x02 dword is initialized to zero and later compared against the game's
//         global tick/time value. It is therefore a GUARD time/timestamp field.
//   +0x06 word is explicitly initialized/assigned with state-dependent values
//         (examples 1 and 0x70), establishing it as a state/countdown timing field.
//   +0x08 word is multiplied by 0x1C before indexing the runtime object array;
//         it is the GUARD -> object-record slot/index.
//   +0x0A byte is a behavior/state-control field used by transition branches.
//   +0x0B/+0x0C/+0x0D are state/next_state/o_id from the original diagnostic.
//   +0x0E byte is populated through an object/definition lookup during spawn.
//   +0x0F byte is written as a derived boolean during GUARD/object synchronization.
//   +0x10 byte is initialized to 0xFF and subsequently read by GUARD logic.
//   +0x13 byte is explicitly assigned during a scripted/state transition.
//   +0x16 byte is explicitly used as a transition/control flag.
//
// Semantics whose exact names are not yet proven remain evidence-oriented rather
// than being mislabeled as HP/speed/direction.
#pragma pack(push, 1)
struct GuardRuntimeRecord {
    std::uint8_t unknown00_01[0x02];
    std::uint32_t timeStamp;          // +0x02, VERIFIED_EXE: tick/time comparison
    std::uint16_t stateTimer;         // +0x06, VERIFIED_EXE: state/countdown timing value
    std::uint16_t objectSlot;         // +0x08, VERIFIED_EXE: index * 0x1C -> object record
    std::uint8_t behaviorControl;     // +0x0A, VERIFIED_EXE role; exact enum pending
    std::uint8_t state;               // +0x0B, VERIFIED_EXE
    std::uint8_t nextState;           // +0x0C, VERIFIED_EXE
    std::uint8_t objectId;            // +0x0D, VERIFIED_EXE diagnostic o_id
    std::uint8_t definitionId;        // +0x0E, VERIFIED_EXE lookup-derived; exact table name pending
    std::uint8_t syncFlag;            // +0x0F, VERIFIED_EXE derived boolean
    std::uint8_t targetOrSequence;    // +0x10, VERIFIED_EXE initialized 0xFF; exact semantic pending
    std::uint8_t unknown11_12[0x02];
    std::uint8_t transitionParam;      // +0x13, VERIFIED_EXE transition assignment
    std::uint8_t unknown14_15[0x02];
    std::uint8_t transitionFlag;       // +0x16, VERIFIED_EXE control flag
    std::uint8_t unknown17_19[0x03];
};
#pragma pack(pop)

static_assert(sizeof(GuardRuntimeRecord) == kGuardRecordSize);
static_assert(offsetof(GuardRuntimeRecord, timeStamp) == 0x02);
static_assert(offsetof(GuardRuntimeRecord, stateTimer) == 0x06);
static_assert(offsetof(GuardRuntimeRecord, objectSlot) == 0x08);
static_assert(offsetof(GuardRuntimeRecord, behaviorControl) == 0x0A);
static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
static_assert(offsetof(GuardRuntimeRecord, objectId) == 0x0D);
static_assert(offsetof(GuardRuntimeRecord, definitionId) == 0x0E);
static_assert(offsetof(GuardRuntimeRecord, syncFlag) == 0x0F);
static_assert(offsetof(GuardRuntimeRecord, targetOrSequence) == 0x10);
static_assert(offsetof(GuardRuntimeRecord, transitionParam) == 0x13);
static_assert(offsetof(GuardRuntimeRecord, transitionFlag) == 0x16);
static_assert(kGuardCapacity * sizeof(GuardRuntimeRecord) == kGuardSaveSize);

// IMPORTANT: HP, speed and direction/angle have not yet been assigned to the
// remaining bytes. They require the damage/movement call-site pass rather than
// value-pattern guessing from a single save.

} // namespace nitemare3d::game
