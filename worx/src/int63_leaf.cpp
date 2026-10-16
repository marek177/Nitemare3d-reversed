#include "worx21/int63_leaf.hpp"

#include <stdexcept>

namespace worx21 {

std::uint8_t CSState::read8(std::uint16_t offset) const noexcept {
    return bytes_[offset];
}
std::uint16_t CSState::read16(std::uint16_t offset) const noexcept {
    return static_cast<std::uint16_t>(read8(offset) |
        (std::uint16_t(read8(static_cast<std::uint16_t>(offset + 1u))) << 8));
}
void CSState::write8(std::uint16_t offset, std::uint8_t value) noexcept {
    bytes_[offset] = value;
}
void CSState::write16(std::uint16_t offset, std::uint16_t value) noexcept {
    write8(offset, static_cast<std::uint8_t>(value));
    write8(static_cast<std::uint16_t>(offset + 1u), static_cast<std::uint8_t>(value >> 8));
}
PortIO &KnownLeafBackend::require_ports() {
    if (!ports_) throw std::logic_error("Original DOS/ISA port behavior needs a supplied PortIO device");
    return *ports_;
}

Registers KnownLeafBackend::interrupt63(const Registers &input) {
    // Refuse unsupported branches before simulating a successful dispatch.
    // A machine invocation of a null slot is NOT equivalent to this exception.
    switch (input.ah()) {
    case 0x02: case 0x03: case 0x08: case 0x09: case 0x0A: case 0x0B: case 0x0E: case 0x13: case 0x16:
    case 0x12: case 0x19: case 0x1C: case 0x1D: case 0x1F: case 0x20: case 0x21: case 0x22: case 0x24: case 0x26: case 0x29: case 0x2A: case 0x2B: case 0x2C: case 0x2D: case 0x2E: case 0x30: case 0x31: case 0x32: case 0x36: case 0x37:
    case 0x3E: case 0x43: case 0x44: case 0x46: case 0x47: case 0x4A: case 0x4B: case 0x4C: case 0x4F: case 0x50: case 0x51:
        break;
    default:
        throw std::logic_error("AH not reconstructed from original body: unsupported by KnownLeafBackend");
    }
    // Missing external devices fail before any state change; original DOS/ISA
    // hardware may still have side effects not modeled in this host contract.
    if (input.ah() == 0x29 || (input.ah() == 0x2E && state_.read16(0x201E) != 1)) {
        (void)require_ports();
    }
    if (input.ah() == 0x19 && state_.read16(0x2DF3) != 0xFFFFu && !dos_) {
        throw std::logic_error("DOS INT21 3Eh required for WORX AH=19h: supply DosFileIO");
    }
    const auto active_before = state_.read16(0x3ED4);
    state_.write16(0x3ED4, static_cast<std::uint16_t>(active_before + 1u));
    Registers out = input;
    switch (input.ah()) {
    case 0x02: // 15BF:485A .. 4865
        state_.write16(0x2DF0, input.bx);
        out.ax = input.al(); // XOR AH,AH
        state_.write16(0x2010, out.ax);
        break;
    case 0x03: { // 15BF:308E .. 3099
        out.ax = state_.read16(0x2C47);
        state_.write16(0x2C47, 0);
        break;
    }
    case 0x08: // 15BF:45E5 .. 45EC
        out.ax = static_cast<std::uint16_t>(state_.read8(0x2DEA) & 1u);
        break;
    case 0x09: { // 15BF:309A .. 30C0 - original UINT16 MUL BX x 04A9
        const std::uint32_t product = std::uint32_t(input.bx) * 0x04A9u;
        const auto lo = static_cast<std::uint16_t>(product);
        const auto hi = static_cast<std::uint16_t>(product >> 16);
        state_.write16(0x2C4B, lo);
        state_.write16(0x2C4D, hi);
        state_.write16(0x2C4F, lo);
        state_.write16(0x2C51, hi);
        state_.write8(0x2C53, 0);
        out.ax = 0x04A9;
        out.dx = hi;
        // CLI/STI happen in original; IRQ interleaving not modeled.
        break;
    }
    case 0x0A: // 15BF:30C1 .. 30DA
        state_.write16(0x2C4B, state_.read16(0x2C4F));
        state_.write16(0x2C4D, state_.read16(0x2C51));
        state_.write8(0x2C53, 0);
        break;
    case 0x0B: // 15BF:30DB .. 30E1
        out.ax = state_.read8(0x2C53);
        break;
    case 0x0E: // 15BF:45DD .. 45E4
        out.ax = static_cast<std::uint16_t>(state_.read8(0x2D62) & 1u);
        break;
    case 0x13: // 15BF:3004 .. 3008
        state_.write8(0x2DBC, input.al());
        break;
    case 0x16: // 15BF:3009 .. 300D
        state_.write8(0x2DBD, input.al());
        break;
    case 0x12: { // 15BF:3E2B .. 3E5A - MIDI controller state, with B0 gate.
        const std::uint8_t command = input.al();
        const std::uint8_t value = static_cast<std::uint8_t>(input.bx);
        state_.write8(0x2DC4, command);
        state_.write8(0x2DC5, value);
        // Branch at 3E37: only suppression when (mode & 20h) && command >= B0h.
        if (!(state_.read8(0x2DC9) & 0x20u) || command < 0xB0u) {
            state_.write8(static_cast<std::uint16_t>(0x2BA7u + command), value);
        }
        break;
    }
    case 0x19: { // 15BF:335B .. 337A - conditional DOS 21h/3Eh close.
        const std::uint16_t handle = state_.read16(0x2DF3);
        if (handle != 0xFFFFu) {
            Registers dos_registers = input;
            dos_registers.ax = static_cast<std::uint16_t>(0x3E00u | input.al());
            dos_registers.bx = handle;
            // Original routine PUSH AX/BX but not DX across DOS service call.
            const Registers after = dos_->close_handle(handle, dos_registers);
            out.dx = after.dx;
        }
        state_.write8(0x2E10, 0);
        state_.write16(0x2DF3, 0xFFFFu);
        break;
    }
    case 0x1C: // 15BF:33AF .. 33B8
        out.ax = static_cast<std::uint16_t>(state_.read8(0x2DCA) & 1u);
        break;
    case 0x1D: // 15BF:3E5B .. 3E66; DS altered inside, restored by ISR
        state_.write8(0x2C61, static_cast<std::uint8_t>(input.bx));
        break;
    case 0x1F: // 15BF:45F2 .. 45F8
        state_.write8(0x2D62, 1);
        break;
    case 0x20: case 0x21: case 0x22: { // 15BF:372F,3771,3750
        if (state_.read8(0x2DF2) < 1u) {
            out.ax = 0xFFFFu;
            break;
        }
        const auto index = static_cast<std::uint8_t>(
            input.ah() == 0x20 ? 0x22 : input.ah() == 0x21 ? 0x04 : 0x26);
        PortIO &io = require_ports();
        const auto port_index = static_cast<std::uint16_t>(state_.read16(0x2DF0) + 4u);
        const auto port_data = static_cast<std::uint16_t>(port_index + 1u);
        io.out8(port_index, index);
        io.out8(port_data, static_cast<std::uint8_t>(input.bx));
        out.ax = 0;
        out.dx = port_data;
        break;
    }
    case 0x24: // 15BF:2F5F .. 2F65
        out.ax = 0x1234;
        out.dx = 0x5678;
        break;
    case 0x26: // 15BF:2E76 .. 2E7C
        state_.write8(0x2C0C, 1);
        break;
    case 0x29: { // 15BF:41F6 .. 4264 - joystick 201h polling, no invented calibration.
        PortIO &io = require_ports();
        state_.write16(0x2012, 0);
        state_.write16(0x2014, 0);
        const std::uint8_t initial = io.in8(0x0201);
        // Four ROL-like SHL carry tests: high nibble maps to 2019..2016.
        for (unsigned i = 0; i < 4; ++i) {
            const bool carry = ((initial >> (7u - i)) & 1u) != 0;
            state_.write8(static_cast<std::uint16_t>(0x2019u - i), carry ? 0 : 1);
        }
        const std::uint8_t write_value = static_cast<std::uint8_t>(initial << 4);
        for (unsigned i = 0; i < 0x28u; ++i) io.out8(0x0201, write_value);
        for (unsigned i = 0; i < 0x0320u; ++i) {
            const std::uint8_t val = io.in8(0x0201);
            state_.write16(0x2012, static_cast<std::uint16_t>(
                state_.read16(0x2012) + (val & 1u)));
            state_.write16(0x2014, static_cast<std::uint16_t>(
                state_.read16(0x2014) + ((val >> 1) & 1u)));
        }
        if (state_.read16(0x201A) == 0) {
            state_.write16(0x201A, state_.read16(0x2012));
            state_.write16(0x201C, state_.read16(0x2014));
        }
        // AX and DX are PUSHed and POPped in original. CLI persists only
        // until outer INT 63h IRET; interleaving is NOT reproduced here.
        break;
    }
    case 0x2A: case 0x2B: { // 15BF:41B3..41CC;41CD..41E6
        const bool b = input.ah() == 0x2B;
        const auto left = state_.read16(b ? 0x2014 : 0x2012);
        const auto divisor = state_.read16(b ? 0x201C : 0x201A);
        // Original MUL 0x40 has 32-bit DX:AX but XOR DX,DX truncates it.
        const auto low_product = static_cast<std::uint16_t>(std::uint32_t(left) * 0x40u);
        out.ax = divisor ? static_cast<std::uint16_t>(low_product / divisor) : low_product;
        out.dx = divisor ? static_cast<std::uint16_t>(low_product % divisor) : 0;
        // Original STC/CLC path is not propagated by IRET.
        break;
    }
    case 0x2C: // 15BF:41E7 .. 41F5
        out.ax = state_.read8(static_cast<std::uint16_t>(0x2016u + input.al()));
        break;
    case 0x2D: // 15BF:45ED .. 45F1
        out.ax = state_.read16(0x2C56);
        break;
    case 0x2E: { // 15BF:3E67 .. 3E76 -> helper 466A..469E.
        out.ax = 0xFFFF;
        if (state_.read16(0x201E) != 1u) {
            // AX=FFFFh => original DIV AX by itself: 0000:FFFF / FFFF = 1.
            state_.write16(0x2DB6, 1u);
            state_.write16(0x2DB4, 1u);
            PortIO &io = require_ports();
            io.out8(0x0043, 0x34);
            io.out8(0x0040, 0xFF);
            io.out8(0x0040, 0xFF);
        }
        state_.write16(0x201E, 1u);
        break;
    }
    case 0x30: // 15BF:4470 .. 4475; internal CLC doesn't change IRET flags
        out.ax = state_.read16(0x2C49);
        break;
    case 0x31: // 15BF:4CE1 .. 4CEC; BX <<= 1 (16-bit wrap)
        out.ax = static_cast<std::uint16_t>(input.al() & 0x3Fu);
        state_.write16(static_cast<std::uint16_t>(0x4BBFu +
            static_cast<std::uint16_t>(input.bx << 1)), out.ax);
        break;
    case 0x32: // 15BF:5675 .. 5678; return sentinel
        out.ax = 0xFFFFu;
        break;
    case 0x36: // 15BF:5664 .. 566F; index is incoming AL
        out.ax = state_.read16(static_cast<std::uint16_t>(0x4BEFu +
            static_cast<std::uint16_t>(input.al() << 1)));
        break;
    case 0x37: // 15BF:4866 .. 486B
        out.ax = state_.read16(0x2DF0);
        break;
    case 0x3E: // 15BF:3ED7 .. 3EDC
        state_.write8(0x3ED6, static_cast<std::uint8_t>(input.bx));
        break;
    case 0x43: // 15BF:34BB .. 34C0
        state_.write16(0x34B9, input.bx);
        break;
    case 0x44: // 15BF:4C61 .. 4C6A
        state_.write16(static_cast<std::uint16_t>(0x4BAFu +
            static_cast<std::uint16_t>(input.bx << 1)), 2u);
        break;
    case 0x46: // 15BF:389A .. 38A6; CLI, CS writes, STI, RET
        state_.write16(0x3896, input.bx);
        state_.write16(0x3898, input.dx);
        break;
    case 0x47: // 15BF:4C6B .. 4C74
        state_.write16(static_cast<std::uint16_t>(0x4BEFu +
            static_cast<std::uint16_t>(input.bx << 1)), 0u);
        break;
    case 0x4A: case 0x4B: case 0x4C: { // 15BF:2208,21DC,21EC
        const auto index = static_cast<std::uint8_t>(
            input.ah() == 0x4A ? 0x0A : input.ah() == 0x4B ? 0x0C : 0x2E);
        const std::uint8_t input_bl = static_cast<std::uint8_t>(input.bx);
        const auto value = static_cast<std::uint8_t>(input.ah() == 0x4C
            ? (input_bl | static_cast<std::uint8_t>(input_bl << 4)) : input_bl);
        PortIO &io = require_ports();
        const auto port_index = static_cast<std::uint16_t>(state_.read16(0x2DF0) + 4u);
        const auto port_data = static_cast<std::uint16_t>(port_index + 1u);
        io.out8(port_index, index);
        io.out8(port_data, value);
        out.ax = static_cast<std::uint16_t>((std::uint16_t(input.ah()) << 8) | value);
        out.dx = port_data;
        break;
    }
    case 0x4F: { // 15BF:5A3F .. 5A6B - write DSP, including after poll exhausts
        PortIO &io = require_ports();
        const std::uint16_t port = static_cast<std::uint16_t>(state_.read16(0x2DF0) + 0x0C);
        // jcxz -> in al,dx -> dec cx -> test bit7 -> jump to jcxz when busy.
        // A permanently busy port yields exactly 65535 status reads, then OUT.
        for (unsigned remaining = 0xFFFFu; remaining != 0; --remaining) {
            if ((io.in8(port) & 0x80u) == 0) break;
        }
        io.out8(port, input.al());
        // The callee pushes/pops AX/BX/CX/DX/BP/DI/SI/DS/ES.
        break;
    }
    case 0x50: { // 15BF:5A1E .. 5A3E - read DSP, even after poll exhausts
        PortIO &io = require_ports();
        const std::uint16_t base = state_.read16(0x2DF0);
        const std::uint16_t status = static_cast<std::uint16_t>(base + 0x0E);
        const std::uint16_t data = static_cast<std::uint16_t>(base + 0x0A);
        for (unsigned remaining = 0xFFFFu; remaining != 0; --remaining) {
            if ((io.in8(status) & 0x80u) != 0) break;
        }
        out.ax = io.in8(data); // xor ah,ah
        out.dx = data;         // AH=50 doesn't push/pop DX; IMPORTANT ABI effect
        break;
    }
    case 0x51: // 15BF:3DB3 .. 3DCA
        state_.write16(0x3DB1, 1);
        state_.write8(0x2B96, input.al());
        state_.write8(0x2B95, 0xFF);
        state_.write8(0x2BC7, 0);
        break;
    default:
        throw std::logic_error("Internal model invariant: excluded AH branch");
    }
    // Original INT63 handler saves returned AX/DX into CS scratch words,
    // restores GPR, decrements nesting depth, then reloads AX/DX for IRET.
    // Reentrant interleavings between these writes are not emulated here.
    state_.write16(0x30E2, out.ax);
    state_.write16(0x30E4, out.dx);
    state_.write16(0x3ED4, static_cast<std::uint16_t>(state_.read16(0x3ED4) - 1u));
    // Called routines can modify AX/DX. Outer INT63 preserves other GPR,
    // returns only those two and IRET restores original FLAGS.
    return out;
}

} // namespace worx21
