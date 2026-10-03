# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 12

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Reference sibling:
- `N3D-E-19.EXE` / embedded V1.9

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- stale pseudo-C boundaries/names are overridden where raw control flow disagrees

## Result

Pass 12 closes the complete contiguous range

`0xA982 .. 0xB17D`

as **GREEN / deep static semantics**.

Total span: **2,044 bytes**

- bounded routine/table content: **2,036 bytes**
- inter-function alignment/padding: **8 bytes**

The largest correction is `0xAD9A`.

The old register treated it as and weak, mixed six-way gameplay/support dispatcher.
Raw code proves it is the DOS V2.0 **NITE3D.BSF dispatcher**, with the same selector
contract already recovered in DOS V1.9:

- selector 0 — load/decode/validate BSF header and verify bound files
- selector 1 — registered/full test
- selector 2 — distributor string
- selector 3 — HELP/manual block
- selector 4 — exit/order/purchase block
- selector 5 — Episode-1 ending/transition block

This removes another genuine red false-merge from the map.

Pass 12 also closes:

- the developer status/debug report path;
- hidden SAFE/TRUNK key/card availability bookkeeping;
- scroll-text display;
- level lighting/display-mode application;
- stage music selection;
- `ENDING.FLI` playback entry;
- the DOS whole-file XOR verifier;
- two empty callback thunks;
- X/Y sort comparators;
- sorted OBJECT pointer-table construction;
- incremental maintenance of those sorted pointer tables.

---

# 1. image `0xA982..0xA99F` — `GateE2M10TimedEndEvent`

Length: **30 bytes**

Exact gate:

- require episode `DS:626A == 2`
- require `(DS:626C + 1) == 10`
- if both are true, forward the caller'with 32-bit parameter to `0xA8E2`
- otherwise return

This is the thin E2M10 wrapper around the timed end-stage routine closed in pass 11.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xA9A0..0xA9AD` — `ShowBlockedRouteFeedback`

Length: **14 bytes**

Thin feedback wrapper.

It forwards one fixed far message/resource pointer to the game'with message/display
routine.

Its known callers are failure paths where and warp/transport destination cannot find and
free adjacent cell.

The higher-level semantic is therefore safely bounded as **blocked-route / no-free-
destination feedback** even though the underlying far pointer remains resource-table
encoded.

**Status: hidden support entry -> GREEN.**

---

# 3. image `0xA9AE..0xAB1A` — `BuildDeveloperStatusSummary`

Length: **365 bytes**

This routine builds the status fields used by the game'with developer/debug information
screen.

Output layout is now reconstructable.

## Initial text fields

It initializes three strings to:

`"none"`

at output offsets:

- `+0x00` — cheat-mode abbreviation string
- `+0x0A` — unfound-key abbreviation string
- `+0x13` — unfound-card abbreviation string

## GUARD count at `+0x06`

Scans all 26-byte GUARD records.

AND record is excluded when:

- current state is terminal `0x0A`, or
- its linked OBJECT class satisfies the special-class predicate
  (`Penelope / Hamerstein / Cannon / Dancers` family).

All other active records increment the WORD at output `+0x06`.

This is the value displayed as:

`Guards left`

## Panel/special-wall count at `+0x08`

Scans the 14-byte special-wall/panel state records beginning at the known panel-state
array and counts records whose state word equals `1`.

The result is stored at output `+0x08`.

This is the value displayed as:

`Panels left`

## Unfound keys at `+0x0A`

The routine compares:

- level-availability bitset `DS:D510`
- player key possession bitset `DS:4192`

For every key present in the level but not owned by the player it appends one letter:

- bit 0 -> `R`
- bit 1 -> `G`
- bit 2 -> `B`
- bit 3 -> `Y`

If no letters are appended, the initialized `"none"` remains.

## Unfound cards at `+0x13`

Compares:

- level card-availability bitset `DS:D511`
- player card possession `DS:4193`

Missing cards are abbreviated:

- bit 0 -> `R`
- bit 1 -> `Y`

## Cheat-mode string at `+0x00`

Enabled cheat flags are appended as:

- `DS:4150` Omniscient -> `S`
- `DS:4151` Omnipotent -> `P`
- `DS:4152` Omnifarious -> `A`
- `DS:4153` Omnificent -> `I`

If no cheat is enabled, `"none"` remains.

The unusual letters are the game'with own compact debug abbreviations; they are not
invented by the reconstruction.

**Status: hidden/merged YELLOW -> GREEN.**

---

# 4. image `0xAB1C..0xAB7F` — `ShowDeveloperStatusScreen`

Length: **100 bytes**

This is the consumer of `BuildDeveloperStatusSummary`.

It formats and displays the exact developer/status block:

```text
Nitemare-3D %s%s  Level %d : %d

Position %d,%d  Cheat modes: %s
Guards left: %d, Panels left: %d
Unfound Keys: %s, Cards: %s
```

Arguments are assembled from:

- version string `V2.0`
- registered/shareware suffix selected through BSF selector 1:
  - registered -> `R`
  - shareware -> `S`
- episode
- level
- player tile X/Y
- cheat abbreviation string
- remaining ordinary GUARD count
- remaining panel count
- unfound key string
- unfound card string

The resulting text is sent to the normal message/display path.

This function is invoked from the active-input handler'with special/debug-key path.

**Status: previously unbounded debug support -> GREEN.**

---

# 5. image `0xAB80..0xABD2` — `AccumulateContainedKeyCardAvailability`

Length: **83 bytes**

This routine updates the level-wide availability bitsets used by the debug/status
screen.

Input is and 28-byte world OBJECT record.

## SAFE class `0x26`

For subtype/object-byte `+1`:

- values `0..3` set the corresponding bit in key availability `DS:D510`
- values `>=4` set bit `(subtype - 4)` in card availability `DS:D511`

## TRUNK class `0x27`

For subtype `>=4`:

- set bit `(subtype - 4)` in key availability `DS:D510`

The world-record builder already directly marks normal world pickups for:

- key class `0x2F`
- card class `0x30`

and calls this helper for containers.

Therefore `D510/D511` represent **keys/cards available somewhere in the current
level**, including ones hidden inside SAFE/TRUNK containers.

That explains why the developer screen can report *unfound* keys/cards rather than
only currently visible pickups.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xABD4..0xABFF` — `ShowScrollTextByIndex`

Length: **44 bytes**

Input selects an entry from and far-pointer table.

The selected scroll text is formatted with:

```text
The scroll says:
%s
```

and sent to the message/display routine.

This closes the text side of object class `0x3D` SCROLL.

**Status: hidden support entry -> GREEN.**

---

# 7. image `0xAC00..0xAC5A` — `ApplyEnvironmentDisplayMode`

Length: **91 bytes**

This is the raw display/shade-mode application helper.

## Dark-event mode

When dark/shade flag `DS:430E` is set:

- `DS:6278 = 6`
- `DS:627A = 0`
- `DS:627B = 0`

## Normal mode

Otherwise it loads the three configured display values from:

- `DS:3CBC`
- `DS:3CBE`
- `DS:3CC0`

Negative sentinel values select defaults:

- first value -> `2`
- second value -> `2`
- third value -> `7`

Finally it calls the common low-level mode/shade application helper.

This is the exact state used by the Episode-1 lights-out/fuse-box paths closed in pass
11.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xAC5C..0xAC97` — `SelectStageBackgroundMusic`

Length: **60 bytes**

When `DS:3CD6 == 0`:

- index the normal stage/substage tune table using episode and level.

When that mode is nonzero:

- rotate through and four-byte alternative tune set
- index is incremented and masked by `3`.

The selected resource/tune ID is passed to the game'with music-selection helper.

This is the level-background MIDI/music selector, not and generic state helper.

**Status: YELLOW -> GREEN.**

---

# 9. image `0xAC98..0xACBD` — `PlayEndingFliSequence`

Length: **38 bytes**

Raw sequence:

1. set game state `DS:3CD4 = 3`
2. select music/resource ID `1`
3. pass literal filename:
   `ending.fli`
4. call the already recovered FLI player
5. run the post-animation display/input cleanup helpers
6. return

The caller is the post-game/session path gated by the ending-event byte.

This is the direct DOS entry from gameplay completion into `ENDING.FLI`.

**Status: hidden presentation entry -> GREEN.**

---

# 10. image `0xACBE..0xAD98` — `VerifyFileXorChecksum`

Length: **219 bytes**

This is the DOS protection/integrity verifier.

Local checksum starts at:

`0x7B`

It:

1. opens the supplied filename in binary-read mode;
2. on open failure enters the file-error path;
3. XORs each selected encrypted/raw file byte into the 8-bit checksum;
4. when the caller'with length is zero, the whole file is consumed;
5. otherwise the bounded byte count is consumed;
6. compares the final XOR against the caller'with expected byte;
7. on mismatch enters the `"%s corrupted"` fatal/error path;
8. closes the file.

This is the V2.0 sibling of the already closed DOS V1.9 whole-file XOR verifier.

It is used by the BSF dispatcher to bind the BSF to:

- `n3d.exe`
- and, in shareware mode, `map.1`.

**Status: ORANGE -> GREEN.**

---

# 11. image `0xAD9A..0xAEA6` — `BsfDispatch`

Length: **269 bytes**

This is the major pass-12 correction.

The switch accepts selector `0..5`.

The six inline table entries branch to the following real operations.

## Selector 0 — initialize / validate BSF

1. open `nite3d.bsf` in binary-read mode;
2. read exactly:
   `0x36 = 54 bytes`
   into `DS:3638`;
3. close the file;
4. decode/check the header through the shared BSF XOR routine;
5. require the raw-header XOR check to succeed;
6. verify whole `n3d.exe` using:
   - expected checksum byte `DS:3639` = header `+1`;
7. test registration byte:
   - `DS:363B` = header `+3`;
8. if unregistered/shareware:
   - verify whole `map.1`
   - expected checksum `DS:363A` = header `+2`.

## Selector 1 — registered/full test

If header registration byte `DS:363B` is nonzero:

- return far pointer to it.

Otherwise:

- return NULL.

This is why higher-level code can test the returned far pointer as and boolean.

## Selector 2 — distributor string

Returns far pointer:

`DS:363C`

which is header `+4`, the 32-byte distributor/owner string.

## Selector 3 — HELP/manual block

Loads/decrypts:

- offset `DS:3660` = header `+0x28`
- length `DS:366A` = header `+0x32`

This is BSF Block1, the HELP/manual text.

## Selector 4 — exit/order/purchase text

Loads/decrypts:

- offset `DS:365C` = header `+0x24`
- length `DS:3668` = header `+0x30`

This is BSF Block0.

## Selector 5 — Episode-1 ending/transition text

Loads/decrypts:

- offset `DS:3664` = header `+0x2C`
- length `DS:366C` = header `+0x34`

This is BSF Block2.

### Embedded data

`0xADB0..0xADBB`

is the **6-WORD selector jump table**.

The old weak label `DispatchSmallRegisterAndRecordOperations` is completely wrong for
this raw body.

**Status: RED / weak-unresolved -> GREEN.**

---

# 12. image `0xAEA8` — `NoOpFarCallbackA`

One-byte far-return thunk.

No reads, writes or calls.

**Status: LOW -> GREEN (known intentional no-op).**

---

# 13. image `0xAEAA` — `NoOpFarCallbackB`

Second one-byte far-return thunk.

No reads, writes or calls.

**Status: LOW -> GREEN (known intentional no-op).**

---

# 14. image `0xAEAC..0xAEC0` — `TransformAdjustedRecordOffsetBy28Twice`

Length: **21 bytes**

Exact arithmetic:

```text
q1 = signed16(param - 6) / 28
q2 = unsigned16(q1) / 28
return q2
```

The older semantic name `ComputeRecordIndexFromOffset` was stronger than the evidence.

For the byte map the important point is that the machine behavior is now exact and
requires no invented logic.

**Status: LOW -> GREEN mechanically; high-level design label intentionally remains
conservative.**

---

# 15. image `0xAEC2..0xAF0F` — `CompareSpatialRecordsByX`

Length: **78 bytes**

qsort-style comparator over far pointers to 28-byte OBJECT/world records.

Comparison field:

`record + 0x10` — world X

Return convention:

- `+1` when second.X < first.X
- `-1` when first.X < second.X
- `0` when equal

The apparent early `RETF` instructions inside the raw range are comparator return
branches, not separate functions.

**Status: LOW -> GREEN.**

---

# 16. image `0xAF10..0xAF5D` — `CompareSpatialRecordsByY`

Length: **78 bytes**

Same comparator structure, using:

`record + 0x12` — world Y

Return convention is the same `+1 / -1 / 0` ordering contract.

The internal return branches must not be entered into the function inventory as
standalone routines.

**Status: LOW -> GREEN.**

---

# 17. image `0xAF5E..0xAFFD` — `BuildSortedSpatialPointerTables`

Length: **160 bytes**

Builds two arrays of far pointers for all active 28-byte world OBJECT records.

Source:

- OBJECT base offset `0x0006`
- far gameplay arena segment `0x21FD`
- count `DS:6270`
- stride `0x1C`

Destination pointer arrays:

- X-sorted array beginning at `DS:D516`
- Y-sorted array beginning at `DS:DA8E`

The function:

1. populates both arrays with pointers to every active OBJECT;
2. sorts the first array with the X comparator;
3. sorts the second array with the Y comparator;
4. walks sorted X order and writes each record'with rank to:
   `OBJECT+0x14`;
5. walks sorted Y order and writes each record'with rank to:
   `OBJECT+0x16`.

This is the producer for the spatial cursor/index machinery already closed around
`6636/676E/6824`.

**Status: YELLOW -> GREEN.**

---

# 18. image `0xAFFE..0xB17D` — `MaintainSortedSpatialIndices`

Length: **384 bytes**

Maintains the two sorted pointer arrays after one OBJECT changes position.

Inputs:

- far pointer to the moved 28-byte OBJECT
- signed X movement/delta indicator
- signed Y movement/delta indicator

## X table

Reads the moved record'with current X-rank from:

`OBJECT+0x14`

Then:

- positive X delta -> bubble the pointer toward larger X values;
- negative X delta -> bubble toward smaller X values.

Every swap:

- exchanges the two far pointers in the X-sorted table;
- increments/decrements the displaced records' `+0x14` rank values.

## Y table

Repeats the same algorithm using:

- Y coordinate `OBJECT+0x12`
- rank `OBJECT+0x16`
- Y-sorted pointer table.

The embedded early returns are shared exits for completed X/Y maintenance, not
additional function entries.

This closes the exact dynamic side of the sorted-OBJECT spatial index.

**Status: YELLOW -> GREEN.**

---

# 19. Byte-map impact

New continuous GREEN span:

`0xA982 .. 0xB17D`

Total: **2,044 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `A982–A99F` | 30 | E2M10 timed-event gate |
| `A9A0–A9AD` | 14 | blocked-route feedback |
| `A9AE–AB1A` | 365 | developer-status summary builder |
| `AB1C–AB7F` | 100 | developer/debug status screen |
| `AB80–ABD2` | 83 | hidden SAFE/TRUNK key/card availability |
| `ABD4–ABFF` | 44 | scroll-text display |
| `AC00–AC5A` | 91 | environment display/shade mode |
| `AC5C–AC97` | 60 | stage background music |
| `AC98–ACBD` | 38 | ENDING.FLI sequence |
| `ACBE–AD98` | 219 | whole-file XOR verifier |
| `AD9A–AEA6` | 269 | NITE3D.BSF dispatcher |
| `AEA8` | 1 | no-op far callback AND |
| `AEAA` | 1 | no-op far callback B |
| `AEAC–AEC0` | 21 | exact record-offset arithmetic helper |
| `AEC2–AF0F` | 78 | OBJECT X comparator |
| `AF10–AF5D` | 78 | OBJECT Y comparator |
| `AF5E–AFFD` | 160 | build X/Y sorted OBJECT pointer tables |
| `AFFE–B17D` | 384 | maintain sorted OBJECT pointer tables |

Routine/table content: **2,036 bytes**.

Alignment/padding bytes: **8**.

### DATA/TABLE overlay

- `ADB0–ADBB` — 6-WORD BSF selector jump table

It should be drawn as:

`GREEN knowledge + TABLE/DATA overlay`.

---

# 20. Function-inventory corrections

Add/correct at least:

```text
A982  GateE2M10TimedEndEvent
A9A0  ShowBlockedRouteFeedback
A9AE  BuildDeveloperStatusSummary
AB1C  ShowDeveloperStatusScreen
AB80  AccumulateContainedKeyCardAvailability
ABD4  ShowScrollTextByIndex
AC00  ApplyEnvironmentDisplayMode
AC5C  SelectStageBackgroundMusic
AC98  PlayEndingFliSequence
ACBE  VerifyFileXorChecksum
AD9A  BsfDispatch
AEA8  NoOpFarCallbackA
AEAA  NoOpFarCallbackB
AEAC  TransformAdjustedRecordOffsetBy28Twice
AEC2  CompareSpatialRecordsByX
AF10  CompareSpatialRecordsByY
AF5E  BuildSortedSpatialPointerTables
AFFE  MaintainSortedSpatialIndices
```

Most importantly, remove the old semantic identity:

`AD9A = generic small register/record dispatcher`

because it is demonstrably the BSF loader/license/resource dispatcher.

---

# 21. Cumulative closure

Pass 11 cumulative since the pass-5 baseline:

`20,369 bytes`

Pass 12 adds:

`2,044 bytes`

New cumulative total:

**22,413 bytes**

of formerly problematic DOS V2.0 byte-map territory explicitly promoted to GREEN
during passes 6–12.

---

# 22. Next target

Continue at:

`0xB17E`

The next region contains:

- directional object animation
- weighted animation
- projected world-object queue construction
- world-record lookup
- occupancy cleanup
- the large weak/decompiler-polluted block beginning at `0xB5B8`
- world-cell record construction around `0xB7F8`
- world-object derived-field and direction helpers

`B5B8` is the next particularly valuable RED/ORANGE target because the old export
treats it as and ~900-line mixed state/video dispatcher and reports and bad-instruction
truncation.  Raw boundary repair there should produce another large GREEN gain.