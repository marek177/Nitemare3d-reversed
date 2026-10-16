#include "worx21/compat.hpp"
#include <cstdlib>
#include <iostream>
#include <stdexcept>
using namespace worx21;

static void require(bool ok, const char *expr, int line) {
    if (!ok) { std::cerr << "TEST FAILURE line " << line << ": " << expr << "\n"; std::exit(2); }
}
#define assert(expr) require(static_cast<bool>(expr), #expr, __LINE__)

int main() {
    TraceBackend backend;
    N3dAdapter adapter(backend);
    Registers base{};
    base.cx = 0x1357;
    base.si = 0x2468;
    base.ax = 0xAABB;
    base.carry = true;
    Registers response{};
    response.ax = 0xCF37;
    response.bx = 0x1010;
    response.cx = 0xAAAA;
    response.dx = 0xBABE;
    response.si = 0xBBBB;
    response.di = 0xABCD;
    response.carry = true;
    backend.queue_response(response);
    auto out = adapter.call(0x51, 0xEF, 0x1234, 0x5678, 0x9ABC, base);
    const auto &in = backend.requests().at(0);
    assert(in.ah() == 0x51 && in.al() == 0xEF && in.ax == 0x51EF);
    assert(in.bx == 0x1234 && in.dx == 0x5678 && in.di == 0x9ABC);
    assert(in.cx == 0x1357 && in.si == 0x2468);
    assert(out.ax == 0xCF37 && out.carry);
    assert(adapter.cached().ax == 0xCF37 && adapter.cached().bx == 0x1010);
    assert(adapter.cached().dx == 0xBABE && adapter.cached().di == 0xABCD);

    assert(N3dAdapter::packed_control_pair(0x0A, 0x0F) == 0xAF);
    assert(N3dAdapter::packed_control_pair(0xFF, 0xFF) == 0xFFF);
    backend.queue_response({});
    adapter.sfx_control_pair(0x05, 0x0E, base);
    const auto &in2 = backend.requests().at(1);
    assert(in2.ah() == 0x21 && in2.bx == 0x005E && in2.cx == base.cx);
    backend.queue_response({});
    adapter.music_control_pair(0x02, 0x0B, base);
    assert(backend.requests().at(2).ah() == 0x22 && backend.requests().at(2).bx == 0x2B);
    backend.queue_response({});
    adapter.joystick_status(3, base);
    assert(backend.requests().at(3).ah() == 0x2C && backend.requests().at(3).al() == 3);
    backend.queue_response({});
    adapter.stop_music(base);
    assert(backend.requests().at(4).ah() == 0x0D);
    backend.queue_response({});
    adapter.autodetect_sound_blaster(base);
    assert(backend.requests().at(5).ah() == 0x01);

    backend.queue_response({});
    adapter.disable_digitized_route(base);
    assert(backend.requests().at(6).ah() == 0x04);
    backend.queue_response({});
    adapter.stop_pc_speaker_sfx(base);
    assert(backend.requests().at(7).ah() == 0x15);
    backend.queue_response({});
    adapter.query_pc_speaker_sfx(base);
    assert(backend.requests().at(8).ah() == 0x1C);

    bool no_fake_success = false;
    try { adapter.stop_pc_speaker_sfx(base); }
    catch (const std::logic_error &) { no_fake_success = true; }
    assert(no_fake_success);

    assert(OplReference::note_to_fnum_block(0) == 0x16B);
    assert(OplReference::note_to_fnum_block(13) == 0x16B);
    assert(OplReference::note_to_fnum_block(24) == 0x2AE);
    assert(OplReference::note_to_fnum_block(25) == (0x16B | 0x400));
    assert(OplReference::note_to_fnum_block(127) == (0x202 | (7 << 10)));
    assert(OplReference::calculate_attenuation(0, 0x7F) == 1);
    assert(OplReference::calculate_attenuation(0x3F, 0x7F) == 63);

    OplReference allocator(2);
    assert(allocator.allocate_voice(1, 3) == 0);
    allocator.set_active(0, true);
    assert(allocator.allocate_voice(2, 2) == 1);
    allocator.set_active(1, true);
    assert(allocator.allocate_voice(1, 4) == 0xFF); // cannot steal active notes
    allocator.set_active(0, false);
    assert(allocator.allocate_voice(1, 3) == 0); // reuse matching inactive
    assert(allocator.allocate_voice(5, 5) == 0); // reuse foreign inactive
    std::cout << "PASS: ABI/OPL reference tests (synthetic; not original runtime parity)\n";
}
