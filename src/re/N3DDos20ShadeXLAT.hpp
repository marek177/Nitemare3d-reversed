#pragma once
// Nitemare 3D DOS 2.0 0x16CE / DS:6278 and DS:D20C shade-remap model.
// Based on the instruction-backed 256-color RGB6 Manhattan nearest match.
//
// The active VGA DAC during fades is a DIFFERENT state from the stable game
// palette used to construct this shade lookup. Do not silently substitute
// current-fade DAC or use identity XLAT for shade index zero: duplicate palette
// colors mean strict-first-minimum tie breaking can select a lower index.
//
// Inputs/outputs are host-owned; no game palette, binaries or art embedded.
#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace n3d::re::dos20::shade {

using Table = std::array<std::uint8_t,256>;
using Palette = std::array<std::uint8_t,256*3>;

inline constexpr std::array<std::uint8_t,8> kShadeLevels{
    0,4,8,12,16,20,30,40
};

constexpr bool isRgb6(std::span<const std::uint8_t> raw) noexcept {
    if (raw.size()!=768) return false;
    for(auto c:raw) if(c>63) return false;
    return true;
}

constexpr int absDiff(int a,int b) noexcept { return a>b ? a-b : b-a; }

// Original routine 16CE: target channel = max(0, RGB6 - shadeAmount),
// nearest candidate by |R-R'|+|G-G'|+|B-B'|, strict < ties keep first.
inline bool buildFromRgb6(std::span<const std::uint8_t> rgb6,
                          unsigned shadeIndex,Table& out) noexcept {
    if(shadeIndex>=kShadeLevels.size() || !isRgb6(rgb6))return false;
    Table candidate{};
    const int amount = kShadeLevels[shadeIndex];
    for(unsigned src=0;src<256;++src) {
        const std::size_t s=3*src;
        const int targetR=std::max(0,int(rgb6[s])-amount);
        const int targetG=std::max(0,int(rgb6[s+1])-amount);
        const int targetB=std::max(0,int(rgb6[s+2])-amount);
        int best=3*64+1; // > maximum possible 3*63
        unsigned first=0;
        for(unsigned j=0;j<256;++j) {
            const std::size_t p=3*j;
            const int d=absDiff(targetR,int(rgb6[p]))+
                        absDiff(targetG,int(rgb6[p+1]))+
                        absDiff(targetB,int(rgb6[p+2]));
            if(d<best){best=d; first=j;}
        }
        candidate[src]=static_cast<std::uint8_t>(first);
    }
    out=candidate; // failure leaves caller's previous table unchanged
    return true;
}

// Original PCX/GAME.PAL payload is RGB8, DOS builds 6-bit logical palette
// using RGB8 >> 2, without rounding.
inline bool buildFromRgb8(std::span<const std::uint8_t> rgb8,
                          unsigned shadeIndex,Table& out) noexcept {
    if(rgb8.size()!=768 || shadeIndex>=kShadeLevels.size())return false;
    Palette converted{};
    for(std::size_t i=0;i<converted.size();++i) converted[i]=rgb8[i]>>2u;
    return buildFromRgb6(converted,shadeIndex,out);
}

// Strictly require a stable base 6-bit palette and 0..7 shade index;
// current DAC fade/flash bytes must never be substituted automatically.
struct Prepared {
    Palette baseRgb6{};
    unsigned shadeIndex{};
    Table xlat{};
};
inline bool prepare(std::span<const std::uint8_t> baseRgb6,
                    unsigned shadeIndex,Prepared& out) noexcept {
    if(!isRgb6(baseRgb6)||shadeIndex>=kShadeLevels.size())return false;
    Prepared candidate{};
    std::copy(baseRgb6.begin(),baseRgb6.end(),candidate.baseRgb6.begin());
    candidate.shadeIndex=shadeIndex;
    if(!buildFromRgb6(candidate.baseRgb6,shadeIndex,candidate.xlat))return false;
    out=candidate;
    return true;
}

} // namespace n3d::re::dos20::shade
