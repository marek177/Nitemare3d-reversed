#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v024 {

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

enum class TransitionKind : std::uint8_t {
    None,
    ToFixedState,
    ToNextState,
    Conditional,
    MultiTarget,
    Unknown
};

struct GuardStateEvidence {
    std::uint8_t state;
    BuildId build;
    bool handlerKnown;
    std::uint16_t segment;
    std::uint16_t handlerOffset;
    std::string_view behavior;
    TransitionKind transitionKind;
    std::uint8_t fixedTarget;
    Confidence controlFlowConfidence;
    Confidence semanticConfidence;
};

inline constexpr std::array<GuardStateEvidence, 22> kWin16V110States = {{
    {0x00, BuildId::Win16V110, true, 0x0003, 0x7BA2,
     "animation/timer; on completion state=nextstate",
     TransitionKind::ToNextState, 0x00, Confidence::Strong, Confidence::Strong},

    {0x01, BuildId::Win16V110, true, 0x0003, 0x7BE0,
     "countdown timer; then state 0x02",
     TransitionKind::ToFixedState, 0x02, Confidence::Strong, Confidence::Strong},

    {0x02, BuildId::Win16V110, true, 0x0003, 0x7BFA,
     "active AI/animation path with sound-type-3 call",
     TransitionKind::Unknown, 0x00, Confidence::Partial, Confidence::Partial},

    {0x03, BuildId::Win16V110, true, 0x0003, 0x7C3C,
     "detection/transition branch",
     TransitionKind::Conditional, 0x00, Confidence::Partial, Confidence::Partial},

    {0x04, BuildId::Win16V110, true, 0x0003, 0x7C86,
     "alternate detection/attack branch",
     TransitionKind::Conditional, 0x00, Confidence::Partial, Confidence::Partial},

    {0x05, BuildId::Win16V110, true, 0x0003, 0x7CE4,
     "helper transition branch",
     TransitionKind::Unknown, 0x00, Confidence::Partial, Confidence::Partial},

    {0x06, BuildId::Win16V110, true, 0x0003, 0x7CEC,
     "movement + timer; then state 0x03",
     TransitionKind::ToFixedState, 0x03, Confidence::Strong, Confidence::Partial},

    {0x07, BuildId::Win16V110, true, 0x0003, 0x7D2A,
     "active AI; strategy 3 has separate branch",
     TransitionKind::Conditional, 0x00, Confidence::Partial, Confidence::Partial},

    {0x08, BuildId::Win16V110, true, 0x0003, 0x7D7E,
     "movement/AI; can enter state 0x02",
     TransitionKind::Conditional, 0x02, Confidence::Partial, Confidence::Partial},

    {0x09, BuildId::Win16V110, true, 0x0003, 0x7DEC,
     "special/collision/action path",
     TransitionKind::Unknown, 0x00, Confidence::Partial, Confidence::Partial},

    {0x0A, BuildId::Win16V110, true, 0x0003, 0x80A4,
     "no local action in dispatcher",
     TransitionKind::None, 0x00, Confidence::Strong, Confidence::Partial},

    {0x0B, BuildId::Win16V110, true, 0x0003, 0x80A4,
     "no local action in dispatcher",
     TransitionKind::None, 0x00, Confidence::Strong, Confidence::Partial},

    {0x0C, BuildId::Win16V110, true, 0x0003, 0x7E54,
     "shared handler with state 0x0D",
     TransitionKind::Unknown, 0x00, Confidence::Partial, Confidence::Partial},

    {0x0D, BuildId::Win16V110, true, 0x0003, 0x7E54,
     "shared handler with state 0x0C",
     TransitionKind::Unknown, 0x00, Confidence::Partial, Confidence::Partial},

    {0x0E, BuildId::Win16V110, true, 0x0003, 0x7E6C,
     "conditional transition to 0x0F",
     TransitionKind::Conditional, 0x0F, Confidence::Strong, Confidence::Partial},

    {0x0F, BuildId::Win16V110, true, 0x0003, 0x7E9E,
     "timer/action; transition to 0x10 or back to 0x0E",
     TransitionKind::MultiTarget, 0x00, Confidence::Strong, Confidence::Partial},

    {0x10, BuildId::Win16V110, true, 0x0003, 0x7F26,
     "timer; then return to 0x0F",
     TransitionKind::ToFixedState, 0x0F, Confidence::Strong, Confidence::Partial},

    {0x11, BuildId::Win16V110, true, 0x0003, 0x7F8E,
     "movement + timer; then strategy=0,state=0x07",
     TransitionKind::ToFixedState, 0x07, Confidence::Strong, Confidence::Partial},

    {0x12, BuildId::Win16V110, true, 0x0003, 0x7FEE,
     "wait for timer/animation; then state=nextstate",
     TransitionKind::ToNextState, 0x00, Confidence::Strong, Confidence::Strong},

    {0x13, BuildId::Win16V110, true, 0x0003, 0x8038,
     "helper transition",
     TransitionKind::Unknown, 0x00, Confidence::Partial, Confidence::Partial},

    {0x14, BuildId::Win16V110, true, 0x0003, 0x804A,
     "long timer + periodic action",
     TransitionKind::Conditional, 0x00, Confidence::Partial, Confidence::Partial},

    {0x15, BuildId::Win16V110, true, 0x0003, 0x807E,
     "pain/hit reaction; then state=nextstate",
     TransitionKind::ToNextState, 0x00, Confidence::Confirmed, Confidence::Confirmed}
}};

struct GuardDispatcherEvidence {
    BuildId build;
    std::uint16_t segment;
    std::uint16_t offset;
    std::uint8_t firstState;
    std::uint8_t lastState;
    Confidence confidence;
};

inline constexpr GuardDispatcherEvidence kWin16Dispatcher{
    BuildId::Win16V110, 0x0003, 0x7B55, 0x00, 0x15, Confidence::Confirmed
};

inline constexpr GuardDispatcherEvidence kDos20Dispatcher{
    BuildId::DosV20, 0x1000, 0x59F0, 0x00, 0x15, Confidence::Strong
};

constexpr const GuardStateEvidence* win16State(std::uint8_t state) noexcept {
    for (const auto& item : kWin16V110States) {
        if (item.state == state) {
            return &item;
        }
    }
    return nullptr;
}

constexpr bool hasFixedTransition(std::uint8_t state,
                                  std::uint8_t target) noexcept {
    const auto* item = win16State(state);
    return item != nullptr &&
           item->transitionKind == TransitionKind::ToFixedState &&
           item->fixedTarget == target;
}

constexpr bool returnsViaNextState(std::uint8_t state) noexcept {
    const auto* item = win16State(state);
    return item != nullptr &&
           item->transitionKind == TransitionKind::ToNextState;
}

constexpr bool semanticNameSafeToAssign(std::uint8_t state) noexcept {
    const auto* item = win16State(state);
    return item != nullptr &&
           item->semanticConfidence == Confidence::Confirmed;
}

} // namespace n3d::re::v024
