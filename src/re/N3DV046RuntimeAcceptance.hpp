#pragma once
#include <array>
#include <cstdint>
namespace n3d::re::v046 {
enum class FrameStage : std::uint8_t { BeforeProjectile, AfterProjectile, BeforeInput, AfterInput };
struct StageAnchor { FrameStage stage; std::uint32_t imageOffset; };
inline constexpr std::array<StageAnchor,4> kDos20SameSchedulerStages{{
 {FrameStage::BeforeProjectile,0xC24B},{FrameStage::AfterProjectile,0xC250},
 {FrameStage::BeforeInput,0xC26F},{FrameStage::AfterInput,0xC274}
}};
constexpr bool directProjectileBeforeInput() noexcept {
 return kDos20SameSchedulerStages[0].imageOffset < kDos20SameSchedulerStages[2].imageOffset;
}
struct GuardVector { std::int8_t vx{}; std::int8_t vy{}; };
constexpr GuardVector doubleBlockedBounce(GuardVector v,std::uint16_t rng15) noexcept {
 if (rng15 & 1u) v.vx=static_cast<std::int8_t>(-static_cast<std::int16_t>(v.vx));
 else v.vy=static_cast<std::int8_t>(-static_cast<std::int16_t>(v.vy));
 return v;
}
constexpr std::uint8_t state06AfterTimerDecrement(std::uint16_t before) noexcept {
 return static_cast<std::uint16_t>(before-1u)==0 ? 0x03 : 0x06;
}
struct GuardState05RuntimeWitness {
 std::uint8_t guardIndex{}, objectClass{}; std::uint16_t timerBefore{},timerAfter{};
 GuardVector vectorAfter{}; std::uint16_t xBefore{},xAfter{}; std::uint32_t rngBefore{},rngAfter{};
};
inline constexpr GuardState05RuntimeWitness kFrankensteinState05{27,0x09,0xFFFF,8,{-8,0},2784,2776,0xE7847115u,0xCAE1DF84u};
inline constexpr GuardState05RuntimeWitness kMummyState05{29,0x0A,0xFFFF,8,{8,0},2720,2720,0xCAE1DF84u,0x3D6C1037u};
struct GuardAttackRuntimeWitness {
 std::uint8_t guardIndex{},objectClass{},hpBefore{},hpAfter{},damage{}; std::uint32_t rngBefore{},rngAfter{};
};
inline constexpr GuardAttackRuntimeWitness kFrankensteinAttack{27,0x09,100,86,14,0xC823F683u,0x18BE873Au};
inline constexpr GuardAttackRuntimeWitness kMummyAttack{29,0x0A,86,82,4,0x18BE873Au,0xE7847115u};
struct WeaponRuntimeSnapshot { std::uint8_t active{},mode{},phase{},frame{},plasma{},wand{},silver{}; };
inline constexpr std::array<WeaponRuntimeSnapshot,6> kDos12Dos20All4Witness{{
 {0,2,0,9,60,32,32},{1,2,0,9,60,32,32},{2,1,0,9,60,32,32},
 {3,2,0,9,60,32,32},{3,2,0,9,37,32,32},{0,2,0,9,37,32,32}
}};
enum class ShutdownRuntimeEvent : std::uint8_t { MusicStopAh0D, DigitalStopAh07, DigitalIrqRestoreAh04, RestoreIrq7Vector, NormalDosExit0 };
inline constexpr std::array<ShutdownRuntimeEvent,5> kDigitalShutdownWitness{{
 ShutdownRuntimeEvent::MusicStopAh0D,ShutdownRuntimeEvent::DigitalStopAh07,
 ShutdownRuntimeEvent::DigitalIrqRestoreAh04,ShutdownRuntimeEvent::RestoreIrq7Vector,
 ShutdownRuntimeEvent::NormalDosExit0
}};
inline constexpr bool kNoXmsManagerIsNonFatalInObservedBuild=true;
inline constexpr bool kActiveDspDmaStopObserved=false;
struct PaletteRuntimeWitness { std::uint32_t seedBefore{},seedAfter{}; std::uint16_t rng15{},timer{}; std::uint8_t firstDacIndex{},secondDacIndex{}; };
inline constexpr PaletteRuntimeWitness kPaletteRngWitness{1u,0x0029E2C0u,41,201,0xEB,0xE3};
} // namespace n3d::re::v046
