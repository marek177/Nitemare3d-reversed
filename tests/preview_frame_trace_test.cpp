#include "re/N3DPreviewFrameTrace.hpp"
#include <cassert>
#include <limits>
#include <sstream>
int main(){
 using namespace n3d::re::preview;
 std::ostringstream out;
 header(out);
 assert(record(out,{0,1,1.5,2.25,0.0,65,3,1}));
 assert(out.str()=="frame,push_tick,x,y,angle,input,pushables,moving\n0,1,1.5,2.25,0,65,3,1\n");
 std::ostringstream invalid;
 assert(!record(invalid,{0,0,std::numeric_limits<double>::quiet_NaN(),2,0,0,0,0}));
 assert(!record(invalid,{0,0,0,0,0,0,1,2}));
 assert(invalid.str().empty());
}
