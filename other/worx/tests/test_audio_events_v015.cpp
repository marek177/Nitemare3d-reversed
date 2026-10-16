#include "worx21/audio_events.hpp"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <vector>

using namespace worx21;
#define CHECK(x) do { if (!(x)) { std::cerr << "FAIL " << __LINE__ << ": " << #x << '\n'; std::exit(2); } } while (0)

struct Memory final : FarByteMemory {
    std::array<std::uint8_t,65536> bytes{};
    std::uint16_t segment=0xABCD;
    std::vector<std::uint16_t> reads;
    std::uint8_t read8(std::uint16_t es,std::uint16_t di) override {
        CHECK(es==segment);
        reads.push_back(di);
        return bytes[di];
    }
    void write8(std::uint16_t es,std::uint16_t di,std::uint8_t value) override {
        CHECK(es==segment);bytes[di]=value;
    }
};

struct Tail final : MidiDispatchTail3a67 {
    unsigned calls=0;
    MidiDispatchRegisters last{};
    bool redirect=false;
    void dispatch_tail_3a67(CSState &cs,MidiDispatchRegisters &regs) override {
        ++calls;last=regs;
        CHECK(cs.read8(0x2DC4)==static_cast<std::uint8_t>(regs.ax&0x0Fu));
        CHECK(cs.read8(0x2DC8)==static_cast<std::uint8_t>(regs.ax&0xF0u));
        CHECK(cs.read8(0x2DC5)==static_cast<std::uint8_t>(regs.bx>>8u));
        CHECK(cs.read8(0x2DC6)==static_cast<std::uint8_t>(regs.bx));
        if(redirect) {
            cs.write16(0x2DC0,4);
            regs.di=200; // demonstrates the 45F9 far-memory cursor boundary
        }
    }
};

static void standard_table(CSState &s) {
    constexpr std::uint8_t counts[16]={0,0,0,0,0,0,0,0,2,2,2,2,1,1,2,0};
    for (unsigned i=0;i<16;i++)s.write8(static_cast<std::uint16_t>(0x2DA4u+i),counts[i]);
}
static MidiStepResult step(CSState &s,Memory &m,Tail *tail=nullptr,
                           MidiReplayCalls *replay=nullptr,
                           std::uint16_t at=100,std::uint16_t incoming_ax=0,
                           std::size_t budget=10) {
    return midi_event_step_44ee(s,m,m.segment,at,incoming_ax,tail,replay,nullptr,budget);
}

static void test_explicit_channel_and_delta() {
    CSState s;Memory m;Tail cb;standard_table(s);
    s.write16(0x2DC0,3);
    m.bytes[100]=0x90;m.bytes[101]=0x3C;m.bytes[102]=0x7F;
    m.bytes[103]=0x81;m.bytes[104]=0x01;
    const auto r=step(s,m,&cb);
    CHECK(r.kind==MidiStepKind::channel_event && r.status==0x90);
    CHECK(r.table_data_count==2 && r.dispatch_bx==0x3C7F && r.dispatch_cx==1);
    CHECK(cb.calls==1 && cb.last.ax==0x0090 && cb.last.bx==0x3C7F);
    CHECK(cb.last.si==9 && cb.last.cx==1 && cb.last.es==m.segment && cb.last.di==103);
    CHECK(s.read16(0x2D63+6)==0x0090); // full WORD cached, not a byte
    CHECK(r.next_delta==129 && r.next_di==105 && r.vlq_bytes==2 && r.index_committed==3);
    CHECK(s.read16(0x2D22+6)==105 && s.read16(0x2CA2+12)==129);
    CHECK(s.read16(0x2CA4+12)==0);
    CHECK((m.reads==std::vector<std::uint16_t>{100,101,102,103,104}));
}

static void test_running_status_stale_data_register() {
    CSState s;Memory m;Tail cb;standard_table(s);
    s.write16(0x2DC0,1);s.write16(0x2D63+2,0x00C3);
    m.bytes[100]=0x35;m.bytes[101]=0;
    auto r=step(s,m,&cb);
    CHECK(r.kind==MidiStepKind::channel_event && r.status==0xC3);
    CHECK(r.table_data_count==1 && cb.last.ax==0xC3);
    CHECK(cb.last.bx==0x3502 && cb.last.cx==0 && cb.last.di==101);
    CHECK(s.read8(0x2DC5)==0x35 && s.read8(0x2DC6)==0x02);
    CHECK(r.next_delta==0 && r.next_di==102);
    CHECK(s.read16(0x2D63+2)==0xC3);
    CHECK((m.reads==std::vector<std::uint16_t>{100,100,101}));
    // Status F0: original nibble lookup is zero; BH and BL remain from
    // the track's doubled index (BX), not forcibly initialized to zero.
    s.write16(0x2DC0,3);
    m.reads.clear();m.bytes[100]=0xF0;m.bytes[101]=0;
    r=step(s,m,&cb);
    CHECK(r.table_data_count==0 && cb.last.bx==6 && cb.last.cx==0 && cb.last.si==15);
    CHECK(s.read16(0x2D63+6)==0xF0);
    CHECK((m.reads==std::vector<std::uint16_t>{100,101}));
}

static void test_downstream_mutation_and_alias() {
    CSState s;Memory m;Tail cb;standard_table(s);
    s.write16(0x2DC0,2);m.bytes[100]=0x90;m.bytes[101]=60;m.bytes[102]=100;
    m.bytes[103]=0; m.bytes[200]=0x81;m.bytes[201]=0x7f;
    cb.redirect=true;
    const auto r=step(s,m,&cb);
    CHECK(r.index_committed==4 && r.next_di==202 && r.next_delta==255);
    CHECK(s.read16(0x2D22+8)==202 && s.read16(0x2CA2+16)==255);
    CHECK(s.read16(0x2D22+4)==0);
    CHECK(s.read16(0x2DC0)==4);
    // Out-of-range index 79 aliases pointer storage with GLOBAL CS:2DC0.
    // This is a synthetic instruction-state test, NOT proof of reachability.
    CSState alias;Memory mm;Tail t;standard_table(alias);
    alias.write16(0x2DC0,79);
    mm.bytes[100]=0x90;mm.bytes[101]=1;mm.bytes[102]=2;mm.bytes[103]=0;
    auto out=step(alias,mm,&t);
    CHECK(out.index_committed==79 && out.next_di==104);
    CHECK(alias.read16(0x2DC0)==104); // 2D22 + 2*79 == 2DC0
    CHECK(alias.read16(static_cast<std::uint16_t>(0x2CA2+4*79))==0);
}

static void test_meta_event_paths() {
    CSState s;Memory m;Tail cb;standard_table(s);
    s.write16(0x2DC0,1);s.write16(0x2D63+2,0x90);
    m.bytes[100]=0xFF;m.bytes[101]=0x01;m.bytes[102]=2;
    m.bytes[103]=0x55;m.bytes[104]=0x66;m.bytes[105]=7;
    auto r=step(s,m,&cb);
    CHECK(r.kind==MidiStepKind::meta_unknown && r.meta_type==1);
    CHECK(r.next_di==106 && r.next_delta==7 && r.index_committed==1);
    CHECK(s.read16(0x2D22+2)==106 && s.read16(0x2D63+2)==0x90);
    CHECK(cb.calls==0);
    CHECK((m.reads==std::vector<std::uint16_t>{100,101,102,105}));

    CSState tempo;Memory tm;standard_table(tempo);
    tempo.write16(0x2DC0,1);tempo.write16(0x2C5A,4);
    tempo.write16(0x201E,1); // explicitly bypass PIT physical IO
    tm.bytes[100]=0xFF;tm.bytes[101]=0x51;tm.bytes[102]=3;
    tm.bytes[103]=0;tm.bytes[104]=0x10;tm.bytes[105]=0;tm.bytes[106]=0;
    r=step(tempo,tm,&cb);
    CHECK(r.kind==MidiStepKind::meta_tempo && r.meta_type==0x51);
    CHECK(r.next_di==107 && r.next_delta==0);
    CHECK(tempo.read16(0x2C49)!=0 && tempo.read16(0x2D22+2)==107);
    CHECK(cb.calls==0);
    CHECK((tm.reads==std::vector<std::uint16_t>{100,101,103,104,105,106}));

    CSState eot;Memory em;standard_table(eot);
    eot.write16(0x2DC0,0);eot.write16(0x2C58,1);
    eot.write16(0x2C62,1);eot.write8(0x2D62,1);
    em.bytes[100]=0xFF;em.bytes[101]=0x2F;em.bytes[102]=0x80;
    r=step(eot,em,&cb);
    CHECK(r.kind==MidiStepKind::meta_end_track && r.next_di==102);
    CHECK(r.vlq_bytes==0 && r.eot.kind==MidiEotKind::all_tracks_stopped);
    CHECK(eot.read8(0x2D62)==0 && eot.read16(0x2C62)==0);
    CHECK((em.reads==std::vector<std::uint16_t>{100,101})); // no length read
}

static void test_fail_closed_on_missing_backend_or_unending_vlq() {
    CSState s;Memory m;standard_table(s);
    s.write16(0x2DC0,0);
    m.bytes[100]=0x90;m.bytes[101]=4;m.bytes[102]=8;m.bytes[103]=0;
    bool failed=false;
    try { (void)step(s,m,nullptr); }
    catch(const std::logic_error &) {failed=true;}
    CHECK(failed && s.read8(0x2DC8)==0x90 && s.read8(0x2DC5)==4);
    CHECK(s.read16(0x2D22)==0);
    // After an accepted callback, an unterminated VLQ fails *as a host
    // safeguard*, without pretending the original had a finite read limit.
    Tail cb;failed=false;
    m.bytes[103]=0x80;m.bytes[104]=0x80;
    try { (void)step(s,m,&cb,nullptr,100,0,2); }
    catch(const std::runtime_error &) {failed=true;}
    CHECK(failed && cb.calls==1 && s.read16(0x2D22)==0);
}

int main() {
    test_explicit_channel_and_delta();
    test_running_status_stale_data_register();
    test_downstream_mutation_and_alias();
    test_meta_event_paths();
    test_fail_closed_on_missing_backend_or_unending_vlq();
    std::cout << "PASS: 44EE channel/running/FF meta, 3A4D prefix, 45F9 delta/commit\n";
}
