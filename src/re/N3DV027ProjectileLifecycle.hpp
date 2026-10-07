#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v027 {

enum class BuildId : std::uint8_t {
    DosV20,
    Win16V110
};

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Partial,
    Open
};

enum class ProjectilePhase : std::uint8_t {
    Allocate,
    Initialize,
    FlyingUpdate,
    Collision,
    ImpactEnter,
    ImpactAnimate,
    Free,
    RenderProject,
    SaveLoad
};

struct ProjectileAnchor {
    BuildId build;
    ProjectilePhase phase;
    bool addressKnown;
    std::uint16_t segment;
    std::uint16_t offset;
    Confidence confidence;
    std::string_view evidence;
};

inline constexpr std::array<ProjectileAnchor, 15> kProjectileAnchors = {{
    {BuildId::DosV20, ProjectilePhase::Allocate, true, 0x0800, 0x7EDE,
     Confidence::Confirmed, "first-free allocation from 8-slot pool"},
    {BuildId::DosV20, ProjectilePhase::Initialize, true, 0x0800, 0x7F96,
     Confidence::Confirmed, "secondary projectile initialization"},
    {BuildId::DosV20, ProjectilePhase::FlyingUpdate, true, 0x0800, 0x8142,
     Confidence::Confirmed, "movement/collision integration"},
    {BuildId::DosV20, ProjectilePhase::Collision, true, 0x0800, 0x8142,
     Confidence::Confirmed, "wall/guard collision path within movement update"},
    {BuildId::DosV20, ProjectilePhase::ImpactEnter, true, 0x0800, 0x8142,
     Confidence::Confirmed, "active state transitions 1->2 on collision"},
    {BuildId::DosV20, ProjectilePhase::ImpactAnimate, true, 0x0800, 0x8230,
     Confidence::Strong, "scheduler iterates slots; exact per-state animation sub-branch not independently split"},
    {BuildId::DosV20, ProjectilePhase::RenderProject, true, 0x0800, 0xB2D4,
     Confidence::Confirmed, "projectile render/projection submit"},

    {BuildId::Win16V110, ProjectilePhase::Allocate, true, 0x1010, 0x9AAC,
     Confidence::Confirmed, "find first free slot and initialize projectile"},
    {BuildId::Win16V110, ProjectilePhase::Initialize, true, 0x1010, 0xE516,
     Confidence::Confirmed, "direction/Bresenham movement initialization"},
    {BuildId::Win16V110, ProjectilePhase::FlyingUpdate, true, 0x1010, 0x9D30,
     Confidence::Confirmed, "small-step Bresenham movement"},
    {BuildId::Win16V110, ProjectilePhase::Collision, true, 0x1010, 0x9B64,
     Confidence::Confirmed, "cell/guard/wall collision test after substep"},
    {BuildId::Win16V110, ProjectilePhase::ImpactAnimate, true, 0x1010, 0x9E20,
     Confidence::Confirmed, "flight/impact animation and state 2->0 completion"},
    {BuildId::Win16V110, ProjectilePhase::RenderProject, true, 0x1010, 0xCC7C,
     Confidence::Confirmed, "embedded OBJECT projection and cache write"},
    {BuildId::Win16V110, ProjectilePhase::SaveLoad, true, 0x1010, 0x5466,
     Confidence::Confirmed, "save 336-byte projectile pool"},
    {BuildId::Win16V110, ProjectilePhase::SaveLoad, true, 0x1010, 0x574C,
     Confidence::Confirmed, "load 336-byte projectile pool"}
}};

struct ProjectileInvariant {
    std::string_view name;
    Confidence confidence;
    std::string_view evidence;
};

inline constexpr std::array<ProjectileInvariant, 9> kProjectileInvariants = {{
    {"pool_capacity_8", Confidence::Confirmed, "8 projectile slots"},
    {"slot_stride_42", Confidence::Confirmed, "0x2A bytes per slot"},
    {"lifecycle_0_1_2_0", Confidence::Confirmed, "Free->Flying->Impact->Free"},
    {"embedded_object_28_bytes", Confidence::Confirmed, "OBJECT begins at +0x0E"},
    {"guard_hit_tolerance_9", Confidence::Confirmed, "abs(dx)<10 && abs(dy)<10"},
    {"impact_sets_flag_0x10", Confidence::Confirmed, "impact sets embedded OBJECT flag bit 0x10"},
    {"new_projectile_moves_next_tick", Confidence::Strong, "projectile update precedes FIRE allocation in audited scheduler order"},
    {"pool_full_preserves_ammo", Confidence::Strong, "Win16 static path checks free slot before ammo helper"},
    {"stale_projection_cache_affects_damage", Confidence::Strong, "embedded OBJECT +0x18/+0x19 may survive slot reuse and feed damage"}
}};

constexpr const ProjectileAnchor* anchorFor(BuildId build,
                                            ProjectilePhase phase) noexcept {
    for (const auto& item : kProjectileAnchors) {
        if (item.build == build && item.phase == phase) {
            return &item;
        }
    }
    return nullptr;
}

constexpr bool hasConfirmedAnchor(BuildId build,
                                  ProjectilePhase phase) noexcept {
    const auto* item = anchorFor(build, phase);
    return item != nullptr && item->confidence == Confidence::Confirmed;
}

constexpr const ProjectileInvariant* invariant(std::string_view name) noexcept {
    for (const auto& item : kProjectileInvariants) {
        if (item.name == name) {
            return &item;
        }
    }
    return nullptr;
}

constexpr bool implementationSafe(std::string_view name) noexcept {
    const auto* item = invariant(name);
    return item != nullptr && item->confidence == Confidence::Confirmed;
}

} // namespace n3d::re::v027
