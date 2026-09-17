# GUARD AI reverse engineering

Date: 2026-09-17
Evidence: supplied `nite3w(4).exe` (Win16 NE, 230400 bytes).

## Newly verified guard-record facts

A direct static pass over the original executable located the diagnostic path using the strings:

- `Problem with guard: state=%d, next_state=%d, o_id=0x%x`
- `Guard not in map`
- `No seqdef defined for guard`
- `MAXGUARD exceeded (%d)`

The guard-validation loop advances its record pointer by **0x1A bytes (26 bytes)** per iteration. This establishes the runtime GUARD record stride.

Immediately before the diagnostic printf-style call, the executable reads three byte fields from the current record and pushes them in right-to-left printf argument order:

| GUARD record offset | Width | Verified semantic |
|---:|---:|---|
| `+0x0B` | 1 byte | `state` |
| `+0x0C` | 1 byte | `next_state` |
| `+0x0D` | 1 byte | `o_id` |
| record stride | `0x1A` | complete runtime GUARD record size |

Evidence classification: **VERIFIED_EXE**.

The loop also compares its iteration index against a global guard count, confirming that active guards are maintained as a contiguous fixed-stride runtime collection. The exact semantic name/address of the count global will remain provisional until its producer/consumer xrefs are completely traced.

## Important consequence for USER.SAV correlation

A 26-byte GUARD record is now a strong binary signature. The next pass should test each fixed USER.SAV runtime array against this stride and against the runtime guard-array base/capacity. This can identify which save block persists GUARD records and unlock additional fields such as coordinates, HP, timers and sequence pointers/indices.

## Next field-recovery targets

| Priority | Field/behavior | Status |
|---:|---|---|
| 1 | guard array base and capacity | partial |
| 2 | position X/Y | TODO |
| 3 | HP | TODO |
| 4 | movement direction / angle | TODO |
| 5 | movement speed | TODO |
| 6 | reaction / state timer | TODO |
| 7 | sequence/animation identifier | TODO |
| 8 | target/player visibility flags | TODO |
| 9 | attack type and damage | TODO |
| 10 | alert/attack/pain/death SFX IDs | TODO |

## State-machine target

The reconstruction must ultimately account for:

`spawn -> idle/patrol -> detection -> reaction -> chase -> attack -> pain -> death`

Transitions inferred from gameplay remain **BEHAVIORAL/INFERRED** until tied to the executable. The three record fields above and the 0x1A stride are already **VERIFIED_EXE** and may safely be represented in clean-room source code.
