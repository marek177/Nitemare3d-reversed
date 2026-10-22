#pragma once
// Opt-in state serializer, not an original DOS execution hook.
#include <cstdint>
#include <ostream>
namespace n3d::re::gameplay_trace {
struct Snapshot {
    std::uint64_t sample{}, tick{};
    std::int32_t x{}, y{};
    std::uint16_t direction{}, input_mask{};
    std::uint32_t hp{}, ammo{}, weapon{}, object_count{}, guard_count{}, projectile_count{};
    std::uint64_t render_count{};
};
inline void write_header(std::ostream& out) {
    out << "sample,tick,x,y,direction,input_mask,hp,ammo,weapon,"
           "object_count,guard_count,projectile_count,render_count\n";
}
inline bool write_snapshot(std::ostream& out, const Snapshot& s) {
    if(s.direction>=360) return false;
    out << s.sample << ',' << s.tick << ',' << s.x << ',' << s.y << ','
        << s.direction << ',' << s.input_mask << ',' << s.hp << ','
        << s.ammo << ',' << s.weapon << ',' << s.object_count << ','
        << s.guard_count << ',' << s.projectile_count << ',' << s.render_count << '\n';
    return bool(out);
}
}
