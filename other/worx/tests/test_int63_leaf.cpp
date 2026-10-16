#include "worx21/int63_leaf.hpp"
#include <cstdint>
#include <cstdlib>
#include <deque>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <vector>

using namespace worx21;
#define CHECK(x) do { if (!(x)) { std::cerr << "FAIL " << __FILE__ << ":" << __LINE__ << " " << #x << "\n"; std::exit(2); } } while(false)

struct ScriptedPorts : PortIO {
    std::deque<std::uint8_t> replies;
    std::vector<std::uint16_t> inputs;
    std::vector<std::pair<std::uint16_t, std::uint8_t>> outputs;
    std::uint8_t default_reply = 0;
    std::uint8_t in8(std::uint16_t port) override {
        inputs.push_back(port);
        if (replies.empty()) return default_reply;
        auto val = replies.front();
        replies.pop_front();
        return val;
    }
    void out8(std::uint16_t port, std::uint8_t data) override {
        outputs.emplace_back(port, data);
    }
};

int main() {
    CSState state;
    ScriptedPorts ports;
    KnownLeafBackend known(state, &ports);
    Registers pre{};
    pre.bx = 0x1234;
    pre.cx = 0xCAFE;
    pre.dx = 0x9BDF;
    pre.di = 0x4444;
    pre.si = 0x7777;
    pre.carry = true;
    const auto run = [&](std::uint8_t cmd, std::uint8_t al = 0) {
        auto input = pre;
        input.ax = std::uint16_t((std::uint16_t(cmd) << 8) | al);
        return known.interrupt63(input);
    };
    auto unchanged = [&](std::uint8_t cmd, std::uint8_t al) {
        const auto out=run(cmd, al);
        CHECK(out.ax == std::uint16_t((std::uint16_t(cmd)<<8)|al));
        CHECK(out.dx == pre.dx && out.bx == pre.bx && out.cx == pre.cx);
        CHECK(out.si == pre.si && out.di == pre.di && out.carry == pre.carry);
    };

    // AH=02 stores exact DSP base and a second zero-extended AL parameter.
    auto cfg=run(0x02, 0xAF);
    CHECK(cfg.ax == 0x00AF && cfg.dx == pre.dx);
    CHECK(state.read16(0x2DF0) == pre.bx && state.read16(0x2010) == 0x00AF);

    state.write16(0x2C47, 0xBEEF);
    CHECK(run(0x03).ax == 0xBEEF);
    CHECK(state.read16(0x2C47) == 0);
    CHECK(run(0x03).ax == 0);

    // AH09 / AH0A: 32-bit unsigned timer-counter multiplication & reset.
    auto tick=run(0x09, 0x14);
    const std::uint32_t ticks = 0x1234u * 0x04A9u;
    CHECK(tick.ax == 0x04A9 && tick.dx == (ticks >> 16));
    CHECK(state.read16(0x2C4B) == static_cast<std::uint16_t>(ticks));
    CHECK(state.read16(0x2C4D) == ticks >> 16);
    CHECK(state.read16(0x2C4F) == static_cast<std::uint16_t>(ticks));
    CHECK(state.read16(0x2C51) == ticks >> 16);
    state.write16(0x2C4B, 0); state.write16(0x2C4D, 0);
    state.write8(0x2C53, 99);
    unchanged(0x0A, 0x03);
    CHECK(state.read16(0x2C4B) == static_cast<std::uint16_t>(ticks));
    CHECK(state.read16(0x2C4D) == ticks >> 16 && state.read8(0x2C53) == 0);

    state.write8(0x2DEA, 0xBE);
    CHECK(run(0x08).ax == 0);
    state.write8(0x2DEA, 0xBF);
    CHECK(run(0x08).ax == 1);
    state.write8(0x2C53, 0xFF);
    CHECK(run(0x0B).ax == 0xFF);
    state.write8(0x2D62, 0xF0);
    CHECK(run(0x0E).ax == 0);
    state.write8(0x2D62, 0xF1);
    CHECK(run(0x0E).ax == 1);

    unchanged(0x13, 0xAB); CHECK(state.read8(0x2DBC) == 0xAB);
    unchanged(0x16, 0xC9); CHECK(state.read8(0x2DBD) == 0xC9);
    state.write8(0x2DCA, 0xDE); CHECK(run(0x1C).ax == 0);
    state.write8(0x2DCA, 0xDF); CHECK(run(0x1C).ax == 1);
    unchanged(0x1D, 0x43); CHECK(state.read8(0x2C61) == 0x34);
    unchanged(0x1F, 0x21); CHECK(state.read8(0x2D62) == 1);
    unchanged(0x26, 0x22); CHECK(state.read8(0x2C0C) == 1);

    // AH20/21/22 require enabled DSP route, otherwise -1 and no port access.
    state.write8(0x2DF2, 0);
    const auto ports_before=ports.outputs.size();
    for(auto cmd: {0x20, 0x21, 0x22}) {
        auto disabled=run(static_cast<std::uint8_t>(cmd));
        CHECK(disabled.ax == 0xFFFF && disabled.dx == pre.dx);
    }
    CHECK(ports.outputs.size() == ports_before);
    state.write8(0x2DF2, 1);
    state.write16(0x2DF0, 0x220);
    for(auto kv: {std::pair<int,int>{0x20,0x22},{0x21,0x04},{0x22,0x26}}) {
        const auto out=run(static_cast<std::uint8_t>(kv.first));
        CHECK(out.ax == 0 && out.dx == 0x225 && out.bx == pre.bx);
        CHECK(ports.outputs[ports.outputs.size()-2] == (std::pair<std::uint16_t,std::uint8_t>{0x224, static_cast<std::uint8_t>(kv.second)}));
        CHECK(ports.outputs.back() == (std::pair<std::uint16_t,std::uint8_t>{0x225, 0x34}));
    }
    ports.outputs.clear();

    state.write16(0x3ED4, 4);
    auto magic = run(0x24);
    CHECK(magic.ax == 0x1234 && magic.dx == 0x5678 && magic.carry);
    CHECK(state.read16(0x3ED4) == 4);
    CHECK(state.read16(0x30E2) == 0x1234 && state.read16(0x30E4) == 0x5678);
    state.write16(0x2012, 0x0102);
    state.write16(0x201A, 0x0009);
    auto axis0 = run(0x2A);
    CHECK(axis0.ax == (static_cast<std::uint16_t>(0x0102 * 0x40) / 9));
    CHECK(axis0.dx == (static_cast<std::uint16_t>(0x0102 * 0x40) % 9));
    state.write16(0x201A, 0);
    auto axis0_zero = run(0x2A);
    CHECK(axis0_zero.ax == static_cast<std::uint16_t>(0x0102 * 0x40) && axis0_zero.dx == 0);
    CHECK(axis0_zero.carry == pre.carry);
    state.write16(0x2014, 0xFFFF);
    state.write16(0x201C, 0x0001);
    CHECK(run(0x2B).ax == 0xFFC0 && run(0x2B).dx == 0);
    state.write8(0x2016 + 0xEA, 0xB5);
    CHECK(run(0x2C, 0xEA).ax == 0xB5);
    CHECK(run(0x2C, 0xEA).carry == pre.carry);
    state.write16(0x2C56, 0xCA18); CHECK(run(0x2D).ax == 0xCA18);
    state.write16(0x2C49, 0x11FF); CHECK(run(0x30).ax == 0x11FF);
    CHECK(run(0x30).carry); // CLC in callee does NOT override IRET FLAGS.
    state.write16(0x2DF0, 0x220);
    CHECK(run(0x37).ax == 0x220);
    CHECK(run(0x31, 0xFF).ax == 0x3F);
    CHECK(state.read16(static_cast<std::uint16_t>(0x4BBF + 2*pre.bx)) == 0x3F);
    CHECK(run(0x32).ax == 0xFFFF);
    state.write16(0x4BEF + 2*0xC8, 0xBA98);
    CHECK(run(0x36, 0xC8).ax == 0xBA98);
    unchanged(0x3E, 0x02); CHECK(state.read8(0x3ED6) == 0x34);
    unchanged(0x43, 0x00); CHECK(state.read16(0x34B9) == pre.bx);
    unchanged(0x44, 0xA9);
    CHECK(state.read16(static_cast<std::uint16_t>(0x4BAF + 2*pre.bx)) == 2);
    state.write16(static_cast<std::uint16_t>(0x4BEF + 2*pre.bx), 0xAAAA);
    unchanged(0x47, 0x00);
    CHECK(state.read16(static_cast<std::uint16_t>(0x4BEF + 2*pre.bx)) == 0);
    unchanged(0x46, 0x00);
    CHECK(state.read16(0x3896) == pre.bx && state.read16(0x3898) == pre.dx);

    for(auto kv: {std::pair<int,int>{0x4A,0x0A},{0x4B,0x0C},{0x4C,0x2E}}) {
        auto out = run(static_cast<std::uint8_t>(kv.first), 0x5E);
        const std::uint8_t expected = kv.first == 0x4C ? 0x74 : 0x34;
        CHECK(out.ax == ((kv.first << 8) | expected) && out.dx == 0x225);
        CHECK(ports.outputs[ports.outputs.size()-2] == (std::pair<std::uint16_t,std::uint8_t>{0x224,static_cast<std::uint8_t>(kv.second)}));
        CHECK(ports.outputs.back() == (std::pair<std::uint16_t,std::uint8_t>{0x225,expected}));
    }
    ports.outputs.clear();
    ports.replies = {0x80, 0x80, 0x00};
    unchanged(0x4F, 0xDA);
    CHECK(ports.inputs.size() == 3);
    for(auto port: ports.inputs) CHECK(port == 0x22C);
    CHECK(ports.outputs.size() == 1 && ports.outputs[0].first == 0x22C && ports.outputs[0].second == 0xDA);

    ports.replies = {0x00, 0x00, 0x80, 0xA7};
    ports.inputs.clear();
    const auto read = run(0x50, 0xC1);
    CHECK(read.ax == 0x00A7 && read.dx == 0x022A); // DX modified by callee
    CHECK(state.read16(0x30E2) == 0x00A7 && state.read16(0x30E4) == 0x022A);
    CHECK(read.bx == pre.bx && read.carry == pre.carry);
    CHECK(ports.inputs.size() == 4);
    CHECK(ports.inputs[0] == 0x22E && ports.inputs[1] == 0x22E &&
          ports.inputs[2] == 0x22E && ports.inputs[3] == 0x22A);

    // Timeout branches: polling exhausted, but original still does its OUT/IN.
    ports.replies.clear(); ports.default_reply = 0x80;
    ports.inputs.clear(); ports.outputs.clear();
    unchanged(0x4F, 0xEE);
    CHECK(ports.inputs.size() == 65535 && ports.outputs.size() == 1);
    ports.replies.clear(); ports.default_reply = 0x00;
    ports.inputs.clear(); ports.outputs.clear();
    CHECK(run(0x50).ax == 0 && run(0x24).dx == 0x5678);
    CHECK(ports.inputs.size() == 65536); // 65535 status reads and one data read

    unchanged(0x51, 0x7C);
    CHECK(state.read16(0x3DB1) == 1 && state.read8(0x2B96) == 0x7C);
    CHECK(state.read8(0x2B95) == 0xFF && state.read8(0x2BC7) == 0);

    for (auto missing: {0x00, 0x01, 0x27, 0x28, 0x2F, 0x33, 0x52, 0xFF}) {
        bool failed=false;
        try { (void)run(static_cast<std::uint8_t>(missing)); }
        catch (const std::logic_error &) { failed=true; }
        CHECK(failed);
    }

    // Memory word access wraps at 16-bit segment boundary.
    state.write16(0xFFFF, 0xA5C3);
    CHECK(state.read8(0xFFFF) == 0xC3 && state.read8(0) == 0xA5);
    std::cout << "PASS: 37 byte-audited AH leaf contracts; 65535-iteration DSP exhaustion\n";
}
