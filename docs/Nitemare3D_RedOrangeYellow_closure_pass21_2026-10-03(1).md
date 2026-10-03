# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 21

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges are unpacked MZ image offsets
- raw 16-bit machine code is authoritative

## Result

Pass 21 closes:

`0xFD40 .. 0x1003D`

as **GREEN / deep static semantics**.

Total newly closed span: **766 bytes**.

This includes the RNG wrapper/seed path, BSF XOR transform, directional VEC sorting
and the formerly weak `FEFA` visibility/column-owner routine.

---

## `0xFD40..0xFD45` — `RuntimeRand`

Calls far runtime target:

`11EE:31F8`

which maps to the already audited DOS RNG implementation.

RNG recurrence:

`state = state*214013 + 2531011 (mod 2^32)`

return:

`(state >> 16) & 0x7FFF`.

Status: GREEN.

## `0xFD46..0xFD50` — `ResetRuntimeRandSeedToOne`

Calls runtime RNG setter `11EE:31E6` with literal seed `1`.

This is the deterministic RNG reset used by startup/DEMO-related flows.

Status: GREEN.

## `0xFD52..0xFD8F` — `XorTransformBufferWithChecksum`

For each byte:

1. XOR original byte into an 8-bit checksum accumulator;
2. XOR the byte in place with repeating key byte:
   `DS:2045[index % 0x34]`.

Returns XOR checksum of the original for-transform bytes.

This is the common NITE3D.BSF encode/decode/checksum primitive.

Status: GREEN.

## `0xFD90..0xFDA4` — `TransformVecRecordOffsetIndex`

Exact arithmetic:

`q1 = signed16(offset - 0x62AC) / 0x1C`

then:

`q2 = unsigned16(q1) / 0x1C`

return `q2`.

The high-level historical source name is not required; exact behavior is bounded.

Status: GREEN.

## `0xFDA6..0xFDED` — `CompareDirectionalVecPointers`

qsort-style comparator over pointers to 28-byte VEC records.

If the first record is vertical:

`VEC+0x10 == VEC+0x0C`

the comparator orders by X (`+0x0C`).

Otherwise it orders by Y (`+0x0E`).

Return:

- `+1`
- `0`
- `-1`

using ordinary comparator semantics.

Status: GREEN.

## `0xFDEE..0xFEF8` — `BuildAndSortDirectionalVecBuckets`

Clears four counts:

- `DS:57FA`
- `DS:57FC`
- `DS:57FE`
- `DS:5800`

Scans every VEC:

- base `DS:62AC`
- count `DS:626E`
- stride `0x1C`.

Direction/orientation byte:

`VEC+0x07`

selects one of four pointer arrays:

- `DS:5802`
- `DS:5A9C`
- `DS:5D36`
- `DS:5FD0`.

Each bucket has maximum accepted count:

`0x14D = 333`.

Overflow enters the fatal/error path.

After collection all four arrays are sorted with the directional comparator at `FDA6`
through the runtime qsort wrapper.

This is the producer of the four directional VEC lists consumed by visibility
traversal.

Status: GREEN.

## `0xFEFA..0x1003D` — `InsertProjectedVecIntoColumnOwnerBuffer`

This is the formerly weak/decompiler-polluted `FEFA` body.

Input:

- pointer to and 28-byte VEC record.

### Eligibility and projection

Reject unless:

`VEC+0x05 bit0 != 0`.

Then call:

`CAB8 = ProjectAndClipVecEndpoints`.

If projection says the VEC is not visible, return false.

### Clip projected X interval

Use:

- `VEC+0x14` projected left X
- `VEC+0x18` projected right X

and clip to:

- viewport left `DS:4548`
- viewport right `DS:454A`.

Column-owner buffer begins at:

`DS:4564`

with one WORD VEC pointer per screen column.

### Empty column

If owner is zero:

- install current VEC pointer;
- decrement `DS:4562`, the remaining-unowned-column count.

### Occupied column

When another VEC already owns the column, the routine resolves replacement using the
new and existing VEC orientation bytes and strict comparisons of world endpoints:

- X comparisons from `+0x0C/+0x10`
- Y comparisons from `+0x0E/+0x12`.

The orientation-specific comparisons decide which VEC is geometrically in front for
that column.

Equality leaves the existing owner.

### Early completion

After processing the projected span:

- if `DS:4562 <= 0`, return `AL=1`;
- otherwise return `AL=0`.

With this routine means:

`project one candidate VEC and merge it into the per-column visibility-owner buffer`.

This is the DOS counterpart of the statically closed Win16 VEC/column ownership
visibility path.

Status: weak/unresolved -> GREEN.

---

## Byte-map impact

| Range | Bytes | Role |
|---|---:|---|
| `FD40–FD45` | 6 | runtime RNG |
| `FD46–FD50` | 11 | reset RNG seed to 1 |
| `FD52–FD8F` | 62 | BSF XOR transform/checksum |
| `FD90–FDA4` | 21 | VEC offset arithmetic helper |
| `FDA6–FDED` | 72 | directional VEC comparator |
| `FDEE–FEF8` | 267 | build/sort four directional VEC lists |
| `FEFA–1003D` | 324 | projected VEC column-owner insertion |

Alignment:

- `FD51`
- `FDA5`
- `FEF9`

are one-byte NOPs.

The entire `FD40..1003D` range can now be GREEN.

## Cumulative closure

Pass 20 cumulative since pass-5 baseline:

`41,806 bytes`

Pass 21 adds:

`766 bytes`

New cumulative:

**42,572 bytes**

promoted from RED/ORANGE/YELLOW to GREEN during passes 6–21.

## Next target

`0x1003E..0x10135` is already GREEN from the earlier corrected VEC-iterator closure.

Continue after that at `0x10136` and onward through the remaining VEC/map lookup and
visibility helpers, while avoiding double-counting bytes already closed by pass 2.