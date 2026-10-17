#include "re/N3DV038ThreeDayFindings.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::v038;

int main() {
    {
        const auto r = joystickCalibration(0, 50);
        assert(!r.divideError);
        assert(r.rawQuotient == 0);
        assert(r.storedV18 == 0);
        assert(r.storedV110 == 1);
    }
    {
        const auto r = joystickCalibration(49, 50);
        assert(r.rawQuotient == 0);
        assert(r.storedV110 == 1);
    }
    {
        const auto r = joystickCalibration(50, 50);
        assert(r.rawQuotient == 1);
        assert(r.storedV18 == 1);
        assert(r.storedV110 == 1);
    }
    {
        const auto r = joystickCalibration(32768u, 1u);
        assert(r.rawQuotient == 32768u);
        assert(r.storedV18 == 32768u);
        assert(r.storedV110 == 1u);
    }
    assert(joystickCalibration(1, 0).divideError);

    {
        const auto b = magicEyeNoiseBudget(1);
        assert(!b.divideError && b.dots == 500 && b.directRngCalls == 1000);
    }
    {
        const auto b = magicEyeNoiseBudget(7);
        assert(!b.divideError && b.dots == 1 && b.directRngCalls == 2);
    }
    {
        const auto b = magicEyeNoiseBudget(8);
        assert(!b.divideError && b.dots == 0 && b.directRngCalls == 0);
    }
    assert(magicEyeNoiseBudget(0).divideError);

    assert(doorState4BlocksNormalUse(4));
    assert(!doorState4BlocksNormalUse(3));

    {
        auto d = normalDoorOpeningStep(0, 4);
        assert(d.coordinate == 2 && d.state == 2 && !d.completed);
        d = normalDoorOpeningStep(d.coordinate, 4, d.state);
        assert(d.coordinate == 4 && d.state == 0 && d.completed && !d.cleanup);
    }
    {
        auto p = fourVectorPanelStep(0, 4);
        assert(p.coordinate == 2 && p.state == 2 && !p.completed);
        p = fourVectorPanelStep(p.coordinate, 4, p.state);
        assert(p.coordinate == 4 && p.state == 2 && !p.completed);
        p = fourVectorPanelStep(p.coordinate, 4, p.state);
        assert(p.coordinate == 4 && p.state == 0 && p.completed && p.cleanup);
    }

    for (std::uint16_t difficulty = 0; difficulty < 3; ++difficulty) {
        assert(class16PlayerHitDamage(1, difficulty) == 0);
    }
    assert(class16PlayerHitDamage(3, 0) == 6);
    assert(class16PlayerHitDamage(3, 1) == 3);
    assert(class16PlayerHitDamage(3, 2) == 1);

    assert(class16ToPlayerAmount(1, 0, 0) == 16);
    assert(class16ToPlayerAmount(1, 0, 1) == 33);
    assert(class16ToPlayerAmount(1, 0, 2) == 66);
    assert(class16ToPlayerAmount(1, 1, 0) == 50);
    assert(class16ToPlayerAmount(1, 1, 1) == 100);
    assert(class16ToPlayerAmount(1, 1, 2) == 200);

    assert(signedEvery20AfterIncrement(19));
    assert(signedEvery20AfterIncrement(0xFFEBu));
    assert(!signedEvery20AfterIncrement(18));

    assert(low16Average(4, 5) == 0);
    assert(low16Average(5, 5) == 1);
    assert(low16Average(327680u, 5) == 0);

    {
        const auto view = projectileCallbackView(10, 10, -5, 1);
        assert(view.storedX == 10);
        assert(view.storedY == 10);
        assert(view.updatedError == -5);
        assert(view.storedState == 1);
    }

    static_assert(kDos12GraphicsSaveSegmentLink == 0x1BDCu);
    static_assert(kDos20GraphicsSaveSegmentLink == 0x1C08u);
    return 0;
}
