#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace nitemare3d::re::win16 {

// Portable field view of the 28-byte Win16 VEC record. Several resource and
// animation fields are still semantically partial; the offsets and total size
// are instruction-backed. This is a host-side value type, not an on-disk dump.
#pragma pack(push, 1)
struct VecRecord {
    std::uint8_t wallId;                 // +00
    std::int8_t textureOffset;            // +01, semantic partial
    std::uint8_t animationAux;            // +02, semantic partial
    std::uint8_t animationFrame;          // +03
    std::uint8_t textureSet;              // +04
    std::uint8_t flags;                   // +05
    std::uint8_t renderClass;             // +06
    std::uint8_t orientation;             // +07, 0..3
    std::uint32_t runtimeTimer;            // +08, semantic partial
    std::int16_t x1;                      // +0C
    std::int16_t y1;                      // +0E
    std::int16_t x2;                      // +10
    std::int16_t y2;                      // +12
    std::int16_t screenX1;                // +14
    std::int16_t projectedY1Q4;           // +16
    std::int16_t screenX2;                // +18
    std::int16_t projectedY2Q4;           // +1A
};
#pragma pack(pop)

static_assert(sizeof(VecRecord) == 28);
static_assert(offsetof(VecRecord, orientation) == 0x07);
static_assert(offsetof(VecRecord, x1) == 0x0C);
static_assert(offsetof(VecRecord, y1) == 0x0E);
static_assert(offsetof(VecRecord, x2) == 0x10);
static_assert(offsetof(VecRecord, y2) == 0x12);
static_assert(offsetof(VecRecord, screenX1) == 0x14);
static_assert(offsetof(VecRecord, projectedY2Q4) == 0x1A);

// FUN_1018_3564 (CS 1018:3564), reduced to the occupied-column decision.
// All coordinate comparisons are signed 16-bit and strict. Equal endpoints
// keep the existing owner. Empty-column insertion and clipping happen outside
// this helper. Same-orientation conflicts are left to list traversal order.
inline constexpr bool ownerConflictReplaces(const VecRecord& oldOwner,
                                           const VecRecord& candidate) noexcept {
    switch (oldOwner.orientation) {
    case 0:
        if (candidate.orientation == 2) {
            return candidate.x1 > oldOwner.x1 && candidate.y1 < oldOwner.y1;
        }
        if (candidate.orientation == 3) {
            return candidate.x2 < oldOwner.x2 && candidate.y1 < oldOwner.y1;
        }
        return false;
    case 1:
        if (candidate.orientation == 2) {
            return candidate.x1 > oldOwner.x1 && candidate.y2 > oldOwner.y2;
        }
        if (candidate.orientation == 3) {
            return candidate.x2 < oldOwner.x2 && candidate.y2 > oldOwner.y2;
        }
        return false;
    case 2:
        if (candidate.orientation == 0) {
            return candidate.x2 > oldOwner.x2 && candidate.y2 < oldOwner.y2;
        }
        if (candidate.orientation == 1) {
            return candidate.x2 > oldOwner.x2 && candidate.y1 > oldOwner.y1;
        }
        return false;
    case 3:
        if (candidate.orientation == 0) {
            return candidate.x1 < oldOwner.x1 && candidate.y2 < oldOwner.y2;
        }
        if (candidate.orientation == 1) {
            return candidate.x1 < oldOwner.x1 && candidate.y1 > oldOwner.y1;
        }
        return false;
    default:
        return false;
    }
}

struct WallSamplingTables {
    // Entry n is the original 16.16 source-texture increment 0x400000 / n.
    std::array<std::uint32_t, 512> step16_16{};

    // FUN_1010_2960's clipped-start tables. Entry n is split exactly as the
    // original stores it: upper source texel byte plus low 16-bit fraction.
    std::array<std::uint8_t, 512> clippedStartTexel{};
    std::array<std::uint16_t, 512> clippedStartFraction{};
};

// Reconstructs FUN_1010_2930 and the raw-assembly initializer at CS 1010:2960.
// screenHeightAt53E2 is the runtime word read at DS:53E2; its semantic name is
// not established beyond its role in this clipping-table calculation.
inline constexpr WallSamplingTables makeWallSamplingTables(
    std::uint16_t screenHeightAt53E2) noexcept {
    WallSamplingTables tables{};
    for (std::uint32_t n = 1; n <= 511; ++n) {
        tables.step16_16[n] = 0x400000U / n;

        const std::uint32_t delta = n > screenHeightAt53E2
            ? n - screenHeightAt53E2
            : 0U;
        const std::uint32_t numerator = (delta * 64U) << 16U;
        // The binary first divides by n, then arithmetic-shifts right once.
        const std::uint32_t clippedStart = (numerator / n) >> 1U;
        tables.clippedStartTexel[n] =
            static_cast<std::uint8_t>((clippedStart >> 16U) & 0xFFU);
        tables.clippedStartFraction[n] =
            static_cast<std::uint16_t>(clippedStart & 0xFFFFU);
    }
    return tables;
}

inline constexpr std::uint32_t clippedStart16_16(
    const WallSamplingTables& tables, std::size_t n) noexcept {
    if (n >= tables.clippedStartTexel.size()) {
        return 0;
    }
    return (static_cast<std::uint32_t>(tables.clippedStartTexel[n]) << 16U) |
           tables.clippedStartFraction[n];
}

// WinG/linear-DIB wall-column loop from FUN_1010_366A. The input is already
// the selected 64-sample texture column and the source coordinate is the
// original combined clipped-start value. rowStride=320 models the game DIB.
// A palette remap pointer models DAT_1048_8094; pass nullptr for direct copies.
// Returns false for invalid spans or if the recovered stepping leaves the
// 64-sample source column, instead of silently clamping a behavior the binary
// does not clamp here.
inline bool drawWinGIndexedColumn(
    std::span<std::uint8_t> framebuffer,
    std::size_t rowStride,
    std::size_t x,
    std::size_t firstY,
    std::size_t pixelCount,
    const std::array<std::uint8_t, 64>& textureColumn,
    std::uint32_t source16_16,
    std::uint32_t step16_16,
    const std::array<std::uint8_t, 256>* paletteRemap = nullptr) noexcept {
    if (rowStride == 0 || x >= rowStride || firstY > framebuffer.size() / rowStride) {
        return false;
    }
    if (pixelCount != 0) {
        if (firstY == framebuffer.size() / rowStride ||
            firstY > (static_cast<std::size_t>(-1) - x) / rowStride) {
            return false;
        }
        const std::size_t firstPixel = firstY * rowStride + x;
        if (firstPixel >= framebuffer.size() ||
            pixelCount - 1 > (framebuffer.size() - 1 - firstPixel) / rowStride) {
            return false;
        }
    }

    // Validate every source lookup before modifying the framebuffer.
    std::uint32_t source = source16_16;
    for (std::size_t y = 0; y < pixelCount; ++y) {
        if ((source >> 16U) >= textureColumn.size()) {
            return false;
        }
        source += step16_16;
    }

    source = source16_16;
    for (std::size_t y = 0; y < pixelCount; ++y) {
        const std::uint8_t texel = textureColumn[source >> 16U];
        framebuffer[(firstY + y) * rowStride + x] =
            paletteRemap == nullptr ? texel : (*paletteRemap)[texel];
        source += step16_16;
    }
    return true;
}

} // namespace nitemare3d::re::win16
