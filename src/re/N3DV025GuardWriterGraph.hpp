#pragma once

#include <array>
#include <cstdint>
#include <string_view>

namespace n3d::re::v025 {

enum class Confidence : std::uint8_t {
    Confirmed,
    Strong,
    Partial,
    Open
};

enum class GuardField : std::uint8_t {
    State,
    NextState,
    Strategy,
    Timer,
    Strength,
    ResultOctant,
    ObjectClass
};

enum class WriteKind : std::uint8_t {
    FixedValue,
    CopyNextStateToState,
    CopyStateToNextState,
    Conditional,
    MultiTarget,
    Unknown
};

struct GuardWriteEvidence {
    std::string_view label;
    bool addressKnown;
    std::uint16_t segment;
    std::uint16_t offset;
    GuardField field;
    WriteKind kind;
    std::uint16_t value;
    Confidence confidence;
    std::string_view evidence;
};

inline constexpr std::array<GuardWriteEvidence, 17> kWin16WriterGraph = {{
    {"state00_return", true, 0x0003, 0x7BA2,
     GuardField::State, WriteKind::CopyNextStateToState, 0,
     Confidence::Strong,
     "state 00 completes by assigning state=nextstate"},

    {"state01_to_02", true, 0x0003, 0x7BE0,
     GuardField::State, WriteKind::FixedValue, 0x02,
     Confidence::Strong,
     "state 01 countdown completes into state 02"},

    {"state06_to_03", true, 0x0003, 0x7CEC,
     GuardField::State, WriteKind::FixedValue, 0x03,
     Confidence::Strong,
     "state 06 movement/timer completes into state 03"},

    {"state0E_to_0F", true, 0x0003, 0x7E6C,
     GuardField::State, WriteKind::Conditional, 0x0F,
     Confidence::Strong,
     "state 0E has a conditional transition to 0F"},

    {"state0F_multi", true, 0x0003, 0x7E9E,
     GuardField::State, WriteKind::MultiTarget, 0,
     Confidence::Strong,
     "state 0F transitions to 10 or back to 0E"},

    {"state10_to_0F", true, 0x0003, 0x7F26,
     GuardField::State, WriteKind::FixedValue, 0x0F,
     Confidence::Strong,
     "state 10 timer completes into state 0F"},

    {"state11_strategy_reset", true, 0x0003, 0x7F8E,
     GuardField::Strategy, WriteKind::FixedValue, 0,
     Confidence::Strong,
     "state 11 completion writes strategy=0"},

    {"state11_to_07", true, 0x0003, 0x7F8E,
     GuardField::State, WriteKind::FixedValue, 0x07,
     Confidence::Strong,
     "state 11 completion writes state=07"},

    {"state12_return", true, 0x0003, 0x7FEE,
     GuardField::State, WriteKind::CopyNextStateToState, 0,
     Confidence::Strong,
     "state 12 completes by assigning state=nextstate"},

    {"state15_return", true, 0x0003, 0x807E,
     GuardField::State, WriteKind::CopyNextStateToState, 0,
     Confidence::Confirmed,
     "pain/hit reaction returns via nextstate"},

    {"normal_pain_save_previous_state", false, 0, 0,
     GuardField::NextState, WriteKind::CopyStateToNextState, 0,
     Confidence::Confirmed,
     "ordinary non-lethal damage preserves prior state in nextstate"},

    {"normal_pain_enter_15", false, 0, 0,
     GuardField::State, WriteKind::FixedValue, 0x15,
     Confidence::Confirmed,
     "ordinary non-lethal damage enters pain state 15"},

    {"normal_pain_resoct_8", false, 0, 0,
     GuardField::ResultOctant, WriteKind::FixedValue, 0x08,
     Confidence::Confirmed,
     "ordinary non-lethal damage writes resoct=8"},

    {"dracula_transform_class", false, 0, 0,
     GuardField::ObjectClass, WriteKind::FixedValue, 0x14,
     Confidence::Confirmed,
     "lethal Dracula phase-1 path rewrites OBJECT+06 from 0x11 to 0x14"},

    {"dracula_transform_state", false, 0, 0,
     GuardField::State, WriteKind::FixedValue, 0x08,
     Confidence::Confirmed,
     "Dracula second phase enters state 08"},

    {"dracula_transform_nextstate", false, 0, 0,
     GuardField::NextState, WriteKind::FixedValue, 0x02,
     Confidence::Confirmed,
     "Dracula second phase writes nextstate=02"},

    {"dracula_transform_timer", false, 0, 0,
     GuardField::Timer, WriteKind::FixedValue, 0x01,
     Confidence::Confirmed,
     "Dracula second phase writes timer=1"}
}};

constexpr const GuardWriteEvidence* writer(std::string_view label) noexcept {
    for (const auto& item : kWin16WriterGraph) {
        if (item.label == label) {
            return &item;
        }
    }
    return nullptr;
}

constexpr std::size_t countWritersFor(GuardField field) noexcept {
    std::size_t count = 0;
    for (const auto& item : kWin16WriterGraph) {
        if (item.field == field) {
            ++count;
        }
    }
    return count;
}

constexpr bool hasKnownAddress(std::string_view label) noexcept {
    const auto* item = writer(label);
    return item != nullptr && item->addressKnown;
}

constexpr bool isConfirmedWriter(std::string_view label) noexcept {
    const auto* item = writer(label);
    return item != nullptr && item->confidence == Confidence::Confirmed;
}

constexpr bool isPainEntryInvariant() noexcept {
    const auto* save = writer("normal_pain_save_previous_state");
    const auto* enter = writer("normal_pain_enter_15");
    const auto* resoct = writer("normal_pain_resoct_8");

    return save != nullptr && enter != nullptr && resoct != nullptr &&
           save->kind == WriteKind::CopyStateToNextState &&
           enter->value == 0x15 &&
           resoct->value == 0x08 &&
           save->confidence == Confidence::Confirmed &&
           enter->confidence == Confidence::Confirmed &&
           resoct->confidence == Confidence::Confirmed;
}

} // namespace n3d::re::v025
