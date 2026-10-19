#include "re/N3DV059Win16SaveLoad.hpp"
using namespace n3d::re::v059;
int main() {
    static_assert(kWin110E1M1SaveLoad.saveSizeBytes == 55015);
    static_assert(kWin110E1M1SaveLoad.changedBytesAfterMovement == 477);
    static_assert(kWin110E1M1SaveLoad.exactPixelBasisPoints == 9837);
    static_assert(kWin110E1M1SaveLoad.restoredVsSavedMeanMilli == 940);
    static_assert(kWin110E1M1SaveLoad.restoredVsStartMeanMilli == 55610);
    static_assert(kWin110E1M1SaveLoad.e1m1Reached);
    static_assert(kWin110E1M1SaveLoad.saveWritten);
    static_assert(kWin110E1M1SaveLoad.loadRestoredMovedView);
    static_assert(!kExactPlayerFieldOffsetsClosed);
    static_assert(!kFirstPostLoadCpuFrameClosed);
    static_assert(!kWin16RngRestoreClosed);
    return 0;
}
