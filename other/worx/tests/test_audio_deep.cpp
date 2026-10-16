#include "worx21/audio_deep.hpp"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <utility>

using namespace worx21;
#define CHECK(expr) do { if (!(expr)) { std::cerr << "FAIL " << __FILE__ << ':' << __LINE__ << " " << #expr << '\n'; std::exit(2); } } while(0)

struct Memory final : FarByteMemory {
    std::array<std::uint8_t,65536> bytes{};
    std::uint16_t segment = 0xA0B0;
    std::uint8_t read8(std::uint16_t seg,std::uint16_t off) override {
        CHECK(seg==segment); return bytes[off];
    }
    void write8(std::uint16_t seg,std::uint16_t off,std::uint8_t value) override {
        CHECK(seg==segment); bytes[off]=value;
    }
};
struct Replay final : MidiReplayCalls {
    int seen_4265=0, seen_4389=0;
    std::uint16_t seen_es=0,seen_di=0;
    void replay_4265(CSState &s,std::uint16_t es,std::uint16_t di) override {
        ++seen_4265; seen_es=es; seen_di=di;
        s.write8(0x2D62,1); // caller-defined side effect, not inferred by adapter
    }
    void replay_4389(CSState &,std::uint16_t es,std::uint16_t di) override {
        ++seen_4389;seen_es=es;seen_di=di;
    }
};
struct Xms final : XmsFarService {
    std::uint16_t returned=1;
    unsigned calls=0;
    XmsRefillRequest seen{};
    std::uint16_t invoke(const XmsRefillRequest &req,CSState &s) override {
        ++calls;seen=req;
        CHECK(s.read16(0x21CC)==0x100);
        CHECK(s.read16(0x21CE)==0xABCD); // stale word is not cleared by original
        CHECK(s.read16(0x21D6)==0);
        return returned;
    }
};
struct Reader final : Read312e {
    unsigned calls=0;
    std::uint16_t result=0;
    std::uint16_t seen_bx=0,seen_es=0,seen_di=0;
    bool mutate_low=false;
    std::uint16_t call_312e(std::uint16_t bx,std::uint16_t es,std::uint16_t di,
                             CSState &s) override {
        ++calls;seen_bx=bx;seen_es=es;seen_di=di;
        if(mutate_low) s.write16(0x48DF,0x0100);
        return result;
    }
};

static void test_midi_gate() {
    CSState s;
    s.write16(0x2DC0,3);
    const auto flag_at=static_cast<std::uint16_t>(0x2C62+2*3);
    const auto delta_lo=static_cast<std::uint16_t>(0x2CA2+4*3);
    const auto delta_hi=static_cast<std::uint16_t>(0x2CA4+4*3);
    const auto ptr=static_cast<std::uint16_t>(0x2D22+2*3);
    s.write16(flag_at,2); // inactive even if other status bits set
    auto r=midi_track_gate_44b3(s);
    CHECK(r.kind==MidiGateKind::inactive && r.index==3);
    s.write16(flag_at,1);s.write16(delta_lo,2);s.write16(delta_hi,0);
    r=midi_track_gate_44b3(s);
    CHECK(r.kind==MidiGateKind::tick_decremented && s.read16(delta_lo)==1 && s.read16(delta_hi)==0);
    s.write16(delta_lo,0);s.write16(delta_hi,1);
    r=midi_track_gate_44b3(s);
    CHECK(r.kind==MidiGateKind::tick_decremented && s.read16(delta_lo)==0xFFFF && s.read16(delta_hi)==0);
    s.write16(delta_lo,0);s.write16(delta_hi,0);
    s.write16(ptr,0xFFFE);s.write16(0x2C5F,0x5566);
    r=midi_track_gate_44b3(s);
    CHECK(r.kind==MidiGateKind::event_ready && r.index==3 && r.es==0x5566 && r.di==0xFFFE);
    CHECK(s.read16(ptr)==0xFFFE); // reading event happens AFTER this gate
}

static void test_meta_skip() {
    Memory m;m.bytes[0xFFFF]=0xFE;
    CHECK(midi_unknown_meta_skip_4553(m,m.segment,0xFFFF)==0x00FE);
    m.bytes[10]=0;
    CHECK(midi_unknown_meta_skip_4553(m,m.segment,10)==11);
    m.bytes[20]=0x80; // length byte 0x80 is NOT a VLQ continuation
    CHECK(midi_unknown_meta_skip_4553(m,m.segment,20)==149);
}

static void test_eot() {
    CSState s;Replay calls;
    s.write16(0x2DC0,2);s.write16(0x2C58,4);
    s.write16(0x2C62,2); // TEST FFFF sees this as active even though bit 0 is 0
    s.write16(0x2C62+2*2,1);
    s.write8(0x2D62,1);
    auto r=midi_end_track_458c(s,&calls);
    CHECK(r.kind==MidiEotKind::another_track_seen && r.scanned==1);
    CHECK(r.next_index==3 && s.read16(0x2DC0)==3); // NOT the found index 0
    CHECK(s.read16(0x2C62+2*2)==0 && calls.seen_4265==0);

    for(int i=0;i<4;++i)s.write16(static_cast<std::uint16_t>(0x2C62+i*2),0);
    s.write16(0x2DC0,1);s.write8(0x2C61,0);
    r=midi_end_track_458c(s,nullptr);
    CHECK(r.kind==MidiEotKind::all_tracks_stopped && r.scanned==4);
    CHECK(s.read8(0x2D62)==0 && s.read16(0x2DC0)==1);

    s.write8(0x2C61,1);s.write8(0x2C5C,1);
    s.write16(0x2C5D,0xFFFA);s.write16(0x2C5F,0xBEEF);
    r=midi_end_track_458c(s,&calls);
    CHECK(r.kind==MidiEotKind::replay_4389 && r.scanned==4);
    CHECK(calls.seen_4389==1 && calls.seen_es==0xBEEF && calls.seen_di==0xFFFA);
    s.write8(0x2C5C,3);
    r=midi_end_track_458c(s,&calls);
    CHECK(r.kind==MidiEotKind::replay_4265 && calls.seen_4265==1);
    CHECK(s.read8(0x2D62)==1); // injected 4265 modifies state

    bool threw=false;
    try {(void)midi_end_track_458c(s,nullptr);}catch(const std::logic_error &){threw=true;}
    CHECK(threw); // no fabricated replay

    // Count=0: scan reaches CS:2D62 after 128 * 2-byte strides.
    // This is a GLOBAL music enabled byte, but TEST [BX+2C62],FFFF
    // misreads it as a track-active word at scan step 129.
    CSState alias;
    alias.write8(0x2D62,1); alias.write16(0x2C58,0);
    r=midi_end_track_458c(alias,nullptr);
    CHECK(r.kind==MidiEotKind::another_track_seen && r.scanned==129);
    CHECK(r.next_index==1 && alias.read8(0x2D62)==1);
    // With all reachable 16-bit words zero, LOOP really takes 65536 scans.
    CSState none;
    none.write16(0x2C58,0);
    r=midi_end_track_458c(none,nullptr);
    CHECK(r.kind==MidiEotKind::all_tracks_stopped && r.scanned==65536);
    CHECK(none.read8(0x2D62)==0);
}

static void test_xms_refill() {
    CSState s;Xms cb;
    s.write16(0x21C8,0x1234);s.write16(0x21CA,0xABBA);
    s.write16(0x21C6,0x7777);s.write16(0x21CE,0xABCD);
    s.write16(0x4BCF+2,0xFFF8); // current voice read cursor
    s.write16(0x4B6F+2,3);      // resource index
    s.write16(0x20C6+12,0x0020);
    s.write16(0x20C8+12,0x1111);
    auto result=xms_refill_packet_5863(s,2,0xBEEF,0x15BF,0x15BF,cb);
    CHECK(cb.calls==1 && cb.seen.ah==0x000B);
    CHECK(cb.seen.driver_ip==0x1234 && cb.seen.driver_cs==0xABBA);
    CHECK(cb.seen.ds==0x15BF && cb.seen.si==0x21CC && cb.seen.bx==12);
    CHECK(s.read16(0x21D8)==0x4DED && s.read16(0x21DA)==0x15BF);
    CHECK(s.read16(0x21D0)==0x7777 && s.read16(0x21D2)==0x0018);
    CHECK(s.read16(0x21D4)==0x1112 && s.read16(0x54ED+2)==0xFFF8);
    CHECK(result.service_returned_one && result.service_ax==1 && result.final_ax==0xBEEF);
    CHECK(s.read16(0x21CE)==0xABCD);
    cb.returned=0x5555;
    result=xms_refill_packet_5863(s,2,0xCAFE,0x3000,0xA100,cb);
    CHECK(!result.service_returned_one && result.final_ax==0xCAFE);
    CHECK(s.read16(0x21DA)==0xA100 && cb.seen.ds==0x3000);
    s.write16(0x4BCF+14,0);s.write16(0x4B6F+14,0);
    result=xms_refill_packet_5863(s,14,123,0xA100,0xA100,cb);
    CHECK(s.read16(0x21D8)==0x53ED); // eight voices have 256-byte slots
    CHECK(cb.seen.bx==0);
}

static void test_stream_modes() {
    CSState s;
    s.write16(0x48DF,0x0010);s.write16(0x48E1,2);s.write16(0x48DB,0x0030);
    auto a=stream_mode_0c_5fd2(s);
    CHECK(!a.underflow && a.remaining==0x0001FFE0u);
    CHECK(s.read16(0x48DF)==0xFFE0 && s.read16(0x48E1)==1);
    s.write16(0x48DF,0x0020);s.write16(0x48E1,0);s.write16(0x48DB,0x0030);
    a=stream_mode_0c_5fd2(s);
    CHECK(a.underflow && a.remaining==0);
    CHECK(s.read16(0x48DF)==0 && s.read16(0x48E1)==0);
    s.write16(0x48DF,0);s.write16(0x48E1,1);s.write16(0x48DB,0xFFFF);
    a=stream_mode_0c_5fd2(s);
    CHECK(!a.underflow && a.remaining==1);
    s.write16(0x48DF,0);s.write16(0x48E1,0);s.write16(0x48DB,0);
    a=stream_mode_0c_5fd2(s);
    CHECK(!a.underflow && a.remaining==0);

    Reader reader;reader.result=9;
    s.write16(0x48DF,4);s.write16(0x48E1,0x1234);
    auto b=stream_mode_08_5fbf(s,0x15BF,reader);
    CHECK(reader.calls==1 && reader.seen_bx==4 && reader.seen_es==0x15BF && reader.seen_di==0x5E69);
    CHECK(b.bytes_reported==9 && b.remaining_low==0xFFFB);
    CHECK(s.read16(0x48DF)==0xFFFB && s.read16(0x48E1)==0x1234); // NO SBB
    reader.result=4;reader.mutate_low=true;
    b=stream_mode_08_5fbf(s,0x15BF,reader);
    CHECK(reader.seen_bx==0xFFFB && b.remaining_low==0xFC); // post-call CS memory is re-read
}

int main() {
    test_midi_gate();test_meta_skip();test_eot();test_xms_refill();test_stream_modes();
    std::cout << "PASS: original machine 44B3 / 4553 / 458C / 5863 / 5FBF / 5FD2 subcontracts\n";
}
