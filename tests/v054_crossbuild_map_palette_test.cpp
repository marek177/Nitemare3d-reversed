#include "re/N3DV054CrossBuildMapPalette.hpp"
#include <cassert>
using namespace n3d::re::v054;

int main() {
    static_assert(kLevelCount * kMarkerKinds == kCrossBuildMarkerCount);
    static_assert(kSameLowByteAsSpawnCount == 112);
    static_assert(kLevelsWithMaxDistanceAtMost2 == 29);
    static_assert(kMaxObservedSpawnChebyshevDistance == 4);
    static_assert(kE1M1SingleMarkerDiffs[0].id == 0x25);
    static_assert(kE1M1SingleMarkerDiffs[3].id == 0x28);
    static_assert(kE1M1SingleMarkerDiffs[2].differingPixels == 8000);
    static_assert(win110PaletteCopyCount(false) == 256);
    static_assert(win110PaletteCopyCount(true) == 236);
    static_assert(kWin110ReservedAtEachEnd == 10);
    static_assert(kDos19To20MainBand.dos20Bytes - kDos19To20MainBand.dos19Bytes == 48);
    static_assert(!kMarkerResourceIdentityFullyClosed);
    static_assert(!kCrossBuildPixelParityClosed);
    assert(kCrossBuildMarkerCount == 124);
    return 0;
}
