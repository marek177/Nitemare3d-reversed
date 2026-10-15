#include "re/N3DV036ProtectedHitOrdering.hpp"

#include <array>
#include <cassert>
#include <initializer_list>

using namespace n3d::re::v036;

int main() {
    constexpr HitInput shielded{100, true, 0, 0x08, 7, -1};
    constexpr auto old10 = applyOriginalIncomingHit(DosBuild::V10, shielded);
    constexpr auto old17 = applyOriginalIncomingHit(DosBuild::V17, shielded);
    constexpr auto old19 = applyOriginalIncomingHit(DosBuild::V19, shielded);
    constexpr auto new20 = applyOriginalIncomingHit(DosBuild::V20, shielded);
    static_assert(old10.outcome == DamageOutcome::SkippedProtection);
    static_assert(old17.outcome == DamageOutcome::SkippedProtection);
    static_assert(old19.outcome == DamageOutcome::SkippedProtection);
    static_assert(!old10.damageProducerWasCalled);
    static_assert(!old17.damageProducerWasCalled);
    static_assert(!old19.damageProducerWasCalled);
    static_assert(old10.directRngCallsInProducer == 0);
    static_assert(old17.directRngCallsInProducer == 0);
    static_assert(old19.directRngCallsInProducer == 0);
    static_assert(new20.outcome == DamageOutcome::SkippedProtection);
    static_assert(new20.damageProducerWasCalled);
    static_assert(new20.directRngCallsInProducer == 1);
    static_assert(new20.indicatorWasWritten);
    static_assert(new20.indicatorCountdown == 3);
    static_assert(new20.hp == 100);
    static_assert(!new20.hudRefreshWasCalled);

    // State 2 check moves after producer in v2.0, independently of protection.
    constexpr HitInput terminal{0, false, 2, 0x09, 12, -1};
    static_assert(!applyOriginalIncomingHit(DosBuild::V19, terminal)
                       .damageProducerWasCalled);
    constexpr auto terminal20 = applyOriginalIncomingHit(DosBuild::V20, terminal);
    static_assert(terminal20.outcome == DamageOutcome::SkippedDeadState);
    static_assert(terminal20.damageProducerWasCalled);
    static_assert(terminal20.directRngCallsInProducer == 1);
    static_assert(terminal20.indicatorCountdown == 3);
    static_assert(terminal20.gameState == 2);
    static_assert(!terminal20.hudRefreshWasCalled);

    // A zero-damage random draw still happens first in v2.0, but no flash.
    constexpr HitInput zeroProtected{100, true, 0, 0x08, 0, -1};
    constexpr auto zero20 = applyOriginalIncomingHit(DosBuild::V20, zeroProtected);
    static_assert(zero20.damageProducerWasCalled);
    static_assert(zero20.directRngCallsInProducer == 1);
    static_assert(!zero20.indicatorWasWritten);
    static_assert(zero20.indicatorCountdown == -1);
    static_assert(zero20.outcome == DamageOutcome::SkippedProtection);

    // The lethal unsigned compare is >=, not >. HP=0, damage=0 is lethal
    // if a debug/rare state reaches the comparison with game state !=2.
    constexpr HitInput rareZero{0, false, 0, 0x08, 0, -1};
    for (const auto build : {DosBuild::V10, DosBuild::V17,
                             DosBuild::V19, DosBuild::V20}) {
        const auto result = applyOriginalIncomingHit(build, rareZero);
        assert(result.outcome == DamageOutcome::Lethal);
        assert(result.hp == 0);
        assert(result.gameState == 2);
        assert(result.hudRefreshWasCalled);
    }
    static_assert(applyOriginalIncomingHit(DosBuild::V20, rareZero)
                      .outcome == DamageOutcome::Lethal);

    constexpr HitInput nullHit{100, false, 0, 0x19, 0, -1};
    constexpr auto harmless = applyOriginalIncomingHit(DosBuild::V20, nullHit);
    static_assert(harmless.outcome == DamageOutcome::Subtracted);
    static_assert(harmless.hp == 100);
    static_assert(harmless.hudRefreshWasCalled);
    static_assert(!harmless.indicatorWasWritten);
    static_assert(harmless.directRngCallsInProducer == 0);
    constexpr auto ordinary = applyOriginalIncomingHit(
        DosBuild::V20, HitInput{100, false, 0, 0x09, 15, -1});
    static_assert(ordinary.outcome == DamageOutcome::Subtracted);
    static_assert(ordinary.hp == 85);
    static_assert(ordinary.indicatorCountdown == 3);
    static_assert(ordinary.directRngCallsInProducer == 1);
    constexpr auto oldOrdinary = applyOriginalIncomingHit(
        DosBuild::V19, HitInput{100, false, 0, 0x09, 15, -1});
    static_assert(oldOrdinary.hp == 85);
    static_assert(!oldOrdinary.indicatorWasWritten);

    // Indicator is a four-invocation sequence, not "three frames".
    static_assert(advanceHitIndicator(-1).draw == HitIndicatorDraw::None);
    static_assert(advanceHitIndicator(3).countdown == 2);
    static_assert(advanceHitIndicator(3).draw == HitIndicatorDraw::HitPaletteIndex);
    static_assert(advanceHitIndicator(0).countdown == -1);
    static_assert(advanceHitIndicator(0).draw == HitIndicatorDraw::Clear);
    std::int16_t countdown = 3;
    constexpr std::array<HitIndicatorDraw, 5> expected{{
        HitIndicatorDraw::HitPaletteIndex,
        HitIndicatorDraw::HitPaletteIndex,
        HitIndicatorDraw::HitPaletteIndex,
        HitIndicatorDraw::Clear,
        HitIndicatorDraw::None
    }};
    for (const auto draw : expected) {
        const auto step = advanceHitIndicator(countdown);
        assert(step.draw == draw);
        countdown = step.countdown;
    }
    assert(countdown == -1);
    static_assert(!kRuntimeOrderVerified);
    static_assert(!kFullCrossVersionDamageParity);
}
