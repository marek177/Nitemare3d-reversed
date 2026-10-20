#include "re/N3DDos20WallMaterialBinding.hpp"

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace m = n3d::re::dos20::wallmaterial;
namespace s = n3d::re::dos20::spanwall;
namespace sh = n3d::re::dos20::shade;

static void w16(std::vector<std::uint8_t>& b,unsigned p,unsigned v){
    b.at(p)=static_cast<std::uint8_t>(v);
    b.at(p+1)=static_cast<std::uint8_t>(v>>8);
}
static void w32(std::vector<std::uint8_t>& b,unsigned p,std::uint32_t v){
    w16(b,p,v&0xffffu); w16(b,p+2,v>>16u);
}
static void trigWord(std::array<std::uint8_t,1440>& b,unsigned p,
                     std::int16_t v){
    const std::uint16_t x=static_cast<std::uint16_t>(v);
    b[p]=static_cast<std::uint8_t>(x);
    b[p+1]=static_cast<std::uint8_t>(x>>8);
}

int main() {
    static_assert((std::int64_t(0x8340)*152*16)==81715200);
    static_assert((std::int64_t(0x2EE0)*304)/0x5000==178);
    static_assert(m::wrap16(-1)==-1);
    static_assert(m::wrap16(65537)==1);
    static_assert(m::normalizeAngle(-90)==270);

    std::array<std::uint8_t,1440> rawTrig{};
    trigWord(rawTrig,0,0);
    trigWord(rawTrig,2*45,724);
    trigWord(rawTrig,2*90,1024);
    trigWord(rawTrig,720+2*0,1024);
    trigWord(rawTrig,720+2*45,724);
    trigWord(rawTrig,720+2*90,0);
    auto trig=m::Trig360::load(rawTrig);
    assert(trig);
    assert(!m::Trig360::load(std::span(rawTrig).subspan(1)));
    rawTrig[2*45]=0;
    assert(!m::Trig360::load(rawTrig));
    trigWord(rawTrig,2*45,724);
    trig=m::Trig360::load(rawTrig);
    assert(trig);

    m::Vec v{};
    v.orientation=0;
    v.renderClass=1;
    v.flags=0x08; // skip endpoint correction in the isolated U test
    v.x1=1440; v.x2=1504;
    v.y1=3620; v.y2=3620;
    v.screenX1=0; v.screenX2=319;
    m::Camera camera{1440,3620,0};
    const auto centerU=m::perspectiveUCandidate(v,160,331,camera,*trig,64);
    assert(centerU && *centerU==0);
    assert(!m::perspectiveUCandidate(v,160,0,camera,*trig,64));
    assert(!m::perspectiveUCandidate(v,160,331,camera,*trig,32));
    v.orientation=2; v.x2=v.x1; v.y2=v.y1+64;
    // At 0 degrees vertical orientation, the EBD6 quotient is
    // trunc((81715200/331)/1024) = 241, masked to 64 -> 49.
    const auto verticalU=m::perspectiveUCandidate(v,160,331,camera,*trig,64);
    assert(verticalU && *verticalU==49);
    v.orientation=0;v.x2=v.x1+64;v.y2=v.y1;
    v.renderClass=0x3F;
    v.flags=0x08;
    const auto curtain=m::perspectiveUCandidate(v,160,331,camera,*trig,128);
    assert(curtain && *curtain==64); // class 3F flips the endpoint
    v.renderClass=1;
    const auto ordinary=m::perspectiveUCandidate(v,160,331,camera,*trig,128);
    assert(ordinary && *ordinary==0);
    v.flags=0x28;
    const auto flagFlip=m::perspectiveUCandidate(v,160,331,camera,*trig,128);
    assert(flagFlip && *flagFlip==64);
    // No silent "fix" for an original 16-bit divided-by-zero condition.
    auto zeroTrig=*trig;
    zeroTrig.cos[0]=0;
    assert(!m::perspectiveUCandidate(v,160,331,camera,zeroTrig,64));

    constexpr unsigned dirSize=0xBC00, frame64=10+4096,
                       frame128=10+8192;
    const unsigned stream1=dirSize;
    const unsigned stream2=stream1+2*frame64;
    std::vector<std::uint8_t> img(stream2+frame128);
    w32(img,4*5,stream1);
    w32(img,4*6,stream1); // wall 5 and 6 alias same animation stream
    w32(img,4*7,stream2);
    w16(img,0x800+5*90,0);
    img[0x800+5*90+2]=2;
    img[0x800+7*90+2]=1;
    img[stream1]=64; img[stream1+1]=64;
    std::fill(img.begin()+stream1+10,
              img.begin()+stream1+frame64,42);
    img[stream1+frame64]=64;
    img[stream1+frame64+1]=64;
    std::fill(img.begin()+stream1+frame64+10,
              img.begin()+stream2,79);
    img[stream2]=128;img[stream2+1]=64;
    for(unsigned u=0;u<128;++u)
      for(unsigned y=0;y<64;++y)
        img[stream2+10+u*64+y]=u<64?40:80;

    std::vector<std::uint8_t> ds(65536);
    w16(ds,s::kSpanCountOffset,1);
    const unsigned a=s::kVecBase,b=a+28,c=b+28;
    ds[a]=5;ds[a+3]=0;ds[a+4]=0;ds[a+5]=0x08;ds[a+6]=1;ds[a+7]=0;
    ds[b]=6;ds[b+3]=1;ds[b+4]=0;ds[b+5]=0x08;ds[b+6]=1;ds[b+7]=0;
    ds[c]=7;ds[c+3]=0;ds[c+4]=1;ds[c+5]=0x08;ds[c+6]=1;ds[c+7]=0;
    for(unsigned ptr:{a,b,c}) {
        w16(ds,ptr+12,1440);
        w16(ds,ptr+14,3620);
        w16(ds,ptr+16,1504);
        w16(ds,ptr+18,3620);
        w16(ds,ptr+20,0);
        w16(ds,ptr+24,319);
    }
    w16(ds,s::kSpanBase,a);
    w16(ds,s::kSpanBase+2,8);
    w16(ds,s::kSpanBase+4,331);
    w16(ds,s::kSpanBase+6,311);
    w16(ds,s::kSpanBase+8,331);
    w32(ds,s::kSpanBase+10,0);
    w32(ds,s::kSpanBase+14,331u<<16u);
    for(unsigned x=8;x<=311;++x) w16(ds,s::kOwnerOffset+2*x,a);

    m::ImgWallCatalog catalog{};
    assert(catalog.build(img,ds,3));
    assert(catalog.caches.size()==2);
    auto selected5=catalog.select(m::vecFromDosDS(ds,a));
    auto selected6=catalog.select(m::vecFromDosDS(ds,b));
    auto selected7=catalog.select(m::vecFromDosDS(ds,c));
    assert(selected5 && selected5->frame.width==64 &&
           selected5->selectedFrameIndex==0);
    assert(selected6 && selected6->frame.width==64 &&
           selected6->selectedFrameIndex==1);
    assert(selected7 && selected7->frame.width==128 &&
           selected7->selectedFrameIndex==0);
    assert(selected5->frame.pixels[0]==42);
    assert(selected6->frame.pixels[0]==79);
    assert(selected7->frame.pixels[0]==40);
    assert(selected7->frame.pixels[64*64]==80);
    assert(selected5->frame.fileOffset==stream1);
    assert(selected6->frame.fileOffset==stream1+frame64);
    assert(selected7->frame.fileOffset==stream2);

    auto highFrame=m::vecFromDosDS(ds,b);
    highFrame.animationFrame=255;
    const auto clamped=catalog.select(highFrame);
    assert(clamped && clamped->clampedAnimationFrame);
    assert(clamped->selectedFrameIndex==1);

    sh::Palette basePalette{};
    for(unsigned i=0;i<256;++i){
        basePalette[3*i]=static_cast<std::uint8_t>(i%64);
        basePalette[3*i+1]=static_cast<std::uint8_t>(i/64);
    }
    std::copy(basePalette.begin(),basePalette.end(),ds.begin()+0x4A64);
    ds[0x6278]=0; ds[0x6279]=0;
    sh::Prepared shading{};
    assert(sh::prepareFromDosSegment(ds,shading));
    m::MaterialBinder material{ds,&catalog,&*trig,&shading,nullptr,camera};
    s::Plan plan{};
    assert(s::prepare(ds,3,0,material,plan)==s::Status::Ok);
    assert(plan.drawnColumns==304);
    assert(plan.columns[0].spanYQ4==331);
    std::vector<std::uint8_t> frame(64000,0xff);
    assert(s::render(plan,frame,{})==s::Status::Ok);
    for(unsigned x=8;x<=311;++x) {
        for(unsigned y=59;y<=100;++y)
            assert(frame[y*320+x]==42);
    }

    // Switch the owner to aliased wall 6: the exact shared IMG stream
    // selector produces frame 1 rather than wall-ID-based preview pixels.
    w16(ds,s::kSpanBase,b);
    for(unsigned x=8;x<=311;++x)w16(ds,s::kOwnerOffset+2*x,b);
    material.ds=ds;
    assert(s::prepare(ds,3,0,material,plan)==s::Status::Ok);
    std::fill(frame.begin(),frame.end(),0xff);
    assert(s::render(plan,frame,{})==s::Status::Ok);
    assert(frame[59*320+8]==79 && frame[100*320+311]==79);

    // Actual DOS shade source is DS:4A64 plus selector DS:6278;
    // the same IMG source index 79 must pass through shade=4 -> index 11.
    ds[0x6278]=1;
    ds[0x430E]=1; // enable global shade on orientation 0/1
    sh::Prepared darker{};
    assert(sh::prepareFromDosSegment(ds,darker));
    material.ds=ds;
    material.shading=&darker;
    material.shadingZero=&shading;
    assert(s::prepare(ds,3,0,material,plan)==s::Status::Ok);
    std::fill(frame.begin(),frame.end(),0xff);
    assert(s::render(plan,frame,{})==s::Status::Ok);
    assert(frame[59*320+8]==11 && frame[100*320+311]==11);

    // DOS2 local 25DC shade selection: orientation0/1, shadeIndex>0,
    // DS:430E==0 forces shade ZERO, unlike the global darker remap.
    ds[0x430E]=0;
    assert(m::useZeroShadeForWall(ds,m::vecFromDosDS(ds,b),1));
    auto vert=m::vecFromDosDS(ds,b);vert.orientation=2;
    assert(!m::useZeroShadeForWall(ds,vert,1));
    assert(!m::useZeroShadeForWall(ds,m::vecFromDosDS(ds,b),0));
    material.shadingZero=nullptr;
    assert(s::prepare(ds,3,0,material,plan)==s::Status::InvalidWallMaterial);
    material.shadingZero=&shading;
    assert(s::prepare(ds,3,0,material,plan)==s::Status::Ok);
    std::fill(frame.begin(),frame.end(),0xff);
    assert(s::render(plan,frame,{})==s::Status::Ok);
    assert(frame[59*320+8]==79 && frame[100*320+311]==79);
    ds[0x6278]=0;
    material.shading=&shading;

    // Third cache has genuine 128x64 (2 x 64x64) frames. Per-column
    // integer U can select both physical halves; no 128 -> 64 squash.
    w16(ds,s::kSpanBase,c);
    for(unsigned x=8;x<=311;++x)w16(ds,s::kOwnerOffset+2*x,c);
    material.ds=ds;
    assert(s::prepare(ds,3,0,material,plan)==s::Status::Ok);
    std::fill(frame.begin(),frame.end(),0xff);
    assert(s::render(plan,frame,{})==s::Status::Ok);
    assert(frame[59*320+8]==80);   // original U candidate x8 -> second face
    assert(frame[59*320+160]==40); // screen center U=0 -> first face
    assert(frame[59*320+311]==40);

    // Strict version/cache guard: missing or out-of-bounds IMG resources
    // reject the entire catalog build without mutating its previous caches.
    const auto originalCaches=catalog.caches.size();
    ds[b+4]=1;  // same stream MUST have same byte cache selector
    assert(!catalog.select(m::vecFromDosDS(ds,b)));
    assert(!catalog.build(img,ds,3));
    assert(catalog.caches.size()==originalCaches);
    ds[b+4]=0;
    // A stale/wrong cache selector must not silently show another IMG frame.
    ds[c+4]=0;
    assert(!catalog.select(m::vecFromDosDS(ds,c)));
    ds[c+4]=1;
    std::vector<std::uint8_t> broken=img;
    broken[0x800+5*90+2]=0;
    assert(!catalog.build(broken,ds,3));
    assert(catalog.caches.size()==originalCaches);
    broken=img;
    w32(broken,4*7,static_cast<unsigned>(broken.size()-2));
    assert(!catalog.build(broken,ds,3));
    assert(catalog.caches.size()==originalCaches);
    assert(!catalog.build(std::span(img).subspan(1),ds,3));
    assert(catalog.caches.size()==originalCaches);

    // Missing exact U/trig/selector/shading is not replaced by DDA fallback.
    m::MaterialBinder invalid=material;
    invalid.trig=nullptr;
    const auto priorPlan=plan;
    assert(s::prepare(ds,3,0,invalid,plan)==s::Status::InvalidWallMaterial);
    assert(plan.drawnColumns==priorPlan.drawnColumns);
    invalid=material;
    invalid.shading=nullptr;
    assert(s::prepare(ds,3,0,invalid,plan)==s::Status::InvalidWallMaterial);
}
