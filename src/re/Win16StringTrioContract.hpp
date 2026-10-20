#pragma once

#include <cstdint>

namespace n3d::re::win16::string_trio {

// Pure 16-bit *address planning* for historical Win16 v1.10
// FUN_1000_0CDC / 0CF2 / 0D3E / 0D74. This code never accesses
// the host process's memory. It does not claim that every original
// error path or allocator retry callback is reachable in gameplay.
inline constexpr std::uint16_t kEmptySentinelOffset = 0x0584;
inline constexpr std::uint16_t kOneShotFlagOffset = 0x00A2;
inline constexpr std::uint16_t kMultimediaClockFlagOffset = 0x46B2;

struct TrioState {
    std::uint16_t ptr;
    std::uint16_t used;
    std::uint16_t capacity;
};

constexpr TrioState emptyState() noexcept {
    return TrioState{kEmptySentinelOffset, 0, 0};
}

constexpr bool originalFreeAttempted(std::uint16_t ptr) noexcept {
    // 1000:0CF8: CMP CX,0584h; JE skips free.
    return ptr != kEmptySentinelOffset;
}

struct TeardownPlan {
    TrioState stateAfter;
    bool callsFree;
};

constexpr TeardownPlan planTeardown(TrioState oldState) noexcept {
    return TeardownPlan{emptyState(), originalFreeAttempted(oldState.ptr)};
}

struct AllocationPlan {
    TrioState stateAfter;
    std::uint16_t forwardedRequest;
    std::uint16_t effectiveRequestAfterWrapper;
    std::uint16_t terminatorWriteDsOffset;
    bool callsLocalAlloc;
    bool writesTerminator;
    bool nullResultBeforeWrite;
    bool freesOldPointer;
};

constexpr AllocationPlan planAllocate(
    std::uint16_t requestedUsed, std::uint16_t localAllocResult) noexcept {
    if (requestedUsed == 0) {
        // Original 0D48 branches to 0CDC without freeing previous ptr.
        return AllocationPlan{emptyState(), 0, 0, 0,
                              false, false, false, false};
    }
    // LEA AX,[DI+1] is a 16-bit addition. Wrapper 1008:5AB0
    // replaces zero requested allocation bytes by one byte.
    const auto rawRequest = static_cast<std::uint16_t>(
        static_cast<std::uint32_t>(requestedUsed) + 1u);
    const auto effectiveRequest = static_cast<std::uint16_t>(
        rawRequest == 0 ? 1u : rawRequest);
    const auto terminatedAddress = static_cast<std::uint16_t>(
        static_cast<std::uint32_t>(localAllocResult) + requestedUsed);
    return AllocationPlan{
        TrioState{localAllocResult,requestedUsed,requestedUsed},
        rawRequest,effectiveRequest,terminatedAddress,
        true,true,localAllocResult == 0,false
    };
}

// Under the original OOM branch (returned pointer zero), the
// first terminator write is DS:[requestedUsed]. This is a
// CONDITIONAL alias; this function does not perform the write.
constexpr bool failedAllocationWouldWrite(
    std::uint16_t requestedUsed, std::uint16_t dsByteOffset) noexcept {
    return requestedUsed != 0 && requestedUsed == dsByteOffset;
}

constexpr bool initialEmptyWouldRequestAllocation(
    std::uint16_t requestedUsed) noexcept {
    // Original 1000:0E30 CMP [struct+4],SI; JGE skips realloc.
    // With capacity 0 and a positive *signed* requested length,
    // 0 >= positive is false, so it enters free + allocate.
    return requestedUsed != 0 && requestedUsed < 0x8000;
}

} // namespace n3d::re::win16::string_trio
