#pragma once

#include <cstdint>

namespace nitemare3d::game {

// Runtime inventory globals recovered from NITE3W.EXE.
// Only addresses and bit relationships directly supported by executable/data
// analysis are promoted here. Human-readable color names are used where they
// are already bound by in-game text and WARP/key-gate behavior.
inline constexpr std::uintptr_t kColoredKeyMaskAddress = 0x4C28;
inline constexpr std::uintptr_t kIdCardMaskAddress    = 0x4C29;
inline constexpr std::uintptr_t kPentagramMaskAddress = 0x4C45;

// The colored-key and ID-card globals are bit masks. Exact per-bit color/card
// ordering should remain data-driven until every door class has been bound to
// a displayed lock message in the same executable build.
using InventoryMask = std::uint8_t;

constexpr bool hasInventoryBit(InventoryMask mask, std::uint8_t bit) noexcept {
    return (mask & static_cast<InventoryMask>(1u << bit)) != 0;
}

constexpr void grantInventoryBit(InventoryMask& mask, std::uint8_t bit) noexcept {
    mask = static_cast<InventoryMask>(mask | static_cast<InventoryMask>(1u << bit));
}

// WARP_S1 uses all four pentagrams. This bit ordering is directly established
// by the reconstructed missing-item text builder.
enum class PentagramBit : std::uint8_t {
    Red    = 0,
    Green  = 1,
    Blue   = 2,
    Yellow = 3,
};

inline constexpr InventoryMask kAllPentagramsMask = 0x0F;

constexpr bool hasPentagram(InventoryMask mask, PentagramBit bit) noexcept {
    return hasInventoryBit(mask, static_cast<std::uint8_t>(bit));
}

constexpr bool hasAllPentagrams(InventoryMask mask) noexcept {
    return (mask & kAllPentagramsMask) == kAllPentagramsMask;
}

// WARP_L1..L4 share one generic key-gate routine. The wall class determines
// which key bit is required; keep the relation explicit rather than cloning
// four separate scripts.
inline constexpr std::uint8_t kWarpKeyClassBase = 0x19;
inline constexpr std::uint8_t kWarpKeyClassLast = 0x1C;

constexpr std::uint8_t warpKeyBitForClass(std::uint8_t wallClass) noexcept {
    return static_cast<std::uint8_t>(wallClass - kWarpKeyClassBase);
}

constexpr bool isWarpKeyClass(std::uint8_t wallClass) noexcept {
    return wallClass >= kWarpKeyClassBase && wallClass <= kWarpKeyClassLast;
}

} // namespace nitemare3d::game
