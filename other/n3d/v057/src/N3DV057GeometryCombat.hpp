#pragma once
// Clean-room reference contract for original DOS 2.0/Win16 local branches.
// Not a standalone game and NOT proof of transitive FAR/runtime behavior.
#include <cstdint>
#include <vector>
#include <utility>
#include <optional>

namespace n3d_v057 {
constexpr std::uint16_t u16(std::int64_t v) noexcept { return static_cast<std::uint16_t>(v); }
constexpr std::int32_t s16(std::uint16_t v) noexcept {
    return (v & 32768u) ? std::int32_t(v) - 65536 : std::int32_t(v);
}
constexpr std::uint16_t sar16(std::uint16_t v,unsigned n) noexcept {
    const std::int32_t q=s16(v), div=std::int32_t(1u<<n);
    return u16(q>=0 ? q/div : -((-q+div-1)/div));
}
struct Tile { std::uint8_t wall=0, object=0; };
enum class GeometryExit { Reached, LimitNonpositive, StepLimit, WallBlocked, SpecialWallBlocked, ObjectBlocked };
struct GeometryResult {
    GeometryExit exit=GeometryExit::StepLimit;
    std::vector<std::pair<std::uint16_t,std::uint16_t>> traversed;
    std::vector<std::pair<std::uint16_t,std::uint16_t>> examined;
    unsigned specialWallCalls=0;
    std::int32_t finalError=0;
    bool accepted() const noexcept { return exit==GeometryExit::Reached; }
};

// caller-supplied tile flags and nested FAR callback outcome. The callbacks
// are deliberately external, because the two nested original FAR routines
// are not part of this bounded static closure.
template<class TileReader,class SpecialWall>
GeometryResult geometryLine(std::uint16_t x,std::uint16_t y,std::int16_t dx,
                            std::int16_t dy,std::int16_t maxSteps,bool checkObject,
                            TileReader tileAt,SpecialWall specialWall) {
    GeometryResult out{};
    const std::int32_t sx=dx>0?1:-1, sy=dy>0?1:-1;
    const auto endX=u16(std::int32_t(x)+dx),endY=u16(std::int32_t(y)+dy);
    const auto abx=u16(dx<0?-std::int32_t(dx):dx);
    const auto aby=u16(dy<0?-std::int32_t(dy):dy);
    const bool xMajor=s16(aby)<s16(abx);
    const std::uint16_t major=xMajor?abx:aby, minor=xMajor?aby:abx;
    auto err=u16(std::int32_t(2)*minor-major);
    const auto noSecond=u16(std::int32_t(2)*minor);
    const auto twoSteps=u16(std::int32_t(2)*(std::int32_t(minor)-major));
    if(maxSteps<=0){out.exit=GeometryExit::LimitNonpositive;out.finalError=s16(err);return out;}
    for(std::int32_t count=0;count<maxSteps;++count){
        if(xMajor)x=u16(std::int32_t(x)+sx);
        else y=u16(std::int32_t(y)+sy);
        if(s16(err)<0)err=u16(std::int32_t(err)+noSecond);
        else {
            err=u16(std::int32_t(err)+twoSteps);
            if(xMajor)y=u16(std::int32_t(y)+sy);
            else x=u16(std::int32_t(x)+sx);
        }
        out.traversed.emplace_back(x,y);
        out.finalError=s16(err);
        if(x==endX && y==endY){out.exit=GeometryExit::Reached;return out;}
        const auto tile=tileAt(x,y);
        out.examined.emplace_back(x,y);
        if(tile.wall&2u){
            if(tile.wall&4u){out.exit=GeometryExit::WallBlocked;return out;}
            if(tile.wall&8u){
                ++out.specialWallCalls;
                if(!specialWall(x,y)){out.exit=GeometryExit::SpecialWallBlocked;return out;}
            }
        }
        if(checkObject && (tile.object&2u) && !(tile.object&32u)){
            out.exit=GeometryExit::ObjectBlocked;return out;
        }
    }
    out.exit=GeometryExit::StepLimit;
    return out;
}

// Exact DOS local state gate over the first record with matching map far ptr.
// std::nullopt means original lookup misses and enters its diagnostic/exit path.
struct MovingWallRecord {
    std::uint16_t cellOffset=0,cellSegment=0,stateAt08=0;
};
inline std::optional<bool> dosMovingWallPass(const std::vector<MovingWallRecord>& records,
                                            std::uint16_t cellOffset,std::uint16_t cellSegment){
    for(const auto& entry:records){
        if(entry.cellOffset==cellOffset && entry.cellSegment==cellSegment)
            return entry.stateAt08==0 || entry.stateAt08==4;
    }
    return std::nullopt;
}

enum class DamagePath {
    Default, Shr1, Shr2, Shr3, Selector1Shr1Else3,Selector2Shr1Else3,
    Selector1Shr8Else1, Selector1Shr8Else2, Selector1Shr8Selector2Shr4Else3,
    Zero, SpecialCallbackZero, Global3ElseZero, Selector1Shr1ElseZero,
    Selector1ZeroElse3,Selector1ZeroElse2
};
struct ScalarDamage {
    std::uint16_t ax=0;
    std::uint8_t appliedByte=0;
    std::int32_t afterRandom=0,afterClass=0,afterDifficulty=0;
    DamagePath branch=DamagePath::Default;
    bool eventCallbackRequired=false;
    unsigned directRngDraws=1;
};

constexpr DamagePath classPath(std::uint8_t cls) noexcept {
    switch(cls){
    case 0x0c:case 0x1d:return DamagePath::Shr3;
    case 0x0d:return DamagePath::Selector1Shr1Else3;
    case 0x0e:case 0x11:case 0x14:return DamagePath::Selector2Shr1Else3;
    case 0x0f:case 0x10:return DamagePath::Selector1Shr8Else1;
    case 0x12:case 0x13:return DamagePath::Shr2;
    case 0x15:return DamagePath::SpecialCallbackZero;
    case 0x16:return DamagePath::Global3ElseZero;
    case 0x17:return DamagePath::Selector1Shr8Else2;
    case 0x18:return DamagePath::Selector1Shr8Selector2Shr4Else3;
    case 0x19:return DamagePath::Zero;
    case 0x1a:return DamagePath::Selector1Shr1ElseZero;
    case 0x1b:case 0x1c:return DamagePath::Shr1;
    case 0x1e:return DamagePath::Selector1ZeroElse3;
    case 0x1f:return DamagePath::Selector1ZeroElse2;
    default:return DamagePath::Default;
    }
}

// RNG value is caller-supplied (0..0x7fff). The actual original function
// makes exactly one direct RNG call before inspecting cls.
inline ScalarDamage scalarDamage(std::uint8_t cls,std::uint8_t selector418f,
                    std::uint16_t difficulty4180,std::uint16_t objectDepth18,
                    std::uint16_t reference4552,std::uint16_t rng15,
                    std::uint16_t special626a=0){
    ScalarDamage out{};
    out.branch=classPath(cls);
    auto v=u16(std::int32_t(objectDepth18)-reference4552);
    v=u16(std::int32_t(v)*8);
    v=u16(std::int32_t(v)+(rng15&0x7fffu)%25);
    out.afterRandom=s16(v);
    auto shift=[&](unsigned n){v=sar16(v,n);};
    switch(out.branch){
    case DamagePath::Default:break;
    case DamagePath::Shr1:shift(1);break;
    case DamagePath::Shr2:shift(2);break;
    case DamagePath::Shr3:shift(3);break;
    case DamagePath::Selector1Shr1Else3:shift(selector418f==1?1:3);break;
    case DamagePath::Selector2Shr1Else3:shift(selector418f==2?1:3);break;
    case DamagePath::Selector1Shr8Else1:shift(selector418f==1?8:1);break;
    case DamagePath::Selector1Shr8Else2:shift(selector418f==1?8:2);break;
    case DamagePath::Selector1Shr8Selector2Shr4Else3:shift(selector418f==1?8:selector418f==2?4:3);break;
    case DamagePath::Zero:v=0;break;
    case DamagePath::SpecialCallbackZero:out.eventCallbackRequired=true;v=0;break;
    case DamagePath::Global3ElseZero:v=(special626a==3)?3:0;break;
    case DamagePath::Selector1Shr1ElseZero:if(selector418f==1)shift(1);else v=0;break;
    case DamagePath::Selector1ZeroElse3:if(selector418f==1)v=0;else shift(3);break;
    case DamagePath::Selector1ZeroElse2:if(selector418f==1)v=0;else shift(2);break;
    }
    out.afterClass=s16(v);
    if(difficulty4180==2)shift(1);
    else if(difficulty4180==0)v=u16(std::int32_t(v)*2);
    out.afterDifficulty=s16(v);
    out.ax=s16(v)>255?std::uint16_t(255):v;
    out.appliedByte=static_cast<std::uint8_t>(out.ax);
    return out;
}

enum class HitRoute { Lethal, NoDamage, Strategy2, Strategy4, ReturnState,
                      State21, SpecialAnimation };
struct GuardHitLocal { std::uint8_t hpAfter=0; HitRoute route=HitRoute::NoDamage;
                       bool writePainTimer=false,preState7Callback=false; };
constexpr HitRoute guardStateRoute(std::uint8_t state) noexcept {
    switch(state){
        case 3:case 4:case 11:return HitRoute::ReturnState;
        case 7:case 8:case 21:return HitRoute::SpecialAnimation;
        default:return HitRoute::State21;
    }
}
constexpr GuardHitLocal guardHitLocal(std::uint8_t hp,std::uint8_t damage,
                                     std::uint8_t strategy,std::uint8_t state) noexcept {
    if(hp<=damage)return {0,HitRoute::Lethal,false,false};
    if(!damage)return {hp,HitRoute::NoDamage,false,false};
    const auto next=strategy==2?HitRoute::Strategy2:strategy==4?HitRoute::Strategy4:guardStateRoute(state);
    return {std::uint8_t(hp-damage),next,true,state==7};
}
}
