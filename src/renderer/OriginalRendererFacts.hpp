#pragma once

#include <cstddef>
#include <cstdint>

namespace n3d::original_renderer {

// Instruction-backed constants recovered from NITE3W.EXE.  These describe
// the original Win16 renderer; they are not a claim that the current
// verification Raycaster already implements that pipeline.
inline constexpr std::size_t kFramebufferWidth = 320;
inline constexpr std::size_t kFramebufferHeight = 200;
inline constexpr std::size_t kFramebufferBytes =
    kFramebufferWidth * kFramebufferHeight;
inline constexpr std::size_t kTextureColumnSamples = 64;
inline constexpr std::uint8_t kTransparentSpriteIndex = 0x29;
inline constexpr std::size_t kWallSpanRecordBytes = 0x14;
inline constexpr std::size_t kWallSpanCapacity = 50;
inline constexpr std::size_t kProjectedSpriteRecordBytes = 0x12;
inline constexpr std::size_t kProjectedSpriteCapacity = 100;

enum class VisibilityModel {
    SortedVectorListsToColumnOwners,
};

inline constexpr VisibilityModel kVisibilityModel =
    VisibilityModel::SortedVectorListsToColumnOwners;

} // namespace n3d::original_renderer
