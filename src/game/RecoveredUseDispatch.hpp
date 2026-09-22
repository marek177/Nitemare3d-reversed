#pragma once

#include <cstdint>

namespace nitemare3d::re {

// Decision layer from NITE3W 1.10 FUN_1010_19d6. The caller supplies the
// already resolved wall property, wall class and object class independently.
// This module selects the handler; it does not guess the handlers' side effects.
enum class UseRoute : std::uint8_t {
    None, Door, LevelExit, Warp, Panel, SpecialWall, Wall04,
    Wall05, Wall06, Wall08, Object26Or27, Push, Object29, ObjectFlagged,
};

constexpr UseRoute useRoute(std::uint8_t wallProperty,
                            std::uint8_t wallClass,
                            std::uint8_t objectClass,
                            std::uint8_t objectProperty = 0) noexcept {
    if ((wallProperty & 0x08) != 0) return UseRoute::Door;
    if (wallClass == 0x09 || wallClass == 0x0A) return UseRoute::LevelExit;
    if (wallClass >= 0x0D && wallClass <= 0x2C) return UseRoute::Warp;
    if (objectClass == 0x03) return UseRoute::Panel;
    switch (wallClass) {
    case 0x03: return UseRoute::SpecialWall;
    case 0x04: return UseRoute::Wall04;
    case 0x05: return UseRoute::Wall05;
    case 0x06: return UseRoute::Wall06;
    case 0x08: return UseRoute::Wall08;
    default: break;
    }
    if (objectClass == 0x26 || objectClass == 0x27) return UseRoute::Object26Or27;
    if (objectClass == 0x28) return UseRoute::Push;
    if (objectClass == 0x29) return UseRoute::Object29;
    return (objectProperty & 0x08) != 0 ? UseRoute::ObjectFlagged : UseRoute::None;
}

enum class DoorUseGate : std::uint8_t {
    Activate, MissingColourKey, MissingIdCard, RemoteOnly, InvalidKeyIndex,
};

// The index is runtime_object+0x01. The EXE reads the masks in this path;
// it does not decrement either mask here. Invalid indices cannot form a bit
// in an eight-bit mask and are reported rather than wrapped or shifted by UB.
constexpr DoorUseGate doorUseGate(std::uint8_t objectClass,
                                  std::uint8_t keyIndex,
                                  std::uint8_t colourKeys,
                                  std::uint8_t idCards) noexcept {
    if (objectClass >= 0x3B && objectClass <= 0x3C) return DoorUseGate::RemoteOnly;
    if (objectClass < 0x33 || objectClass > 0x3A) return DoorUseGate::Activate;
    if (keyIndex >= 8) return DoorUseGate::InvalidKeyIndex;
    const auto bit = static_cast<std::uint8_t>(1u << keyIndex);
    if (objectClass <= 0x38)
        return (colourKeys & bit) != 0 ? DoorUseGate::Activate : DoorUseGate::MissingColourKey;
    return (idCards & bit) != 0 ? DoorUseGate::Activate : DoorUseGate::MissingIdCard;
}

enum class WarpFamily : std::uint8_t {
    None, Paired, Special, ColourKey, Elevator, Reserved,
};

constexpr WarpFamily warpFamily(std::uint8_t wallClass) noexcept {
    if (wallClass >= 0x0D && wallClass <= 0x14) return WarpFamily::Paired;
    if (wallClass >= 0x15 && wallClass <= 0x18) return WarpFamily::Special;
    if (wallClass >= 0x19 && wallClass <= 0x1C) return WarpFamily::ColourKey;
    if (wallClass >= 0x1D && wallClass <= 0x24) return WarpFamily::Elevator;
    if (wallClass >= 0x25 && wallClass <= 0x2C) return WarpFamily::Reserved;
    return WarpFamily::None;
}

// WARP_L1..L4 test bit (wallClass-0x19) in the colour-key mask.
constexpr bool colourWarpUnlocked(std::uint8_t wallClass,
                                  std::uint8_t colourKeys) noexcept {
    return warpFamily(wallClass) == WarpFamily::ColourKey &&
           (colourKeys & (1u << (wallClass - 0x19))) != 0;
}

// WARP_S1 is the forward portal; WARP_S2 displays a message without a
// reverse teleport. The other S-class handlers remain uncharacterised.
constexpr bool otherSidePortalUnlocked(std::uint8_t wallClass,
                                       std::uint8_t pentagrams) noexcept {
    return wallClass == 0x15 && (pentagrams & 0x0F) == 0x0F;
}

} // namespace nitemare3d::re
