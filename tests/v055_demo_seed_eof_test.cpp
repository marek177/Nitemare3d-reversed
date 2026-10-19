#include "re/N3DV055DemoSeedEofStatic.hpp"
#include <cassert>
using namespace n3d::re::v055;
int main() {
    static_assert(kDemo1RecordCount == 275);
    static_assert(kDemo1First.key == 0x48E0);
    static_assert(kDemo1First.input == 2);
    static_assert(kDemo1First.counter == 8);
    static_assert(kDemo1Last.key == 0x74E0);
    static_assert(kDemo1Last.input == 0x0090);
    static_assert(kDemo1Last.counter == 1074);
    static_assert(kEqualAdjacentCounterPairs == 4);
    static_assert(kSeedHelperCallImageOffset > kRecordApplyImageOffset);
    static_assert(!kSeedHelperIsRandomDrawHelper);
    static_assert(!kCallerChecksReadCountAt6E07);
    static_assert(!kEofBehaviorClosed);
    static_assert(!kSeedToFirstDrawContinuousTraceClosed);
    assert(kDemoModeDispatcherImageOffset == 0x6D04);
    return 0;
}
