#include "game/Dos20VecProducer.hpp"

#include <cassert>
#include <cstdint>
#include <iostream>

using namespace n3d::dos20::vecproducer;
using n3d::LevelMap;

static Tables tables(){
    Tables t{};
    t.wallProperty[2]=0x04; t.wallClass[2]=0x01;
    t.firstWallId[1]=2;t.firstWallIdKnown[1]=true;
    t.wallClass[0x31]=0x31;t.firstWallId[0x31]=0x31;t.firstWallIdKnown[0x31]=true;
    t.wallClass[0x32]=0x32;t.firstWallId[0x32]=0x32;t.firstWallIdKnown[0x32]=true;
    t.wallClass[0x3d]=0x3d;t.firstWallId[0x3e]=0x3d;t.firstWallIdKnown[0x3e]=true;
    t.objectClass[0x22]=3;
    return t;
}
static int word(const RawVec& v, unsigned off){return v.bytes[off]|(v.bytes[off+1]<<8);}
static void testIsolated() {
    LevelMap m{};m.cells[10+10*64].wall=2;
    const Result r=produce(m,tables());
    assert(r.status==Status::Ok);
    assert(r.vecs.size()==4);
    assert((r.countByOrientation==std::array<unsigned,4>{1,1,1,1}));
    assert(r.vecs[0].bytes[7]==0 && r.vecs[0].bytes[0]==2);
    assert(word(r.vecs[0],0x0c)==640 && word(r.vecs[0],0x0e)==640);
    assert(word(r.vecs[0],0x10)==704 && word(r.vecs[0],0x12)==640);
    assert(r.vecs[1].bytes[7]==1 && word(r.vecs[1],0x0e)==704);
    assert(r.vecs[2].bytes[7]==2 && word(r.vecs[2],0x0c)==704);
    assert(r.vecs[3].bytes[7]==3 && word(r.vecs[3],0x0c)==640);
    const auto groups=groupBeforeSort(r.vecs);
    assert(groups.valid);
    for(unsigned o=0;o<4;++o){
        assert(groups.pointers[o].size()==1);
        assert(groups.pointers[o][0]==0x62AC+28*o);
    }
    // 0xFDA6 treats equal primary keys as genuinely tied.
    assert(originalPrimaryCompare(r.vecs[0],r.vecs[0])==0);
    assert(originalPrimaryCompare(r.vecs[0],r.vecs[1])<0);
    n3d::dos20::vecpool::Pool pool(r.vecs);
    n3d::dos20::vecpool::LookupCursor cursor{};
    const auto lookup=pool.lookup(10,10,1,cursor);
    assert(lookup && lookup->index==0 && lookup->near==0x62AC);
}
static void testMergedH() {
    LevelMap m{};m.cells[10+10*64].wall=2;m.cells[11+10*64].wall=2;
    const Result r=produce(m,tables());
    assert(r.status==Status::Ok && r.vecs.size()==4);
    assert((r.countByOrientation==std::array<unsigned,4>{1,1,1,1}));
    assert(word(r.vecs[0],0x0c)==640 && word(r.vecs[0],0x10)==768);
    assert(word(r.vecs[1],0x0c)==640 && word(r.vecs[1],0x10)==768);
    assert(word(r.vecs[2],0x0c)==768 && word(r.vecs[2],0x10)==768);
    assert(word(r.vecs[3],0x0c)==640 && word(r.vecs[3],0x10)==640);
}
static void testMergedV(){
    LevelMap m{};m.cells[10+10*64].wall=2;m.cells[10+11*64].wall=2;
    const Result r=produce(m,tables());
    assert(r.status==Status::Ok && r.vecs.size()==4);
    assert(word(r.vecs[2],0x0e)==640 && word(r.vecs[2],0x12)==768);
    assert(word(r.vecs[3],0x0e)==640 && word(r.vecs[3],0x12)==768);
}
static void testDoor(){
    LevelMap m{};m.cells[10+10*64].wall=0x31;
    auto r=produce(m,tables());
    assert(r.status==Status::Ok);
    assert((r.countByOrientation==std::array<unsigned,4>{0,0,1,1}));
    assert(word(r.vecs[0],0x0c)==672 && word(r.vecs[0],0x10)==672);
    assert(word(r.vecs[0],0x0e)==640 && word(r.vecs[0],0x12)==704);
    m.cells[10+10*64].wall=0x32;
    r=produce(m,tables());
    assert(r.status==Status::Ok);
    assert((r.countByOrientation==std::array<unsigned,4>{1,1,0,0}));
    assert(word(r.vecs[0],0x0e)==672 && word(r.vecs[0],0x12)==672);
    assert(word(r.vecs[0],0x0c)==640 && word(r.vecs[0],0x10)==704);
    m.cells[10+10*64].wall=0x3d;
    r=produce(m,tables());
    assert(r.status==Status::Ok && r.vecs.size()==2);
    assert(r.vecs[0].bytes[1]==0);
}
static void testUnsupported(){
    auto t=tables();LevelMap m{};m.cells[10+10*64].wall=2;
    t.firstWallIdKnown[1]=false;
    assert(produce(m,t).status==Status::MissingFirstClassId);
    t=tables();t.wallProperty[2]|=0x08;
    assert(produce(m,t).status==Status::UnsupportedResourceRemap);
    t=tables();
    // Extreme checkerboard: capacity path must be bounded rather than
    // silently overwriting the original DOS2 fixed-size VEC pool.
    for(int y=0;y<64;++y)for(int x=0;x<64;++x)
        if((x+y)%2==0)m.cells[x+64*y].wall=2;
    assert(produce(m,t).status==Status::ExceedsOriginalVecCapacity);
}
static void testRuntimeTableImport(){
    std::array<std::uint8_t,65536> ds{};
    ds[0xD00C + 2]=4;ds[0xD30E + 2]=1;ds[0xD40E + 0x22]=3;
    auto tables=tablesFromRuntimeSegment(ds);
    assert(tables);
    assert(tables->wallProperty[2]==4 && tables->wallClass[2]==1);
    assert(tables->objectClass[0x22]==3);
    assert(!tables->firstWallIdKnown[1]);
    assert(!tablesFromRuntimeSegment(std::span<const std::uint8_t>(ds.data(),4096)));
}
static void testObjectClass3Effect(){
    auto t=tables();
    LevelMap m{};m.cells[10+10*64].wall=2;m.cells[11+10*64].wall=2;
    const auto before=produce(m,t);
    assert(before.status==Status::Ok && before.vecs.size()==4);
    m.cells[11+10*64].object=0x22;
    const auto after=produce(m,t);
    assert(after.status==Status::Ok && after.vecs.size()>=4);
}
static void testBoundariesAndSortTies(){
    for(unsigned cls=0x31;cls<=0x40;++cls)
        for(unsigned o=0;o<4;++o)
            assert(specialDoorOrientation(static_cast<std::uint8_t>(cls),o)==((cls&1)?o>=2:o<=1));
    assert(!specialDoorOrientation(0x30,0) && !specialDoorOrientation(0x41,2));
    LevelMap edge{};edge.cells[0].wall=2;
    const auto r=produce(edge,tables());
    assert(r.status==Status::Ok);
    assert((r.countByOrientation==std::array<unsigned,4>{0,1,1,0}));
    std::vector<RawVec> records(333);
    assert(groupBeforeSort(records).valid);
    records.emplace_back();assert(!groupBeforeSort(records).valid);
    records.resize(1001);assert(!groupBeforeSort(records).valid);
    auto a=regularVec(10,10,0,2,tables()), b=regularVec(20,10,0,2,tables());
    assert(originalPrimaryCompare(a,b)==0); // no invented secondary X key
    setWord(b,0x0E,11*64);assert(originalPrimaryCompare(a,b)<0);
}
int main(){
    testIsolated();testMergedH();testMergedV();testDoor();testBoundariesAndSortTies();
    testUnsupported();testObjectClass3Effect();testRuntimeTableImport();
    std::cout<<"DOS20 VEC producer bounded tests PASS\n";
}
