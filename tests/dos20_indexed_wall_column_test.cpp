#include "re/N3DDos20IndexedWallColumn.hpp"

#include <algorithm>
#include <array>
#include <cassert>
#include <cstdint>
#include <span>
#include <vector>

using namespace n3d::re::dos20::wall;

int main() {
    static_assert(kIndexedBytes == 64000);
    static_assert(kVgaBytes == 2097152);
    static_assert(interleavedVgaOffset(0,8,59) == 18888);
    static_assert(interleavedVgaOffset(1,8,59) == 0x10000 + 18888);
    static_assert(interleavedVgaOffset(0,319,199) == 63999);
    static_assert(interleavedVgaOffset(0,0,0) == 0);

    // Exact bounded DOS2 writer witness parameters from the original E1M1
    // 097A:0599..05D5 trace: 42 logical pixel stores, x8 y59..100,
    // source step integer 1 + fractional 0x8F9C, SS:BX=0xD20C XLAT.
    // Texture samples other than first/last are synthetic here: this test
    // does NOT pretend to re-run the original 64KiB source/SS dumps.
    std::vector<std::uint8_t> indexed(kIndexedBytes, 0xEE);
    std::vector<std::uint8_t> vram(kVgaBytes, 0xEE);
    std::array<std::uint8_t,64> source{};
    for(unsigned i=0;i<64;++i) source[i]=static_cast<std::uint8_t>(i);
    source[0]=149; source[63]=143;
    std::array<std::uint8_t,256> lut{};
    for(unsigned i=0;i<256;++i) lut[i]=static_cast<std::uint8_t>(i);
    lut[149]=139; lut[143]=134;
    const Column originalWitness{8,59,42,0,0x00018F9Cu,0};

    assert(drawColumn(indexed, vram, originalWitness, source, &lut) ==
           Result::Written);
    assert(indexed[59*320+8] == 139);
    assert(indexed[100*320+8] == 134);
    assert(indexed[58*320+8] == 0xEE && indexed[101*320+8] == 0xEE);
    assert(indexed[59*320+9] == 0xEE);
    assert(vram[interleavedVgaOffset(0,8,59)] == 139);
    assert(vram[interleavedVgaOffset(0,8,100)] == 134);
    assert(vram[interleavedVgaOffset(1,8,59)] == 0xEE);
    // Every original bounded column read stays within source texels 0..63.
    std::uint32_t position=0;
    for(unsigned y=0;y<42;++y) {
        const auto texel=source[position >> 16u];
        const auto expected=lut[texel];
        assert((position>>16u)<64);
        assert(indexed[(59+y)*320+8]==expected);
        assert(vram[interleavedVgaOffset(0,8,59+y)]==expected);
        position+=0x18F9Cu;
    }
    assert((position >> 16u) == 65); // cursor AFTER last store

    // A 128x64 IMG frame contains two 64x64 faces: passing *physical* U
    // selects the full texture column. There is no DDA face guessing.
    std::vector<std::uint8_t> paired(128*64);
    for(unsigned u=0;u<128;++u)
        for(unsigned y=0;y<64;++y)
            paired[u*64+y]=u<64?0x1Fu:0x42u;
    std::array<std::uint8_t,64> selected{};
    selected.fill(0xCC);
    assert(selectPhysicalColumn(paired,128,64,0,selected));
    assert(std::all_of(selected.begin(),selected.end(),
                       [](auto c){return c==0x1F;}));
    assert(drawColumn(indexed,vram,Column{9,4,64,0,0x10000u,0},
                      selected)==Result::Written);
    // 0x1F is transparent for DOS SPRITES, but NOT for a wall column.
    assert(indexed[4*320+9]==0x1F);
    assert(indexed[67*320+9]==0x1F);

    assert(selectPhysicalColumn(paired,128,64,64,selected));
    assert(std::all_of(selected.begin(),selected.end(),
                       [](auto c){return c==0x42;}));
    assert(drawColumn(indexed,vram,Column{10,4,64,0,0x10000u,1},
                      selected)==Result::Written);
    assert(indexed[4*320+10]==0x42 && indexed[67*320+10]==0x42);
    assert(vram[interleavedVgaOffset(1,10,4)]==0x42);
    assert(vram[interleavedVgaOffset(0,10,4)]==0xEE);
    assert(vram[interleavedVgaOffset(1,10,4)-1]==0xEE);

    const auto beforeSelected=selected;
    assert(!selectPhysicalColumn(paired,128,64,128,selected));
    assert(!selectPhysicalColumn(paired,128,32,64,selected));
    assert(!selectPhysicalColumn(paired,256,64,64,selected));
    assert((selected==beforeSelected));

    // Preflight across ALL samples prevents partial source/VRAM writes.
    const auto baselineFrame=indexed;
    const auto baselineVram=vram;
    assert(drawColumn(indexed,vram,Column{11,4,2,63u<<16u,1u<<16u,0},
                      selected)==Result::InvalidTextureSource);
    assert(indexed==baselineFrame && vram==baselineVram);
    assert(drawColumn(indexed,vram,Column{320,4,1,0,0,0},selected) ==
           Result::InvalidViewport);
    assert(drawColumn(indexed,vram,Column{8,199,2,0,0,0},selected) ==
           Result::InvalidViewport);
    assert(drawColumn(indexed,vram,Column{8,4,1,0,0,2},selected) ==
           Result::InvalidVgaPage);
    std::vector<std::uint8_t> tooSmall(kVgaBytes-1);
    assert(drawColumn(indexed,tooSmall,Column{8,4,1,0,0,0},selected) ==
           Result::InvalidVgaBuffer);
    std::vector<std::uint8_t> badFrame(63999);
    assert(drawColumn(badFrame,{},Column{8,4,1,0,0,0},selected) ==
           Result::InvalidFramebuffer);
    assert(indexed==baselineFrame && vram==baselineVram);

    // Indexed-only backend shares the exact same wall source/phase contract.
    assert(drawColumn(indexed,{},Column{0,0,1,0,0,0},selected) ==
           Result::Written);
    assert(indexed[0]==0x42);
}
