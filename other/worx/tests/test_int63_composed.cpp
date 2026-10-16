#include "worx21/int63_leaf.hpp"

#include <cstdint>
#include <cstdlib>
#include <deque>
#include <iostream>
#include <utility>
#include <vector>
#include <stdexcept>

using namespace worx21;
#define CHECK(x) do { if (!(x)) { std::cerr << "FAIL " << __FILE__ << ":" << __LINE__ << " " << #x << "\n"; std::exit(2); } } while(false)

struct Ports final : PortIO {
    std::deque<std::uint8_t> replies;
    std::vector<std::uint16_t> read_ports;
    std::vector<std::pair<std::uint16_t, std::uint8_t>> writes;
    std::uint8_t default_read = 0;
    std::uint8_t in8(std::uint16_t port) override {
        read_ports.push_back(port);
        const auto ret = replies.empty() ? default_read : replies.front();
        if (!replies.empty()) replies.pop_front();
        return ret;
    }
    void out8(std::uint16_t port, std::uint8_t data) override { writes.emplace_back(port, data); }
};

struct Dos final : DosFileIO {
    std::vector<Registers> calls;
    std::vector<std::uint16_t> handles;
    std::uint16_t resulting_dx = 0;
    Registers close_handle(std::uint16_t handle, const Registers &input) override {
        handles.push_back(handle); calls.push_back(input);
        auto after = input;
        after.ax = 0xFFFF; // This AX is restored by WORX.
        after.dx = resulting_dx; // This DX is NOT restored by WORX.
        return after;
    }
};

int main() {
    CSState state;
    Ports ports;
    Dos dos;
    KnownLeafBackend backend(state, &ports, &dos);
    Registers input;
    input.bx=0xCA5E; input.dx=0xBEE7; input.si=0x1234; input.di=0x5678;
    input.cx=0x8989; input.carry=true;
    const auto call=[&](std::uint8_t ah, std::uint8_t al=0) {
        input.ax=static_cast<std::uint16_t>((std::uint16_t(ah)<<8)|al);
        const auto out=backend.interrupt63(input);
        CHECK(out.bx==input.bx && out.cx==input.cx && out.si==input.si &&
              out.di==input.di && out.carry==input.carry);
        return out;
    };

    // AH12: conditional indexed mutation; 0xB0 is the unsigned boundary.
    state.write8(0x2DC9, 0);
    CHECK(call(0x12,0xFF).ax==0x12FF);
    CHECK(state.read8(0x2DC4)==0xFF && state.read8(0x2DC5)==0x5E);
    CHECK(state.read8(0x2BA7+0xFF)==0x5E);
    state.write8(0x2DC9,0x20);
    state.write8(0x2BA7+0xB0,0x77);
    CHECK(call(0x12,0xB0).dx==input.dx);
    CHECK(state.read8(0x2BA7+0xB0)==0x77); // B0 excluded with mode 20h.
    CHECK(call(0x12,0xAF).ax==0x12AF);
    CHECK(state.read8(0x2BA7+0xAF)==0x5E); // AF included.
    state.write8(0x2DC9,0);
    CHECK(call(0x12,0xB0).dx==input.dx);
    CHECK(state.read8(0x2BA7+0xB0)==0x5E);

    // AH19: no DOS call for FFFF; with valid handle, DOS return DX propagates.
    state.write8(0x2E10,0xAB);
    state.write16(0x2DF3,0xFFFF);
    CHECK(call(0x19,0xCC).ax==0x19CC);
    CHECK(dos.calls.empty() && state.read8(0x2E10)==0);
    state.write16(0x2DF3,0x4444); state.write8(0x2E10,1);
    dos.resulting_dx=0xABCD;
    const auto close=call(0x19,0x97);
    CHECK(close.ax==0x1997 && close.dx==0xABCD);
    CHECK(state.read16(0x2DF3)==0xFFFF && state.read8(0x2E10)==0);
    CHECK(dos.calls.size()==1 && dos.handles[0]==0x4444);
    CHECK(dos.calls[0].ax==0x3E97 && dos.calls[0].bx==0x4444);
    CHECK(state.read16(0x30E4)==0xABCD);

    // Invalid external environment must be surfaced; not masked by a fake OK.
    KnownLeafBackend no_dos(state, &ports);
    state.write16(0x2DF3,0x2222);
    bool threw=false;
    try { Registers req=input;req.ax=0x1900;(void)no_dos.interrupt63(req); }
    catch (const std::logic_error &) {threw=true;}
    CHECK(threw && state.read16(0x2DF3)==0x2222);
    state.write16(0x2DF3,0xFFFF);

    // AH29: one button sample, 40 0x201 writes, 800 analog polls.
    ports.writes.clear();ports.read_ports.clear();ports.replies.clear();
    ports.replies.push_back(0xA5);
    for (int i=0;i<400;++i) ports.replies.push_back(0x03);
    for (int i=0;i<400;++i) ports.replies.push_back(0x01);
    state.write16(0x201A,0);state.write16(0x201C,0);
    auto joystick=call(0x29,0xFE);
    CHECK(joystick.ax==0x29FE && joystick.dx==input.dx);
    CHECK(ports.read_ports.size()==801 && ports.writes.size()==40);
    for (auto p:ports.read_ports) CHECK(p==0x0201);
    for (const auto &w:ports.writes) CHECK(w.first==0x0201 && w.second==0x50);
    CHECK(state.read8(0x2019)==0 && state.read8(0x2018)==1 &&
          state.read8(0x2017)==0 && state.read8(0x2016)==1);
    CHECK(state.read16(0x2012)==800 && state.read16(0x2014)==400);
    CHECK(state.read16(0x201A)==800 && state.read16(0x201C)==400);
    ports.writes.clear();ports.read_ports.clear();ports.replies.clear();
    CHECK(call(0x29,0xFF).dx==input.dx);
    CHECK(state.read16(0x2012)==0 && state.read16(0x2014)==0);
    CHECK(state.read16(0x201A)==800 && state.read16(0x201C)==400); // no recalibration

    // Special calibration edge: when the first measured axis is zero,
    // even a nonzero second-axis calibration does not disable recalibration.
    ports.replies.clear(); ports.writes.clear(); ports.read_ports.clear();
    ports.replies.push_back(0xFF);
    for (int i=0;i<0x320;++i) ports.replies.push_back(0x02);
    state.write16(0x201A,0);state.write16(0x201C,0x5555);
    (void)call(0x29);
    CHECK(state.read16(0x201A)==0 && state.read16(0x201C)==800);
    ports.replies.clear(); ports.writes.clear(); ports.read_ports.clear();
    (void)call(0x29);
    CHECK(state.read16(0x201A)==0 && state.read16(0x201C)==0);

    // AH2E: reprogram PIT only if CS:[201E] != 1. Original helper 466A.
    state.write16(0x201E,0);
    state.write16(0x2DB4,0xEEEE);state.write16(0x2DB6,0xDDDD);
    ports.writes.clear();ports.read_ports.clear();
    auto pit=call(0x2E,0x11);
    CHECK(pit.ax==0xFFFF && pit.dx==input.dx);
    CHECK(state.read16(0x201E)==1);
    CHECK(state.read16(0x2DB4)==1 && state.read16(0x2DB6)==1);
    CHECK(ports.writes.size()==3);
    CHECK(ports.writes[0]==(std::pair<std::uint16_t,std::uint8_t>{0x43,0x34}));
    CHECK(ports.writes[1]==(std::pair<std::uint16_t,std::uint8_t>{0x40,0xFF}));
    CHECK(ports.writes[2]==(std::pair<std::uint16_t,std::uint8_t>{0x40,0xFF}));
    auto nop=call(0x2E,0x11);
    CHECK(nop.ax==0xFFFF && ports.writes.size()==3);

    // Return semantics: outer IRET restores pre-call CF even if callee uses STI.
    CHECK(nop.carry);
    std::cout << "PASS: v0.12 AH12/19/29/2E original byte contract + external DOS/ISA boundary\n";
}
