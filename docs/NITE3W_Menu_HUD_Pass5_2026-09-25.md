# NITE3W Menu/HUD — Pass 5

Date: 2026-09-25  
Target: NITE3W Win16 V1.10, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

This pass resolves the former `A69E` unknown save block and closes the semantics of `7E52/7E54`. It also narrows the six-byte block at `6D60` and the four-byte save-header time field without over-naming either.

## 1. `A69E` is the live MAP level payload

`3:488C..48F9` opens the current `MAP.*` file, validates the requested level index, seeks to:

```text
0x202 + (int32)DS:7E54 * 0x2000
```

and reads exactly `0x2000` bytes into `DS:A69E`.

`0x202 = 514`, matching the recovered MAP episode header. `0x2000 = 8192 = 64 * 64 * 2`, matching one 64x64 level payload.

Therefore the save block at slot offset `+0x0035`, length `0x2000`, is not and secondary cache. It is the current mutable in-memory copy of the level'with MAP cell payload.

### Exact cell layout

The movement/collision path computes and cell address as:

```text
cell = A69E + 2 * (y * 64 + x)
```

At that address:

```text
cell[0] -> index into wall property table DS:7E94
cell[1] -> index into object property table DS:7F94
```

Thus the two-byte runtime cell is directly:

```cpp
struct MapCell {
    uint8_t wallId;
    uint8_t objectId;
};
```

The map is row-major by `y*64+x` in this path.

### Why saving the block matters

Because the entire 8192-byte live payload is written to USER.SAV and restored, runtime wall/object-cell mutations survive save/load. The save is not reconstructed only from the original MAP archive plus actor tables.

After load, the code rebuilds pointers into this block. For example, player/cell state and each runtime OBJECT'with map binding are reconstructed to point back into `A69E`.

## 2. `7E52` = episode number, `7E54` = zero-based level index

These can now be named with high confidence.

### `DS:7E52` — episode number, 1-based

`3:4989` stores its function argument directly into `7E52`. The same routine formats episode resource names from the strings:

```text
"map."
"img."
"%s%d"
```

Thus values 1, 2, 3 select episode-suffixed resources such as `MAP.1` / `IMG.1` etc.

Recommended name:

```cpp
uint16_t episodeNumber; // 1..3
```

### `DS:7E54` — level index, zero-based

Segment 4 function around `4:09F2` stores its first argument directly to `7E54`, then initializes the selected level. The MAP loader uses that value in `0x202 + levelIndex*0x2000`.

The HUD at `3:A43B` explicitly increments it before formatting:

```text
AX = DS:7E54
AX++
format("%d : %d", DS:7E52, AX)
```

With the user-visible level number is `levelIndex + 1`.

Recommended name:

```cpp
uint16_t levelIndex; // 0-based
```

The save header therefore stores:

```text
+0x2D  uint16 episodeNumber
+0x2F  uint16 levelIndex
```

not two unknown story words.

## 3. Save/load cross-check

On save, both globals are written into the 53-byte slot header. On load, both are read into locals. The loader compares them with the current runtime episode and level; when the context differs, it enters the resource/level transition path before rebuilding live pointers.

This gives independent evidence from:

1. resource filename construction;
2. MAP seek arithmetic;
3. HUD formatting;
4. save header serialization;
5. load-time context comparison.

## 4. `DS:A69E` address consumers

Additional code independently supports the MAP interpretation:

- wall setup scans byte 0 of each cell and applies wall property bit masks;
- panel/object setup reads byte 1 and checks object-class/property tables;
- collision computes `A69E + 2*(y*64+x)`;
- runtime OBJECT records keep and far pointer to their associated map cell;
- object removal/replacement paths write through that cell pointer.

This is stronger than identifying the block from size alone.

## 5. Six-byte block `DS:6D60..6D65`

The save writer serializes six bytes starting at `6D60` immediately before the 350 x 28-byte OBJECT array at `6D66`. The load routine restores the same six bytes.

AND direct disassembly scan of executable code segments 1–4 finds only two explicit references to the literal address `6D60`:

```text
save: push 6D60, length 6
load: push 6D60, length 6
```

No direct semantic reader/writer was found in those code segments.

Therefore the correct current label is something conservative such as:

```cpp
uint8_t objectRuntimeAux[6]; // persisted, semantics unknown
```

It should not yet be called an object count, player object, sentinel, pointer triple, or padding. Its separate persistence argues against casually dropping it in and faithful save implementation, while the absence of explicit xrefs prevents and stronger semantic claim.

## 6. Four-byte header field from `3:D6C6`

The save writer calls `3:D6C6` and stores its 32-bit result at header offset `+0x31`.

The timing audit identifies `3:D6C6` as the game'with time-reading helper. It returns the game'with current millisecond-like timing source selected by the Win16 timing setup.

Important new boundary from the load routine:

- the four bytes are read into and local variable;
- within the reconstructed save-load function, that local is not subsequently consumed;
- the save-slot validation/listing routine reads the stride plus episode/level metadata but does not use this four-byte field.

With this is best described as and **saved time-source snapshot / tick value**, not as proven gameplay state that is restored. It is also not proven to be and calendar date/time stamp.

Recommended provisional field name:

```cpp
uint32_t saveTimeTick; // source = Time_Read(), restore use not found
```

## 7. Updated save header

```cpp
#pragma pack(push, 1)
struct SaveSlotHeader53 {
    uint32_t slotStrideMarker;   // 0x0000D6E7
    char     name[41];           // +0x04 .. +0x2C
    uint16_t episodeNumber;      // +0x2D, 1-based
    uint16_t levelIndex;         // +0x2F, 0-based
    uint32_t saveTimeTick;       // +0x31, Time_Read() snapshot
};
#pragma pack(pop)
static_assert(sizeof(SaveSlotHeader53) == 0x35);
```

The high-level semantics of the first three fields are now substantially stronger than in Pass 4.

## 8. Updated save payload interpretation

The beginning of the slot can now be documented as:

```text
+0000  0035   SaveSlotHeader53
+0035  2000   live MAP cell payload (64x64 x {wallId,objectId})
+2035  005E   compact gameplay/global block
+2093  0006   persisted object-runtime auxiliary block (meaning open)
+2099  2648   OBJECT runtime table, 350 x 28 B
...           remainder as reconstructed in Pass 4
```

This resolves the largest unnamed block in the save layout.

## 9. Verification

`pass5_verify.py` performs 20 binary/model checks. Result: **20/20 PASS**.

Checks include:

- exact EXE SHA-256;
- MAP seek expression using `7E54 << 13` plus `0x202`;
- 8192-byte read into `A69E`;
- row-major 64x64 cell address expression;
- byte-0 wall-property lookup and byte-1 object-property lookup;
- HUD display of `7E52 : (7E54+1)`;
- episode and level setter byte patterns;
- save/load persistence of `A69E` and `6D60`;
- episode resource-format strings;
- direct `6D60` save/load references.

## 10. Remaining high-value targets

1. Determine the six bytes at `6D60` through indirect-pointer/data-flow analysis or runtime watchpoints.
2. Split the 94-byte `4BE8` gameplay block into exact named fields and identify bytes currently between known globals.
3. Determine whether `saveTimeTick` is used anywhere outside the main load/list routines, especially in restart-at-last-save logic.
4. Trace every mutation of `A69E` to classify persistent map changes: destroyed walls, moved walls, pickups/removals, switches and scripted replacements.