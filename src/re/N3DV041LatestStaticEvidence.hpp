#pragma once

#include <array>
#include <cstdint>

namespace n3d::re::v041 {

struct MapCell {
    std::uint8_t wallId{};
    std::uint8_t objectId{};
};

// Win16 1.3-1.10 E1M9 radio/special mode-0 local effect:
// OBJECT+0C points at the WALL byte, so the original write clears wallId.
// It does NOT clear the adjacent objectId byte.
constexpr MapCell clearRadioWallOnly(MapCell cell) noexcept {
    cell.wallId = 0;
    return cell;
}

constexpr std::uint32_t combineSplitClock(
    std::uint16_t lowWord,
    std::uint16_t highWord) noexcept {
    return static_cast<std::uint32_t>(lowWord) |
           (static_cast<std::uint32_t>(highWord) << 16u);
}

// Projectile rearm reads low and high clock words with separate 16-bit
// instructions. This models the composed value; whether an IRQ occurs between
// those reads is an external timing/reachability question.
constexpr std::uint32_t projectileRearmDeadline(
    std::uint16_t lowWordRead,
    std::uint16_t highWordRead,
    std::uint16_t interval) noexcept {
    return combineSplitClock(lowWordRead, highWordRead) +
           static_cast<std::uint32_t>(interval);
}

struct NestedSchedulerTail {
    std::uint32_t nextFrame{};
    std::uint32_t legacyEpoch{};
};

// DOS v2.0 outer tail after nested projectile callbacks:
// nextFrame uses the latest GLOBAL frame scratch, while legacyEpoch is written
// from the OUTER invocation's stack-local snapshot.
constexpr NestedSchedulerTail commitOuterTailAfterNested(
    std::uint32_t latestGlobalFrameScratch,
    std::uint32_t outerLocalLegacySnapshot) noexcept {
    return {latestGlobalFrameScratch + 1u, outerLocalLegacySnapshot};
}

enum class E2M10Stage : std::uint8_t {
    PaletteEffect7,
    HitCounterIncrement,
    SignedModulo20Gate,
    PlayerTransfer,
    NestedScheduler,
    ExitGameplayState,
};

inline constexpr std::array<E2M10Stage, 6> kE2M10TwentiethHitOrder{{
    E2M10Stage::PaletteEffect7,
    E2M10Stage::HitCounterIncrement,
    E2M10Stage::SignedModulo20Gate,
    E2M10Stage::PlayerTransfer,
    E2M10Stage::NestedScheduler,
    E2M10Stage::ExitGameplayState,
}};

constexpr std::uint16_t preClassDamageScalar(
    std::uint16_t objectProjectionCache,
    std::uint16_t projectionBase,
    std::uint16_t rngModulo25) noexcept {
    const auto delta = static_cast<std::uint16_t>(
        objectProjectionCache - projectionBase);
    return static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(delta * 8u) +
        static_cast<std::uint16_t>(rngModulo25 % 25u));
}

constexpr bool hitscanGenerationMatches(
    std::uint32_t guardGeneration,
    std::uint32_t currentGeneration) noexcept {
    return guardGeneration == currentGeneration;
}

constexpr bool projectileProximityAccepts(
    std::int16_t dx,
    std::int16_t dy) noexcept {
    const auto ax = dx < 0 ? -static_cast<std::int32_t>(dx)
                           : static_cast<std::int32_t>(dx);
    const auto ay = dy < 0 ? -static_cast<std::int32_t>(dy)
                           : static_cast<std::int32_t>(dy);
    return ax < 10 && ay < 10;
}

struct PoolCapacityFact {
    std::uint16_t capacity{};
    std::uint16_t sourceMaximum{};
    std::uint16_t reserve{};
};

inline constexpr PoolCapacityFact kWorldObjectPool{350, 323, 27};
inline constexpr PoolCapacityFact kGuardPool{100, 99, 1};
inline constexpr PoolCapacityFact kDoorControllerPool{64, 62, 2};
inline constexpr PoolCapacityFact kSecretPanelPool{32, 32, 0};
inline constexpr PoolCapacityFact kPushPool{12, 11, 1};

inline constexpr std::uint16_t kE2M10DoorControllerCandidates = 60;
inline constexpr std::uint16_t kE2M10DoorControllerReserve = 4;
inline constexpr std::uint16_t kE3M8SecretPanels = 32;

// For a valid 64-world-unit four-VEC panel moving in +2 steps:
// call 32 reaches the endpoint but reasserts state=2; call 33 performs cleanup.
inline constexpr std::uint16_t kSecretPanel64MovementCalls = 32;
inline constexpr std::uint16_t kSecretPanel64CleanupCall = 33;

struct E1M9InitialGroupFacts {
    std::uint8_t frankenstein{};
    std::uint8_t skeleton{};
    std::uint8_t mrsH{};
    std::uint8_t dancers{};
};

inline constexpr E1M9InitialGroupFacts kE1M9InitialGroups{17, 9, 5, 12};

inline constexpr std::uint16_t kE1M1ObjectByteDifferencesDosVsWin = 20;
inline constexpr std::uint16_t kE1M1PlacedGuardCountDos = 33;
inline constexpr std::uint16_t kE1M1PlacedGuardCountWin = 39;

struct ImgAliasBankFact {
    std::uint16_t nonzeroIds{};
    std::uint16_t mismatchedAliasPairs{};
};

inline constexpr std::array<ImgAliasBankFact, 6> kDosWinImgAliasBanks{{
    {150, 0}, // E1 wall
    {167, 0}, // E1 object
    {144, 0}, // E2 wall
    {160, 0}, // E2 object
    {142, 0}, // E3 wall
    {136, 0}, // E3 object
}};

} // namespace n3d::re::v041
