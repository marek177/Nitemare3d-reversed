# GUARD AI reverse engineering

Date: 2026-09-17
Evidence: original NITE3W.EXE V1.10 Win16 binary (230400 bytes), reconstructed USER.SAV writer/layout, direct 16-bit disassembly and embedded developer/debug strings.

## Fixed GUARD / OBJECT anchors

- GUARD stride: **0x1A = 26 bytes**, capacity **100**.
- USER.SAV GUARD pool: **0xB43B..0xBE62**, 0x0A28 bytes.
- `GUARD+08` is an OBJECT slot; `slot * 0x1C` addresses a 28-byte OBJECT record.
- `OBJECT+10/+12` are **world X/Y**; world-to-tile conversion uses arithmetic shift right by 6.
- `OBJECT+0C:+0E` is the object's map-cell far pointer, not X/Y.

Evidence: **VERIFIED_EXE + VERIFIED_SAVE_LAYOUT**.

## Embedded debug string unlocks GUARD semantics

NITE3W contains the developer diagnostic:

```text
class %d, strength %d, strategy %d
state %d, nextstate %d, timer %d
octant %d, resoct %d
```

The call site pushes, in reverse C argument order:

```text
GUARD+12
GUARD+11
GUARD+06
GUARD+0C
GUARD+0B
GUARD+0A
GUARD+10
OBJECT+06
format
```

Therefore the labels are direct executable evidence, not inferred names:

| Field | Meaning | Status |
|---|---|---|
| `OBJECT+06` | class | VERIFIED_EXE |
| `GUARD+10` | **strength / HP** | **VERIFIED_EXE** |
| `GUARD+0A` | **strategy** | **VERIFIED_EXE** |
| `GUARD+0B` | state | VERIFIED_EXE |
| `GUARD+0C` | nextstate | VERIFIED_EXE |
| `GUARD+06` | timer | **VERIFIED_EXE** |
| `GUARD+11` | **octant** | **VERIFIED_EXE** |
| `GUARD+12` | **resoct / result octant** | **VERIFIED_EXE** |

This replaces earlier conservative names for +0A/+10/+11/+12.

## Damage receiver recovered

The guard-hit routine obtains a damage amount from a helper and compares it against `GUARD+10 strength`.

Equivalent control flow:

```text
damage = compute_damage(...)
if (strength <= damage) {
    strength = 0;
    death_handler(...);
    ...
} else if (damage > 0) {
    if (state == 7)
        special_state7_hit_handler(...);
    strength -= damage;
    resoct = 8;
    pain/state reaction dispatch(...);
}
```

Direct instructions include:

```text
mov al, es:[si+10]
cmp ax, damage
jg  non_lethal
mov es:[si+10], ah       ; AH is zero here -> strength = 0
...
non_lethal:
mov al, damage
sub es:[si+10], al       ; strength -= damage
mov byte ptr es:[si+12], 8
```

Thus **enemy HP storage and the lethal/non-lethal damage split are now VERIFIED_EXE**. Exact initial HP per enemy and exact weapon damage constants are still TODO; those require tracing the strength initializer and `compute_damage` producer.

## Current GUARD layout

| Offset | Width | Meaning | Status |
|---:|---:|---|---|
| `+00` | 2 | sequence/definition-derived value | PARTIAL |
| `+02` | 4 | timestamp/time value | VERIFIED_EXE |
| `+06` | 2 | **timer** | VERIFIED_EXE |
| `+08` | 2 | OBJECT slot/index | VERIFIED_EXE |
| `+0A` | 1 | **strategy** | VERIFIED_EXE |
| `+0B` | 1 | state | VERIFIED_EXE |
| `+0C` | 1 | nextstate | VERIFIED_EXE |
| `+0D` | 1 | o_id | VERIFIED_EXE |
| `+0E` | 1 | definition lookup result | PARTIAL |
| `+0F` | 1 | synchronization boolean | PARTIAL |
| `+10` | 1 | **strength / HP** | **VERIFIED_EXE** |
| `+11` | 1 | **octant** | **VERIFIED_EXE** |
| `+12` | 1 | **resoct** | **VERIFIED_EXE** |
| `+13` | 1 | transition parameter | PARTIAL |
| `+14..15` | 2 | unknown | TODO |
| `+16` | 1 | transition/control flag | PARTIAL |
| `+17..19` | 3 | unknown | TODO |

## 28-byte OBJECT layout

| Offset | Width | Role | Status |
|---:|---:|---|---|
| `+00` | 1 | object/map ID | VERIFIED access |
| `+01` | 1 | subtype/variant-like value | PARTIAL |
| `+02/+03` | 2 | signed render/movement-related components depending runtime object class | PARTIAL |
| `+04` | 1 | definition-table ID | VERIFIED access |
| `+05` | 1 | flags; bit 0x08 selects GUARD creation | VERIFIED_EXE |
| `+06` | 1 | **class** | VERIFIED_EXE developer label |
| `+07` | 1 | GUARD index for guard objects | VERIFIED_EXE |
| `+08` | 4 | runtime value initialized zero | TODO semantic |
| `+0C:+0E` | 4 | map-cell far pointer | VERIFIED_EXE |
| `+10` | 2 | world X | VERIFIED_EXE |
| `+12` | 2 | world Y | VERIFIED_EXE |
| `+14..19` | 6 | unknown | TODO |
| `+1A` | 1 | runtime byte initialized zero | TODO semantic |
| `+1B` | 1 | unknown | TODO |

A separate runtime mover has also been found that resolves an OBJECT by `index*0x1C`, adds signed byte deltas to `OBJECT+10/+12`, updates the map-cell pointer and decrements a lifetime/count byte. This proves that X/Y are mutable integer world coordinates and that some movers use per-tick signed deltas. It is not yet promoted as the GUARD walking-speed routine until its owning runtime class is tied to GUARD state dispatch.

## Next targets

1. Trace the **strength initializer** -> exact HP by enemy class.
2. Trace `compute_damage` producer -> exact weapon damage / randomization / difficulty effects.
3. Trace GUARD movement state handlers that write OBJECT X/Y -> direction and walking speed.
4. Trace timer/timestamp writes in detection and attack states -> reaction delay and attack interval.
5. Follow lethal/non-lethal handlers into sound calls -> pain/death SND.DAT IDs; then alert/attack states.

The renderer remains deferred until this runtime/combat layer is substantially complete.
