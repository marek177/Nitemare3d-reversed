#include "worx21/int08_gate.hpp"
#include <cstdlib>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

using namespace worx21;
#define CHECK(x) do {if(!(x)){std::cerr << "FAIL " << __LINE__ << " " << #x << "\n";std::exit(2);}}while(false)

struct Ports final: PortIO {
    std::vector<std::pair<std::uint16_t,std::uint8_t>> writes;
    std::uint8_t in8(std::uint16_t) override { std::exit(3); }
    void out8(std::uint16_t port, std::uint8_t val) override { writes.emplace_back(port,val); }
};
struct Hooks final: Timer08Hooks {
    std::vector<std::string> events;
    void music_tick_4476(CSState &) override { events.emplace_back("music_4476"); }
    void chain_old_irq08(CSState &) override { events.emplace_back("old_08"); }
    void audio_engine_40e7(CSState &) override { events.emplace_back("audio_40e7"); }
};
int main() {
    CSState state;
    Ports ports;
    Hooks hooks;
    Timer08Gate timer(state,ports,hooks);
    // Original image CS:3ED4=FFFF; init AX=0952 -> 65535/0952 = 27.
    state.write16(0x3ED4,0xFFFF);
    state.write16(0x2DB6,27);
    state.write16(0x2DB4,27); // INT08 immediately chains once after init.
    timer.irq08();
    CHECK(hooks.events==std::vector<std::string>{"old_08"});
    CHECK(ports.writes.empty() && state.read16(0x2DB4)==0);
    hooks.events.clear();
    timer.irq08();
    CHECK(hooks.events==std::vector<std::string>{"audio_40e7"});
    CHECK(ports.writes.size()==1 && ports.writes[0].first==0x20 && ports.writes[0].second==0x20);
    CHECK(state.read16(0x2DB4)==1 && state.read16(0x3ED4)==0xFFFF);
    CHECK(state.read16(0x40E5)==0);
    // The guest's original code tests 2DBC & 16h, not only bit 0x10.
    hooks.events.clear();ports.writes.clear();
    state.write8(0x2DBC,0x02);
    state.write16(0x3ED4,0); // already reentrant: cannot call 40E7 again.
    timer.irq08();
    CHECK((hooks.events==std::vector<std::string>{"music_4476"}));
    CHECK(state.read16(0x40E5)==1 && state.read16(0x3ED4)==0);
    CHECK(ports.writes.size()==1);
    // 2DB4 wrap is genuinely uint16: FFFF+1=0. If period>0 it does NOT
    // call BIOS despite the pre-INC counter looking large.
    hooks.events.clear();ports.writes.clear();
    state.write16(0x2DB4,0xFFFF);state.write16(0x2DB6,27);
    state.write16(0x3ED4,0xFFFF);
    timer.irq08();
    CHECK((hooks.events==std::vector<std::string>{"music_4476","audio_40e7"}));
    CHECK(state.read16(0x2DB4)==0 && ports.writes.size()==1);
    // Threshold of 0 will always chain, including counter wrap.
    hooks.events.clear();ports.writes.clear();
    state.write16(0x2DB6,0);state.write16(0x2DB4,0xFFFF);
    timer.irq08();
    CHECK((hooks.events==std::vector<std::string>{"music_4476","old_08"}));
    CHECK(state.read16(0x2DB4)==0 && ports.writes.empty());
    // No assertion of the unimplemented callbacks' own effects.
    std::cout<<"PASS: original INT08 gate, PIC EOI, BIOS chaining, reentrancy sentinel\n";
}
