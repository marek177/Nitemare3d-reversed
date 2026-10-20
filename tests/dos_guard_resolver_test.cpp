#include "re/N3DDosGuardResolver.hpp"
#include <array>
#include <cstdlib>
#include <iostream>
namespace gr=n3d::re::dos::guardresolver;
static void check(bool ok) { if(!ok) { std::cerr<<"GUARD resolver contract mismatch\n"; std::exit(1); } }
int main() {
    std::array<std::uint8_t,65536> world{},area{};
    const auto put=[](auto& bank,unsigned index,gr::FarPointer p) {
        const auto at=std::uint16_t(index*28u+0x12u);
        bank[at]=std::uint8_t(p.offset); bank[std::uint16_t(at+1u)]=std::uint8_t(p.offset>>8u);
        bank[std::uint16_t(at+2u)]=std::uint8_t(p.segment); bank[std::uint16_t(at+3u)]=std::uint8_t(p.segment>>8u);
    };
    const gr::FarPointer cell{0x1234,0x5678};
    put(world,2,cell); area=world;
    std::array<gr::Guard,3> guards{{{2,0x0A,1,7},{2,1,9,8},{2,1,1,9}}};
    auto run=[&](std::int16_t count=3) {return gr::resolve(guards,count,world,area,cell);};
    auto r=run(); check(r.outcome==gr::Outcome::Accepted && r.guardIndex==2);
    // An earlier rejected duplicate does not force fatal diagnostic.
    r=run(2);check(r.outcome==gr::Outcome::RejectedMatchExit1 && r.guardIndex==0);
    check(r.diagnostic0D==7 && r.diagnostic0C==1 && r.diagnostic0B==10);
    guards[0].objectIndex=1;r=run(2);check(r.outcome==gr::Outcome::RejectedMatchExit1 && r.guardIndex==1);
    guards[1].objectIndex=1;check(run(2).outcome==gr::Outcome::MissingMatchExit1);
    check(run(0).outcome==gr::Outcome::MissingMatchExit1);
    check(run(-1).outcome==gr::Outcome::MissingMatchExit1);
    check(run(4).outcome==gr::Outcome::IncompleteSnapshot);
    check(gr::resolve(guards,3,{},area,cell).outcome==gr::Outcome::IncompleteSnapshot);
    // Second-bank aliases are supplied, never silently assumed.
    area.fill(0); guards[2].field0B=10;
    check(run().outcome==gr::Outcome::MissingMatchExit1);
    check(gr::resolve(guards,3,world,{},cell).outcome==gr::Outcome::IncompleteSnapshot);
    put(area,2,cell);check(run().outcome==gr::Outcome::RejectedMatchExit1);
    // Both FAR words must match. Either mismatch prevents acceptance.
    guards[2].field0B=1;put(world,2,{cell.offset,0x5679});area=world;
    check(run().outcome==gr::Outcome::MissingMatchExit1);
    put(world,2,{0x1235,cell.segment});area=world;
    check(run().outcome==gr::Outcome::MissingMatchExit1);
    // Low-word multiplication is explicit even for high-bit object indices.
    guards[2].objectIndex=0xFFFF;put(world,0xFFFF,cell);
    check(run().outcome==gr::Outcome::Accepted);
    std::cout<<"Bounded GUARD lookup scenarios PASS; original runtime not exercised\n";
}
