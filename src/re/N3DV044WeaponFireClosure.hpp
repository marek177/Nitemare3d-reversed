#pragma once

#include <array>
#include <cstdint>

namespace n3d::re::v044 {

enum class Build : std::uint8_t {
    Dos12,
    Dos20,
    Win110,
};

enum class FireReason : std::uint8_t {
    CadenceDenied,
    NoSelectedWeapon,
    Jam,
    ActionNotReady,
    PoolFull,
    NoAmmo,
    ProjectileIssued,
    HitscanIssued,
};

inline constexpr std::array<std::uint8_t,4> kThresholds{2,1,3,1};

constexpr std::uint8_t thresholdFor(Build build, std::uint8_t weapon) noexcept {
    if (weapon < 4) return kThresholds[weapon];
    // Audited initialized overread values at thresholdBase+0xFF.
    switch (build) {
    case Build::Dos12: return 0x33;
    case Build::Dos20: return 0x65;
    case Build::Win110: return 0x03;
    }
    return 0;
}

constexpr std::uint8_t cadenceSlowTick(std::uint8_t counter) noexcept {
    return counter == 0xFF ? 0xFF : static_cast<std::uint8_t>(counter + 1u);
}

struct CadenceResult {
    bool accepted{};
    std::uint8_t nextCounter{};
};

constexpr CadenceResult cadenceAttempt(
    Build build,
    std::uint8_t weapon,
    std::uint8_t counter,
    bool freshPressEdge) noexcept {
    const auto threshold = thresholdFor(build, weapon);
    if (counter < threshold) return {false, counter};

    const bool accepted = weapon == 3 ? true : freshPressEdge;
    return accepted ? CadenceResult{true, 0} : CadenceResult{false, counter};
}

struct FireInput {
    Build build{Build::Dos20};
    std::uint8_t weapon{};
    std::uint8_t counter{};
    bool freshPressEdge{};
    bool jam{};
    std::uint16_t fireMode{}; // 1 hitscan, 2 projectile
    std::uint8_t ammo{};
    std::uint8_t occupiedProjectileSlots{};
    bool ammoBypass{};
};

struct FireResult {
    FireReason reason{FireReason::CadenceDenied};
    std::uint8_t nextCounter{};
    std::uint8_t nextAmmo{};
    std::uint8_t nextOccupiedProjectileSlots{};
    bool shotSuccess{};
    bool ammoHelperCalled{};
};

constexpr FireResult attemptFire(FireInput in) noexcept {
    FireResult out{};
    out.nextCounter = in.counter;
    out.nextAmmo = in.ammo;
    out.nextOccupiedProjectileSlots = in.occupiedProjectileSlots;

    const auto cadence = cadenceAttempt(
        in.build, in.weapon, in.counter, in.freshPressEdge);
    if (!cadence.accepted) {
        out.reason = FireReason::CadenceDenied;
        return out;
    }
    // Original order: accepted cadence resets before entering FIRE dispatcher.
    out.nextCounter = cadence.nextCounter;

    if (in.weapon == 0xFF) {
        out.reason = FireReason::NoSelectedWeapon;
        return out;
    }
    if (in.jam) {
        out.reason = FireReason::Jam;
        return out;
    }
    if (in.fireMode != 1 && in.fireMode != 2) {
        out.reason = FireReason::ActionNotReady;
        return out;
    }

    if (in.fireMode == 2) {
        // Projectile allocator runs before the ammo helper.
        if (in.occupiedProjectileSlots >= 8) {
            out.reason = FireReason::PoolFull;
            return out;
        }
    }

    out.ammoHelperCalled = true;
    if (!in.ammoBypass && in.ammo == 0) {
        out.reason = FireReason::NoAmmo;
        return out;
    }
    if (!in.ammoBypass) {
        out.nextAmmo = static_cast<std::uint8_t>(in.ammo - 1u);
    }

    if (in.fireMode == 2) {
        out.nextOccupiedProjectileSlots =
            static_cast<std::uint8_t>(in.occupiedProjectileSlots + 1u);
        out.reason = FireReason::ProjectileIssued;
    } else {
        out.reason = FireReason::HitscanIssued;
    }
    out.shotSuccess = true;
    return out;
}

constexpr std::uint8_t ammoPoolSelector(std::uint8_t weapon) noexcept {
    // 0 and 3 share the same plasma-cell counter.
    switch (weapon) {
    case 0:
    case 3: return 0;
    case 1: return 1;
    case 2: return 2;
    default: return 0xFF;
    }
}

constexpr bool isAutomaticHeldFireWeapon(std::uint8_t weapon) noexcept {
    return weapon == 3;
}

} // namespace n3d::re::v044
