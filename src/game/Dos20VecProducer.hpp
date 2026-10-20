#pragma once
// DOS v2.0 VEC producer: bounded original-ASM-derived MAP data plane.
// Original normalized MZ offsets 0x10892 (4-pass scan), 0x10BAC (dispatcher),
// 0x105EA (normal wall), 0x106F2 (special door), 0x10854 (extend).
//
// Caller supplies runtime wall-property/class, object-class, and class-first-ID
// tables: they are not derivable from the bare MAP bytes alone. Unsupported
// bit08 resource remap (106BC..106EB) is intentionally REJECTED, not guessed.
// Original 1000-vector capacity, 16-bit/mutable global and alias edge cases
// beyond the bounded input domain still need separate proof.
#include "formats/MapArchive.hpp"
#include "game/Dos20VecPoolRuntime.hpp"

#include <array>
#include <cstdint>
#include <optional>
#include <span>
#include <vector>

namespace n3d::dos20::vecproducer {

using vecpool::RawVec;

struct Tables {
    std::array<std::uint8_t,256> wallProperty{}; // original DS:D00C
    std::array<std::uint8_t,256> wallClass{};    // original DS:D30E
    std::array<std::uint8_t,256> objectClass{};  // original DS:D40E
    std::array<std::uint8_t,256> firstWallId{}; // supplied original F7:0004 lookup
    std::array<bool,256> firstWallIdKnown{};
};
// Import exact original runtime property/class tables when a *private* DOS2
// DS snapshot exists. Do not guess F7:0004 class-first IDs from the image.
inline std::optional<Tables> tablesFromRuntimeSegment(
        std::span<const std::uint8_t> ds) noexcept {
    if(ds.size()!=65536) return std::nullopt;
    Tables t{};
    for(std::size_t i=0;i<256;++i) {
        t.wallProperty[i]=ds[0xD00C + i];
        t.wallClass[i]=ds[0xD30E + i];
        t.objectClass[i]=ds[0xD40E + i];
    }
    return t;
}

enum class Status : std::uint8_t {
    Ok, MissingFirstClassId, UnsupportedResourceRemap,
    ExceedsOriginalVecCapacity
};
struct Result {
    Status status{Status::Ok};
    std::array<unsigned,4> countByOrientation{};
    std::vector<RawVec> vecs{};
};

constexpr bool specialDoorOrientation(std::uint8_t cls, unsigned orientation) noexcept {
    if (cls<0x31 || cls>0x40 || orientation>3) return false;
    // 10592 dispatch: odd classes go to 105CC (type 2/3),
    // even classes go to 105DA (type 0/1).
    return (cls&1u) ? (orientation>=2) : (orientation<=1);
}

inline void setWord(RawVec& vec, unsigned off, int value) noexcept {
    auto u=static_cast<std::uint16_t>(value);
    vec.bytes[off]=static_cast<std::uint8_t>(u);
    vec.bytes[off+1]=static_cast<std::uint8_t>(u>>8);
}

inline RawVec regularVec(int x, int y, unsigned orientation,
                         std::uint8_t wallId, const Tables& t) noexcept {
    RawVec r{};
    const auto cls=t.wallClass[wallId];
    r.bytes[0]=wallId;
    r.bytes[1]=static_cast<std::uint8_t>(wallId-t.firstWallId[cls]);
    r.bytes[5]=t.wallProperty[wallId];
    r.bytes[6]=cls;
    r.bytes[7]=static_cast<std::uint8_t>(orientation);
    // DOS2 105EA: type 0/1 horizontal; type 2/3 vertical.
    setWord(r,0x0C,(x+(orientation==2))*64);
    setWord(r,0x0E,(y+(orientation==1))*64);
    setWord(r,0x10,(x+(orientation==2)+(orientation<=1))*64);
    setWord(r,0x12,(y+(orientation==1)+(orientation>=2))*64);
    return r;
}
inline RawVec doorVec(int x,int y,unsigned orientation,
                      std::uint8_t wallId,const Tables& t) noexcept {
    RawVec r{};
    const auto cls=t.wallClass[wallId];
    r.bytes[0]=wallId;
    const int base=(cls==0x3D || cls==0x3E)
                    ? t.firstWallId[0x3E] : t.firstWallId[cls];
    const int ordinal=int(wallId)-base;
    // 1081C/1083C: generic signed SAR 1; class 3D/3E use class 3E base.
    r.bytes[1]=static_cast<std::uint8_t>(
        (cls==0x3D || cls==0x3E) ? ordinal :
        (ordinal>=0 ? ordinal/2 : -((-ordinal+1)/2)));
    r.bytes[5]=t.wallProperty[wallId];
    r.bytes[6]=cls;
    r.bytes[7]=static_cast<std::uint8_t>(orientation);
    // 106F2: a half-cell centered door segment.
    const bool vertical=orientation>=2;
    setWord(r,0x0C,x*64+(vertical?32:0));
    setWord(r,0x0E,y*64+(vertical?0:32));
    setWord(r,0x10,x*64+(vertical?32:64));
    setWord(r,0x12,y*64+(vertical?64:32));
    return r;
}
inline void extendVec(RawVec& r,unsigned orientation) noexcept {
    // 10854 extends +10 by 64 for orientation 0/1 and +12 for 2/3.
    const unsigned off=orientation<=1 ? 0x10 : 0x12;
    const unsigned v=std::uint16_t(r.bytes[off] | (unsigned(r.bytes[off+1])<<8));
    setWord(r,off,int((v+64u)&0xFFFFu));
}

// 0xFDEE builds four orientation-separated near-pointer arrays *after*
// construction; 0xFDA6 is the original primary-key comparator used by the
// external sort.  We do not invent the external quicksort's tie permutation.
constexpr unsigned kMaxOrientationPointers=333;
struct Groups {
    bool valid{true};
    std::array<std::vector<std::uint16_t>,4> pointers{};
};
inline Groups groupBeforeSort(const std::vector<RawVec>& records) {
    Groups out{};
    if(records.size()>vecpool::kMaxRecords) {out.valid=false;return out;}
    for(std::size_t i=0;i<records.size();++i) {
        const auto orientation=records[i].bytes[7];
        if(orientation>3 || out.pointers[orientation].size()>=kMaxOrientationPointers) {
            out.valid=false;return out; // fail closed before old overflow path
        }
        out.pointers[orientation].push_back(static_cast<std::uint16_t>(
            vecpool::kBase+i*vecpool::kStride));
    }
    return out;
}
inline int originalPrimaryCompare(const RawVec& lhs,const RawVec& rhs) noexcept {
    auto value=[](const RawVec& r,unsigned off)->std::int16_t {
        return vecpool::signed16(static_cast<std::uint16_t>(r.bytes[off]|
                       (std::uint16_t(r.bytes[off+1])<<8)));
    };
    // 0xFDA6: if lhs.X0==lhs.X1, compare signed X0, else signed Y0.
    // Never insert guessed secondary coordinates for equal-key cases.
    const bool lhsVertical=value(lhs,0x0C)==value(lhs,0x10);
    const auto a=lhsVertical?value(lhs,0x0C):value(lhs,0x0E);
    const auto b=lhsVertical?value(rhs,0x0C):value(rhs,0x0E);
    return a<b?-1:(a>b?1:0);
}

inline Result produce(const LevelMap& map,const Tables& t) {
    Result out{};
    std::vector<RawVec> built;
    built.reserve(700);
    for (unsigned orientation=0;orientation<4;++orientation) {
        bool previousIsRegular=false;
        std::uint8_t lastWall=0, lastObjectClass3=0, lastProperty10=0;
        unsigned groupCount=0;
        // 10892 scans all 64*64 cells in each orientation, but the inner
        // coordinate is X for 0/1 and Y for 2/3.  Boundary neighbours are
        // skipped at 10914..1096F before any MAP byte is read.
        for(int outer=0;outer<64;++outer) for(int inner=0;inner<64;++inner) {
            const int x=orientation<=1?inner:outer;
            const int y=orientation<=1?outer:inner;
            const int adjX=x+(orientation==2)-(orientation==3);
            const int adjY=y+(orientation==1)-(orientation==0);
            if(adjX<0 || adjY<0 || adjX>=64 || adjY>=64) continue;
            const MapCell cur=map.at(x,y), other=map.at(adjX,adjY);
            const auto wall=cur.wall, side=other.wall;
            const auto prop=t.wallProperty[wall], sideProp=t.wallProperty[side];
            const bool currentObject3=(t.objectClass[cur.object]==3);
            bool neighborObject3=(t.objectClass[other.object]==3);
            if(currentObject3 && wall==side) neighborObject3=false;
            const bool property10=(prop & 0x10u)!=0;
            const bool nearSpecial10=(property10 && wall==side) ? false :
                                     (sideProp & 0x10u)!=0;
            const bool changedProperty8=((prop^sideProp)&0x08u)!=0;
            if(prop&0x04u) {
                if((sideProp&0x04u) && !neighborObject3 && !nearSpecial10) {
                    previousIsRegular=false;
                } else {
                    if(previousIsRegular && lastWall==wall && !changedProperty8 &&
                       lastObjectClass3==currentObject3 &&
                       lastProperty10==property10) {
                        extendVec(built.back(),orientation);
                    } else {
                        if(prop&0x08u) {
                            out.status=Status::UnsupportedResourceRemap;
                            return out; // original 106BC..106EB lookup not modeled
                        }
                        if(!t.firstWallIdKnown[t.wallClass[wall]]) {
                            out.status=Status::MissingFirstClassId;
                            return out;
                        }
                        if(built.size()>=vecpool::kMaxRecords){
                            out.status=Status::ExceedsOriginalVecCapacity;
                            return out;
                        }
                        built.push_back(regularVec(x,y,orientation,wall,t));
                        ++groupCount;
                    }
                    previousIsRegular=true;
                }
            } else {
                const std::uint8_t cls=t.wallClass[wall];
                if(specialDoorOrientation(cls,orientation)) {
                    const auto key=(cls==0x3D || cls==0x3E)?0x3E:cls;
                    if(!t.firstWallIdKnown[key]) {
                        out.status=Status::MissingFirstClassId;
                        return out;
                    }
                    if(built.size()>=vecpool::kMaxRecords){
                        out.status=Status::ExceedsOriginalVecCapacity;
                        return out;
                    }
                    built.push_back(doorVec(x,y,orientation,wall,t));
                    ++groupCount;
                    // 10B70 jumps past 10B72: preserve prev-regular marker.
                } else {
                    previousIsRegular=false;
                }
            }
            lastWall=wall;
            lastObjectClass3=static_cast<std::uint8_t>(currentObject3);
            lastProperty10=static_cast<std::uint8_t>(property10);
        }
        out.countByOrientation[orientation]=groupCount;
    }
    out.vecs=std::move(built);
    return out;
}
} // namespace n3d::dos20::vecproducer
