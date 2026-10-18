#pragma once

#include <bit>
#include <cstdint>
#include <optional>

namespace n3d::re::dos20::sprite {
// Instruction-backed subset of 1000:1B3E; see docs/RENDERER_STATIC_PIXEL_CONTRACT.md.
// Inputs are decoded slot/descriptor words. No IMG loader or projection implied.
constexpr std::int16_t signedWord(std::uint16_t v) noexcept {
    return std::bit_cast<std::int16_t>(v);
}
constexpr bool columnVisible(std::uint16_t wall, std::uint16_t sprite,
                             std::uint8_t actorFlags) noexcept {
    // 1C89..1CDD: OBJECT+05 bit 10 bypass; JA skips, equality draws.
    return (actorFlags & 0x10U) != 0 || wall <= sprite;
}
constexpr bool writesTexel(std::uint8_t texel) noexcept {
    return texel != 0x1F; // 1CEE..1CF4, no shade remap in this loop.
}
struct VerticalSetup {
    std::uint16_t firstY;
    std::uint16_t count;
    std::uint32_t step16_16;
    std::uint16_t sourceAdvance;
    std::uint16_t fraction;
};
// Exact local vertical setup 1B84..1C07 including wrapping 16-bit arithmetic.
// Empty/negative clipped counts are returned raw: caller reachability is open.
// nullopt represents the original DIV-by-zero precondition, not game behavior.
constexpr std::optional<VerticalSetup> setupVertical(
    std::uint16_t top, std::uint16_t bottom, std::uint8_t sourceHeight,
    std::uint16_t viewportTop, std::uint16_t viewportBottom) noexcept {
    auto count = static_cast<std::uint16_t>(bottom - top + 1U);
    if (count == 0) return std::nullopt;
    const std::uint32_t step = (std::uint32_t{sourceHeight} << 16U) / count;
    std::uint16_t firstY = top;
    std::uint32_t start = 0;
    if (signedWord(bottom) > signedWord(viewportBottom)) {
        count = static_cast<std::uint16_t>(count + viewportBottom - bottom);
    }
    if (signedWord(top) < signedWord(viewportTop)) {
        firstY = viewportTop;
        count = static_cast<std::uint16_t>(count + top - viewportTop);
        const auto delta = signedWord(static_cast<std::uint16_t>(viewportTop - top));
        start = static_cast<std::uint32_t>(delta) * step; // low 32 bits of MUL
    }
    return VerticalSetup{firstY, count, step,
        static_cast<std::uint16_t>(start >> 16U), static_cast<std::uint16_t>(start)};
}
struct SampleCursor {
    std::uint16_t offset;
    std::uint16_t fraction;
};
// 1CF7..1CFE: ADD fraction, ADC integer offset, both wrapping at 16 bits.
constexpr SampleCursor advance(SampleCursor cursor, std::uint32_t step) noexcept {
    const auto sum = std::uint32_t{cursor.fraction} + (step & 0xFFFFU);
    cursor.fraction = static_cast<std::uint16_t>(sum);
    cursor.offset = static_cast<std::uint16_t>(cursor.offset + (step >> 16U) + (sum >> 16U));
    return cursor;
}
struct PlanarAddress {
    std::uint16_t offset;
    std::uint8_t sequencerValue;
};
// 1C9E..1CC7 uses MUL BL (AL only!), logical x>>2 and ROL8(11h,x&3).
// Relative to the framebuffer segment from DS:012E; no invented page offset.
constexpr PlanarAddress address(std::uint16_t x, std::uint16_t y) noexcept {
    return {static_cast<std::uint16_t>((y & 0xFFU) * 80U + (x >> 2U)),
            static_cast<std::uint8_t>(0x11U << (x & 3U))};
}
// One already selected sample, suitable for either a planar or indexed host sink.
// Wall visibility is read-only; this does not choose samples or clip geometry.
template<class Store>
constexpr bool emitSample(std::uint16_t wall, std::uint16_t sprite,
                          std::uint8_t flags, std::uint8_t texel, Store&& store) {
    if (!columnVisible(wall, sprite, flags) || !writesTexel(texel)) return false;
    store(texel);
    return true;
}
} // namespace n3d::re::dos20::sprite
