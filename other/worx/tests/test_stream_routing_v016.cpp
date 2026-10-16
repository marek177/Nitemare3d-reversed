#include "worx21/stream_routing.hpp"

#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace worx21;
#define CHECK(x) do { if(!(x)) { std::cerr<<"FAIL "<<__LINE__<<": "<<#x<<'\n'; std::exit(2);} } while(0)

struct Calls : StreamExternalCalls {
    std::vector<std::string> &log;
    explicit Calls(std::vector<std::string> &l):log(l){}
    void dsp_command_5a3f(std::uint8_t al,CSState &state) override {
        CHECK(al==0xD0u && state.read8(0x4740u)==0u);
        log.emplace_back("dsp:D0");
    }
    void close_4741(CSState &) override {log.emplace_back("close:4741");}
    void continue_mode(std::uint16_t ip,CSState &) override {
        log.emplace_back("continue:"+std::to_string(ip));
    }
};
struct Ports : PortIO {
    std::vector<std::string> &log;
    explicit Ports(std::vector<std::string> &l):log(l){}
    std::uint8_t in8(std::uint16_t) override {CHECK(false);return 0;}
    void out8(std::uint16_t port,std::uint8_t value) override {
        CHECK(port==0x0Au && value==0x05u);log.emplace_back("out0A:05");
    }
};
struct Reader : Read312e {
    std::vector<std::string> &log;
    std::uint8_t new_mode=0x0Cu;
    std::uint32_t new_remaining=0x30u;
    std::uint16_t first_return=1u;
    std::uint16_t second_return=3u;
    std::uint16_t data_return=4u;
    unsigned calls=0;
    explicit Reader(std::vector<std::string> &l):log(l){}
    std::uint16_t call_312e(std::uint16_t bx,std::uint16_t es,
                            std::uint16_t di,CSState &state) override {
        CHECK(es==0xBEEFu);
        log.emplace_back("read:"+std::to_string(bx)+":"+std::to_string(di));
        ++calls;
        if(di==0x48E3u){CHECK(bx==1u);state.write8(di,new_mode);return first_return;}
        if(di==0x48DFu){CHECK(bx==3u);state.write16(0x48DFu,static_cast<std::uint16_t>(new_remaining));
                            state.write8(0x48E1u,static_cast<std::uint8_t>(new_remaining>>16u));return second_return;}
        if(di==0x5E69u){return data_return;}
        CHECK(false);return 0;
    }
};
static void set_mode(CSState &s,std::uint8_t mode){s.write8(0x48E3u,mode);}
static void test_no_header_and_mode0c(){
    CSState s;set_mode(s,0x0C);s.write16(0x48DF,0x0001);s.write16(0x48E1,1u);
    s.write16(0x48DB,2u);
    auto result=stream_route_5f3e(s,0xBEEF,nullptr,nullptr,nullptr);
    CHECK(!result.fetched_header && result.route==StreamRouteKind::mode_0c);
    CHECK(s.read16(0x48DF)==0xFFFF && s.read16(0x48E1)==0);
    CHECK(!result.explicit_stc && !result.error_close_called);
}
static void test_header_dsp_order_and_clamp(){
    CSState s;set_mode(s,0);s.write8(0x4740u,0x81u);s.write16(0x48DBu,0x40u);
    std::vector<std::string> log;Reader rd(log);Ports io(log);Calls cb(log);
    rd.new_mode=0x0C;rd.new_remaining=0x30;
    const auto result=stream_route_5f3e(s,0xBEEF,&rd,&io,&cb);
    CHECK(result.fetched_header && result.stopped_previous_dsp);
    CHECK(result.first_read_ax==1 && result.second_read_ax==3);
    CHECK(result.route==StreamRouteKind::mode_0c && result.mode==0x0C);
    CHECK(s.read16(0x48DF)==0 && s.read16(0x48E1)==0);
    CHECK(s.read8(0x4740)==0); // clears whole BYTE not bit0 only
    CHECK((log==std::vector<std::string>{"dsp:D0","out0A:05","read:1:18659","read:3:18655"}));
}
static void test_failed_first_header_read_closes_and_sets_carry(){
    CSState s;set_mode(s,0x09);
    std::vector<std::string> log;Reader rd(log);Calls cb(log);
    rd.first_return=0;
    auto r=stream_route_5f3e(s,0xBEEF,&rd,nullptr,&cb);
    CHECK(r.fetched_header && r.first_read_incomplete && r.explicit_stc);
    CHECK(r.error_close_called && rd.calls==1 && !r.stopped_previous_dsp);
    CHECK((log==std::vector<std::string>{"read:1:18659","close:4741"}));
}
static void test_second_header_read_ax_not_checked(){
    CSState s;
    std::vector<std::string> log;Reader rd(log);Calls cb(log);
    rd.new_mode=0x0C;rd.new_remaining=0x00001234u;rd.second_return=0;
    s.write16(0x48DBu,1u);
    auto r=stream_route_5f3e(s,0xBEEF,&rd,nullptr,&cb);
    CHECK(r.second_read_ax==0u && !r.first_read_incomplete && !r.error_close_called);
    CHECK(r.route==StreamRouteKind::mode_0c && s.read16(0x48DFu)==0x1233u);
    CHECK(rd.calls==2);
}
static void test_invalid_mode_closes_and_unexpected_callbacks_fail(){
    CSState s;set_mode(s,0xFF);s.write16(0x48EEu,1u); // prevents header
    std::vector<std::string> log;Calls cb(log);
    auto r=stream_route_5f3e(s,0xBEEF,nullptr,nullptr,&cb);
    CHECK(!r.fetched_header && r.route==StreamRouteKind::invalid_mode);
    CHECK(r.error_close_called && r.explicit_stc && log.size()==1 && log[0]=="close:4741");
    bool failed=false;
    try{(void)stream_route_5f3e(s,0xBEEF,nullptr,nullptr,nullptr);}
    catch(const std::logic_error&){failed=true;}
    CHECK(failed);
}
static void test_other_modes_use_explicit_continuations(){
    for(const auto mode : {0x03u,0x09u,0x02u,0x01u}) {
        CSState s;set_mode(s,static_cast<std::uint8_t>(mode));
        s.write16(0x48DFu,1u); // bypass external header read
        std::vector<std::string> log;Calls cb(log);
        auto r=stream_route_5f3e(s,0xBEEF,nullptr,nullptr,&cb);
        CHECK(r.mode==mode && r.continuation_ip!=0 && log.size()==1);
        CHECK(log[0]=="continue:"+std::to_string(r.continuation_ip));
        CHECK(!r.explicit_stc);
        bool failed=false;
        try{(void)stream_route_5f3e(s,0xBEEF,nullptr,nullptr,nullptr);}
        catch(const std::logic_error&){failed=true;}
        CHECK(failed);
    }
}
static void test_mode08_single_low_word_subtraction(){
    CSState s;set_mode(s,0x08u);s.write16(0x48DFu,2u);s.write16(0x48E1u,1u);
    std::vector<std::string> log;Reader rd(log);rd.data_return=4u;
    const auto r=stream_route_5f3e(s,0xBEEF,&rd,nullptr,nullptr);
    CHECK(r.route==StreamRouteKind::mode_08 && !r.fetched_header);
    CHECK(s.read16(0x48DFu)==0xFFFEu && s.read16(0x48E1u)==1u);
    CHECK((log==std::vector<std::string>{"read:2:24169"}));
}
static void test_header_skip_when_buffer_nonzero_even_if_remaining_zero(){
    CSState s;set_mode(s,0x02u);s.write16(0x48EEu,1u);
    std::vector<std::string> log;Calls cb(log);
    const auto r=stream_route_5f3e(s,0xBEEF,nullptr,nullptr,&cb);
    CHECK(!r.fetched_header && r.route==StreamRouteKind::mode_02 && r.continuation_ip==0x60E8u);
    CHECK(log.size()==1);
}
static void test_explicit_fail_closed_external_dependencies(){
    CSState s;set_mode(s,0x0C);s.write8(0x4740u,1u);
    std::vector<std::string> log;Calls cb(log);
    bool threw=false;
    try{(void)stream_route_5f3e(s,0xBEEF,nullptr,nullptr,&cb);}
    catch(const std::logic_error&){threw=true;}
    CHECK(threw && s.read8(0x4740)==0u && log==std::vector<std::string>{"dsp:D0"});
}
int main(){
    test_no_header_and_mode0c();
    test_header_dsp_order_and_clamp();
    test_failed_first_header_read_closes_and_sets_carry();
    test_second_header_read_ax_not_checked();
    test_invalid_mode_closes_and_unexpected_callbacks_fail();
    test_other_modes_use_explicit_continuations();
    test_mode08_single_low_word_subtraction();
    test_header_skip_when_buffer_nonzero_even_if_remaining_zero();
    test_explicit_fail_closed_external_dependencies();
    std::cout << "PASS: v016 5F3E mode/header/DSP/close, no fabricated 03/09/02/01\n";
}
