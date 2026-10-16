#include "worx21/audio_events.hpp"

#include <stdexcept>

namespace worx21 {
namespace {
constexpr std::uint16_t add16(std::uint16_t a, unsigned b) noexcept {
    return static_cast<std::uint16_t>(a + b);
}

void commit_next_delta(CSState &state, std::uint16_t di,
                       const MidiVlq45f9Result &next, MidiStepResult &result) {
    // 452B reads the current index only AFTER 3A4D and 45F9 returned.
    const auto index=state.read16(0x2DC0u);
    const auto twice=static_cast<std::uint16_t>(index << 1u);
    const auto four=static_cast<std::uint16_t>(twice << 1u);
    // 4532/4539/453E: exact write order, including CS alias cases.
    state.write16(add16(twice,0x2D22u),di);
    state.write16(add16(four,0x2CA2u),static_cast<std::uint16_t>(next.delta));
    state.write16(add16(four,0x2CA4u),static_cast<std::uint16_t>(next.delta>>16u));
    result.index_committed=index;
    result.next_di=di;
    result.next_delta=next.delta;
    result.vlq_bytes=next.bytes_read;
}
} // namespace

MidiStepResult midi_event_step_44ee(CSState &state, FarByteMemory &memory,
                                    std::uint16_t es,std::uint16_t di,
                                    std::uint16_t ax_from_gate,
                                    MidiDispatchTail3a67 *dispatch_tail,
                                    MidiReplayCalls *replay,
                                    PortIO *pit_ports,
                                    std::size_t safety_max_vlq_reads) {
    MidiStepResult result{};
    const auto track=state.read16(0x2DC0u);
    const auto twice=static_cast<std::uint16_t>(track<<1u); // BX on entry
    // 44EE: read AL from ES:[DI]. The comparison against FF PRECEDES the
    // generic status-high-bit test. FF events do not update running status.
    const auto lead=memory.read8(es,di);
    if (lead==0xFFu) {
        di=add16(di,1u);                         // 4546 INC DI
        const auto type=memory.read8(es,di);      // 4547 MOV AL,ES:[DI]
        di=add16(di,1u);                         // 454A INC DI
        result.status=0xFFu;
        result.meta_type=type;
        if (type==0x2Fu) {
            result.kind=MidiStepKind::meta_end_track;
            result.eot=midi_end_track_458c(state,replay);
            result.next_di=di; // observed at entry of EOT; not committed
            return result;
        }
        if (type==0x51u) {
            result.kind=MidiStepKind::meta_tempo;
            // 455D: skip exactly 1 length byte, then 3 tempo bytes; helper
            // may raise a host representation of guest x86 #DE.
            di=tempo_ff51_455d(state,memory,pit_ports,es,di).next_di;
        } else {
            result.kind=MidiStepKind::meta_unknown;
            // 4553: length is a SINGLE byte, *not* VLQ.
            di=midi_unknown_meta_skip_4553(memory,es,di);
        }
    } else {
        const auto status_address=add16(twice,0x2D63u);
        if ((lead & 0x80u)!=0u) {
            // 44F9: WORD store. AH is the value inherited from the zero-delta
            // gate, usually 0. Do not replace with a BYTE store.
            state.write16(status_address,static_cast<std::uint16_t>((ax_from_gate & 0xFF00u)|lead));
            di=add16(di,1u);
        }
        // Running status (<80h) neither increments DI nor overwrites cache.
        const auto cached_ax=state.read16(status_address);
        const auto status=static_cast<std::uint8_t>(cached_ax);
        const auto si=static_cast<std::uint16_t>(status>>4u);
        const auto count=state.read8(add16(0x2DA4u,si));
        std::uint16_t cx=count; // 4511 XOR CH,CH
        std::uint8_t bh=static_cast<std::uint8_t>(twice>>8u);
        std::uint8_t bl=static_cast<std::uint8_t>(twice);
        if(cx!=0u) {
            bh=memory.read8(es,di); // 451A first data byte in BH
            di=add16(di,1u);
            --cx;
            if(cx!=0u) {
                bl=memory.read8(es,di); // 4521 second data byte in BL
                di=add16(di,1u);
                // There is NO second DEC CX here, even if count==2!
            }
        }
        MidiDispatchRegisters regs{cached_ax,
                                   static_cast<std::uint16_t>((std::uint16_t(bh)<<8u)|bl),
                                   cx,si,es,di};
        result.kind=MidiStepKind::channel_event;
        result.status=status;
        result.table_data_count=count;
        result.dispatch_bx=regs.bx;
        result.dispatch_cx=regs.cx;
        // 3A4D..3A66 unconditional CS prologue, BEFORE the opaque hardware
        // or software routing at 3A67. These global effects are byte-pinned.
        state.write8(0x2DC4u,static_cast<std::uint8_t>(status&0x0Fu));
        state.write8(0x2DC8u,static_cast<std::uint8_t>(status&0xF0u));
        state.write8(0x2DC5u,bh);
        state.write8(0x2DC6u,bl);
        if(!dispatch_tail)
            throw std::logic_error("3A4D tail 3A67+: explicit downstream MIDI backend required");
        dispatch_tail->dispatch_tail_3a67(state,regs);
        // The direct handler might alter ES/DI. Do not silently assume it
        // preserved these registers without complete transitive closure.
        es=regs.es;
        di=regs.di;
    }
    // 4528 CALL 45F9, followed by 452B..4543 commit and JMP 44B4.
    const auto next=read_vlq_45f9(memory,es,di,safety_max_vlq_reads);
    commit_next_delta(state,next.next_di,next,result);
    return result;
}
} // namespace worx21
