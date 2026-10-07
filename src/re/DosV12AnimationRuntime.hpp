#pragma once

#include <array>
#include <cstdint>

namespace nitemare3d::re::dos_v12 {

// Clean-room value model for the fields touched by DOS v1.2 routine
// 0800:2410. This deliberately does not claim the complete original record
// layout; only offsets used by that routine are reconstructed.
struct AnimationState {
    std::uint8_t randomVariant{}; // original record +0x02
    std::uint8_t frame{};         // original record +0x03
    std::uint8_t runtimeClass{};  // original record +0x06
    std::uint32_t deadline{};     // original record +0x08
};

// The optional table reached through sequence+0x04 contains eight selectable
// words at table+0x04+variant*2. The low byte becomes a starting frame and the
// high byte is the non-zero span used by the original threshold test.
struct RandomFrameWindow {
    std::uint8_t startFrame{};
    std::uint8_t span{};
};

struct SequenceDefinition {
    std::uint16_t frameCount{}; // original sequence +0x00
    std::uint16_t frameDelay{}; // original sequence +0x02
    bool hasRandomTable{};      // original sequence +0x04 != 0
    std::array<RandomFrameWindow, 8> randomWindows{};
};

using RandomByteFunction = std::uint8_t (*)(void* context);

enum class AnimationAdvanceResult : std::uint8_t {
    NotDue,
    Advanced,
    CompletionCallbackRequested,
};

// Reconstructs the state mutations performed by DOS v1.2 0800:2410.
//
// The original completion branch for runtime class 0x2D makes a far call. The
// clean-room helper reports that side effect to the caller instead of guessing
// the callee's engine-level behavior. For random-table sequences, randomByte
// must be non-null and at least one window must have a non-zero span, matching
// the invariant expected by the original loop.
AnimationAdvanceResult advanceAnimation(
    AnimationState& state,
    const SequenceDefinition& sequence,
    std::uint32_t currentTick,
    RandomByteFunction randomByte = nullptr,
    void* randomContext = nullptr) noexcept;

} // namespace nitemare3d::re::dos_v12
