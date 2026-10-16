#pragma once

#include "worx21/audio_deep.hpp"

#include <cstddef>
#include <cstdint>

namespace worx21 {

// Registers visible at the first nontrivial decision of the transitive
// CS:3A4D MIDI device handler.  The rest of 3A4D is NOT reconstructed here.
// In particular, DX, DS, FLAGS and physical device timing remain opaque.
struct MidiDispatchRegisters {
    std::uint16_t ax = 0;
    std::uint16_t bx = 0;
    std::uint16_t cx = 0;
    std::uint16_t si = 0;
    std::uint16_t es = 0;
    std::uint16_t di = 0;
};

// The original 3A4D..3A66 prefix writes four CS globals unconditionally.
// This callback starts AFTER those four writes, at 3A67; it must be supplied
// to continue a channel event. The callback may mutate ES:DI and CS memory.
class MidiDispatchTail3a67 {
public:
    virtual ~MidiDispatchTail3a67() = default;
    virtual void dispatch_tail_3a67(CSState &state, MidiDispatchRegisters &regs) = 0;
};

enum class MidiStepKind : std::uint8_t {
    channel_event,
    meta_unknown,
    meta_tempo,
    meta_end_track
};
struct MidiStepResult {
    MidiStepKind kind = MidiStepKind::channel_event;
    std::uint8_t status = 0;        // after running-status resolution, or 0xFF
    std::uint8_t meta_type = 0;     // valid for FF branches only
    std::uint8_t table_data_count = 0;  // original 2DA4 nibble lookup
    std::uint16_t dispatch_bx = 0;  // BH/BL actually sent to 3A4D, channel only
    std::uint16_t dispatch_cx = 0;  // CX at CALL 3A4D, channel only
    std::uint16_t index_committed = 0; // read *after* 3A4D, channel/meta delta
    std::uint16_t next_di = 0;
    std::uint32_t next_delta = 0;
    std::size_t vlq_bytes = 0;
    MidiEotResult eot{MidiEotKind::all_tracks_stopped,0,0};
};

// One event from CS:44EE..4552, with composition of the pre-audited
// 4553/455D/458C and 45F9 helpers. On normal/tempo/unknown events, it stops
// precisely at JMP 44B4, *without* fabricating the following track iteration.
// FF 2F takes the distinct EOT path (no delta decode). A channel event needs
// a real injected remaining 3A4D device backend, or throws logic_error.
//
// Precondition: the CS:44B3 gate selected an event-ready track. That gate
// leaves AX=0000h at 44EE. ax_from_gate is explicit to document the WORD
// cache store and to allow instruction-level checks of noncanonical states.
// VLQ read limit is a HOST safety mechanism, not an original DOS behavior.
MidiStepResult midi_event_step_44ee(CSState &state,
                                    FarByteMemory &memory,
                                    std::uint16_t es,
                                    std::uint16_t di,
                                    std::uint16_t ax_from_gate,
                                    MidiDispatchTail3a67 *dispatch_tail,
                                    MidiReplayCalls *replay,
                                    PortIO *pit_ports,
                                    std::size_t safety_max_vlq_reads);

} // namespace worx21
