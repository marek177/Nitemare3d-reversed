#include "re/N3DV048DemoBootstrap.hpp"
#include <cassert>

using namespace n3d::re::v048;

int main() {
    static_assert(kDemo1Header.field0 == 15);
    static_assert(kDemo1Header.field1 == 7);
    static_assert(kDemo1Header.field2 == 30);

    static_assert(kDemo1FirstRecord.key == 0x48E0);
    static_assert(kDemo1FirstRecord.inputMask == 2);
    static_assert(kDemo1FirstRecord.counter == 8);
    static_assert(kDemo1MapIndex == 10);

    static_assert(!shouldApplyRecord(7,8));
    static_assert(shouldApplyRecord(8,8));
    static_assert(alternateDemoUpdateParity(1));
    static_assert(alternateDemoUpdateParity(3));
    static_assert(!alternateDemoUpdateParity(2));

    constexpr auto s1 = nextRngState(seedFromDemoStart(1));
    constexpr auto s2 = nextRngState(s1);
    static_assert(s1 == 0x0029E2C0u);
    static_assert(rng15(s1) == 41);
    static_assert(s2 == 0xC823F683u);
    static_assert(rng15(s2) == 18467);

    static_assert(kDemo1FirstMovement.angle == 90);
    static_assert(kDemo1FirstMovement.step == 15);
    static_assert(kDemo1FirstMovement.xAfter - kDemo1FirstMovement.xBefore == 15);
    static_assert(kDemo1FirstMovement.yAfter == kDemo1FirstMovement.yBefore);
    static_assert(kDemo1FirstMovement.cellXBefore == kDemo1FirstMovement.cellXAfter);
    static_assert(kDemo1FirstMovement.cellYBefore == kDemo1FirstMovement.cellYAfter);

    static_assert(kMode3Checkpoint.mode == 3);
    static_assert(kMode3Checkpoint.renderCounter == 1);
    static_assert(kMode3Checkpoint.updateArgument == 1);
    static_assert(kMode4Checkpoint.mode == 4);
    static_assert(kMode4Checkpoint.renderCounter == 3);
    static_assert(kMode4Checkpoint.updateArgument == 2);

    return 0;
}
