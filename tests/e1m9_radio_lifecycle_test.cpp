#include "re/E1M9RadioLifecycle.hpp"
#include <cassert>
using namespace n3d::re::e1m9;
int main() {
    // The write is independent of OBJECT value, including zero/sentinel bytes.
    for (unsigned wall = 0; wall < 256; ++wall)
        for (unsigned object = 0; object < 256; ++object) {
            auto result = mode0MapWriteWin13To110(
                {static_cast<std::uint8_t>(wall), static_cast<std::uint8_t>(object)});
            assert(result.wallId == 0 && result.objectId == object);
        }
    static_assert(danceDescriptorWordOffset(0x09) == 0x04);
    static_assert(danceDescriptorWordOffset(0x0B) == 0x24);
    static_assert(danceDescriptorWordOffset(0x0C) == 0x14);
    static_assert(!danceDescriptorWordOffset(0x21));
    // Exhaust the state filter, rather than assuming saved byte implies restore.
    for (unsigned state = 0; state < 256; ++state) {
        RadioRestoreFields f{12, 9, 2, static_cast<std::uint8_t>(state), 77};
        const bool restored = restoreRadioFields(f);
        assert(restored == (state == 0x14));
        if (restored) {
            assert(f.objectGroup == 9 && f.strategy == 0 && f.state == 6 && f.timer == 1);
        } else {
            assert(f.objectGroup == 12 && f.savedGroupOrNextState == 9);
            assert(f.strategy == 2 && f.state == state && f.timer == 77);
        }
    }
    // Conditional witness only: supplied state 0/15 is NOT a simulated hit.
    for (auto state : {0, 0x15}) {
        RadioRestoreFields f{12, 0x14, 2, static_cast<std::uint8_t>(state), 1};
        assert(!restoreRadioFields(f));
        assert(f.objectGroup == 12); // no accidental nextstate-as-group restore
    }
}
