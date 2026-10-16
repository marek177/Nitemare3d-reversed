#include "worx21/midi_routing.hpp"

#include <stdexcept>

namespace worx21 {

MpuSendResult mpu_send_58f8(CSState &state, PortIO &ports,
                            MidiDispatchRegisters &regs,
                            MidiFarCallback3896 *callback) {
    // 58F8 pushes AX/CX/DX, and restores them before a possible FAR CALL.
    // Internal polling uses CX=FFFFh and DX=0331h.  JCXZ executes before
    // DEC CX/IN, so there can be precisely 65535 reads, not 65536.
    MpuSendResult out{};
    out.output=static_cast<std::uint8_t>(regs.ax);
    for (std::uint32_t i=0; i<65535u; ++i) {
        const std::uint8_t status=ports.in8(0x331u);
        ++out.status_reads;
        if ((status & 0x40u)!=0u) continue;
        // Original OUT DX,AL at 5910, followed by POP DX,CX,AX.
        ports.out8(0x330u,out.output);
        out.transmitted=true;
        // CMP WORD CS:[3898],0 after the OUT: the port may have been
        // made ready, but the callback itself may still be unavailable.
        const auto segment=state.read16(0x3898u);
        if(segment!=0u) {
            if(!callback)
                throw std::logic_error("58F8: FAR CS:[3896] callback required");
            const auto offset=state.read16(0x3896u);
            callback->invoke_3896(segment,offset,state,regs);
            out.far_callback_invoked=true;
        }
        return out;
    }
    // 5922: POP DX,CX,AX; RET.  No OUT, no indirect callback.
    return out;
}

MidiRouting3a67::MidiRouting3a67(std::uint16_t current_cs, PortIO *ports,
                               MidiFarCallback3896 *far_callback,
                               MidiOtherRoutes3a67 *other_routes) noexcept
    : current_cs_(current_cs), ports_(ports), far_callback_(far_callback),
      other_routes_(other_routes) {}

void MidiRouting3a67::dispatch_tail_3a67(CSState &state,MidiDispatchRegisters &regs) {
    result_=MidiRoutingResult{};
    result_.pitch_after=state.read8(0x2DC5u);
    if ((state.read8(0x2DBCu)&0x06u)==0u) {
        result_.kind=MidiRoutingKind::direct_mpu;
        const auto saved_ax=regs.ax;
        const auto saved_cx=regs.cx;
        const auto saved_si=regs.si;
        // PUSH CS / POP DS at 3A6F, not matched by a restoration.
        regs.ds=current_cs_;
        // MOV AL,AH; XOR AH,AH; SHR AX,4; MOV SI,AX
        const auto upper=static_cast<std::uint8_t>(regs.ax >> 8u);
        regs.ax=static_cast<std::uint16_t>(upper >> 4u);
        regs.si=regs.ax;
        regs.cx=state.read8(static_cast<std::uint16_t>(0x2DA4u+regs.si));
        if (regs.cx!=0u) {
            if (!ports_) throw std::logic_error("3A67 direct MIDI: port I/O backend required");
            // The original MOV AL changes only AL; AH is inherited from
            // the preceding SHR and from any reentrant FAR callbacks.
            auto send_byte=[&](std::uint8_t value) {
                regs.ax=static_cast<std::uint16_t>((regs.ax&0xFF00u)|value);
                result_.send_calls.push_back(mpu_send_58f8(state,*ports_,regs,far_callback_));
            };
            send_byte(static_cast<std::uint8_t>(state.read8(0x2DC8u)|state.read8(0x2DC4u)));
            if (regs.cx!=0u) {
                --regs.cx;
                send_byte(state.read8(0x2DC5u));
                if (regs.cx!=0u) {
                    --regs.cx;
                    send_byte(state.read8(0x2DC6u));
                }
            }
        }
        // 3AA7 POP SI; POP CX; POP AX: outer status, count and SI restored;
        // far-callback side effects on DX/DS/DI/ES/BX are not undone.
        regs.si=saved_si;
        regs.cx=saved_cx;
        regs.ax=saved_ax;
        return;
    }

    const auto event_type=state.read8(0x2DC8u);
    if(event_type>0x90u) {
        if(event_type<=0xB0u) {
            result_.kind=MidiRoutingKind::route_3941;
            if(!other_routes_) throw std::logic_error("3A67: synth call 3941 required");
            other_routes_->call_3941(state,regs);
        } else if(event_type<=0xC0u) {
            result_.kind=MidiRoutingKind::route_3e34;
            if(!other_routes_) throw std::logic_error("3A67: synth call 3E34 required");
            other_routes_->call_3e34(state,regs);
        } else {
            result_.kind=MidiRoutingKind::ignored_status;
        }
    } else {
        bool transpose=true;
        if((state.read8(0x2DC9u)&0x20u)!=0u) {
            if(state.read8(0x2B4Du)==1u) {
                if(state.read8(0x2DC4u)==9u) transpose=false;
            } else if(state.read8(0x2DC4u)>=11u) {
                transpose=false;
            }
        }
        if(transpose) {
            const std::uint8_t pitch=state.read8(0x2DC5u);
            const auto after=static_cast<std::uint8_t>(pitch+state.read8(0x2DA3u));
            state.write8(0x2DC5u,after);
            regs.ax=static_cast<std::uint16_t>((regs.ax&0xFF00u)|after);
            result_.transposed_pitch=true;
            result_.pitch_after=after;
        }
        result_.kind=MidiRoutingKind::route_3b5b;
        if(!other_routes_) throw std::logic_error("3A67: synth call 3B5B required");
        other_routes_->call_3b5b(state,regs);
    }
    // Only this route has 3B02 CLC, after its chosen direct callee returns.
    result_.explicit_clc=true;
}

} // namespace worx21
