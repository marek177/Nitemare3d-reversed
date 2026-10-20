#include "re/N3DDos20TextureUEdge.hpp"
#include "renderer/Win16WallRasterCore.hpp"
#include <array>
#include <cassert>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace dos=n3d::re::dos20::texture_u;
namespace win=nitemare3d::re::win16;

constexpr dos::VecEdge edge(unsigned o,unsigned cls=1,unsigned flags=0,
                            int firstX=40,int lastX=80,int len=64){
    dos::VecEdge v{};
    v.screenX1=static_cast<std::int16_t>(firstX);
    v.screenX2=static_cast<std::int16_t>(lastX);
    v.flags=static_cast<std::uint8_t>(flags);
    v.renderClass=static_cast<std::uint8_t>(cls);
    v.orientation=static_cast<std::uint8_t>(o);
    if(o==0 || o==1)v.worldX2=static_cast<std::int16_t>(len);
    else v.worldY2=static_cast<std::int16_t>(len);
    return v;
}
constexpr win::VecRecord convert(const dos::VecEdge& v){
    win::VecRecord w{};
    w.orientation=v.orientation;w.flags=v.flags;w.renderClass=v.renderClass;
    w.x1=v.worldX1;w.y1=v.worldY1;w.x2=v.worldX2;w.y2=v.worldY2;
    w.screenX1=v.screenX1;w.screenX2=v.screenX2;
    return w;
}
static_assert(dos::correctRaw(edge(3,2,0,166,193),166,0,128)==127);
static_assert(dos::correctRaw(edge(3,1,0,46,101),101,64,128)==63);
static_assert(dos::correctRaw(edge(0,2,0,116,146),116,62,128)==63);
static_assert(dos::correctRaw(edge(3,2,8,166,193),166,0,128)==0);
static_assert(dos::correctRaw(edge(0,1,0,40,80),60,-1,128)==127);
static_assert(!dos::correctBounded(edge(0),42,8,96));
static_assert(!dos::correctBounded(edge(4),42,8,128));

static void syntheticCrossBuild(){
    unsigned tested=0,realCorrections=0;
    const std::array<int,17> sourceU{-32768,-129,-128,-65,-64,-2,-1,0,1,
                                     62,63,64,65,126,127,128,32767};
    const std::array<int,13> xDelta{-100,-9,-8,-7,-1,0,1,6,7,8,9,42,100};
    for(unsigned o=0;o<4;++o)for(unsigned cls:{1u,2u,0x3fu,0x40u})
        for(unsigned flags:{0u,8u,0x20u,0x28u})
          for(unsigned width:{64u,128u})
            for(int d:xDelta)for(int raw:sourceU){
                const auto v=edge(o,cls,flags,40,80,64);
                const auto x=static_cast<std::int16_t>(40+d);
                const auto u=static_cast<std::int16_t>(raw);
                const auto result=dos::correctBounded(v,x,u,width);
                assert(result);
                const auto reference=win::selectTextureU(
                    convert(v),x,u,static_cast<std::uint16_t>(width));
                assert(*result==reference);
                ++tested;
                if(*result!=(static_cast<std::uint16_t>(u)&(width-1)))
                    ++realCorrections;
            }
    assert(tested==4u*4u*4u*2u*13u*17u && realCorrections>0);
    std::cout<<"SYNTHETIC_CROSS_BUILD_EXACT: "<<tested
             <<", nontrivial edge corrections="<<realCorrections<<"\n";
}
static std::vector<std::string> splitCsv(const std::string& line){
    std::vector<std::string> out;
    std::istringstream ss(line);
    std::string field;
    while(std::getline(ss,field,','))out.push_back(field);
    return out;
}
static void replayPrivateOriginal(const std::string& file){
    std::ifstream in(file);
    if(!in)throw std::runtime_error("Private original 22CA witness CSV missing");
    std::string line;
    if(!std::getline(in,line))throw std::runtime_error("Missing CSV header");
    if(!line.empty() && line.back()=='\r')line.pop_back();
    if(line!="session,event,screen_x,x1,x2,orientation,render_class,flags,world_length,unadjusted_u,width,observed_u,vec_near")
        throw std::runtime_error("Unexpected private witness schema");
    unsigned count=0,corrected=0;
    std::array<unsigned,4> orientations{};
    while(std::getline(in,line)){
        if(line.empty())continue;
        const auto p=splitCsv(line);
        if(p.size()!=13)throw std::runtime_error("Unexpected CSV field count");
        const int x=std::stoi(p[2]),x1=std::stoi(p[3]),x2=std::stoi(p[4]);
        const unsigned o=static_cast<unsigned>(std::stoul(p[5]));
        const unsigned cls=static_cast<unsigned>(std::stoul(p[6]));
        const unsigned flags=static_cast<unsigned>(std::stoul(p[7]));
        const int len=std::stoi(p[8]),raw=std::stoi(p[9]);
        const unsigned width=static_cast<unsigned>(std::stoul(p[10]));
        const unsigned expected=static_cast<unsigned>(std::stoul(p[11]));
        if(x<8 || x>311 || o>3 || width!=128 || expected>=width)
            throw std::runtime_error("Original witness outside verified scope");
        const auto v=edge(o,cls,flags,x1,x2,len);
        const auto actual=dos::correctBounded(v,static_cast<std::int16_t>(x),
                                             static_cast<std::int16_t>(raw),width);
        const auto win16=win::selectTextureU(convert(v),
                static_cast<std::int16_t>(x),static_cast<std::int16_t>(raw),
                static_cast<std::uint16_t>(width));
        if(!actual || *actual!=expected || win16!=expected){
            std::cerr<<"U mismatch at original screen X="<<x
                     <<" expected="<<expected
                     <<" DOS2="<<(actual?int(*actual):-1)
                     <<" Win16="<<win16<<"\n";
            throw std::runtime_error("Original DOS2 22CA mismatched");
        }
        count++;orientations[o]++;
        if(expected!=(static_cast<unsigned>(raw)&(width-1)))corrected++;
    }
    if(count!=1520 || corrected!=23)throw std::runtime_error("Incomplete original corpus");
    for(unsigned i:orientations)if(!i)throw std::runtime_error("Missing original orientation");
    std::cout<<"ORIGINAL_RUNTIME_EXACT: "<<count<<"/1520, corrected="<<corrected<<"\n";
}
int main(int argc,char**argv){
    try{
        syntheticCrossBuild();
        if(argc>1)replayPrivateOriginal(argv[1]);
        return 0;
    }catch(const std::exception& error){
        std::cerr<<"FAIL: "<<error.what()<<"\n";
        return 1;
    }
}
