# Win16 DoorRuntime layout closure — 2026-09-28

## Result

The Win16 1.10 dynamic-door controller record is now byte-accounted across its full 22-byte stride. Static layout/state coverage is estimated at **99%** for this Win16-specific subarea.

This does not mean the cross-platform door subsystem is 99%: DOS uses a different 18-byte runtime record and still requires its own byte-level closure.

## Complete Win16 record

```text
+00 dword moving wall component A far pointer
+04 dword moving wall component B far pointer
+08 dword owning MAP-cell far pointer
+0C word  state
+0E word  auto-close countdown
+10 word  world/controller anchor X
+12 word  world/controller anchor Y
+14 byte  sound/action latch
+15 byte  no direct XREF; runtime-unused/padding
stride = 0x16 / 22 bytes
capacity = 64
save block = 0x580 bytes
```

## Closed behavior

- state 0 open/passable;
- state 1 closed;
- state 2 opening;
- state 3 closing;
- state 4 corpse hold-open/passable disabled-door state;
- motion step = 2 internal units/update;
- completed motion sets countdown 32;
- occupied doorway retries auto-close after 4 updates;
- opening/closing SFX requests use runtime indices 0x25/0x26;
- manual/remote activation uses +0x14 as the SFX/action latch;
- +0x15 has no direct Win16 1.10 XREF.

## Why not 100%

The remaining 1% is deliberately reserved for dynamic parity:

1. controlled original-runtime trace of every state transition, including corpse state 4;
2. exact simulation-time calibration of the 32/4 countdowns;
3. confirmation that +0x15 remains semantically unused under load/save across retail saves;
4. DOS and older-Windows-version structural comparison is tracked separately.

The record layout itself is statically complete enough for clean-room typed reconstruction.
