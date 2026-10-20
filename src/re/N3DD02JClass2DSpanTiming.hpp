#pragma once
#include <cstdint>

namespace n3d::re::d02j {
// Scoped byte-accurate DOS2 v2.0 class 0x2D SPAN gate; not whole renderer.
struct Result {
    bool dispatched=false; // SPAN interval != 0, class2D
    bool due=false;
    bool wallClearCall=false;
    std::uint8_t frame=0;
    std::uint32_t deadline=0;
};
constexpr Result update(std::uint8_t cls, std::uint8_t frame,
                        std::int16_t N, std::uint16_t interval,
                        std::uint32_t oldDeadline, std::uint32_t clock) noexcept {
    if (cls != 0x2d || interval==0) return {false,false,false,frame,oldDeadline};
    // 2500: 16-bit signed JG, then low-byte N-1 clamp (if frame>=N).
    if (N<=static_cast<std::int16_t>(frame))
        frame=static_cast<std::uint8_t>(static_cast<std::uint16_t>(N-1));
    // 241E: 32-bit unsigned JA -> ignore if deadline strictly greater.
    if (oldDeadline>clock) return {true,false,false,frame,oldDeadline};
    // 2433 INC BYTE wraps at 0xff, 24CA..24D4 signed threshold.
    frame=static_cast<std::uint8_t>(frame+1u);
    const bool clear=static_cast<std::int16_t>(frame)>=N;
    // 24E6: low16 addition + ADC high16, identical to wrapping uint32 add.
    return {true,true,clear,frame,clock+interval};
}
}
