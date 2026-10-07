#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v023 {

enum class BuildId : std::uint8_t {
    DosV20,
    Win16V110,
    Unknown
};

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Open
};

enum class BehaviorId : std::uint16_t {
    FindSpecialWallAt,
    FindObjectReferenceByTile,
    BuildPairedWallRuntimeTable,
    SetAndPropagatePairedWallState,
    HandlePlayerUse,
    UpdateDoorAutoClose,
    TickPairedWallMotion,
    ActivateMapObject,
    TickMovingMapObjects,

    GuardStateDispatch,
    GuardPainState,
    HudDispatch,
    AutomapDispatch,
    MenuDispatch
};

struct SegmentedAddress {
    std::uint16_t segment;
    std::uint16_t offset;
};

struct BuildSymbol {
    BehaviorId behavior;
    BuildId build;
    bool present;
    SegmentedAddress address;
    Confidence confidence;
    std::string_view evidence;
};

inline constexpr std::array<BuildSymbol, 19> kBuildSymbols = {{
    {BehaviorId::FindSpecialWallAt, BuildId::DosV20, true,
     {0x1000, 0x0052}, Confidence::Confirmed,
     "DOS v2.0 core anchor"},
    {BehaviorId::FindObjectReferenceByTile, BuildId::DosV20, true,
     {0x1000, 0x00A4}, Confidence::Confirmed,
     "DOS v2.0 core anchor"},
    {BehaviorId::BuildPairedWallRuntimeTable, BuildId::DosV20, true,
     {0x1000, 0x0212}, Confidence::Confirmed,
     "DOS v2.0 paired-wall table construction"},
    {BehaviorId::SetAndPropagatePairedWallState, BuildId::DosV20, true,
     {0x1000, 0x0598}, Confidence::Confirmed,
     "DOS v2.0 paired-wall state propagation"},
    {BehaviorId::HandlePlayerUse, BuildId::DosV20, true,
     {0x1000, 0x0704}, Confidence::Confirmed,
     "DOS v2.0 USE dispatcher"},
    {BehaviorId::UpdateDoorAutoClose, BuildId::DosV20, true,
     {0x1000, 0x0A40}, Confidence::Confirmed,
     "DOS v2.0 door auto-close"},
    {BehaviorId::TickPairedWallMotion, BuildId::DosV20, true,
     {0x1000, 0x0C5F}, Confidence::Confirmed,
     "DOS v2.0 paired-wall motion"},
    {BehaviorId::ActivateMapObject, BuildId::DosV20, true,
     {0x1000, 0x0DF8}, Confidence::Confirmed,
     "DOS v2.0 map-object activation"},
    {BehaviorId::TickMovingMapObjects, BuildId::DosV20, true,
     {0x1000, 0x0E50}, Confidence::Open,
     "candidate runtime identity retained open pending mutation-order proof"},

    {BehaviorId::GuardStateDispatch, BuildId::Win16V110, true,
     {0x0003, 0x7B55}, Confidence::Confirmed,
     "Win16 v1.10 22-state GUARD dispatcher"},
    {BehaviorId::GuardPainState, BuildId::Win16V110, true,
     {0x0003, 0x807E}, Confidence::Confirmed,
     "Win16 v1.10 state 0x15 pain-return handler"},
    {BehaviorId::HudDispatch, BuildId::Win16V110, true,
     {0x0003, 0xA3B6}, Confidence::Confirmed,
     "Win16 HUD dispatcher"},
    {BehaviorId::AutomapDispatch, BuildId::Win16V110, true,
     {0x0003, 0xB1A4}, Confidence::Confirmed,
     "Win16 automap/right-panel dispatcher"},
    {BehaviorId::MenuDispatch, BuildId::Win16V110, true,
     {0x0004, 0x27DE}, Confidence::Confirmed,
     "Win16 menu/save dispatcher"},

    // Explicit unresolved cross-build entries. Missing addresses are not guessed.
    {BehaviorId::HandlePlayerUse, BuildId::Win16V110, false,
     {0, 0}, Confidence::Open,
     "Win16 equivalent not yet paired strongly enough"},
    {BehaviorId::TickPairedWallMotion, BuildId::Win16V110, false,
     {0, 0}, Confidence::Open,
     "Win16 equivalent not yet paired strongly enough"},
    {BehaviorId::GuardStateDispatch, BuildId::DosV20, true,
     {0x1000, 0x59F0}, Confidence::Strong,
     "DOS v2.0 state dispatcher; behavior pairing strong, exact semantic parity pending"},
    {BehaviorId::GuardPainState, BuildId::DosV20, false,
     {0, 0}, Confidence::Open,
     "DOS pain-state equivalent not promoted without a direct pair"},
    {BehaviorId::HudDispatch, BuildId::DosV20, false,
     {0, 0}, Confidence::Open,
     "DOS HUD equivalent not paired in this registry"}
}};

constexpr const BuildSymbol* symbolFor(BehaviorId behavior,
                                       BuildId build) noexcept {
    for (const auto& symbol : kBuildSymbols) {
        if (symbol.behavior == behavior && symbol.build == build) {
            return &symbol;
        }
    }
    return nullptr;
}

constexpr bool hasAddress(BehaviorId behavior, BuildId build) noexcept {
    const auto* symbol = symbolFor(behavior, build);
    return symbol != nullptr && symbol->present;
}

constexpr bool isConfirmedPair(BehaviorId behavior) noexcept {
    const auto* dos = symbolFor(behavior, BuildId::DosV20);
    const auto* win = symbolFor(behavior, BuildId::Win16V110);

    return dos != nullptr && win != nullptr &&
           dos->present && win->present &&
           dos->confidence == Confidence::Confirmed &&
           win->confidence == Confidence::Confirmed;
}

constexpr bool needsCrossBuildPairing(BehaviorId behavior) noexcept {
    const auto* dos = symbolFor(behavior, BuildId::DosV20);
    const auto* win = symbolFor(behavior, BuildId::Win16V110);

    const bool dosKnown = dos != nullptr && dos->present;
    const bool winKnown = win != nullptr && win->present;
    return dosKnown != winKnown ||
           (dosKnown && winKnown && !isConfirmedPair(behavior));
}

}  // namespace n3d::re::v023
