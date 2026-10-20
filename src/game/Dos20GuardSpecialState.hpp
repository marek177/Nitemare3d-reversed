#pragma once
// DOS2 local state21 save/restore semantics, reported D02-N original RAM events.
// IMG:6103/610C/6113 and 5F14/5F17; see docs/BULK_UPDATE_20261020.md.
// The caller must supply a validated entry/return event; no guessed timer,
// hit eligibility, RNG, actor routing, or scheduler advancement is performed.
#include <cstdint>
namespace n3d::dos20::guard {
struct SpecialState {
    std::uint8_t state{};       // GUARD +0B
    std::uint8_t savedState{};  // GUARD +0C
};
constexpr void enterSpecial21(SpecialState& g) noexcept {
    if(g.state!=0) g.savedState=g.state;
    g.state=0x15;
}
// Host precondition avoids applying a return event to an unrelated state.
// The original caller's branch/timing eligibility remains outside this API.
constexpr bool returnFromSpecial21(SpecialState& g) noexcept {
    if(g.state!=0x15) return false;
    g.state=g.savedState;
    return true;
}
} // namespace n3d::dos20::guard
