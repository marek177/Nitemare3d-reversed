#include "worx21/compat.hpp"

#include <stdexcept>

namespace worx21 {

Registers N3dAdapter::call(std::uint8_t command, std::uint8_t al, std::uint16_t bx,
                           std::uint16_t dx, std::uint16_t di,
                           const Registers &precall_context) {
    Registers input = precall_context;
    input.ax = static_cast<std::uint16_t>((std::uint16_t(command) << 8) | al);
    input.bx = bx;
    input.dx = dx;
    input.di = di;
    // DO NOT zero CX or SI; the exposed N3D wrapper does not initialize them.
    Registers output = backend_.interrupt63(input);
    cached_ = {output.ax, output.bx, output.dx, output.di};
    return output;
}

std::uint16_t N3dAdapter::packed_control_pair(std::uint8_t a, std::uint8_t b) noexcept {
    return static_cast<std::uint16_t>((std::uint16_t(a) << 4) | std::uint16_t(b));
}

Registers N3dAdapter::autodetect_sound_blaster(const Registers &ctx) {
    return call(0x01, 0, 0, 0, 0, ctx);
}
Registers N3dAdapter::disable_digitized_route(const Registers &ctx) {
    return call(0x04, 0, 0, 0, 0, ctx);
}
Registers N3dAdapter::stop_music(const Registers &ctx) {
    return call(0x0D, 0, 0, 0, 0, ctx);
}
Registers N3dAdapter::stop_pc_speaker_sfx(const Registers &ctx) {
    return call(0x15, 0, 0, 0, 0, ctx);
}
Registers N3dAdapter::query_pc_speaker_sfx(const Registers &ctx) {
    return call(0x1C, 0, 0, 0, 0, ctx);
}
Registers N3dAdapter::sfx_control_pair(std::uint8_t a, std::uint8_t b,
                                       const Registers &ctx) {
    return call(0x21, 0, packed_control_pair(a, b), 0, 0, ctx);
}
Registers N3dAdapter::music_control_pair(std::uint8_t a, std::uint8_t b,
                                         const Registers &ctx) {
    return call(0x22, 0, packed_control_pair(a, b), 0, 0, ctx);
}
Registers N3dAdapter::joystick_status(std::uint8_t index, const Registers &ctx) {
    return call(0x2C, index, 0, 0, 0, ctx);
}

void TraceBackend::queue_response(const Registers &response) { responses_.push_back(response); }
Registers TraceBackend::interrupt63(const Registers &input) {
    requests_.push_back(input);
    if (cursor_ >= responses_.size()) {
        throw std::logic_error("No recorded INT 63h response: hardware parity is UNKNOWN");
    }
    return responses_[cursor_++];
}

std::uint16_t OplReference::note_to_fnum_block(std::uint8_t midi_note) noexcept {
    const int note = midi_note >= 13 ? int(midi_note) - 13 : 0;
    const int octave_note = note % 12;
    const int block = (note / 12) < 7 ? (note / 12) : 7;
    return static_cast<std::uint16_t>(kNoteFnums[octave_note] | (block << 10));
}
std::uint8_t OplReference::calculate_attenuation(std::uint8_t instrument_op_level,
                                                  std::uint8_t channel_volume) noexcept {
    // MIDI velocity is absent from the candidate WORX v2.1 volume calculation.
    const unsigned op_volume = 0x3F - (instrument_op_level & 0x3F);
    const unsigned scaled = (op_volume * channel_volume) >> 7;
    return static_cast<std::uint8_t>((0x3F - scaled) & 0xFF);
}
OplReference::OplReference(std::uint8_t melodic_voice_count)
    : voices_(melodic_voice_count) {}
std::uint8_t OplReference::allocate_voice(std::uint8_t source, std::uint8_t midi_channel) {
    // Cross-game priority: inactive matching voice > unallocated > inactive foreign;
    // never steal an actively playing voice. This is a provisional algorithm.
    int same_idle = -1;
    int fresh = -1;
    int other_idle = -1;
    for (std::size_t i = 0; i < voices_.size(); ++i) {
        const Voice &v = voices_[i];
        if (v.allocated && v.source == source && v.midi_channel == midi_channel && !v.active) {
            same_idle = static_cast<int>(i);
            break;
        }
        if (!v.allocated && fresh == -1) fresh = static_cast<int>(i);
        if (v.allocated && !v.active && other_idle == -1 &&
            (v.source != source || v.midi_channel != midi_channel)) {
            other_idle = static_cast<int>(i);
        }
    }
    const int selected = same_idle != -1 ? same_idle : (fresh != -1 ? fresh : other_idle);
    if (selected == -1 || selected > 0xFE) return 0xFF;
    Voice &v = voices_[static_cast<std::size_t>(selected)];
    v.allocated = true;
    v.source = source;
    v.midi_channel = midi_channel;
    return static_cast<std::uint8_t>(selected);
}
void OplReference::set_active(std::uint8_t index, bool active) {
    if (index >= voices_.size()) throw std::out_of_range("OPL voice index");
    voices_[index].active = active;
}
} // namespace worx21
