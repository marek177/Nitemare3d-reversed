#pragma once

#include "re/N3DV035RngCensus.hpp"

#include <cstdint>

namespace n3d::re::v036 {

// Builds are separate original DOS load images, each independently
// fingerprinted. This is a narrow branch-order contract, NOT an emulated
// incoming-damage formula, whole animation, or actual game execution.
enum class DosBuild : std::uint8_t { V10, V17, V19, V20 };
enum class DamageOutcome : std::uint8_t {
    SkippedProtection, SkippedDeadState, Subtracted, Lethal
};
enum class HitIndicatorDraw : std::uint8_t { None, HitPaletteIndex, Clear };

struct HitInput {
    std::uint8_t hp;
    bool protectionEnabled;
    std::uint16_t gameState;
    std::uint8_t actorClass;
    std::uint8_t calculatedDamage;
    std::int16_t indicatorCountdown{-1};
};

struct HitResult {
    DamageOutcome outcome;
    std::uint8_t hp;
    std::uint16_t gameState;
    std::int16_t indicatorCountdown;
    bool damageProducerWasCalled;
    std::uint8_t directRngCallsInProducer;
    bool indicatorWasWritten;
    bool hudRefreshWasCalled;
};

// Static original evidence:
// DOS v1.0 6798/679F gates before 67B4 damage call;
// DOS v1.7 6912/6919 before 692E;
// DOS v1.9 6A76/6A7D before 6A92;
// DOS v2.0 6A84 producer, then optional 6A93 indicator=3,
// then 6A99/6AA0 gates. In all four, damage>=HP is lethal,
// including HP=0/damage=0, if execution reaches that comparison.
// Only class-specific *direct* RNG within the producer is counted,
// not other callers, indirect RNG, or future render/animation RNG.
constexpr HitResult applyOriginalIncomingHit(DosBuild build,
                                             HitInput input) noexcept {
    HitResult out{DamageOutcome::Subtracted, input.hp, input.gameState,
                  input.indicatorCountdown, false, 0, false, false};
    const auto protectedStop = [&]() noexcept {
        if (input.protectionEnabled) {
            out.outcome = DamageOutcome::SkippedProtection;
            return true;
        }
        if (input.gameState == 2u) {
            out.outcome = DamageOutcome::SkippedDeadState;
            return true;
        }
        return false;
    };

    if (build != DosBuild::V20 && protectedStop()) return out;
    out.damageProducerWasCalled = true;
    out.directRngCallsInProducer =
        v035::damageRngCallsite(input.actorClass).has_value() ? 1u : 0u;

    if (build == DosBuild::V20) {
        if (input.calculatedDamage != 0) {
            out.indicatorCountdown = 3;
            out.indicatorWasWritten = true;
        }
        if (protectedStop()) return out;
    }

    if (input.calculatedDamage >= input.hp) {
        out.hp = 0;
        out.gameState = 2;
        out.outcome = DamageOutcome::Lethal;
    } else {
        out.hp = static_cast<std::uint8_t>(input.hp - input.calculatedDamage);
        out.outcome = DamageOutcome::Subtracted;
    }
    // Original branches converge on the HUD update call even when
    // nonlethal damage is zero. Death SFX/transitions are NOT simulated.
    out.hudRefreshWasCalled = true;
    return out;
}

struct IndicatorStep {
    std::int16_t countdown;
    HitIndicatorDraw draw;
};

// DOS v2.0 only, opcode region A236..A24F. Each invocation with a
// nonnegative countdown decrements it; 3->2->1->0 draw code 4,
// then 0->-1 draws code 3 once. This does NOT establish how
// many times the outer scheduler invokes this per rendered frame.
constexpr IndicatorStep advanceHitIndicator(std::int16_t before) noexcept {
    if (before < 0) return {before, HitIndicatorDraw::None};
    const auto after = static_cast<std::int16_t>(before - 1);
    return {after, after < 0 ? HitIndicatorDraw::Clear
                             : HitIndicatorDraw::HitPaletteIndex};
}

inline constexpr bool kRuntimeOrderVerified = false;
inline constexpr bool kFullCrossVersionDamageParity = false;

} // namespace n3d::re::v036
