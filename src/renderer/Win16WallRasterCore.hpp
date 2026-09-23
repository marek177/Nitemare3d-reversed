#pragma once

#include <array>
#include <bit>
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

// Host-side view of the 20-byte span consumed by FUN_1010_66B0.
#pragma pack(push, 1)
struct WallSpanRecord {
    std::uint32_t vecFarPointer;          // +00
    std::int16_t xStart;                  // +04
    std::int16_t yAtStart;                // +06, interpolated
    std::int16_t xEnd;                    // +08
    std::int16_t yAtEnd;                  // +0A, interpolated
    std::int32_t yStep16_16;              // +0C
    std::uint32_t yAccumulator16_16;      // +10, fixed-point screen Y
};
#pragma pack(pop)

static_assert(sizeof(WallSpanRecord) == 20);
static_assert(offsetof(WallSpanRecord, yStep16_16) == 0x0C);
static_assert(offsetof(WallSpanRecord, yAccumulator16_16) == 0x10);

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

constexpr std::int16_t subtract16(std::int16_t a, std::int16_t b) noexcept {
    const auto bits = static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(a) - static_cast<std::uint16_t>(b));
    return std::bit_cast<std::int16_t>(bits);
}

constexpr std::int16_t negate16(std::int16_t value) noexcept {
    const auto bits = static_cast<std::uint16_t>(0U - static_cast<std::uint16_t>(value));
    return std::bit_cast<std::int16_t>(bits);
}

// FUN_1010_6152 span setup. xStart/xEnd are the already-coalesced screen
// limits in the span record; endpoint values are the projected VEC x/y pairs.
// The 32-bit accumulator stores the screen-Y displacement from centerYQ4 plus
// the fractional start offset. False means the source quotient would overflow
// the original signed 32-bit IDIV result for pathological input coordinates.
inline bool initializeSpanInterpolation(WallSpanRecord& span,
                                        std::int16_t x1,
                                        std::int16_t y1Q4,
                                        std::int16_t x2,
                                        std::int16_t y2Q4,
                                        std::int16_t centerYQ4) noexcept {
    const std::int16_t dx = subtract16(x2, x1);
    const std::int16_t dy = subtract16(y2Q4, y1Q4);

    std::int32_t step = 0;
    if (dx != 0) {
        const std::int64_t numerator = static_cast<std::int64_t>(dy) * 65536;
        const std::int64_t quotient = numerator / dx;
        if (quotient < INT32_MIN || quotient > INT32_MAX) {
            return false;
        }
        step = static_cast<std::int32_t>(quotient);
    }

    std::int16_t yStart = y1Q4;
    std::int16_t yEnd = dy == 0 ? y1Q4 : y2Q4;
    std::uint32_t accumulator =
        static_cast<std::uint32_t>(static_cast<std::uint16_t>(subtract16(y1Q4, centerYQ4))) << 16U;

    if (dx != 0 && dy != 0) {
        const auto interpolate = [=](std::int16_t x) noexcept {
            const std::int16_t offset = subtract16(x, x1);
            const std::int64_t product = static_cast<std::int64_t>(offset) * dy;
            const std::int64_t value = static_cast<std::int64_t>(y1Q4) + product / dx;
            return std::bit_cast<std::int16_t>(static_cast<std::uint16_t>(value));
        };
        yStart = interpolate(span.xStart);
        yEnd = interpolate(span.xEnd);

        const std::int16_t startOffset = subtract16(span.xStart, x1);
        const std::int64_t product = static_cast<std::int64_t>(startOffset) * step;
        const std::uint32_t productLow = static_cast<std::uint32_t>(product);
        accumulator += productLow;
    }

    span.yAtStart = yStart;
    span.yAtEnd = yEnd;
    span.yStep16_16 = step;
    span.yAccumulator16_16 = accumulator;
    return true;
}

// FUN_1010_6422 texture-U endpoint correction. DOS E-20 FUN_1000_22CA has the
// same branch family. Arithmetic that the 16-bit binary performs in AX/CX is
// explicitly wrapped before signed comparisons. Width normally equals 64, so
// the final operation applies mask 0x3F.
inline constexpr std::uint16_t selectTextureU(const VecRecord& vec,
                                              std::int16_t screenX,
                                              std::int16_t alongWall,
                                              std::uint16_t width) noexcept {
    const bool nearLeft = subtract16(screenX, vec.screenX1) < 8;
    const bool nearRight = subtract16(vec.screenX2, screenX) < 8;
    const std::uint16_t mask = static_cast<std::uint16_t>(width - 1U);

    if ((!nearLeft && !nearRight) || (vec.flags & 0x08U) != 0) {
        return static_cast<std::uint16_t>(alongWall) & mask;
    }

    const std::int16_t length = (vec.orientation == 0 || vec.orientation == 1)
        ? subtract16(vec.x2, vec.x1)
        : subtract16(vec.y2, vec.y1);

    if (vec.renderClass == 2 && (vec.orientation == 0 || vec.orientation == 3)) {
        if (vec.orientation == 0) {
            if ((nearRight && alongWall < 0) || screenX == vec.screenX2) {
                return 0;
            }
            if ((nearLeft && length <= alongWall) || screenX == vec.screenX1) {
                alongWall = subtract16(length, 1);
            }
        } else {
            if ((nearLeft && alongWall >= 0) || screenX == vec.screenX1) {
                alongWall = -1;
            } else if ((nearRight && negate16(length) > alongWall) ||
                       screenX == vec.screenX2) {
                alongWall = negate16(length);
            }
        }
    } else if (vec.orientation == 0 || vec.orientation == 2) {
        if ((nearRight && alongWall >= 0) || screenX == vec.screenX2) {
            alongWall = -1;
        } else if ((nearLeft && negate16(length) > alongWall) ||
                   screenX == vec.screenX1) {
            alongWall = negate16(length);
        }
    } else if (vec.orientation == 1 || vec.orientation == 3) {
        if ((nearLeft && alongWall < 0) || screenX == vec.screenX1) {
            alongWall = 0;
        } else if ((nearRight && length <= alongWall) ||
                   screenX == vec.screenX2) {
            alongWall = subtract16(length, 1);
        }
    }

    return static_cast<std::uint16_t>(alongWall) & mask;
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
