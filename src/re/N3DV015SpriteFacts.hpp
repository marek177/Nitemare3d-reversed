#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v015 {

enum class Evidence : std::uint8_t {
    VerifiedExe,
    VerifiedData,
    Behavioral,
    Inferred,
    Partial,
    Todo
};

enum class VerticalAnchor : std::uint8_t {
    Floor,
    MidHeight,
    Ceiling,
    Unknown
};

enum class ViewMode : std::uint8_t {
    Fixed,
    Directional2,
    Directional4,
    Directional8,
    Animated,
    Unknown
};

struct SpriteBehavior {
    std::string_view name{};
    VerticalAnchor anchor{VerticalAnchor::Unknown};
    ViewMode viewMode{ViewMode::Unknown};
    bool blocksPlayer{};
    bool verticalOscillation{};
    Evidence evidence{Evidence::Todo};
    std::string_view note{};
};

inline constexpr SpriteBehavior kBatBehavior{
    "Bat",
    VerticalAnchor::Ceiling,
    ViewMode::Animated,
    false,
    true,
    Evidence::Behavioral,
    "Gameplay/video observation: ceiling-associated sprite with wing animation and vertical bob/oscillation; exact EXE writer remains open."
};

inline constexpr SpriteBehavior kBedBehavior{
    "Bed",
    VerticalAnchor::Floor,
    ViewMode::Directional2,
    true,
    false,
    Evidence::Behavioral,
    "Observed front/side visual variants. Exact object definition flags and renderer selector remain unresolved."
};

inline constexpr std::array<VerticalAnchor, 4> kKnownAnchorClasses = {
    VerticalAnchor::Floor,
    VerticalAnchor::MidHeight,
    VerticalAnchor::Ceiling,
    VerticalAnchor::Unknown
};

constexpr bool hasDirectionalVariants(ViewMode mode) {
    return mode == ViewMode::Directional2 ||
           mode == ViewMode::Directional4 ||
           mode == ViewMode::Directional8;
}

constexpr bool isExecutableVerified(const SpriteBehavior& behavior) {
    return behavior.evidence == Evidence::VerifiedExe;
}

} // namespace n3d::re::v015
