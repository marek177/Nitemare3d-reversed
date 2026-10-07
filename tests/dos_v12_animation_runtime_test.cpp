#include "re/DosV12AnimationRuntime.hpp"
#include "re/DosV12RuntimeAddresses.hpp"

#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>

namespace {

struct RandomScript {
    std::array<std::uint8_t, 4> values{};
    std::size_t cursor{};
};

std::uint8_t scriptedRandom(void* opaque) {
    auto& script = *static_cast<RandomScript*>(opaque);
    assert(script.cursor < script.values.size());
    return script.values[script.cursor++];
}

} // namespace

int main() {
    using namespace nitemare3d::re::dos_v12;

    static_assert(kCurrentTickDword == 0x07EC);
    static_assert(kCurrentTickHighWord == 0x07EE);
    static_assert(kAnimationAdvanceDisasmSegment == 0x0800);
    static_assert(kAnimationAdvanceDisasmOffset == 0x2410);
    static_assert(kRecordDeadlineOffset == 0x08);

    SequenceDefinition linear{};
    linear.frameCount = 3;
    linear.frameDelay = 5;

    AnimationState notDue{0, 1, 0x10, 101};
    assert(advanceAnimation(notDue, linear, 100) ==
           AnimationAdvanceResult::NotDue);
    assert(notDue.frame == 1);
    assert(notDue.deadline == 101);

    AnimationState linearAdvance{0, 1, 0x10, 100};
    assert(advanceAnimation(linearAdvance, linear, 100) ==
           AnimationAdvanceResult::Advanced);
    assert(linearAdvance.frame == 2);
    assert(linearAdvance.deadline == 105);

    AnimationState linearWrap{0, 2, 0x10, 100};
    advanceAnimation(linearWrap, linear, 100);
    assert(linearWrap.frame == 0);

    AnimationState forceZero{0, 9, kForceFrameZeroClass, 0};
    advanceAnimation(forceZero, linear, 10);
    assert(forceZero.frame == 0);
    assert(forceZero.deadline == 15);

    AnimationState class07{0, 0, kStaticLikeClass, 0};
    advanceAnimation(class07, linear, 10);
    assert(class07.frame == 0); // ++0 -> 1 -> -- -> 0

    AnimationState completion{0, 2, kCompletionCallbackClass, 0};
    assert(advanceAnimation(completion, linear, 20) ==
           AnimationAdvanceResult::CompletionCallbackRequested);
    assert(completion.frame == 3); // original callee owns completion side effects
    assert(completion.deadline == 25);

    SequenceDefinition randomized{};
    randomized.frameCount = 20;
    randomized.frameDelay = 7;
    randomized.hasRandomTable = true;
    randomized.randomWindows[0] = {2, 2}; // active for frames < 4
    randomized.randomWindows[3] = {8, 0}; // deliberately unselectable
    randomized.randomWindows[5] = {11, 3};

    RandomScript script{{3, 5, 0, 0}, 0};
    AnimationState randomState{0, 3, 0x10, 0};
    assert(advanceAnimation(randomState, randomized, 30,
                            scriptedRandom, &script) ==
           AnimationAdvanceResult::Advanced);
    assert(script.cursor == 2); // 3 rejected (span 0), then 5 accepted
    assert(randomState.randomVariant == 5);
    assert(randomState.frame == 11);
    assert(randomState.deadline == 37);

    SequenceDefinition wrapDelay{};
    wrapDelay.frameCount = 4;
    wrapDelay.frameDelay = 0x20;
    AnimationState wrapTick{0, 0, 0x10, 0xFFFFFFF0u};
    advanceAnimation(wrapTick, wrapDelay, 0xFFFFFFF0u);
    assert(wrapTick.deadline == 0x00000010u);

    return 0;
}
