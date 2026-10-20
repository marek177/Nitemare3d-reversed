#pragma once
// DOS Nitemare3D v2.0 0x16CE: recovered 256-entry nearest-palette XLAT.
// Caller must supply the ORIGINAL base palette in VGA RGB6 representation.
// Does NOT treat current fade/flash DAC as the stable reference palette.
// No per-pixel RGB arithmetic in the wall raster; this builds DS:D20C-like LUT.
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
namespace n3d::re::dos20::shade {
inline constexpr std::array<unsigned,8> kShadeAmounts{0,4,8,12,16,20,30,40};
struct Result {
    std::array<std::uint8_t,256> xlat{};
    bool ok{false};
};
constexpr unsigned difference(unsigned a,unsigned b) noexcept {
    return a>b?a-b:b-a;
}
// First-minimum tie-break is a strict < comparison, including shade 0;
// duplicate palette colors mean shade-0 is NOT necessarily an identity LUT.
inline Result build(std::span<const std::uint8_t> baseRGB6,
                    unsigned shadeIndex) noexcept {
    Result out{};
    if(baseRGB6.size()!=768 || shadeIndex>=kShadeAmounts.size()) return out;
    for(auto v:baseRGB6)if(v>63)return out;
    const unsigned darken=kShadeAmounts[shadeIndex];
    for(unsigned src=0;src<256;++src) {
        std::array<unsigned,3> target{};
        for(unsigned c=0;c<3;++c) {
            const unsigned v=baseRGB6[3u*src+c];
            target[c]=v>darken?v-darken:0u;
        }
        unsigned bestDistance=~0u,best=0u;
        for(unsigned candidate=0;candidate<256;++candidate) {
            unsigned distance=0;
            for(unsigned c=0;c<3;++c)
                distance+=difference(baseRGB6[3u*candidate+c],target[c]);
            if(distance<bestDistance) {
                bestDistance=distance;
                best=candidate;
            }
        }
        out.xlat[src]=static_cast<std::uint8_t>(best);
    }
    out.ok=true;
    return out;
}
// The packed original DS segment has base palette at DS:4A64,
// active shade index at DS:6278, and 256-byte output table at DS:D20C.
// This helper builds a candidate table; matching the actual DS:D20C bytes
// of an original checkpoint is a SEPARATE runtime proof obligation.
inline Result buildFromOriginalDS(std::span<const std::uint8_t> ds) noexcept {
    if(ds.size()!=65536u)return {};
    const unsigned index=static_cast<unsigned>(ds[0x6278]) |
                         (static_cast<unsigned>(ds[0x6279])<<8u);
    return build(ds.subspan(0x4A64,768),index);
}
} // namespace n3d::re::dos20::shade
