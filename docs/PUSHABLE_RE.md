# Pushable objects — NITE3W.EXE reconstruction notes

This module is based on the supplied `NITE3W.EXE`, `MAP.1-3`, and `OBJECTS.1-3`. The constants below are not guessed from Wolf3D.

All three `OBJECTS.*` files mark four object IDs as class `PUSH`: `0x18`, `0x4B`, `0x4C`, `0x4D` (tombstone and box variants).

## Executable evidence

### `3:181C` — BuildPushTable / InitPushes

Scans 28-byte runtime object records, compares the class byte at `+6` to `0x28`, creates 6-byte push records, and enforces a maximum of 12.

### `3:21B6` — StartPush

Looks up the push record, rejects an already active push, validates the destination, copies two signed movement bytes into the push record and writes an 8-update counter.

### `3:2210` — UpdatePushes

For active records it updates fixed-point X/Y, recomputes the containing map cell, transfers the object-layer byte when the cell changes, writes coordinates back and decrements the counter.

Coordinates are shifted right by 6 elsewhere in the same code, establishing 64 internal units per map tile. Cardinal movement increments are ±8, giving 8 updates × 8 units = one tile.

## Implementation constants

```cpp
FixedUnitsPerTile = 64;
PushStepUnits     = 8;
PushTicks         = 8;
MaxPushables      = 12;
```

Still unresolved: the exact destination tile-property bit tested by StartPush and the exact global tick frequency controlling wall-clock push speed.
