#include "re/N3DV049Oct19Evidence.hpp"
#include "game/CombatSystem.hpp"
#include "game/GuardSystem.hpp"
#include "re/Win16MfcMemory.hpp"

#include <cassert>

using namespace n3d::re::v049;

int main() {
    static_assert(nextRngState(kRng11.before) == kRng11.after);
    static_assert(rng15(kRng11.after) == kRng11.result);
    static_assert(nextRngState(kRng12.before) == kRng12.after);
    static_assert(rng15(kRng12.after) == kRng12.result);
    static_assert(nextRngState(kRng15.before) == kRng15.after);
    static_assert(rng15(kRng15.after) == kRng15.result);
    static_assert(nextRngState(kRng16.before) == kRng16.after);
    static_assert(rng15(kRng16.after) == kRng16.result);
    static_assert(nextRngState(kRng17Prediction.before) == kRng17Prediction.after);
    static_assert(rng15(kRng17Prediction.after) == kRng17Prediction.result);
    static_assert(!kRng17Prediction.postObserved);

    static_assert(kGuard41Death.guardIndex == 41);
    static_assert(kGuard41Death.hpBefore == 111);
    static_assert(kGuard41Death.hpAfter == 0);
    static_assert(kGuard41Death.damage == 165);

    static_assert(kDos20E1M1Trace.instructions == 3775835);
    static_assert(kDos20E1M1Trace.dispatcherCalls == 396);
    static_assert(kDos20E1M1Trace.state7Dispatches + kDos20E1M1Trace.state8Dispatches == 396);
    static_assert(kDos20E1M1Trace.vramAddressMismatches == 0);
    static_assert(kDos20E1M1Trace.vramColorMismatches == 0);

    static_assert(kDos20ControlledProjectile.stateAfterFire == 1);
    static_assert(kDos20ControlledProjectile.stateAtImpact == 2);
    static_assert(kDos20ControlledProjectile.stateAfterExpiry == 0);
    static_assert(kDos20ControlledProjectile.ammoBefore == 64);
    static_assert(kDos20ControlledProjectile.ammoAfter == 63);

    static_assert(e2m10WaitQuotient(100, 9, 14) == 64);
    static_assert(kE2M10RepeatedOuterSchedulerBackedgeStatic);
    static_assert(!kNaturalProjectileAbaObserved);

    static_assert(win110PaletteCopyCount(false) == 256);
    static_assert(win110PaletteCopyCount(true) == 236);
    static_assert(kWin110SystemPaletteReserveAtEachEnd == 10);
    static_assert(!kWin16GameWindowObservedInCurrentLab);
    static_assert(kWin16BuildsTriedInCurrentLab == 5);

    static_assert(nitemare3d::game::kFreshGuardStrength == 0xFF);
    static_assert(sizeof(nitemare3d::re::win16::HandleMap16) == 0x26);

    assert(kDos20ControlledProjectile.yImpact < kDos20ControlledProjectile.yFirst);
    return 0;
}
