#include "re/N3DV020VerificationHarness.hpp"

#include <algorithm>

namespace n3d::re::v020 {

FirstDivergence firstDivergence(const std::uint16_t* expected,
                                std::size_t expectedCount,
                                const std::uint16_t* observed,
                                std::size_t observedCount) noexcept {
    const auto common = std::min(expectedCount, observedCount);

    for (std::size_t i = 0; i < common; ++i) {
        if (expected[i] != observed[i]) {
            return {i, expected[i], observed[i], true};
        }
    }

    if (expectedCount != observedCount) {
        const auto expectedValue =
            common < expectedCount ? expected[common] : std::uint16_t{0};
        const auto observedValue =
            common < observedCount ? observed[common] : std::uint16_t{0};
        return {common, expectedValue, observedValue, true};
    }

    return {common, 0, 0, false};
}

}  // namespace n3d::re::v020
