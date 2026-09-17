#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d {

// Episode 3 level-specific anchors recovered from MAP.3-derived catalogue data
// and cross-checked against the original Episode 3 hint documentation.
//
// These are evidence-backed coordinates, not guessed runtime script addresses.
// Keep direct video observations separate in docs/VIDEO_AUDIT_E3M3.md.
enum class LevelAnchorKind : std::uint8_t {
    PlayerStart,
    ExplodableBarrier,
    RouteMarker,
    KeyPickup,
    IdCardPickup,
    KeyLock,
    StairWarp
};

enum class AccessToken : std::uint8_t {
    None,
    RedKey,
    GreenKey,
    BlueKey,
    YellowKey,
    RedIdCard,
    YellowIdCard
};

struct LevelAnchor {
    LevelAnchorKind kind{};
    std::uint8_t x{};
    std::uint8_t y{};
    AccessToken token{AccessToken::None};
    std::string_view note{};
};

// Episode 3 / Level 3 (Death or Glory)
// Intended progression from the original hint data:
//   shootable red-door chain -> green key -> chapel/stairs -> red key ->
//   yellow ID card -> red-key section -> blue key -> stairs -> blue-key exit.
inline constexpr std::array<LevelAnchor, 11> Episode3Level3Anchors{{
    {LevelAnchorKind::PlayerStart,       7,  5, AccessToken::None,         "MAP.3 start position, facing north"},
    {LevelAnchorKind::ExplodableBarrier,22, 31, AccessToken::None,         "red door on the initial shootable-door route"},
    {LevelAnchorKind::ExplodableBarrier,25, 40, AccessToken::None,         "red door opening into the fiery-dog section"},
    {LevelAnchorKind::KeyPickup,        36, 30, AccessToken::GreenKey,     "green key"},
    {LevelAnchorKind::RouteMarker,       8, 10, AccessToken::None,         "double doors near the start; return point for chapel route"},
    {LevelAnchorKind::KeyPickup,        27, 17, AccessToken::RedKey,       "red key after chapel/log-stairs section"},
    {LevelAnchorKind::IdCardPickup,     62, 46, AccessToken::YellowIdCard, "yellow ID card in fiery-monkey branch"},
    {LevelAnchorKind::KeyLock,           2, 58, AccessToken::RedKey,       "second explicitly documented red-key door"},
    {LevelAnchorKind::KeyPickup,         4, 62, AccessToken::BlueKey,      "blue key"},
    {LevelAnchorKind::StairWarp,        24, 51, AccessToken::None,         "log stairs; ascend toward final section"},
    {LevelAnchorKind::KeyLock,          59,  5, AccessToken::BlueKey,      "final blue-key door leading to Transportation Booth"},
}};

// Global Episode 3 object IDs confirmed by the MAP/OBJECTS catalogue for E3M3.
inline constexpr std::uint8_t E3M3RedKeyObjectId     = 0x05;
inline constexpr std::uint8_t E3M3GreenKeyObjectId   = 0x06;
inline constexpr std::uint8_t E3M3BlueKeyObjectId    = 0x07;
inline constexpr std::uint8_t E3M3YellowIdCardObjectId = 0x0A;

} // namespace n3d
