#include "re/N3DDos20SpanWallPipeline.hpp"

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iterator>
#include <optional>
#include <span>
#include <vector>

using namespace n3d::re::dos20;
namespace sp = n3d::re::dos20::spanwall;

static void put16(std::vector<std::uint8_t>& mem,unsigned at,std::uint16_t v){
    mem.at(at)=static_cast<std::uint8_t>(v);
    mem.at(at+1)=static_cast<std::uint8_t>(v>>8u);
}
static void put32(std::vector<std::uint8_t>& mem,unsigned at,std::uint32_t v){
    put16(mem,at,static_cast<std::uint16_t>(v));
    put16(mem,at+2,static_cast<std::uint16_t>(v>>16u));
}
static std::vector<std::uint8_t> fixture(unsigned spans) {
    assert(spans>=1 && spans<=9);
    std::vector<std::uint8_t> mem(65536);
    put16(mem,sp::kRemainingOffset,0);
    put16(mem,sp::kSpanCountOffset,static_cast<std::uint16_t>(spans));
    for(unsigned j=0;j<spans;++j){
        const unsigned x0=8+j*304/spans;
        const unsigned x1=8+(j+1)*304/spans-1;
        const auto ptr=static_cast<std::uint16_t>(sp::kVecBase+j*28);
        const unsigned at=sp::kSpanBase+j*sp::kSpanStride;
        mem[ptr]=static_cast<std::uint8_t>(10+j);
        mem[ptr+5]=7;
        mem[ptr+7]=static_cast<std::uint8_t>(j%4);
        put16(mem,at,ptr);
        put16(mem,at+2,static_cast<std::uint16_t>(x0));
        put16(mem,at+4,static_cast<std::uint16_t>(331+16*j));
        put16(mem,at+6,static_cast<std::uint16_t>(x1));
        put16(mem,at+8,static_cast<std::uint16_t>(331+16*j));
        put32(mem,at+10,0);
        put32(mem,at+14,static_cast<std::uint32_t>(331+16*j)<<16u | 0x800Fu);
        for(unsigned x=x0;x<=x1;++x)put16(mem,sp::kOwnerOffset+2*x,ptr);
    }
    return mem;
}
static std::array<std::uint8_t,8192> doubleFace(){
    std::array<std::uint8_t,8192> img{};
    for(unsigned u=0;u<128;++u)
      for(unsigned v=0;v<64;++v)
        img[u*64+v] = static_cast<std::uint8_t>(u<64 ? 0x1F : 0x42);
    return img;
}

int main(int argc,char**argv){
    // Recovered DOS 2500 -> 1A2E vertical geometry for original captured
    // E1M1 x8 original span phase high 331. Entire intermediate IMG/DS
    // content is NOT included in this synthetic test.
    static_assert(sp::kColumns==304);
    static_assert(sp::signedShiftRight4(1611)==100);
    static_assert(sp::signedShiftRight4(-1)==-1);
    static_assert(sp::signedShiftRight4(-17)==-2);
    constexpr auto v=sp::verticalFromSpanQ4(331);
    static_assert(v.has_value());
    static_assert(v->visible && v->projectedBottomY==100);
    static_assert(v->heightIndex==41);
    static_assert(v->firstY==59 && v->pixelCount==42);
    static_assert(v->step16_16==0x00018F9Cu);
    static_assert(v->source16_16==0);
    constexpr auto e=sp::verticalFromSpanQ4(1200);
    static_assert(e && e->visible && e->projectedBottomY==155);
    static_assert(e->heightIndex==151 && e->firstY==4 && e->pixelCount==152);
    constexpr auto clip=sp::verticalFromSpanQ4(1232);
    static_assert(clip && clip->visible && clip->heightIndex==155);
    static_assert(clip->firstY==4 && clip->pixelCount==152);
    static_assert(clip->source16_16 ==
        ((3u*64u*65536u/155u)>>1u));
    static_assert(sp::verticalFromSpanQ4(-2000)->visible==false);
    static_assert(!sp::verticalFromSpanQ4(8192));

    const auto image=doubleFace();
    std::array<std::uint8_t,256> lut{};
    for(unsigned i=0;i<256;++i)lut[i]=static_cast<std::uint8_t>(i);
    lut[0x42]=0x57;
    const auto material=[&](unsigned x,std::uint16_t p,std::uint8_t wallId,
                           const sp::Span& span,int bottom,unsigned height)
                           -> std::optional<sp::Material>{
        assert(x>=8 && x<=311);
        assert(sp::validNear(p,9));
        assert(span.nearOwner==p);
        assert(wallId>=10 && wallId<=18);
        assert(bottom>=100 && bottom<=108);
        assert(height>=41 && height<=57);
        return sp::Material{image,128,64,x<160 ? 0u:64u,&lut};
    };

    auto mem=fixture(1);
    sp::Plan plan{};
    assert(sp::prepare(mem,1,1,material,plan)==sp::Status::Ok);
    assert(plan.spanCount==1 && plan.drawnColumns==304);
    assert(plan.culledColumns==0);
    assert(plan.columns[0].nearOwner==sp::kVecBase);
    assert(plan.columns[0].drawArgs.firstY==59);
    assert(plan.columns[0].drawArgs.pixelCount==42);
    assert(plan.columns[0].drawArgs.step16_16==0x18F9C);
    assert(plan.columns[0].heightIndex==41);
    assert(plan.columns[303].drawArgs.x==311);
    std::vector<std::uint8_t> frame(64000,0xEE);
    std::vector<std::uint8_t> vram(2097152,0xEE);
    assert(sp::render(plan,frame,vram)==sp::Status::Ok);
    for(unsigned x=8;x<=311;++x) {
        const std::uint8_t expected=x<160 ? 0x1F : 0x57;
        for(unsigned y=59;y<=100;++y) {
            assert(frame[y*320+x]==expected);
            assert(vram[wall::interleavedVgaOffset(1,x,y)]==expected);
            assert(vram[wall::interleavedVgaOffset(0,x,y)]==0xEE);
        }
        assert(frame[58*320+x]==0xEE);
        assert(frame[101*320+x]==0xEE);
    }
    assert(frame[59*320+7]==0xEE);
    assert(frame[59*320+312]==0xEE);
    assert(frame[0]==0xEE && frame[199*320+319]==0xEE);
    assert(plan.columns[0].source[0]==0x1F);
    assert(plan.columns[303].source[0]==0x42);

    // A nine-run VEC/OWNER/SPAN fixture exercises the exact original
    // 28-byte VEC / 16-bit owner / 18-byte span record widths.
    mem=fixture(9);
    const auto preserved=frame;
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::Ok);
    assert(plan.spanCount==9 && plan.drawnColumns==304);
    for(unsigned x=8;x<=311;++x) {
        const unsigned j=(x-8+1)*9/304; // not a required span index formula
        (void)j;
        const auto& p=plan.columns[x-8];
        assert(sp::validNear(p.nearOwner,9));
        assert(p.spanIndex<9);
        assert(p.drawArgs.x==x);
        assert(p.drawArgs.page==0);
    }
    assert(plan.columns[0].drawArgs.firstY==59);
    assert(plan.columns[303].drawArgs.firstY==51);
    assert(plan.columns[303].drawArgs.pixelCount==58);
    std::fill(frame.begin(),frame.end(),0xEE);
    assert(sp::render(plan,frame,{})==sp::Status::Ok);
    assert(frame[59*320+8]==0x1F);
    assert(frame[108*320+311]==0x57);
    assert(frame[50*320+311]==0xEE);

    // Invalid input never changes the preceding complete plan.
    const auto beforePlan=plan;
    put16(mem,sp::kOwnerOffset+2*18,0);
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::OwnerMismatch);
    assert(plan.columns[0].spanIndex==beforePlan.columns[0].spanIndex);
    assert(plan.drawnColumns==beforePlan.drawnColumns);
    mem=fixture(9);
    put16(mem,sp::kSpanBase+2,9);
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::InvalidSpanRange);
    mem=fixture(9);
    put16(mem,sp::kSpanBase,0xB000);
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::InvalidNearPointer);
    mem=fixture(9);
    put16(mem,sp::kRemainingOffset,1);
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::IncompleteOwnerViewport);
    mem=fixture(9);
    put16(mem,sp::kSpanCountOffset,51);
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::InvalidSpanCount);
    mem=fixture(9);
    assert(sp::prepare(mem,0,0,material,plan)==sp::Status::InvalidVecCount);
    assert(sp::prepare(mem,9,2,material,plan)==sp::Status::InvalidVga);
    assert(sp::prepare(std::span<const std::uint8_t>(mem).subspan(1),
                       9,0,material,plan)==sp::Status::InvalidSegment);
    const auto missing=[&](auto,auto,auto,const auto&,auto,auto)
                         -> std::optional<sp::Material>{return std::nullopt;};
    assert(sp::prepare(mem,9,0,missing,plan)==sp::Status::InvalidWallMaterial);
    const auto invalidU=[&](auto,auto,auto,const auto&,auto,auto)
                          -> std::optional<sp::Material>{
        return sp::Material{image,128,64,128,&lut};
    };
    assert(sp::prepare(mem,9,0,invalidU,plan)==sp::Status::InvalidWallMaterial);
    assert(plan.drawnColumns==beforePlan.drawnColumns);

    // All-column preflight, no partial drawing, even after plan corruption.
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::Ok);
    std::fill(frame.begin(),frame.end(),0xEE);
    plan.columns[303].drawArgs.source16_16=64u<<16u;
    assert(sp::render(plan,frame,{})==sp::Status::InvalidPreparedColumn);
    assert(std::all_of(frame.begin(),frame.end(),
                       [](auto c){return c==0xEE;}));
    assert(sp::prepare(mem,9,0,material,plan)==sp::Status::Ok);
    assert(sp::render(plan,std::span<std::uint8_t>(frame).subspan(1),{}) ==
           sp::Status::InvalidFrame);
    std::vector<std::uint8_t> wrongVram(1024);
    assert(sp::render(plan,frame,wrongVram)==sp::Status::InvalidVga);

    // Optional authentic check against the user's private original DOS2
    // 64KiB segment. It does NOT need original IMG files: synthetic texture
    // provider checks only owner->span->per-column geometry/writes.
    if(argc>1) {
        std::ifstream input(argv[1],std::ios::binary);
        assert(input);
        const std::vector<std::uint8_t> original{
            std::istreambuf_iterator<char>(input),{}};
        assert(original.size()==65536);
        const auto snapshotMaterial=[&](unsigned,
             std::uint16_t near,std::uint8_t, const sp::Span&, int, unsigned)
             -> std::optional<sp::Material> {
            assert(sp::validNear(near,592));
            return sp::Material{image,128,64,64,&lut};
        };
        assert(sp::prepare(original,592,0,snapshotMaterial,plan)==sp::Status::Ok);
        assert(plan.spanCount==9 && plan.drawnColumns==304);
        assert(plan.columns[0].drawArgs.firstY==59);
        assert(plan.columns[0].drawArgs.pixelCount==42);
        assert(plan.columns[0].drawArgs.step16_16==0x18F9C);
        assert(sp::render(plan,frame,{})==sp::Status::Ok);
    }
}
