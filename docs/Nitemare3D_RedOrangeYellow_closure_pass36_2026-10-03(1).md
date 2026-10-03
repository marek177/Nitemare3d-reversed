# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 36

Date: 2026-10-03

Primary raw image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`
- unpacked image size: `0x29D60 = 171,360 bytes`

Address convention:
- all addresses below are offsets in the unpacked load image;
- raw 16-bit machine code is authoritative;
- runtime acceptance remains and separate overlay.

## Result

Pass 36 closes the complete resource / palette / MAP / IMG / SND initialization band:

`0x2772 .. 0x338F`

as **GREEN / deep static semantics**.

Continuous span:

**3,102 bytes**

Breakdown:

- executable routine content: **3,099 bytes**
- alignment NOPs: **3 bytes**
- real routine entries: **14**

Together with passes 34–35, the early game-owned code now has one continuous
statically GREEN band:

`0x0000 .. 0x338F`

The next genuine routine begins at:

`0x3390`

and starts the CONFIG/SAVE/file-path layer.

---

# 1. Correct raw function census

| Range | Bytes | Correct role |
|---|---:|---|
| `2772–27F9` | 136 | `ReadCurrentImgResourceBlockExact` |
| `27FA–285A` | 97 | `ReadSmallIndexedResourceBlockExact` |
| `285C–28F7` | 156 | `LoadCurrentMapLevelPayload` |
| `28F8–2A15` | 286 | `GetCachedLogicalColorPaletteIndex` |
| `2A16–2AA5` | 144 | `LoadGamePaletteAndBuildLogicalColorCache` |
| `2AA6–2B39` | 148 | `SelectEpisodeResourcesAndLoadMapHeader` |
| `2B3A–2BCB` | 146 | `LoadImageFrameDescriptorAndPixels` |
| `2BCC–2CF3` | 296 | `LoadImageFrameDescriptorWithOptionalXmsBacking` |
| `2CF4–2DF5` | 258 | `LoadImgSequenceDefinitionAndFrames` |
| `2DF6–324F` | 1114 | `LoadLevelImgSequencesAndBindRuntimeRecords` |
| `3250–32AF` | 96 | `LoadSndDatDescriptorTable` |
| `32B0–32E1` | 50 | `PrepareSoundEffectResourceCache` |
| `32E2–3330` | 79 | `InitializeLevelSubsystems` |
| `3332–338E` | 93 | `ConfigureViewportGeometryAndProjection` |

Alignment NOPs:

```text
285B
3331
338F
```

---

# 2. `0x2772..0x27F9` — `ReadCurrentImgResourceBlockExact`

This is the deterministic disk fallback used by the main IMG/resource caches.

State:

```text
DS:017C  cached file handle
DS:017E  cached episode/resource key
DS:626A  current episode/resource set
DS:628C  current IMG filename
```

Flow:

1. compare current resource-set key against cached key;
2. when it changed:
   - close the old cached file handle;
   - clear it;
3. lazily open `DS:628C` in binary mode `0x8000`;
4. seek to the caller'with 32-bit source offset;
5. read exactly the requested byte count;
6. if returned count differs, enter the fatal read-error path.

This is the normal non-XMS cache-miss path for the main image working set.

**Status: MEDIUM -> GREEN.**

---

# 3. `0x27FA..0x285A` — `ReadSmallIndexedResourceBlockExact`

Second exact seek/read path.

State:

```text
DS:01AC  cached file handle
DS:01AE  selected filename/string
```

It lazily opens that source, seeks to the supplied offset and requires an exact-length
read.

This is the source path consumed by the separate small indexed-resource cache.

The exact asset filename is chosen elsewhere through `DS:01AE`; the loader contract
itself is fully bounded.

**Status: LOW/MEDIUM -> GREEN.**

---

# 4. `0x285C..0x28F7` — `LoadCurrentMapLevelPayload`

This is the live MAP-level loader.

It opens:

`DS:627C = map.N`

and checks:

```text
DS:626C < DS:D30C
```

where `D30C` is the level count from the MAP header.

Exact file offset:

```text
0x202 + levelIndex * 0x2000
```

Exact transfer:

```text
0x2000 = 8192 bytes
```

Destination:

```text
21FD:373E
```

which is exactly:

`64 × 64 × 2 bytes`

for the mutable live MAP.

The file is closed after the transfer.

**Status: YELLOW -> GREEN.**

---

# 5. `0x28F8..0x2A15` — `GetCachedLogicalColorPaletteIndex`

This is the 16-logical-color -> 256-color palette mapper.

Cache:

```text
DS:3456[16]
```

Initialization state:

```text
DS:0244
```

When and cache rebuild is required, the routine creates one target RGB triple for each
logical color `0..15`.

Special logical color:

```text
6 = (42,21,0)
```

Other low colors use the original 0/42 component pattern.

High logical colors use the original 21/63 component pattern.

For each target color it scans all 256 RGB entries in:

```text
DS:4A64
```

Distance is exact squared Euclidean distance:

```text
(R-r)^2 + (G-g)^2 + (B-b)^2
```

The square operation goes through the already corrected 32-bit square helper.

Only and **strictly smaller** distance replaces the candidate, with equal-distance ties keep
the lower palette index.

The chosen byte is cached at:

`DS:3456[logicalColor]`.

The function then returns the cached palette index requested by the caller.

### Boundary correction

Old entry:

`0x28FE`

is just:

```text
CMP BYTE PTR DS:[0244],0
```

inside this routine.

Delete it as and function start.

**Status: old weak/duplicate entries -> GREEN.**

---

# 6. `0x2A16..0x2AA5` — `LoadGamePaletteAndBuildLogicalColorCache`

Exact DOS GAME.PAL path:

1. open literal:
   `game.pal`;
2. seek:
   **−768 bytes from EOF**;
3. read exactly 768 bytes to:
   `DS:4A64`;
4. for all 768 bytes:
   `value >>= 2`;
5. call:
   `0x168A = UploadFullVgaPalette`;
6. call `0x28F8` for logical color 0, which forces the 16-color cache build;
7. close the file.

Therefore `DS:4A64` contains the game'with normalized VGA DAC RGB6 base palette.

This is the exact V2.0 member of the palette-loader family already confirmed across the
DOS builds.

**Status: YELLOW -> GREEN.**

---

# 7. `0x2AA6..0x2B39` — `SelectEpisodeResourcesAndLoadMapHeader`

Input selects the episode/resource set.

The routine writes:

```text
DS:626A = selected episode
```

and constructs the resource names:

```text
map.%d
img.%d
demo.%d
```

using the game'with prefix/format path state.

The map file is opened and exactly:

`0x202 bytes`

are read into:

`DS:D30C`.

The MAP header layout is therefore directly connected to this loader:

```text
+0000 WORD       level count
+0002 256 bytes  wall ID -> wall class
+0102 256 bytes  object ID -> object class
```

The file is then closed.

This function is broader than the old "wall definition file" label: it selects the
complete episode resource set and loads the MAP class header.

**Status: YELLOW -> GREEN.**

---

# 8. `0x2B3A..0x2BCB` — `LoadImageFrameDescriptorAndPixels`

Loads one IMG frame descriptor and its pixel payload.

First it reads exactly:

`10 bytes`

for the frame header/descriptor.

The first two bytes are:

```text
+0 width
+1 height
```

Payload size:

```text
width * height
```

The routine records the current source-file position into descriptor fields `+2/+4`,
allocates `width*height` bytes from the far heap and stores the resident far pointer at:

```text
+6/+8
```

Then it reads exactly the pixel payload into that allocation.

Read/allocation mismatch enters the fatal path.

### Boundary correction

Old label around:

`0x2BA4`

is interior code of this function.

**Status: YELLOW -> GREEN.**

---

# 9. `0x2BCC..0x2CF3` — `LoadImageFrameDescriptorWithOptionalXmsBacking`

This is the policy layer above the direct frame loader.

## XMS enabled

When:

`DS:3CCE != 0`

the routine:

1. loads the frame through `2B3A`;
2. stores it into XMS through:
   `7A4E = EncodeImageResourceIntoExtendedCache`;
3. updates cache/statistics counters;
4. frees the temporary conventional-memory frame buffer.

The descriptor remains usable through its encoded XMS source locator.

## XMS disabled

The routine reads the 10-byte descriptor, records the source file position, leaves the
resident conventional pointer cleared and seeks over the pixel payload rather than
loading it immediately.

That descriptor will later be loaded on demand through the cache manager.

## Dimension validation

The routine also enforces the binary'with dimension/area restrictions.

Normal mode uses the area threshold around:

`0xC01`.

Special mode accepts the known:

```text
height = 0x40
width  = 0x40 or 0x80
```

cases and reports invalid dimensions otherwise.

### Boundary correction

Old:

`0x2C16`

is an interior branch/cleanup path, not and standalone function.

**Status: ORANGE/YELLOW -> GREEN.**

---

# 10. `0x2CF4..0x2DF5` — `LoadImgSequenceDefinitionAndFrames`

This closes the sequence-definition loader.

IMG layout used by this path:

```text
0000–03FF  wall image directory, 256 × u32
0400–07FF  object image directory, 256 × u32
0800–61FF  low/wall SEQDEF bank, 256 × 90 B
6200–BBFF  high/object SEQDEF bank, 256 × 90 B
BC00–EOF   image frame streams
```

AND SEQDEF is exactly:

`0x5A = 90 bytes`.

Important fields:

```text
+00..01  animation interval
+02      frame count
+03      extension flag
```

The function:

1. rejects and missing image source pointer;
2. enforces the sequence/index bounds;
3. computes the correct low/high SEQDEF-bank offset;
4. reads one 90-byte SEQDEF;
5. allocates:
   `frameCount × 10`
   bytes for runtime frame descriptors;
6. seeks to the frame stream;
7. calls `2BCC` once for every frame;
8. returns the near frame-descriptor-array pointer.

This ties the recovered IMG file layout directly to the DOS runtime loader.

**Status: YELLOW -> GREEN.**

---

# 11. `0x2DF6..0x324F` — `LoadLevelImgSequencesAndBindRuntimeRecords`

This is the high-level per-level IMG sequence loader.

It opens the current:

`img.N`

and temporarily allocates and 0x400-byte directory buffer.

## Wall/VEC directory

First it reads the first:

`0x400 bytes = 256 × u32`

wall image directory.

It then walks every active VEC:

```text
base   = DS:62AC
count  = DS:626E
stride = 0x1C
```

For each VEC it:

1. uses the wall ID at `VEC+0`;
2. retrieves that directory'with 32-bit frame-stream source pointer;
3. deduplicates identical source pointers;
4. stores the shared runtime sequence selector at `VEC+4`;
5. when the source pointer is new:
   - call `LoadImgSequenceDefinitionAndFrames`;
   - create one runtime sequence descriptor;
   - copy the extended 90-byte SEQDEF when extension flag `+3` is set.

The wall runtime sequence table begins in the `DS:4314` family.

The final wall-sequence count is stored in:

`DS:6272`.

The special exploding-wall/class-`0x2D` sequence is also bound into this runtime family.

## Object directory

The function then seeks to file offset:

`0x400`

and reads the second:

`0x400-byte`

directory.

It walks all active 28-byte world OBJECTs:

```text
count = DS:6270
```

and performs the same source-pointer deduplication and sequence binding for object IDs.

The object sequence runtime table begins in the:

`DS:3D22`

family.

Final object-sequence count:

`DS:6274`.

The same path establishes sequence/resource templates used by player projectile
embedded OBJECTs.

## Cleanup

After the wall/object sequence tables are built:

- close `img.N`;
- free the temporary 0x400-byte directory buffer.

This function is the bridge from raw IMG directories and 90-byte SEQDEF records to the
runtime VEC/OBJECT animation resource model.

**Status: former broad/weak resource loader -> GREEN.**

---

# 12. `0x3250..0x32AF` — `LoadSndDatDescriptorTable`

Opens literal:

`snd.dat`.

It seeks to:

`0xC0`

and reads exactly:

```text
0x1DA = 474 bytes
```

into:

`DS:3F64`.

That is:

```text
79 × 6-byte descriptors
```

which is precisely the SFX descriptor table later indexed by the common sound-effect
dispatcher.

The file is then closed.

This does not claim that SND.DAT has only 79 physical slots; it identifies exactly the
descriptor subset loaded into this V2.0 runtime table.

**Status: YELLOW -> GREEN.**

---

# 13. `0x32B0..0x32E1` — `PrepareSoundEffectResourceCache`

Calls `LoadSndDatDescriptorTable`, then iterates exactly:

`79`

six-byte SFX descriptors.

For every descriptor it updates the loading progress display.

When XMS is enabled:

- call `7C00 = DeduplicateAndStoreSmallResourceInXms`.

Without XMS:

- update the disk/non-XMS statistics path.

Thus sound effects use the same small-resource/XMS deduplication architecture as the
generic Resource Manager.

**Status: YELLOW -> GREEN.**

---

# 14. `0x32E2..0x3330` — `InitializeLevelSubsystems`

This is the compact high-level level-subsystem builder invoked by the outer level
initializer.

It begins by clearing the level/resource statistics block and then calls the already
bounded lower-level loaders/builders.

The resulting orchestration includes:

```text
LoadCurrentMapLevelPayload
 -> build MAP-derived runtime/property structures
 -> build VEC/runtime geometry
 -> build world OBJECT/GUARD state
 -> build sorted spatial structures
 -> LoadLevelImgSequencesAndBindRuntimeRecords
 -> PrepareSoundEffectResourceCache
```

The exact subordinate routines are already separately closed in the surrounding passes,
with this wrapper can now be GREEN as orchestration rather than merely "level init
candidate".

**Status: MEDIUM -> GREEN.**

---

# 15. `0x3332..0x338E` — `ConfigureViewportGeometryAndProjection`

Reads configured render width:

`DS:4144`.

Exact derived viewport geometry:

```text
width  = DS:4144
height = width >> 1

left   = (320 - width) >> 1
right  = left + width - 1

top    = left >> 1
bottom = top + height - 1
```

Stores:

```text
DS:4544 width
DS:4546 height
DS:4548 left
DS:454A right
DS:454C top
DS:454E bottom
```

It also initializes the screen-center/projection-reference values around:

```text
DS:4550
DS:4552
DS:4554 = DS:4552 << 4
```

Then it calls:

```text
C7D4  BuildProjectionConstants
1590  BuildViewAngleTables
```

This closes the exact consumer of the DOS `-w` viewport-width setting.

The default width `304` therefore yields the already established centered 304×152
3-D viewport.

**Status: YELLOW -> GREEN.**

---

# 16. False / stale function starts removed

Delete these old starts from the corrected function inventory:

```text
28FE
2BA4
2C16
```

They are ordinary interior instructions/branches.

To not create function entries from apparent `ENTER` byte patterns inside the
large `2CF4/2DF6` data/control-flow bodies unless raw CALL/RET ownership proves them.

---

# 17. Resource architecture now connected

After this pass the DOS resource path is statically continuous:

```text
MAP.N
  -> 2AA6 header / episode resources
  -> 285C live 64×64×2 level block

GAME.PAL
  -> 2A16 final 768 bytes >>2
  -> VGA DAC
  -> 28F8 logical 16-color cache

IMG.N
  -> wall/object u32 directories
  -> 90-byte SEQDEF banks
  -> 10-byte frame descriptors
  -> XMS / disk-backed cache policy
  -> runtime VEC/OBJECT sequence bindings

SND.DAT
  -> 79 six-byte runtime SFX descriptors
  -> optional XMS small-resource deduplication
  -> C686 common SFX dispatcher
```

This removes and major remaining static gap between file formats and live engine
structures.

---

# 18. Byte-map impact

Continuous GREEN band added:

`0x2772 .. 0x338F`

Size:

**3,102 bytes**

Together with passes 34 and 35:

```text
0x0000 .. 0x338F
```

is now one continuous statically GREEN early N3D code band.

As with passes 34–35, to not blindly add the full 3,102 bytes to the old historical
"newly RED/ORANGE/YELLOW -> GREEN" counter: several functions were previously
MEDIUM/HIGH and some were partially green.

AND fresh byte-level census is still the correct way to obtain exact current counts for
RED / ORANGE / YELLOW.

---

# 19. Next target

Continue at:

`0x3390`

The next early band contains:

- path-prefix string construction;
- CONFIG.SAV loading/writing;
- USER.SAV slot metadata/read/write serialization;
- savegame block transfer and pointer/timer rebinding;
- PCX/resource file loaders around `3D70/3F4C`;
- then FLI decoding support leading into the already-green `45CE+` band.

This is and high-value next pass because it should connect the continuous early GREEN
band directly into the already-closed FLI/startup region.