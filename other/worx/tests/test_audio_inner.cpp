#include "worx21/audio_inner.hpp"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using namespace worx21;
#define CHECK(expr) do { if (!(expr)) { std::cerr << "FAIL line " << __LINE__ << ": " << #expr << '\n'; std::exit(2); } } while(0)

struct Ports final : PortIO {
    std::vector<std::uint8_t> samples;
    unsigned reads = 0;
    std::vector<std::pair<std::uint16_t, std::uint8_t>> outputs;
    std::uint8_t in8(std::uint16_t port) override {
        CHECK(port == 2);
        CHECK(reads < samples.size());
        return samples[reads++];
    }
    void out8(std::uint16_t port, std::uint8_t value) override {
        outputs.emplace_back(port, value);
    }
    void set(std::uint8_t first, std::uint8_t second) {
        samples = {first,second}; reads=0; outputs.clear();
    }
    void expect_two_reads() {
        CHECK(reads==2);
        CHECK(outputs.size()==1 && outputs[0].first==0x0C && outputs[0].second==0);
    }
};
struct Stream final : MusicStream5f17 {
    unsigned calls = 0;
    void stream_5f17(CSState &) override {++calls;}
};
struct Tracks final : MidiTrack44b3 {
    std::uint32_t calls = 0;
    std::vector<std::uint16_t> indices;
    void track_44b3(CSState &state) override {
        if(calls < 5 || calls==65536) indices.push_back(state.read16(0x2DC0));
        ++calls;
    }
};
struct Memory final : FarByteMemory {
    std::array<std::uint8_t,65536> bytes{};
    std::uint16_t only_seg=0x1234;
    unsigned writes = 0;
    std::uint8_t read8(std::uint16_t seg,std::uint16_t off) override {
        CHECK(seg==only_seg); return bytes[off];
    }
    void write8(std::uint16_t seg,std::uint16_t off,std::uint8_t value) override {
        CHECK(seg==only_seg); bytes[off]=value; ++writes;
    }
};

static void test_dma() {
    CSState s;Ports p;
    s.write16(0x2DDF,0x1000);
    p.set(0x99,0x0F); // 0F00 < base, no window
    auto r=poll_dma_49bc(s,p,0xAABB);
    CHECK(!r.accepted && r.cx==0 && r.ax==0x1000 && r.dx==0xAABB);
    p.expect_two_reads();
    p.set(0x00,0x11); // 1100-1000=0100 < 0400
    r=poll_dma_49bc(s,p);
    CHECK(!r.accepted && r.cx==0);p.expect_two_reads();
    s.write16(0x48DD,0x0600);
    p.set(0xFF,0x18); // 1800-1000=0800; 0800-0600=0200
    r=poll_dma_49bc(s,p);
    CHECK(r.accepted && r.cx==0x0200 && r.dx==0x0600);
    CHECK(s.read16(0x49BA)==0x0600 && s.read16(0x48DD)==0x0800 && s.read16(0x48DB)==0x0200);
    p.expect_two_reads();
    s.write16(0x48DD,0x0A00);
    p.set(0x01,0x18); // signed CX=0800 < DX=0A00 -> wrap 1000-0A00=0600
    r=poll_dma_49bc(s,p);
    CHECK(r.accepted && r.cx==0x0600);
    CHECK(s.read16(0x49BA)==0x0A00 && s.read16(0x48DD)==0 && s.read16(0x48DB)==0x0600);
    p.expect_two_reads();
    p.set(0x02,0x30); // 3000-1000=2000, signed >1000 => rejected
    r=poll_dma_49bc(s,p);
    CHECK(!r.accepted && r.cx==0);p.expect_two_reads();
    s.write16(0x2DDF,0x0100);s.write16(0x48DD,0x0200);
    p.set(0x33,0xFF); // FF00-0100=FE00, NEGATIVE signed; JLE ACCEPTS!
    r=poll_dma_49bc(s,p);
    CHECK(r.accepted && r.cx==0x0E00);
    CHECK(s.read16(0x48DD)==0 && s.read16(0x49BA)==0x0200);
    p.expect_two_reads();
}

static void test_music_gateway() {
    CSState s;Ports p;Stream h;
    s.write16(0x2DDF,0x1000);s.write16(0x48DD,0);
    s.write8(0x2DEA,0);s.write8(0x48E3,2);
    music_gateway_5df2(s,nullptr,h); CHECK(h.calls==0);
    s.write8(0x2DEA,1);
    bool missing=false;try{music_gateway_5df2(s,nullptr,h);}catch(const std::logic_error &){missing=true;}
    CHECK(missing && h.calls==0);
    p.set(9,0x0F);music_gateway_5df2(s,&p,h);CHECK(h.calls==0);p.expect_two_reads();
    p.set(9,0x18);music_gateway_5df2(s,&p,h);CHECK(h.calls==1);p.expect_two_reads();
    s.write8(0x48E3,0x0c);p.set(9,0x1A);music_gateway_5df2(s,&p,h);CHECK(h.calls==2);p.expect_two_reads();
    s.write8(0x48E3,0x03);p.reads=0;p.outputs.clear();
    music_gateway_5df2(s,nullptr,h);CHECK(h.calls==3 && p.reads==0 && p.outputs.empty());
}

static void test_outer_midi_tick() {
    CSState s; Tracks h;
    s.write8(0x2D62,0);s.write16(0x2C58,2);
    midi_tick_outer_4476(s,h);CHECK(h.calls==0);
    s.write8(0x2D62,1);s.write16(0x2C54,14);s.write16(0x2C5A,15);
    s.write16(0x2C56,0xFFFF);
    midi_tick_outer_4476(s,h);
    CHECK(h.calls==3 && h.indices.size()==3);
    CHECK(h.indices[0]==0 && h.indices[1]==1 && h.indices[2]==2);
    CHECK(s.read16(0x2DC0)==2);
    CHECK(s.read16(0x2C54)==0 && s.read16(0x2C56)==0); // normal threshold and count wrap
    s.write16(0x2C54,0xFFFF);s.write16(0x2C56,3);
    Tracks wrapping; midi_tick_outer_4476(s,wrapping);
    CHECK(s.read16(0x2C54)==0 && s.read16(0x2C56)==3); // tick 16-bit wrap skips unsigned threshold
    s.write16(0x2C54,0);s.write16(0x2C5A,5);s.write16(0x2C58,0);
    Tracks zeros;
    midi_tick_outer_4476(s,zeros);
    CHECK(zeros.calls==65537);
    CHECK(zeros.indices[0]==0 && zeros.indices[1]==1);
    CHECK(zeros.indices.back()==0); // 65536 INC wraps CS:2DC0
    CHECK(s.read16(0x2DC0)==0);
}

static void test_vlq() {
    Memory m;
    m.bytes[10]=0x00;
    auto r=read_vlq_45f9(m,m.only_seg,10,10);
    CHECK(r.delta==0 && r.next_di==11 && r.bytes_read==1);
    m.bytes[100]=0x81;m.bytes[101]=0x00;
    r=read_vlq_45f9(m,m.only_seg,100,10);
    CHECK(r.delta==128 && r.next_di==102 && r.bytes_read==2);
    m.bytes[0xFFFF]=0xFF; m.bytes[0]=0x7F;
    r=read_vlq_45f9(m,m.only_seg,0xFFFF,10);
    CHECK(r.delta==16383 && r.next_di==1 && r.bytes_read==2);
    // Original does not limit length to four bytes; DX:AX shifts mod 2^32.
    for(unsigned i=0;i<9;++i) m.bytes[500+i]=0xFF;
    m.bytes[509]=0x7F;
    r=read_vlq_45f9(m,m.only_seg,500,15);
    CHECK(r.delta==0xFFFFFFFFu && r.next_di==510 && r.bytes_read==10);
    bool exhausted=false;try{(void)read_vlq_45f9(m,m.only_seg,500,5);}catch(const std::runtime_error &){exhausted=true;}
    CHECK(exhausted);
}

static void test_tempo_meta() {
    CSState s;Memory mem;Ports p;
    // FF 51 'length=3' (byte at 100) is SKIPPED, then tempo 07 A1 20 = 500000 us.
    mem.bytes[100]=3;mem.bytes[101]=0x07;mem.bytes[102]=0xA1;mem.bytes[103]=0x20;
    s.write16(0x2C5A,96);
    s.write16(0x201E,0);
    const auto r=tempo_ff51_455d(s,mem,&p,mem.only_seg,100);
    const std::uint32_t tempo=500000u;
    const auto quotient=static_cast<std::uint16_t>(tempo/96u);
    const std::uint16_t pit_div=static_cast<std::uint16_t>((std::uint32_t(quotient)*0x1E73u >>16)*10u);
    CHECK(r.next_di==104 && r.timer_divisor==pit_div && r.pit_programmed);
    CHECK(pit_div!=0 && s.read16(0x2C49)==pit_div);
    CHECK(s.read16(0x2DB6)==static_cast<std::uint16_t>(0xFFFFu/pit_div));
    CHECK(s.read16(0x2DB4)==s.read16(0x2DB6));
    CHECK(p.outputs.size()==3);
    CHECK(p.outputs[0]==std::make_pair(std::uint16_t(0x43),std::uint8_t(0x34)));
    CHECK(p.outputs[1]==std::make_pair(std::uint16_t(0x40),static_cast<std::uint8_t>(pit_div)));
    CHECK(p.outputs[2]==std::make_pair(std::uint16_t(0x40),static_cast<std::uint8_t>(pit_div>>8)));
    p.outputs.clear();s.write16(0x201E,1);s.write16(0x2DB6,0xABCD);
    auto noPit=tempo_ff51_455d(s,mem,nullptr,mem.only_seg,100);
    CHECK(!noPit.pit_programmed && noPit.timer_divisor==pit_div);
    CHECK(s.read16(0x2DB6)==0xABCD && p.outputs.empty());
    // CPU DIV BX/zero: no guessed result, surface guest fault.
    s.write16(0x2C5A,0);bool fault=false;
    try{(void)tempo_ff51_455d(s,mem,nullptr,mem.only_seg,100);}
    catch(const std::overflow_error &){fault=true;}
    CHECK(fault);
    // Positive but too-small ticks: 24-bit dividend / ticks gives 17+ bit quotient.
    s.write16(0x2C5A,1);fault=false;
    try{(void)tempo_ff51_455d(s,mem,nullptr,mem.only_seg,100);}
    catch(const std::overflow_error &){fault=true;}
    CHECK(fault);
    // A genuine zero timer reaches a *second* guest DIV BX inside 466A,
    // unless the 'PIT already installed' word 201E bypasses that helper.
    mem.bytes[101]=0;mem.bytes[102]=0;mem.bytes[103]=0;
    s.write16(0x2C5A,96);s.write16(0x201E,0);
    fault=false;
    try{(void)tempo_ff51_455d(s,mem,&p,mem.only_seg,100);}
    catch(const std::overflow_error &){fault=true;}
    CHECK(fault);
    s.write16(0x201E,1);auto zero=tempo_ff51_455d(s,mem,nullptr,mem.only_seg,100);
    CHECK(!zero.pit_programmed && zero.timer_divisor==0 && s.read16(0x2C49)==0);
}

static void test_stream_fill_prefix() {
    CSState s; Memory m;
    m.bytes.fill(0x42);
    s.write16(0x2DDF,0xFFFC);s.write16(0x2DE1,m.only_seg);s.write16(0x49BA,3);
    s.write8(0x2DEA,0);s.write8(0x48E4,0);s.write16(0x48DB,5);
    stream_fill_prefix_5f17(s,m);
    CHECK(s.read8(0x2DEA)==1 && m.writes==5);
    CHECK(m.bytes[0xFFFF]==0x80 && m.bytes[0]==0x80 && m.bytes[3]==0x80);
    CHECK(m.bytes[4]==0x42);
    m.writes=0;s.write8(0x48E4,1);
    stream_fill_prefix_5f17(s,m);
    CHECK(m.writes==5 && m.bytes[0xFFFF]==0 && m.bytes[0]==0 && m.bytes[3]==0);
    m.writes=0;s.write16(0x48DB,0);s.write8(0x2DEA,0);
    stream_fill_prefix_5f17(s,m);
    CHECK(m.writes==0 && s.read8(0x2DEA)==1);
}

static void test_pcm() {
    CHECK(pcm_mix_byte_5625(0x80,0x80,0)==0x80);
    CHECK(pcm_mix_byte_5625(0x80,0x80,12)==0x80); // sample zero-centered
    // Independent machine-word oracle: high byte of signed 16-bit product.
    for(unsigned sample=0;sample<256;++sample){
      for(unsigned volume=0;volume<256;++volume){
        int signedSample=static_cast<int>(sample/2u)-64;
        std::uint16_t volbits=static_cast<std::uint16_t>(volume*4u);
        int signedVolume=volbits>=32768u ? static_cast<int>(volbits)-65536:static_cast<int>(volbits);
        std::uint16_t lowbits=static_cast<std::uint16_t>(signedSample*signedVolume);
        std::uint8_t addend=static_cast<std::uint8_t>(lowbits/256u);
        for(unsigned dst: {0u,1u,128u,254u,255u})
          CHECK(pcm_mix_byte_5625(static_cast<std::uint8_t>(dst),static_cast<std::uint8_t>(sample),static_cast<std::uint16_t>(volume))
            == static_cast<std::uint8_t>(dst+addend));
      }
    }
    // Specifically force the signed IMUL input through wrapped 16-bit volumes.
    for(unsigned sample=0;sample<256;++sample){
      for(unsigned raw_volume: {0x1FFFu,0x2000u,0x2001u,0x3FFFu,0x4000u,0x7FFFu,0x8000u,0xFFFFu}){
        auto bits=static_cast<std::uint16_t>(raw_volume*4u);
        int signed_vol=bits>=0x8000u ? static_cast<int>(bits)-65536:static_cast<int>(bits);
        int centered=static_cast<int>(sample/2)-64;
        auto product=static_cast<std::uint16_t>(centered*signed_vol);
        auto expected=static_cast<std::uint8_t>(250u+static_cast<std::uint8_t>(product>>8));
        CHECK(pcm_mix_byte_5625(250,static_cast<std::uint8_t>(sample),static_cast<std::uint16_t>(raw_volume)) == expected);
      }
    }
    Memory mem;CSState s;
    mem.bytes.fill(0x42);
    s.write16(0x2DDF,0xFFFC);s.write16(0x2DE1,mem.only_seg);
    s.write16(0x49BA,0x0002);
    pcm_clear_prefix_5568(s,mem,5);
    CHECK(mem.writes==4 && s.read16(0x478B)==5);
    CHECK(mem.bytes[0xFFFE]==0x80 && mem.bytes[0xFFFF]==0x80 && mem.bytes[0]==0x80 && mem.bytes[1]==0x80);
    CHECK(mem.bytes[2]==0x42); // last odd byte untouched
    mem.writes=0;s.write16(0x478B,0xABCD);
    pcm_clear_prefix_5568(s,mem,0);
    CHECK(mem.writes==0 && s.read16(0x478B)==0xABCD); // zero length RET before write
}

int main() {
    test_dma();test_music_gateway();test_outer_midi_tick();test_vlq();test_pcm();test_stream_fill_prefix();test_tempo_meta();
    std::cout<<"PASS: pinned DMA 49BC; MIDI 4476/45F9/5DF2; PCM 555D/5625 contracts\n";
}
