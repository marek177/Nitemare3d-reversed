#pragma once

// Nitemare3D RE-MAX v0.41 integration of the instruction-derived DOS
// compositor contract recovered in the v0.56 research pass.
// This is NOT the complete renderer, image loader, qsort, IRQ or VGA path.

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace n3d::re::v041::compositor {

enum class DosBuild : std::uint8_t { V10, V17, V19, V20 };

constexpr bool hasLazyLoad(DosBuild build) noexcept {
    return build != DosBuild::V10;
}

inline constexpr std::size_t kSpriteSlotBytes = 18;
inline constexpr std::size_t kSpriteSlotCount = 100;
inline constexpr std::uint8_t kUnusedOrCompleted = 1;
inline constexpr std::uint8_t kAllocatedNotDrawn = 0;

#pragma pack(push, 1)
struct SpriteSlot {
    std::uint8_t status;
    std::uint8_t opaque01;
    std::uint32_t actorFar;
    std::uint16_t descriptorNear;
    std::uint8_t remaining[10];
};
#pragma pack(pop)

static_assert(sizeof(SpriteSlot) == 18);
static_assert(offsetof(SpriteSlot, status) == 0);
static_assert(offsetof(SpriteSlot, actorFar) == 2);
static_assert(offsetof(SpriteSlot, descriptorNear) == 6);

using SpritePool = std::array<SpriteSlot, kSpriteSlotCount>;

// Original initialization only writes the status byte at 18-byte spacing.
// The remaining bytes are not implicitly zeroed by this local routine.
constexpr void initializeSpriteFlags(SpritePool& slots) noexcept {
    for (auto& slot : slots) {
        slot.status = kUnusedOrCompleted;
    }
}

constexpr void markProjected(SpriteSlot& slot) noexcept {
    slot.status = kAllocatedNotDrawn;
}

enum class StepKind : std::uint8_t {
    RequestLoad,
    Draw,
    MarkCompleted,
};

struct Step {
    StepKind kind{};
    std::uint8_t slotIndex{};
};

struct WalkResult {
    std::vector<Step> sequence;
    bool completed{true};
};

template <typename Missing, typename Load, typename Draw>
WalkResult compositeSpriteSlots(
    DosBuild build,
    SpritePool& pool,
    Missing&& descriptorPixelsMissing,
    Load&& load,
    Draw&& draw) {
    WalkResult result{};
    for (std::size_t i = 0; i < kSpriteSlotCount; ++i) {
        auto& slot = pool[i];
        if (slot.status != kAllocatedNotDrawn) {
            continue;
        }

        if (hasLazyLoad(build) &&
            descriptorPixelsMissing(slot.descriptorNear)) {
            result.sequence.push_back(
                {StepKind::RequestLoad, static_cast<std::uint8_t>(i)});
            if (!load(slot.descriptorNear)) {
                result.completed = false;
                return result;
            }
        }

        result.sequence.push_back(
            {StepKind::Draw, static_cast<std::uint8_t>(i)});
        draw(slot);
        slot.status = kUnusedOrCompleted;
        result.sequence.push_back(
            {StepKind::MarkCompleted, static_cast<std::uint8_t>(i)});
    }
    return result;
}

struct FrameDirectChild {
    std::uint16_t dos20Site{};
    std::uint32_t target{};
};

inline constexpr std::array<FrameDirectChild, 6> kDos20FrameChildren{{
    {0xBF3B, 0x1021E},
    {0xBF40, 0x0213E},
    {0xBF52, 0x019C6},
    {0xBF5A, 0x02500},
    {0xBF5F, 0x021F0},
    {0xBF64, 0x0273C},
}};

} // namespace n3d::re::v041::compositor
