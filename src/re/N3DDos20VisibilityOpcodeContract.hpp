#pragma once
// Nitemare 3D DOS v2.0 visibility: instruction-backed, host-side research model.
// FEFA image offsets 0xFEFA..0x1003D recovered from *original* CPU I traces.
// CAB8 image offsets: Y writes precede a vertical cull at 0xCBEB..0xCBF2.
// This is not the entire 1:1 renderer and must never silently replace DDA.

#include <array>
#include <cstdint>
#include <stdexcept>

namespace n3d::re::dos20::v070 {

struct Vec {
    std::int16_t x0{}, y0{}, x1{}, y1{};
    std::uint8_t orientation{}, flags{};
};

// DOS2 FEFA: inactive VECs do not enter projection or ownership.
constexpr bool active(std::uint8_t flags) noexcept { return (flags & 1u) != 0; }

// DOS2 FEFA (image 0xFF54..0x10020): signed STRICT comparisons.
// old is current column owner, incoming is newly projected candidate.
// Case analysis is from DOS2 opcodes, not Win16 assumptions.
constexpr bool replaces(const Vec& old, const Vec& incoming) noexcept {
    switch (old.orientation) {
        case 0:
            if (incoming.orientation == 2)
                return old.x0 < incoming.x0 && old.y0 > incoming.y0;
            if (incoming.orientation == 3)
                return old.x1 > incoming.x1 && old.y0 > incoming.y0;
            return false;
        case 1:
            if (incoming.orientation == 2)
                return old.x0 < incoming.x0 && old.y1 < incoming.y1;
            if (incoming.orientation == 3)
                return old.x1 > incoming.x1 && old.y1 < incoming.y1;
            return false;
        case 2:
            if (incoming.orientation == 0)
                return old.x1 < incoming.x1 && old.y1 > incoming.y1;
            if (incoming.orientation == 1)
                return old.x1 < incoming.x1 && old.y0 < incoming.y0;
            return false;
        case 3:
            if (incoming.orientation == 0)
                return old.x0 > incoming.x0 && old.y1 > incoming.y1;
            if (incoming.orientation == 1)
                return old.x0 > incoming.x0 && old.y0 < incoming.y0;
            return false;
        default:
            return false;
    }
}

struct Camera {
    std::int16_t playerX{}, playerY{}, sinQ10{}, cosQ10{},
                 horizonQ4{}, viewportBottom{};
    std::int64_t verticalNumerator{};
};

struct VerticalCull {
    std::array<std::int16_t,2> newProjectedYQ4{};
    bool earlyReturnBeforeX{false};
    std::int32_t cullThresholdQ4{};
    // projected X is NOT an output: on early cull CAB8 does not write +14/+18.
};

constexpr std::int64_t kNearPlane = 0x4000;

// CAB8 0xCACC..0xCBF5. Correct for the bounded signed camera / world ranges
// in the archived original checkpoint. Full 32-bit overflow & cardinal-special
// branches remain separate proof obligations.
inline VerticalCull projectVerticalAndTestEarlyCull(const Vec& vec, const Camera& c) {
    const std::array<std::int64_t,2> xs{vec.x0,vec.x1};
    const std::array<std::int64_t,2> ys{vec.y0,vec.y1};
    VerticalCull out{};
    for (int i=0;i<2;++i) {
        const std::int64_t dx=xs[i]-c.playerX;
        const std::int64_t dy=std::int64_t(c.playerY)-ys[i];
        const std::int64_t rawDepth=dx*c.sinQ10+dy*c.cosQ10;
        const std::int64_t clamped=rawDepth<kNearPlane ? kNearPlane : rawDepth;
        const std::int64_t projectedY=c.verticalNumerator/clamped+c.horizonQ4;
        if (projectedY < INT16_MIN || projectedY > INT16_MAX)
            throw std::runtime_error("Projected Y outside separately verified DOS2 range");
        out.newProjectedYQ4[i]=static_cast<std::int16_t>(projectedY);
    }
    out.cullThresholdQ4=(std::int32_t(c.viewportBottom)+0xb4)*16;
    out.earlyReturnBeforeX=out.newProjectedYQ4[0]>out.cullThresholdQ4 &&
                           out.newProjectedYQ4[1]>out.cullThresholdQ4;
    return out;
}

} // namespace n3d::re::dos20::v070
