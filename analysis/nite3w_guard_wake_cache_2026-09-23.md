# Nitemare 3-D Win16 guard wake cache

**Date:** 2026-09-23  
**Scope:** Win16 1.10, cross-checked against Win16 1.8; static decompilation, raw 16-bit assembly, and the supplied WALLS metadata.

## Finding

The 64-byte block at runtime offset 0xA65E and USER.SAV offset 0xD5A3 is a per-level, saved one-shot gate for waking a subset of guards after the player fires. Its key is derived from a wall tile in class D (the DOOR family), not from a unique map coordinate or the current floor number.

The behavior is mechanically well-supported. The intended design reason for grouping guards by DOOR tile ID remains unknown, and runtime observation is still needed.

## Selector calculation

FUN_1010_247A in Win16 1.10 classifies a map cell's first byte using the 256-entry table at DAT_1048_8196. If the class is D, it returns the wall ID minus the first wall ID classified D. Otherwise it returns -1. It caches that first D ID until DAT_1048_7E52 changes. Raw assembly at segment 3 offset 0x247A pushes 0x0044:0x0000 to FUN_1010_2334; the latter scans the class table for byte 0x44 ('D') from index zero.

The supplied WALLS metadata lists 24 DOOR-family IDs. They range from 0x70 through 0xAE, so the returned selector values are sparse and range from 0 through 62:

| Wall IDs | Selector values | WALLS class |
|---|---|---|
| 0x70–0x77 | 0–7 | DOORVC / DOORHC / DOORV / DOORH |
| 0x79–0x80 | 9–16 | keyed DOORVL / DOORHL |
| 0x82–0x83 | 18–19 | closet DOORV / DOORH |
| 0xA3–0xA6 | 51–54 | transport-chamber DOORVI / DOORHI |
| 0xAD–0xAE | 61–62 | elevator DOORV / DOORH |

Selector 0 is a real result for wall ID 0x70, but the wake routine treats argument zero as a no-op. Selector 63 is allocated but has no DOOR-family ID in the supplied WALLS metadata. The current data therefore stays within the 64-byte cache. FUN_1010_247A itself does not clamp the result, so that safety depends on the wall-class table's ID range.

WARP_L*, WARP_S*, and WARP_* classes are not class D, so they do not update this selector through this function.

## Where the player and guards get the key

FUN_1010_8A20 updates the player's map-cell pointer from the player's coordinates, calls FUN_1010_247A, and writes DAT_1048_4C1C only when the result is not -1. Moving across a non-D cell therefore leaves the previous value in DAT_1048_4C1C.

The guard movement path in FUN_1010_71DC performs the same classification for the guard's current map cell. When the result is not -1, it stores the selector in guard record byte +0x0E. Non-D cells do not clear that field. The player and guard fields thus represent their most recently recorded DOOR-family wall selector. The value identifies a tile/resource code shared by instances of that wall ID; it is not a coordinate.

The same selector comparison is also used by guard state 0x0F: when guard byte +0x0E equals DAT_1048_4C1C, the code calls the class-dependent helper FUN_1010_B5E4 before continuing the state sequence. This is a second consumer of the selector, but it does not establish the original design label for the grouping.

## Wake gate

FUN_1010_7664 uses its 16-bit argument as a selector:

1. Argument 0 returns without action.
2. Argument -1 clears sixteen dwords at runtime offset 0xA65E, exactly 64 bytes.
3. For another value, it checks byte 0xA65E + selector. If already nonzero, it returns. Otherwise it stores 1 and scans the active guard records.
4. A guard is changed only when strategy byte +0x0A is zero, selector byte +0x0E equals DAT_1048_4C1C, and state byte +0x0B is 7 or 8.
5. A matching guard gets a random timer of 0–7 simulation updates in word +0x06 and state 1. State 1 counts down before proceeding to state 2; normal AI processing then continues.

The wake loop has no distance or line-of-sight test. Because it marks the selector before scanning, later shots with the same selector do not rescan or wake further guards until the cache is cleared. A zero selector never reaches this gate.

## Attack and sound path

In Win16 1.10, FUN_1010_8B06 reaches the wake routine after the hitscan or projectile-fire path succeeds. Raw assembly at segment 3 offset 0x8BED loads DAT_1048_4C1C, pushes it, and far-calls FUN_1010_7664. It then calls FUN_1010_B594 to select and play the attack sound and marks DAT_1048_4C30.

The direct wake behavior is therefore triggered by a successful player-fire path; this handler does not model sound travel, attenuation, distance, or visibility. That does not rule out other sound-related AI paths elsewhere in the executable.

The same sequence is present in Win16 1.8 under different function names: the cache routine is FUN_1010_75C0, the corresponding attack path is FUN_1010_8A62, and the selector classifier is FUN_1010_242E. The 1.8 cache body has the same 64-byte clear, selector gate, strategy/state filters, and random 0–7 timer.

## Save lifetime

The save writer and loader copy 0x40 bytes at runtime offset 0xA65E to/from USER.SAV offset 0xD5A3. Win16 1.10 level setup FUN_1018_09F2 clears the gate with FUN_1010_7664(-1). The save-menu load path calls level setup first and then FUN_1010_574C, which restores the saved bytes. A fresh level entry clears the gate; resuming a saved slot restores its prior selector marks.

## Remaining questions

- Why the design groups guard wake events by a DOOR-family wall ID instead of by proximity, door instance, or room.
- Whether every supported WALLS build keeps all class-D IDs within selector range 0–63.
- Runtime behavior for each DOOR-family selector, especially the no-op selector 0 and repeated shots in separate areas sharing one wall ID.
- Whether the direct shot-triggered wake and the separate state-0x0F selector check are parts of one intended room/door mechanic.

## Evidence limits

This is static analysis of Win16 1.10 and 1.8. The selector range uses the supplied WALLS metadata, and the raw assembly check uses the local 1.10 code-segment extraction. No live game trace was performed.
