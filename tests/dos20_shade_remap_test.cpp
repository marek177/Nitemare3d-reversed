#include "re/N3DDos20ShadeRemap.hpp"
#include "re/N3DDos20ShadeXLAT.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <vector>
namespace sh=n3d::re::dos20::shade;
int main(){
    static_assert(sh::kShadeAmounts[0]==0 && sh::kShadeAmounts[7]==40);
    std::array<std::uint8_t,768> palette{};
    for(unsigned i=0;i<256;++i) {
        palette[3*i]=static_cast<std::uint8_t>(i%64);
        palette[3*i+1]=static_cast<std::uint8_t>((i/64)*12);
        palette[3*i+2]=static_cast<std::uint8_t>((i*7)%64);
    }
    // Tie semantics: palette entry 1 has the same exact RGB6 as entry 0,
    // hence even the shade=0 remap maps entry1 to the first index 0.
    palette[3]=palette[0];palette[4]=palette[1];palette[5]=palette[2];
    const auto zero=sh::build(palette,0);
    assert(zero.ok && zero.xlat[0]==0 && zero.xlat[1]==0);
    // Nonzero levels are the original fixed 8-value DOS table.
    for(unsigned level=0;level<8;++level){
        const auto actual=sh::build(palette,level);
        assert(actual.ok);
        sh::Table independent{};
        assert(sh::buildFromRgb6(palette,level,independent));
        assert(actual.xlat==independent); // independent native implementations
        for(unsigned src=0;src<256;++src){
            int target[3]{};
            for(unsigned c=0;c<3;++c){
                const int original=palette[3*src+c];
                target[c]=original>static_cast<int>(sh::kShadeAmounts[level])
                    ?original-static_cast<int>(sh::kShadeAmounts[level]):0;
            }
            int bestD=100000,bestIndex=-1;
            for(unsigned cand=0;cand<256;++cand){
                int d=0;
                for(unsigned c=0;c<3;++c){
                    const int diff=int(palette[3*cand+c])-target[c];
                    d+=diff>=0?diff:-diff;
                }
                if(d<bestD){bestD=d;bestIndex=static_cast<int>(cand);}
            }
            assert(actual.xlat[src]==static_cast<std::uint8_t>(bestIndex));
        }
    }
    std::array<std::uint8_t,768> grey{};
    for(unsigned n=0;n<256;++n){
        grey[n*3]=grey[n*3+1]=grey[n*3+2]=
            static_cast<std::uint8_t>(n<64?n:63);
    }
    auto level4=sh::build(grey,1);
    assert(level4.ok && level4.xlat[20]==16);
    auto level40=sh::build(grey,7);
    assert(level40.ok && level40.xlat[20]==0);
    assert(!sh::build(grey,8).ok);
    auto bad=grey;bad[7]=64;
    assert(!sh::build(bad,0).ok);
    assert(!sh::build(std::span<const std::uint8_t>(grey).subspan(1),0).ok);

    std::vector<std::uint8_t> ds(65536);
    for(unsigned i=0;i<768;++i)ds[0x4A64+i]=palette[i];
    ds[0x6278]=2;ds[0x6279]=0;
    auto dsRemap=sh::buildFromOriginalDS(ds);
    auto model=sh::build(palette,2);
    assert(dsRemap.ok && dsRemap.xlat==model.xlat);
    ds[0x6279]=1;assert(!sh::buildFromOriginalDS(ds).ok);
    ds[0x6279]=0;ds[0x6278]=0;
    assert(sh::buildFromOriginalDS(ds).xlat==zero.xlat);
    assert(!sh::buildFromOriginalDS(std::span<const std::uint8_t>(ds).subspan(1)).ok);
}
