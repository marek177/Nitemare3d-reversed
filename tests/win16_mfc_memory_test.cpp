#include "re/Win16MfcMemory.hpp"

#include <cassert>

int main() {
    using namespace nitemare3d::re::win16;

    static_assert(sizeof(CRuntimeClass16) == 0x10);
    static_assert(sizeof(HandleMap16) == 0x26);

    assert(kCWndObjectSize == 0x1A);
    assert(kRuntimeClasses[0].offset == kCObjectRuntimeClass);
    assert(kRuntimeClasses[1].base == kCCmdTargetRuntimeClass);
    assert(kRuntimeClasses.size() == 31);
    assert(kRuntimeClasses[26].offset == kCSingleDocTemplateRuntimeClass);
    assert(kRuntimeClasses[27].base == kCWndRuntimeClass);
    assert(kRuntimeClasses[28].base == kCViewRuntimeClass);
    assert(kRuntimeClasses[29].base == kCScrollViewRuntimeClass);
    assert(kRuntimeClasses[30].offset == kCWinAppRuntimeClass);
    assert(kCWndSentinels[0].pseudoHwnd == 0);
    assert(kCWndSentinels[1].pseudoHwnd == 1);
    assert(kCWndSentinels[2].pseudoHwnd == -1);
    assert(kCWndSentinels[3].pseudoHwnd == -2);
    assert(kCWndConstructor.segment == 1 && kCWndConstructor.offset == 0x114A);
    assert(kCWndCreateObjectThunk.offset == 0x1AEC);
    assert(kCWndDeletingDestructor.offset == 0x281E);
    assert(kRuntimeCreateObject.offset == 0x06C0);
    assert(kCWndVtableSlots.size() == 20);
    assert(kCWndVtableSlots[0].target.offset == 0x1B0C);
    assert(kCWndVtableSlots[1].target.offset == 0x281E);
    assert(kCWndVtableSlots[2].target.segment == 3);
    assert(kCWndVtableSlots[13].byteOffset == 0x34);
    assert(kCWndVtableSlots[13].target.offset == 0x171C);
    assert(kHandleMaps.size() == 4);
    assert(kHandleMaps[0].runtimeClassOffset == kCWndRuntimeClass);
    assert(kHandleMaps[0].handleFieldOffset == 0x14);
    assert(kHandleMaps[1].handleCount == 2);
    assert(kHandleMaps[2].handleFieldOffset == 0x04);
    assert(kHandleMaps[3].runtimeClassOffset == kCMenuRuntimeClass);
    assert(handleMapBucket(0x1234, 17) == ((0x1234 >> 4) % 17));
    assert(kTemporaryWrapperLifecycle.permanentLookupFirst);
    assert(kTemporaryWrapperLifecycle.temporaryLookupSecond);
    assert(kTemporaryWrapperLifecycle.allocateOnMiss);
    assert(kTemporaryWrapperLifecycle.clearHandleBeforeDelete);
    assert(kTemporaryWrapperLifecycle.cleanupAtNestingZero);
    assert(kCWndLifecycle.constructor.offset == 0x114A);
    assert(kCWndLifecycle.createThunk.offset == 0x1AEC);
    assert(kCWndLifecycle.destroyWindowPath.offset == 0x171C);

    return 0;
}
