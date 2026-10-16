#pragma once

#include "worx21/audio_events.hpp"

#include <cstdint>
#include <vector>

namespace worx21 {

// Original CS:58F8..5925 sends a byte to an MPU-401 UART-like port path.
// A far callback at CS:[3896] is called ONLY after the OUT succeeds and
// CS:[3898] != 0. Because it runs after 58F8 POPs AX/CX/DX, the callback
// can affect the caller's subsequent JCXZ branches and any live registers.
class MidiFarCallback3896 {
public:
    virtual ~MidiFarCallback3896() = default;
    virtual void invoke_3896(std::uint16_t segment, std::uint16_t offset,
                             CSState &state, MidiDispatchRegisters &regs) = 0;
};

struct MpuSendResult {
    bool transmitted = false;
    std::uint32_t status_reads = 0; // max 65,535 from the original CX loop
    bool far_callback_invoked = false;
    std::uint8_t output = 0;
};

// Exact bounded local CS:58F8–5925 machine branch/port ordering.
// I/O backend models external port behavior; callback is mandatory if
// CS:[3898]!=0 and a byte was actually emitted. No IRQ/timing parity claim.
MpuSendResult mpu_send_58f8(CSState &state, PortIO &ports,
                            MidiDispatchRegisters &regs,
                            MidiFarCallback3896 *callback);

class MidiOtherRoutes3a67 {
public:
    virtual ~MidiOtherRoutes3a67() = default;
    virtual void call_3941(CSState &, MidiDispatchRegisters &) = 0;
    virtual void call_3e34(CSState &, MidiDispatchRegisters &) = 0;
    virtual void call_3b5b(CSState &, MidiDispatchRegisters &) = 0;
};

enum class MidiRoutingKind : std::uint8_t {
    direct_mpu,       // 2DBC & 06 == 0
    route_3941,       // (2DBC & 06)!=0; status 91h..B0h
    route_3e34,       // ... status B1h..C0h
    route_3b5b,       // ... status <=90h, optional pitch transpose
    ignored_status    // ... status >C0h
};
struct MidiRoutingResult {
    MidiRoutingKind kind = MidiRoutingKind::ignored_status;
    std::vector<MpuSendResult> send_calls{};
    bool transposed_pitch = false;
    std::uint8_t pitch_after = 0; // CS:[2DC5] after local arithmetic
    bool explicit_clc = false;   // 3B02 CLC only on non-direct route
};

// CS:3A67–3B03 includes locally executable routing decisions and a
// hard dependency on three deeper synth/callback paths.
// Registers MUST represent the state AFTER 3A4D..3A66, including transformed
// AX. If a far callback edits CX, the next JCXZ sees that edited value.
// DS:=current_cs on the direct branch is not restored by 3A67 itself.
class MidiRouting3a67 final : public MidiDispatchTail3a67 {
public:
    MidiRouting3a67(std::uint16_t current_cs, PortIO *ports,
                   MidiFarCallback3896 *far_callback,
                   MidiOtherRoutes3a67 *other_routes) noexcept;
    void dispatch_tail_3a67(CSState &state, MidiDispatchRegisters &regs) override;
    const MidiRoutingResult &last_result() const noexcept { return result_; }
private:
    std::uint16_t current_cs_;
    PortIO *ports_;
    MidiFarCallback3896 *far_callback_;
    MidiOtherRoutes3a67 *other_routes_;
    MidiRoutingResult result_{};
};

} // namespace worx21
