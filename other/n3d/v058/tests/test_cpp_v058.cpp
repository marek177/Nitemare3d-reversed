#include "../src/N3DV058GuardDeathContract.hpp"
#include <array>
#include <cassert>
#include <cstdint>
using namespace n3d::v058;
static_assert(scoreFor(0x15)==-1000,"signed fatal score table");
static_assert(scoreFor(0x20)==50,"0x20 included in 25-way score dispatcher");
static_assert(scoreFor(0x21)==0,"class beyond 0x20 defaults 0");
static_assert(addSignedScore32(500,0x15)==0xfffffe0cU,"signed 32-bit add");
static_assert(addSignedScore32(0xfffffffeU,0x20)==48,"score overflow wraps");
static_assert(fatalEventFor(0x20).base==0,"class20 sound defaults zero");
static_assert(state7EventFor(0x10).kind==SoundKind::RngModulo2,"state7 random2 selector");
int main() {
  RngState r{1,0};
  assert(nextRng(r)==41);
  assert(nextRng(r)==18467);
  assert(r.draws==2);
  assert(applyEvent(fatalEventFor(0x0F),41)==13);
  assert(applyEvent(state7EventFor(0x09),41)==58);
  auto noop=[]()->std::uint16_t{assert(false&&"fast variant should not draw");return 0;};
  auto fast=chooseVariant(0,1,std::array<std::uint8_t,7>{0,0,0,0,0,0,0},noop);
  assert(fast.resolved&&fast.selection==7&&fast.draws==0);
  RngState q{1,0};
  auto nonfatal=chooseVariant(8,1,std::array<std::uint8_t,7>{1,1,1,1,1,1,1},[&](){return nextRng(q);});
  assert(nonfatal.resolved&&nonfatal.draws>=1&&q.draws==nonfatal.draws);
  auto noSlots=chooseVariant(8,0,std::array<std::uint8_t,7>{0,0,0,0,0,0,0},[&](){return nextRng(q);},7);
  assert(!noSlots.resolved&&noSlots.draws==7);
  for(unsigned cls=0;cls<256;++cls){
    const auto expect=cls>=8&&cls<=0x20?kScores[cls-8]:0;
    assert(scoreFor(static_cast<std::uint8_t>(cls))==expect);
  }
}
