#pragma once

namespace n3d {

enum class GameEdition {
    Episode1Demo,
    CompleteTrilogy,
};

inline constexpr bool hasCompleteTrilogy(GameEdition edition) {
    return edition == GameEdition::CompleteTrilogy;
}

} // namespace n3d
