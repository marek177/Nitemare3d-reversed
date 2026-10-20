#pragma once
// Nitemare 3D DOS2 experimental material binding:
// 28B VEC (+03 frame, +04 cache selector) -> aliased IMG wall stream
// -> 10B frame header + width*height column-major bytes
// -> Win16 EBD6/6422 perspective-U *candidate* -> DOS 16CE shade XLAT
// -> the existing DOS2 304-column span raster.
//
// IMG cache/frame policy is traced to original N3D shared sequence offsets.
// DOS2 2500/25DC additionally overrides nonzero active shade to level 0
// for orientation 0/1 when DS:430E==0; the relevant Ghidra branch was also
// recorded by prior DOS static audits. This is per wall/span, NOT a global
// adjustment to the entire indexed framebuffer.
// The 66B0/EBD6 perspective mathematics came from Win16 1.10 and is NOT
// instruction-exact independently proven for DOS 2.0. This API marks it as
// a candidate and rejects missing resources instead of using a DDA fallback.
#include "re/N3DDos20SpanWallPipeline.hpp"
#include "re/N3DDos20ShadeXLAT.hpp"
#include "renderer/Win16WallRasterCore.hpp"

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace n3d::re::dos20::wallmaterial {

using Vec = nitemare3d::re::win16::VecRecord;
namespace wc = nitemare3d::re::win16;
namespace sw = n3d::re::dos20::spanwall;

inline constexpr unsigned kImgWallDirectorySize = 0x400;
inline constexpr unsigned kImgWallSeqOffset = 0x800;
inline constexpr unsigned kImgSequenceStride = 90;
inline constexpr unsigned kImgFrameStreamsStart = 0xBC00;
inline constexpr unsigned kImgFrameHeaderSize = 10;

constexpr std::int16_t wrap16(std::int64_t v) noexcept {
    return std::bit_cast<std::int16_t>(static_cast<std::uint16_t>(v));
}
constexpr int normalizeAngle(int degree) noexcept {
    const int v = degree % 360;
    return v < 0 ? v + 360 : v;
}

struct Trig360 {
    std::array<std::int16_t,360> sin{},cos{};
    // Exact N3D_TRIG_Q10.BIN layout: 360 i16 sin then 360 i16 cos.
    // Source is the SHA-checked Win16 trig extractor, not floating-point sin.
    static std::optional<Trig360> load(std::span<const std::uint8_t> src) noexcept {
        if(src.size()!=1440) return std::nullopt;
        Trig360 result{};
        for(unsigned i=0;i<360;++i) {
            result.sin[i] = sw::signedWord(sw::word(src,2*i));
            result.cos[i] = sw::signedWord(sw::word(src,720+2*i));
        }
        if(result.sin[0]!=0 || result.sin[45]!=724 ||
           result.sin[90]!=1024 || result.cos[0]!=1024 ||
           result.cos[90]!=0) return std::nullopt;
        return result;
    }
};

struct Camera {
    std::int16_t playerX{},playerY{};
    int angleDegrees{}; // 0..359 degrees, not the DOS raw angle-unit ABI
};

// Win16 66B0 -> EBD6 -> 6422 semantic cross-build CANDIDATE.
// 0x2EE0 * 304 / 0x5000 -> horizontal scale 178;
// (0x8340 * 152) << 4 -> vertical numerator 81715200.
// Does NOT use double/FOV/DDA. Returns nullopt for original-divisor or
// unsupported texture layouts. No forced-pixel corrections.
inline std::optional<std::uint16_t> perspectiveUCandidate(
    const Vec& vec,
    std::int16_t screenX,
    std::uint16_t spanYQ4,
    const Camera& camera,
    const Trig360& trig,
    unsigned width) noexcept {
    if(spanYQ4==0 || (width!=64 && width!=128) || vec.orientation>3)
        return std::nullopt;
    const int angle=normalizeAngle(camera.angleDegrees);
    const int sine=trig.sin[angle],cosine=trig.cos[angle];
    const bool cosineDivisor=(0x99u & (1u << (angle/45))) != 0;
    const int divisor=cosineDivisor?cosine:sine;
    if(divisor==0)return std::nullopt;
    const bool vertical=vec.orientation>=2;
    const bool isClassCurtain=vec.renderClass==0x3Fu || vec.renderClass==0x40u;
    bool flip=(vec.flags & 0x20u)!=0;
    if(isClassCurtain)flip=!flip;

    std::int16_t local=0,perpendicular=0;
    if(!vertical) {
        local = flip
          ? wrap16(std::int32_t(wc::subtract16(camera.playerX,vec.x2))+0x80)
          : wc::subtract16(camera.playerX,vec.x1);
        perpendicular=wc::subtract16(camera.playerY,vec.y1);
    } else {
        local = flip
          ? wrap16(std::int32_t(wc::subtract16(vec.y2,camera.playerY))-0x80)
          : wc::subtract16(vec.y1,camera.playerY);
        perpendicular=wc::subtract16(vec.x1,camera.playerX);
    }
    const std::int64_t opposite=cosineDivisor?sine:cosine;
    const std::int64_t perpendicularProduct =
        std::int64_t(perpendicular)*opposite;
    constexpr std::int64_t kVertical=std::int64_t(0x8340)*152*16;
    constexpr std::int64_t kHorizontal=
        (std::int64_t(0x2EE0)*304)/0x5000; // 178
    constexpr std::int64_t kInverse=kVertical/kHorizontal;
    const std::int64_t screenTerm=
        (std::int64_t(screenX-160)*kInverse)/spanYQ4;
    const std::int64_t verticalTerm=kVertical/spanYQ4;
    std::int64_t temp=0;
    if(!cosineDivisor) {
        temp=vertical ? perpendicularProduct-screenTerm
                      : verticalTerm-perpendicularProduct;
    }else{
        temp=vertical ? verticalTerm-perpendicularProduct
                      : screenTerm+perpendicularProduct;
    }
    auto along=wrap16(temp/divisor);
    along=wrap16(std::int32_t(along)+local);
    if(vec.renderClass!=2 && (vec.orientation==0 || vec.orientation==3))
        along=wc::negate16(along);
    return wc::selectTextureU(
        vec,screenX,along,static_cast<std::uint16_t>(width));
}

inline Vec vecFromDosDS(std::span<const std::uint8_t> ds,
                       std::uint16_t near) noexcept {
    Vec v{};
    v.wallId=ds[near];
    v.textureOffset=std::bit_cast<std::int8_t>(ds[near+1]);
    v.animationAux=ds[near+2];
    v.animationFrame=ds[near+3];
    v.textureSet=ds[near+4];
    v.flags=ds[near+5];
    v.renderClass=ds[near+6];
    v.orientation=ds[near+7];
    v.runtimeTimer=sw::dword(ds,near+8);
    v.x1=sw::signedWord(sw::word(ds,near+12));
    v.y1=sw::signedWord(sw::word(ds,near+14));
    v.x2=sw::signedWord(sw::word(ds,near+16));
    v.y2=sw::signedWord(sw::word(ds,near+18));
    v.screenX1=sw::signedWord(sw::word(ds,near+20));
    v.projectedY1Q4=sw::signedWord(sw::word(ds,near+22));
    v.screenX2=sw::signedWord(sw::word(ds,near+24));
    v.projectedY2Q4=sw::signedWord(sw::word(ds,near+26));
    return v;
}

struct RawFrame {
    std::span<const std::uint8_t> pixels{};
    std::uint32_t fileOffset{};
    unsigned width{},height{};
};
struct Sequence {
    std::uint32_t streamOffset{};
    std::uint8_t sourceWallId{};
    std::uint16_t interval{};
    bool extended{};
    std::vector<RawFrame> frames{};
};
struct Selection {
    RawFrame frame{};
    std::uint8_t cacheSelector{};
    unsigned selectedFrameIndex{};
    bool clampedAnimationFrame{};
};

class ImgWallCatalog {
public:
    std::vector<Sequence> caches{};
    std::array<int,256> selectorByWall{};
    // No copying original IMG frame pixels; spans retain caller ownership.
    // Build from VEC order; alias wall IDs by the same absolute IMG stream.
    // Checked VEC +04 must correspond to the original cache selector.
    bool build(std::span<const std::uint8_t> rawImg,
               std::span<const std::uint8_t> ds,
               unsigned activeVecCount) {
        if(rawImg.size()<kImgFrameStreamsStart ||
           ds.size()!=sw::kSegmentBytes ||
           activeVecCount==0 || activeVecCount>sw::kMaxVecs)
            return false;
        ImgWallCatalog next{};
        next.selectorByWall.fill(-1);
        for(unsigned i=0;i<activeVecCount;++i){
            const auto near=sw::kVecBase+i*sw::kVecStride;
            const std::uint8_t wallId=ds[near];
            const unsigned directory=4u*wallId;
            const std::uint32_t stream=sw::dword(rawImg,directory);
            if(stream<kImgFrameStreamsStart || stream>=rawImg.size())
                return false;
            unsigned selector=0;
            while(selector<next.caches.size() &&
                  next.caches[selector].streamOffset!=stream)++selector;
            if(selector==next.caches.size()){
                if(selector>=256)return false;
                const unsigned seq=kImgWallSeqOffset+
                                   unsigned(wallId)*kImgSequenceStride;
                if(seq+kImgSequenceStride>rawImg.size())return false;
                const unsigned frameCount=rawImg[seq+2];
                if(frameCount==0)return false;
                Sequence added{};
                added.streamOffset=stream;
                added.sourceWallId=wallId;
                added.interval=sw::word(rawImg,seq);
                added.extended=rawImg[seq+3]!=0;
                std::size_t cursor=stream;
                for(unsigned frame=0;frame<frameCount;++frame){
                    if(cursor>rawImg.size() ||
                       kImgFrameHeaderSize>rawImg.size()-cursor)return false;
                    const unsigned width=rawImg[cursor];
                    const unsigned height=rawImg[cursor+1];
                    if(!width || !height)return false;
                    const std::size_t payload=std::size_t(width)*height;
                    if(payload>rawImg.size()-cursor-kImgFrameHeaderSize)
                        return false;
                    added.frames.push_back(RawFrame{
                        rawImg.subspan(cursor+kImgFrameHeaderSize,payload),
                        static_cast<std::uint32_t>(cursor),width,height});
                    cursor+=kImgFrameHeaderSize+payload;
                }
                next.caches.push_back(std::move(added));
            }
            if(selector!=ds[near+4])return false; // no silent alias reshuffle
            next.selectorByWall[wallId]=static_cast<int>(selector);
        }
        *this=std::move(next);
        return true;
    }
    std::optional<Selection> select(const Vec& v) const noexcept {
        if(v.textureSet>=caches.size() ||
           selectorByWall[v.wallId]!=static_cast<int>(v.textureSet))
            return std::nullopt;
        const Sequence& cache=caches[v.textureSet];
        if(cache.frames.empty())return std::nullopt;
        unsigned frame=v.animationFrame;
        const bool clamp=frame>=cache.frames.size();
        if(clamp)frame=static_cast<unsigned>(cache.frames.size()-1);
        return Selection{cache.frames[frame],v.textureSet,frame,clamp};
    }
};

// DOS2 2500/25DC shade selection: if DS:6278 != 0, DS:430E == 0,
// and orientation is 0 or 1, the original local shade selector is 0.
// 0x430E is an opaque display/shade runtime flag; do not infer its name.
inline bool useZeroShadeForWall(std::span<const std::uint8_t> ds,
                               const Vec& vec,unsigned activeShade) noexcept {
    return ds.size()==sw::kSegmentBytes && activeShade>0 &&
           ds[0x430E]==0 && (vec.orientation==0 || vec.orientation==1);
}

// Bridge into spanwall::prepare's opt-in SEVENTH argument spanYQ4.
// Returned Material borrows IMG and Xlat from Catalog and Prepared. Both must
// remain alive until prepare has copied sources and shade table into Plan.
class MaterialBinder {
public:
    std::span<const std::uint8_t> ds{};
    const ImgWallCatalog* catalog{};
    const Trig360* trig{};
    const shade::Prepared* shading{};
    // Required only when original DOS orientation-specific shade override
    // activates. Must hold independently generated shade index 0 XLAT.
    const shade::Prepared* shadingZero{};
    Camera camera{};

    std::optional<sw::Material> operator()(
        unsigned screenX,std::uint16_t nearOwner,std::uint8_t wallId,
        const sw::Span&,int /*bottomY*/,unsigned /*heightIndex*/,
        std::uint16_t spanYQ4) const noexcept {
        if(ds.size()!=sw::kSegmentBytes || !catalog || !trig || !shading ||
           !sw::validNear(nearOwner,sw::kMaxVecs) ||
           screenX<sw::kLeft || screenX>sw::kRight ||
           wallId!=ds[nearOwner])
            return std::nullopt;
        // A live shade-mode change must rebuild the input translation first;
        // never silently render with an XLAT captured at another engine tick.
        if(sw::word(ds,0x6278)!=shading->shadeIndex)return std::nullopt;
        const auto vec=vecFromDosDS(ds,nearOwner);
        const auto selection=catalog->select(vec);
        if(!selection || (selection->frame.width!=64 &&
                          selection->frame.width!=128) ||
                          selection->frame.height!=64)
            return std::nullopt;
        const auto u=perspectiveUCandidate(vec,
            static_cast<std::int16_t>(screenX),spanYQ4,
            camera,*trig,selection->frame.width);
        if(!u)return std::nullopt;
        const bool forceZero=useZeroShadeForWall(ds,vec,shading->shadeIndex);
        const shade::Prepared* active=forceZero?shadingZero:shading;
        if(!active || (forceZero && (active->shadeIndex!=0 ||
                                      active->baseRgb6!=shading->baseRgb6)))
            return std::nullopt;
        return sw::Material{selection->frame.pixels,
            selection->frame.width,selection->frame.height,
            *u,&active->xlat};
    }
};

} // namespace n3d::re::dos20::wallmaterial
