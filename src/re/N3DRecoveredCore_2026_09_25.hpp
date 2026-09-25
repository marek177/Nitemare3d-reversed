#pragma once
#include <array>
#include <cstdint>
#include <optional>
namespace n3d::re20260925 {
inline constexpr std::size_t MaxObjects=350, MaxGuards=100, MaxProjectiles=8;
inline constexpr std::size_t ObjectStride=28, GuardStride=26, ProjectileStride=42;
enum class Evidence:uint8_t{Confirmed,Inferred,Unknown};
enum class GuardState:uint8_t{Animate=0,Delay=1,Wake=2,Acquire=3,Attack=4,Plan=5,Move=6,WaitLos=7,WallMove=8,Interact=9,NoBranchA=0x0A,Disabled=0x0B,DirectionalC=0x0C,DirectionalD=0x0D,CannonIdle=0x0E,CannonCycle=0x0F,CannonAttack=0x10,RecoverMove=0x11,SequenceOffset=0x12,Strategy3=0x13,GlobalTimed=0x14,HitReaction=0x15};
enum class GuardStrategy:uint8_t{Generic=0,LowHpTargetSearch=1,AlternateMove=2,SpecialWall=3,HitReactionSuppressed=4};
class Rng{uint32_t s_;public:explicit Rng(uint32_t s=1):s_(s){} uint16_t next(); uint32_t state()const{return s_;}};
int16_t scoreForClass(uint8_t c);
struct DamageInput{int16_t projectedRow,viewportCenter;uint8_t objectClass,weapon,difficulty,episode;uint16_t rng;};
struct DamageResult{int seed,transformed,finalValue;uint8_t storedByte;};
DamageResult computeDamage(const DamageInput&);
std::optional<uint8_t> fireDamage(uint8_t objectId);
inline constexpr std::array<int8_t,8> MoveX{0,8,8,0,0,-8,-8,0};
inline constexpr std::array<int8_t,8> MoveY{-8,0,0,8,8,0,0,-8};
struct RuntimeAddresses{
 static constexpr uint16_t PlayerX=0x4BF6,PlayerY=0x4BF8,Difficulty=0x4C14,PlayerHP=0x4C1D;
 static constexpr uint16_t AmmoWeapon2=0x4C1F,AmmoWeapon0=0x4C20,AmmoWeapon1=0x4C44,WeaponSelector=0x4C23;
 static constexpr uint16_t CredentialMask=0x4C29,WeaponMask=0x4C2A,ProjectileBase=0x4C4A;
 static constexpr uint16_t EventFlags=0x51A4,Generation=0x53DC,ViewportCenter=0x53EE;
 static constexpr uint16_t ColumnOwners=0x53FE,VisibleSpanCount=0x5E7E,VisibleSpans=0x5E88;
};
struct EventFlags{uint8_t secretPanelMask,cannonEnabled,storyLatch,oneShotH,eventG,eventA9,eventAA,darkEvent;};
} // namespace n3d::re20260925
