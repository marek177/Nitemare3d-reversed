#include "re/N3DDos20VisibilityOpcodeContract.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <random>
#include <stdexcept>
#include <vector>
namespace v=n3d::re::dos20::v070;

static std::uint16_t u16(const std::vector<std::uint8_t>& b,std::size_t a){
    return static_cast<std::uint16_t>(b.at(a) | (std::uint16_t(b.at(a+1))<<8));
}
static std::int16_t i16(const std::vector<std::uint8_t>& b,std::size_t a){
    const int x=u16(b,a);return static_cast<std::int16_t>(x<0x8000?x:x-0x10000);
}
static bool independentReference(const v::Vec& a,const v::Vec& b){
    const int i=a.orientation,j=b.orientation;
    if(i==0 && j==2)return b.x0>a.x0 && b.y0<a.y0;
    if(i==0 && j==3)return b.x1<a.x1 && b.y0<a.y0;
    if(i==1 && j==2)return b.x0>a.x0 && b.y1>a.y1;
    if(i==1 && j==3)return b.x1<a.x1 && b.y1>a.y1;
    if(i==2 && j==0)return b.x1>a.x1 && b.y1<a.y1;
    if(i==2 && j==1)return b.x1>a.x1 && b.y0>a.y0;
    if(i==3 && j==0)return b.x0<a.x0 && b.y1<a.y1;
    if(i==3 && j==1)return b.x0<a.x0 && b.y0>a.y0;
    return false;
}
static void synthetic(){
    assert(v::active(1));assert(v::active(0xff));assert(!v::active(0x00));
    assert(!v::active(0x0e));
    std::mt19937 rng(0x70C0DEu);
    std::uniform_int_distribution<int> d(-512,512);
    int yes=0,no=0;
    for(int old=0;old<4;++old){
        for(int candidate=0;candidate<4;++candidate){
            for(int n=0;n<20000;++n){
                v::Vec a{static_cast<std::int16_t>(d(rng)),static_cast<std::int16_t>(d(rng)),
                         static_cast<std::int16_t>(d(rng)),static_cast<std::int16_t>(d(rng)),
                         static_cast<std::uint8_t>(old),1};
                v::Vec b{static_cast<std::int16_t>(d(rng)),static_cast<std::int16_t>(d(rng)),
                         static_cast<std::int16_t>(d(rng)),static_cast<std::int16_t>(d(rng)),
                         static_cast<std::uint8_t>(candidate),1};
                auto got=v::replaces(a,b);
                assert(got==independentReference(a,b));
                if(got)++yes;else ++no;
                auto same=a;same.orientation=static_cast<std::uint8_t>(candidate);
                assert(!v::replaces(a,same));
            }
        }
    }
    assert(yes>0 && no>0);
    v::Camera cam{1440,3620,177,1008,1280,155,81715200};
    v::Vec a{1344,3584,1344,3648,2,7};
    const auto x=v::projectVerticalAndTestEarlyCull(a,cam);
    assert(x.newProjectedYQ4[0]==5514 && x.newProjectedYQ4[1]==6267);
    assert(x.cullThresholdQ4==5360 && x.earlyReturnBeforeX);
    v::Vec b{1792,3712,1792,3840,3,7};
    const auto y=v::projectVerticalAndTestEarlyCull(b,cam);
    assert(y.newProjectedYQ4[0]==6267 && y.newProjectedYQ4[1]==6267);
    assert(y.earlyReturnBeforeX);
    v::Camera atBoundary{0,0,0,1024,0,0,180*16*0x4000LL};
    auto borderline=v::projectVerticalAndTestEarlyCull({0,0,64,-128,0,1},atBoundary);
    assert(!borderline.earlyReturnBeforeX);
    std::cout<<"SYNTHETIC_PASS 320000 conflict combinations; early vertical cull examples OK\n";
}
static void original(const char* path){
    std::ifstream f(path,std::ios::binary);
    if(!f)throw std::runtime_error("Snapshot could not be opened");
    const std::vector<std::uint8_t> b{std::istreambuf_iterator<char>(f),{}};
    if(b.size()!=65536)throw std::runtime_error("Expected full original 64KiB DOS2 memory segment");
    v::Camera cam{i16(b,0x4162),i16(b,0x4164),i16(b,0x41b2),i16(b,0x41b4),
                  i16(b,0x4554),i16(b,0x454e),
                  std::int64_t(u16(b,0x3686))+(std::int64_t(u16(b,0x3688))<<16)};
    int culled=0;
    for(const int p : {0x8a28,0x9a90}){
        const v::Vec vec{i16(b,p+12),i16(b,p+14),i16(b,p+16),i16(b,p+18),b[p+7],b[p+5]};
        const auto c=v::projectVerticalAndTestEarlyCull(vec,cam);
        assert(c.newProjectedYQ4[0]==i16(b,p+22));
        assert(c.newProjectedYQ4[1]==i16(b,p+26));
        assert(c.earlyReturnBeforeX);
        ++culled;
    }
    assert(culled==2);
    std::cout<<"ORIGINAL_SNAPSHOT_PASS: 2/2 early culls, 4/4 written Y WORDs exact; X is not rewritten on this branch\n";
}
int main(int argc,char**argv){
    synthetic();if(argc>1)original(argv[1]);return 0;
}
