#pragma once

#include "worx21/int63_leaf.hpp"

#include <cstddef>
#include <cstdint>

namespace worx21 {

// A user-supplied real-mode far-memory boundary. DOS memory mapping, A20,
// aliased segments, DMA coherency and cycles are deliberately NOT fabricated.
class FarByteMemory {
public:
    virtual ~FarByteMemory() = default;
    virtual std::uint8_t read8(std::uint16_t segment, std::uint16_t offset) = 0;
    virtual void write8(std::uint16_t segment, std::uint16_t offset,
                        std::uint8_t byte) = 0;
};

struct Dma49bcResult {
    std::uint16_t ax = 0;
    std::uint16_t cx = 0;
    std::uint16_t dx = 0;
    bool accepted = false;
};

// AX/CX/DX, CS memory and port-side CS:49BC..4A11 sub-contract.
// The original signed JLE/JGE comparisons are preserved; DS and CLI/STI
// state/cycles are outside this host function.
// initial_dx is the register DX on entry; early returns keep it unchanged.
Dma49bcResult poll_dma_49bc(CSState &state, PortIO &port,
                            std::uint16_t initial_dx = 0);

class MusicStream5f17 {
public:
    virtual ~MusicStream5f17() = default;
    virtual void stream_5f17(CSState &state) = 0;
};

// Complete branch/call shell at CS:5DF2..5E18; transitive CS:5F17 remains
// an injected dependency and is not claimed as 1:1.
void music_gateway_5df2(CSState &state, PortIO *ports,
                        MusicStream5f17 &stream);

class MidiTrack44b3 {
public:
    virtual ~MidiTrack44b3() = default;
    virtual void track_44b3(CSState &state) = 0;
};

// Exact outer control flow at CS:4476..44B2 (with deliberate fallthrough
// INTO 44B3). Each call to 44B3 is visible to the injected full track body.
// If the original track body hangs or does not return, neither will a real
// guest; this synchronous model assumes each injected callback returns.
void midi_tick_outer_4476(CSState &state, MidiTrack44b3 &track);

struct MidiVlq45f9Result {
    std::uint32_t delta;
    std::uint16_t next_di;
    std::size_t bytes_read;
};

struct MidiTempoMeta455dResult {
    std::uint16_t next_di;
    std::uint16_t timer_divisor;
    bool pit_programmed;
};

// Machine-byte-derived FF 51 tempo event branch at CS:455D..458B and the
// direct PIT helper at CS:466A..469E. The event length byte is SKIPPED and
// never verified; 24-bit big-endian tempo / CS:2C5A uses x86 DIV, which can
// fault on zero divisor/quotient overflow. The C++ overflow_error represents
// a GUEST #DE edge only, not a full protected-mode/real-mode trap frame.
// When CS:201E==1 the PIT helper is inert, but CS:2C49 still updates.
MidiTempoMeta455dResult tempo_ff51_455d(CSState &state,
                                         FarByteMemory &memory,
                                         PortIO *ports,
                                         std::uint16_t es,
                                         std::uint16_t di);

// The original CS:45F9..462F emits the low 32 bits of any-length MIDI-style
// big-endian 7-bit VLQ, wraps DI at 16 bits and does NOT reject 5+ bytes.
// safety_max_reads is a host safety GUARD, not a DOS original limit; when
// it is hit the call fails explicitly instead of manufacturing a result.
MidiVlq45f9Result read_vlq_45f9(FarByteMemory &memory,
                               std::uint16_t es, std::uint16_t di,
                               std::size_t safety_max_reads);

// Exact sample arithmetic of CS:5625..563D (excluding memory writes):
// (sample >> 1) - 64; signed IMUL with (volume << 2) mod 2^16;
// use AH (bits 8..15 of product) and ADD BYTE (8-bit wrap, no clipping).
std::uint8_t pcm_mix_byte_5625(std::uint8_t destination,
                               std::uint8_t sample,
                               std::uint16_t volume) noexcept;

// Direct prefix of CS:5F17..5F3D, independently from the subsequent file
// processing and callback graph: 2DEA=1; clear 48DB bytes in ES:DI to
// (48E4==0 ? 80h : 00h). This does NOT perform DOS stream refill.
void stream_fill_prefix_5f17(CSState &state, FarByteMemory &memory);

// Executed portion of CS:555D..557D only, GIVEN a completed 49BC poll:
// save CX at CS:478B and REP STOSW with AX=8080; unpaired odd byte untouched.
// Does not implement subsequent 8-voice mixing loop at CS:557E..5663.
void pcm_clear_prefix_5568(CSState &state, FarByteMemory &memory,
                           std::uint16_t bytes_available);

} // namespace worx21
