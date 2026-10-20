#include "game/Dos20VecPoolRuntime.hpp"

#include "formats/DefinitionTable.hpp"
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

using n3d::dos20::vecpool::RawVec;
using n3d::dos20::vecpool::Pool;
using n3d::dos20::vecpool::LookupCursor;
using n3d::dos20::vecpool::ApplyStatus;
using n3d::dos20::vecpool::advanceFromPool;
namespace fs=std::filesystem;

static void setWord(RawVec& vec, unsigned off, int raw) {
    const auto u=static_cast<std::uint16_t>(raw);
    vec.bytes[off]=static_cast<std::uint8_t>(u & 0xffu);
    vec.bytes[off+1]=static_cast<std::uint8_t>((u>>8u)&0xffu);
}
static RawVec makeRaw(std::uint8_t cls,std::uint8_t type,std::uint8_t flags,
                      int x0,int y0,int x1,int y1) {
    RawVec r{};
    r.bytes[5]=flags;r.bytes[6]=cls;r.bytes[7]=type;
    setWord(r,0x0c,x0*64);setWord(r,0x0e,y0*64);
    setWord(r,0x10,x1*64);setWord(r,0x12,y1*64);
    return r;
}
static std::vector<RawVec> originalLikeRecords() {
    std::vector<RawVec> records(257);
    records[3]=makeRaw(0x2D,0,0x17,10,4,12,4);  // same class, misses (52,4)
    records[8]=makeRaw(0x2E,0,0x17,52,4,56,4);  // other class
    records[9]=makeRaw(0x2D,0,0x17,52,4,56,4);  // first matching VEC
    // DOS 1003E type 1 and flags & 8==0: endpoint values each decrease 1.
    records[256]=makeRaw(0x2D,1,0x17,52,4,57,5);
    return records;
}
static void testOriginalLookup() {
    Pool pool(originalLikeRecords());
    LookupCursor c{};
    assert(!pool.lookup(52,4,0,c)); // uninitialized "continue" fails closed
    const auto first=pool.lookup(52,4,0x2D,c);
    assert(first && first->index==9 && first->near==0x63A8);
    assert(c.index==9 && c.cls==0x2D);
    const auto second=pool.lookup(52,4,0,c);
    assert(second && second->index==256 && second->near==0x7EAC);
    assert(!pool.lookup(52,4,0,c));
    assert(c.index==257);
    // Inclusive endpoints exactly as signed CMP/JG/JL/JGE at 100A2.
    assert(pool.lookup(56,4,0x2D,c)->index==9);
    assert(!pool.lookup(57,4,0x2D,c));
    assert(pool.lookup(52,4,0x2E,c)->index==8);
    assert(pool.atNear(0x63A8)->index==9);
    assert(!pool.atNear(0x63A9));
    assert(!pool.atNear(0x7EC8)); // one past last record

    const auto type1=pool.at(256).decoded(256);
    assert(type1.x0==52 && type1.y0==4);
    assert(type1.x1==56 && type1.y1==4);
    auto type2=makeRaw(0x2D,2,0x17,53,5,56,7).decoded(0);
    assert(type2.x0==52 && type2.y0==4 && type2.x1==56 && type2.y1==7);
    auto withoutAdjust=makeRaw(0x2D,1,0x1F,52,4,57,5).decoded(0);
    assert(withoutAdjust.x1==57 && withoutAdjust.y1==5);
    auto negative=makeRaw(0x2D,0,0x17,-1,-2,0,0).decoded(0);
    assert(negative.x0==-1 && negative.y0==-2);

    // Load from the exact original 64KiB DS layout, not just a test vector.
    std::array<std::uint8_t,65536> ds{};
    ds[0x626e]=1;ds[0x626f]=1; // 257 records
    auto entries=originalLikeRecords();
    for(std::size_t i=0;i<entries.size();++i)
        for(std::size_t j=0;j<28;++j)
            ds[0x62ac+i*28+j]=entries[i].bytes[j];
    auto imported=Pool::fromSegment(ds);
    assert(imported && imported->count()==257);
    assert(imported->lookup(52,4,0x2D,c)->index==9);
    assert(imported->lookup(52,4,0,c)->index==256);
    ds[0x626e]=0xe9;ds[0x626f]=0x03; // 1001, invalid
    assert(!Pool::fromSegment(ds));
    assert(!Pool::fromSegment(std::span<const std::uint8_t>(ds.data(),4096)));
}

struct Defs {
    fs::path root;
    explicit Defs(fs::path root):root(std::move(root)){
        fs::create_directories(this->root);
        std::ofstream(this->root/"o.txt")<<"0000 0000 NULL NULL Empty\n0001 0000 NULL START Start\n";
        std::ofstream(this->root/"w.txt")<<"0000 0000 NULL NULL None\n00FE 0000 FAKE WALL Block\n";
    }
    ~Defs(){std::error_code ec;fs::remove_all(root,ec);}
    auto objects()const{return n3d::DefinitionTable::load(root/"o.txt");}
    auto walls()const{return n3d::DefinitionTable::load(root/"w.txt");}
};
static n3d::LevelMap testMap() {
    n3d::LevelMap map{};
    for(auto& c:map.cells)c.wall=0xFE;
    map.cells[1+64].object=1;
    return map;
}
static void checkEvent(const n3d::dos20::vecpool::ApplyResult& r) {
    assert(r.status==ApplyStatus::Applied);
    assert(r.matched.size()==2);
    assert(r.matched[0].index==9 && r.matched[1].index==256);
    assert(r.geometry.writes.size()==8);
    for(std::size_t i=0;i<8;++i) {
        const auto& w=r.geometry.writes[i];
        assert(w.vecIndex==(i<4?9:256));
        assert(w.vecType==(i<4?0:1));
        assert(w.x==52+i%4 && w.y==4);
        assert(w.originalOffset==0x39A6+2*(i%4));
        assert(w.physicalAddress && *w.physicalAddress==0x2DBA6+2*(i%4));
        assert(w.before==(i<4?0xFE:0) && w.after==0);
    }
}
static void testGeometry(const Defs& defs) {
    auto pool=Pool(originalLikeRecords());
    auto world=n3d::LevelState::create(testMap(),defs.objects(),defs.walls());
    n3d::dos20::geometry::Animation anim{0x2D,8,100};
    const auto r=advanceFromPool(world,anim,{9,100},100,pool,0x7EAC,0x2A20);
    checkEvent(r);
    assert(anim.frame==9 && anim.deadline==200);
    assert(pool.at(9).flags()==0x16 && pool.at(256).flags()==0x16);
    for(int x=52;x<56;++x){
        assert(world.at(x,4).wall==0);
        assert(world.at(x,4).object==0);
        assert(world.cellAllowsPlayer(x,4));
        assert(!world.wallObscuresView(world.at(x,4).wall));
    }
    // IMPORTANT original 100A2 has no active-bit guard; repeat still writes.
    const auto repeated=advanceFromPool(world,anim,{9,100},200,pool,0x7EAC,0x2A20);
    assert(repeated.status==ApplyStatus::Applied);
    assert(repeated.matched.size()==2 && repeated.geometry.writes.size()==8);
    for(const auto& w:repeated.geometry.writes)assert(w.before==0 && w.after==0);

    auto noGeometry=Pool(originalLikeRecords());
    auto w7=n3d::LevelState::create(testMap(),defs.objects(),defs.walls());
    n3d::dos20::geometry::Animation a7{0x2D,4,100};
    const auto r7=advanceFromPool(w7,a7,{9,100},101,noGeometry,0x7EAC,0x2A20);
    assert(r7.status==ApplyStatus::GeometryNotApplied);
    assert(r7.geometry.status==n3d::dos20::geometry::Status::Advanced);
    assert(r7.geometry.writes.empty() && r7.matched.empty());
    assert(a7.frame==5 && w7.at(52,4).wall==0xFE);

    // Clear WALL only: even a blocking unknown OBJECT on that cell survives.
    auto occupiedMap=testMap();
    occupiedMap.cells[52+4*64].object=0xA5;
    auto occupied=n3d::LevelState::create(occupiedMap,defs.objects(),defs.walls());
    std::array<std::uint8_t,4096> objectsBefore{};
    for(int y=0;y<64;++y) for(int x=0;x<64;++x)
        objectsBefore[y*64+x]=occupied.at(x,y).object;
    auto occupiedPool=Pool(originalLikeRecords());
    n3d::dos20::geometry::Animation occupiedAnim{0x2D,8,100};
    assert(advanceFromPool(occupied,occupiedAnim,{9,100},100,occupiedPool,0x7EAC).status==ApplyStatus::Applied);
    assert(occupied.at(52,4).wall==0 && occupied.at(52,4).object==0xA5);
    assert(!occupied.cellAllowsPlayer(52,4));
    for(int y=0;y<64;++y) for(int x=0;x<64;++x)
        assert(occupied.at(x,y).object==objectsBefore[y*64+x]);

    // Out of bounds matched VEC aborts *all* writes and preserves the cursor.
    auto invalidRecords=originalLikeRecords();
    invalidRecords[256]=makeRaw(0x2D,1,0x17,52,4,66,5);
    auto invalid=Pool(std::move(invalidRecords));
    auto wbad=n3d::LevelState::create(testMap(),defs.objects(),defs.walls());
    n3d::dos20::geometry::Animation badAnim{0x2D,8,100};
    const auto bad=advanceFromPool(wbad,badAnim,{9,100},100,invalid,0x7EAC,0x2A20);
    assert(bad.status==ApplyStatus::UnsupportedMatchedGeometry);
    assert(badAnim.frame==8 && badAnim.deadline==100);
    assert(invalid.at(9).flags()==0x17 && invalid.at(256).flags()==0x17);
    assert(!invalid.cursor().initialized);
    assert(wbad.at(52,4).wall==0xFE);
    assert(advanceFromPool(wbad,badAnim,{9,100},100,invalid,0x63A9,0x2A20).status==ApplyStatus::InvalidTrigger);
}

static void privateOriginalMap(const fs::path& mapfile,const fs::path& objects,
                               const fs::path& walls,const fs::path& outfile) {
    std::ifstream in(mapfile,std::ios::binary);
    if(!in)throw std::runtime_error("Cannot open private MAP.1");
    std::vector<std::uint8_t> raw((std::istreambuf_iterator<char>(in)),{});
    constexpr std::size_t base=514+10*8192;
    if(raw.size()<base+8192)throw std::runtime_error("Missing E1M11 map");
    n3d::LevelMap m{};
    for(std::size_t i=0;i<4096;++i){
        m.cells[i].wall=raw[base+i*2];m.cells[i].object=raw[base+i*2+1];
    }
    auto world=n3d::LevelState::create(m,n3d::DefinitionTable::load(objects),
                                       n3d::DefinitionTable::load(walls));
    std::array<std::uint8_t,4096> priorObjects{};
    for(std::size_t i=0;i<4096;++i)
        priorObjects[i]=world.at(static_cast<int>(i%64),static_cast<int>(i/64)).object;
    for(int x=52;x<56;++x){
        assert(world.at(x,4).wall==0xFE && world.at(x,4).object==0);
    }
    auto pool=Pool(originalLikeRecords());
    n3d::dos20::geometry::Animation a{0x2D,8,100};
    const auto r=advanceFromPool(world,a,{9,100},100,pool,0x7EAC,0x2A20);
    checkEvent(r);
    for(std::size_t i=0;i<4096;++i)
        assert(world.at(static_cast<int>(i%64),static_cast<int>(i/64)).object==priorObjects[i]);
    if(!outfile.empty()){
        std::ofstream out(outfile);
        if(!out)throw std::runtime_error("Cannot open output trace");
        out<<"sequence,vec_index,vec_type,cell_x,cell_y,wall_offset,physical_address,before,after\n";
        for(std::size_t i=0;i<r.geometry.writes.size();++i){
            const auto& w=r.geometry.writes[i];
            out<<i+1<<','<<w.vecIndex<<','<<int(w.vecType)
               <<','<<int(w.x)<<','<<int(w.y)<<','<<w.originalOffset
               <<','<<*w.physicalAddress<<','<<int(w.before)<<','<<int(w.after)<<'\n';
        }
    }
    std::cout<<"D02M private-original MAP1 E1M11: PASS\n";
}

int main(int argc,char** argv) {
    const Defs defs(fs::temp_directory_path()/"n3d_d02m_vec_pool_test_defs");
    testOriginalLookup();
    testGeometry(defs);
    if(argc==5)
        privateOriginalMap(argv[1],argv[2],argv[3],argv[4]);
    std::cout<<"D02M vec-pool lookup and LevelState integration: PASS\n";
    return 0;
}
