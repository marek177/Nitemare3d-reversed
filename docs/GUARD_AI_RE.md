# GUARD AI reverse engineering

Date: 2026-09-17
Evidence: supplied `nite3w(4).exe` (Win16 NE, 230400 bytes) plus the reconstructed USER.SAV write layout.

## Verified guard-record facts

The executable diagnostic paths contain `Problem with guard: state=%d, next_state=%d, o_id=0x%x`, `Guard not in map`, `No seqdef defined for guard` and `MAXGUARD exceeded (%d)`.

The guard-validation loop advances its record pointer by **0x1A bytes (26 bytes)** per iteration. Immediately before the diagnostic call it reads these byte fields:

| GUARD offset | Width | Verified semantic |
|---:|---:|---|
| `+0x0B` | 1 | `state` |
| `+0x0C` | 1 | `next_state` |
| `+0x0D` | 1 | `o_id` |
| stride | `0x1A` | complete GUARD runtime record |

Evidence: **VERIFIED_EXE**.

## USER.SAV correlation: GUARD array identified

The reconstructed USER.SAV writer stores a block at **`0xB43B`** of exactly **`0x0A28` = 2600 bytes**. The recovered GUARD stride gives:

```text
2600 / 26 = 100
0x0A28 / 0x1A = 100
```

Thus this save block has the exact shape **100 x GuardRuntimeRecord**. Together with the EXE's fixed-stride GUARD iteration and `MAXGUARD exceeded` capacity diagnostic, `USER.SAV+0xB43B` is identified as the persisted fixed-capacity GUARD runtime array.

Evidence: **VERIFIED_EXE + VERIFIED_SAVE_LAYOUT**.

### Confirmed anchors

- GUARD capacity: **100 records**.
- GUARD record size: **26 bytes (`0x1A`)**.
- Serialized GUARD array: **2600 bytes (`0x0A28`)**.
- Serialized GUARD array range: **`USER.SAV+0xB43B .. +0xBE62`**.
- Saved `+0x0B/+0x0C/+0x0D` map directly to `state/next_state/o_id` for every persisted guard.

This provides a deterministic path to recover position, HP, speed/reaction timers and remaining fields by correlating controlled save snapshots with executable accesses.

## Next field-recovery targets

| Priority | Field/behavior | Status |
|---:|---|---|
| 1 | GUARD stride | VERIFIED `0x1A` |
| 2 | capacity | VERIFIED `100` |
| 3 | USER.SAV GUARD block | VERIFIED `0xB43B..0xBE62` |
| 4 | state / next_state / o_id | VERIFIED `+0x0B/+0x0C/+0x0D` |
| 5 | position X/Y | TODO |
| 6 | HP | TODO |
| 7 | movement direction/angle | TODO |
| 8 | movement speed | TODO |
| 9 | reaction/state timer | TODO |
| 10 | sequence/animation ID | TODO |
| 11 | visibility/target flags | TODO |
| 12 | attack type/damage | TODO |
| 13 | alert/attack/pain/death SFX IDs | TODO |

## State-machine target

`spawn -> idle/patrol -> detection -> reaction -> chase -> attack -> pain -> death`

Transitions remain **BEHAVIORAL/INFERRED** until tied to executable branches. Record size, capacity, save-array location and the three named byte fields are verified clean-room anchors.
