#include "worx21/midi_routing.hpp"

#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace worx21;
#define CHECK(cond) do { if (!(cond)) { std::cerr << "FAIL: " << __LINE__ << ": " << #cond << '\n'; std::exit(2); } } while(0)

struct PortTrace final : PortIO {
    std::vector<std::string> events;
    std::vector<std::uint8_t> scripted;
    std::size_t at=0;
    std::uint8_t fallback=0;
    std::uint8_t in8(std::uint16_t p) override {
        CHECK(p==0x331u);
        events.push_back("in331");
        return at<scripted.size()?scripted[at++]:fallback;
    }
    void out8(std::uint16_t p,std::uint8_t val) override {
        CHECK(p==0x330u);
        events.push_back(std::string("out330:")+std::to_string(val));
    }
    unsigned count_reads() const {
        unsigned r=0;for(const auto &e:events)if(e=="in331")++r;return r;
    }
};
struct Callback final : MidiFarCallback3896 {
    unsigned calls=0;
    std::vector<std::uint8_t> ax_input;
    bool mute_remaining=false;
    bool add_more=false;
    bool alter_state=false;
    void invoke_3896(std::uint16_t segment,std::uint16_t offset,
                     CSState &s,MidiDispatchRegisters &r) override {
        CHECK(segment==0x1234u && offset==0x5678u);
        ++calls;
        ax_input.push_back(static_cast<std::uint8_t>(r.ax));
        if(mute_remaining)r.cx=0;
        if(add_more)r.cx=2;
        if(alter_state){s.write8(0x2DC5u,0x71u);r.dx=0xCAFEu;}
    }
};
struct Synth final : MidiOtherRoutes3a67 {
    std::vector<std::string> calls;
    MidiDispatchRegisters last{};
    void call_3941(CSState &,MidiDispatchRegisters &r) override { calls.emplace_back("3941");last=r; }
    void call_3e34(CSState &,MidiDispatchRegisters &r) override { calls.emplace_back("3e34");last=r; }
    void call_3b5b(CSState &s,MidiDispatchRegisters &r) override {
        calls.emplace_back("3b5b");last=r;
        (void)s; // the no-transpose route keeps AL=channel, not pitch
    }
};

static MidiDispatchRegisters context(std::uint8_t status,std::uint16_t cx=1) {
    MidiDispatchRegisters r{};
    r.ax=static_cast<std::uint16_t>((std::uint16_t(status&0xF0u)<<8u) | (status&0x0Fu));
    r.bx=0x3333u;r.cx=cx;r.si=0xC0DEu;r.ds=0xABCDu;r.dx=0x1111u;
    r.es=0xABBAu;r.di=0x5050u;
    return r;
}
static void state_status(CSState &s,std::uint8_t status,
                         std::uint8_t data1=0x40u,std::uint8_t data2=0x7Fu) {
    constexpr std::uint8_t counts[16]={0,0,0,0,0,0,0,0,2,2,2,2,1,1,2,0};
    for(unsigned i=0;i<16;i++)s.write8(static_cast<std::uint16_t>(0x2DA4u+i),counts[i]);
    s.write8(0x2DC8u,status&0xF0u);
    s.write8(0x2DC4u,status&0x0Fu);
    s.write8(0x2DC5u,data1);
    s.write8(0x2DC6u,data2);
}

static void test_three_direct_writes_and_saved_registers(){
    CSState s;state_status(s,0x93u,0x32u,0x6fu);
    PortTrace p;p.scripted={0x40u,0,0x40u,0,0};
    MidiRouting3a67 handler(0xBEEFu,&p,nullptr,nullptr);
    auto r=context(0x93u,0xDEADu);
    handler.dispatch_tail_3a67(s,r);
    const auto &result=handler.last_result();
    CHECK(result.kind==MidiRoutingKind::direct_mpu && result.send_calls.size()==3);
    CHECK(result.send_calls[0].status_reads==2 && result.send_calls[1].status_reads==2);
    CHECK(result.send_calls[2].status_reads==1);
    CHECK((p.events==std::vector<std::string>{"in331","in331","out330:147","in331","in331","out330:50","in331","out330:111"}));
    CHECK(r.ds==0xBEEFu && r.ax==0x9003u && r.cx==0xDEADu && r.si==0xC0DEu);
    CHECK(r.bx==0x3333u && r.dx==0x1111u && r.es==0xABBAu && r.di==0x5050u);
    CHECK(!result.explicit_clc);
}
static void test_no_parameters_no_port_and_direct_ds_effect(){
    CSState s;state_status(s,0xF2u);
    MidiRouting3a67 handler(0xAFAFu,nullptr,nullptr,nullptr);
    auto r=context(0xF2u);handler.dispatch_tail_3a67(s,r);
    CHECK(handler.last_result().kind==MidiRoutingKind::direct_mpu);
    CHECK(handler.last_result().send_calls.empty() && r.ds==0xAFAFu);
    CHECK(r.cx==1 && r.ax==0xF002u);
}
static void test_timeout_65535_no_far_callback(){
    CSState s;s.write16(0x3898u,0x1234u);s.write16(0x3896u,0x5678u);
    PortTrace p;p.fallback=0x40u;
    Callback cb;auto r=context(0x90u);
    const auto out=mpu_send_58f8(s,p,r,&cb);
    CHECK(!out.transmitted && !out.far_callback_invoked);
    CHECK(out.status_reads==65535u && p.count_reads()==65535u && cb.calls==0);
    CHECK(r.ax==0x9000u);
}
static void test_far_callback_controls_jcxz_and_live_globals(){
    CSState s;state_status(s,0x92u,0x55u,0x60u);
    s.write16(0x3896u,0x5678u);s.write16(0x3898u,0x1234u);
    PortTrace p;Callback cb;cb.mute_remaining=true;cb.alter_state=true;
    MidiRouting3a67 handler(0xBEEFu,&p,&cb,nullptr);
    auto r=context(0x92u,0x1234u);
    handler.dispatch_tail_3a67(s,r);
    CHECK(cb.calls==1 && cb.ax_input==std::vector<std::uint8_t>{0x92u});
    CHECK(handler.last_result().send_calls.size()==1);
    CHECK(s.read8(0x2DC5u)==0x71u && r.dx==0xCAFEu);
    CHECK(r.ax==0x9002u && r.cx==0x1234u); // saved frame restored
}
static void test_callback_changes_count_and_followup_bytes(){
    CSState s;state_status(s,0xC1u,0x42u,0x59u); // nibble count == 1
    s.write16(0x3896u,0x5678u);s.write16(0x3898u,0x1234u);
    PortTrace p;Callback cb;cb.add_more=true;
    MidiRouting3a67 handler(0xBEEFu,&p,&cb,nullptr);auto r=context(0xC1u);
    handler.dispatch_tail_3a67(s,r);
    // After callback, CX=2; 3A95 DEC->1, data1; 3A9F DEC->0, data2.
    CHECK(handler.last_result().send_calls.size()==3 && cb.calls==3);
    CHECK((p.events==std::vector<std::string>{"in331","out330:193","in331","out330:66","in331","out330:89"}));
}
static void test_missing_far_callback_fails_after_write(){
    CSState s;s.write16(0x3898u,0x1234u);s.write16(0x3896u,0x5678u);
    PortTrace p;auto r=context(0x90u);
    bool threw=false;
    try {(void)mpu_send_58f8(s,p,r,nullptr);}catch(const std::logic_error&){threw=true;}
    CHECK(threw);
    CHECK((p.events==std::vector<std::string>{"in331","out330:0"}));
}
static void test_alternate_routes_and_ignored_status(){
    CSState s;Synth callbacks;MidiRouting3a67 handler(0xAAAAu,nullptr,nullptr,&callbacks);
    s.write8(0x2DBCu,0x02u);
    for(const auto [status,name] : std::vector<std::pair<std::uint8_t,std::string>>{
        {0xA4u,"3941"},{0xB0u,"3941"},{0xC3u,"3e34"}}){
        state_status(s,status);auto r=context(status);
        handler.dispatch_tail_3a67(s,r);
        CHECK(callbacks.calls.back()==name && handler.last_result().explicit_clc);
        CHECK(r.ds==0xABCDu && r.ax==context(status).ax);
    }
    state_status(s,0xD0u);auto r=context(0xD0u);
    handler.dispatch_tail_3a67(s,r);
    CHECK(handler.last_result().kind==MidiRoutingKind::ignored_status);
    CHECK(handler.last_result().explicit_clc && callbacks.calls.size()==3);
}
static void test_transpose_conditions_and_byte_wrap(){
    CSState s;Synth cb;MidiRouting3a67 handler(0xAAAAu,nullptr,nullptr,&cb);
    s.write8(0x2DBCu,0x04u);s.write8(0x2DA3u,0x30u);
    state_status(s,0x90u,0xF1u);auto r=context(0x90u);
    handler.dispatch_tail_3a67(s,r);
    CHECK(handler.last_result().transposed_pitch && s.read8(0x2DC5u)==0x21u);
    CHECK(cb.last.ax==0x9021u && handler.last_result().explicit_clc);
    s.write8(0x2DC9u,0x20u);s.write8(0x2B4Du,1);
    state_status(s,0x99u,0x40u);r=context(0x99u);
    handler.dispatch_tail_3a67(s,r);
    CHECK(!handler.last_result().transposed_pitch && s.read8(0x2DC5u)==0x40u);
    s.write8(0x2B4Du,0);
    state_status(s,0x8Bu,0x50u);r=context(0x8Bu);
    handler.dispatch_tail_3a67(s,r);
    CHECK(!handler.last_result().transposed_pitch && s.read8(0x2DC5u)==0x50u);
    state_status(s,0x8Au,0x60u);r=context(0x8Au);
    handler.dispatch_tail_3a67(s,r);
    CHECK(handler.last_result().transposed_pitch && s.read8(0x2DC5u)==0x90u);
}
struct MidiStreamMemory final : FarByteMemory {
    std::array<std::uint8_t,65536> b{};
    std::uint8_t read8(std::uint16_t es,std::uint16_t di) override {CHECK(es==0xABCDu);return b[di];}
    void write8(std::uint16_t es,std::uint16_t di,std::uint8_t v) override {CHECK(es==0xABCDu);b[di]=v;}
};
static void test_integration_44ee_to_real_3a67_mpu_58f8(){
    CSState s;state_status(s,0x90u);s.write8(0x2DBCu,0);
    s.write16(0x2DC0u,2u);
    MidiStreamMemory mem;mem.b[100]=0x92u;mem.b[101]=0x40u;
    mem.b[102]=0x55u;mem.b[103]=0x07u;
    PortTrace p;MidiRouting3a67 route(0xBEEFu,&p,nullptr,nullptr);
    const auto r=midi_event_step_44ee(s,mem,0xABCDu,100u,0u,&route,nullptr,nullptr,12u);
    CHECK(r.next_di==104u && r.next_delta==7u && r.index_committed==2u);
    CHECK(route.last_result().kind==MidiRoutingKind::direct_mpu);
    CHECK((p.events==std::vector<std::string>{"in331","out330:146","in331","out330:64","in331","out330:85"}));
    CHECK(s.read16(0x2D22u+4u)==104u && s.read8(0x2DC8u)==0x90u);
}
static void test_synth_backend_mandatory_only_on_reached_path(){
    CSState s;state_status(s,0x90u);s.write8(0x2DBCu,2);
    auto r=context(0x90u);
    MidiRouting3a67 no_backend(0xABCDu,nullptr,nullptr,nullptr);
    bool threw=false;
    try {no_backend.dispatch_tail_3a67(s,r);} catch(const std::logic_error&){threw=true;}
    CHECK(threw && s.read8(0x2DC5u)==0x40u);
    s.write8(0x2DBCu,0);s.write8(0x2DC8u,0xF0u);
    state_status(s,0xF0u);r=context(0xF0u);
    no_backend.dispatch_tail_3a67(s,r); // no port is accessed for zero-count nibble
    CHECK(no_backend.last_result().send_calls.empty());
}
int main(){
    test_three_direct_writes_and_saved_registers();
    test_no_parameters_no_port_and_direct_ds_effect();
    test_timeout_65535_no_far_callback();
    test_far_callback_controls_jcxz_and_live_globals();
    test_callback_changes_count_and_followup_bytes();
    test_missing_far_callback_fails_after_write();
    test_alternate_routes_and_ignored_status();
    test_transpose_conditions_and_byte_wrap();
    test_integration_44ee_to_real_3a67_mpu_58f8();
    test_synth_backend_mandatory_only_on_reached_path();
    std::cout << "PASS: v016 3A67 route and 58F8 bounded port + reentrant far callback\n";
}
