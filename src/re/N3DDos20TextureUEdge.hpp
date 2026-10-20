#pragma once
// DOS Nitemare 3D v2.0: original image offset 0x22CA..0x241D (340 bytes).
// Native, independently translated 8086 edge-U routine for an already
// computed CEDC/25DC unadjusted signed-16 texture coordinate.
//
// SOURCE OF AUTHORITY: pinned N3D-E-20.EXE, 16-bit 22CA machine code, with
// 1,520 authentic original CPU return values in the private v0.77 corpus.
// This is not the CEDC perspective projection, IMG frame selector, or proof of
// complete original-vs-port pixel-perfect rendering.
#include <bit>
#include <cstdint>
#include <optional>

namespace n3d::re::dos20::texture_u {

struct VecEdge {
    std::int16_t screenX1{};           // original VEC +14
    std::int16_t screenX2{};           // original VEC +18
    std::int16_t worldX1{}, worldY1{}; // +0C, +0E
    std::int16_t worldX2{}, worldY2{}; // +10, +12
    std::uint8_t flags{};             // +05
    std::uint8_t renderClass{};       // +06
    std::uint8_t orientation{};       // +07
};

constexpr std::int16_t asSigned(std::uint16_t word) noexcept {
    return std::bit_cast<std::int16_t>(word);
}
constexpr std::int16_t subtract16(std::int16_t a,
                                  std::int16_t b) noexcept {
    return asSigned(static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(a) - static_cast<std::uint16_t>(b)));
}
constexpr std::int16_t negate16(std::int16_t value) noexcept {
    return asSigned(static_cast<std::uint16_t>(
        0u - static_cast<std::uint16_t>(value)));
}

// Original 22CA does NOT validate texture width; its final instructions
// are literally AX = (width - 1) & corrected_signed_U. The caller controls
// the supported texture format. This raw function follows the original
// 16-bit arithmetic even for nonstandard width inputs.
constexpr std::uint16_t correctRaw(const VecEdge& v, std::int16_t screenX,
                                   std::int16_t unadjustedU,
                                   std::uint16_t textureWidth) noexcept {
    const bool leftNear  = subtract16(screenX,v.screenX1) < 8;
    const bool rightNear = subtract16(v.screenX2,screenX) < 8;
    const auto mask = static_cast<std::uint16_t>(textureWidth - 1u);
    if ((!leftNear && !rightNear) || (v.flags & 0x08u) != 0u)
        return static_cast<std::uint16_t>(unadjustedU) & mask;

    const std::int16_t length = (v.orientation==0 || v.orientation==1)
         ? subtract16(v.worldX2,v.worldX1)
         : subtract16(v.worldY2,v.worldY1);

    std::int16_t adjusted=unadjustedU;
    if (v.renderClass==2 && (v.orientation==0 || v.orientation==3)) {
        if (v.orientation==0) {
            if ((rightNear && unadjustedU<0) || v.screenX2==screenX)
                adjusted=0;
            else if ((leftNear && length<=unadjustedU) || v.screenX1==screenX)
                adjusted=subtract16(length,1);
        } else {
            if ((leftNear && unadjustedU>=0) || v.screenX1==screenX)
                adjusted=static_cast<std::int16_t>(-1);
            else if ((rightNear && negate16(length)>unadjustedU) ||
                     v.screenX2==screenX)
                adjusted=negate16(length);
        }
    } else if(v.orientation==0 || v.orientation==2) {
        if ((rightNear && unadjustedU>=0) || v.screenX2==screenX)
            adjusted=static_cast<std::int16_t>(-1);
        else if ((leftNear && negate16(length)>unadjustedU) ||
                 v.screenX1==screenX)
            adjusted=negate16(length);
    } else if(v.orientation==1 || v.orientation==3) {
        if ((leftNear && unadjustedU<0) || v.screenX1==screenX)
            adjusted=0;
        else if ((rightNear && length<=unadjustedU) || v.screenX2==screenX)
            adjusted=subtract16(length,1);
    }
    return static_cast<std::uint16_t>(adjusted) & mask;
}

// Host-facing material selector: the current native renderer accepts source
// IMG wall frames of width 64 or 128. Original 22CA raw width semantics
// remain available through correctRaw for separately investigated cases.
constexpr std::optional<std::uint16_t> correctBounded(
    const VecEdge& v, std::int16_t screenX, std::int16_t unadjustedU,
    unsigned textureWidth) noexcept {
    if (v.orientation > 3 || (textureWidth != 64u && textureWidth != 128u))
        return std::nullopt;
    return correctRaw(v,screenX,unadjustedU,
                      static_cast<std::uint16_t>(textureWidth));
}

} // namespace n3d::re::dos20::texture_u
