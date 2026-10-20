#include "re/N3DDos20ShadeXLAT.hpp"
#include "re/N3DDos20IndexedWallColumn.hpp"
#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <span>
#include <vector>

namespace sh = n3d::re::dos20::shade;
namespace w = n3d::re::dos20::wall;
int main() {
    static_assert(sh::kShadeLevels == std::array<std::uint8_t,8>{0,4,8,12,16,20,30,40});

    sh::Palette unique{};
    for(unsigned i=0;i<256;++i) {
        unique[3*i]=static_cast<std::uint8_t>(i%64);
        unique[3*i+1]=static_cast<std::uint8_t>(i/64);
        unique[3*i+2]=0;
    }
    assert(sh::isRgb6(unique));
    sh::Table t{};
    assert(sh::buildFromRgb6(unique,0,t));
    for(unsigned i=0;i<256;++i)assert(t[i]==i);

    // The 0x16CE mapper subtracts in SIX-BIT palette space, before the
    // Manhattan nearest-color search. The target color for src 79 (15,1,0)
    // under shade amount 4 is (11,0,0), whose exact palette index is 11.
    assert(sh::buildFromRgb6(unique,1,t));
    assert(t[79]==11);
    assert(t[3]==0); // negative source channels clamp to zero
    assert(sh::buildFromRgb6(unique,7,t));
    assert(t[63]==23); // 63 -> 23 after shade 40

    // First/lower candidate wins ties, even at shade index 0.
    sh::Palette duplicate{};
    duplicate.fill(0);
    duplicate[3*11]=6; duplicate[3*11+1]=7; duplicate[3*11+2]=8;
    duplicate[3*201]=6; duplicate[3*201+1]=7; duplicate[3*201+2]=8;
    assert(sh::buildFromRgb6(duplicate,0,t));
    assert(t[201]==11); // NOT an identity map
    assert(t[11]==11);
    assert(t[200]==0); // duplicate black palette entries map to zero
    for(unsigned shade=0;shade<8;++shade)
        assert(sh::buildFromRgb6(duplicate,shade,t));

    // Exact RGB8 -> VGA6 truncation / strict-bounds semantics.
    std::array<std::uint8_t,768> rgb8{};
    for(unsigned i=0;i<768;++i)rgb8[i]=
        static_cast<std::uint8_t>((i*119+31u)%256);
    std::array<std::uint8_t,768> rgb6{};
    for(unsigned i=0;i<768;++i)rgb6[i]=rgb8[i]>>2u;
    sh::Table from8{},from6{};
    for(unsigned shade=0;shade<8;++shade) {
        assert(sh::buildFromRgb8(rgb8,shade,from8));
        assert(sh::buildFromRgb6(rgb6,shade,from6));
        assert(from8==from6);
    }

    // Invalid callers MUST NOT lose the previous good translation.
    const auto saved=t;
    assert(!sh::buildFromRgb6(rgb6,8,t));
    assert(!sh::buildFromRgb6(std::span(rgb6).subspan(1),0,t));
    std::array<std::uint8_t,768> bad=rgb6;
    bad[37]=64;
    assert(!sh::buildFromRgb6(bad,0,t));
    assert(!sh::buildFromRgb8(std::span(rgb8).subspan(1),0,t));
    assert(t==saved);

    sh::Prepared p{};
    assert(sh::prepare(duplicate,0,p));
    assert(p.xlat[201]==11);
    const auto preserved=p;
    assert(!sh::prepare(bad,0,p));
    assert(p.xlat==preserved.xlat);
    assert(p.baseRgb6==preserved.baseRgb6);
    assert(p.shadeIndex==preserved.shadeIndex);

    // Reading original global palette and shade from the 64KiB DOS segment
    // must use DS:4A64 RGB6 and DS:6278 WORD, not the current RGB8 DAC fade.
    std::vector<std::uint8_t> ds(65536);
    std::copy(duplicate.begin(),duplicate.end(),ds.begin()+0x4A64);
    ds[0x6278]=0; ds[0x6279]=0;
    sh::Prepared originalLayout{};
    assert(sh::prepareFromDosSegment(ds,originalLayout));
    assert(originalLayout.shadeIndex==0);
    assert(originalLayout.xlat[201]==11);
    std::copy(originalLayout.xlat.begin(),originalLayout.xlat.end(),
              ds.begin()+0xD20C);
    assert(sh::matchesStoredDosXlat(ds,originalLayout));
    ds[0xD20C+201]=200;
    assert(!sh::matchesStoredDosXlat(ds,originalLayout));
    ds[0xD20C+201]=11;
    ds[0x6278]=8; // invalid shade index
    const auto previous=originalLayout;
    assert(!sh::prepareFromDosSegment(ds,originalLayout));
    assert(originalLayout.xlat==previous.xlat);
    ds[0x6278]=0;
    ds[0x4A64]=64; // out-of-range RGB6 channel
    assert(!sh::prepareFromDosSegment(ds,originalLayout));
    ds[0x4A64]=0;
    assert(sh::prepareFromDosSegment(ds,originalLayout));
    assert(!sh::prepareFromDosSegment(std::span(ds).subspan(1),originalLayout));

    // Feed the recovered remap into v0.74's REAL indexed wall writer, proving
    // the bridge does not quietly bypass XLAT or make index 0x1F transparent.
    std::vector<std::uint8_t> indexed(w::kIndexedBytes,255);
    std::array<std::uint8_t,64> column{};
    column.fill(201);
    column[1]=0x1F;
    assert(sh::prepare(duplicate,0,p));
    assert(w::drawColumn(indexed,{},w::Column{8,59,2,0,0x10000u,0},
                         column,&p.xlat)==w::Result::Written);
    assert(indexed[59*320+8]==11);
    assert(indexed[60*320+8]==0); // duplicate black entry selects first 0
    assert(indexed[61*320+8]==255);
    assert(indexed[59*320+9]==255);
}
