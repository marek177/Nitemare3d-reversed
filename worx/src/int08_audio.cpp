#include "worx21/int08_audio.hpp"

namespace worx21 {

void Timer08AudioService::run() {
    // Original 40E7..4107: CLI, save SS:SP, switch to private stack,
    // STI and save registers. These asynchronous CPU side effects cannot
    // be represented by our synchronous CSState contract.

    // 4108..411D: 32-bit modular subtract using SUB + SBB (little endian).
    const std::uint32_t old_value = std::uint32_t(state_.read16(0x2C4B)) |
        (std::uint32_t(state_.read16(0x2C4D)) << 16);
    const std::uint16_t decrement = state_.read16(0x2C49);
    const std::uint32_t result = old_value - decrement;
    state_.write16(0x2C4B, static_cast<std::uint16_t>(result));
    state_.write16(0x2C4D, static_cast<std::uint16_t>(result >> 16));

    // 4117 CMP CS:[2C4D],0; 411D JGE; 411F sets sticky 2C53 when
    // high word is signed-negative. Routine does not clear flag otherwise.
    if ((result & 0x80000000u) != 0)
        state_.write8(0x2C53, 1);

    // 4125..413B: the PCM and MIDI branches are independent. PCM first.
    if ((state_.read8(0x2DBC) & 0x20u) != 0)
        hooks_.pcm_mix_555d(state_);
    if (state_.read8(0x3ED6) != 0)
        hooks_.midi_schedule_5df2(state_);
}

} // namespace worx21
