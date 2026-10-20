#include "game/Dos20GuardSpecialState.hpp"
#include "re/N3DV052Dos20RngTimer.hpp"
#include <cstdlib>
#include <iostream>
namespace g=n3d::dos20::guard;
static void check(bool b){if(!b){std::cerr<<"GUARD special-state contract mismatch\n";std::exit(1);}}
int main(){
    // Source-reported original D02-N pair: same special state, different return.
    g::SpecialState slow{5,4}, fast{0,4};
    g::enterSpecial21(slow);g::enterSpecial21(fast);
    check(slow.state==21 && slow.savedState==5);
    check(fast.state==21 && fast.savedState==4);
    check(g::returnFromSpecial21(slow) && g::returnFromSpecial21(fast));
    check(slow.state==5 && fast.state==4);
    // Unrelated handler return must leave both fields unchanged.
    g::SpecialState unrelated{7,4};
    check(!g::returnFromSpecial21(unrelated));
    check(unrelated.state==7 && unrelated.savedState==4);
    // Nonzero entry is a save/restore round trip. Zero preserves the prior slot.
    for(unsigned state=0;state<256;++state){
        g::SpecialState actor{static_cast<std::uint8_t>(state),0xA5};
        g::enterSpecial21(actor);
        check(g::returnFromSpecial21(actor));
        check(actor.state==(state?state:0xA5));
    }
    // v26's reported Win16 EVENT first draw reuses the existing shared math.
    namespace rng=n3d::re::v052;
    const auto next=rng::nextRngState(1);
    check(next==0x0029E2C0 && rng::rng15(next)==41);
    check(rng::randomCountdown(rng::rng15(next))==201);
    std::cout<<"GUARD21 local return scenarios and EVENT RNG arithmetic PASS\n";
}
