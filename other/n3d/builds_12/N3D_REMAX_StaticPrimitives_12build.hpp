#pragma once
// Nitemare 3D – instruction-backed local reference primitives (2026-10-16)
// Clean-room reference: NO original bytecode or copyrighted game assets.
// These are local contracts, NOT a reconstructed main loop or full parity proof.
#include <array>
#include <cstddef>
#include <cstdint>

namespace n3d::remax {

enum class DosBuild : unsigned { V10, V11, V12, V15, V17, V19, V20 };

struct DosProfile {
    DosBuild build;
    std::uint32_t unpacked_damage_wrapper;
    std::uint16_t hp_ds_offset;
    std::uint32_t unpacked_lcg_implementation;
    std::uint32_t unpacked_lcg_wrapper;
    std::uint16_t rng_state_ds_offset;
    std::uint8_t hud_hp_dispatch_index;
    std::uint8_t hud_dispatcher_slot_count;
    std::uint8_t direct_rng_callsite_count;
    bool damage_producer_runs_before_protection;
};

inline constexpr std::array<DosProfile, 7> dos_profiles = {{
    {DosBuild::V10, 0x6792, 0x3FDF, 0x14C6C, 0x0F80E, 0x23B2, 6, 24, 22, false},
    {DosBuild::V11, 0x6816, 0x40E5, 0x14DB8, 0x0FA26, 0x24AA, 6, 24, 22, false},
    {DosBuild::V12, 0x6822, 0x40E5, 0x14E18, 0x0FA86, 0x24A6, 5, 23, 22, false},
    {DosBuild::V15, 0x6870, 0x40B5, 0x14E6C, 0x0FAD4, 0x2478, 5, 23, 22, false},
    {DosBuild::V17, 0x690C, 0x40F7, 0x14F08, 0x0FB70, 0x247C, 5, 23, 22, false},
    {DosBuild::V19, 0x6A70, 0x4187, 0x1509C, 0x0FD04, 0x24B6, 5, 23, 22, false},
    {DosBuild::V20, 0x6A70, 0x4189, 0x150D8, 0x0FD40, 0x24B8, 5, 23, 22, true},
}};

constexpr const DosProfile& profile(DosBuild build) {
    return dos_profiles[static_cast<std::size_t>(build)];
}

struct RngStep {
    std::uint32_t next_state;
    std::uint16_t result;
};

// Historical implementation: 16-bit output from upper half, high bit cleared.
// Arithmetic wraps modulo 2^32.
constexpr RngStep rng_next(std::uint32_t prev_state) {
    const std::uint32_t state = prev_state * UINT32_C(0x000343FD) + UINT32_C(0x00269EC3);
    return {state, static_cast<std::uint16_t>((state >> 16U) & 0x7FFFU)};
}

// This cap occurs in the confirmed HP status-dispatch HANDLER, not necessarily
// on every write to HP. Never generalize it to all GAME or LOAD paths.
constexpr std::uint8_t hp_hud_handler_cap(std::uint8_t original_hp) {
    return (original_hp > 100U) ? std::uint8_t{100U} : original_hp;
}

// Only the local incoming-actor-damage wrapper ordering is represented.
// Other hazard/projectile/actor paths are NOT inferred.
constexpr bool damage_producer_is_called(DosBuild build, bool protected_flag,
                                         bool already_in_death_state) {
    return profile(build).damage_producer_runs_before_protection ||
           (!protected_flag && !already_in_death_state);
}

constexpr bool v20_sets_hit_countdown(std::uint8_t computed_damage) {
    return computed_damage != 0;
}

static_assert(rng_next(1U).next_state == (UINT32_C(0x000343FD) + UINT32_C(0x00269EC3)));
static_assert(hp_hud_handler_cap(100)==100 && hp_hud_handler_cap(255)==100);
static_assert(!damage_producer_is_called(DosBuild::V11, true, false));
static_assert(damage_producer_is_called(DosBuild::V20, true, false));
static_assert(profile(DosBuild::V10).hud_hp_dispatch_index==6);
static_assert(profile(DosBuild::V12).hud_hp_dispatch_index==5);

} // namespace n3d::remax
