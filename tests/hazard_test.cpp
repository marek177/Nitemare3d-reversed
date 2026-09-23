#include "game/HazardSystem.hpp"

#include <cassert>

int main() {
    using namespace n3d;

    const auto small = fireHazardBehavior(FireHazardClass::Small);
    assert(small.passable);
    assert(small.damagePerSimulationUpdate == 2);

    const auto medium = fireHazardBehavior(FireHazardClass::Medium);
    assert(medium.passable);
    assert(medium.damagePerSimulationUpdate == 10);

    const auto large = fireHazardBehavior(FireHazardClass::Large);
    assert(!large.passable);
    assert(large.damagePerSimulationUpdate == 100);

    assert(fireHazardClassForObjectId(0x3D) == FireHazardClass::Small);
    assert(fireHazardClassForObjectId(0x3C) == FireHazardClass::Medium);
    assert(fireHazardClassForObjectId(0x3B) == FireHazardClass::Large);
    assert(fireHazardClassForObjectId(0xFF) == FireHazardClass::None);
}
