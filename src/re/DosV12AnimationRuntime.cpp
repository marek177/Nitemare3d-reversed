#include "re/DosV12AnimationRuntime.hpp"

#include "re/DosV12RuntimeAddresses.hpp"

#include <cassert>

namespace nitemare3d::re::dos_v12 {
namespace {

constexpr bool randomTableHasSelectableWindow(
    const SequenceDefinition& sequence) noexcept {
    for (const auto& window : sequence.randomWindows) {
        if (window.span != 0) return true;
    }
    return false;
}

} // namespace

AnimationAdvanceResult advanceAnimation(
    AnimationState& state,
    const SequenceDefinition& sequence,
    std::uint32_t currentTick,
    RandomByteFunction randomByte,
    void* randomContext) noexcept {
    // 0800:2419..2421: unsigned dword compare; future deadline returns.
    if (state.deadline > currentTick) {
        return AnimationAdvanceResult::NotDue;
    }

    // 0800:2425
    ++state.frame;

    AnimationAdvanceResult result = AnimationAdvanceResult::Advanced;

    if (state.runtimeClass == kForceFrameZeroClass) {
        // 0800:242D/2430 -> 24D4
        state.frame = 0;
    } else if (state.runtimeClass == kStaticLikeClass) {
        // 0800:249E..24BA. Preserve the original byte-level decrement when
        // frameCount is zero or has a high byte; valid game data is smaller.
        if (state.frame == 1) {
            --state.frame;
        } else if (static_cast<std::uint16_t>(state.frame) >= sequence.frameCount) {
            auto lowCount = static_cast<std::uint8_t>(sequence.frameCount);
            state.frame = static_cast<std::uint8_t>(lowCount - 1u);
        }
    } else if (state.runtimeClass == kCompletionCallbackClass) {
        // 0800:24BC..24CE. The original calls 0FAD:072E(state) when the final
        // frame is reached, then still schedules the next deadline.
        if (static_cast<std::uint16_t>(state.frame) >= sequence.frameCount) {
            result = AnimationAdvanceResult::CompletionCallbackRequested;
        }
    } else if (sequence.hasRandomTable) {
        // 0800:2447..248F. The currently selected window remains active while
        // start+span > frame. Otherwise RNG&7 selects a non-empty window and
        // its low byte becomes the new frame.
        assert(state.randomVariant < sequence.randomWindows.size());
        if (state.randomVariant >= sequence.randomWindows.size()) {
            state.deadline = currentTick + static_cast<std::uint32_t>(sequence.frameDelay);
            return result;
        }
        const auto current = sequence.randomWindows[state.randomVariant];
        const auto endExclusive = static_cast<std::uint16_t>(current.startFrame) +
                                  static_cast<std::uint16_t>(current.span);
        if (endExclusive <= static_cast<std::uint16_t>(state.frame)) {
            assert(randomByte != nullptr);
            assert(randomTableHasSelectableWindow(sequence));
            if (randomByte != nullptr && randomTableHasSelectableWindow(sequence)) {
                RandomFrameWindow selected{};
                do {
                    state.randomVariant = static_cast<std::uint8_t>(
                        randomByte(randomContext) & 7u);
                    selected = sequence.randomWindows[state.randomVariant];
                } while (selected.span == 0);
                state.frame = selected.startFrame;
            }
        }
    } else if (static_cast<std::uint16_t>(state.frame) >= sequence.frameCount) {
        // 0800:2492..249B -> 24D4
        state.frame = 0;
    }

    // 0800:24D8..24EB: 32-bit add with natural wraparound.
    state.deadline = currentTick + static_cast<std::uint32_t>(sequence.frameDelay);
    return result;
}

} // namespace nitemare3d::re::dos_v12
