#include "N3D_REMAX_StaticPrimitives_12build.hpp"
#include <cassert>
#include <cstdint>
#include <iostream>

int main() {
    using namespace n3d::remax;
    for (unsigned value=0;value<256;++value) {
        const auto cap=hp_hud_handler_cap(static_cast<std::uint8_t>(value));
        assert(cap==(value>100?100:value));
        // Equivalent byte-accurate x86 SUB/SBB/AND/ADD effect at handler entry.
        const bool borrow=(value<100);
        unsigned result=(((value-100U)&0xffU)&(borrow?0xffU:0U));
        result=(result+100U)&0xffU;
        assert(cap==result);
    }
    for (auto build : {DosBuild::V10,DosBuild::V11,DosBuild::V12,DosBuild::V15,
                       DosBuild::V17,DosBuild::V19,DosBuild::V20}) {
        auto p=profile(build);
        assert(p.direct_rng_callsite_count==22);
        assert(p.hud_dispatcher_slot_count==(p.hud_hp_dispatch_index==6?24:23));
        assert(damage_producer_is_called(build,false,false));
        assert(damage_producer_is_called(build,true,false)==(build==DosBuild::V20));
    }
    std::uint32_t s=1;
    for (unsigned n=0;n<100000;++n) {
        const auto r=rng_next(s);
        assert(r.next_state==(std::uint32_t)(s*0x343FDU+0x269EC3U));
        assert(r.result==((r.next_state>>16U)&0x7FFFU));
        s=r.next_state;
    }
    std::cout << "PASS: 256 HP cases, 100000 RNG transitions, 7 DOS profiles\n";
}
