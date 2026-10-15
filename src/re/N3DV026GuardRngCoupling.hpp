#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string_view>

namespace n3d::re::v026 {

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Partial,
    Open
};

enum class RngConsumer : std::uint8_t {
    AnimationVariant,
    GuardBlockedAxisFlip,
    GuardPlanner,
    GuardState13Timer,
    GuardDamagePain,
    GuardWakeTimer,
    IncomingDamageMasked,
    SceneEffectPosition,
    GuardSfxVariant,
    ResourceTableVariant,
    SceneEffectTimer,
    ProjectedAnimationVariant,
    Unassigned
};

enum class DrawCountModel : std::uint8_t {
    ExactlyOne,
    VariableRejectionLoop,
    Unknown
};

struct GuardRngCoupling {
    std::uint16_t callsite;
    RngConsumer consumer;
    bool guardStateKnown;
    std::uint8_t guardState;
    DrawCountModel drawCount;
    Confidence confidence;
    std::string_view effect;
};

// v0.35: 22 raw direct far-call sites, verified against the fingerprinted
// original DOS v2.0 unpacked load image. Confidence means the INSTRUCTION-
// LOCAL consumer is supported, not that dynamic order or reachability is.
inline constexpr std::array<GuardRngCoupling, 22> kDos20RngCoupling = {{
    {0x2478, RngConsumer::AnimationVariant, false, 0,
     DrawCountModel::VariableRejectionLoop, Confidence::Confirmed,
     "animation variant selection via RNG&7; rejection loop may consume 0..N additional draws"},

    {0x525E, RngConsumer::GuardBlockedAxisFlip, true, 0x06,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "when blockedX && blockedY, bit0 chooses stored X/Y direction flip"},

    {0x5582, RngConsumer::GuardWakeTimer, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "GUARD+0A=0 and matching +0E with state 7/8: timer GUARD+06 = RNG%8 (0..7), then state=1"},

    {0x5666, RngConsumer::GuardPlanner, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Strong,
     "planner cluster RNG draw; exact consumer within timer/direction chain still requires trace closure"},

    {0x56A6, RngConsumer::GuardPlanner, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Strong,
     "planner cluster RNG draw; exact consumer within timer/direction chain still requires trace closure"},

    {0x573F, RngConsumer::GuardPlanner, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Strong,
     "planner cluster RNG draw; exact consumer within timer/direction chain still requires trace closure"},

    {0x58A7, RngConsumer::GuardState13Timer, true, 0x13,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "state 13 timer = RNG%80 + 8, range 8..87"},

    {0x85AD, RngConsumer::GuardDamagePain, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Strong,
     "damage/pain ordering RNG draw; exact branch consumer still needs runtime ordering proof"},

    {0x8860, RngConsumer::IncomingDamageMasked, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "actor class 08 incoming player damage: RNG & 7; 87D8 jump-table entry 882E"},
    {0x886C, RngConsumer::IncomingDamageMasked, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "actor classes 09/0A incoming player damage: RNG & 15; jump-table entries 8830/8832"},
    {0x887C, RngConsumer::IncomingDamageMasked, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "actor classes 11..14 incoming player damage: RNG & 31; class table entries 8840..8846"},

    {0x9A68, RngConsumer::SceneEffectPosition, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "immediate consumer RNG%62 -> DS:3632; effect rendering semantics separately open"},

    {0x9A77, RngConsumer::SceneEffectPosition, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "after 9A68, second RNG%36 -> DS:3630; exact effect trigger still runtime open"},

    {0x9C98, RngConsumer::GuardSfxVariant, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "class-specific sound selector RNG%3+0x17 (0x17..0x19); class/name pairing outside this record"},

    {0x9CC2, RngConsumer::GuardSfxVariant, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "class-specific sound selector RNG%4+0x4B (0x4B..0x4E); class/name pairing outside this record"},

    {0x9D6E, RngConsumer::GuardSfxVariant, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "class-specific sound selector RNG%3+0x0B (0x0B..0x0D); class/name pairing outside this record"},

    {0x9F0C, RngConsumer::GuardSfxVariant, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "class-specific sound selector RNG%3+0x38 (0x38..0x3A); class/name pairing outside this record"},

    {0x9F36, RngConsumer::GuardSfxVariant, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "class-specific sound selector RNG%2+0x36 (0x36..0x37); class/name pairing outside this record"},

    {0x9FE3, RngConsumer::ResourceTableVariant, false, 0,
     DrawCountModel::VariableRejectionLoop, Confidence::Confirmed,
     "RNG%7 -> 0..6; SI==7 branch unreachable for 15-bit output; retry if resource byte +0x4B == 0"},

    {0xA047, RngConsumer::ResourceTableVariant, false, 0,
     DrawCountModel::VariableRejectionLoop, Confidence::Confirmed,
     "RNG%7 -> 0..6; SI==7 branch unreachable for 15-bit output; retry if resource byte +0x3B == 0"},

    {0xA12B, RngConsumer::SceneEffectTimer, false, 0,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "RNG%240 + 160 -> DS:3634; upstream event semantics not yet named"},

    {0xB276, RngConsumer::ProjectedAnimationVariant, false, 0,
     DrawCountModel::VariableRejectionLoop, Confidence::Confirmed,
     "B22C frame boundary -> RNG&7 -> OBJECT+02; retry if selected descriptor word high byte zero; then OBJECT+03"},
}};

constexpr const GuardRngCoupling* couplingFor(std::uint16_t callsite) noexcept {
    for (const auto& item : kDos20RngCoupling) {
        if (item.callsite == callsite) {
            return &item;
        }
    }
    return nullptr;
}

constexpr std::size_t countAssignedConsumers() noexcept {
    std::size_t count = 0;
    for (const auto& item : kDos20RngCoupling) {
        if (item.consumer != RngConsumer::Unassigned) {
            ++count;
        }
    }
    return count;
}

constexpr std::size_t countConfirmedCouplings() noexcept {
    std::size_t count = 0;
    for (const auto& item : kDos20RngCoupling) {
        if (item.confidence == Confidence::Confirmed) {
            ++count;
        }
    }
    return count;
}

constexpr bool isExactlyOneDraw(std::uint16_t callsite) noexcept {
    const auto* item = couplingFor(callsite);
    return item != nullptr &&
           item->drawCount == DrawCountModel::ExactlyOne;
}

constexpr bool isStateBound(std::uint16_t callsite,
                            std::uint8_t state) noexcept {
    const auto* item = couplingFor(callsite);
    return item != nullptr &&
           item->guardStateKnown &&
           item->guardState == state;
}

} // namespace n3d::re::v026
