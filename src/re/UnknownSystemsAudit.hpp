#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

// Machine-readable index of remaining reverse-engineering targets. This keeps
// evidence levels and next observations shared by code/tests and Markdown.
namespace nitemare3d::re {

enum class Evidence : std::uint8_t {
    VerifiedExe, VerifiedData, VerifiedSaveLayout, Behavioural,
    Inferred, Partial, Todo,
};

enum class AuditArea : std::uint8_t {
    GuardAi, SequenceEvents, SpawnDespawn, CollisionFlags, Projectile,
    Damage, DeathScoreMorph, Difficulty, WallDispatcher, Renderer, RngTick,
    MapHeader, Resources, Bsf, NeRelocations, HiddenContent,
};

struct AuditTarget {
    AuditArea area;
    Evidence evidence;
    const char* name;
    const char* anchor;
    const char* nextObservation;
};

inline constexpr std::array<AuditTarget, 28> kUnknownSystemTargets = {{
    {AuditArea::GuardAi, Evidence::Partial, "GUARD strategy/state/nextState", "GUARD +0A/+0B/+0C; states 00..15; pain 15h", "map reads/writes, timer, LOS, attack and transitions"},
    {AuditArea::GuardAi, Evidence::Partial, "GUARD26..30", "classes beyond scored switch", "trace creation, class changes, projectile and scripted uses"},
    {AuditArea::SequenceEvents, Evidence::Todo, "sequence-definition events", "seqdef/animation references", "find duration, sound, attack, movement and next-sequence writes"},
    {AuditArea::SequenceEvents, Evidence::Partial, "animated-wall timing/completion", "known multi-frame wall resources; VEC timer/animation fields", "prove tick delay, loop/one-shot completion and collision cleanup"},
    {AuditArea::SpawnDespawn, Evidence::Partial, "runtime spawn/despawn", "OBJECT count 7E58; GUARD count 7E5E", "classify load, trigger, drop, projectile and morph callers"},
    {AuditArea::CollisionFlags, Evidence::VerifiedExe, "wall property preprocessing", "wall props 7E94: 01 geometry, 02 collision, 04 hard block, 08 door, 10 explodable, 40 trigger", "finish exact semantic label for bit 01 and cross-check all class ranges"},
    {AuditArea::CollisionFlags, Evidence::Partial, "object/player/projectile collision matrix", "property tables 7E94/7F94", "separate player, guard, projectile and object masks"},
    {AuditArea::Projectile, Evidence::Todo, "projectile runtime class", "enemy attack to damage chain", "prove record type and lifetime/owner"},
    {AuditArea::Damage, Evidence::Partial, "damage dispatcher", "weapon/class transforms; strength +10", "recover remaining RNG/resistance/class bindings"},
    {AuditArea::DeathScoreMorph, Evidence::Partial, "death/score/morph chain", "score switch classes 08..20; Dracula score 0", "trace all HP<=0 paths through sound, drop, morph and removal"},
    {AuditArea::Difficulty, Evidence::VerifiedExe, "difficulty fan-out", "global 4C14 values 0/1/2; independent damage and GUARD timing paths", "audit any remaining probability/cadence consumers"},
    {AuditArea::WallDispatcher, Evidence::Partial, "USE/wall dispatcher remainder", "USE 0200; door first; LEVEL_UP 09/0A; WARP 0D..2C; object class 03 panel", "close special classes 03-06/08 and object classes 26-29"},
    {AuditArea::WallDispatcher, Evidence::Partial, "TRIGGER1/2 -> CONTROL -> remote outputs", "classes 47/48; wall property 40; remote door classes already identified", "recover exact command/group mapping for remote doors and cannons"},
    {AuditArea::WallDispatcher, Evidence::Todo, "ONE_SHOT activation", "original ONE_SHOT class/resource; projectile/USE/proximity candidates", "prove trigger source, animation and final removal semantics"},
    {AuditArea::WallDispatcher, Evidence::Todo, "SPECIAL1 dispatch", "SPECIAL1 wall family; fuse-box/chalkboard behaviour candidates", "map class/variant to trigger, sound, animation and final texture"},
    {AuditArea::WallDispatcher, Evidence::Todo, "E2M4 wall 37", "map cell (61,54), undefined wall candidate", "compare WALLS.2, handler domain and runtime behavior"},
    {AuditArea::Renderer, Evidence::Partial, "VEC/VECLIST/owner pipeline", "VEC 28B; lists 333; owner 53FE; occlusion 58FE", "resolve conflict math, texture-U and animation fields"},
    {AuditArea::Renderer, Evidence::Todo, "VEC flags 04/08/10", "VEC +05", "collect TEST/AND/OR/CMP domains and calls"},
    {AuditArea::RngTick, Evidence::Todo, "RNG and main tick", "demo 8B records; timers", "locate generator/seed and deterministic replay order"},
    {AuditArea::MapHeader, Evidence::Partial, "MAP 514-byte header", "31 supplied levels; 8192-byte payload", "diff offsets and correlate metadata/spawns/flags"},
    {AuditArea::Resources, Evidence::Partial, "UIF/SND/FLI edge cases", "UIF 0..31; SND directory; FLI deltas", "xref reserved slots and map events to resources"},
    {AuditArea::Bsf, Evidence::Todo, "NITE3D.BSF consumer", "six known xrefs across versions", "recover read size/stride/compare and mutation behavior"},
    {AuditArea::NeRelocations, Evidence::Partial, "Win16 NE relocations", "NITE3W has 10 logical segments", "classify far calls, imports and far data pointers"},
    {AuditArea::HiddenContent, Evidence::Todo, "defined/placed/referenced/executed sets", "IMG, OBJECTS, WALLS, SND, MAP", "report unused assets, orphan handlers and unreachable states"},
    {AuditArea::HiddenContent, Evidence::Partial, "runtime/save 336-byte block", "USER.SAV offset C403, 336 bytes", "diff before/after push, door, death and trigger events"},
    {AuditArea::Resources, Evidence::Partial, "global 7E60 / save D6E5", "runtime/save mirrored word", "enumerate initial value, writes, arithmetic and consumers"},
    {AuditArea::GuardAi, Evidence::VerifiedExe, "guard physical record", "base 93AE, stride 26, capacity 100", "finish tail-field semantics without changing record size"},
    {AuditArea::Renderer, Evidence::VerifiedExe, "renderer capacities", "vectors 1000; spans 50x20; sprites 100x18", "validate alternate backend and overflow boundaries"},
}};

constexpr std::size_t countByEvidence(Evidence wanted) noexcept {
    std::size_t count = 0;
    for (const auto& target : kUnknownSystemTargets)
        if (target.evidence == wanted) ++count;
    return count;
}

} // namespace nitemare3d::re
