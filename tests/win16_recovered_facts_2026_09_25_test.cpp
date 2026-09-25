#include "re/Win16RecoveredFacts_2026_09_25.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>

int main() {
    namespace f = nitemare3d::re::win16_20260925;

    static_assert(f::kHudDispatcherSegment == 3 && f::kHudDispatcherOffset == 0xA3B6);
    static_assert(f::kAutomapDispatcherSegment == 3 && f::kAutomapDispatcherOffset == 0xB1A4);
    static_assert(f::hudPortraitFrame(0) == 13);
    static_assert(f::hudPortraitFrame(1) == 14);
    static_assert(f::hudPortraitFrame(10) == 14);
    static_assert(f::hudPortraitFrame(11) == 15);
    static_assert(f::hudPortraitFrame(90) == 22);
    static_assert(f::hudPortraitFrame(91) == 23);
    static_assert(f::hudPortraitFrame(100) == 23);
    static_assert(f::hudPortraitFrame(255) == 23);

    static_assert(f::kAutomapBytes == 64 * 64);
    static_assert(f::automapIndex(0, 0) == 0);
    static_assert(f::automapIndex(1, 0) == 64);
    static_assert(f::automapIndex(63, 63) == 4095);
    static_assert(f::automapOriginX(0) == 0);
    static_assert(f::automapOriginX(31) == 0);
    static_assert(f::automapOriginX(32) == 1);
    static_assert(f::automapOriginX(63) == 2);
    static_assert(f::automapOriginY(0) == 0);
    static_assert(f::automapOriginY(18) == 0);
    static_assert(f::automapOriginY(19) == 1);
    static_assert(f::automapOriginY(63) == 28);

    static_assert(f::automapNoisePointCount(0) == 0);
    static_assert(f::automapNoisePointCount(1) == 500);
    static_assert(f::automapNoisePointCount(2) == 62);
    static_assert(f::automapNoisePointCount(7) == 1);
    static_assert(f::automapNoisePointCount(8) == 0);
    static_assert(!f::enemyLocatorVisible(0));
    static_assert(f::enemyLocatorVisible(1));
    static_assert(!f::enemyLocatorVisible(2));
    static_assert(f::enemyLocatorVisible(15));
    static_assert(f::enemyLocatorVisible(16));

    static_assert(f::automapGuardClassExcluded(0x15));
    static_assert(f::automapGuardClassExcluded(0x21));
    static_assert(!f::automapGuardClassExcluded(0x20));

    static_assert(f::kViewportWidth == 304 && f::kViewportHeight == 152);
    static_assert(f::kVisibleSpanCapacity == 50 && f::kVisibleSpanStride == 20);
    static_assert(f::kProjectedSpriteCapacity == 100 && f::kProjectedSpriteStride == 18);
    static_assert(f::kVecListCount == 4 && f::kVecListCapacity == 333);

    static_assert(f::kGuardStride == 0x1A);
    static_assert(f::kGuardResultOctant == 0x12);
    static_assert(f::kGuardState13MoveX == 0x13 && f::kGuardState13MoveY == 0x14);
    static_assert(f::guardState13Step(0).dx == 0 && f::guardState13Step(0).dy == -8);
    static_assert(f::guardState13Step(1).dx == 8 && f::guardState13Step(1).dy == 0);
    static_assert(f::guardState13Step(5).dx == -8 && f::guardState13Step(5).dy == 0);

    static_assert(f::imgColumnMajorPixelIndex(2, 3, 10) == 23);
    static_assert(f::kHudBankFrameCount == 29);
    static_assert(f::kUifDirectorySlots == 32 && f::kUifDirectoryEntryBytes == 6);

    static_assert(f::kMenuDispatcherSegment == 4 && f::kMenuDispatcherOffset == 0x27DE);
    static_assert(f::kMenuTableCount == 14 && f::kMenuItemCount == 80);
    static_assert(f::kSaveSlotCount == 10 && f::kSaveNameMaxChars == 40 &&
                  f::kSaveNameMaxPixels == 179);

    assert(true);
    return 0;
}
