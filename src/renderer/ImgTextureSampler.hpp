#pragma once

#include "formats/ImgArchive.hpp"

#include <algorithm>
#include <cstddef>
#include <cstdint>

namespace n3d::img {

enum class RenderSlot : std::uint8_t { Wall, Object };

// The on-disk IMG pixel plane is column-major: pixels[x * height + y].
// Each slot points to an absolute IMG frame offset. Zero/unresolved slots
// intentionally return nullptr so the DDA preview can use a fallback color.
inline const ImgFrame* imageForSlot(const ImgArchive& archive,
                                    RenderSlot bank,
                                    std::uint8_t slot) noexcept {
    const auto& offsets = bank == RenderSlot::Wall
        ? archive.wallSlotOffsets() : archive.objectSlotOffsets();
    if (static_cast<std::size_t>(slot) >= offsets.size() || !offsets[slot]) {
        return nullptr;
    }
    const auto index = archive.frameAtExactOffset(offsets[slot]);
    if (!index || *index >= archive.frames().size()) {
        return nullptr;
    }
    const auto& frame = archive.frames()[*index];
    const auto expected = static_cast<std::size_t>(frame.width) * frame.height;
    if (!expected || frame.pixels.size() != expected) {
        return nullptr;
    }
    return &frame;
}

inline std::uint8_t pixelAtColumnMajor(const ImgFrame& frame,
                                       unsigned x, unsigned y) noexcept {
    if (x >= frame.width || y >= frame.height ||
        (static_cast<std::size_t>(x) * frame.height + y) >= frame.pixels.size()) {
        return 0;
    }
    return frame.pixels[static_cast<std::size_t>(x) * frame.height + y];
}

// Provisional nearest-neighbour mapping of each 64/128-wide image onto one
// DDA wall face. This is deliberately NOT a recovered DOS texture-U contract.
inline std::uint8_t sampleImage(const ImgFrame& frame, double u, double v) noexcept {
    if (!frame.width || !frame.height) return 0;
    const auto x = static_cast<unsigned>(std::clamp(u, 0.0, 1.0) * frame.width);
    const auto y = static_cast<unsigned>(std::clamp(v, 0.0, 1.0) * frame.height);
    return pixelAtColumnMajor(frame,
        std::min(x, static_cast<unsigned>(frame.width - 1)),
        std::min(y, static_cast<unsigned>(frame.height - 1)));
}

// Many wall frames store two distinct 64x64 faces in one 128x64 IMG
// allocation (elevator doors visibly contain two *complete* doors).
// Do not stretch the full 128 pixels across one wall cell; use a single face.
// The exact orientation-bit choice is still a preview heuristic pending
// instruction-level DOS VEC/EBD6 proof (not a parity contract).
inline unsigned previewWallFaceHalf(int ddaSide, int stepX, int stepY) noexcept {
    // Verified qualitative witness: E2M1 starts facing north (-Y). Its
    // elevator DOORH is the left-hand half in the original video.
    return ddaSide == 1 ? (stepY > 0 ? 1u : 0u) : (stepX < 0 ? 1u : 0u);
}

inline std::uint8_t samplePreviewWallFace(const ImgFrame& frame, double u,
                                         double v, unsigned half) noexcept {
    if (frame.width != 128 || frame.height != 64) {
        return sampleImage(frame, u, v);
    }
    // Avoid reaching pixel 64 on a u=1 sample of the first face.
    const unsigned x = std::min(63u,
        static_cast<unsigned>(std::clamp(u, 0.0, 1.0) * 64.0));
    const unsigned y = std::min(63u,
        static_cast<unsigned>(std::clamp(v, 0.0, 1.0) * 64.0));
    return pixelAtColumnMajor(frame, x + (half ? 64u : 0u), y);
}

inline constexpr std::uint8_t kSpriteTransparentIndex = 0x1Fu;

} // namespace n3d::img
