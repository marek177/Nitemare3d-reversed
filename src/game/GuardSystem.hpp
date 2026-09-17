#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

inline constexpr std::size_t kGuardCapacity = 100;
inline constexpr std::size_t kGuardRecordSize = 0x1A;
inline constexpr std::size_t kGuardSaveOffset = 0xB43B;
inline constexpr std::size_t kGuardSaveSize = 0x0A28;

// Clean-room runtime layout recovered from NITE3W.EXE V1.10.
// Names below are promoted only where direct executable evidence exists.
#pragma pack(push, 1)
struct GuardRuntimeRecord {
    std::uint8_t unknown00_01[0x02];
    std::uint32_t timeStamp;          // +02 VERIFIED_EXE
    std::uint16_t stateTimer;         // +06 VERIFIED_EXE; debug label "timer"
    std::uint16_t objectSlot;         // +08 VERIFIED_EXE; index * 0x1C -> OBJECT
    std::uint8_t strategy;            // +0A VERIFIED_EXE; debug label "strategy"
    std::uint8_t state;               // +0B VERIFIED_EXE
    std::uint8_t nextState;           // +0C VERIFIED_EXE
    std::uint8_t objectId;            // +0D VERIFIED_EXE; diagnostic o_id
    std::uint8_t definitionId;        // +0E lookup-derived; exact table name pending
    std::uint8_t syncFlag;            // +0F derived boolean
    std::uint8_t strength;            // +10 VERIFIED_EXE: enemy HP/strength; damage subtracts here
    std::uint8_t octant;              // +11 VERIFIED_EXE; debug label "octant"
    std::uint8_t resultOctant;        // +12 VERIFIED_EXE; debug label "resoct"; set to 8 on non-lethal hit
    std::uint8_t transitionParam;      // +13 transition assignment; exact semantic pending
    std::uint8_t unknown14_15[0x02];
    std::uint8_t transitionFlag;       // +16 control flag
    std::uint8_t unknown17_19[0x03];
};
#pragma pack(pop)

static_assert(sizeof(GuardRuntimeRecord) == kGuardRecordSize);
static_assert(offsetof(GuardRuntimeRecord, timeStamp) == 0x02);
static_assert(offsetof(GuardRuntimeRecord, stateTimer) == 0x06);
static_assert(offsetof(GuardRuntimeRecord, objectSlot) == 0x08);
static_assert(offsetof(GuardRuntimeRecord, strategy) == 0x0A);
static_assert(offsetof(GuardRuntimeRecord, state) == 0x0B);
static_assert(offsetof(GuardRuntimeRecord, nextState) == 0x0C);
static_assert(offsetof(GuardRuntimeRecord, objectId) == 0x0D);
static_assert(offsetof(GuardRuntimeRecord, definitionId) == 0x0E);
static_assert(offsetof(GuardRuntimeRecord, syncFlag) == 0x0F);
static_assert(offsetof(GuardRuntimeRecord, strength) == 0x10);
static_assert(offsetof(GuardRuntimeRecord, octant) == 0x11);
static_assert(offsetof(GuardRuntimeRecord, resultOctant) == 0x12);
static_assert(offsetof(GuardRuntimeRecord, transitionParam) == 0x13);
static_assert(offsetof(GuardRuntimeRecord, transitionFlag) == 0x16);
static_assert(kGuardCapacity * sizeof(GuardRuntimeRecord) == kGuardSaveSize);

// Damage receiver is now structurally verified: a computed damage byte is
// compared with strength. If damage >= strength, strength is cleared to zero
// and the death path is called; otherwise damage is subtracted from strength
// and resultOctant is set to 8 before pain/state handling.
// Exact per-weapon damage constants remain TODO until the damage producer is traced.

} // namespace nitemare3d::game
