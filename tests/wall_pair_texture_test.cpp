#include "renderer/ImgTextureSampler.hpp"
#include <cassert>
#include <cstdint>
#include <vector>

int main() {
    n3d::ImgFrame paired{};
    paired.width = 128;
    paired.height = 64;
    paired.pixels.resize(128 * 64);
    for (int x = 0; x < 128; ++x) {
        for (int y = 0; y < 64; ++y)
            paired.pixels[static_cast<std::size_t>(x) * 64 + y] =
                static_cast<std::uint8_t>(x < 64 ? 21 : 42);
    }
    assert(n3d::img::samplePreviewWallFace(paired, 0.0, 0.2, 0) == 21);
    assert(n3d::img::samplePreviewWallFace(paired, 1.0, 0.8, 0) == 21);
    assert(n3d::img::samplePreviewWallFace(paired, 0.0, 0.2, 1) == 42);
    assert(n3d::img::samplePreviewWallFace(paired, 1.0, 0.8, 1) == 42);
    assert(n3d::img::previewWallFaceHalf(1, 0, -1) == 0); // E2M1 start
    assert(n3d::img::previewWallFaceHalf(1, 0,  1) == 1);
    assert(n3d::img::previewWallFaceHalf(0, 1, 0) == 0);
    assert(n3d::img::previewWallFaceHalf(0, -1, 0) == 1);
    n3d::ImgFrame single{};
    single.width = 64;
    single.height = 64;
    single.pixels.resize(64 * 64, 53);
    assert(n3d::img::samplePreviewWallFace(single, 0.44, 0.25, 0) == 53);
    assert(n3d::img::samplePreviewWallFace(single, 0.44, 0.25, 1) == 53);
}
