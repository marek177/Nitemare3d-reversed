#include "worx21/stream_routing.hpp"

#include <stdexcept>

namespace worx21 {
namespace {
Read312e &require_reader(Read312e *read) {
    if(!read)throw std::logic_error("5F3E: DOS read 312E backend required");
    return *read;
}
StreamExternalCalls &require_external(StreamExternalCalls *e) {
    if(!e)throw std::logic_error("5F3E: external DSP/close/continuation backend required");
    return *e;
}
} // namespace

StreamRouteResult stream_route_5f3e(CSState &state, std::uint16_t current_cs,
                                    Read312e *reader,PortIO *ports,
                                    StreamExternalCalls *external) {
    StreamRouteResult res{};
    // 5F3E–5F51: only when 48DF:48E1 == 0 and buffered length 48EE == 0
    // does the original refill path perform header I/O.
    if((state.read16(0x48DFu)|state.read16(0x48E1u))==0u &&
       state.read16(0x48EEu)==0u) {
        res.fetched_header=true;
        // 5F51 TEST BYTE 4740,1: clear the *whole byte*, not merely bit0.
        if((state.read8(0x4740u)&1u)!=0u) {
            state.write8(0x4740u,0u);
            require_external(external).dsp_command_5a3f(0xD0u,state);
            if(!ports)throw std::logic_error("5F66: PIC/DSP output port 0A required");
            ports->out8(0x0Au,0x05u);
            res.stopped_previous_dsp=true;
        }
        // 5F68–5F76: read one mode byte into CS:48E3.
        res.first_read_ax=require_reader(reader).call_312e(1u,current_cs,0x48E3u,state);
        if(res.first_read_ax!=1u) {
            res.first_read_incomplete=true;
            // Failure joins 5FBA; CALL 4741, STC, RET.
            require_external(external).close_4741(state);
            res.error_close_called=true;
            res.explicit_stc=true;
            return res;
        }
        // 5F78–5F7E: read THREE bytes into 48DF..48E1; the original
        // does NOT validate AX before dispatch on mode. Stale values are
        // therefore possible after a short/failed second read.
        res.second_read_ax=require_reader(reader).call_312e(3u,current_cs,0x48DFu,state);
    }
    const auto mode=state.read8(0x48E3u);
    res.mode=mode;
    if(mode==0x0Cu) {
        res.route=StreamRouteKind::mode_0c;
        (void)stream_mode_0c_5fd2(state);
        return res;
    }
    if(mode==0x08u) {
        res.route=StreamRouteKind::mode_08;
        (void)stream_mode_08_5fbf(state,current_cs,require_reader(reader));
        return res;
    }
    // Original routing order is 0C,03,08,09,02,01, else 5FBA error.
    switch(mode) {
        case 0x03u: res.route=StreamRouteKind::mode_03;res.continuation_ip=0x5FF3u;break;
        case 0x09u: res.route=StreamRouteKind::mode_09;res.continuation_ip=0x6092u;break;
        case 0x02u: res.route=StreamRouteKind::mode_02;res.continuation_ip=0x60E8u;break;
        case 0x01u: res.route=StreamRouteKind::mode_01;res.continuation_ip=0x6037u;break;
        default:
            res.route=StreamRouteKind::invalid_mode;
            require_external(external).close_4741(state);
            res.error_close_called=true;
            res.explicit_stc=true;
            return res;
    }
    require_external(external).continue_mode(res.continuation_ip,state);
    return res;
}

} // namespace worx21
