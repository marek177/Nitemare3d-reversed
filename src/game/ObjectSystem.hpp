#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

inline constexpr std::size_t kObjectRecordSize = 0x1C; // VERIFIED_EXE

// Clean-room partial layout of the original NITE3W V1.10 runtime object record.
// Only fields with direct executable evidence are named. PARTIAL fields are
// intentionally named by observed role rather than guessed original symbols.
#pragma pack(push, 1)
struct ObjectRuntimeRecord {
    std::uint8_t objectId;        // +0x00, object/map identifier (VERIFIED_EXE)
    std::uint8_t variant;         // +0x01, class-relative variant index (VERIFIED_EXE); gameplay meaning PARTIAL
    std::uint8_t animationAux;    // +0x02, animation/render auxiliary byte; full semantics PARTIAL
    std::uint8_t animationFrame;  // +0x03, current sequence frame (VERIFIED_EXE)
    std::uint8_t sequenceId;      // +0x04, runtime sequence index (VERIFIED_EXE)
    std::uint8_t flags;           // +0x05, runtime/property flags (VERIFIED_EXE)
    std::uint8_t type;            // +0x06, runtime class lookup from definition (VERIFIED_EXE)
    std::uint8_t guardIndex;      // +0x07, assigned from current GUARD count for guard objects
    std::uint32_t animationDeadline; // +0x08, absolute sequence/frame deadline (VERIFIED_EXE)
    std::uint16_t mapCellOffset;  // +0x0C, near part of persisted map-cell far pointer
    std::uint16_t mapCellSegment; // +0x0E, segment part of map-cell far pointer
    std::int16_t worldX;          // +0x10, world-space X coordinate (VERIFIED_EXE)
    std::int16_t worldY;          // +0x12, world-space Y coordinate (VERIFIED_EXE)
    std::int16_t renderSortA;     // +0x14, renderer/sort-related value (PARTIAL)
    std::int16_t renderSortB;     // +0x16, renderer/sort-related value (PARTIAL)
    std::int16_t projectedYBase;  // +0x18, FUN_1010_CC7C projection/depth-scale cache read by damage producer; not world Y
    std::uint8_t runtime1A;       // +0x1A, zero for ordinary objects; embedded projectile OBJECT uses a vertical sprite offset (5..20 in flight)
    std::uint8_t unknown1B;
};
#pragma pack(pop)

static_assert(sizeof(ObjectRuntimeRecord) == kObjectRecordSize);
static_assert(offsetof(ObjectRuntimeRecord, animationFrame) == 0x03);
static_assert(offsetof(ObjectRuntimeRecord, sequenceId) == 0x04);
static_assert(offsetof(ObjectRuntimeRecord, flags) == 0x05);
static_assert(offsetof(ObjectRuntimeRecord, type) == 0x06);
static_assert(offsetof(ObjectRuntimeRecord, guardIndex) == 0x07);
static_assert(offsetof(ObjectRuntimeRecord, animationDeadline) == 0x08);
static_assert(offsetof(ObjectRuntimeRecord, mapCellOffset) == 0x0C);
static_assert(offsetof(ObjectRuntimeRecord, mapCellSegment) == 0x0E);
static_assert(offsetof(ObjectRuntimeRecord, worldX) == 0x10);
static_assert(offsetof(ObjectRuntimeRecord, worldY) == 0x12);
static_assert(offsetof(ObjectRuntimeRecord, renderSortA) == 0x14);
static_assert(offsetof(ObjectRuntimeRecord, renderSortB) == 0x16);
static_assert(offsetof(ObjectRuntimeRecord, projectedYBase) == 0x18);
static_assert(offsetof(ObjectRuntimeRecord, runtime1A) == 0x1A);

inline constexpr std::uint8_t kObjectRuntimePresent = 0x01; // 0x7F94: instantiate runtime OBJECT
inline constexpr std::uint8_t kObjectBlocksMovement = 0x02; // 0x7F94: blocks player movement
inline constexpr std::uint8_t kObjectSpecialTouch = 0x04;   // 0x7F94: special/touch handler; exact subtype semantics PARTIAL
inline constexpr std::uint8_t kObjectCreatesGuard = 0x08;   // 0x7F94 / OBJECT+05: create GUARD
inline constexpr std::uint8_t kObjectSpecial20 = 0x20;      // exact semantic TODO
inline constexpr std::uint8_t kObjectSpecial40 = 0x40;      // exact semantic TODO

// Damage path cross-binding (see docs/COMBAT_DAMAGE_RE.md): OBJECT+0x18 is read
// by seg3:9FA2 as a projected/view-space vertical value. It must not be confused
// with worldY at +0x12. The exact writer-level renderer symbol remains open.
inline constexpr std::size_t kObjectProjectedDamageBaselineOffset = 0x18;

} // namespace nitemare3d::game
