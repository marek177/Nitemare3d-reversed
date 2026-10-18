#include "re/N3DDos20SpriteRaster.hpp"
#include "re/N3DV041FrameCompositor.hpp"
#include <array>
#include <cassert>
#include <vector>
using namespace n3d::re::dos20::sprite;
int main() {
    // The high-bit witnesses distinguish unsigned JA from signed JG.
    static_assert(columnVisible(0x7FFF, 0x8000, 0));
    static_assert(!columnVisible(0x8000, 0x7FFF, 0));
    static_assert(columnVisible(42, 42, 0));
    static_assert(columnVisible(65535, 0, 0x10));
    static_assert(!columnVisible(65535, 0, 0x08));
    for (unsigned t=0; t<256; ++t) assert(writesTexel(t) == (t != 31));
    constexpr auto clip = setupVertical(0xFFFE, 5, 8, 0, 3);
    static_assert(clip && clip->firstY == 0 && clip->count == 4);
    static_assert(clip->step16_16 == 65536 && clip->sourceAdvance == 2 && clip->fraction == 0);
    constexpr auto fractional = setupVertical(0xFFFF, 4, 4, 0, 199);
    static_assert(fractional && fractional->step16_16 == 43690);
    static_assert(fractional->sourceAdvance == 0 && fractional->fraction == 43690);
    static_assert(!setupVertical(0, 65535, 64, 0, 199));
    constexpr auto c = advance({65535, 65535}, 0x00018000);
    static_assert(c.offset == 1 && c.fraction == 32767);
    static_assert(address(319,199).offset == 15999);
    static_assert(address(319,199).sequencerValue == 0x88);
    static_assert(address(0,256).offset == 0); // literal AL multiply, not a host clamp
    // Independent planar decode back to x/y checks all four planes and row edges.
    for (unsigned y=0; y<200; ++y) for (unsigned x=0; x<320; ++x) {
        auto a=address(x,y);
        assert(a.offset/80 == y && (a.offset%80)*4 + (x%4) == x);
        assert((a.sequencerValue & 15) == (1U << (x%4)));
    }
    // Synthetic overlap integrates the existing slot walk with the sampled sink.
    // Transparent later sprite preserves earlier output; sprites never write wall depth.
    using namespace n3d::re::v041::compositor;
    SpritePool pool{}; initializeSpriteFlags(pool);
    markProjected(pool[2]); markProjected(pool[99]);
    std::array<std::uint8_t,3> pixels{7,7,7};
    const std::array<std::uint16_t,3> wall{4,5,6};
    std::vector<unsigned> order;
    auto r=compositeSpriteSlots(DosBuild::V20,pool,[](auto){return false;},
        [](auto){assert(false);return false;},[&](const SpriteSlot& s){
            const auto i=unsigned(&s-pool.data()); order.push_back(i);
            for (unsigned x=0;x<3;++x) {
                const std::uint8_t t=i==2 ? 9 : (x==1 ? 0x1F : 12);
                emitSample(wall[x],5,0,t,[&](auto value){pixels[x]=value;});
            }
        });
    assert(r.completed && (order==std::vector<unsigned>{2,99}));
    assert((pixels==std::array<std::uint8_t,3>{12,9,7}));
    assert((wall==std::array<std::uint16_t,3>{4,5,6}));
}
