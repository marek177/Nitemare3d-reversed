#include "re/N3DV062Dos20PaletteFade.hpp"
using namespace n3d::re::v062;
int main(){
 static_assert(kComponents==768);
 static_assert(kPasses==21);
 static_assert(kWrites==21u*768u);
 static_assert(kAdjacentChecks==20u*768u);
 static_assert(kFinalCounts[0]+kFinalCounts[1]+kFinalCounts[2]==768);
 static_assert(kFinalFnv64==0x78F3DAEBC5DDA37Dull);
 static_assert(run21(61)==1 && run21(62)==2);
 static_assert(kCallerObserved);
 static_assert(!kExactTimingClosed);
 static_assert(!kFramebufferZeroDiffClosed);
 return 0;
}
