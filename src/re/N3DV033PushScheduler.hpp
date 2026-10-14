#pragma once

#include <cstddef>
#include <cstdint>

namespace n3d::re::v033 {

// All DOS offsets refer to the fingerprinted v2.0 unpacked MZ load image.
// Win16 offsets refer to logical NE segment 3 of the fingerprinted v1.10 EXE.
// Neither address convention is a modern host pointer.
inline constexpr std::uint16_t kDos20FastEntry = 0xC150;
inline constexpr std::uint16_t kDos20PushStart = 0x0DF8;
inline constexpr std::uint16_t kDos20PushUpdate = 0x0E50;
inline constexpr std::uint16_t kWin16PushStartSeg3 = 0x21B6;
inline constexpr std::uint16_t kWin16PushUpdateSeg3 = 0x2210;
inline constexpr std::size_t kCrossBuildUpdaterBytes = 0x124;
inline constexpr std::size_t kCrossBuildDifferingOperandBytes = 20;
inline constexpr std::uint16_t kPushRecordStride = 6;
inline constexpr std::uint16_t kObjectRecordStride = 28;
inline constexpr std::uint16_t kDos20PushPoolOffset = 0x36B6;
inline constexpr std::uint16_t kWin16PushPoolOffset = 0xA616;
inline constexpr std::uint16_t kDos20MapByteBase = 0x373E;
inline constexpr std::uint16_t kWin16MapByteBase = 0xA69E;
inline constexpr std::uint8_t kPushStartBlockedWallMask = 0x02;
inline constexpr std::uint8_t kPushUpdateBlockedObjectMask = 0x06;
inline constexpr std::uint8_t kPushStartCountdown = 8;
inline constexpr std::uint8_t kPushRemainingField = 4;
inline constexpr std::uint8_t kObjectCellFarPointerField = 0x0C;
inline constexpr std::uint8_t kObjectWorldXField = 0x10;
inline constexpr std::uint8_t kObjectWorldYField = 0x12;

// DOS StartPush at 0DF8 reads the target cell's WALL byte and tests DS
// property table at (wallId - 0x2FF4), before setting the +4 countdown to 8.
// It also rejects an already active push; other caller gates are not modeled.
constexpr bool startPushPassesWallFlag(std::uint8_t wallProperty) noexcept {
    return (wallProperty & kPushStartBlockedWallMask) == 0;
}

// DOS 0E50 / Win16 3:2210: 6-byte records point at 28-byte runtime OBJECTs.
// The destination cell's OBJECT byte indexes a distinct 256-entry property
// table; only bits 1 and 2 block an update when the 32-bit MAP far pointer
// changes. A nonzero destination with neither bit is NOT automatically blocked.
constexpr bool updatePushCanEnter(bool sameFarMapCell,
                                  std::uint8_t destinationObjectProperty) noexcept {
    return sameFarMapCell ||
           (destinationObjectProperty & kPushUpdateBlockedObjectMask) == 0;
}

// Exact x86 16-bit addition of a signed 8-bit step.
constexpr std::uint16_t advanceWorldWord(std::uint16_t oldWord,
                                         std::int8_t delta) noexcept {
    return static_cast<std::uint16_t>(static_cast<std::int32_t>(oldWord) +
                                      static_cast<std::int32_t>(delta));
}

// Mirror the original register sequence:
// CL &= DFh; SAR CX,5; AL &= C0h; AX *= 2; AX += CX; AX += base.
// This matters at 32-unit subdivisions, signed edge values, and word wrap.
// It does NOT certify that positions outside the 64x64 map are reachable.
constexpr std::uint16_t dos20MapByteOffset(std::uint16_t worldX,
                                           std::uint16_t worldY) noexcept {
    const auto maskedX = static_cast<std::uint16_t>(worldX & 0xFFDFu);
    const auto signedX = maskedX < 0x8000u
        ? static_cast<std::int32_t>(maskedX)
        : static_cast<std::int32_t>(maskedX) - 65536;
    const auto xTerm = signedX >= 0 ? signedX / 32
                                      : -(((-signedX) + 31) / 32);
    const auto yTerm = static_cast<std::uint32_t>(worldY & 0xFFC0u) * 2u;
    return static_cast<std::uint16_t>(
        static_cast<std::int32_t>(kDos20MapByteBase) +
        static_cast<std::int32_t>(yTerm) + xTerm);
}

enum class PushDisposition : std::uint8_t {
    Inactive,
    BlockedByObjectProperty,
    AcceptedSameCell,
    AcceptedNewCell
};

struct PushStepInput {
    std::uint16_t worldX;
    std::uint16_t worldY;
    std::int8_t deltaX;
    std::int8_t deltaY;
    std::uint8_t remaining;
    std::uint32_t oldMapFarPointer;
    std::uint32_t candidateMapFarPointer;
    std::uint8_t destinationObjectProperty;
};

struct PushStepPlan {
    PushDisposition disposition;
    std::uint16_t committedWorldX;
    std::uint16_t committedWorldY;
    std::uint16_t candidateDosMapByteOffset;
    std::uint8_t remainingAfter;
    bool transferObjectLayer;
    bool invokeSpatialIndexReorder;
};

// Narrow instruction-exact branch/commit plan, NOT an executable game tick.
// The caller owns the original MAP/VEC pointers, flag table and +0/+2/+3/+4
// PUSH record. Neither the scheduler nor external sorting callbacks are run.
constexpr PushStepPlan planPushUpdate(const PushStepInput& in) noexcept {
    const auto x = advanceWorldWord(in.worldX, in.deltaX);
    const auto y = advanceWorldWord(in.worldY, in.deltaY);
    const auto mapOffset = dos20MapByteOffset(x, y);

    if (in.remaining == 0)
        return {PushDisposition::Inactive, in.worldX, in.worldY,
                mapOffset, 0, false, false};

    const bool changed = in.oldMapFarPointer != in.candidateMapFarPointer;
    if (!updatePushCanEnter(!changed, in.destinationObjectProperty))
        return {PushDisposition::BlockedByObjectProperty,
                in.worldX, in.worldY, mapOffset, in.remaining, false, false};

    return {changed ? PushDisposition::AcceptedNewCell
                    : PushDisposition::AcceptedSameCell,
            x, y, mapOffset,
            static_cast<std::uint8_t>(in.remaining - 1u),
            changed, true};
}

// The original overwrites the target object-layer byte with the source
// object-layer byte and clears the source on an accepted cell transition.
// No unconditional 'destination must be empty' check is present in 0E50.
constexpr void transferAcceptedPushObjectByte(std::uint8_t& source,
                                              std::uint8_t& destination) noexcept {
    destination = source;
    source = 0;
}

// Called from 0E50 after committing x/y and MAP-cell pointer: DOS far target
// 0AEA:015E (load image 0xAFFE). It reorders two sorted OBJECT-pointer lists,
// first X (OBJECT+14, DS:D516) and then Y (OBJECT+16, DS:DA8E).
// The neighbor comparisons use SIGNED 16-bit coordinates and strictly
// positive/negative delta tests, so equality must not swap.
enum class SpatialSwap : std::uint8_t { None, WithNext, WithPrevious };
constexpr SpatialSwap sortedIndexAdjustment(std::int16_t delta,
                                            std::int16_t objectCoord,
                                            std::int16_t neighborCoord,
                                            bool neighborExists) noexcept {
    if (!neighborExists) return SpatialSwap::None;
    if (delta > 0 && neighborCoord < objectCoord) return SpatialSwap::WithNext;
    if (delta < 0 && neighborCoord > objectCoord) return SpatialSwap::WithPrevious;
    return SpatialSwap::None;
}

} // namespace n3d::re::v033
