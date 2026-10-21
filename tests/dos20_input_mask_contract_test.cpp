#include "re/N3DDos20InputMaskContract.hpp"
#include <cassert>
using namespace n3d::re::dos20_input;
static_assert(Observed==0x039E && Actions==0x0380);
static_assert(V085V086.aligned+V085V086.stale==V085V086.samples);
static_assert(ActionMasks.size()==V085V086.masks);
static_assert(encode({})==0);
static_assert(encode({false,false,false,false,true,true,true})==0x0380);
static_assert(validActionMask(0x0380) && !validActionMask(0x0400));
static_assert(!validActionMask(Up|Fire));
static_assert(actionOnly(Up|Fire|Use)==(Fire|Use));
static_assert(unknown(0x8000|Use)==0x8000);
int main(){
    for(unsigned i=0;i<128;++i){
        Held h{bool(i&1),bool(i&2),bool(i&4),bool(i&8),
               bool(i&16),bool(i&32),bool(i&64)};
        const auto m=encode(h);
        assert(encode(decode(m))==m);
        assert(!(m&std::uint16_t(~Observed)));
        for(unsigned k=0;k<7;++k){
            const auto key=static_cast<Key>(k);
            const auto down=hold(m|0x8000,key,true);
            assert((down&bit(key))!=0 && (down&0x8000)!=0);
            const auto up=hold(down,key,false);
            assert((up&bit(key))==0 && (up&0x8000)!=0);
            assert(hold(down,key,true)==down);
        }
    }
    const auto a=hold(hold(0,Key::Fire,true),Key::Alt,true);
    const auto b=hold(hold(0,Key::Alt,true),Key::Fire,true);
    assert(a==b && a==0x0180);
    assert(hold(a,Key::Use,true)==0x0380);
    assert(hold(0x0380,Key::Alt,false)==0x0280);
    assert(hold(hold(0x0280,Key::Fire,false),Key::Use,false)==0);
    // Opposite directions are both represented; physical resolution is open.
    assert((encode({true,true,true,true})&Movement)==Movement);
}
