#include "re/N3DV021SubsystemEvidence.hpp"

namespace n3d::re::v021 {

TraceOrderCheck verifyRelativeOrder(const std::uint16_t* trace,
                                    std::size_t count,
                                    std::uint16_t first,
                                    std::uint16_t second) noexcept {
    std::size_t firstIndex = count;
    std::size_t secondIndex = count;

    for (std::size_t i = 0; i < count; ++i) {
        if (firstIndex == count && trace[i] == first) {
            firstIndex = i;
        }
        if (secondIndex == count && trace[i] == second) {
            secondIndex = i;
        }
    }

    const bool firstSeen = firstIndex != count;
    const bool secondSeen = secondIndex != count;
    const bool orderSatisfied =
        firstSeen && secondSeen && firstIndex < secondIndex;

    return {firstSeen, secondSeen, orderSatisfied};
}

}  // namespace n3d::re::v021
