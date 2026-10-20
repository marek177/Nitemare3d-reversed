#include "re/Win16StringTrioContract.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::win16::string_trio;

static_assert(kEmptySentinelOffset == 0x0584);
static_assert(kOneShotFlagOffset == 0x00A2);
static_assert(kMultimediaClockFlagOffset == 0x46B2);
static_assert(emptyState().ptr == 0x0584);
static_assert(emptyState().used == 0);
static_assert(emptyState().capacity == 0);
static_assert(!originalFreeAttempted(0x0584));
static_assert(originalFreeAttempted(0));
static_assert(originalFreeAttempted(0x2000));
static_assert(!planTeardown(emptyState()).callsFree);
static_assert(planTeardown(TrioState{0x2000,4,8}).callsFree);

static_assert(!planAllocate(0,0).callsLocalAlloc);
static_assert(planAllocate(0,0).stateAfter.ptr == 0x0584);
static_assert(!planAllocate(0,0).writesTerminator);
static_assert(planAllocate(0x00A2,0).nullResultBeforeWrite);
static_assert(planAllocate(0x00A2,0).terminatorWriteDsOffset == 0x00A2);
static_assert(planAllocate(0x46B2,0).nullResultBeforeWrite);
static_assert(planAllocate(0x46B2,0).terminatorWriteDsOffset == 0x46B2);
static_assert(failedAllocationWouldWrite(0x00A2,kOneShotFlagOffset));
static_assert(failedAllocationWouldWrite(0x46B2,kMultimediaClockFlagOffset));
static_assert(!failedAllocationWouldWrite(0x46B2,kOneShotFlagOffset));
static_assert(!failedAllocationWouldWrite(0,kMultimediaClockFlagOffset));
static_assert(planAllocate(65535,0).forwardedRequest == 0);
static_assert(planAllocate(65535,0).effectiveRequestAfterWrapper == 1);
static_assert(planAllocate(65535,0).terminatorWriteDsOffset == 0xFFFF);
static_assert(planAllocate(0x46B2,0x2000).terminatorWriteDsOffset == 0x66B2);

static_assert(initialEmptyWouldRequestAllocation(1));
static_assert(initialEmptyWouldRequestAllocation(32767));
static_assert(!initialEmptyWouldRequestAllocation(0));
static_assert(!initialEmptyWouldRequestAllocation(32768));
static_assert(!initialEmptyWouldRequestAllocation(65535));
static_assert(planAssignToOriginalEmpty(32768).skipsAllocation);
static_assert(planAssignToOriginalEmpty(32768).wouldCopy);
static_assert(planAssignToOriginalEmpty(32768).selectedDestination == 0x0584);
static_assert(planAssignToOriginalEmpty(32768).wouldTouchClockFlagOnNonFaultingCopy);
static_assert(!planAssignToOriginalEmpty(32768).actualLargeSourceReachabilityProven);
static_assert(!planAssignToOriginalEmpty(32767).skipsAllocation);
static_assert(!planAssignToOriginalEmpty(32767).wouldTouchClockFlagOnNonFaultingCopy);

int main() {
    // Verify all sixteen-bit pointer-index and signed-length branch
    // effects without touching any actual Windows 3.x or host memory.
    for (std::uint32_t n=0; n<=0xFFFFu; ++n) {
        const auto count=static_cast<std::uint16_t>(n);
        const auto p=planAllocate(count,0);
        if (n==0) {
            assert(!p.callsLocalAlloc && !p.writesTerminator);
            assert(p.stateAfter.ptr==kEmptySentinelOffset);
        } else {
            assert(p.callsLocalAlloc && p.writesTerminator);
            assert(p.stateAfter.ptr==0);
            assert(p.stateAfter.used==count);
            assert(p.stateAfter.capacity==count);
            assert(p.terminatorWriteDsOffset==count);
            assert(p.forwardedRequest==static_cast<std::uint16_t>(n+1u));
            assert(p.effectiveRequestAfterWrapper==
                   static_cast<std::uint16_t>(p.forwardedRequest ?
                                              p.forwardedRequest:1u));
        }
        const auto initial=planAssignToOriginalEmpty(count);
        const bool expectSkip=(n==0 || n>=0x8000u);
        assert(initial.skipsAllocation==expectSkip);
        assert(initial.wouldTouchClockFlagOnNonFaultingCopy==
               (n>=0x8000u));
        assert(initial.wouldCopy==(n!=0));
        assert(!initial.actualLargeSourceReachabilityProven);
    }
    return 0;
}
