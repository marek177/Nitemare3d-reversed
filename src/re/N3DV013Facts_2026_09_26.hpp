#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace nitemare3d::re::v013_20260926 {

// Cross-version evidence added for reconstruction v0.13.
// Keep platform/version-specific layouts separate: the DOS tables below are
// not aliases for the Win16 V1.10 runtime arrays in RuntimeAddresses.hpp.

struct DosFunctionAnchor {
    std::string_view name;
    std::uint16_t offset;
};

inline constexpr std::uint16_t kDosCoreSegment = 0x1000;
inline constexpr std::array<DosFunctionAnchor, 11> kDos20CoreAnchors{{
    {"FindSpecialWallAt", 0x0052},
    {"FindObjectReferenceByTile", 0x00A4},
    {"BuildPairedWallRuntimeTable", 0x0212},
    {"SetAndPropagatePairedWallState", 0x0598},
    {"HandlePlayerUse", 0x0704},
    {"UpdateDoorAutoClose", 0x0A40},
    {"TickPairedWallMotion", 0x0C5F},
    {"ActivateMapObject", 0x0DF8},
    {"TickMovingMapObjects", 0x0E50},
    {"PrimaryWallClassLookup", 0x0F74},
    {"SecondaryWallClassLookup", 0x0FBE},
}};

inline constexpr std::uint16_t kDosGuardClassToRuntimeType = 0x0FF4;

// DOS v1.8/v2.0 runtime-table capacities/layouts recovered from map scanners.
// These differ from some Win16 V1.10 records, so they intentionally carry a
// DOS prefix rather than replacing the existing Win16 constants.
inline constexpr std::size_t kDosDoorRecordSize = 0x12;
inline constexpr std::size_t kDosDoorCapacity = 0x40;
inline constexpr std::size_t kDosPanelRecordSize = 0x0E;
inline constexpr std::size_t kDosPanelCapacity = 0x20;
inline constexpr std::size_t kDosPushRecordSize = 0x06;
inline constexpr std::size_t kDosPushCapacity = 12;
inline constexpr std::size_t kDosObjectRecordSize = 0x1C;
inline constexpr std::size_t kDosGuardRecordSize = 0x1A;
inline constexpr int kMapWidth = 64;
inline constexpr int kMapHeight = 64;

// Win16 v1.8 player-facing tables used by interaction/push logic.
inline constexpr std::array<std::int16_t, 8> kFrontCellDelta{{
    -64, 1, 1, 64, 64, -1, -1, -64
}};
inline constexpr std::array<std::int8_t, 8> kPushDx{{
    0, 8, 8, 0, 0, -8, -8, 0
}};
inline constexpr std::array<std::int8_t, 8> kPushDy{{
    -8, 0, 0, 8, 8, 0, 0, -8
}};

constexpr std::int16_t frontCellDelta(std::uint8_t octant) noexcept {
    return kFrontCellDelta[static_cast<std::size_t>(octant & 7u)];
}

constexpr int pushDistanceUnits() noexcept {
    return 8 * 8;
}

static_assert(kDosObjectRecordSize == 28);
static_assert(kDosGuardRecordSize == 26);
static_assert(pushDistanceUnits() == 64);

} // namespace nitemare3d::re::v013_20260926
