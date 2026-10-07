#include "re/N3DV020VerificationHarness.hpp"

#include <array>
#include <cassert>
#include <cstdint>

int main() {
    using namespace n3d::re::v020;

    static_assert(kFastTick.offset == 0xC150);
    static_assert(kOuterScheduler.offset == 0xC1A8);
    static_assert(kMainUpdate.offset == 0xC0D8);
    static_assert(kObjectRuntimeCandidate.offset == 0x0E50);
    static_assert(kObjectRuntimeCandidate.confidence == Confidence::Open);

    static_assert(isKnownDirectRngCallsite(0x2478));
    static_assert(isKnownDirectRngCallsite(0xB276));
    static_assert(!isKnownDirectRngCallsite(0x1234));

    constexpr std::uint32_t before = 1;
    constexpr std::uint32_t after = rngNextState(before);
    constexpr std::uint16_t result = rngResult(after);

    static_assert(after == 2745024u);
    static_assert(result == 41u);

    constexpr RngTraceEntry valid{0x2478, before, after, result};
    constexpr auto validCheck = validateRngTraceEntry(valid);
    static_assert(validCheck.valid());

    constexpr RngTraceEntry badCaller{0x1234, before, after, result};
    static_assert(!validateRngTraceEntry(badCaller).valid());

    constexpr RngTraceEntry badState{0x2478, before, after + 1u, result};
    static_assert(!validateRngTraceEntry(badState).valid());

    static_assert(classifySchedulerAddress(0xBCC2) == SchedulerEvent::Irq8);
    static_assert(classifySchedulerAddress(0xC150) == SchedulerEvent::FastTick);
    static_assert(classifySchedulerAddress(0x0E50) ==
                  SchedulerEvent::ObjectRuntimeCandidate);
    static_assert(classifySchedulerAddress(0x9999) == SchedulerEvent::Unknown);

    constexpr std::array<std::uint16_t, 4> expected{
        0xBCC2, 0xBE74, 0xC150, 0xC1A8
    };
    constexpr std::array<std::uint16_t, 4> observedGood{
        0xBCC2, 0xBE74, 0xC150, 0xC1A8
    };
    constexpr std::array<std::uint16_t, 4> observedBad{
        0xBCC2, 0xBE74, 0xC0D8, 0xC1A8
    };

    const auto good = firstDivergence(expected.data(), expected.size(),
                                      observedGood.data(), observedGood.size());
    assert(!good.found);

    const auto bad = firstDivergence(expected.data(), expected.size(),
                                     observedBad.data(), observedBad.size());
    assert(bad.found);
    assert(bad.index == 2);
    assert(bad.expected == 0xC150);
    assert(bad.observed == 0xC0D8);

    return 0;
}
