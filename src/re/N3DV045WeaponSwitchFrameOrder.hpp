#pragma once

#include <cstdint>

namespace n3d::re::v045 {

enum class HudPhase : std::uint8_t {
    Idle = 0,
    Raise = 1,
    Lower = 2,
};

struct WeaponSwitchState {
    std::uint8_t current{0xFF};
    std::uint8_t pending{0xFF};
    std::uint8_t fireMode{};   // 1 hitscan, 2 projectile
    HudPhase phase{HudPhase::Idle};
    std::uint16_t hudPos{};
    std::uint8_t cadenceCounter{};
};

constexpr std::uint8_t fireModeFor(std::uint8_t weapon) noexcept {
    return weapon == 2 ? 1 : 2;
}

// Bounded request contract from DOS v1.2/v2.0 switch routine:
// - no current weapon: install immediately and enter Raise
// - different active weapon: update pending; only Idle begins Lower
// - request equal to current: no local transition
constexpr WeaponSwitchState requestWeapon(
    WeaponSwitchState s,
    std::uint8_t requested) noexcept {
    if (s.current == 0xFF) {
        s.current = requested;
        s.fireMode = fireModeFor(requested);
        s.phase = HudPhase::Raise;
        return s;
    }

    if (requested != s.current) {
        s.pending = requested;
        if (s.phase == HudPhase::Idle) {
            s.phase = HudPhase::Lower;
        }
    }
    return s;
}

// Exact commit slice once the Lower path reaches position zero.
constexpr WeaponSwitchState commitPendingAtLowerZero(
    WeaponSwitchState s) noexcept {
    s.current = s.pending;
    s.fireMode = fireModeFor(s.current);
    s.phase = HudPhase::Raise;
    return s;
}

// Bounded phase-1 model: raise by one 16-bit unit; at/after supplied limit,
// transition to Idle. The dynamic limit is caller/data supplied.
constexpr WeaponSwitchState raiseOne(
    WeaponSwitchState s,
    std::uint16_t limit) noexcept {
    if (s.phase != HudPhase::Raise) return s;
    s.hudPos = static_cast<std::uint16_t>(s.hudPos + 1u);
    if (s.hudPos >= limit) s.phase = HudPhase::Idle;
    return s;
}

// Bounded phase-2 model: decrement one 16-bit unit when nonzero.
// If the resulting position is zero, commit pending immediately.
constexpr WeaponSwitchState lowerOne(
    WeaponSwitchState s) noexcept {
    if (s.phase != HudPhase::Lower) return s;
    if (s.hudPos != 0) {
        s.hudPos = static_cast<std::uint16_t>(s.hudPos - 1u);
    }
    if (s.hudPos == 0) {
        s = commitPendingAtLowerZero(s);
    }
    return s;
}

enum class DirectFrameStage : std::uint8_t {
    WeaponHudUpdate,
    ProjectilePoolUpdate,
    Present,
    GameplayInput,
};

// Checked DOS main-frame order, reduced to the weapon/projectile-relevant stages.
constexpr bool stageBefore(DirectFrameStage a, DirectFrameStage b) noexcept {
    return static_cast<unsigned>(a) < static_cast<unsigned>(b);
}

// Within the checked active-input function, numeric weapon selection request
// occurs before the later FIRE cadence/dispatcher block.
inline constexpr bool kWeaponRequestBeforeFireInSameInputCall = true;

// A request for a different already-active weapon only updates pending/phase.
// Therefore the later FIRE block in the SAME input call still reads old current.
constexpr std::uint8_t sameInputWeaponSeenByFire(
    std::uint8_t currentBefore,
    std::uint8_t requested) noexcept {
    if (currentBefore == 0xFF) return requested; // direct-equip case
    return currentBefore;                       // pending-switch case
}

// The direct parent frame runs projectile update before gameplay input.
// A projectile spawned by FIRE in that input therefore cannot be visited by
// that already-completed direct parent projectile pass.
inline constexpr bool kNewProjectileMovesInSameDirectParentFrame = false;

// If HUD Lower commits weapon 3 before the frame's input stage, held FIRE may
// be accepted later in that SAME frame once cadenceCounter >= threshold 1.
// No fresh-edge requirement applies to weapon 3.
constexpr bool weapon3CanFireOnCommitFrame(
    bool fireHeld,
    std::uint8_t cadenceCounter) noexcept {
    return fireHeld && cadenceCounter >= 1;
}

// Request/commit code does not itself reset cadence counter; it is carried
// across switching unless another slow-tick/FIRE path changes it.
constexpr bool switchPreservesCadenceCounter(
    WeaponSwitchState before,
    WeaponSwitchState after) noexcept {
    return before.cadenceCounter == after.cadenceCounter;
}

} // namespace n3d::re::v045
