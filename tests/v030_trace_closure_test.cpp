#include "re/N3DV030TraceClosure.hpp"

#include <array>
#include <cassert>
#include <span>

using namespace n3d::re::v030;

int main() {
    static_assert(kCanonicalDos20UnpackedLength == 171360u);
    static_assert(kCanonicalDos20UnpackedSha ==
        "e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297");

    constexpr std::uint32_t a0 = 1u;
    constexpr std::uint32_t a1 = v020::rngNextState(a0);
    constexpr std::uint32_t a2 = v020::rngNextState(a1);
    constexpr std::uint32_t a3 = v020::rngNextState(a2);
    constexpr std::array<RngRecord, 3> reference{{
        {0x2478, a0, a1, v020::rngResult(a1)},
        {0x525E, a1, a2, v020::rngResult(a2)},
        {0x58A7, a2, a3, v020::rngResult(a3)}
    }};
    static_assert(firstInvalidRngEntry(reference, 1) == 3);
    static_assert(firstInvalidRngEntry(reference, 2) == 0);

    constexpr TraceSeal sealed{true, true, true, true, true, true};
    constexpr TraceSeal noEnd{true, false, true, true, true, true};
    static_assert(sealed.fullyAttested());
    static_assert(!noEnd.fullyAttested());
    static_assert(compareRngTraces(reference, reference, 1).verdict ==
                  ComparisonVerdict::EqualUnsealed);
    static_assert(compareRngTraces(reference, reference, 1, sealed).verdict ==
                  ComparisonVerdict::EqualAttested);
    static_assert(compareRngTraces(reference, reference, 1, noEnd).verdict ==
                  ComparisonVerdict::EqualUnsealed);

    constexpr std::array<RngRecord, 3> differentCaller{{
        reference[0], {0x5666, a1, a2, v020::rngResult(a2)}, reference[2]
    }};
    constexpr auto mismatch =
        compareRngTraces(reference, differentCaller, 1, sealed);
    static_assert(mismatch.verdict == ComparisonVerdict::FirstDifference);
    static_assert(mismatch.index == 1);
    static_assert(mismatch.referenceCaller == 0x525E);
    static_assert(mismatch.candidateCaller == 0x5666);

    // A valid but shorter stream is still an error, never an "equal prefix".
    constexpr std::array<RngRecord, 2> shortCandidate{{
        reference[0], reference[1]
    }};
    static_assert(compareRngTraces(reference, shortCandidate, 1, sealed).verdict ==
                  ComparisonVerdict::CountDifference);

    // Removing a captured middle draw breaks continuity even if the final
    // RNG state still looks plausible in the remaining raw rows.
    constexpr std::array<RngRecord, 2> skippedRecord{{
        reference[0], reference[2]
    }};
    static_assert(compareRngTraces(reference, skippedRecord, 1).verdict ==
                  ComparisonVerdict::InvalidCandidate);
    static_assert(compareRngTraces(reference, skippedRecord, 1).index == 1);

    constexpr std::array<RngRecord, 3> wrongResult{{
        reference[0], {0x525E, a1, a2,
                       static_cast<std::uint16_t>(v020::rngResult(a2) + 1u)},
        reference[2]
    }};
    static_assert(compareRngTraces(reference, wrongResult, 1).verdict ==
                  ComparisonVerdict::InvalidCandidate);
    constexpr std::array<RngRecord, 3> unknownCaller{{
        reference[0], {0xFFFF, a1, a2, v020::rngResult(a2)}, reference[2]
    }};
    static_assert(compareRngTraces(reference, unknownCaller, 1).verdict ==
                  ComparisonVerdict::InvalidCandidate);

    constexpr std::array<RngRecord, 0> empty{};
    static_assert(compareRngTraces(empty, empty, 1).verdict ==
                  ComparisonVerdict::EmptyReference);
    static_assert(compareRngTraces(reference, empty, 1).verdict ==
                  ComparisonVerdict::EmptyCandidate);

    assert(compareRngTraces(reference, reference, 1, sealed).streamEqual());
    assert(!compareRngTraces(reference, differentCaller, 1, sealed).streamEqual());
    return 0;
}
