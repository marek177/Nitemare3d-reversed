#include "renderer/OriginalRendererFacts.hpp"

#include <cassert>

int main() {
    using namespace n3d::original_renderer;

    static_assert(kFramebufferBytes == 64000);
    static_assert(kWallSpanRecordBytes == 20);
    static_assert(kProjectedSpriteRecordBytes == 18);

    assert(kTextureColumnSamples == 64);
    assert(kTransparentSpriteIndex == 0x29);
    assert(kWallSpanCapacity == 50);
    assert(kProjectedSpriteCapacity == 100);
    assert(kVisibilityModel == VisibilityModel::SortedVectorListsToColumnOwners);
}
