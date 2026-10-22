# Nitemare 3D DOS v2.0 — E1M1 weapon pickup and Ctrl FIRE behavior (22.10.2026)

**Provenance:** earlier original-game Linux DOSBox-X runtime report named **N3D_Runtime_NEXT_Turn_Pickup_Fire_20261022.zip**, with **30 reported consistency checks**. This document is an evidence transfer from that prior experimental session, **not** a fresh execution or revalidation of its original CSV in this commit. Original reference DOS 2.0 EXE SHA-256 (also independently present in the user's original archive): **552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301**. Do not assume a fixed host memory base or guest DS across emulator restarts.

## Observed controlled route

| Condition / event | Observed response | Scope |
|---|---|---|
| Right/Left rotation | Direction **0 → 55 → 5**; player X/Y stayed unchanged in those phases | One E1M1 route, not a universal degrees-per-tick constant |
| Stable idle after releasing movement | 50 consecutive read-only samples without further position change | Asynchronous RAM sampling, not 50 game ticks |
| Weapon/ammo pickup | Observed ammo **0 → 50** and visible pistol/weapon selection | Initial inventory, specific pickup route and its selection predicates require future opcode correlation |
| Ctrl tap | One recorded ammo decrement/shot | One weapon and starting state |
| Ctrl held for approximately 1, 2 or 8 host seconds | **One** recorded ammo decrement in each tested held-press phase | Host durations are NOT original simulation ticks |
| Repeated Ctrl keydown without release | Still one decrement for the continuous press | Does not prove the internal repeat-filter implementation |
| Ctrl release, then new press | A new decrement per release-enabled press | Required key-up/key-down transition in tested route |
| After all keys released | Ammo and other selected player state remained stable | Read-only memory observations |

The tested behavior is **consistent with a press/rearm gate** in the actual weapon path. It does **not** identify the exact byte-sized latch, firearm automaton, opcode branch, sound event, RNG call or scheduler tick, and does not prove identical behavior for Multi Plasma or other weapons.

## Why this matters

The earlier V085/V086 input tests already established **Ctrl=0x0080**, Alt=0x0100, USE=0x0200 in the guest input mask, but did not prove a FIRE event, hit or ammo consumption. The pickup/fire session adds **a bounded, causal gameplay observation** that holding Ctrl need not cause repeated shots. It must NOT be implemented as a global rule across all weapons until weapon-dependent opcode handling has been recovered.

Read alongside [original action-mask truth table](V085_V086_DOS20_LIVE_E1M1_ACTION_MASKS_SK.md), [cross-build class36 weapon pickups](V053_REMAX_HUD_WEAPON_CLASS36.md), [combined movement test](DOS20_E1M1_COMBINED_KEY_RUNTIME_2026-10-22_SK.md) and [V088 diagnostic diff contract](GAMEPLAY_DIFF_V088_2026-10-22.md).

## Precise next experiment (P0)

1. Lock active EXE, IMG, MAP, palette and difficulty with SHA, and locate the guest DS on **each** run; capture tick and input mask at the original dispatcher.
2. Record first Ctrl bit transition, weapon active/owned state, ammunition **before/after the write**, fire clock, sound ID, projectile/hitscan routing and RNG caller in ordered CPU trace.
3. Record Ctrl held/released transitions and whether the same path fires again without a rearm.
4. Run **the same tick-indexed state and input** through native candidate code. V089 SDL preview input bits, tile coordinates and frame delta are **not** the DOS DS:3F50 schema or its integer coordinate units.
5. Compare the first divergent state/event using V088 only once a legitimate original/candidate schema exists; do not invent absent fields.

**Status:** observed original behavior in one scoped E1M1 route; exact rearm cause, projectiles/damage, timing and original↔remake parity **OPEN**. Private EXE, trace and user-generated runtime ZIP are deliberately **not** committed.
