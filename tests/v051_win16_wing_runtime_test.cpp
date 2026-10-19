#include "re/N3DV051Win16WingRuntime.hpp"
#include <cassert>
using namespace n3d::re::v051;
int main() {
    static_assert(kBuilds.size() == 5);
    static_assert(allFiveReachE1M1());
    static_assert(!kBuilds[0].localWingDllConflictRemoved);
    static_assert(kBuilds[4].localWingDllConflictRemoved);
    static_assert(!kGameplayInputParityMeasured);
    static_assert(!kTimingParityMeasured);
    static_assert(!kPixelZeroDiffMeasured);
    static_assert(!kAudibleAudioParityMeasured);
    assert(allFiveReachE1M1());
    return 0;
}
