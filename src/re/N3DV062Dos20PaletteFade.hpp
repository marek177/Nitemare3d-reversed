#pragma once
#include <array>
#include <cstdint>
namespace n3d::re::v062 {
constexpr std::uint8_t step(std::uint8_t c) noexcept { return c>=3?static_cast<std::uint8_t>(c-3):c; }
constexpr std::uint8_t run21(std::uint8_t c) noexcept { for(unsigned i=0;i<21;++i)c=step(c); return c; }
inline constexpr std::uint16_t kComponents=768;
inline constexpr std::uint8_t kPasses=21;
inline constexpr std::uint32_t kWrites=16128;
inline constexpr std::uint32_t kAdjacentChecks=15360;
inline constexpr std::array<std::uint16_t,3> kFinalCounts{{305,240,223}};
inline constexpr std::uint64_t kFinalFnv64=0x78F3DAEBC5DDA37Dull;
inline constexpr bool kCallerObserved=true;
inline constexpr bool kExactTimingClosed=false;
inline constexpr bool kFramebufferZeroDiffClosed=false;
static_assert(run21(0)==0 && run21(1)==1 && run21(2)==2 && run21(63)==0);
}
