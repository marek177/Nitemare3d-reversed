#pragma once

#include "worx21/audio_inner.hpp"

#include <cstdint>

namespace worx21 {

// CS:44B3..44E1: entry gate for *one* MIDI track.  The caller owns the
// 44E2+ body and any subsequent loops.  No inferred MIDI event is emitted.
enum class MidiGateKind : std::uint8_t { inactive, tick_decremented, event_ready };
struct MidiGateResult {
    MidiGateKind kind;
    std::uint16_t index;
    std::uint16_t es; // valid only for event_ready
    std::uint16_t di; // valid only for event_ready
};
MidiGateResult midi_track_gate_44b3(CSState &state);

// CS:4553..455B (unknown FF meta type): length is *one byte*, not a VLQ;
// DI wraps in 16 bits.  No output writes except the returned DI.
std::uint16_t midi_unknown_meta_skip_4553(FarByteMemory &mem,
                                          std::uint16_t es, std::uint16_t di);

class MidiReplayCalls {
public:
    virtual ~MidiReplayCalls() = default;
    virtual void replay_4265(CSState &state, std::uint16_t es, std::uint16_t di) = 0;
    virtual void replay_4389(CSState &state, std::uint16_t es, std::uint16_t di) = 0;
};

enum class MidiEotKind : std::uint8_t {
    another_track_seen, // CS:45AB increments global CS:2DC0, not found index
    replay_4265,         // callback invoked; jump back to 44B4 still pending
    replay_4389,
    all_tracks_stopped
};
struct MidiEotResult {
    MidiEotKind kind;
    std::uint32_t scanned; // number of array words read by original TEST
    std::uint16_t next_index; // CS:2DC0 after branch
};
// Exact local control/CS writes of CS:458C..45DC, up to the next 44B4
// iteration.  Full 4265/4389 and next-event processing remain injections.
// On track_count==0, LOOP scans 65536 slots unless an active bit is found.
MidiEotResult midi_end_track_458c(CSState &state, MidiReplayCalls *replay);

struct XmsRefillRequest {
    std::uint16_t driver_ip;
    std::uint16_t driver_cs;
    std::uint16_t ah; // 000Bh function number of far service
    std::uint16_t ds; // caller-supplied DS (after prior WORX PUSH CS/POP DS)
    std::uint16_t si; // CS:21CC argument block
    std::uint16_t bx; // original BX rewritten as 4 * resource number
};
class XmsFarService {
public:
    virtual ~XmsFarService() = default;
    virtual std::uint16_t invoke(const XmsRefillRequest &request,
                                 CSState &mutable_cs_state) = 0;
};
struct XmsRefillResult {
    XmsRefillRequest request;
    std::uint16_t service_ax;
    bool service_returned_one;
    std::uint16_t final_ax; // original AX is POPped *after* checking service AX
};
// Original direct instruction shell CS:5863..58D7.  This writes the packet
// and calls an EXPLICIT far service; it is NOT an emulation of XMS or EMS.
// The original leaves CS:21CE UNTOUCHED, even when it is stale.
XmsRefillResult xms_refill_packet_5863(CSState &state,
                                      std::uint16_t voice_bx,
                                      std::uint16_t original_ax,
                                      std::uint16_t original_ds,
                                      std::uint16_t current_cs,
                                      XmsFarService &service);

// CS:5FD2..5FF2: stream mode 0Ch subtracts the 16-bit block length from the
// 32-bit amount and clamps BOTH words to 0 on borrow.
struct StreamMode0cResult {
    bool underflow;
    std::uint32_t remaining;
};
StreamMode0cResult stream_mode_0c_5fd2(CSState &state) noexcept;

// CS:5FBF..5FD1: stream mode 08h uses input BX from CS:48DF,
// calls 312Eh with ES=CS, DI=5E69h, and subtracts ONLY AX from low 48DF;
// it does NOT borrow from the high word at 48E1.
class Read312e {
public:
    virtual ~Read312e() = default;
    virtual std::uint16_t call_312e(std::uint16_t bx,
                                    std::uint16_t es,
                                    std::uint16_t di,
                                    CSState &state) = 0;
};
struct StreamMode08Result {
    std::uint16_t bytes_reported;
    std::uint16_t remaining_low;
};
StreamMode08Result stream_mode_08_5fbf(CSState &state,
                                      std::uint16_t current_cs,
                                      Read312e &reader);

} // namespace worx21
