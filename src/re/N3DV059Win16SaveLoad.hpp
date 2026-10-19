#pragma once
#include <cstdint>

namespace n3d::re::v059 {

struct Win16SaveLoadWitness {
    std::uint32_t saveSizeBytes;
    std::uint32_t changedBytesAfterMovement;
    std::uint32_t exactPixelBasisPoints;
    std::uint32_t restoredVsSavedMeanMilli;
    std::uint32_t restoredVsStartMeanMilli;
    bool e1m1Reached;
    bool saveWritten;
    bool loadRestoredMovedView;
};

inline constexpr Win16SaveLoadWitness kWin110E1M1SaveLoad{
    55015, 477, 9837, 940, 55610, true, true, true
};

inline constexpr bool kExactPlayerFieldOffsetsClosed = false;
inline constexpr bool kFirstPostLoadCpuFrameClosed = false;
inline constexpr bool kWin16RngRestoreClosed = false;
inline constexpr bool kAudioRestoreParityClosed = false;

} // namespace n3d::re::v059
