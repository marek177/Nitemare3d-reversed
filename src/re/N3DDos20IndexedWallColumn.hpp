#pragma once
// Nitemare 3D DOS v2.0: host-safe, indexed, fixed-point *wall column* raster.
//
// Scope: the already-selected IMG texture column and already-projected 16.16
// source step. This implements the bounded 097A:0599..05D5 scaled/XLAT
// evidence family; it does NOT choose VECs, spans, wall-U, shade table,
// palette phase or sprite order, nor establish full original-vs-port parity.
//
// No DDA, float math, transparent wall key or implicit 128x64 image squashing.
// INVALID operations are atomic: no partial framebuffer/VRAM writes.
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace n3d::re::dos20::wall {

inline constexpr std::size_t kWidth = 320;
inline constexpr std::size_t kHeight = 200;
inline constexpr std::size_t kIndexedBytes = kWidth * kHeight;
inline constexpr std::size_t kVgaBytes = 2u * 1024u * 1024u;
inline constexpr std::size_t kTextureHeight = 64u;
inline constexpr std::size_t kVgaPlaneRowBytes = 80u;

enum class Result : std::uint8_t {
    Written,
    InvalidViewport,
    InvalidVgaPage,
    InvalidVgaBuffer,
    InvalidFramebuffer,
    InvalidTextureSource,
};

struct Column {
    unsigned x{};
    unsigned firstY{};
    unsigned pixelCount{};
    std::uint32_t source16_16{};
    std::uint32_t step16_16{};
    unsigned page{}; // DOSBox-X A000 page 0, A400 page 1
};

// Full 2MiB emulated interleaved VGA array offset (not A000:xxxx aperture).
// Model for the archived DOSBox-X VGA snapshots; does not model CRTC page flips.
constexpr std::size_t interleavedVgaOffset(unsigned page, unsigned x,
                                           unsigned y) noexcept {
    return static_cast<std::size_t>(page) * 0x10000u
         + 4u * (static_cast<std::size_t>(y) * kVgaPlaneRowBytes + x / 4u)
         + x % 4u;
}

// Source IMG pixels are column-major. 128x64 contains TWO complete 64x64
// faces; physical U 0..127 is explicit. Never infer side from a DDA hit.
// Failure does not change the destination column.
inline bool selectPhysicalColumn(std::span<const std::uint8_t> img,
                                 unsigned imageWidth, unsigned imageHeight,
                                 unsigned physicalU,
                                 std::array<std::uint8_t,64>& selected) noexcept {
    if ((imageWidth != 64u && imageWidth != 128u) ||
        imageHeight != kTextureHeight || physicalU >= imageWidth ||
        img.size() != static_cast<std::size_t>(imageWidth) * imageHeight) {
        return false;
    }
    const std::size_t off = static_cast<std::size_t>(physicalU) * kTextureHeight;
    for (std::size_t i = 0; i < kTextureHeight; ++i) {
        selected[i] = img[off + i];
    }
    return true;
}

// Source is one 64-texel column, already selected by a separate exact
// texture/frame/U calculator. Translation is the caller's original XLAT table;
// nullptr means identity/no shade. No sprite transparency check for walls.
// 'vram' may be empty to render indexed-only, or must be a 2MiB interleaved
// VGA image. Every sample is bounds-checked BEFORE the first write.
inline Result drawColumn(
    std::span<std::uint8_t> indexed,
    std::span<std::uint8_t> vram,
    const Column& c,
    const std::array<std::uint8_t,64>& source,
    const std::array<std::uint8_t,256>* translation = nullptr) noexcept {

    if (indexed.size() != kIndexedBytes) return Result::InvalidFramebuffer;
    if (c.x >= kWidth || c.firstY >= kHeight ||
        c.pixelCount > (kHeight - c.firstY)) return Result::InvalidViewport;
    if (c.page > 1) return Result::InvalidVgaPage;
    if (!vram.empty() && vram.size() != kVgaBytes) return Result::InvalidVgaBuffer;

    std::uint32_t cursor = c.source16_16;
    for (unsigned i=0; i<c.pixelCount; ++i) {
        if ((cursor >> 16u) >= source.size()) {
            return Result::InvalidTextureSource;
        }
        // Original 16.16 arithmetic advances the low word and carries to the
        // integer word. Unsigned wrap here is explicitly defined by C++.
        cursor += c.step16_16;
    }

    cursor = c.source16_16;
    for (unsigned i=0; i<c.pixelCount; ++i) {
        const unsigned y=c.firstY+i;
        const std::uint8_t texel=source[cursor >> 16u];
        const std::uint8_t mapped=translation ? (*translation)[texel] : texel;
        indexed[static_cast<std::size_t>(y)*kWidth+c.x]=mapped;
        if (!vram.empty()) {
            vram[interleavedVgaOffset(c.page,c.x,y)]=mapped;
        }
        cursor+=c.step16_16;
    }
    return Result::Written;
}
} // namespace n3d::re::dos20::wall
