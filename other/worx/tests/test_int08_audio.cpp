#include "worx21/int08_audio.hpp"
#include "worx21/int08_gate.hpp"
#include <cstdlib>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

using namespace worx21;
#define CHECK(x) do {if(!(x)){std::cerr<<"FAIL "<<__LINE__<<" "<<#x<<"\n";std::exit(2);}}while(false)

struct AudioCalls final: TimerAudioHooks {
    std::vector<std::string> calls;
    void pcm_mix_555d(CSState &) override { calls.push_back("555d"); }
    void midi_schedule_5df2(CSState &) override { calls.push_back("5df2"); }
};
struct IO final: PortIO {
    std::vector<std::pair<std::uint16_t,std::uint8_t>> writes;
    std::uint8_t in8(std::uint16_t) override {std::exit(4);}
    void out8(std::uint16_t port,std::uint8_t val) override {writes.emplace_back(port,val);}
};
struct Chain final: Timer08Hooks {
    Timer08AudioService &audio;
    int music_count=0, bios_count=0, audio_count=0;
    explicit Chain(Timer08AudioService &a):audio(a){}
    void music_tick_4476(CSState &) override { ++music_count; }
    void chain_old_irq08(CSState &) override { ++bios_count; }
    void audio_engine_40e7(CSState &) override { ++audio_count;audio.run(); }
};

int main() {
    CSState state;
    AudioCalls calls;
    Timer08AudioService service(state,calls);
    state.write16(0x2C49,0x0100);
    state.write16(0x2C4B,0x0100);
    state.write16(0x2C4D,0);
    state.write8(0x2C53,0);
    state.write8(0x2DBC,0x20);
    state.write8(0x3ED6,1);
    service.run();
    CHECK((calls.calls==std::vector<std::string>{"555d","5df2"}));
    CHECK(state.read16(0x2C4B)==0 && state.read16(0x2C4D)==0 && state.read8(0x2C53)==0);
    calls.calls.clear();
    service.run(); // 0000:0000 - 0100 => FFFF:FF00 (signed negative).
    CHECK(state.read16(0x2C4B)==0xFF00 && state.read16(0x2C4D)==0xFFFF);
    CHECK(state.read8(0x2C53)==1);
    state.write8(0x2DBC,0);
    state.write8(0x3ED6,0);
    calls.calls.clear();
    state.write16(0x2C49,0);
    service.run();
    CHECK(calls.calls.empty() && state.read8(0x2C53)==1); // sticky bit
    // A negative old value that wraps to nonnegative should not set flag.
    state.write8(0x2C53,0);
    state.write16(0x2C4D,0x8000);state.write16(0x2C4B,0x0010);
    state.write16(0x2C49,0x20);
    service.run();
    CHECK(state.read16(0x2C4D)==0x7FFF && state.read16(0x2C4B)==0xFFF0);
    CHECK(state.read8(0x2C53)==0);

    // Real INT08 gate -> 40E7 shell, and first IO PIC EOI is captured.
    IO ports;
    Chain chain(service);
    Timer08Gate gate(state,ports,chain);
    calls.calls.clear();
    state.write8(0x2DBC,0x20);
    state.write8(0x3ED6,1);
    state.write16(0x3ED4,0xFFFF);
    state.write16(0x2DB4,0);
    state.write16(0x2DB6,27);
    state.write16(0x2C49,0x0100);
    gate.irq08();
    CHECK(chain.audio_count==1 && chain.music_count==0 && chain.bios_count==0);
    CHECK(ports.writes.size()==1 && ports.writes[0].first==0x20);
    CHECK((calls.calls==std::vector<std::string>{"555d","5df2"}));
    CHECK(state.read16(0x3ED4)==0xFFFF);
    std::cout<<"PASS: original 40E7 timer subtraction, signed high-word latch, PCM/MIDI gates\n";
}
