#include "re/N3DDos20CedcProjection.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
namespace dos=n3d::re::dos20::cedc;

static_assert(dos::subtract16(-32768,32767)==1);
static_assert(dos::callerBefore22ca(27,27,true)==65482);
static_assert(!dos::project({}));
constexpr dos::Input archivedCase{308,160,0,337,459074,0,-221544,0,-724,true};
static_assert(dos::project(archivedCase).has_value());
static_assert(dos::project(archivedCase)->screenOrVerticalQuotient==201611);
static_assert(dos::project(archivedCase)->combinedNumerator==-19933);
static_assert(dos::project(archivedCase)->returnedAX==27);

static std::vector<std::string> split(const std::string& in){
    std::vector<std::string> tokens;
    std::istringstream stream(in);
    std::string cell;
    while(std::getline(stream,cell,','))tokens.push_back(cell);
    return tokens;
}
static std::int32_t asInt(const std::string& s){
    return static_cast<std::int32_t>(std::stoll(s));
}
static bool parseBool(const std::string& s){
    if(s=="True")return true;
    if(s=="False")return false;
    throw std::runtime_error("Invalid private CPU boolean");
}
static void verifyOriginalPrivateCSV(const std::string& filename){
    std::ifstream f(filename);
    if(!f)throw std::runtime_error("Private original CEDC CSV unavailable");
    std::string line;
    if(!std::getline(f,line))throw std::runtime_error("Missing original CSV header");
    if(!line.empty()&&line.back()=='\r')line.pop_back();
    const auto header=split(line);
    constexpr std::array<const char*,24> fields{
        "session","first_event","last_event","x","orientation","branch",
        "branch_fourway","span","screen_delta","center_x","inverse_scale",
        "vertical_numerator","product32","trig_divisor",
        "cached_2643_product32","partial_original_result",
        "final_original_num","cedc_quotient_original","returned_ax",
        "candidate_ax","caller_local16","caller_negates_u",
        "caller_pre_edge_u","candidate_unadjusted_u"};
    if(header.size()!=fields.size())throw std::runtime_error("Wrong CEDC CSV layout");
    for(unsigned i=0;i<fields.size();++i)
        if(header[i]!=fields[i])throw std::runtime_error("Wrong CEDC CSV field");
    unsigned verified=0,directCallerImul=0;
    std::array<unsigned,4> branches{};
    while(std::getline(f,line)){
        if(line.empty())continue;
        if(line.back()=='\r')line.pop_back();
        const auto c=split(line);
        if(c.size()!=fields.size())throw std::runtime_error("Truncated CEDC row");
        dos::Path expected{};
        bool selector=false;
        if(c[6]=="selector1_horizontal"){
            expected=dos::Path::Selector1Horizontal;selector=true;++branches[0];
        }else if(c[6]=="selector1_vertical"){
            expected=dos::Path::Selector1Vertical;selector=true;++branches[1];
        }else if(c[6]=="selector0_horizontal"){
            expected=dos::Path::Selector0Horizontal;++branches[2];
        }else if(c[6]=="selector0_vertical"){
            expected=dos::Path::Selector0Vertical;++branches[3];
        }else throw std::runtime_error("Invalid original DOS2 branch");
        const auto div=static_cast<std::int16_t>(asInt(c[13]));
        const dos::Input in{
            static_cast<std::int16_t>(asInt(c[3])),
            static_cast<std::int16_t>(asInt(c[9])),
            static_cast<std::uint8_t>(asInt(c[4])),
            static_cast<std::uint16_t>(asInt(c[7])),
            asInt(c[10]),asInt(c[11]),asInt(c[12]),
            static_cast<std::int16_t>(selector?0:div),
            static_cast<std::int16_t>(selector?div:0),
            selector
        };
        const auto got=dos::project(in);
        if(!got || got->path!=expected ||
           got->screenOrVerticalQuotient!=asInt(c[15]) ||
           got->combinedNumerator!=asInt(c[16]) ||
           got->quotient32!=asInt(c[17]) ||
           got->returnedAX!=asInt(c[18])){
            std::cerr<<"Original CEDC mismatch at event="<<c[1]
                     <<" x="<<c[3]<<"\n";
            throw std::runtime_error("Original CEDC quotient differs");
        }
        if(!c[14].empty()){
            if(in.product32!=asInt(c[14]))
                throw std::runtime_error("Original parent IMUL differs");
            ++directCallerImul;
        }
        if(dos::callerBefore22ca(got->returnedAX,
                static_cast<std::uint16_t>(asInt(c[20])),
                parseBool(c[21]))!=asInt(c[22]))
            throw std::runtime_error("Original caller raw-U mismatch");
        ++verified;
    }
    if(verified!=1808 || directCallerImul!=1804 ||
       branches!=std::array<unsigned,4>{1030,474,187,117})
        throw std::runtime_error("Original CEDC corpus incomplete");
    std::cout<<"ORIGINAL_DOS2_CEDC_EXACT "<<verified
             <<"/1808; caller IMUL "<<directCallerImul<<"/1808\n";
}
static void synthetic(){
    const auto seed=dos::project(archivedCase);
    assert(seed && seed->returnedAX==27);
    // An 8086 SUB wraps signed-16 before the DOS2 signed-32 multiply.
    dos::Input p=archivedCase;
    p.screenX=-32768;p.screenCenterX=32767;p.inverseScale=10;
    p.spanYQ4=2;p.product32=0;p.cosineQ10=1;
    auto r=dos::project(p);
    assert(r && r->screenOrVerticalQuotient==5);
    // EAX is 32-bit even when the mathematical product exceeds INT32_MAX.
    p.screenX=260;p.screenCenterX=160;p.inverseScale=0x7fffffff;
    p.spanYQ4=1;
    r=dos::project(p);assert(r && r->screenOrVerticalQuotient==-100);
    // Signed IDIV truncates toward zero rather than floors a negative value.
    p={160,160,0,2,0,-7,0,-2,0,false};
    r=dos::project(p);
    assert(r && r->screenOrVerticalQuotient==-3 && r->quotient32==1);
    p={200,160,3,2,10,-7,4,-2,-3,false};
    r=dos::project(p);
    assert(r && r->path==dos::Path::Selector0Vertical);
    assert(r->screenOrVerticalQuotient==200 && r->quotient32==98);
    p.selector415cNonzero=true;p.cosineQ10=-3;
    r=dos::project(p);
    assert(r && r->path==dos::Path::Selector1Vertical);
    p.orientation=0;
    r=dos::project(p);
    assert(r && r->path==dos::Path::Selector1Horizontal);
    p.cosineQ10=0;assert(!dos::project(p));
    p.cosineQ10=-1;p.spanYQ4=1;p.screenX=160;p.screenCenterX=160;
    p.inverseScale=0;p.product32=static_cast<std::int32_t>(0x80000000u);
    assert(!dos::project(p)); // INT32_MIN/-1: original IDIV would fault
    p.orientation=4;assert(!dos::project(p));
    p.orientation=0;p.spanYQ4=0;assert(!dos::project(p));
    std::cout<<"SYNTHETIC_CEDC_ARITHMETIC_PASS\n";
}
int main(int argc,char**argv){
    try{
        synthetic();
        if(argc>1)verifyOriginalPrivateCSV(argv[1]);
        return 0;
    }catch(const std::exception& e){
        std::cerr<<"FAIL: "<<e.what()<<"\n";
        return 1;
    }
}
