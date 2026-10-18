#include "re/N3DV041FrameCompositor.hpp"

#include <cassert>
#include <cstdint>

using namespace n3d::re::v041::compositor;

int main() {
    SpritePool pool{};

    // Prove this local init only touches status, not the rest of the record.
    pool[0].opaque01 = 0xAA;
    pool[0].actorFar = 0x11223344u;
    pool[0].descriptorNear = 0x3456u;
    initializeSpriteFlags(pool);
    assert(pool[0].status == kUnusedOrCompleted);
    assert(pool[0].opaque01 == 0xAA);
    assert(pool[0].actorFar == 0x11223344u);
    assert(pool[0].descriptorNear == 0x3456u);

    markProjected(pool[0]);
    assert(pool[0].status == kAllocatedNotDrawn);

    int loadCalls = 0;
    int drawCalls = 0;
    auto missing = [](std::uint16_t) { return true; };
    auto load = [&](std::uint16_t) {
        ++loadCalls;
        return true;
    };
    auto draw = [&](const SpriteSlot&) { ++drawCalls; };

    // DOS 1.0: no lazy-load request in this bounded compositor path.
    auto r10 = compositeSpriteSlots(DosBuild::V10, pool, missing, load, draw);
    assert(r10.completed);
    assert(loadCalls == 0);
    assert(drawCalls == 1);
    assert(pool[0].status == kUnusedOrCompleted);

    markProjected(pool[1]);
    auto r17 = compositeSpriteSlots(DosBuild::V17, pool, missing, load, draw);
    assert(r17.completed);
    assert(loadCalls == 1);
    assert(drawCalls == 2);
    assert(pool[1].status == kUnusedOrCompleted);
    assert(r17.sequence.size() == 3);
    assert(r17.sequence[0].kind == StepKind::RequestLoad);
    assert(r17.sequence[1].kind == StepKind::Draw);
    assert(r17.sequence[2].kind == StepKind::MarkCompleted);

    static_assert(kDos20FrameChildren.front().target == 0x1021E);
    static_assert(kDos20FrameChildren.back().target == 0x0273C);
    return 0;
}
