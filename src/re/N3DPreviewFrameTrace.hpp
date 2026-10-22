#pragma once
// Preview-frame diagnostic only, not DOS tick parity.
#include <cmath>
#include <cstdint>
#include <ostream>
namespace n3d::re::preview {
struct Frame {std::uint64_t frame{},push_tick{}; double x{},y{},angle{}; std::uint16_t input{}; unsigned pushables{},moving{};};
inline void header(std::ostream& o){o<<"frame,push_tick,x,y,angle,input,pushables,moving\n";}
inline bool record(std::ostream& o,const Frame& f){
 if(!std::isfinite(f.x)||!std::isfinite(f.y)||!std::isfinite(f.angle)||f.moving>f.pushables)return false;
 o<<f.frame<<','<<f.push_tick<<','<<f.x<<','<<f.y<<','<<f.angle<<','<<f.input<<','<<f.pushables<<','<<f.moving<<'\n';return bool(o);
}
}