#pragma once

#include <cstddef>
#include <cstdint>

namespace nitemare3d::game {

inline constexpr std::size_t kObjectRecordSize = 0x1C; // VERIFIED_EXE

// Clean-room partial layout of the original NITE3W V1.10 runtime object record.
// Only fields with direct executable evidence are named.
#pragma pack(push, 1)
struct ObjectRuntimeRecord {
    std::uint8_t objectId;        // +0x00, object/map identifier (VERIFIED_EXE)
    std::uint8_t variant;         // +0x01, subtype/variant-like value (partial semantic)
    std::uint8_t animX;           // +0x02, used as signed animation/render offset
    std::uint8_t animY;           // +0x03, used as signed animation/render offset
    std::uint8_t definitionId;    // +0x04, indexes object definition tables
    std::uint8_t flags;           // +0x05; bit 0x08 selects GUARD creation
    std::uint8_t type;            // +0x06, runtime object type/class
    std::uint8_t guardIndex;      // +0x07, assigned from current GUARD count for guard objects
    std::uint32_t runtime08;      // +0x08, initialized to zero; semantic TODO
    std::uint16_t mapCellOffset;  // +0x0C, near part of persisted map-cell far pointer
    std::uint16_t mapCellSegment; // +0x0E, segment part of map-cell far pointer
    std::int16_t worldX;          // +0x10, world-space X coordinate (VERIFIED_EXE)
    std::int16_t worldY;          // +0x12, world-space Y coordinate (VERIFIED_EXE)
    std::uint8_t unknown14_19[6];
    std::uint8_t runtime1A;       // +0x1A, initialized to zero
    std::uint8_t unknown1B;
};
#pragma pack(pop)

static_assert(sizeof(ObjectRuntimeRecord) == kObjectRecordSize);
static_assert(offsetof(ObjectRuntimeRecord, flags) == 0x05);
static_assert(offsetof(ObjectRuntimeRecord, type) == 0x06);
static_assert(offsetof(ObjectRuntimeRecord, guardIndex) == 0x07);
static_assert(offsetof(ObjectRuntimeRecord, mapCellOffset) == 0x0C);
static_assert(offsetof(ObjectRuntimeRecord, mapCellSegment) == 0x0E);
static_assert(offsetof(ObjectRuntimeRecord, worldX) == 0x10);
static_assert(offsetof(ObjectRuntimeRecord, worldY) == 0x12);

} // namespace nitemare3d::game
