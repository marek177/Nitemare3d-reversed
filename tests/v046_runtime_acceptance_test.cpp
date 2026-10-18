#include "re/N3DV046RuntimeAcceptance.hpp"
#include <cassert>
using namespace n3d::re::v046;
int main(){
 static_assert(directProjectileBeforeInput());
 static_assert(kDos20SameSchedulerStages[0].imageOffset==0xC24B);
 static_assert(kDos20SameSchedulerStages[1].imageOffset==0xC250);
 static_assert(kDos20SameSchedulerStages[2].imageOffset==0xC26F);
 static_assert(kDos20SameSchedulerStages[3].imageOffset==0xC274);
 constexpr auto odd=doubleBlockedBounce({8,-8},41);
 constexpr auto even=doubleBlockedBounce({8,-8},11478);
 static_assert(odd.vx==-8 && odd.vy==-8);
 static_assert(even.vx==8 && even.vy==8);
 static_assert(state06AfterTimerDecrement(8)==0x06);
 static_assert(state06AfterTimerDecrement(1)==0x03);
 static_assert(kFrankensteinState05.timerAfter==8 && kFrankensteinState05.xAfter==2776);
 static_assert(kMummyState05.timerAfter==8 && kMummyState05.xAfter==2720);
 static_assert(kFrankensteinAttack.damage==14 && kFrankensteinAttack.hpBefore-kFrankensteinAttack.hpAfter==14);
 static_assert(kMummyAttack.damage==4 && kMummyAttack.hpBefore-kMummyAttack.hpAfter==4);
 assert(kDos12Dos20All4Witness[2].active==2 && kDos12Dos20All4Witness[2].mode==1);
 assert(kDos12Dos20All4Witness[3].active==3 && kDos12Dos20All4Witness[4].plasma==37);
 assert(kDos12Dos20All4Witness[5].active==0 && kDos12Dos20All4Witness[5].plasma==37);
 static_assert(kNoXmsManagerIsNonFatalInObservedBuild);
 static_assert(!kActiveDspDmaStopObserved);
 static_assert(kPaletteRngWitness.seedAfter==0x0029E2C0u && kPaletteRngWitness.timer==201);
 return 0;
}
