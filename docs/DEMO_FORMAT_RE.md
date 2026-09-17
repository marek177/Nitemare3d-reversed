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

The level initialization scan walks the second byte of every 2-byte MAP cell. Runtime class 2 is the player start. For the player-start object:

```text
playerX = tileX * 64 + 32
playerY = tileY * 64 + 32
initialAngle = (objectId - baseObjectIdForClass2) * 90 degrees
```

The angle is normalized into `0..359` and stored in `0x4BEA`; player coordinates are `0x4BF6/0x4BF8`. **VERIFIED_EXE**.

Player-start IDs are 1,2,3,4 = 0,90,180,270 degrees. **VERIFIED_DATA + VERIFIED_EXE**.

## All 31 final-map starts / first-room fingerprint baseline

A fresh parse of the supplied final MAP.1-3 finds exactly one player-start marker in every one of the 31 final maps. These are the exact tile starts and orientations:

| Level | tile | angle |
|---|---|---:|
| E1M1 | (22,56) | 0 |
| E1M2 | (32,28) | 0 |
| E1M3 | (16,49) | 90 |
| E1M4 | (50,40) | 0 |
| E1M5 | (26,25) | 0 |
| E1M6 | (27,32) | 0 |
| E1M7 | (18,45) | 270 |
| E1M8 | (33,52) | 180 |
| E1M9 | (24,35) | 90 |
| E1M10 | (50,29) | 180 |
| E1M11 | (16,49) | 90 |
| E2M1 | (22,59) | 0 |
| E2M2 | (24,24) | 90 |
| E2M3 | (27,52) | 90 |
| E2M4 | (32,41) | 90 |
| E2M5 | (35,62) | 270 |
| E2M6 | (42,29) | 270 |
| E2M7 | (30,39) | 0 |
| E2M8 | (4,2) | 90 |
| E2M9 | (18,37) | 0 |
| E2M10 | (49,18) | 270 |
| E3M1 | (45,38) | 90 |
| E3M2 | (25,16) | 180 |
| E3M3 | (7,5) | 0 |
| E3M4 | (34,34) | 270 |
| E3M5 | (30,29) | 180 |
| E3M6 | (35,27) | 180 |
| E3M7 | (59,52) | 90 |
| E3M8 | (4,7) | 180 |
| E3M9 | (43,42) | 270 |
| E3M10 | (54,44) | 180 |

**VERIFIED_DATA**.

A 15x15 first-plane patch centered on each spawn was hashed as a geometry-local fingerprint. Among all 31 final maps the only duplicate local first-plane fingerprint is **E1M3 == E1M11**. Their second-plane fingerprints differ, as expected from the known 17 object/state byte differences. This independently strengthens the use of E1M3/E1M11 as the positive-control pair for trajectory matching. **VERIFIED_DATA**.

## Early DEMO command fingerprints

The uploaded demo streams have visibly different early command patterns. Examples from the first records:

- DEMO.1 begins with forward (`0x0002`), then idle, FIRE (`0x0080`), turn (`0x0008`), FIRE, opposite turn (`0x0010`), further FIRE events.
- DEMO.2 begins forward, turn (`0x0010`), forward, later backward (`0x0004`), combined backward+turn (`0x0014`), and further movement/turning.
- DEMO.3 begins forward, then two early USE/ACTION (`0x0200`) pulses, more forward movement, then additional USE/ACTION pulses.

Across the full streams, DEMO.3 contains 21 records carrying `0x0200`, compared with 6 in DEMO.1 and 5 in DEMO.2. DEMO.3 therefore has a particularly strong interaction-event fingerprint that should help reject candidate first rooms lacking compatible nearby doors/switches/interactives. **VERIFIED_DATA** for record counts; exact world interaction target remains dependent on collision/action reconstruction.

## Movement commit / collision chain

The normal movement path computes a proposed destination and reaches a commit routine around raw `0x1E9E0`. Helpers run before committing `DI -> 0x4BF6` and `SI -> 0x4BF8`; after commit tile coordinates are derived by arithmetic shift right 6. **VERIFIED_EXE**.

This confirms 64 world units per tile. Exact passability flags for wall/door types remain PARTIAL. A naive `wallByte != 0` rule is invalid because spawn cells themselves can have nonzero first-plane values.

## Playback/record state machine

Global `0x46B8`: state 1 creates/opens `demo.N` and writes the header; state 2 records; state 3 opens for playback; state 4 timed playback; state 5 close/reset. Timestamps are compared against game tick `0x53DC`. **VERIFIED_EXE**.

## Resource relationship and attract mode

Resource setup constructs `map.N`, `img.N`, and `demo.N` from the same numeric selector. Normal menu attract behavior observed by testing forces resource set 1 and visibly runs Level 1:11. Removing demos produces `Error opening file demo.1`; substituting DEMO.2/3 does not change the loaded HUD/map from 1:11. **BEHAVIORAL + VERIFIED_FORMAT**.

## DEMO origin search policy — corrected

Do not constrain DEMO.2 to Episode 2 or DEMO.3 to Episode 3. Their suffixes are not yet proof of original recording level. Each demo must be tested against **all 31 preserved final maps**:

```text
DEMO.1 x E1M1..E1M11, E2M1..E2M10, E3M1..E3M10
DEMO.2 x E1M1..E1M11, E2M1..E2M10, E3M1..E3M10
DEMO.3 x E1M1..E1M11, E2M1..E2M10, E3M1..E3M10
```

This is 93 demo/map combinations. **METHOD / TODO**.

Possible outcomes are deliberately broader than the earlier E2M3/E3M3 hypothesis:

1. exact or near-exact match to a preserved map;
2. strong early match followed by systematic divergence, suggesting an older revision of that preserved map;
3. no convincing match among all 31 maps, increasing the likelihood of a deleted/development map absent from the final containers.

E2M3 and E3M3 remain candidates only; they receive no prior scoring advantage.

## First-room forensic matcher

Before full-engine collision fidelity, use a staged fingerprint matcher. For each map collect spawn, angle, a local 15x15/21x21 two-plane patch, nearby wall/resource IDs, nearby object IDs, and eventually decoded doors/enemies/interactives. Compare the earliest demo command sequence against this local environment. This can eliminate impossible candidates before full trajectory simulation.

The positive control is DEMO.1: a correct matcher should independently rank E1M3/E1M11 together because they have the same spawn and local first-plane geometry. If it fails this test, the movement/collision model is not yet reliable enough to interpret DEMO.2/3 rankings.

## Command-line switch

`NITE3W.EXE -r` sets demo state 1 and enables recording. **VERIFIED_EXE**. No command-line case directly setting playback state 3 has yet been found.

## Next

Decode exact collision/passability and USE target semantics, then run the 93-combination staged matcher. DEMO.3's unusually dense early USE/ACTION pattern is a high-value discriminator. Preserve ranked raw scores and divergence timestamps rather than forcing a winner; a deleted/older map must remain a valid outcome.
