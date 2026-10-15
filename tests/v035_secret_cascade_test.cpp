#include "re/N3DV035SecretCascade.hpp"

#include <cassert>
#include <cstdint>
#include <stdexcept>

using namespace n3d::re::v035;

namespace {
PanelWorld worldTwo(std::array<std::uint32_t,4> a,
                    std::array<std::uint32_t,4> b) {
    PanelWorld world;
    world.mapCells = {{0x5B, 0x62}, {0x5B, 0x62}};
    world.panels = {{a, 0, 2}, {b, 1, 1}};
    for (const auto& slots : {a, b}) {
        for (auto ptr : slots) {
            if (!ptr) continue;
            bool exists = false;
            for (const auto& v : world.vectors) if (v.farPointer == ptr) exists = true;
            if (!exists) world.vectors.push_back({ptr, 0, 0, 0xFF});
        }
    }
    return world;
}
}

int main() {
    static_assert(kOriginalPanelRecordBytes == 22);
    static_assert(kOriginalMatchSlotOrder == std::array<std::size_t,4>{0,2,1,3});
    static_assert(kWin110MapObjectClear < kWin110MapWallClear);
    static_assert(kWin16LocalInstructionSemanticsStaticVerified);
    static_assert(!kE1M9SameSlotVecAliasRuntimeVerified && !kOriginalCpuTraceCaptured);
    static_assert(!kDosEquivalentAlgorithmVerified && !kFullGameSecretTimingVerified);

    // Inactive B shares aligned slot with A. Completion of A erases B,
    // despite never having issued USE on B.
    {
        auto world = worldTwo({0x12340010, 0, 0, 0}, {0x12340010, 0, 0xBEEFAA10, 0});
        tickPanels(world);
        assert(world.panels[0].state == 0 && world.panels[1].state == 0);
        assert(world.mapCells[0].wall == 0 && world.mapCells[0].object == 0);
        assert(world.mapCells[1].wall == 0 && world.mapCells[1].object == 0);
        assert(originalVec(world, 0x12340010).flags == 0xFE);
        assert(originalVec(world, 0xBEEFAA10).flags == 0xFE); // all B VEC flags
    }
    // Same far pointer in DIFFERENT slots is not sufficient.
    {
        auto world = worldTwo({0x10010, 0, 0, 0}, {0, 0x10010, 0, 0});
        tickPanels(world);
        assert(world.mapCells[0].wall == 0);
        assert(world.mapCells[1].wall == 0x5B && world.mapCells[1].object == 0x62);
        assert(world.panels[1].state == 1);
    }
    // Four null pointers cannot match even the completed panel itself.
    {
        auto world = worldTwo({0, 0, 0, 0}, {0, 0, 0, 0});
        tickPanels(world);
        assert(world.panels[0].state == 0);
        assert(world.mapCells[0].wall == 0x5B && world.mapCells[0].object == 0x62);
    }
    // Original VEC pointer identity means SHARED mutation: B reads A's VEC.
    {
        auto world = worldTwo({0xABCD0001, 0, 0, 0}, {0xABCD0001, 0, 0, 0});
        auto& vec = originalVec(world, 0xABCD0001);
        vec.targetCoordinate = 5;
        tickPanels(world); // 0 -> 2
        assert(originalVec(world, 0xABCD0001).movingCoordinate == 2);
        assert(world.panels[0].state == 2 && world.panels[1].state == 1);
        tickPanels(world); // 2 -> 4
        tickPanels(world); // 4 -> 6 (no clamping)
        assert(originalVec(world, 0xABCD0001).movingCoordinate == 6);
        assert(world.mapCells[1].object == 0x62);
        tickPanels(world); // completion -> cascade
        assert(world.mapCells[0].object == 0 && world.mapCells[1].object == 0);
    }
    // A 16-bit increment can wrap: no undocumented saturation to target.
    {
        auto world = worldTwo({0x100, 0, 0, 0}, {0, 0, 0, 0});
        auto& vec = originalVec(world, 0x100);
        vec.movingCoordinate = 0xFFFE;
        vec.targetCoordinate = 0xFFFF;
        tickOnePanel(world, 0);
        assert(originalVec(world, 0x100).movingCoordinate == 0);
        assert(world.panels[0].state == 2);
    }
    // EX wall clear and SECRET cleanup are NOT a common clear-cell action.
    {
        auto world = worldTwo({0x123, 0, 0, 0}, {0, 0, 0, 0});
        applyExplodableDirectWallClear(world.mapCells[0]);
        assert(world.mapCells[0].wall == 0 && world.mapCells[0].object == 0x62);
        tickOnePanel(world, 0);
        assert(world.mapCells[0].wall == 0 && world.mapCells[0].object == 0);
    }
    // No transition for not-yet-activated panel (unless a different completes).
    {
        auto world = worldTwo({0x123, 0, 0, 0}, {0, 0, 0, 0});
        world.panels[0].state = 1;
        tickPanels(world);
        assert(world.mapCells[0].object == 0x62 && world.panels[0].state == 1);
    }
    // Missing non-null pointer is a bad synthetic fixture, not harmless NULL.
    {
        auto world = worldTwo({0x123, 0, 0, 0}, {0, 0, 0, 0});
        world.vectors.clear();
        bool threw = false;
        try { tickOnePanel(world, 0); } catch (const std::out_of_range&) { threw = true; }
        assert(threw);
    }
    return 0;
}
