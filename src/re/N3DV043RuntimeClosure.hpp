#pragma once

#include <array>
#include <cstdint>

namespace n3d::re::v043 {

enum class GuardInitFamily : std::uint8_t { Old19, New26 };

struct GuardInitState {
    std::uint8_t strategy{};
    std::uint8_t state{};
    std::uint8_t nextState{};
    std::uint8_t perceptionMode{};
};

// Bounded constructor/initializer contract from the 12-build v0.81 audit.
constexpr GuardInitState guardInit(
    GuardInitFamily family,
    std::uint8_t objectClass,
    bool movementOverride) noexcept {
    GuardInitState g{0, 7, 2, 1};

    if (objectClass == 0x15 || objectClass == 0x16) {
        g.nextState = 0;
    } else if (objectClass == 0x19) {
        g.strategy = 4;
        g.state = 0x0E;
    } else if (objectClass == 0x21 && family == GuardInitFamily::New26) {
        g.state = 0;
        g.nextState = 0;
    }

    if (movementOverride) {
        g.state = 8;
    }
    return g;
}

struct WakeResult {
    bool accepted{};
    bool rngConsumed{};
    std::uint8_t timer{};
    std::uint8_t state{};
};

constexpr WakeResult areaWake(
    std::uint8_t strategy,
    std::uint8_t guardArea,
    std::uint8_t playerArea,
    std::uint8_t state,
    bool areaLatchUnused,
    std::uint16_t rng15) noexcept {
    const bool eligible =
        areaLatchUnused &&
        strategy == 0 &&
        guardArea == playerArea &&
        (state == 7 || state == 8);

    if (!eligible) return {false, false, 0, state};
    return {true, true, static_cast<std::uint8_t>(rng15 % 8u), 1};
}

constexpr std::int16_t damageBaseFromDistance(std::int16_t distance) noexcept {
    if (distance <= 0) return 100;
    return static_cast<std::int16_t>(100 / distance);
}

constexpr std::int16_t applyDifficulty(
    std::int16_t value,
    std::uint16_t difficulty) noexcept {
    if (difficulty == 2) return static_cast<std::int16_t>(value * 2);
    if (difficulty == 0) return static_cast<std::int16_t>(value >> 1);
    return value;
}

// Complete local v0.80 contact-damage switch, bounded to the audited calculator.
constexpr std::int16_t guardContactDamage(
    std::uint8_t objectClass,
    std::int16_t distance,
    std::uint16_t episode,
    std::uint8_t eventLatch,
    std::uint16_t difficulty,
    std::uint16_t rng15) noexcept {
    const auto base = damageBaseFromDistance(distance);
    std::int16_t value{};

    switch (objectClass) {
    case 0x08:
        value = static_cast<std::int16_t>(rng15 & 7u);
        break;
    case 0x09:
    case 0x0A:
        value = static_cast<std::int16_t>(rng15 & 15u);
        break;
    case 0x0B:
        value = static_cast<std::int16_t>(base >> 2);
        break;
    case 0x0C:
    case 0x1D:
    case 0x1E:
        value = base;
        break;
    case 0x11:
    case 0x12:
    case 0x13:
    case 0x14:
        value = static_cast<std::int16_t>(rng15 & 31u);
        break;
    case 0x16:
        value = (episode != 3 && eventLatch == 0) ? 33 : 100;
        break;
    case 0x19:
        value = 100;
        break;
    default:
        value = static_cast<std::int16_t>(base >> 1);
        break;
    }

    return applyDifficulty(value, difficulty);
}

struct NaturalDoorUseObservation {
    std::uint8_t recordIndex{};
    std::uint16_t stateBefore{};
    std::uint16_t stateAfter{};
    std::uint16_t flagBefore{};
    std::uint16_t flagAfter{};
};

inline constexpr NaturalDoorUseObservation kDos12E1M1DoorUse{
    8, 1, 2, 0, 1
};

enum class ShutdownStage : std::uint8_t {
    SetVideoMode3,
    MusicStopDispatch,
    ProgramPitDivisor65535,
    RestoreInt08,
    RestoreInt63,
    ResetMouse,
    RestoreInt09,
    DisableRtcPeriodic,
    RestoreInt70,
    GameCacheXmsUnlock,
    GameCacheXmsFree,
    ExitBsfReadDecodePrint,
    CrtCallback,
    RestoreInt00,
    DosExit0,
};

inline constexpr std::array<ShutdownStage, 15> kObservedNormalDosShutdown{{
    ShutdownStage::SetVideoMode3,
    ShutdownStage::MusicStopDispatch,
    ShutdownStage::ProgramPitDivisor65535,
    ShutdownStage::RestoreInt08,
    ShutdownStage::RestoreInt63,
    ShutdownStage::ResetMouse,
    ShutdownStage::RestoreInt09,
    ShutdownStage::DisableRtcPeriodic,
    ShutdownStage::RestoreInt70,
    ShutdownStage::GameCacheXmsUnlock,
    ShutdownStage::GameCacheXmsFree,
    ShutdownStage::ExitBsfReadDecodePrint,
    ShutdownStage::CrtCallback,
    ShutdownStage::RestoreInt00,
    ShutdownStage::DosExit0,
}};

inline constexpr std::uint16_t kPitDivisorObserved = 0xFFFF;
inline constexpr std::uint16_t kExitBsfDecodedBytes = 474;
inline constexpr std::uint16_t kExitBsfXorPeriod = 52;
inline constexpr std::uint16_t kExitBsfPrintedBytes = 473;
inline constexpr std::uint8_t kNormalDosExitCode = 0;
inline constexpr std::uint8_t kLateBsfOpenErrorExitCode = 1;

} // namespace n3d::re::v043
