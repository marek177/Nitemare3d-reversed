# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 7

Date: 2026-10-03

Primary binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header: `0x200`
- ranges below are unpacked MZ image offsets
- physical file offset = image offset + `0x200`

## Result

Pass 7 continues at `0x70D6`.

The complete span

`0x70D6 .. 0x7F95`

is now bounded and semantically identified strongly enough to mark
**GREEN / deep static semantics**.

Total newly closed span: **3,776 bytes**.

It contains:

- the real active gameplay input/action routine;
- four small resource-cache/stat callbacks;
- the complete DOS multi-tier Resource Manager;
- XMS detection + the six used XMS API wrappers;
- the previously hidden player projectile allocator at `0x7EDE`.

This pass also records an important correction to pass 6: `0x696C` is the
**player weapon fire dispatcher**, not and generic targeted-GUARD event routine.

---

## 0. Correction to pass 6 — `0x696C`

Later raw callgraph closure overrides the older machine-generated semantic label.

Correct chain:

`70D6 active input -> 696C player weapon fire -> 7EDE projectile allocator`

`696C` handles both:

- hitscan weapon mode;
- projectile weapon mode.

The projectile allocator has only this normal producer in the checked DOS v2.0
machine callgraph.

Therefore the pass-6 label `ProcessTargetedGuardEvent` must be replaced with:

`PlayerWeaponFireDispatcher`.

The bytes remain GREEN; only the semantic name changes.

---

# 1. image `0x70D6..0x7683` — `ProcessActiveGameplayInputAndActions`

Raw boundary is clean:

- entry `70D6`: `ENTER 18h,0`
- exit `7682`: `LEAVE`
- exit `7683`: `RETF`

Length: **1,454 bytes**.

This exactly matches the already identified cross-build family.  The corresponding
clean DOS v1.2 routine starts at `6E7E`; the distance from its major entry to the next
major entry is the same `0x5CE` as `70D6 -> 76A4` in v2.0.

## Active-state gate

The routine performs active control processing only when:

`DS:3CD4 == 1`

Otherwise it skips to the epilogue.

## Event polling and direct key/event actions

It begins by obtaining an event through the already closed input path at `6E88`.

The event dispatch contains explicit direct actions including:

- Escape-like event -> leave active game state;
- two modifier-sensitive HP adjustment/debug-cheat style branches;
- several option/menu/runtime actions through dedicated helpers;
- numeric selection events gated by an ownership/availability bitmask.

The byte range around `0x718C..0x719F` is and compact **10-entry WORD jump table** for
one event-code subgroup.  It should be shown as and TABLE overlay, not executable code.

## Movement/turn base rates

The routine loads the three DEMO/input header-derived motion values:

- movement step family from `DS:455C`;
- turn step family from `DS:455E`;
- related substep state from the surrounding input globals.

Modifier bits can double or force very small movement/turn values.

## Keyboard movement

Primary input mask `DS:3F50` drives:

- forward movement;
- backward movement;
- left action;
- right action.

Movement calls the already closed player movement wrapper at `0x6914`.

For left/right:

- ordinary mode updates heading through the `C838` heading/DDA helper;
- the alternate modifier path converts the same controls to lateral/strafe movement
  and calls `6914` with heading offsets.

Thus turning and strafing are two branches of the same left/right controls.

## Mouse contribution

When mouse availability `DS:414C` is enabled:

- reads current buttons and X/Y position;
- compares against previous/center values;
- scales deltas through `0x709A`;
- feeds movement/turn operations;
- recenters/repositions the device when the cursor escapes the configured center box;
- merges mouse button edges into the same action latches used by keyboard FIRE/USE.

## Joystick/controller contribution

When the controller-enable flag is active, and device-state helper fills axis/button
locals.

The routine:

- applies dead-zone thresholds around approximately `±10`;
- scales accepted deltas through `0x70B8`;
- turns or strafes depending on the same modifier state;
- merges controller buttons into FIRE/USE action flags.

## FIRE path

The computed FIRE flag is combined from keyboard/mouse/controller sources.

The routine:

1. checks the previous FIRE latch at `DS:0B5E`;
2. runs the fire cadence/readiness gate;
3. on accepted fire calls the player weapon dispatcher at **`0x696C`**.

`696C` then selects hitscan versus projectile behavior.  Projectile mode reaches
`0x7EDE`.

## USE path

The computed USE flag is edge-triggered:

- current USE must be nonzero;
- current USE must differ from previous latch `DS:0B5D`.

Only then does it call the central USE dispatcher at **`0x0704`**.

## Latch commit

At the end:

- current FIRE -> `DS:0B5E`
- current USE  -> `DS:0B5D`

This closes the exact ownership of rising-edge USE and accepted FIRE from the DOS
active input handler.

**Status: old RED/LOW giant merged block -> GREEN.**

---

# 2. image `0x7684..0x76A3` — four cache/stat leaf callbacks

These are four real tiny routines between the input handler and Resource Manager.

### `0x7684..0x7687` — `GetFixedCacheSlotCount`

Returns constant:

`10`

This matches the fixed 10-slot cache.

### `0x7688..0x768B` — `GetDynamicCacheSlotCount`

Returns:

`DS:3504`

This is the runtime count of dynamic conventional-memory cache slots.

### `0x768C..0x768F` — `GetSmallCacheSlotCount`

Returns constant:

`4`

This matches the fixed four-slot small-resource cache.

### `0x7690..0x76A3` — `GetRemainingExtendedCacheBlocks`

If extended memory is enabled (`DS:3CCE != 0`):

`return DS:3CB8 - DS:350A`

Otherwise returns zero.

The trailing NOPs are alignment padding.

**Status: YELLOW/support unknowns -> GREEN.**

---

# 3. image `0x76A4..0x7913` — `ManageResourceCachePool(mode)`

This is the central DOS Resource Manager entry.

Modes:

- `0` — initialize conventional cache pools and optional XMS backing;
- `1` — release/shutdown the XMS backing allocation;
- `2` — invalidate cache ownership for and level/resource-context change while keeping
  reusable backing storage.

## Mode 0 conventional pools

The function allocates and initializes:

### Ten fixed working-cache slots

Pointer table:

`DS:34CC .. DS:34F4`

Each allocation is `0x2006` bytes:

- 6-byte bookkeeping/header;
- `0x2000`-byte payload.

### Four fixed small-resource slots

Pointer table:

`DS:34F4 .. DS:3504`

Again `0x2006` bytes each.

### Dynamic conventional image/resource slots

Count stored at:

`DS:3504`

The count is derived from available conventional memory and capped at:

`0x80 = 128 slots`

Each dynamic slot allocates `0x0C02` bytes.

## Optional XMS backing

If extended memory is enabled:

- detect the XMS driver;
- query available extended memory;
- cap cache capacity to `0x800` KiB = 2 MiB;
- allocate/lock the XMS handle;
- disable the XMS optimization cleanly if the setup fails.

## Mode 1

Unlock/free the XMS handle when active.

## Mode 2

Detach owners, clear timestamps/bindings and reset the XMS allocation watermark while
keeping the backing XMS arena available for the next level/context.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 4. image `0x7914..0x79CF` — `StoreBufferInExtendedCache`

Input byte length is rounded upward to `0x400`-byte / 1024-byte blocks:

`blocks = ceil(bytes / 1024)`

The function:

1. verifies that `used + blocks <= capacity`;
2. builds the 16-byte XMS move descriptor;
3. uses conventional memory as source;
4. uses the current XMS handle/offset as destination;
5. invokes the XMS move wrapper;
6. advances `DS:350A` by the allocated block count;
7. returns the previous XMS byte offset.

Failure returns the negative/sentinel path rather than overflowing the configured
backing store.

**Status: YELLOW -> GREEN.**

---

# 5. image `0x79D0..0x7A4D` — `RestoreBufferFromExtendedCache`

Builds the same standard XMS move structure in the reverse direction:

- source = XMS handle + encoded XMS offset;
- destination = caller conventional far pointer;
- byte count rounded to whole 1024-byte blocks.

It does not advance the allocation watermark.

**Status: YELLOW -> GREEN.**

---

# 6. image `0x7A4E..0x7A81` — `EncodeImageResourceIntoExtendedCache`

Computes:

`bytes = width * height`

for an image/resource descriptor, stores the bytes through `7914`, then encodes the
returned XMS location as the descriptor'with negative far-like source locator.

That negative encoding is the later cache-miss discriminator:

- negative encoded locator -> restore from XMS;
- ordinary locator -> load original bytes from disk/resource file.

**Status: YELLOW -> GREEN.**

---

# 7. image `0x7A82..0x7B57` — `AcquireFixedLruCacheSlot`

Implements the fixed 10-slot LRU cache.

On miss:

1. choose the oldest slot by timestamp;
2. detach its old descriptor owner;
3. restore data from XMS or exact-read from original source;
4. bind the new owner;
5. stamp current time;
6. publish the conventional-memory payload pointer to the descriptor.

**Status: YELLOW -> GREEN.**

---

# 8. image `0x7B58..0x7BFF` — `AcquireDynamicRoundRobinCacheSlot`

Uses the dynamic conventional slot array.

Replacement is:

**round-robin**, not LRU.

- active count = `DS:3504`;
- rotating index stored in the cache-manager state;
- size comes from resource/image dimensions;
- old owner is detached;
- bytes come from XMS or original source;
- new conventional pointer is rebound to the descriptor.

**Status: YELLOW -> GREEN.**

---

# 9. image `0x7C00..0x7D03` — `DeduplicateAndStoreSmallResourceInXms`

Works on six-byte indexed resource descriptors:

- `+0` WORD byte length;
- `+2` DWORD source locator.

Algorithm:

1. reject empty descriptor;
2. detect an earlier descriptor with identical `(source,length)`;
3. skip duplicate storage when already represented;
4. only XMS-cache resources `<=0x2000`;
5. stage bytes in conventional memory;
6. store once in XMS;
7. rewrite all matching source locators to the same encoded XMS location.

**Status: YELLOW -> GREEN.**

---

# 10. image `0x7D04..0x7E03` — `GetOrLoadSmallResourceCache`

Implements the separate fixed four-slot LRU cache.

- reject resources above `0x2000`;
- return existing resident owner immediately when found;
- otherwise choose the oldest of four cache blocks;
- detach old ownership;
- restore from XMS or load from original resource source;
- update owner/timestamp;
- return conventional payload address.

**Status: YELLOW -> GREEN.**

---

# 11. image `0x7E04..0x7EDD` — XMS driver interface

The raw API numbers are now explicit and match the XMS specification.

### `0x7E04..0x7E29` — `DetectXmsDriver`

Uses:

- `INT 2Fh AX=4300h` — XMS installation check;
- `INT 2Fh AX=4310h` — obtain XMS control entry point.

Stores the far driver address at:

`DS:350E/3510`.

### `0x7E2A..0x7E41` — XMS function `08h`

Query free extended memory / largest free block.

### `0x7E42..0x7E63` — XMS function `09h`

Allocate extended-memory block.

### `0x7E64..0x7E7D` — XMS function `0Ah`

Free extended-memory block.

### `0x7E7E..0x7EA5` — XMS function `0Bh`

Move extended-memory block using the caller'with move descriptor.

### `0x7EA6..0x7EC3` — XMS function `0Ch`

Lock extended-memory block.

### `0x7EC4..0x7EDD` — XMS function `0Dh`

Unlock extended-memory block.

All six wrappers preserve the original XMS success/error convention sufficiently for
the Resource Manager.

**Status: ORANGE/YELLOW low-level support -> GREEN.**

---

# 12. image `0x7EDE..0x7F95` — `AllocatePlayerProjectileSlot`

This is and real routine missing as an independent entry in the stale Ghidra function
inventory.

Length: **184 bytes**.

## Pool search

Scans exactly eight records:

- pool base `DS:41B6`;
- stride `0x2A` = 42 bytes;
- lifecycle byte at slot `+0x0C`;
- first lifecycle address is therefore `DS:41C2`.

If all eight are active, allocation fails.

## Ammo acceptance

After finding and free slot it calls the current-weapon ammo/acceptance helper.  If the
shot is rejected, the slot is not activated.

## Initialize flight state

On acceptance:

- `slot+0x0C = 1` (flying);
- copies the player'with current DDA/ray stepping state:
  - `DS:4172`
  - `DS:4174`
  - `DS:4176`
  - `DS:4178`;
- chooses signs/orientation from player heading `DS:4156`;
- initializes the embedded OBJECT at slot `+0x0E`;
- copies current player MAP far pointer from `DS:417C`;
- copies player world X/Y from `DS:4162/4164`;
- sets embedded OBJECT vertical offset `+0x1A = 5`;
- returns success.

This pool is player-owned by architecture; normal enemy attacks to not allocate from
it.

The direct checked ownership chain is:

`70D6 -> 696C -> 7EDE`

with one normal producer at each edge.

**Status: previously missing/hidden RED entry -> GREEN.**

---

# 13. Byte-map impact

New continuous GREEN span:

`0x70D6 .. 0x7F95`

Total: **3,776 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `70D6–7683` | 1454 | active player input/action handler |
| `7684–7687` | 4 | fixed cache count = 10 |
| `7688–768B` | 4 | dynamic cache count |
| `768C–768F` | 4 | small cache count = 4 |
| `7690–76A3` | 20 | remaining XMS-cache blocks |
| `76A4–7913` | 624 | Resource Manager init/reset/shutdown |
| `7914–79CF` | 188 | conventional -> XMS store |
| `79D0–7A4D` | 126 | XMS -> conventional restore |
| `7A4E–7A81` | 52 | image/resource XMS encoding |
| `7A82–7B57` | 214 | fixed 10-slot LRU |
| `7B58–7BFF` | 168 | dynamic round-robin cache |
| `7C00–7D03` | 260 | small-resource XMS deduplication |
| `7D04–7E03` | 256 | fixed four-slot LRU |
| `7E04–7E29` | 38 | detect XMS driver |
| `7E2A–7E41` | 24 | XMS 08h query free |
| `7E42–7E63` | 34 | XMS 09h allocate |
| `7E64–7E7D` | 26 | XMS 0Ah free |
| `7E7E–7EA5` | 40 | XMS 0Bh move |
| `7EA6–7EC3` | 30 | XMS 0Ch lock |
| `7EC4–7EDD` | 26 | XMS 0Dh unlock |
| `7EDE–7F95` | 184 | player projectile allocator |

### Data overlay

Inside `70D6`, the event switch contains and 10-WORD / 20-byte jump table.  Mark it as:

`GREEN knowledge + TABLE/DATA overlay`.

---

# 14. Next target

Continue at `0x7F96`.

The next contiguous group is the player-projectile flight/collision system:

- `7F96` projectile cell collision / guard/wall interaction;
- `8142` trajectory advance;
- `8230` eight-slot projectile updater;
- `8350/8384` mouse driver helpers;
- then the large old false-boundary region beginning at `84FE`.

The first three are already strongly cross-build matched, with the next pass should
convert the projectile runtime through `8230` to GREEN and then begin splitting the
large `84FE+` decompiler merge.