#include "formats/DefinitionTable.hpp"
#include "formats/MapArchive.hpp"
#include "game/Dos20Class2DGeometry.hpp"
#include "game/LevelState.hpp"

#include <array>
#include <cassert>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace n3d;
using namespace n3d::dos20::geometry;
namespace fs=std::filesystem;

struct TemporaryDefs {
    fs::path p;
    TemporaryDefs() {
        p=fs::temp_directory_path()/"n3d_d02l_test_defs";
        fs::create_directories(p);
        std::ofstream(p/"OBJECTS.1")<<"0000 0000 NULL NULL Nothing\n0001 a0f0 NULL START Start\n";
        std::ofstream(p/"WALLS.1")<<"0000 0000 NULL NULL Invalid\n00FE 0000 FAKE WALL Wall\n";
    }
    ~TemporaryDefs(){std::error_code ec;fs::remove_all(p,ec);}
    DefinitionTable objects() const {return DefinitionTable::load(p/"OBJECTS.1");}
    DefinitionTable walls() const {return DefinitionTable::load(p/"WALLS.1");}
};

LevelMap fixtureMap() {
    LevelMap m{};
    for(auto& c:m.cells){c.wall=0xFE;c.object=0;}
    m.cells[1+64].object=1; // START
    for(int x=52;x<56;++x)m.cells[x+4*64].object=0x00;
    return m;
}

std::array<Vec,2> twoOriginalVecs(){
    return {{{9,0x2D,0,0x17,52,4,56,4},
             {256,0x2D,1,0x17,52,4,56,4}}};
}

void assertWriteSequence(const std::vector<Write>& v) {
    assert(v.size()==8);
    for(std::size_t i=0;i<v.size();++i){
        const auto& w=v[i];
        const auto x=static_cast<unsigned>(52+i%4);
        assert(w.vecIndex==(i<4?9:256));
        assert(w.vecType==(i<4?0:1));
        assert(w.x==x && w.y==4);
        assert(w.before==(i<4?0xFE:0));
        assert(w.after==0);
        assert(w.originalOffset==0x39A6+2*(i%4));
        assert(w.physicalAddress.has_value());
        assert(*w.physicalAddress==0x2DBA6+2*(i%4));
    }
}

void testFixture() {
    const TemporaryDefs defs;
    auto original=fixtureMap();
    auto world=LevelState::create(original,defs.objects(),defs.walls());
    for(int x=52;x<56;++x){
        assert(world.at(x,4).wall==0xFE);
        assert(!world.wallAllowsMovement(0xFE));
        assert(world.wallObscuresView(0xFE));
    }
    assert(world.wallAllowsMovement(0));
    assert(!world.wallObscuresView(0));

    auto vecs=twoOriginalVecs();
    Animation state{0x2D,8,100};
    auto result=advanceAndApply(world,state,{9,100},100,vecs,0x2A20);
    assert(result.status==Status::GeometryApplied);
    assert(state.frame==9 && state.deadline==200);
    assert(vecs[0].flags==0x16 && vecs[1].flags==0x16);
    assertWriteSequence(result.writes);
    for(int x=52;x<56;++x){
        assert(world.at(x,4).wall==0);
        assert(world.at(x,4).object==original.at(x,4).object);
        assert(world.cellAllowsPlayer(x,4));
        assert(!world.wallObscuresView(world.at(x,4).wall));
    }

    // Original 100A2 does not reject VECs whose flag bit0 is clear.
    state.deadline=0;
    const auto again=advanceAndApply(world,state,{9,100},200,vecs,0x2A20);
    assert(again.writes.size()==8);
    for(const auto& w : again.writes) assert(w.before==0 && w.after==0);

    // 7k scope: due but frame 4->5 does not erase the wall.
    auto world7=LevelState::create(original,defs.objects(),defs.walls());
    auto v7=twoOriginalVecs();
    Animation s7{0x2D,4,100};
    const auto seven=advanceAndApply(world7,s7,{9,100},101,v7,0x2A20);
    assert(seven.status==Status::Advanced && seven.writes.empty());
    assert(s7.frame==5);
    assert(world7.at(52,4).wall==0xFE);
    assert(v7[0].flags==0x17);

    // Fail closed for unsupported geometry without partial mutation.
    auto invalid=twoOriginalVecs();
    invalid[1].x1=65;
    auto worldBad=LevelState::create(original,defs.objects(),defs.walls());
    Animation sb{0x2D,8,100};
    const auto bad=advanceAndApply(worldBad,sb,{9,100},100,invalid,0x2A20);
    assert(bad.status==Status::UnsupportedCoordinates && bad.writes.empty());
    assert(sb.frame==8 && sb.deadline==100);
    assert(invalid[0].flags==0x17 && invalid[1].flags==0x17);
    assert(worldBad.at(52,4).wall==0xFE);

    // Vertical: check DOS map offsets advance by 0x80 per row.
    auto worldVert=LevelState::create(original,defs.objects(),defs.walls());
    std::array<Vec,1> vertical{{Vec{9,0x2D,0,0x17,4,10,4,14}}};
    Animation sv{0x2D,8,100};
    const auto v=advanceAndApply(worldVert,sv,{9,100},100,vertical,0x2A20);
    assert(v.writes.size()==4);
    for(std::size_t i=1;i<v.writes.size();++i)
        assert(v.writes[i].originalOffset-v.writes[i-1].originalOffset==0x80);
}

void testPrivateOriginalMap(const fs::path& mapFile,const fs::path& objectDefs,
                            const fs::path& wallDefs,const fs::path* output) {
    std::ifstream f(mapFile,std::ios::binary);
    if(!f)throw std::runtime_error("Cannot open private MAP.1");
    std::vector<std::uint8_t> raw((std::istreambuf_iterator<char>(f)),{});
    constexpr std::size_t base=514+10*8192;
    if(raw.size()<base+8192)throw std::runtime_error("Private MAP.1 lacks E1M11");
    LevelMap m{};
    for(std::size_t i=0;i<4096;++i){
        m.cells[i].wall=raw[base+2*i];
        m.cells[i].object=raw[base+2*i+1];
    }
    auto world=LevelState::create(m,DefinitionTable::load(objectDefs),
                                   DefinitionTable::load(wallDefs));
    std::array<std::uint8_t,4096> objects{},walls{};
    for(int y=0;y<64;++y)for(int x=0;x<64;++x){
        objects[64*y+x]=world.at(x,y).object;
        walls[64*y+x]=world.at(x,y).wall;
    }
    auto vec=twoOriginalVecs();
    Animation state{0x2D,8,100};
    const auto result=advanceAndApply(world,state,{9,100},100,vec,0x2A20);
    assertWriteSequence(result.writes);
    if(output){
        std::ofstream out(*output);
        if(!out)throw std::runtime_error("Cannot create candidate trace");
        out<<"sequence,vec_index,vec_type,cell_x,cell_y,wall_offset,physical_address,before,after\n";
        for(std::size_t i=0;i<result.writes.size();++i){
            const auto& w=result.writes[i];
            out<<i+1<<','<<w.vecIndex<<','<<static_cast<unsigned>(w.vecType)
               <<','<<static_cast<unsigned>(w.x)<<','<<static_cast<unsigned>(w.y)
               <<','<<w.originalOffset<<','<<*w.physicalAddress
               <<','<<static_cast<unsigned>(w.before)
               <<','<<static_cast<unsigned>(w.after)<<'\n';
        }
    }
    unsigned wallChanges=0;
    for(int y=0;y<64;++y)for(int x=0;x<64;++x){
        const std::size_t idx=y*64+x;
        assert(world.at(x,y).object==objects[idx]);
        if(world.at(x,y).wall!=walls[idx]){
            ++wallChanges;
            assert(y==4 && x>=52 && x<=55);
            assert(walls[idx]==0xFE && world.at(x,y).wall==0);
        }
    }
    assert(wallChanges==4);
    assert(world.cellAllowsPlayer(52,4));
    std::cout<<"PRIVATE_MAP_E1M11 original wall and object layer: PASS\n";
}

int main(int argc,char** argv){
    testFixture();
    if(argc==4 || argc==5){
        const fs::path out=argc==5?fs::path(argv[4]):fs::path{};
        testPrivateOriginalMap(argv[1],argv[2],argv[3],argc==5?&out:nullptr);
    }
    std::cout<<"D02L_LEVELSTATE_BRIDGE PASS\n";
}
