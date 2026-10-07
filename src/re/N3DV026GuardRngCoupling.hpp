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

inline constexpr std::array<GuardRngCoupling, 20> kDos20RngCoupling = {{
    {0x2478, RngConsumer::AnimationVariant, false, 0,
     DrawCountModel::VariableRejectionLoop, Confidence::Confirmed,
     "animation variant selection via RNG&7; rejection loop may consume 0..N additional draws"},

    {0x525E, RngConsumer::GuardBlockedAxisFlip, true, 0x06,
     DrawCountModel::ExactlyOne, Confidence::Confirmed,
     "when blockedX && blockedY, bit0 chooses stored X/Y direction flip"},

    {0x5582, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

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

    {0x887C, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9A68, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9A77, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9C98, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9CC2, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9D6E, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9F0C, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9F36, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0x9FE3, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0xA047, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0xA12B, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"},

    {0xB276, RngConsumer::Unassigned, false, 0,
     DrawCountModel::Unknown, Confidence::Open,
     "direct RNG callsite; semantic consumer not yet closed"}
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
