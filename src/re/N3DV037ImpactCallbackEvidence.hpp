#pragma once

// Evidence-scoped direct branch: DOS v2.0 (SHA e2efde70...), Win16 v1.8
// (SHA 144e96bb...) and Win16 v1.10 (SHA 12fe5168...). Not a full projectile
// collision algorithm, and not a claim of natural runtime reachability.
#include <cstdint>
#include <optional>

namespace n3d::re::v037 {

enum class OriginalBuild : std::uint8_t { Dos20, Win18, Win110 };

// Proven three-version class-to-property encoder local to the 256-ID table.
constexpr std::uint8_t objectPropertyForClass(std::uint8_t cls) noexcept {
    std::uint8_t f = 0;
    if (cls >= 6 && cls <= 0x3d) f |= 1;
    if (cls >= 8 && cls <= 0x2d) f |= 2;
    if (cls >= 0x2f && cls <= 0x3d) f |= 4;
    if (cls >= 8 && cls <= 0x25) f |= 8;
    if (cls == 0x2a) f |= 0x20;
    if (cls == 4) f |= 0x40;
    return f;
}

// One CALLF branch in the player projectile's map collision callback.
// std::nullopt means the 0x40 gate does not call the special handler at all.
// For E2M10, AL==1 is conditional on a normal return; this model excludes
// divide faults, aborts and side effects in the E2M10 scripted handler.
constexpr std::optional<std::uint8_t> specialCallbackResult(
    OriginalBuild build, std::uint8_t objectProperty,
    std::uint8_t episode, std::uint8_t oneBasedLevel) noexcept {
    if ((objectProperty & 0x40) == 0) return std::nullopt;
    if (episode == 2 && oneBasedLevel == 10) return std::uint8_t{1};
    if (build == OriginalBuild::Dos20) return objectProperty;
    return std::uint8_t{0};
}

constexpr bool callbackConsumesProjectileOnNormalReturn(
    OriginalBuild build, std::uint8_t objectProperty,
    std::uint8_t episode, std::uint8_t oneBasedLevel) noexcept {
    const auto r = specialCallbackResult(build,objectProperty,episode,oneBasedLevel);
    return r.has_value() && *r != 0;
}

static_assert(objectPropertyForClass(4) == 0x40);
static_assert(objectPropertyForClass(0x2a) & 0x20);
static_assert(callbackConsumesProjectileOnNormalReturn(OriginalBuild::Dos20,0x40,1,1));
static_assert(!callbackConsumesProjectileOnNormalReturn(OriginalBuild::Win110,0x40,1,1));
static_assert(callbackConsumesProjectileOnNormalReturn(OriginalBuild::Win18,0x40,2,10));

inline constexpr bool kLocalOriginalStaticProven = true;
inline constexpr bool kFirstLoadLevelCensusProvenForAuditedMapSet = true;
inline constexpr bool kAllDynamicMapWritersExhausted = false;
inline constexpr bool kOriginalRuntimeParityVerified = false;

} // namespace n3d::re::v037
