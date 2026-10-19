#pragma once
#include <array>
#include <cstdint>

namespace n3d::re::v053 {

constexpr std::uint8_t dos20HudIdFromDos19(std::uint8_t oldId) noexcept {
    return (oldId >= 4 && oldId <= 8)
        ? static_cast<std::uint8_t>(oldId + 1)
        : oldId;
}

inline constexpr std::uint8_t kDos20InsertedDamageHudId = 4;

struct HudRectWitness {
    std::uint16_t x{};
    std::uint16_t y{};
    std::uint16_t width{};
    std::uint16_t height{};
};

inline constexpr HudRectWitness kDamageHudRegion{256,162,62,36};

constexpr std::array<std::uint8_t,4> damageHudSequence(std::int16_t initial) noexcept {
    // Observed static consequence of DS:417A=3 in the DOS2 HUD path.
    return initial == 3
        ? std::array<std::uint8_t,4>{4,4,4,3}
        : std::array<std::uint8_t,4>{0,0,0,0};
}

struct WeaponPickup36 {
    std::uint8_t mapHighId{};
    std::uint8_t variant{};
    std::uint8_t ownershipBit{};
    std::uint8_t ammoSet{};
    std::uint8_t ammoPool{};
};

inline constexpr std::array<WeaponPickup36,4> kWin110WeaponPickups{{
    {0x25,0,0x01,50,0},
    {0x26,1,0x02,50,1},
    {0x27,2,0x04,50,2},
    {0x28,3,0x08,50,0},
}};

constexpr std::uint8_t ownershipMaskForVariant(std::uint8_t variant) noexcept {
    return variant < 4 ? static_cast<std::uint8_t>(1u << variant) : 0;
}

inline constexpr bool kDosPickupAlgorithmIdenticalToWin16Proven = false;
inline constexpr bool kDamageHudPixelColorClosed = false;

} // namespace n3d::re::v053
