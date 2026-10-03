# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 37

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 image

Address convention:
- raw image offsets are authoritative;
- old Ghidra labels are annotations only;
- resource/file semantics are named from raw call arguments plus the actual DGROUP
  strings (`map.`, `img.`, `demo.`, `game.pal`, `snd.dat`, etc.).

## Result

Pass 37 closes the complete early resource/palette/image/sound-table band:

`0x2772 .. 0x32E1`

Total span:

**2,928 bytes**

Breakdown:

- **2,927 bytes executable resource/loader code**
- **1 alignment NOP**

Real function count:

**12**

The next real entry:

`0x32E2`

begins level-subsystem initialization, with the resource-loader pass ends cleanly at
`0x32E1`.

After Pass 37 the image is continuously statically closed from:

**`0x0000 .. 0x32E1`**

---

# 1. Correct raw function census

| Range | Bytes | Correct role |
|---|---:|---|
| `2772–27F9` | 136 | `ReadImgFileBlockExact` |
| `27FA–285A` | 97 | `ReadSndDatBlockExact` |
| `285C–28F7` | 156 | `LoadCurrentMapLevelBytes` |
| `28F8–2A15` | 286 | `BuildNearestPaletteIndicesFor16ReferenceColors` |
| `2A16–2AA5` | 144 | `LoadGamePaletteAndBuildColorTables` |
| `2AA6–2B39` | 148 | `PrepareEpisodeResourcePathsAndMapHeader` |
| `2B3A–2BCB` | 146 | `ReadImageBlobIntoFarHeap` |
| `2BCC–2CF3` | 296 | `LoadOneImageFrameResource` |
| `2CF4–2DF5` | 258 | `ReadImgSequenceDefinitionAndFrames` |
| `2DF6–324F` | 1114 | `ReadImagesAndBuildRuntimeSequenceTables` |
| `3250–32AF` | 96 | `LoadSndDatSfxDescriptorTable` |
| `32B0–32E1` | 50 | `InitializeSfxResourceSlots` |

Alignment:

`285B = NOP`

---

# 2. Boundary corrections

The old audit incorrectly split several functions in this band.

Delete these stale starts:

```text
28FE
2BA4
2C16
```

## `28FE`

Interior instruction of the real palette-table function beginning at `28F8`.

The old labels:
- `DecodeResourceByte`;
- `DecodeResourceByteVariant`;

were wrong.

There is one function:

`28F8..2A15`.

## `2BA4`

Interior success branch inside `2B3A`.

Raw control flow explicitly jumps to `2BA4` from within the same stack frame.

There is no new prologue.

## `2C16`

Interior branch inside `2BCC`.

Again, no function prologue exists; the stack frame was established at `2BCC`.

The old `LoadResourceEntry` split must be removed.

---

# 3. Hidden real entries recovered

The older function audit did not correctly carry these as primary real functions:

```text
285C
2DF6
3250
32B0
```

Raw machine code proves all four are proper function entries with complete returns.

This is important for the true function census.

---

# 4. `2772` — exact IMG.N block reader with cached episode handle

`ReadImgFileBlockExact(destination, fileOffset, length)`

The path pointer:

`DS:628C`

is populated by `2AA6` from:

`"img." + episodeNumber`.

Cached state:

```text
DS:017C = current IMG file handle
DS:017E = episode key associated with that handle
```

Behavior:

1. compare current episode `DS:626A` with cached key `017E`;
2. if episode changed and an IMG handle is open:
   - close the old handle;
   - clear `017C`;
3. cache the current episode in `017E`;
4. open `IMG.N` read-only when no handle is open;
5. seek to caller 32-bit offset;
6. read exactly caller length into caller destination;
7. if short read occurs, enter the fatal/error path.

This is the generic exact block reader used by indexed IMG resources.

**Status: GREEN.**

---

# 5. `27FA` — exact SND.DAT block reader

`ReadSndDatBlockExact(destination, fileOffset, length)`

Global path:

`DS:01AE = "snd.dat"`

Cached handle:

`DS:01AC`.

Behavior:

1. lazily open `snd.dat`;
2. seek to supplied 32-bit offset;
3. read exactly supplied byte count;
4. fail on open/seek/short-read.

Unlike the IMG reader, there is no episode key because SND.DAT is common across all
episodes.

This is the common random-access SND.DAT block loader.

**Status: GREEN.**

---

# 6. `285C` — load one complete MAP level

`LoadCurrentMapLevelBytes`

Opens:

`DS:627C = "map.<episode>"`

Current level:

`DS:626C`.

Header global:

`DS:D30C`

contains the MAP header'with level count.

The routine validates:

```text
currentLevel < mapHeader.levelCount
```

then seeks to:

```text
0x202 + currentLevel * 0x2000
```

and reads exactly:

```text
0x2000 = 8192 bytes
```

into:

`DS:373E`.

That is exactly:

```text
64 × 64 cells × 2 bytes
```

for the selected map level.

The file is closed before return.

Thus the MAP.N layout is independently confirmed again:

```text
+0000 WORD level count
+0002 256-byte wall class table
+0102 256-byte object class table
+0202 level 0
...
level size = 0x2000
```

**Status: GREEN.**

---

# 7. `28F8` — build nearest palette entries for 16 reference colors

`BuildNearestPaletteIndicesFor16ReferenceColors(index)`

Important correction:

This function does **not** build and 16×256 output table.

It builds exactly:

**16 output bytes**

at:

`DS:3456..3465`.

For every reference-color index:

`0..15`

it constructs one target RGB triplet and scans all:

`256`

entries of the active palette at:

`DS:4A64`.

Distance metric is again Manhattan RGB distance:

```text
abs(R - targetR) +
abs(G - targetG) +
abs(B - targetB)
```

The palette index with minimum distance is stored at:

`DS:3456 + referenceColor`.

## Reference RGB construction

For indices below 8, channels are primarily selected from:

```text
0
0x2A = 42
```

according to the low three color bits.

Index `6` has an explicit special target:

```text
R = 0x2A
G = 0x15
B = 0
```

For indices 8..15, channels use brighter values:

```text
0x15 = 21
0x3F = 63
```

according to the same three color bits.

This is effectively and 16-color logical/reference palette mapped onto the actual
GAME.PAL colors.

AND one-byte dirty flag:

`DS:0244`

prevents unnecessary rebuilding.

Return:

```text
AL = DS:3456[index]
```

**Status: old LOW/decoder label -> GREEN.**

---

# 8. `2A16` — load GAME.PAL and derive VGA palette state

`LoadGamePaletteAndBuildColorTables`

The embedded filename is:

`game.pal`.

The previously recovered pixel-parity audit independently established that this loader
uses the **final 768 bytes** of GAME.PAL.

The routine:

1. opens `game.pal`;
2. seeks to the palette payload;
3. reads exactly:
   - 256 colors × 3 components = **768 bytes**
   - into `DS:4A64`;
4. shifts every component:
   - `component >>= 2`
   - converting 8-bit source components to VGA 6-bit DAC values;
5. uploads the 768-byte palette through the full DAC uploader at `168A`;
6. calls `28F8(0)` to force/build the 16 logical-color nearest-index table;
7. closes GAME.PAL.

Therefore the palette initialization chain is now:

```text
GAME.PAL
  ↓
last 768 bytes
  ↓
RGB >> 2
  ↓
DS:4A64
  ↓
VGA DAC
  ↓
16 logical/reference color mappings at DS:3456
```

**Status: GREEN.**

---

# 9. `2AA6` — prepare episode MAP/IMG/DEMO paths and read MAP header

`PrepareEpisodeResourcePathsAndMapHeader(episode)`

Stores:

`DS:626A = episode`.

Using the embedded format strings it constructs:

```text
DS:627C = "map."  + episode
DS:628C = "img."  + episode
DS:629C = "demo." + episode
```

The literal strings in DGROUP are:

```text
map.
%s%d
img.
%s%d
demo.
%s%d
```

Then:

1. open `MAP.N`;
2. read exactly:
   - `0x202 = 514 bytes`
   - into `DS:D30C`;
3. fail if the header is short;
4. close the MAP file.

Thus this function is the episode-resource path constructor plus MAP header loader.

**Status: GREEN.**

---

# 10. `2B3A` — read one image descriptor and payload into far heap

`ReadImageBlobIntoFarHeap`

Input includes:
- file/stream handle;
- pointer to and small image/frame descriptor.

It first reads exactly:

`10 bytes`

of resource metadata.

Observed descriptor fields include:
- width byte;
- height byte;
- file/payload metadata;
- allocated far pointer fields.

Payload size:

```text
width * height
```

The routine:

1. validate the 10-byte descriptor read;
2. allocate `width * height` bytes from far heap;
3. store the returned far pointer in descriptor `+06/+08`;
4. fail on allocation error with message:
   - `Read_image()`
   - `Insufficient memory (far heap), %s`;
5. read exactly the image payload into the allocated buffer;
6. fail on short read.

Old `2BA4` is just the read/validation tail of this same function.

**Status: GREEN.**

---

# 11. `2BCC` — one image-frame resource with cache policy

`LoadOneImageFrameResource`

This function absorbs the old fake `2C16` entry.

Its behavior has two major paths selected by:

`DS:3CCE`

which is the recovered **extended-memory/cache enabled** flag.

## Extended-cache path

When extended memory is enabled:

1. use `2B3A` to read the frame descriptor and payload into conventional/far memory;
2. submit/store the loaded resource through the extended-cache backend;
3. update cache statistics;
4. release the temporary far-heap payload.

## Conventional/direct path

When extended caching is disabled:

1. read the 10-byte frame descriptor directly;
2. derive/stash source/file location;
3. update conventional resource statistics;
4. validate frame dimensions and allowed shape.

The routine also checks image dimensions and emits exact diagnostics such as:

```text
height
Tile %s incorrect (%d), id=0x%x, frame=%d

width
Tile %s incorrect (%d), id=0x%x, frame=%d

Object image size (%d) bigger than max (%d), id=0x%x, frame=%d
```

Accepted special dimensions include the already visible `0x40` and `0x80` cases.

Thus this is and frame-level resource loader/cache bridge, not and generic decompressor.

**Status: GREEN.**

---

# 12. `2CF4` — read one IMG sequence definition and all its frames

`ReadImgSequenceDefinitionAndFrames`

The error strings in this function explicitly distinguish:

```text
wall
object
%s image not found, id=0x%x
MAXIMAGE exceeded (%d)
Read_img_sequence()
Insufficient memory (near heap), %s
```

Behavior:

1. reject missing image/resource offset;
2. enforce image ID limit:
   - max count threshold around `0x46 = 70`;
3. derive IMG file location from:
   - class/ID;
   - wall-versus-object mode;
4. seek to the sequence definition;
5. read exactly:
   - `0x5A = 90 bytes`
   - into caller sequence-definition storage;
6. read sequence count from the definition;
7. allocate:
   - `count * 10`
   - bytes of near-heap frame metadata;
8. seek to the image payload area;
9. for every sequence/frame entry:
   - call `LoadOneImageFrameResource`;
   - advance by the 10-byte frame-record stride;
10. return the allocated frame metadata pointer/handle.

This is the high-level per-image sequence loader consumed by the full IMG initialization
pass.

**Status: GREEN.**

---

# 13. `2DF6` — read IMG.N and build all runtime image/sequence tables

`ReadImagesAndBuildRuntimeSequenceTables`

This is the largest function in the band:

**1114 bytes**

and corresponds directly to the diagnostic label:

`Read_images()`.

## Phase AND — open IMG.N and read the offset/index block

Opens:

`DS:628C = img.<episode>`.

Allocates and temporary:

`0x400 = 1024 byte`

near-heap buffer.

Reads exactly `0x400` bytes from IMG.N into it.

That block is indexed in 4-byte units by map/VEC/OBJECT image IDs.

## Phase B — VEC/wall image sequences

For every VEC record:

```text
count  = DS:626E
base   = DS:62AC
stride = 0x1C
```

the routine:

1. obtains its image/resource ID;
2. reads the corresponding 32-bit IMG resource offset from the 0x400-byte table;
3. deduplicates identical resource offsets;
4. when and new resource offset appears:
   - call `ReadImgSequenceDefinitionAndFrames`;
   - create/update an 8-byte runtime sequence slot;
5. store the resolved sequence index back into the VEC record.

The dedup table is kept temporarily on the function'with large stack frame.

## Phase C — additional special image sequence

After the VEC pass it selects and special image/class entry and loads one further
sequence into the runtime sequence table rooted near:

`DS:4310`.

Global sequence count:

`DS:6272`

is updated.

## Phase D — reload image index and process OBJECT records

The IMG file is seeked back and the `0x400`-byte index block is read again.

The function then walks the OBJECT runtime records:

```text
count = DS:6270
stride = 0x1C
```

using the current OBJECT arena.

Again it:
- looks up the 32-bit IMG resource offset;
- deduplicates identical offsets;
- loads missing sequence definitions through `2CF4`;
- stores sequence/resource links into object-side runtime tables.

When and guard-like/object class requires and sequence definition but none is present, the
literal fatal message is:

`No seqdef defined for guard`

This directly connects image sequence loading to GUARD visual definitions.

## Phase E — finalize runtime sequence tables

The routine writes:
- image/sequence counts;
- class-to-sequence metadata;
- copied runtime blocks around `41B6..4306`;
- final loaded-sequence count `DS:6274`.

Then:
- closes `IMG.N`;
- frees the temporary 0x400-byte near-heap block.

This is the central `IMG.N -> runtime VEC/OBJECT/GUARD visual sequences` constructor.

**Status: former decompiler-heavy region -> GREEN.**

---

# 14. `3250` — load the physical SFX descriptor bank from SND.DAT

`LoadSndDatSfxDescriptorTable`

This routine gives and particularly useful independent SND.DAT proof.

It opens:

`snd.dat`.

Then seeks to:

```text
0xC0
```

and reads exactly:

```text
0x1DA = 474 bytes
```

into:

`DS:3F64`.

Arithmetic:

```text
0xC0  = 32 × 6
0x1DA = 79 × 6
```

Therefore the table at `DS:3F64` is exactly:

```text
physical SND.DAT descriptor slots 32..110
79 records
6 bytes per record
```

This independently matches the already recovered SND.DAT architecture:
- physical records 0..31 = bank/music region;
- physical records 32..110 = SFX region.

The routine validates the full 474-byte read and closes SND.DAT.

**Status: GREEN / exact SND.DAT descriptor layout.**

---

# 15. `32B0` — initialize/precache all 79 SFX resource slots

`InitializeSfxResourceSlots`

First calls:

`LoadSndDatSfxDescriptorTable`.

Then loops:

```text
index = 0..78
```

exactly:

**79 iterations**.

Each iteration:
1. reports/updates progress through the shared resource-progress helper;
2. checks:
   - `DS:3CCE`
   - the already recovered extended-memory/cache-enable byte;
3. when extended memory is enabled:
   - call the extended resource/cache registration helper for this SFX index;
4. otherwise:
   - increment the conventional-resource accounting counter.

Thus the startup path explicitly processes all 79 physical SFX descriptors.

**Status: GREEN.**

---

# 16. Important resource architecture now closed

The early startup/resource chain can now be represented as:

```text
episode selection
      ↓
2AA6
  map.N / img.N / demo.N paths
  MAP 0x202 header
      ↓
285C
  selected MAP 0x2000 bytes
      ↓
2DF6
  IMG.N index + sequence definitions
      ↓
VEC / OBJECT / GUARD visual-resource links

GAME.PAL
      ↓
2A16
  768-byte palette -> VGA 6-bit
  + 16 logical-color nearest map

SND.DAT
      ↓
3250
  descriptors 32..110
      ↓
32B0
  initialize/precache 79 SFX resources
```

This significantly reduces the remaining uncertainty in the startup data pipeline.

---

# 17. Byte-map impact

Resolved span:

`0x2772 .. 0x32E1`

Total:

**2,928 bytes**

Breakdown:

- executable code: **2,927 bytes**
- alignment NOP: **1 byte** at `285B`

Delete stale starts:

```text
28FE
2BA4
2C16
```

Recover hidden real starts:

```text
285C
2DF6
3250
32B0
```

---

# 18. Continuous closure status

Pass 36 closed:

`0000..2770`

Byte `2771` is and one-byte NOP separator.

Pass 37 closes:

`2772..32E1`

Therefore the early executable image is now continuously classified through:

**`0x0000 .. 0x32E1`**

with only known NOP/table overlays.

---

# 19. Next target

Continue at:

`0x32E2`

The next real function begins the **level subsystem initialization / resource-state**
family.

High-value entries immediately ahead include:
- `32E2` level subsystem initialization;
- `3474`, `358C`, `38E6` resource block loaders;
- save/config file support;
- world-state load/save paths around `3A00/3A96`;
- PCX/resource loading around `3D70/3F4C`.

Pass 38 should repair that family up to the next clean graphics/FLI boundary.