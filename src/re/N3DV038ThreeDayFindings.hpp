#pragma once

#include <cstdint>

namespace n3d::re::v038 {

enum class EvidenceLevel : std::uint8_t {
    OriginalStaticProven,
    IsolatedModelTested,
    RuntimeOpen,
};

struct JoystickCalibrationResult {
    bool divideError{};
    std::uint16_t rawQuotient{};
    std::uint16_t storedV18{};
    std::uint16_t storedV110{};
};

// Bounded model of the Win16 recalibration branch only. It does not model the
// cached/shortcut path or prove that sensitivity==0 is reachable from the UI.
constexpr JoystickCalibrationResult joystickCalibration(
    std::uint16_t delta,
    std::uint8_t sensitivity) noexcept {
    if (sensitivity == 0) {
        return {true, 0, 0, 0};
    }

    const auto raw = static_cast<std::uint16_t>(delta / sensitivity);
    const auto signedRaw = static_cast<std::int16_t>(raw);
    const auto v110 = static_cast<std::uint16_t>(signedRaw > 0 ? raw : 1u);
    return {false, raw, raw, v110};
}

struct MagicEyeNoiseBudget {
    bool divideError{};
    std::uint16_t dots{};
    std::uint32_t directRngCalls{};
};

// Exact local arithmetic for the audited automap case-7 path for charge 0..15.
// The caller only enters this path for charge<=15. Charge==0 would divide by 0.
constexpr MagicEyeNoiseBudget magicEyeNoiseBudget(std::uint8_t charge) noexcept {
    if (charge == 0) {
        return {true, 0, 0};
    }
    if (charge > 15) {
        return {false, 0, 0};
    }

    const std::uint16_t cube = static_cast<std::uint16_t>(
        static_cast<std::uint16_t>(charge) *
        static_cast<std::uint16_t>(charge) *
        static_cast<std::uint16_t>(charge));
    const auto dots = static_cast<std::uint16_t>(500u / cube);
    return {false, dots, static_cast<std::uint32_t>(dots) * 2u};
}

constexpr bool doorState4BlocksNormalUse(std::uint8_t state) noexcept {
    return state == 4;
}

struct DoorStepResult {
    std::uint16_t coordinate{};
    std::uint8_t state{};
    bool completed{};
    bool cleanup{};
};

// Bounded single-axis illustration of the 18-byte door controller opening path:
// move by +2, then test equality in the same call.
constexpr DoorStepResult normalDoorOpeningStep(
    std::uint16_t coordinate,
    std::uint16_t target,
    std::uint8_t state = 2) noexcept {
    if (state != 2) {
        return {coordinate, state, false, false};
    }
    if (coordinate != target) {
        coordinate = static_cast<std::uint16_t>(coordinate + 2u);
    }
    if (coordinate == target) {
        return {coordinate, 0, true, false};
    }
    return {coordinate, 2, false, false};
}

// Bounded single-axis illustration of the 14-byte four-VEC record. A move keeps
// state=2; cleanup is reached only on a later call that performs no movement.
constexpr DoorStepResult fourVectorPanelStep(
    std::uint16_t coordinate,
    std::uint16_t target,
    std::uint8_t state = 2) noexcept {
    if (state != 2) {
        return {coordinate, state, false, false};
    }
    if (static_cast<std::int16_t>(coordinate) < static_cast<std::int16_t>(target)) {
        coordinate = static_cast<std::uint16_t>(coordinate + 2u);
        return {coordinate, 2, false, false};
    }
    return {coordinate, 0, true, true};
}

constexpr std::int16_t class16PlayerHitDamage(
    std::uint16_t episode,
    std::uint16_t difficulty) noexcept {
    std::int16_t damage = episode == 3 ? 3 : 0;
    if (difficulty == 2) {
        damage = static_cast<std::int16_t>(damage >> 1);
    } else if (difficulty == 0) {
        damage = static_cast<std::int16_t>(damage + damage);
    }
    return damage;
}

constexpr std::int16_t class16ToPlayerAmount(
    std::uint16_t episode,
    std::uint8_t storyStage,
    std::uint16_t difficulty) noexcept {
    std::int16_t amount = (episode == 3 || storyStage != 0) ? 100 : 33;
    if (difficulty == 2) {
        amount = static_cast<std::int16_t>(amount * 2);
    } else if (difficulty == 0) {
        amount = static_cast<std::int16_t>(amount >> 1);
    }
    return amount;
}

constexpr bool signedEvery20AfterIncrement(std::uint16_t before) noexcept {
    const auto after = static_cast<std::uint16_t>(before + 1u);
    const auto signedAfter = static_cast<std::int16_t>(after);
    return static_cast<std::int16_t>(signedAfter % 20) == 0;
}

constexpr std::uint16_t low16Average(
    std::uint32_t elapsed,
    std::uint16_t samples) noexcept {
    if (samples == 0) {
        return 0;
    }
    return static_cast<std::uint16_t>(elapsed / samples);
}

struct ProjectileCallbackView {
    std::int16_t storedX{};
    std::int16_t storedY{};
    std::int16_t updatedError{};
    std::uint8_t storedState{};
};

// Captures the audited mixed-generation invariant at collision callback entry:
// stored X/Y and flying state are still pre-commit, while the line-error field
// can already contain the substep-updated value.
constexpr ProjectileCallbackView projectileCallbackView(
    std::int16_t storedX,
    std::int16_t storedY,
    std::int16_t updatedError,
    std::uint8_t storedState = 1) noexcept {
    return {storedX, storedY, updatedError, storedState};
}

inline constexpr std::uint16_t kDos12GraphicsSaveSegmentLink = 0x1BDCu;
inline constexpr std::uint16_t kDos20GraphicsSaveSegmentLink = 0x1C08u;

} // namespace n3d::re::v038
