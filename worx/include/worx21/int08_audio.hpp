#pragma once

#include "worx21/int63_leaf.hpp"

namespace worx21 {

// Subroutines called by 15BF:40E7: their internals require further RE.
class TimerAudioHooks {
public:
    virtual ~TimerAudioHooks() = default;
    virtual void pcm_mix_555d(CSState &state) = 0;
    virtual void midi_schedule_5df2(CSState &state) = 0;
};

// Original-machine-proven content of the private-stack audio service
// 15BF:40E7..414F, excluding CPU stack, STI/CLI/IRET concurrency. Do NOT
// confuse this with a completed PCM/MIDI or interrupt implementation.
class Timer08AudioService final {
public:
    Timer08AudioService(CSState &state, TimerAudioHooks &hooks) noexcept
        : state_(state), hooks_(hooks) {}
    void run();
private:
    CSState &state_;
    TimerAudioHooks &hooks_;
};

} // namespace worx21
