#include "re/n3d_v018_facts.h"

#include <cassert>
#include <cstdint>

int main() {
    static_assert(N3D_V018_PROJECTILE_SLOT_COUNT == 8);
    static_assert(N3D_V018_PROJECTILE_SLOT_STRIDE == 0x2A);
    static_assert(N3D_V018_GUARD_STRIDE == 0x1A);
    static_assert(N3D_V018_SECRET_PANEL_RECORD_SIZE == 0x0E);

    assert(N3D_V018_DOS20_ROUTINES.player_step_collision == 0x6378);
    assert(N3D_V018_DOS20_ROUTINES.projectile_scheduler == 0x8230);
    assert(N3D_V018_DOS20_ROUTINES.secret_panel_update == 0x0AEA);
    assert(N3D_V018_WEAPON_CADENCE_THRESHOLDS[0] == 2);
    assert(N3D_V018_WEAPON_CADENCE_THRESHOLDS[2] == 3);

    std::uint32_t state = 1;
    const std::uint16_t first = n3d_v018_rng_step(&state);
    assert(state == 2745024u);
    assert(first == 41u);

    assert(N3D_V018_DOS20_RNG_CALLSITES[0] == 0x2478);
    assert(N3D_V018_DOS20_RNG_CALLSITES[19] == 0xB276);
    return 0;
}
