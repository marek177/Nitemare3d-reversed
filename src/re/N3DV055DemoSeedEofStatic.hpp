#pragma once
#include <cstdint>

namespace n3d::re::v055 {

struct DemoRecord {
    std::uint16_t key{};
    std::uint16_t input{};
    std::uint32_t counter{};
};

inline constexpr std::uint16_t kDemo1RecordCount = 275;
inline constexpr DemoRecord kDemo1First{0x48E0,0x0002,8};
inline constexpr DemoRecord kDemo1Last{0x74E0,0x0090,1074};
inline constexpr std::uint16_t kEqualAdjacentCounterPairs = 4;

inline constexpr std::uint32_t kSeedHelperCallImageOffset = 0xF9AC;
inline constexpr std::uint32_t kPostSeedBoundaryImageOffset = 0xF9B1;
inline constexpr std::uint32_t kDemoModeDispatcherImageOffset = 0x6D04;
inline constexpr std::uint32_t kFirstRecordReadImageOffset = 0x6DC9;
inline constexpr std::uint32_t kRecordApplyImageOffset = 0x6DE4;
inline constexpr std::uint32_t kReadReturnSiteImageOffset = 0x6E07;

inline constexpr bool kSeedHelperIsRandomDrawHelper = false;
inline constexpr bool kCallerChecksReadCountAt6E07 = false;
inline constexpr bool kEofBehaviorClosed = false;
inline constexpr bool kSeedToFirstDrawContinuousTraceClosed = false;

} // namespace n3d::re::v055
