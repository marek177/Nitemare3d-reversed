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
    uint8_t  eventByte;     // runtime 0x0108
    uint16_t inputMask;     // runtime 0x3756
    uint8_t  pad;           // zero in all supplied records
    uint32_t timestamp;     // game/demo tick
};
#pragma pack(pop)
```

Recording state 2 writes `0x0108 -> +0`, `0x3756 -> +1`, current tick `0x53DC -> +4`. Playback state 4 performs the inverse copy. **VERIFIED_EXE**. `pad` is zero in all 760 supplied records. **VERIFIED_DATA**.

## Input-mask decoding

The normal player-input routine directly tests `0x3756`, so most movement/action bits can now be decoded. **VERIFIED_EXE** for the bit tests/effects.

| mask | reconstructed effect |
|---:|---|
| `0x0002` | move in current facing direction |
| `0x0004` | move opposite current facing direction (angle + 180 degrees) |
| `0x0008` | turn one direction; with `0x0100`, strafe using angle + 270 degrees |
| `0x0010` | turn opposite direction; with `0x0100`, strafe using angle + 90 degrees |
| `0x0020` | double movement and turn increments |
| `0x0040` | force movement/turn increments to 1; user-facing key name still TODO |
| `0x0080` | FIRE; reaches verified weapon-fire routine `seg3:8B06` |
| `0x0100` | strafe modifier for `0x0008/0x0010` |
| `0x0200` | edge-triggered action/use-like event; exact user-facing name still PARTIAL |

Left/right naming for `0x0008/0x0010` remains to be fixed against the engine angle convention. The forward/back interpretation of `0x0002/0x0004` is stronger because the latter explicitly uses current angle + 180.

The first two demo-header WORDs feed the same routine as movement/angular increments. `0x0020` doubles both and `0x0040` forces both to 1. Exact semantic name of the third header WORD is still TODO. **VERIFIED_EXE / PARTIAL labels**.

## Input vocabulary in original streams

All three files use the same compact family of masks, confirming recorded relative player input rather than absolute X/Y trajectories. Common masks include `0`, `2`, `4`, `8`, `10`, `16`, `18`, `128`, `130`, `136`, `144`, `512`, and combinations such as `514` and `528`. **VERIFIED_DATA**.

This explains the substitution test: when DEMO.2 or DEMO.3 is copied into the DEMO.1 slot while E1M11 remains loaded, the engine blindly executes valid movement/fire/use commands against incompatible geometry, producing collisions, spinning and shots into walls. **BEHAVIORAL + VERIFIED_FORMAT**.

## Playback/record state machine

Global `0x46B8`:

- state 1: create/open `demo.N`, write 6-byte header
- state 2: record changed event/input state as 8-byte records
- state 3: open existing `demo.N`, read header + first record
- state 4: timed playback
- state 5: close/reset

Record timestamps are compared against game tick `0x53DC`. **VERIFIED_EXE**.

## Resource relationship and attract mode

The resource setup constructs `map.N`, `img.N`, and `demo.N` from the same numeric selector; demo filename buffer is `0x7E84`. **VERIFIED_EXE**.

Normal menu attract behavior observed by testing forces resource set 1 and visibly runs Level 1:11. Removing demos produces `Error opening file demo.1`. Substituting DEMO.2/3 does not change the loaded HUD/map from 1:11. Therefore map identity is not encoded in the 8-byte demo command records. **BEHAVIORAL + VERIFIED_FORMAT**.

## MAP.1 E1M3 versus E1M11

A direct comparison of their 8192-byte payloads finds only 17 differing bytes. They are extremely close variants, but not literally byte-identical. **VERIFIED_DATA**.

This is strong evidence that E1M11 is derived from/copies the E1M3 layout for attract playback, but exact map-plane semantics must remain separate from the demo-stream proof.

## DEMO.2 / DEMO.3 origin hypothesis

- DEMO.1 is compatible with E1M3/E1M11.
- DEMO.2 may originate from an Episode 2 map; E2M3 is a high-value candidate.
- DEMO.3 may originate from an Episode 3 map; E3M3 is a high-value candidate.

E2M3/E3M3 remain **INFERRED**. Final MAP.2/MAP.3 contain 10 maps each, so deleted E2M11/E3M11 maps cannot currently be asserted.

## Command-line switch

`NITE3W.EXE -r` sets demo state 1 and enables recording. **VERIFIED_EXE**. No command-line case directly setting playback state 3 has yet been found.

## Next: automatic trajectory matcher

The demo command format is no longer the main blocker. A trustworthy matcher now needs exact player spawn/initial angle and map collision/passability semantics.

Planned scoring:

1. recover candidate level player start and initial angle;
2. replay forward/back and turn commands with the header-derived increments;
3. apply strafe modifier behavior;
4. reproduce wall/door collision sufficiently to detect impossible movement;
5. score collisions/stalls versus valid corridor traversal;
6. use FIRE events as secondary enemy/line-of-sight evidence;
7. use action/use events as strong door/switch evidence;
8. calibrate DEMO.1 on E1M3/E1M11;
9. rank DEMO.2 across E2M1-10 and DEMO.3 across E3M1-10.

The next EXE pass should therefore target player-spawn extraction and the movement/collision routine called from this decoded input handler.
