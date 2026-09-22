#include "renderer/OriginalRendererFacts.hpp"

#include <cassert>

int main() {
    using namespace n3d::original_renderer;

    static_assert(kFramebufferBytes == 64000);
    static_assert(kViewportWidth == 304);
    static_assert(kViewportHeight == 152);
    static_assert(kViewportCenterX == 160);
    static_assert(kViewportCenterY == 80);
    static_assert(kViewportCenterYQ4 == 1280);

    static_assert(kVectorRecordBytes == 28);
    static_assert(kVectorCapacity == 1000);
    static_assert(kOrientationListCapacity == 333);
    static_assert(kVectorListBytes == 0x534);
    static_assert(kVectorListBases[1] - kVectorListBases[0] == 0x534);
    static_assert(kVectorListBases[2] - kVectorListBases[1] == 0x534);
    static_assert(kVectorListBases[3] - kVectorListBases[2] == 0x534);

    static_assert(kVecOrientationOffset == 0x07);
    static_assert(kVecX1Offset == 0x0C);
    static_assert(kVecY1Offset == 0x0E);
    static_assert(kVecX2Offset == 0x10);
    static_assert(kVecY2Offset == 0x12);
    static_assert(kVecScreenX1Offset == 0x14);
    static_assert(kVecProjectedY2Q4Offset == 0x1A);

    static_assert(kColumnOwnerEntries == 320);
    static_assert(kColumnOwnerEntryBytes == 4);
    static_assert(kColumnOwnerBase + kColumnOwnerEntries * kColumnOwnerEntryBytes ==
                  kWallOcclusionBase);
    static_assert(kWallOcclusionEntries == 320);
    static_assert(kWallOcclusionEntryBytes == 2);

    static_assert(kWallSpanRecordBytes == 20);
    static_assert(kWallSpanCapacity == 50);
    static_assert(kProjectedSpriteRecordBytes == 18);
    static_assert(kProjectedSpriteCapacity == 100);

    assert(kTextureColumnSamples == 64);
    assert(kTransparentSpriteIndex == 0x29);
    assert(kVecFlagTextureUFlip == 0x20);
    assert(kVisibilityModel ==
           VisibilityModel::MapBoundariesToVectorsThenSortedListsToColumnOwners);
}
