#include "re/n3d_v018_facts.h"

const n3d_v018_dos20_routines N3D_V018_DOS20_ROUTINES = {
    0x6914,
    0x6488,
    0x6378,
    0x688C,
    0x6A70,

    0x89A2,
    0x8F12,
    0x7EDE,
    0x8142,
    0x8230,

    0x59F0,
    0x5F26,
    0x0AEA,

    0xC150,
    0xC1A8,
    0xC0D8
};

const uint8_t N3D_V018_WEAPON_CADENCE_THRESHOLDS[4] = {2, 1, 3, 1};

const uint16_t N3D_V018_DOS20_RNG_CALLSITES[20] = {
    0x2478, 0x525E, 0x5582, 0x5666, 0x56A6,
    0x573F, 0x58A7, 0x85AD, 0x887C, 0x9A68,
    0x9A77, 0x9C98, 0x9CC2, 0x9D6E, 0x9F0C,
    0x9F36, 0x9FE3, 0xA047, 0xA12B, 0xB276
};

uint32_t n3d_v018_rng_next_state(uint32_t state) {
    return state * UINT32_C(214013) + UINT32_C(2531011);
}

uint16_t n3d_v018_rng_result(uint32_t next_state) {
    return (uint16_t)((next_state >> 16) & UINT32_C(0x7FFF));
}

uint16_t n3d_v018_rng_step(uint32_t *state) {
    if (state == NULL) {
        return 0;
    }

    *state = n3d_v018_rng_next_state(*state);
    return n3d_v018_rng_result(*state);
}
