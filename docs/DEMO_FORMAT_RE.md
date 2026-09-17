# DEMO.1-3 format / attract-mode reverse engineering

Date: 2026-09-17

## Data comparison

| file | size | header | 8-byte records | final timestamp |
|---|---:|---|---:|---:|
| DEMO.1 | 1630 | `0A 00 05 00 14 00` | 203 | 1157 |
| DEMO.2 | 2174 | `0A 00 05 00 14 00` | 271 | 2284 |
| DEMO.3 | 2294 | `0A 00 05 00 14 00` | 286 | 2565 |

All three have the same 6-byte header, three little-endian WORDs `(10,5,20)`. **VERIFIED_DATA**.

## Corrected 8-byte record layout

Direct recording/playback code at `seg3:90CE..9266` proves:

```cpp
#pragma pack(push,1)
struct DemoRecord {
    uint8_t  eventByte;
    uint16_t inputMask;
    uint8_t  pad;
    uint32_t timestamp;
};
#pragma pack(pop)
```

Recording state 2 writes current input/event state and tick; playback state 4 restores it. **VERIFIED_EXE**.

## Input-mask decoding

| mask | reconstructed effect |
|---:|---|
| `0x0002` | move in current facing direction |
| `0x0004` | move opposite current facing direction (angle + 180 degrees) |
| `0x0008` | turn one direction; with `0x0100`, strafe using angle + 270 degrees |
| `0x0010` | turn opposite direction; with `0x0100`, strafe using angle + 90 degrees |
| `0x0020` | double movement and turn increments |
| `0x0040` | force movement/turn increments to 1 |
| `0x0080` | FIRE; reaches weapon-fire routine `seg3:8B06` |
| `0x0100` | strafe modifier |
| `0x0200` | edge-triggered action/use-like event |

**VERIFIED_EXE** for bit tests/effects; left/right user-facing labels remain PARTIAL.

The first two demo-header WORDs feed movement/angular increments. With the supplied demos the base values are 10 and 5. **VERIFIED_EXE / VERIFIED_DATA**.

## Player spawn and initial angle — recovered

The level initialization scan at raw disassembly `0x23312..0x23386` walks the second byte of every 2-byte MAP cell (`mapBuffer+1`, stride 2). For each object byte it performs a runtime class lookup. When the resolved class equals 2, the entry is treated as the player start. **VERIFIED_EXE**.

For the player-start object the routine sets:

```text
playerX = tileX * 64 + 32
playerY = tileY * 64 + 32
initialAngle = (objectId - baseObjectIdForClass2) * 90 degrees
```

The angle is passed to the normal angle setter. That setter normalizes into `0..359` and stores the result in global `0x4BEA`. Player world coordinates are globals `0x4BF6`/`0x4BF8`. **VERIFIED_EXE**.

A data-wide search over all supplied MAP.1/2/3 levels independently identifies one and only one contiguous four-ID family that occurs exactly once per level: object IDs **1,2,3,4**. This matches the EXE's four-orientation subtraction/multiply-by-90 construction. Therefore player start markers are:

| object ID | initial angle |
|---:|---:|
| 1 | 0 degrees |
| 2 | 90 degrees |
| 3 | 180 degrees |
| 4 | 270 degrees |

**VERIFIED_DATA + VERIFIED_EXE**.

### Exact starts for high-value demo candidates

- E1M3: object 2 at tile `(16,49)` -> world `(1056,3168)`, angle 90 degrees.
- E1M11: object 2 at tile `(16,49)` -> world `(1056,3168)`, angle 90 degrees.
- E2M3: object 2 at tile `(27,52)` -> world `(1760,3360)`, angle 90 degrees.
- E3M3: object 1 at tile `(7,5)` -> world `(480,352)`, angle 0 degrees.

E1M3 and E1M11 thus share not only almost identical payload geometry but also exactly the same player spawn and initial facing. **VERIFIED_DATA**.

## Movement commit / collision chain

The normal movement path computes a proposed destination and reaches a commit routine around raw `0x1E9E0`. That routine calls multiple helpers before committing `DI -> 0x4BF6` and `SI -> 0x4BF8`; after commit it derives current tile coordinates by arithmetic shift right 6 and updates the current map-cell far pointer. **VERIFIED_EXE**.

This confirms 64 world units per tile and that collision/interaction processing occurs before the final coordinate write. The exact passability flags for each wall/door type are still PARTIAL because the helper chain consults runtime lookup tables populated from episode resources. A naive rule such as `wallByte != 0` is incorrect: known player spawn cells themselves contain nonzero first-byte values (for example E1M3/E1M11 spawn first byte `187`, E2M3/E3M3 `193`).

Therefore the final trajectory matcher must use the recovered collision flags/lookup semantics rather than guessing that zero means floor.

## Playback/record state machine

Global `0x46B8`:

- state 1: create/open `demo.N`, write 6-byte header
- state 2: record 8-byte records
- state 3: open existing `demo.N`, read header + first record
- state 4: timed playback
- state 5: close/reset

Record timestamps are compared against game tick `0x53DC`. **VERIFIED_EXE**.

## Resource relationship and attract mode

Resource setup constructs `map.N`, `img.N`, and `demo.N` from the same numeric selector. Normal menu attract behavior observed by testing forces resource set 1 and visibly runs Level 1:11. Removing demos produces `Error opening file demo.1`; substituting DEMO.2/3 does not change the loaded HUD/map from 1:11. **BEHAVIORAL + VERIFIED_FORMAT**.

## MAP.1 E1M3 versus E1M11

Their 8192-byte payloads differ by only 17 bytes and their player start is identical. E1M11 is therefore a very close E1M3-derived demo variant. **VERIFIED_DATA**.

## DEMO.2 / DEMO.3 origin hypothesis

- DEMO.1 is compatible with E1M3/E1M11.
- DEMO.2 may originate from an Episode 2 map; E2M3 remains a high-value candidate.
- DEMO.3 may originate from an Episode 3 map; E3M3 remains a high-value candidate.

E2M3/E3M3 are still **INFERRED**, not yet verified. The newly recovered spawn system gives the matcher exact start state for every candidate level, removing one major ambiguity.

## Command-line switch

`NITE3W.EXE -r` sets demo state 1 and enables recording. **VERIFIED_EXE**. No command-line case directly setting playback state 3 has yet been found.

## Next: finish collision flags, then automatic matcher

Spawn and initial angle are no longer blockers. The remaining critical prerequisite is the exact movement collision/passability lookup used before the `0x4BF6/0x4BF8` commit.

Once recovered, replay DEMO.1 across E1 levels as calibration, then DEMO.2 across E2M1-10 and DEMO.3 across E3M1-10. Score wall collisions/stalls, successful door/use interactions, firing lines toward guard positions, and duration before divergence. E1M3/E1M11 should form the positive-control pair for DEMO.1.
