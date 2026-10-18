#pragma once
#include "re/N3DV039LateStaticClosures.hpp"
#include "re/N3DV041LatestStaticEvidence.hpp"
#include <cstdint>
#include <optional>

namespace n3d::re::e1m9 {
// Bounded Win16 contracts; sources and missing edges: docs/E1M9_STATIC_LIFECYCLE.md.
// Do not call these helpers a full AE56 implementation or accepted-hit solver.
constexpr std::optional<std::uint8_t> danceDescriptorWordOffset(
    std::uint8_t originalClass) noexcept {
    switch (originalClass) {
    case 0x09: return 0x04;
    case 0x0B: return 0x24;
    case 0x0C: return 0x14;
    default: return std::nullopt; // no claim about the original default branch
    }
}

// +0C is overloaded: saved OBJECT group during radio, nextstate elsewhere.
struct RadioRestoreFields {
    std::uint8_t objectGroup; // OBJECT+04
    std::uint8_t savedGroupOrNextState; // GUARD+0C
    std::uint8_t strategy; // GUARD+0A
    std::uint8_t state; // GUARD+0B
    std::uint16_t timer; // GUARD+06
};

// AE56(1) state filter is essential. A modified +0C alone cannot make a
// non-state14 record participate. Other restore effects are outside this slice.
constexpr bool restoreRadioFields(RadioRestoreFields& fields) noexcept {
    if (fields.state != 0x14) return false;
    fields.objectGroup = fields.savedGroupOrNextState;
    const auto reset = v039::radioStopRestoreState14();
    fields.strategy = reset.strategy;
    fields.state = reset.state;
    fields.timer = reset.timer;
    return true;
}

// Local map write does not provide a projectile acceptance decision.
// v1.0 deliberately has no wrapper here: its activation differs.
constexpr v041::MapCell mode0MapWriteWin13To110(v041::MapCell cell) noexcept {
    return v041::clearRadioWallOnly(cell);
}
} // namespace n3d::re::e1m9
