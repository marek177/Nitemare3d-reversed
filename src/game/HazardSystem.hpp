#pragma once

#include <cstdint>

namespace n3d {

// Episode 3 fire behavior reconstructed from the original hint material and
// the E3M6 walkthrough.  The numeric damage values/tick interval remain
// intentionally unspecified until they are recovered from NITE3W.EXE.
enum class FireHazardClass : std::uint8_t {
    None = 0,
    Small,
    Medium,
    Large,
};

struct FireHazardBehavior {
    bool passable{};
    bool instantKill{};
    bool appliesContinuousDamage{};
};

constexpr FireHazardBehavior fireHazardBehavior(FireHazardClass fire) {
    switch (fire) {
    case FireHazardClass::Small:
        // E3M6: visibly traversable; player takes damage while crossing.
        return {true, false, true};
    case FireHazardClass::Medium:
        // Official behavior: passable, but almost deadly; E3M6 shows the
        // player can cross it and survive with severe health loss.
        return {true, false, true};
    case FireHazardClass::Large:
        // Large flames are the lethal/impassable class.
        return {false, true, false};
    case FireHazardClass::None:
    default:
        return {true, false, false};
    }
}

} // namespace n3d
