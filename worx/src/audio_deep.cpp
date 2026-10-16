#include "worx21/audio_deep.hpp"

#include <stdexcept>

namespace worx21 {
namespace {
constexpr std::uint16_t add16(std::uint16_t a, unsigned b) noexcept {
    return static_cast<std::uint16_t>(a+b);
}
}

MidiGateResult midi_track_gate_44b3(CSState &state) {
    const std::uint16_t index=state.read16(0x2DC0u);
    const std::uint16_t two=static_cast<std::uint16_t>(index << 1u);
    if ((state.read16(add16(two,0x2C62u)) & 1u) == 0)
        return {MidiGateKind::inactive,index,0,0};
    const std::uint16_t four=static_cast<std::uint16_t>(two << 1u);
    const std::uint16_t low_at=add16(four,0x2CA2u);
    const std::uint16_t high_at=add16(four,0x2CA4u);
    const std::uint16_t lo=state.read16(low_at);
    const std::uint16_t hi=state.read16(high_at);
    if ((lo|hi)!=0) {
        // SUB [low],1; SBB [high],0, modulo 2^16, in this exact order.
        state.write16(low_at,static_cast<std::uint16_t>(lo-1u));
        state.write16(high_at,static_cast<std::uint16_t>(hi-(lo==0u ? 1u:0u)));
        return {MidiGateKind::tick_decremented,index,0,0};
    }
    // SHR BX,1; DI=CS:[BX+2D22]; ES=CS:[2C5F]; no DI increment yet.
    return {MidiGateKind::event_ready,index,state.read16(0x2C5Fu),
            state.read16(add16(two,0x2D22u))};
}

std::uint16_t midi_unknown_meta_skip_4553(FarByteMemory &mem,
                                          std::uint16_t es,std::uint16_t di) {
    const std::uint8_t payload=mem.read8(es,di);
    return add16(di,1u+payload);
}

MidiEotResult midi_end_track_458c(CSState &state, MidiReplayCalls *replay) {
    const std::uint16_t old_idx=state.read16(0x2DC0u);
    const std::uint16_t active_slot=add16(static_cast<std::uint16_t>(old_idx << 1u),0x2C62u);
    state.write16(active_slot,0u);
    std::uint16_t cx=state.read16(0x2C58u);
    std::uint16_t bx=0;
    std::uint32_t scanned=0;
    // 459A TEST [BX+2C62], FFFF; 45A6 LOOP 459A.  Starting CX=0
    // means 65536 TESTs, but returns as soon as a nonzero WORD is found.
    for (;;) {
        ++scanned;
        if (state.read16(add16(bx,0x2C62u)) != 0u) {
            state.write16(0x2DC0u,add16(state.read16(0x2DC0u),1u));
            return {MidiEotKind::another_track_seen,scanned,state.read16(0x2DC0u)};
        }
        bx=add16(bx,2u);
        cx=add16(cx,0xFFFFu);
        if (cx==0u) break;
    }
    if (state.read8(0x2C61u) != 0u) {
        if (!replay) throw std::logic_error("MIDI replay 4265/4389 backend is required");
        const auto es=state.read16(0x2C5Fu);
        const auto di=state.read16(0x2C5Du);
        if (state.read8(0x2C5Cu) == 1u) {
            replay->replay_4389(state,es,di);
            return {MidiEotKind::replay_4389,scanned,state.read16(0x2DC0u)};
        }
        replay->replay_4265(state,es,di);
        return {MidiEotKind::replay_4265,scanned,state.read16(0x2DC0u)};
    }
    state.write8(0x2D62u,0);
    return {MidiEotKind::all_tracks_stopped,scanned,state.read16(0x2DC0u)};
}

XmsRefillResult xms_refill_packet_5863(CSState &state,
                                      std::uint16_t voice_bx,
                                      std::uint16_t original_ax,
                                      std::uint16_t original_ds,
                                      std::uint16_t current_cs,
                                      XmsFarService &service) {
    // 5868 MOV AX,BX; SHR AX,1; XCHG AL,AH; ADD AX,4CEDh.
    const std::uint16_t half=voice_bx >> 1u;
    const std::uint16_t swapped=static_cast<std::uint16_t>((half<<8u)|(half>>8u));
    const auto target=add16(swapped,0x4CEDu);
    state.write16(0x21D8u,target);
    state.write16(0x21DAu,current_cs);
    state.write16(0x21CCu,0x0100u);
    state.write16(0x21D6u,0u);
    state.write16(0x21D0u,state.read16(0x21C6u));
    const auto progress=state.read16(add16(voice_bx,0x4BCFu));
    state.write16(add16(voice_bx,0x54EDu),progress);
    const auto resource=state.read16(add16(voice_bx,0x4B6Fu));
    const auto index=static_cast<std::uint16_t>(resource<<2u);
    const auto base_lo=state.read16(add16(index,0x20C6u));
    const auto base_hi=state.read16(add16(index,0x20C8u));
    const auto sum=std::uint32_t(progress)+base_lo;
    state.write16(0x21D2u,static_cast<std::uint16_t>(sum));
    // CS:21D4=0 followed by ADC [21D4],AX.  MOV preserves ADD's CF.
    state.write16(0x21D4u,0);
    state.write16(0x21D4u,static_cast<std::uint16_t>(base_hi+(sum>>16u)));
    // Deliberately no write to CS:21CE: the original 5863 doesn't do one.
    XmsRefillRequest request{state.read16(0x21C8u),state.read16(0x21CAu),
                             0x000Bu,original_ds,0x21CCu,index};
    const std::uint16_t ret_ax=service.invoke(request,state);
    // CMP AX,1; optionally MOV AX,0; then POP SI,DX,CX,BX,AX.
    return {request,ret_ax,ret_ax==1u,original_ax};
}

StreamMode0cResult stream_mode_0c_5fd2(CSState &state) noexcept {
    const std::uint16_t lo=state.read16(0x48DFu);
    const std::uint16_t hi=state.read16(0x48E1u);
    const std::uint16_t count=state.read16(0x48DBu);
    const auto new_lo=static_cast<std::uint16_t>(lo-count);
    const auto borrow=lo<count;
    const auto new_hi=static_cast<std::uint16_t>(hi-(borrow?1u:0u));
    state.write16(0x48DFu,new_lo);
    state.write16(0x48E1u,new_hi);
    // JAE checks the CF from SBB: only 32-bit underflow clamps to zero.
    if(hi==0u && borrow) {
        state.write16(0x48DFu,0);
        state.write16(0x48E1u,0);
        return {true,0};
    }
    return {false, (std::uint32_t(new_hi)<<16u)|new_lo};
}

StreamMode08Result stream_mode_08_5fbf(CSState &state,
                                      std::uint16_t current_cs,
                                      Read312e &reader) {
    const std::uint16_t bx=state.read16(0x48DFu);
    const std::uint16_t ax=reader.call_312e(bx,current_cs,0x5E69u,state);
    const auto remaining=static_cast<std::uint16_t>(state.read16(0x48DFu)-ax);
    state.write16(0x48DFu,remaining);
    return {ax,remaining};
}

} // namespace worx21
