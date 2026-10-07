#ifndef N3D_V018_FACTS_H
#define N3D_V018_FACTS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum {
    N3D_V018_DOS20_PLAYER_X = 0x4162,
    N3D_V018_DOS20_PLAYER_Y = 0x4164,
    N3D_V018_DOS20_PLAYER_HP = 0x4189,
    N3D_V018_DOS20_CURRENT_WEAPON = 0x418F,

    N3D_V018_PROJECTILE_POOL_BASE = 0x41B6,
    N3D_V018_PROJECTILE_SLOT_COUNT = 8,
    N3D_V018_PROJECTILE_SLOT_STRIDE = 0x2A,

    N3D_V018_GUARD_POOL_BASE = 0x264E,
    N3D_V018_GUARD_STRIDE = 0x1A,

    N3D_V018_SECRET_PANEL_POOL_BASE = 0x34F6,
    N3D_V018_SECRET_PANEL_RECORD_SIZE = 0x0E,

    N3D_V018_SPAN_COUNT = 0x4D64,
    N3D_V018_SPAN_POOL = 0x4D6E,
    N3D_V018_SPAN_STRIDE = 0x12,
    N3D_V018_OWNER_TABLE = 0x4564,
    N3D_V018_VEC_COUNT = 0x626E,
    N3D_V018_VEC_POOL = 0x62AC
};

enum {
    N3D_V018_COLLISION_PRIMARY_HARD_BLOCK = 0x04,
    N3D_V018_COLLISION_PRIMARY_DYNAMIC = 0x08,
    N3D_V018_COLLISION_PRIMARY_TRIGGER = 0x40,
    N3D_V018_COLLISION_SECONDARY_CALLBACK = 0x04,
    N3D_V018_COLLISION_SECONDARY_BLOCK = 0x02
};

typedef struct n3d_v018_dos20_routines {
    uint16_t player_move_entry;
    uint16_t player_step_move;
    uint16_t player_step_collision;
    uint16_t player_commit;
    uint16_t player_damage;

    uint16_t action_dispatch;
    uint16_t fire_gate;
    uint16_t projectile_alloc;
    uint16_t projectile_move;
    uint16_t projectile_scheduler;

    uint16_t guard_dispatch;
    uint16_t guard_loop;
    uint16_t secret_panel_update;

    uint16_t fast_tick;
    uint16_t outer_scheduler;
    uint16_t main_update;
} n3d_v018_dos20_routines;

extern const n3d_v018_dos20_routines N3D_V018_DOS20_ROUTINES;
extern const uint8_t N3D_V018_WEAPON_CADENCE_THRESHOLDS[4];
extern const uint16_t N3D_V018_DOS20_RNG_CALLSITES[20];

uint32_t n3d_v018_rng_next_state(uint32_t state);
uint16_t n3d_v018_rng_result(uint32_t next_state);
uint16_t n3d_v018_rng_step(uint32_t *state);

#ifdef __cplusplus
}
#endif

#endif
