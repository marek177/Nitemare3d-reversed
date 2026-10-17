#include "re/N3DV039LateStaticClosures.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::v039;

int main() {
    {
        const auto c = class19WeaponDamage();
        assert(c.damage == 0);
        assert(c.rngDraws == 1);
        assert(class19PositiveHpReturnsBeforePainDeath(255));
        assert(!class19PositiveHpReturnsBeforePainDeath(0));
        assert(!standardNonlethalPainFast7Eligible());
    }

    {
        const auto e = e2m10Property40Collision();
        assert(e.scriptReturn == 1);
        assert(e.collisionAccepted);
        assert(!e.ddaBudgetReread);
        assert(e.impact);
    }

    {
        auto t = radioState14Tick(0x70);
        assert(t.timer == 0x6F && t.action == RadioAction::None);
        for (int i = 1; i < 16; ++i) {
            t = radioState14Tick(t.timer);
        }
        assert(t.timer == 0x60 && t.action == RadioAction::None);
        t = radioState14Tick(t.timer);
        assert(t.timer == 0x5F && t.action == RadioAction::Move);
        auto stop = radioState14Tick(0);
        assert(stop.action == RadioAction::GlobalStop);
        const auto restored = radioStopRestoreState14();
        assert(restored.strategy == 0 && restored.state == 6 && restored.timer == 1);
    }

    {
        auto d = fireCadenceInput(1, 0, true);
        assert(d.validWeaponIndex && !d.accepted && d.nextTimer == 1);
        d = fireCadenceInput(2, 0, true);
        assert(d.accepted && d.nextTimer == 0);
        d = fireCadenceInput(2, 0, false);
        assert(!d.accepted && d.nextTimer == 2);
        d = fireCadenceInput(1, 3, false);
        assert(d.accepted && d.nextTimer == 0);
        d = fireCadenceInput(10, 0xFF, true);
        assert(!d.validWeaponIndex && !d.accepted && d.nextTimer == 10);
        assert(fireCadenceFastTick(0) == 1);
        assert(fireCadenceFastTick(0xFE) == 0xFF);
        assert(fireCadenceFastTick(0xFF) == 0xFF);
    }

    {
        assert(cachedClockSource(true) == CachedClockSource::RtcCache);
        assert(cachedClockSource(false) == CachedClockSource::Backend);
        assert(backendClockSource(false, true) == BackendClockSource::BiosBdaTicksTimes55);
        assert(backendClockSource(true, true) == BackendClockSource::SystemDateTime);
        assert(backendClockSource(false, false) == BackendClockSource::SystemDateTime);
        auto b = biosClock55(1000, 0);
        assert(b.value == 0 && b.origin == 1000);
        b = biosClock55(1010, b.origin);
        assert(b.value == 550 && b.origin == 1000);
    }

    {
        assert(normalizeAngleOneTurn(-360) == 0);
        assert(normalizeAngleOneTurn(-1) == 359);
        assert(normalizeAngleOneTurn(0) == 0);
        assert(normalizeAngleOneTurn(359) == 359);
        assert(normalizeAngleOneTurn(360) == 0);
        assert(normalizeAngleOneTurn(719) == 359);
        assert(normalizeAngleOneTurn(720) == 360);
        assert(angleInputIsStaticallySafe(-360));
        assert(angleInputIsStaticallySafe(719));
        assert(!angleInputIsStaticallySafe(720));
        assert(angleNormalizesToRetailRange(719));
        assert(!angleNormalizesToRetailRange(720));
    }

    return 0;
}
