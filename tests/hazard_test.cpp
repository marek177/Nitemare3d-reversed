#include "game/HazardSystem.hpp"

#include <cassert>
#include <iostream>

int main() {
    using namespace n3d;

    const auto small = fireHazardBehavior(FireHazardClass::Small);
    assert(small.passable);
    assert(!small.instantKill);
    assert(small.appliesContinuousDamage);

    const auto medium = fireHazardBehavior(FireHazardClass::Medium);
    assert(medium.passable);
    assert(!medium.instantKill);
    assert(medium.appliesContinuousDamage);

    const auto large = fireHazardBehavior(FireHazardClass::Large);
    assert(!large.passable);
    assert(large.instantKill);
    assert(!large.appliesContinuousDamage);

    std::cout << "hazard_test: PASS\n";
    return 0;
}
