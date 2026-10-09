#pragma once

#include <cstddef>
#include <cstdint>

namespace n3d::re::door20260928 {

inline constexpr std::uint16_t kDoorRuntimeBase = 0x9DD6;
inline constexpr std::size_t kDoorRuntimeStride = 0x16;
inline constexpr std::size_t kDoorRuntimeCapacity = 64;
inline constexpr std::size_t kDoorRuntimeSaveBytes =
    kDoorRuntimeStride * kDoorRuntimeCapacity; // 0x580

inline constexpr std::int16_t kDoorMotionStep = 2;
inline constexpr std::uint16_t kDoorOpenCountdown = 0x20;
inline constexpr std::uint16_t kDoorObstructedRetryCountdown = 4;
inline constexpr std::uint8_t kDoorOpenSfx = 0x25;
inline constexpr std::uint8_t kDoorCloseSfx = 0x26;

enum class DoorControllerState : std::uint16_t {
    Open = 0,
    Closed = 1,
    Opening = 2,
    Closing = 3,
    CorpseHoldOpen = 4,
};

#pragma pack(push, 1)
struct DoorRuntimeRecord {
    std::uint32_t movingWallA;      // +00 Win16 far pointer
    std::uint32_t movingWallB;      // +04 Win16 far pointer
    std::uint32_t mapCell;          // +08 Win16 far pointer to 2-byte MAP cell
    DoorControllerState state;      // +0C
    std::uint16_t autoCloseTimer;   // +0E
    std::int16_t anchorX;           // +10 world-space controller/motion anchor
    std::int16_t anchorY;           // +12 world-space controller/motion anchor
    std::uint8_t soundLatch;        // +14 enables open/close SFX requests
    std::uint8_t unusedPadding;     // +15 no direct Win16 1.10 XREF
};
#pragma pack(pop)

static_assert(sizeof(DoorRuntimeRecord) == kDoorRuntimeStride);
static_assert(offsetof(DoorRuntimeRecord, movingWallA) == 0x00);
static_assert(offsetof(DoorRuntimeRecord, movingWallB) == 0x04);
static_assert(offsetof(DoorRuntimeRecord, mapCell) == 0x08);
static_assert(offsetof(DoorRuntimeRecord, state) == 0x0C);
static_assert(offsetof(DoorRuntimeRecord, autoCloseTimer) == 0x0E);
static_assert(offsetof(DoorRuntimeRecord, anchorX) == 0x10);
static_assert(offsetof(DoorRuntimeRecord, anchorY) == 0x12);
static_assert(offsetof(DoorRuntimeRecord, soundLatch) == 0x14);
static_assert(offsetof(DoorRuntimeRecord, unusedPadding) == 0x15);

constexpr bool allowsPlayerPassage(DoorControllerState state) noexcept {
    return state == DoorControllerState::Open ||
           state == DoorControllerState::CorpseHoldOpen;
}

constexpr bool canManualOrRemoteToggle(DoorControllerState state) noexcept {
    return state != DoorControllerState::CorpseHoldOpen;
}

constexpr bool autoCloseCountdownRuns(DoorControllerState state) noexcept {
    return state == DoorControllerState::Open;
}

} // namespace n3d::re::door20260928
