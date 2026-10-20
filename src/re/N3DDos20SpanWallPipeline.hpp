#pragma once
// Nitemare 3D DOS v2.0: checked DS owner/span -> 304 indexed wall columns.
//
// Scope: 64KiB DOS2 renderer snapshot with post-span DS:4564 and DS:4D6E.
// Vertical formula: original 0x2500 -> 0x1A2E (Pass 47).
// Horizontal source texture U / IMG frame / shade LUT are EXPLICIT inputs
// from a resolver, not falsely reconstructed from a DDA intersection.
//
// This is a research pipeline; no full-scene pixel-parity claim or live DDA
// replacement. An entire frame plan is validated before touching pixels.
#include "re/N3DDos20IndexedWallColumn.hpp"

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <utility>

namespace n3d::re::dos20::spanwall {

inline constexpr unsigned kLeft = 8, kRight = 311, kTop = 4, kBottom = 155;
inline constexpr unsigned kCenterY = 80, kViewportHeight = 152;
inline constexpr unsigned kColumns = kRight - kLeft + 1; // 304
inline constexpr std::size_t kSegmentBytes = 65536;
inline constexpr unsigned kVecBase = 0x62AC, kVecStride = 28, kMaxVecs = 1000;
inline constexpr unsigned kOwnerOffset = 0x4564, kRemainingOffset = 0x4562;
inline constexpr unsigned kSpanCountOffset = 0x4D64, kSpanBase = 0x4D6E;
inline constexpr unsigned kSpanStride = 18, kMaxSpans = 50;

enum class Status : std::uint8_t {
    Ok, InvalidSegment, InvalidVecCount, InvalidSpanCount,
    IncompleteOwnerViewport, InvalidSpanRange, InvalidNearPointer,
    OwnerMismatch, UnsupportedProjectionHeight, InvalidWallMaterial,
    InvalidFrame, InvalidVga, InvalidPreparedColumn,
};

struct Span {
    std::uint16_t nearOwner{};
    std::int16_t xStart{}, yStartQ4{}, xEnd{}, yEndQ4{};
    std::int32_t step16_16{};
    std::uint32_t phase16_16{};
};
struct Material {
    std::span<const std::uint8_t> imgColumnMajor{};
    unsigned imageWidth{}, imageHeight{64}, physicalU{};
    const std::array<std::uint8_t,256>* shadeXLAT{nullptr};
};
struct ColumnPlan {
    std::uint16_t nearOwner{};
    std::uint8_t wallId{};
    unsigned spanIndex{};
    std::int16_t spanYQ4{};
    int projectedBottomY{};
    unsigned heightIndex{};
    bool draw{false};
    wall::Column drawArgs{};
    std::array<std::uint8_t,64> source{};
    std::array<std::uint8_t,256> xlat{};
    bool useXLAT{false};
};
struct Plan {
    unsigned spanCount{};
    unsigned drawnColumns{};
    unsigned culledColumns{};
    std::array<ColumnPlan,kColumns> columns{};
};

// Use explicit little-endian decoding; never reinterpret-cast packed memory.
constexpr std::uint16_t word(std::span<const std::uint8_t> bytes,
                             unsigned at) noexcept {
    return static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(bytes[at]) |
        (static_cast<std::uint16_t>(bytes[at+1]) << 8u));
}
constexpr std::uint32_t dword(std::span<const std::uint8_t> bytes,
                              unsigned at) noexcept {
    return static_cast<std::uint32_t>(word(bytes,at)) |
           (static_cast<std::uint32_t>(word(bytes,at+2)) << 16u);
}
constexpr std::int16_t signedWord(std::uint16_t bits) noexcept {
    return std::bit_cast<std::int16_t>(bits);
}
constexpr std::int32_t signedDword(std::uint32_t bits) noexcept {
    return std::bit_cast<std::int32_t>(bits);
}
constexpr int signedShiftRight4(int value) noexcept {
    // Explicit x86 SAR 4 for the range of all 16-bit span Q4 displacements.
    return value >= 0 ? value / 16 : -((-value+15)/16);
}

inline Span parseSpan(std::span<const std::uint8_t> ds,
                      unsigned index) noexcept {
    const unsigned at = kSpanBase + index * kSpanStride;
    return {
        word(ds,at),
        signedWord(word(ds,at+2)),
        signedWord(word(ds,at+4)),
        signedWord(word(ds,at+6)),
        signedWord(word(ds,at+8)),
        signedDword(dword(ds,at+10)),
        dword(ds,at+14)
    };
}

constexpr bool validNear(std::uint16_t ptr, unsigned count) noexcept {
    return ptr >= kVecBase &&
           (ptr-kVecBase) % kVecStride == 0 &&
           static_cast<unsigned>((ptr-kVecBase)/kVecStride) < count;
}

// DOS 0x2500 passes (centerYQ4 + signed high(span.phase)) >> 4.
// DOS 0x1A2E then derives heightIndex and the exact unclipped/clipped
// destination coordinates. Formula cross-check: phase high 331 -> bottom100,
// heightIndex41, firstY59, count42, step0x18F9C.
struct Vertical {
    bool visible{false};
    unsigned firstY{}, pixelCount{}, heightIndex{};
    int projectedBottomY{};
    std::uint32_t source16_16{}, step16_16{};
};
constexpr std::optional<Vertical> verticalFromSpanQ4(
    std::int16_t displacementQ4) noexcept {

    const int bottom = signedShiftRight4((int(kCenterY)<<4) +
                                          int(displacementQ4));
    const int n = 2*(bottom-int(kCenterY))+1;
    if (n <= 0) return Vertical{false,0,0,0,bottom,0,0};
    if (n > 511) return std::nullopt; // table 1..511; do not invent values

    Vertical v{};
    v.visible = true;
    v.heightIndex = static_cast<unsigned>(n);
    v.projectedBottomY = bottom;
    v.step16_16 = 0x400000u/static_cast<unsigned>(n);
    if (bottom < int(kBottom)) {
        const int first = bottom-n;
        const unsigned count = static_cast<unsigned>(n+1);
        if (first < int(kTop) || first > int(kBottom) ||
            count > kViewportHeight ||
            first + static_cast<int>(count) - 1 > int(kBottom)) {
            return std::nullopt;
        }
        v.firstY = static_cast<unsigned>(first);
        v.pixelCount = count;
        v.source16_16 = 0;
    } else {
        v.firstY = kTop;
        v.pixelCount = kViewportHeight;
        // floor(floor((n-152)*64*65536/n)/2), 0 for n<=152.
        const unsigned delta = static_cast<unsigned>(n)>kViewportHeight
                             ? static_cast<unsigned>(n)-kViewportHeight : 0u;
        v.source16_16 =
            ((delta*64u*65536u)/static_cast<unsigned>(n)) >> 1u;
    }
    return v;
}

// Resolver signature:
// std::optional<Material>(unsigned screenX, std::uint16_t nearOwner,
//                         std::uint8_t wallId, const Span&, int bottomY,
//                         unsigned heightIndex).
// It MUST resolve exact image/frame/U/shade selection. No inferred DDA U here.
// Produces all 304 owner-associated column records atomically.
template<class Resolve>
Status prepare(std::span<const std::uint8_t> ds,
               unsigned activeVecCount, unsigned vgaPage, Resolve&& resolve,
               Plan& out) {
    if (ds.size()!=kSegmentBytes) return Status::InvalidSegment;
    if (activeVecCount==0 || activeVecCount>kMaxVecs)
        return Status::InvalidVecCount;
    if (vgaPage>1) return Status::InvalidVga;
    if (word(ds,kRemainingOffset)!=0) return Status::IncompleteOwnerViewport;
    const unsigned count=word(ds,kSpanCountOffset);
    if (count==0 || count>kMaxSpans) return Status::InvalidSpanCount;

    Plan next{};
    next.spanCount=count;
    unsigned expectedX=kLeft;
    for (unsigned si=0;si<count;++si) {
        const Span s=parseSpan(ds,si);
        if (s.xStart<0 || s.xEnd<0 ||
            static_cast<unsigned>(s.xStart)!=expectedX ||
            s.xEnd<s.xStart || s.xEnd>static_cast<int>(kRight)) {
            return Status::InvalidSpanRange;
        }
        if (!validNear(s.nearOwner,activeVecCount))
            return Status::InvalidNearPointer;
        const std::uint8_t wallId=ds[s.nearOwner];
        std::uint32_t phase=s.phase16_16;
        for (unsigned x=static_cast<unsigned>(s.xStart);
             x<=static_cast<unsigned>(s.xEnd); ++x) {
            if (word(ds,kOwnerOffset+2*x)!=s.nearOwner)
                return Status::OwnerMismatch;
            ColumnPlan& p=next.columns[x-kLeft];
            p.nearOwner=s.nearOwner;
            p.wallId=wallId;
            p.spanIndex=si;
            p.spanYQ4=signedWord(static_cast<std::uint16_t>(phase >> 16u));
            const auto v=verticalFromSpanQ4(p.spanYQ4);
            if (!v) return Status::UnsupportedProjectionHeight;
            p.projectedBottomY=v->projectedBottomY;
            p.heightIndex=v->heightIndex;
            if (v->visible) {
                const std::optional<Material> material =
                    resolve(x,s.nearOwner,wallId,s,v->projectedBottomY,
                            v->heightIndex);
                if (!material) return Status::InvalidWallMaterial;
                if (!wall::selectPhysicalColumn(
                    material->imgColumnMajor,material->imageWidth,
                    material->imageHeight,material->physicalU,p.source)) {
                    return Status::InvalidWallMaterial;
                }
                p.draw=true;
                p.drawArgs={x,v->firstY,v->pixelCount,
                            v->source16_16,v->step16_16,vgaPage};
                p.useXLAT=material->shadeXLAT!=nullptr;
                if (p.useXLAT) p.xlat=*material->shadeXLAT;
                // 64-texel source preflight matches the v0.74 pixel writer.
                std::uint32_t cursor=p.drawArgs.source16_16;
                for(unsigned i=0;i<p.drawArgs.pixelCount;++i) {
                    if((cursor>>16u)>=p.source.size())
                        return Status::InvalidWallMaterial;
                    cursor+=p.drawArgs.step16_16;
                }
                ++next.drawnColumns;
            } else {
                ++next.culledColumns;
            }
            phase+=static_cast<std::uint32_t>(s.step16_16);
        }
        expectedX=static_cast<unsigned>(s.xEnd)+1;
    }
    if(expectedX!=kRight+1 || next.drawnColumns+next.culledColumns!=kColumns)
        return Status::InvalidSpanRange;
    out=std::move(next); // Do not mutate a previous plan on invalid input.
    return Status::Ok;
}

inline Status render(const Plan& plan,
                     std::span<std::uint8_t> indexed,
                     std::span<std::uint8_t> vram) noexcept {
    if(indexed.size()!=wall::kIndexedBytes) return Status::InvalidFrame;
    if(!vram.empty() && vram.size()!=wall::kVgaBytes)
        return Status::InvalidVga;
    if(plan.drawnColumns+plan.culledColumns!=kColumns ||
       plan.spanCount==0 || plan.spanCount>kMaxSpans)
        return Status::InvalidPreparedColumn;

    // All-or-nothing preflight prevents partial frame writes even if caller
    // mutates a publicly visible plan after prepare().
    for(unsigned j=0;j<kColumns;++j) {
        const ColumnPlan& p=plan.columns[j];
        if (!p.draw) continue;
        const auto& c=p.drawArgs;
        if(c.x!=j+kLeft || c.page>1 || c.firstY<kTop ||
           c.firstY>kBottom || c.pixelCount==0 ||
           c.pixelCount>kBottom+1-c.firstY)
            return Status::InvalidPreparedColumn;
        std::uint32_t cursor=c.source16_16;
        for(unsigned y=0;y<c.pixelCount;++y) {
            if((cursor>>16u)>=p.source.size())
                return Status::InvalidPreparedColumn;
            cursor+=c.step16_16;
        }
    }
    for(const ColumnPlan& p:plan.columns) {
        if(!p.draw)continue;
        const auto status=wall::drawColumn(
            indexed,vram,p.drawArgs,p.source,p.useXLAT?&p.xlat:nullptr);
        // All preconditions above are validated, so this must succeed.
        if(status!=wall::Result::Written) return Status::InvalidPreparedColumn;
    }
    return Status::Ok;
}

} // namespace n3d::re::dos20::spanwall
