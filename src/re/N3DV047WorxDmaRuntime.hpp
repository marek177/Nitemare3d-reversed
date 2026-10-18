#pragma once
#include <array>
#include <cstdint>

namespace n3d::re::v047 {

struct DmaStartWitness {
    bool activeFlagBeforeCompletion{};
    std::uint16_t dspPort{};
    std::uint8_t dmaMode{};
    std::uint16_t dmaOffset{};
    std::uint8_t dmaPage{};
    std::uint16_t dmaCount{};
    std::uint8_t dmaUnmaskValue{};
};

inline constexpr DmaStartWitness kNaturalDmaStart{
    true, 0x022C, 0x59, 0xDB6E, 0x01, 0x0FFF, 0x01
};

struct DmaAutoStopWitness {
    bool activeBefore{};
    bool activeAfter{};
    std::uint8_t dspCommand{};
    std::uint8_t dmaMaskValue{};
    bool laterExplicitStopEnteredAfterClear{};
};

inline constexpr DmaAutoStopWitness kNaturalAutoStop{
    true, false, 0xD0, 0x05, true
};

constexpr bool activePlaybackStarted() noexcept {
    return kNaturalDmaStart.activeFlagBeforeCompletion &&
           kNaturalDmaStart.dmaUnmaskValue == 0x01;
}

constexpr bool automaticStopClearsAndMasks() noexcept {
    return kNaturalAutoStop.activeBefore &&
           !kNaturalAutoStop.activeAfter &&
           kNaturalAutoStop.dspCommand == 0xD0 &&
           kNaturalAutoStop.dmaMaskValue == 0x05;
}

inline constexpr bool kActiveShutdownStopObserved = false;
inline constexpr bool kAudibleWaveformParityObserved = false;

} // namespace n3d::re::v047
