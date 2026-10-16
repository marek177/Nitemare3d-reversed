#include "worx21/int08_gate.hpp"

namespace worx21 {

void Timer08Gate::irq08() {
    // 4152: TEST CS:[2DBC],16h; 4163: CALL 4476 if nonzero.
    if ((state_.read8(0x2DBC) & 0x16u) != 0)
        hooks_.music_tick_4476(state_);

    // 416F..418F: 16-bit unsigned counter wraps like original INC WORD.
    const auto period = state_.read16(0x2DB6);
    const auto tick = static_cast<std::uint16_t>(state_.read16(0x2DB4) + 1u);
    state_.write16(0x2DB4, tick);
    if (tick >= period) {
        state_.write16(0x2DB4, 0);
        // 4188: PUSHF / CALL FAR CS:[000A] to previous INT08. Previous
        // handler owns EOI; this path must not emit a second PIC EOI.
        hooks_.chain_old_irq08(state_);
        return;
    }

    // 418F..41B2: special 0xFFFF idle sentinel for 3ED4; the increment
    // tests EXACTLY zero, not whether 3ED4 is merely nonnegative/zero before.
    state_.write16(0x3ED4, static_cast<std::uint16_t>(state_.read16(0x3ED4) + 1u));
    ports_.out8(0x0020u, 0x20u); // PIC EOI before nested audio/deferral
    if (state_.read16(0x3ED4) == 0)
        hooks_.audio_engine_40e7(state_);
    else
        state_.write16(0x40E5, static_cast<std::uint16_t>(state_.read16(0x40E5) + 1u));
    state_.write16(0x3ED4, static_cast<std::uint16_t>(state_.read16(0x3ED4) - 1u));
}

} // namespace worx21
