#pragma once
#include <array>
#include <cstdint>
namespace n3d::re::v042 {
enum class DamageGateOrder:std::uint8_t{ProtectionBeforeCalculation,CalculationBeforeProtection};
enum class BuildFamily:std::uint8_t{Dos10To19,Dos20,Win16};
constexpr DamageGateOrder incomingDamageGateOrder(BuildFamily b) noexcept {
  return b==BuildFamily::Dos10To19?DamageGateOrder::ProtectionBeforeCalculation:DamageGateOrder::CalculationBeforeProtection;
}
constexpr bool hasDamageFeedbackTimer(BuildFamily b) noexcept { return b!=BuildFamily::Dos10To19; }
constexpr std::uint8_t rngMaskForIncomingClass(std::uint8_t c) noexcept {
  if(c==0x08)return 0x07; if(c==0x09||c==0x0A)return 0x0F; if(c>=0x11&&c<=0x14)return 0x1F; return 0;
}
struct FeedbackStep{std::int16_t timerAfter{};std::uint8_t selector{};bool active{};};
constexpr FeedbackStep feedbackStep(std::int16_t before) noexcept {
  if(before<0)return{before,0,false}; const auto after=static_cast<std::int16_t>(before-1); return{after,static_cast<std::uint8_t>(after>=0?4:3),true};
}
inline constexpr std::uint16_t kSecretDiskBytes=32;
struct SecretSaveContract{std::uint16_t activeCount{},locallyWrittenBytes{},diskBytes{},undefinedTailBytes{};};
constexpr SecretSaveContract secretSaveContract(std::uint16_t count) noexcept {
  const auto n=static_cast<std::uint16_t>(count>32?32:count); return{n,n,32,static_cast<std::uint16_t>(32-n)};
}
constexpr std::uint16_t secretLoadStateWord(std::uint8_t b) noexcept { return b; }
constexpr bool saveLoadCallerTreatsIoAsSuccess(std::int16_t ax) noexcept { return ax>=0; }
struct DoorLoadLayout{std::uint16_t records{},recordBytes{},runtimePrefixPreserved{},saveBytesAuthoritativeAfterLoad{};};
constexpr DoorLoadLayout doorLoadLayout(BuildFamily b) noexcept { return b==BuildFamily::Win16?DoorLoadLayout{64,22,12,10}:DoorLoadLayout{64,18,8,10}; }
struct WinMessageAck{std::int16_t countAfter{};bool forcedPresent{},displayAnother{},endMessageMode{};std::int16_t nextIndex{};};
constexpr WinMessageAck winMode4Ack(std::int16_t before) noexcept {
  const auto after=static_cast<std::int16_t>(before-1); if(after>0)return{after,true,true,false,after}; return{after,false,false,true,-1};
}
struct PoolLayout{std::uint16_t capacity{},stride{};};
inline constexpr PoolLayout kDosDynamicWall{64,18},kDosClass3Geometry{32,14},kWinDynamicWall{64,22},kWinClass3Geometry{32,22};
inline constexpr std::uint16_t kReclassifiedWriterSites=62;
inline constexpr std::uint16_t kDirectObjectPointerRecalcCallEdges=60;
inline constexpr std::uint16_t kDirectObjectPointerMoveCallEdges=12;
inline constexpr std::uint16_t kDirectObjectPointerCallEdgesTotal=72;
struct ImportThunk{std::uint16_t ordinal{};};
inline constexpr std::array<ImportThunk,5> kWin16TimingImportOrdinals{{{604},{605},{606},{607},{13}}};
}
