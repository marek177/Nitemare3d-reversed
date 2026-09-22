#pragma once

#include <cstdint>

namespace n3d::recovered {

// Confirmed from NITE3W.EXE reverse engineering and MAP/WALLS cross-checks.
// Keep this header documentary-first until every command/group field is runtime-verified.

enum class TriggerWallClass : std::uint8_t {
    Trigger1 = 0x47,
    Trigger2 = 0x48,
};

constexpr std::uint8_t kWallPropertyTrigger = 0x40;

// Runtime record sizes/capacities recovered from the Win16 executable.
constexpr std::size_t kPanelRecordSize = 22;
constexpr std::size_t kMaxPanels = 32;
constexpr std::size_t kDoorRecordSize = 22;
constexpr std::size_t kMaxDoors = 64;

// CONTROL/PANEL interaction facts already confirmed:
// - object class 0x03 dispatches to the control/panel runtime path
// - panel runtime state uses states 0/1/2
// - activation emits event 0x27
// - panel movement/update step observed as 2
constexpr std::uint8_t kControlObjectClass = 0x03;
constexpr std::uint8_t kControlEvent = 0x27;
constexpr std::uint8_t kPanelStep = 2;

// Remote-door classes are known to live in the door class family and are not
// manually opened by the ordinary USE path. Exact command/group mapping from
// TRIGGER1/2 -> CONTROL -> remote door remains intentionally unresolved here.
// Do not hardcode speculative group IDs until runtime watchpoint evidence exists.

struct TriggerControlAuditState {
    bool triggerWallClassesConfirmed = true;
    bool triggerPropertyBitConfirmed = true;
    bool controlObjectClassConfirmed = true;
    bool panelRuntimeShapeConfirmed = true;
    bool remoteDoorCommandMappingConfirmed = false;
    bool remoteCannonCommandMappingConfirmed = false;
};

} // namespace n3d::recovered
