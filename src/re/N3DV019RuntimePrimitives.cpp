#include "re/N3DV019RuntimePrimitives.hpp"

#include <algorithm>

namespace n3d::re::v019 {

std::int16_t retractCoordinateToward(std::int16_t firstEndpoint,
                                     std::int16_t secondEndpoint) noexcept {
    if (firstEndpoint < secondEndpoint) {
        const auto advanced = static_cast<int>(firstEndpoint) +
                              static_cast<int>(kSecretPanelStepPerUpdate);
        return static_cast<std::int16_t>(
            std::min(advanced, static_cast<int>(secondEndpoint)));
    }

    if (firstEndpoint > secondEndpoint) {
        const auto advanced = static_cast<int>(firstEndpoint) -
                              static_cast<int>(kSecretPanelStepPerUpdate);
        return static_cast<std::int16_t>(
            std::max(advanced, static_cast<int>(secondEndpoint)));
    }

    return firstEndpoint;
}

}  // namespace n3d::re::v019
