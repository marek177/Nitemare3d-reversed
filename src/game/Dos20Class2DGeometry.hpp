#pragma once
// Nitemare 3D DOS2 scoped SPAN animation -> VEC -> WALL integration.
// Connects the recovered D02J timing predicate to live LevelState map cells.
// Deliberately does not auto-discover VEC records, synthesize scheduler ticks,
// overwrite OBJECT bytes, or replace the diagnostic renderer.
#include "game/LevelState.hpp"
#include "re/N3DD02JClass2DSpanTiming.hpp"

#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace n3d::dos20::geometry {

struct Animation {
    std::uint8_t cls{0x2D};
    std::uint8_t frame{};
    std::uint32_t deadline{};
};
struct Descriptor {
    std::int16_t count{};
    std::uint16_t interval{};
};
struct Vec {
    std::uint16_t index{};
    std::uint8_t cls{0x2D};
    std::uint8_t type{};
    std::uint8_t flags{};
    std::int16_t x0{}, y0{}, x1{}, y1{};
};
struct Write {
    std::uint16_t vecIndex{};
    std::uint8_t vecType{}, x{}, y{}, before{}, after{};
    std::uint16_t originalOffset{}; // DOS ES:BX byte offset, 0x373E + 2*(64*y+x)
    std::optional<std::uint32_t> physicalAddress{}; // 20-bit if original ES supplied
};
enum class Status : std::uint8_t {
    NoSpan, NotDue, Advanced, GeometryApplied, UnsupportedDescriptor,
    UnsupportedCoordinates
};
struct Result {
    Status status{Status::NoSpan};
    std::uint8_t frame{};
    std::uint32_t deadline{};
    std::vector<Write> writes{};
};

inline bool supportedRect(const Vec& v) noexcept {
    // Unknown out-of-map and wrapping semantics are fail-closed, not guessed.
    const auto inside=[](std::int16_t n){return n>=0 && n<64;};
    if (!inside(v.x0) || !inside(v.y0)) return false;
    if (v.x0 == v.x1) return inside(v.y1) && v.y1>=v.y0;
    return inside(v.x1) && v.x1>=v.x0;
}

// "vecs" must already be the original 0x100A2-matched VEC candidates in
// original encounter order. This function does not guess the pool lookup.
// The original 0x100A2 has no VEC+05 bit0 filter: previously processed matching
// records are revisited on a later 0x104BE invocation. Their bit0 is cleared
// again and their WALL positions are rewritten (possibly 00->00).
// Geometry mutation is a synchronous explicit terminal-animation event.
inline Result advanceAndApply(LevelState& level, Animation& animation,
                              Descriptor descriptor, std::uint32_t clock,
                              std::span<Vec> vecs,
                              std::optional<std::uint16_t> originalEs = std::nullopt) {
    Result out{};
    out.frame=animation.frame;
    out.deadline=animation.deadline;
    if (descriptor.count<=0 || descriptor.count>255 ||
        (animation.cls==0x2D && descriptor.interval==0)) {
        // Interval zero is a no-op in the D02J predicate; preserve it.
        if (animation.cls==0x2D && descriptor.interval==0)
            return out;
        out.status=Status::UnsupportedDescriptor;
        return out;
    }
    const auto step=n3d::re::d02j::update(animation.cls,animation.frame,
                    descriptor.count,descriptor.interval,animation.deadline,clock);
    if (!step.dispatched) return out;
    if (step.wallClearCall) {
        // Validate all selected VECs before any wall/flag/deadline mutation.
        for (const auto& v:vecs) {
            if (v.cls==0x2D && !supportedRect(v)) {
                out.status=Status::UnsupportedCoordinates;
                return out;
            }
        }
    }
    animation.frame=step.frame;
    animation.deadline=step.deadline;
    out.frame=step.frame;
    out.deadline=step.deadline;
    if (!step.due) {
        out.status=Status::NotDue;
        return out;
    }
    if (!step.wallClearCall) {
        out.status=Status::Advanced;
        return out;
    }
    for (auto& v:vecs) {
        if (v.cls!=0x2D) continue;
        v.flags=static_cast<std::uint8_t>(v.flags & 0xFEu);
        auto write=[&](int x,int y){
            auto& cell=level.at(x,y);
            const auto before=cell.wall;
            cell.wall=0; // DO NOT change cell.object.
            const auto offset=static_cast<std::uint16_t>(0x373Eu+2u*(64u*y+x));
            std::optional<std::uint32_t> address;
            if(originalEs) address=((*originalEs*16u)+offset)&0xFFFFFu;
            out.writes.push_back(Write{v.index,v.type,
                static_cast<std::uint8_t>(x),static_cast<std::uint8_t>(y),
                before,0,offset,address});
        };
        if (v.x0==v.x1) {
            for(int y=v.y0;y<v.y1;++y) write(v.x0,y);
        } else {
            for(int x=v.x0;x<v.x1;++x) write(x,v.y0);
        }
    }
    out.status=Status::GeometryApplied;
    return out;
}
} // namespace n3d::dos20::geometry
