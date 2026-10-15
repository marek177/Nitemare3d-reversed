#pragma once

// Win16 v1.10/v1.8 evidence-scoped SECRET/VEC reference model (2026-10-15).
// This header uses synthetic structures, NOT the original packed memory ABI.
// No original CPU trace, DOS equivalence, MAP-specific pointer sharing, or
// full game integration is implied. All addresses below are Win16 logical NE
// segment:offset coordinates, NOT live guest CS selectors.

#include <array>
#include <cstddef>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace n3d::re::v035 {

inline constexpr const char* kWin110Sha256 =
    "12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481";
inline constexpr const char* kWin18Sha256 =
    "144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22";
inline constexpr std::size_t kOriginalPanelRecordBytes = 0x16;
inline constexpr std::uint16_t kWin110PanelTickStateGate = 0x2000;
inline constexpr std::uint16_t kWin110CandidateCleanup = 0x2140;
inline constexpr std::uint16_t kWin110MapObjectClear = 0x217D;
inline constexpr std::uint16_t kWin110MapWallClear = 0x2185;
inline constexpr std::uint16_t kWin110PanelStateClear = 0x2189;
inline constexpr std::array<std::size_t, 4> kOriginalMatchSlotOrder = {0, 2, 1, 3};

struct MapCell {
    std::uint8_t wall{};
    std::uint8_t object{};
};

// Identity is the *whole* nonzero original far pointer, not a VEC class/index.
// A shared address occurs in the vector table only once; every panel that
// references it mutates the same coordinate and flag bytes.
struct VecRecord {
    std::uint32_t farPointer{};
    std::uint16_t movingCoordinate{};
    std::uint16_t targetCoordinate{};
    std::uint8_t flags{};
};

struct PanelRecord {
    // Original panel record byte offsets: +0,+4,+8,+C; +10 MAP far pointer;
    // +14 activation state. mapCellIndex is a synthetic host-side mapping.
    std::array<std::uint32_t, 4> vecFarPointers{};
    std::size_t mapCellIndex{};
    std::uint16_t state{1};
};

struct PanelWorld {
    std::vector<MapCell> mapCells;
    std::vector<VecRecord> vectors;
    std::vector<PanelRecord> panels; // preserve original record/scan order
};

constexpr bool sharesAlignedNonNullVec(const PanelRecord& candidate,
                                       const PanelRecord& completed) noexcept {
    // Original compares same slot: +0, +8, +4, +C. Cross-slot matches do NOT
    // satisfy the condition, and NULL cannot match NULL.
    for (const std::size_t k : kOriginalMatchSlotOrder) {
        if (candidate.vecFarPointers[k] != 0 &&
            candidate.vecFarPointers[k] == completed.vecFarPointers[k]) return true;
    }
    return false;
}

inline VecRecord& originalVec(PanelWorld& world, std::uint32_t farPointer) {
    if (!farPointer) throw std::invalid_argument("NULL is not a VEC record");
    for (auto& vec : world.vectors) {
        if (vec.farPointer == farPointer) return vec;
    }
    throw std::out_of_range("Non-NULL panel pointer not found in synthetic VEC pool");
}

// Narrow model of the two *direct* wall-byte writers in EX cleanup
// (Win16 NE4:3CB2 / 3CD2). This does not model all other EX helper effects.
inline void applyExplodableDirectWallClear(MapCell& cell) noexcept {
    cell.wall = 0;
}

inline void tickOnePanel(PanelWorld& world, std::size_t index) {
    PanelRecord& active = world.panels.at(index);
    if (active.state != 2) return;

    active.state = 0;
    // Four VEC updates are in record slot order 0,4,8,C, separately from the
    // completed-panel matching order 0,8,4,C. Increment is u16 +2 without
    // clamping; synthetic odd-target overshoot must not be silently fixed.
    for (std::size_t slot = 0; slot < 4; ++slot) {
        const auto ptr = active.vecFarPointers[slot];
        if (!ptr) continue;
        VecRecord& vec = originalVec(world, ptr);
        if (vec.movingCoordinate < vec.targetCoordinate) {
            vec.movingCoordinate = static_cast<std::uint16_t>(vec.movingCoordinate + 2u);
            active.state = 2;
        }
    }
    if (active.state != 0) return;

    // A completed panel scans EVERY candidate, including itself and panels
    // still in state=1, in original record order. The far-pointer identities
    // remain stable while candidates have their state/cell mutated.
    const PanelRecord completed = active;
    for (PanelRecord& candidate : world.panels) {
        if (!sharesAlignedNonNullVec(candidate, completed)) continue;
        for (const auto ptr : candidate.vecFarPointers) {
            if (ptr) originalVec(world, ptr).flags &= static_cast<std::uint8_t>(~1u);
        }
        MapCell& cell = world.mapCells.at(candidate.mapCellIndex);
        cell.object = 0; // Win16 NE3:217D: OBJECT cleared first
        cell.wall = 0;   // Win16 NE3:2185: WALL cleared next
        candidate.state = 0;
    }
    // If all 4 VEC pointers are NULL, the original scan cannot even match
    // this active panel, so the local path does not clear its MAP cell.
}

inline void tickPanels(PanelWorld& world) {
    for (std::size_t i = 0; i < world.panels.size(); ++i) tickOnePanel(world, i);
}

inline constexpr bool kWin16LocalInstructionSemanticsStaticVerified = true;
inline constexpr bool kE1M9SameSlotVecAliasRuntimeVerified = false;
inline constexpr bool kOriginalCpuTraceCaptured = false;
inline constexpr bool kDosEquivalentAlgorithmVerified = false;
inline constexpr bool kFullGameSecretTimingVerified = false;

} // namespace n3d::re::v035
