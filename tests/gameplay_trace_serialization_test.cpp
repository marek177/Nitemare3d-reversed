#include "re/N3DGameplayTrace.hpp"
#include <cassert>
#include <sstream>
int main() {
    using namespace n3d::re::gameplay_trace;
    std::ostringstream out;
    write_header(out);
    assert(write_snapshot(out, Snapshot{0,58,1440,3616,350,0x180,100,50,1,3,2,0,10}));
    assert(out.str()=="sample,tick,x,y,direction,input_mask,hp,ammo,weapon,object_count,guard_count,projectile_count,render_count\n0,58,1440,3616,350,384,100,50,1,3,2,0,10\n");
    Snapshot invalid{};
    invalid.direction=360;
    std::ostringstream rejected;
    assert(!write_snapshot(rejected,invalid));
    assert(rejected.str().empty());
}
