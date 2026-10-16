#pragma once

#include "worx21/compat.hpp"

#include <array>
#include <cstdint>

namespace worx21 {

// 64 KiB WORX CS-segment state; the REAL initial image + post-init state
// must be supplied by the caller. A zero-filled test state is NOT a claim
// about the memory layout after the original WORX initialization.
class CSState {
public:
    std::uint8_t read8(std::uint16_t offset) const noexcept;
    std::uint16_t read16(std::uint16_t offset) const noexcept;
    void write8(std::uint16_t offset, std::uint8_t value) noexcept;
    void write16(std::uint16_t offset, std::uint16_t value) noexcept;
private:
    std::array<std::uint8_t, 65536> bytes_{};
};

class PortIO {
public:
    virtual ~PortIO() = default;
    virtual std::uint8_t in8(std::uint16_t port) = 0;
    virtual void out8(std::uint16_t port, std::uint8_t value) = 0;
};

// External INT 21h AH=3Eh boundary for WORX AH=19h. The DOS handler's
// register/side effect behavior is a supplied service, not guessed. Original
// WORX restores AX/BX but not DX before it returns to its INT 63h dispatcher.
class DosFileIO {
public:
    virtual ~DosFileIO() = default;
    virtual Registers close_handle(std::uint16_t handle, const Registers &dos_input) = 0;
};

// 41 original-machine-audited entrypoints: 37 v0.11 contracts and four v0.12
// additional contracts (12h,19h,29h,2Eh), with explicit external DOS/port
// boundaries. All remaining 41 selectors in 00..51 (38 non-null and 3
// initial-image null slots) THROW instead of inventing DSP, OPL or PCM behavior.
//
// Outer INT 63h restores FLAGS with IRET; this model does not carry the
// transient callee's CLC/STC out to the caller. Non-AX/DX GPR are restored.
class KnownLeafBackend final : public Backend {
public:
    explicit KnownLeafBackend(CSState &state, PortIO *ports = nullptr,
                              DosFileIO *dos = nullptr) noexcept
        : state_(state), ports_(ports), dos_(dos) {}
    Registers interrupt63(const Registers &input) override;
private:
    CSState &state_;
    PortIO *ports_;
    DosFileIO *dos_;
    PortIO &require_ports();
};

} // namespace worx21
