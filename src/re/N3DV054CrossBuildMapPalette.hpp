#pragma once
#include <array>
#include <cstdint>

namespace n3d::re::v054 {

inline constexpr std::uint16_t kLevelCount = 31;
inline constexpr std::uint16_t kMarkerKinds = 4;
inline constexpr std::uint16_t kCrossBuildMarkerCount = 124;
inline constexpr std::uint16_t kSameLowByteAsSpawnCount = 112;
inline constexpr std::uint16_t kLevelsWithMaxDistanceAtMost2 = 29;
inline constexpr std::uint16_t kMaxObservedSpawnChebyshevDistance = 4;

struct E1M1MarkerDiff {
    std::uint8_t id{};
    std::uint16_t mapOffset{};
    std::uint32_t differingPixels{};
};

inline constexpr std::array<E1M1MarkerDiff,4> kE1M1SingleMarkerDiffs{{
    {0x25,0x1E2D,5576},
    {0x26,0x1DAD,5548},
    {0x27,0x1D2D,8000},
    {0x28,0x1C2D,6592},
}};

constexpr std::uint16_t win110PaletteCopyCount(bool reserveSystemEnds) noexcept {
    return reserveSystemEnds ? 236 : 256;
}
inline constexpr std::uint8_t kWin110ReservedAtEachEnd = 10;

struct DosCodeBand {
    std::uint32_t dos19Bytes{};
    std::uint32_t dos20Bytes{};
    std::uint32_t alignedEqualBytes{};
};
inline constexpr DosCodeBand kDos19To20MainBand{46832,46880,44108};

inline constexpr bool kMarkerResourceIdentityFullyClosed = false;
inline constexpr bool kCrossBuildPixelParityClosed = false;

} // namespace n3d::re::v054
