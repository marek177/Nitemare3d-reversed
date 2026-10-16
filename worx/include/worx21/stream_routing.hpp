#pragma once

#include "worx21/audio_deep.hpp"

#include <cstdint>

namespace worx21 {

// This model enters at CS:5F3E, *after* 5F17 has set 2DEA and optionally
// cleared the PCM output buffer. Original CS:5F17 PUSH CS/POP DS is a
// precondition managed by the caller. Neither emulator RAM nor OS files are
// fabricated: all read/stop/close/mode continuations must be injected.
class StreamExternalCalls {
public:
    virtual ~StreamExternalCalls() = default;
    // CALL 5A3F receives AL=D0h. It is the full DSP write call, not just OUT.
    virtual void dsp_command_5a3f(std::uint8_t al, CSState &state) = 0;
    virtual void close_4741(CSState &state) = 0;
    // Only missing target modes: 03->5FF3, 09->6092, 02->60E8, 01->6037.
    // This callback must perform their full transitive semantics (if known).
    // Without it, only the local 5F3E dispatch gate is reconstructed.
    virtual void continue_mode(std::uint16_t target_ip, CSState &state) = 0;
};

enum class StreamRouteKind : std::uint8_t {
    mode_0c, mode_03, mode_08, mode_09, mode_02, mode_01, invalid_mode
};
struct StreamRouteResult {
    StreamRouteKind route = StreamRouteKind::invalid_mode;
    bool fetched_header = false;
    bool stopped_previous_dsp = false;
    std::uint16_t first_read_ax = 0;
    std::uint16_t second_read_ax = 0;
    bool first_read_incomplete = false;
    bool error_close_called = false;
    bool explicit_stc = false; // CS:5FBD; other routes' FLAGS not covered here
    std::uint16_t mode = 0;
    std::uint16_t continuation_ip = 0; // 0 for implemented 08/0C and invalid
};

// Exact control branch at CS:5F3E–5FBE with existing implementations
// of the local 5FBF (08) and 5FD2 (0C) branch tail functions.
// Other target tails still require explicit continuation callbacks.
// Passing nullptr is safe only when that dependency is not reached.
StreamRouteResult stream_route_5f3e(CSState &state, std::uint16_t current_cs,
                                    Read312e *reader, PortIO *ports,
                                    StreamExternalCalls *external);

} // namespace worx21
