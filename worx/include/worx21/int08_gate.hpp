#pragma once

#include "worx21/int63_leaf.hpp"

namespace worx21 {

// Contract for opaque subroutines at 15BF:4476, previous 08h vector,
// and private-stack audio ISR at 15BF:40E7. Their internals remain unmodeled.
class Timer08Hooks {
public:
    virtual ~Timer08Hooks() = default;
    virtual void music_tick_4476(CSState &state) = 0;
    virtual void chain_old_irq08(CSState &state) = 0;
    virtual void audio_engine_40e7(CSState &state) = 0;
};

// Machine-proven control-flow prefix of WORX INT08 15BF:4150..41B2.
// Precisely models state gate/EOI order, not IRQ frames, register saves,
// private-stack switching, old BIOS handler, 4476 parser or 40E7 mixing.
class Timer08Gate final {
public:
    Timer08Gate(CSState &state, PortIO &ports, Timer08Hooks &hooks) noexcept
        : state_(state), ports_(ports), hooks_(hooks) {}
    void irq08();
private:
    CSState &state_;
    PortIO &ports_;
    Timer08Hooks &hooks_;
};

} // namespace worx21
