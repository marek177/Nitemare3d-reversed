#pragma once

#include <array>
#include <cstdint>

namespace n3d::re::v039 {

struct Class19DamageResult {
    std::int16_t damage{};
    std::uint8_t rngDraws{};
};

// Audited class 0x19/Cannon branch: one shared RNG draw occurs before
// class dispatch, then the class-specific path overwrites damage with zero.
constexpr Class19DamageResult class19WeaponDamage() noexcept {
    return {0, 1};
}

constexpr bool class19PositiveHpReturnsBeforePainDeath(std::uint8_t hp) noexcept {
    return hp > 0;
}

// Standard nonlethal receiver writes GUARD+0x12 = 8 before its direct pain
// selector calls. The selector's fast variant-7 shortcut requires +0x12 == 0.
constexpr bool standardNonlethalPainFast7Eligible() noexcept {
    return false;
}

struct E2M10Property40Collision {
    std::uint8_t scriptReturn{};
    bool collisionAccepted{};
    bool ddaBudgetReread{};
    bool impact{};
};

// For the audited property-0x40 E2M10 normal-return path across 12 builds:
// script -> AL=1, collision accepts, DDA branches to IMPACT and does not
// execute the AL==0 budget-reread continuation.
constexpr E2M10Property40Collision e2m10Property40Collision() noexcept {
    return {1, true, false, true};
}

enum class RadioAction : std::uint8_t {
    None,
    Move,
    GlobalStop,
};

struct RadioState14Tick {
    std::uint16_t timer{};
    RadioAction action{RadioAction::None};
};

// Local state-0x14 timing model: timer<=0 invokes global radio stop.
// Otherwise timer decrements once. Movement begins only once the post-
// decrement timer is below 0x60. Starting at 0x70 this yields 16 no-move
// updates, then 96 movement updates, and global stop on update 113.
constexpr RadioState14Tick radioState14Tick(std::uint16_t timerBefore) noexcept {
    if (timerBefore == 0) {
        return {0, RadioAction::GlobalStop};
    }
    const auto after = static_cast<std::uint16_t>(timerBefore - 1u);
    return {after, after < 0x60u ? RadioAction::Move : RadioAction::None};
}

struct RadioRestoredGuard {
    std::uint8_t strategy{};
    std::uint8_t state{};
    std::uint16_t timer{};
};

// Bounded common restore fields for records still in state 0x14.
constexpr RadioRestoredGuard radioStopRestoreState14() noexcept {
    return {0, 6, 1};
}

struct FireCadenceDecision {
    bool validWeaponIndex{};
    bool accepted{};
    std::uint8_t nextTimer{};
};

inline constexpr std::array<std::uint8_t, 4> kFireCadenceThresholds{2, 1, 3, 1};

// Mode-0 input branch for valid weapon indices 0..3. Weapons 0..2 require
// a fresh press edge; weapon 3 accepts held FIRE once the threshold is met.
// On acceptance the timer resets before the downstream weapon dispatcher.
constexpr FireCadenceDecision fireCadenceInput(
    std::uint8_t timer,
    std::uint8_t weapon,
    bool pressEdge) noexcept {
    if (weapon >= kFireCadenceThresholds.size()) {
        return {false, false, timer};
    }
    if (timer < kFireCadenceThresholds[weapon]) {
        return {true, false, timer};
    }
    const bool accepted = weapon == 3 ? true : pressEdge;
    return {true, accepted, static_cast<std::uint8_t>(accepted ? 0 : timer)};
}

// Mode-1 FAST branch: saturating increment.
constexpr std::uint8_t fireCadenceFastTick(std::uint8_t timer) noexcept {
    return timer == 0xFFu ? 0xFFu : static_cast<std::uint8_t>(timer + 1u);
}

enum class CachedClockSource : std::uint8_t {
    RtcCache,
    Backend,
};

enum class BackendClockSource : std::uint8_t {
    BiosBdaTicksTimes55,
    SystemDateTime,
};

// DS:3CCF != 0: BE74 reads the IRQ-updated RTC cache.
// DS:3CCF == 0: BE74 calls the backend and refreshes the cache.
constexpr CachedClockSource cachedClockSource(bool rtcTimingEnabled) noexcept {
    return rtcTimingEnabled ? CachedClockSource::RtcCache
                            : CachedClockSource::Backend;
}

// In BDF8, BIOS BDA ticks are selected only when DS:3CC7==0 and
// DS:3CCF!=0. Other combinations use the system date/time path.
constexpr BackendClockSource backendClockSource(
    bool flag3cc7,
    bool flag3ccf) noexcept {
    return (!flag3cc7 && flag3ccf)
        ? BackendClockSource::BiosBdaTicksTimes55
        : BackendClockSource::SystemDateTime;
}

struct BiosClockResult {
    std::uint32_t value{};
    std::uint32_t origin{};
};

constexpr BiosClockResult biosClock55(
    std::uint32_t bdaTick,
    std::uint32_t origin) noexcept {
    if (origin == 0) {
        origin = bdaTick;
    }
    return {
        static_cast<std::uint32_t>(
            static_cast<std::uint32_t>(bdaTick - origin) * 55u),
        origin
    };
}

// Original angle normalizer applies at most one +360 and at most one -360,
// not a true modulo loop.
constexpr std::int32_t normalizeAngleOneTurn(std::int16_t input) noexcept {
    std::int32_t a = input;
    if (a < 0) {
        a += 360;
    }
    if (a >= 360) {
        a -= 360;
    }
    return a;
}

constexpr bool angleNormalizesToRetailRange(std::int16_t input) noexcept {
    const auto a = normalizeAngleOneTurn(input);
    return a >= 0 && a <= 359;
}

// Exact input interval that the audited one-turn normalizer maps into 0..359.
constexpr bool angleInputIsStaticallySafe(std::int16_t input) noexcept {
    return input >= -360 && input <= 719;
}

} // namespace n3d::re::v039
