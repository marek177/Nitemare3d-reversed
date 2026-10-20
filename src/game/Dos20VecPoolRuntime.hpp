#pragma once
// Nitemare 3D DOS v2.0 VEC lookup 0x100A2 and geometry consumer 0x104BE.
// Fingerprint-scoped, original-order NON-REENTRANT contract; class 0 means
// "continue current lookup", not "search for class 0".  Does not construct
// the pool from MAP or create an original scheduler/SPAN producer.
//
// The raw 28-byte VEC record comes from a caller-owned recovered pool or a
// DOS2 64KiB DS memory snapshot. Source class, bounds, and flags are decoded
// from the original offsets. The bounded event then updates live LevelState.

#include "game/Dos20Class2DGeometry.hpp"

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <stdexcept>
#include <utility>
#include <vector>

namespace n3d::dos20::vecpool {

inline constexpr std::uint16_t kBase = 0x62AC;
inline constexpr std::uint16_t kCountField = 0x626E;
inline constexpr std::uint16_t kStride = 0x001C;
inline constexpr std::size_t kRecordBytes = 28;
inline constexpr std::size_t kMaxRecords = 1000;
inline constexpr std::size_t kSegmentBytes = 65536;

constexpr std::uint16_t u16(std::uint8_t lo, std::uint8_t hi) noexcept {
    return static_cast<std::uint16_t>(lo | (std::uint16_t(hi) << 8));
}
constexpr std::int16_t signed16(std::uint16_t bits) noexcept {
    return std::bit_cast<std::int16_t>(bits);
}
// Emulate SAR signed16,6, including negatives (C++ division rounds to zero).
constexpr int sar6(std::int16_t v) noexcept {
    const int n=static_cast<int>(v);
    return n>=0 ? n/64 : -((-n+63)/64);
}

struct RawVec {
    std::array<std::uint8_t,kRecordBytes> bytes{};

    std::uint8_t cls() const noexcept {return bytes[6];}
    std::uint8_t flags() const noexcept {return bytes[5];}
    std::uint8_t type() const noexcept {return bytes[7];}
    void clearBit0() noexcept {bytes[5] &= 0xFEu;}
    std::int16_t coord(std::size_t offset) const noexcept {
        return signed16(u16(bytes[offset],bytes[offset+1]));
    }
    geometry::Vec decoded(std::uint16_t index) const noexcept {
        geometry::Vec out{};
        out.index=index;
        out.cls=cls();out.flags=flags();out.type=type();
        out.x0=static_cast<std::int16_t>(sar6(coord(0x0C)));
        out.y0=static_cast<std::int16_t>(sar6(coord(0x0E)));
        out.x1=static_cast<std::int16_t>(sar6(coord(0x10)));
        out.y1=static_cast<std::int16_t>(sar6(coord(0x12)));
        // Original 1003E checks flags & 08h, then type 2 and type 1.
        if ((flags() & 0x08u)==0) {
            if (type()==2) {--out.x0;--out.y0;}
            if (type()==1) {--out.x1;--out.y1;}
        }
        return out;
    }
};

struct LookupCursor {
    bool initialized=false;
    std::uint16_t index{};       // original DS:3C92
    std::uint16_t near{kBase};  // original DS:3C94
    std::uint16_t cls{};         // original DS:3C96
};
struct Hit {
    std::uint16_t index{},near{};
};

class Pool {
public:
    explicit Pool(std::vector<RawVec> records) : records_(std::move(records)) {
        if (records_.size()>kMaxRecords)
            throw std::invalid_argument("DOS2 VEC capacity is 1000 records");
    }
    static std::optional<Pool> fromSegment(std::span<const std::uint8_t> ds) {
        if(ds.size()!=kSegmentBytes) return std::nullopt;
        const auto count=u16(ds[kCountField],ds[kCountField+1]);
        if(count>kMaxRecords || std::size_t(kBase)+std::size_t(count)*kStride>ds.size())
            return std::nullopt;
        std::vector<RawVec> records(count);
        for(std::size_t i=0;i<count;++i)
            for(std::size_t k=0;k<kRecordBytes;++k)
                records[i].bytes[k]=ds[kBase+i*kStride+k];
        return Pool(std::move(records));
    }
    std::size_t count() const noexcept {return records_.size();}
    const RawVec& at(std::size_t i) const {return records_.at(i);}
    RawVec& at(std::size_t i) {return records_.at(i);}
    std::optional<Hit> atNear(std::uint16_t near) const noexcept {
        if(near<kBase || (near-kBase)%kStride!=0) return std::nullopt;
        const std::size_t index=(near-kBase)/kStride;
        if(index>=records_.size()) return std::nullopt;
        return Hit{static_cast<std::uint16_t>(index),near};
    }
    std::uint16_t nearFor(std::size_t index) const noexcept {
        return static_cast<std::uint16_t>(kBase+index*kStride);
    }
    const LookupCursor& cursor() const noexcept {return cursor_;}
    void saveCursor(LookupCursor cursor) noexcept {cursor_=cursor;}

    // Exact 100A2 direct-call semantics for one nonreentrant stream:
    // nonzero class resets pointer/index and stores class; 0 resumes after
    // the prior match, then checks class and inclusive signed rect bounds.
    // Original DS globals are modeled by 'cursor'; nested lookup interference
    // still needs separate runtime proof. Unsupported uninitialized
    // continuation fails closed instead of reading arbitrary old DS values.
    std::optional<Hit> lookup(int x,int y,std::uint16_t clsOrContinue,
                              LookupCursor& cursor) const noexcept {
        if(clsOrContinue!=0) {
            cursor.initialized=true;
            cursor.index=0;
            cursor.near=kBase;
            cursor.cls=clsOrContinue;
        } else {
            if(!cursor.initialized) return std::nullopt;
            cursor.index=static_cast<std::uint16_t>(cursor.index+1);
            cursor.near=static_cast<std::uint16_t>(cursor.near+kStride);
        }
        while(cursor.index<records_.size()) {
            const auto& rec=records_[cursor.index];
            if(rec.cls()==cursor.cls) {
                const auto v=rec.decoded(cursor.index);
                // Original signed JG/JL/JGE: inclusive x0<=x<=x1,y0<=y<=y1.
                // No VEC flag (+05 bit0) test in original lookup 0x100A2.
                if(v.x0<=x && x<=v.x1 && v.y0<=y && y<=v.y1)
                    return Hit{cursor.index,cursor.near};
            }
            cursor.index=static_cast<std::uint16_t>(cursor.index+1);
            cursor.near=static_cast<std::uint16_t>(cursor.near+kStride);
        }
        return std::nullopt;
    }
private:
    std::vector<RawVec> records_;
    LookupCursor cursor_{};
};

enum class ApplyStatus : std::uint8_t {
    Applied, InvalidTrigger, UnsupportedTriggerLocation,
    UnsupportedMatchedGeometry, GeometryNotApplied
};
struct ApplyResult {
    ApplyStatus status{ApplyStatus::InvalidTrigger};
    geometry::Result geometry{};
    std::vector<Hit> matched{};
};

// Called at a validated original class-2D terminal SPAN event.
// Precisely mimics 104BE: decode triggering VEC bounds, start lookup with
// VEC+06 class at trigger.x0,y0, then use classArg=0 to find every later
// match. DOES NOT filter on VEC+05 bit0. Values not representable as safe
// LevelState cells deliberately fail before mutation; original 16-bit wrap
// / malformed geometry semantics are still open.
inline ApplyResult advanceFromPool(n3d::LevelState& level,
                                   geometry::Animation& animation,
                                   geometry::Descriptor descriptor,
                                   std::uint32_t clock,
                                   Pool& pool,
                                   std::uint16_t triggerNear,
                                   std::optional<std::uint16_t> originalEs=std::nullopt) {
    ApplyResult result{};
    const auto trigger=pool.atNear(triggerNear);
    if(!trigger || pool.at(trigger->index).cls()!=0x2D || animation.cls!=0x2D)
        return result;
    const auto source=pool.at(trigger->index).decoded(trigger->index);
    if(source.x0<0 || source.x0>=64 || source.y0<0 || source.y0>=64) {
        result.status=ApplyStatus::UnsupportedTriggerLocation;
        return result;
    }

    const auto predicted=n3d::re::d02j::update(animation.cls,animation.frame,
                             descriptor.count,descriptor.interval,animation.deadline,clock);
    std::vector<geometry::Vec> selected{};
    LookupCursor nextCursor=pool.cursor();
    if(predicted.wallClearCall) {
        auto found=pool.lookup(source.x0,source.y0,source.cls,nextCursor);
        while(found) {
            result.matched.push_back(*found);
            const auto vec=pool.at(found->index).decoded(found->index);
            // Fail closed, including previously inactive matched VECs.
            if(!geometry::supportedRect(vec)) {
                result.status=ApplyStatus::UnsupportedMatchedGeometry;
                return result;
            }
            selected.push_back(vec);
            found=pool.lookup(source.x0,source.y0,0,nextCursor);
        }
    }
    result.geometry=geometry::advanceAndApply(level,animation,descriptor,
                                               clock,selected,originalEs);
    if(result.geometry.status==geometry::Status::UnsupportedCoordinates ||
       result.geometry.status==geometry::Status::UnsupportedDescriptor) {
        result.status=ApplyStatus::UnsupportedMatchedGeometry;
        return result;
    }
    if(predicted.wallClearCall) {
        for(const auto& vec : selected)
            pool.at(vec.index).bytes[5]=vec.flags;
        pool.saveCursor(nextCursor);
    }
    result.status=result.geometry.status==geometry::Status::GeometryApplied
                  ?ApplyStatus::Applied:ApplyStatus::GeometryNotApplied;
    return result;
}
} // namespace n3d::dos20::vecpool
