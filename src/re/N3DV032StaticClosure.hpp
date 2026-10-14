#pragma once

#include <array>
#include <cstdint>
#include <optional>
#include <span>
#include <string_view>
#include <utility>

namespace n3d::re::v032 {

// Closure refers to a precise, build-scoped primitive, not the entire gameplay
// subsystem. No original runtime capture was produced during this pass.
struct ClosureEvidence {
    std::string_view id;
    std::string_view build;
    std::string_view instruction;
    bool localStaticClosed;
    bool originalRuntimeClosed;
};

inline constexpr std::array<ClosureEvidence, 8> kTargetedClosures = {{
    {"push_target_wall_property_gate", "Win16 v1.10", "3:21E0", true, false},
    {"user_sav_hp_offset", "Win16 v1.10", "3:55A7 + save sample", true, false},
    {"guard_pain_and_dracula_writer_sites", "Win16 v1.10", "3:8290/8297 and A16D..A184", true, false},
    {"demo_20_40_input_step_semantics", "Win16 v1.10", "3:9903..993B", true, false},
    {"five_original_executable_file_identities", "DOS 1.0/1.2/1.9/2.0 + Win16", "SHA-256", true, false},
    {"door_retry_four_branch", "DOS v2.0", "1000:0ACF", true, false},
    {"full_projectile_pool_early_return", "Win16 v1.10", "3:9AC2..9ACC", true, false},
    {"secret_panel_endpoint_cleanup", "DOS v2.0", "1000:0BDD..0DCB", true, false}
}};

constexpr const ClosureEvidence* closure(std::string_view id) noexcept {
    for (const auto& row : kTargetedClosures)
        if (row.id == id) return &row;
    return nullptr;
}

constexpr bool canClaimCompleteRuntimeParity(std::string_view id) noexcept {
    const auto* item = closure(id);
    return item != nullptr && item->originalRuntimeClosed;
}

inline constexpr std::uint8_t kWin16PushDestinationForbiddenWallProperty = 0x02;

// Only the destination wall-property gate at 3:21E0. Source record inactivity
// and other preconditions are separate; do not use as the complete PUSH rule.
constexpr bool win16PushPassesWallGate(std::uint8_t property) noexcept {
    return (property & kWin16PushDestinationForbiddenWallProperty) == 0;
}

inline constexpr std::size_t kWin16SaveSlotSize = 0xD6E7;
inline constexpr std::size_t kWin16GameplayBlockOffset = 0x2035;
inline constexpr std::size_t kWin16GameplayBlockLength = 0x5E;
inline constexpr std::size_t kWin16HpBlockOffset = 0x35;
inline constexpr std::size_t kWin16SavedHpOffset =
    kWin16GameplayBlockOffset + kWin16HpBlockOffset;

// An isolated, read-only snapshot query. Does not reconstruct any LOAD side
// effects, clamp health, or treat a historical different-length slot as Win16.
constexpr std::optional<std::uint8_t>
win16SavedHp(std::span<const std::uint8_t> oneSlot) noexcept {
    if (oneSlot.size() < kWin16SaveSlotSize ||
        oneSlot[0] != 0xE7 || oneSlot[1] != 0xD6 ||
        oneSlot[2] != 0 || oneSlot[3] != 0)
        return std::nullopt;
    return oneSlot[kWin16SavedHpOffset];
}

inline constexpr std::uint16_t kWin16DemoDoubleStepBit = 0x0020;
inline constexpr std::uint16_t kWin16DemoUnitStepBit = 0x0040;

struct InputStep {
    std::uint16_t move;
    std::uint16_t turn;
};

// The narrow arithmetic on Win16 3:9903..993B. 'Unit' wins if both bits are
// set. NOT a complete key map, DEMO deserializer or playback scheduler.
constexpr InputStep win16InputStep(std::uint16_t baseMove,
                                   std::uint16_t baseTurn,
                                   std::uint16_t inputMask) noexcept {
    std::uint16_t move = baseMove;
    std::uint16_t turn = baseTurn;
    if (inputMask & kWin16DemoDoubleStepBit) {
        move = static_cast<std::uint16_t>(baseMove * 2u);
        turn = static_cast<std::uint16_t>(baseTurn * 2u);
    }
    if (inputMask & kWin16DemoUnitStepBit) {
        move = 1;
        turn = 1;
    }
    return {move, turn};
}

inline constexpr std::uint16_t kDos20DoorBlockedRetry = 4;
inline constexpr std::uint16_t kDos20DoorRetryWriterOffset = 0x0ACF;
inline constexpr std::uint8_t kWin16ProjectilePoolSlots = 8;
inline constexpr std::uint16_t kWin16FullPoolReturnOffset = 0x9AC7;
inline constexpr std::uint16_t kDos20PanelCompletionStateReset = 0x0C09;
inline constexpr std::uint16_t kDos20PanelFinishMapObjectClear = 0x0DBC;

} // namespace n3d::re::v032
