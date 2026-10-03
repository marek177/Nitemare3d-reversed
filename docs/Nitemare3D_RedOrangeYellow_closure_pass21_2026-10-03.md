# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 21

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- image offsets below exclude the `0x200` MZ header
- physical file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative

## Result

Pass 21 closes the previously unresolved gap:

`0xFD40 .. 0x100A1`

as **GREEN / deep static semantics**.

Newly promoted span: **866 bytes**.

This joins the already green main-engine band `0x45CE..0xFD3F` directly to the
previously closed VEC iterator beginning at `0x100A2`.

Therefore the DOS byte map now contains one continuous GREEN knowledge band:

`0x45CE .. 0x10135`

apart from the independent high-image runtime areas.

---

## 1. `0xFD40..0xFD45` — `RuntimeRand`

Length: 6 bytes.

Thin far wrapper around runtime target `11EE:31F8`.

This is the random-number producer used throughout gameplay and renderer support.

**Status: YELLOW -> GREEN.**

---

## 2. `0xFD46..0xFD50` — `SeedRuntimeRandOne`

Length: 11 bytes.

Pushes constant `1` and calls runtime target `11EE:31E6`.

This is the fixed RNG seed path used by deterministic/demo initialization.

`0xFD51` is alignment NOP.

**Status: LOW/YELLOW -> GREEN.**

---

## 3. `0xFD52..0xFD8F` — `XorTransformBufferWithChecksum`

Length: 62 bytes.

For exactly `length` bytes:

1. XOR the original byte into an 8-bit checksum accumulator;
2. XOR the byte in place with the repeating 0x34-byte key beginning at `DS:2045`;
3. advance key position modulo `0x34`.

Return:
- XOR checksum of the original, for-transform bytes.

This is the shared BSF transform/checksum primitive.

**Status: YELLOW -> GREEN.**

---

## 4. `0xFD90..0xFDA4` — `MapVecOffsetToBucket`

Length: 21 bytes.

Exact arithmetic:

```text
q = signed16(vecOffset - 0x62AC) / 0x1C
return unsigned16(q) / 0x1C
```

With this is not merely and direct VEC index.  It maps the record offset through two
successive 28-byte divisions.

`0xFDA5` is alignment NOP.

**Status: LOW -> GREEN mechanically.**

---

## 5. `0xFDA6..0xFDED` — `CompareDirectionalVecPointers`

Length: 72 bytes.

qsort-style comparator over pointers to VEC records.

It examines the first record orientation:

- when `x0 == x1`, compare X coordinate;
- otherwise compare Y coordinate.

Return values:

```text
+1
 0
-1
```

with descending ordering under the runtime qsort contract.

This comparator is used by all four directional VEC buckets built immediately after.

**Status: YELLOW -> GREEN.**

---

## 6. `0xFDEE..0xFEF8` — `BuildAndSortDirectionalVecBuckets`

Length: 267 bytes.

This is the high-confidence directional VEC bucket builder.

It clears four counts:

```text
DS:57FA
DS:57FC
DS:57FE
DS:5800
```

and scans all VEC records:

```text
base   DS:62AC
count  DS:626E
stride 0x1C
```

VEC byte `+07` selects bucket 0..3.

Pointer arrays begin at:

```text
5802
5A9C
5D36
5FD0
```

Each bucket is limited to:

`0x14D = 333`

records.

Overflow enters the fatal error path.

After collection, each pointer array is sorted with the common runtime qsort wrapper
using comparator `FDA6`.

This directly closes the producer side of the directional VEC index used by visibility
and renderer traversal.

`0xFEF9` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

## 7. `0xFEFA..0x1003D` — `InsertProjectedVecIntoColumnOwnership`

Length: 324 bytes.

This is the major pass-21 correction.

The old export described `FEFA` as and weak mixed renderer/index routine and contained and
`halt_baddata` artifact.

Raw machine code is coherent.

Input:
- pointer to one 28-byte VEC.

### Projection gate

1. require VEC active flag bit 0 at `VEC+05`;
2. call `CAB8 = ProjectAndClipVecEndpoints`;
3. reject if projection reports not visible.

### Clip to viewport X interval

Projected VEC bounds are:

```text
VEC+14  left X
VEC+18  right X
```

They are clamped against:

```text
DS:4548  viewport left
DS:454A  viewport right
```

### Per-column ownership array

For every covered screen column, index into:

`DS:4564 + column*2`

which stores and VEC pointer.

If the column is empty:

- install the candidate VEC;
- decrement `DS:4562`, the remaining-unowned-column count.

If an owner already exists, the function compares old/new VEC orientation/category and
the relevant geometry fields `+0C/+0E/+10/+12`.

The branch matrix chooses which VEC should own that screen column according to its
direction/orientation and coordinate ordering.

The exact comparisons are now bounded from raw ASM; no decompiler offcut is needed.

### Return

After processing the projected interval:

```text
AL = 1  when DS:4562 <= 0
AL = 0  otherwise
```

With the function reports whether all required viewport columns have acquired an owner.

This is and renderer visibility/column-ownership insertion routine, not and generic
record dispatcher.

**Status: RED/weak -> GREEN.**

---

## 8. `0x1003E..0x100A0` — `DecodeVecCellBounds`

Length: 99 bytes.

Reads VEC world bounds:

```text
+0C
+0E
+10
+12
```

and converts all four to map-cell coordinates with arithmetic `>> 6`.

Unless VEC flag bit `0x08` is set:

- orientation `+07 == 2` decrements the X bound pair;
- orientation `+07 == 1` decrements the Y bound pair.

The four cell bounds are written through caller output pointers.

This is the raw helper consumed by the already closed VEC iterator at `0x100A2`.

`0x100A1` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# Byte-map impact

New GREEN span:

`0xFD40..0x100A1`

= **866 bytes**.

Combined with prior passes:

`0x45CE..0x10135`

is now one continuous statically GREEN base-engine band.

Cumulative RED/ORANGE/YELLOW -> GREEN conversion since the pass-5 baseline:

`41,806 + 866 = 42,672 bytes`.

The next target begins at `0x10136` and proceeds through typed VEC/cell lookup and the
next large `2000:` gameplay/renderer continuation.