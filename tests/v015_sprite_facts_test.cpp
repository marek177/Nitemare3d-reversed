#include "re/N3DV015SpriteFacts.hpp"

#include <cassert>

int main() {
    using namespace n3d::re::v015;

    static_assert(kBatBehavior.anchor == VerticalAnchor::Ceiling);
    static_assert(kBatBehavior.viewMode == ViewMode::Animated);
    static_assert(kBatBehavior.verticalOscillation);
    static_assert(kBatBehavior.evidence == Evidence::Behavioral);
    static_assert(!isExecutableVerified(kBatBehavior));

    static_assert(kBedBehavior.anchor == VerticalAnchor::Floor);
    static_assert(kBedBehavior.viewMode == ViewMode::Directional2);
    static_assert(kBedBehavior.blocksPlayer);
    static_assert(hasDirectionalVariants(kBedBehavior.viewMode));
    static_assert(!kBedBehavior.verticalOscillation);

    static_assert(kKnownAnchorClasses.size() == 4);
    assert(!isExecutableVerified(kBedBehavior));
    return 0;
}
