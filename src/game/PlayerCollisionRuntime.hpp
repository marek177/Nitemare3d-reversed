#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace nitemare3d::game::collision {

// Runnable arithmetic/property-table subsets of docs/PLAYER_COLLISION_RE.md.
// NOT a replacement for 8604/84F4: axis-step order, CF60 touch side effects,
// mutable door records and original trajectory equivalence are not supplied.
inline constexpr int kWorldUnitsPerTile = 64;
inline constexpr int kPlayerHalfExtent = 27; // AABB, not a circular radius
inline constexpr std::uint8_t kEnteredTileEvent = 0x16;
inline constexpr std::uint16_t kWallMappedTypesAddress = 0x8196;
inline constexpr std::uint16_t kObjectMappedTypesAddress = 0x8296;
inline constexpr std::uint16_t kWallPropertiesAddress = 0x7E94;
inline constexpr std::uint16_t kObjectPropertiesAddress = 0x7F94;
inline constexpr std::uint16_t kWallPropertyBuilderOffset = 0x24C3; // segment 3
inline constexpr std::uint16_t kObjectPropertyBuilderOffset = 0x255D;
inline constexpr std::uint16_t kDoorPassageOffset = 0x1476;
inline constexpr std::uint16_t kPostMoveOffset = 0x8A20;
inline constexpr std::uint16_t kSoundPlaybackOffset = 0xE3B0;

// Wall-property bits recovered from the Win16 1.10 executable.
// 0x01 is copied into wall VEC records and gates projection/column claiming.
// 0x10 marks the exploding/destructible wall family in projectile collision.
inline constexpr std::uint8_t kWallRenderEligible = 0x01;
inline constexpr std::uint8_t kWallOccupied = 0x02;
inline constexpr std::uint8_t kWallHardBlock = 0x04;
inline constexpr std::uint8_t kWallDynamicDoor = 0x08;
inline constexpr std::uint8_t kWallExploding = 0x10;
inline constexpr std::uint8_t kWallScriptTouch = 0x40;
inline constexpr std::uint8_t kBlockedStepSfxIndex = 1;

using ByteTable = std::array<std::uint8_t, 256>;

// Input is a MAPPED runtime type from DS:8196, NOT a MAP wall ID or a
// definition-file class number.
constexpr std::uint8_t wallPropertiesForMappedType(std::uint8_t type) noexcept {
    std::uint8_t flags = 0;
    if (type >= 0x01 && type <= 0x30) flags |= kWallHardBlock;
    if (type >= 0x2E && type <= 0x2F) flags |= kWallExploding;
    if (type >= 0x31 && type <= 0x40) flags |= kWallDynamicDoor;
    if ((flags & (kWallHardBlock | kWallDynamicDoor)) != 0) flags |= kWallRenderEligible;
    if (type >= 0x01 && type <= 0x40) flags |= kWallOccupied;
    if (type >= 0x47 && type <= 0x48) flags |= kWallScriptTouch;
    return flags;
}

// Input is a MAPPED runtime type from DS:8296, NOT an OBJECTS record ID.
constexpr std::uint8_t objectPropertiesForMappedType(std::uint8_t type) noexcept {
    std::uint8_t flags = 0;
    if (type >= 0x06 && type <= 0x3D) flags |= 0x01;
    if (type >= 0x08 && type <= 0x2D) flags |= 0x02;
    if (type >= 0x2F && type <= 0x3D) flags |= 0x04;
    if (type >= 0x08 && type <= 0x25) flags |= 0x08;
    if (type == 0x2A) flags |= 0x20;
    if (type == 0x04) flags |= 0x40;
    return flags;
}

constexpr ByteTable buildWallProperties(const ByteTable& mappedTypes) noexcept {
    ByteTable result{};
    for (std::size_t id = 0; id < result.size(); ++id)
        result[id] = wallPropertiesForMappedType(mappedTypes[id]);
    return result;
}

constexpr ByteTable buildObjectProperties(const ByteTable& mappedTypes) noexcept {
    ByteTable result{};
    for (std::size_t id = 0; id < result.size(); ++id)
        result[id] = objectPropertiesForMappedType(mappedTypes[id]);
    return result;
}

enum class DoorState : std::uint16_t {
    Open = 0,
    Closed = 1,
    Opening = 2,
    Closing = 3,
    CorpseHoldOpen = 4,
};

// States 0..3 and their transitions are verified in the controller lifecycle.
// State 4 is written by GUARD death-finalization when a retained corpse/object
// occupies a dynamic-door cell. It is passable and excluded from normal toggle
// and auto-close processing, effectively holding/disabling the door open.
// A wider numeric overload prevents an invalid value such as 256 aliasing 0.
constexpr bool doorStateAllowsPassage(std::uint16_t state) noexcept {
    return state == static_cast<std::uint16_t>(DoorState::Open) ||
           state == static_cast<std::uint16_t>(DoorState::CorpseHoldOpen);
}
constexpr bool doorStateAllowsPassage(DoorState state) noexcept {
    return doorStateAllowsPassage(static_cast<std::uint16_t>(state));
}
constexpr bool doorStateIsClosed(std::uint16_t state) noexcept {
    return state == static_cast<std::uint16_t>(DoorState::Closed);
}

// Arithmetic >>6 from 8A20, expressed as floor division. Plain signed /64
// would incorrectly map -1..-63 to tile 0. Safe over the full int32_t domain.
constexpr std::int32_t worldToTile(std::int32_t world) noexcept {
    return world / kWorldUnitsPerTile - (world < 0 && world % kWorldUnitsPerTile != 0);
}

// Offset from a runtime 64x64 MAP-cell buffer, not from a MAP archive file.
// Out-of-map coordinates are explicitly rejected by this modern helper;
// this is a safety contract, not a claim about original out-of-bounds behavior.
constexpr std::optional<std::uint16_t>
mapCellByteOffset(std::int32_t tileX, std::int32_t tileY) noexcept {
    if (tileX < 0 || tileY < 0 || tileX >= 64 || tileY >= 64) return std::nullopt;
    return static_cast<std::uint16_t>((tileY * 64 + tileX) * 2);
}

struct CellCommit {
    std::int32_t tileX;
    std::int32_t tileY;
    std::uint16_t byteOffset;
    std::optional<std::uint8_t> event;
};

// Value result for the 8A20 post-move subset. The caller commits coordinates
// and dispatches the event; this helper never dereferences a Win16 far pointer.
constexpr std::optional<CellCommit>
postMoveCell(std::int32_t worldX, std::int32_t worldY,
             std::int32_t oldTileX, std::int32_t oldTileY) noexcept {
    const auto tx = worldToTile(worldX);
    const auto ty = worldToTile(worldY);
    const auto offset = mapCellByteOffset(tx, ty);
    if (!offset) return std::nullopt;
    const bool changed = tx != oldTileX || ty != oldTileY;
    return CellCommit{tx, ty, *offset,
                      changed ? std::optional<std::uint8_t>{kEnteredTileEvent} : std::nullopt};
}

} // namespace nitemare3d::game::collision
