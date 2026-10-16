#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <vector>

namespace worx21 {

// Register-level Nitemare DOS v2.0 WORX INT 63h compatibility boundary.
// This is NOT a complete DOS interrupt controller, OPL synthesizer or PCM driver.
struct Registers {
    std::uint16_t ax = 0;
    std::uint16_t bx = 0;
    std::uint16_t cx = 0;
    std::uint16_t dx = 0;
    std::uint16_t si = 0;
    std::uint16_t di = 0;
    bool carry = false;
    std::uint8_t ah() const noexcept { return static_cast<std::uint8_t>(ax >> 8); }
    std::uint8_t al() const noexcept { return static_cast<std::uint8_t>(ax & 0xFFu); }
};

struct CachedResult {
    // The N3D central wrapper caches these in DGROUP at +413E/+4140/+4142/+3F4E.
    std::uint16_t ax = 0;
    std::uint16_t bx = 0;
    std::uint16_t dx = 0;
    std::uint16_t di = 0;
};

class Backend {
public:
    virtual ~Backend() = default;
    // Caller must supply the exact existing CX/SI values; no invented constants.
    // All device effects and the resulting CF/register values are backend-owned.
    virtual Registers interrupt63(const Registers &input) = 0;
};

class N3dAdapter {
public:
    explicit N3dAdapter(Backend &backend) noexcept : backend_(backend) {}

    // AH = command; AL = byte argument; BX/DX/DI = word arguments.
    // The other input registers are inherited from the supplied pre-call context.
    Registers call(std::uint8_t command, std::uint8_t al, std::uint16_t bx,
                   std::uint16_t dx, std::uint16_t di,
                   const Registers &precall_context);
    const CachedResult &cached() const noexcept { return cached_; }

    // Only the following higher-level meanings are independently corroborated
    // by N3D call sites. No implicit music/SFX state or hardware return values
    // are invented by this layer.
    Registers autodetect_sound_blaster(const Registers &context);
    Registers disable_digitized_route(const Registers &context);
    Registers stop_music(const Registers &context);
    Registers stop_pc_speaker_sfx(const Registers &context);
    Registers query_pc_speaker_sfx(const Registers &context);
    Registers sfx_control_pair(std::uint8_t a, std::uint8_t b, const Registers &context);
    Registers music_control_pair(std::uint8_t a, std::uint8_t b, const Registers &context);
    Registers joystick_status(std::uint8_t index, const Registers &context);

    // N3D decompiler shows (a << 4) | b, with no explicit nibble masks.
    // Word-level, NOT a saturating/clamping operation. Keep out-of-range bits.
    static std::uint16_t packed_control_pair(std::uint8_t a, std::uint8_t b) noexcept;

private:
    Backend &backend_;
    CachedResult cached_{};
};

// Test/trace backend. Responses must be scripted explicitly, rather than
// silently assumed to be successful DSP/OPL/PCM operations.
class TraceBackend final : public Backend {
public:
    void queue_response(const Registers &response);
    Registers interrupt63(const Registers &input) override;
    const std::vector<Registers> &requests() const noexcept { return requests_; }
    std::size_t unused_responses() const noexcept { return responses_.size() - cursor_; }
private:
    std::vector<Registers> requests_{};
    std::vector<Registers> responses_{};
    std::size_t cursor_ = 0;
};

// Cross-game *candidate* (ScummVM Dark Seed CD WORX 2.1). Must be verified
// against Nitemare's exact 16-bit OPL assembly/table BEFORE declaring parity.
class OplReference {
public:
    static constexpr std::array<std::uint16_t, 12> kNoteFnums = {
        0x16B, 0x181, 0x198, 0x1B0, 0x1CA, 0x1E5,
        0x202, 0x220, 0x241, 0x263, 0x287, 0x2AE
    };
    static std::uint16_t note_to_fnum_block(std::uint8_t midi_note) noexcept;
    static std::uint8_t calculate_attenuation(std::uint8_t instrument_op_level,
                                               std::uint8_t channel_volume) noexcept;

    struct Voice {
        bool allocated = false;
        bool active = false;
        std::uint8_t source = 0;
        std::uint8_t midi_channel = 0;
    };
    // Caller chooses the actual melodic hardware voice count (not always 9).
    explicit OplReference(std::uint8_t melodic_voice_count);
    std::uint8_t allocate_voice(std::uint8_t source, std::uint8_t midi_channel);
    void set_active(std::uint8_t index, bool active);
    const std::vector<Voice> &voices() const noexcept { return voices_; }
private:
    std::vector<Voice> voices_;
};

} // namespace worx21
