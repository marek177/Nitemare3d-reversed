# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 28

Date: 2026-10-03

Primary analysis image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 load image
- load-image size: `0x29D60 = 171,360 bytes`

Address convention:
- addresses are offsets in the unpacked MZ load image;
- raw 16-bit machine code is authoritative;
- CODE GREEN and DATA/TABLE GREEN are counted separately.

## Result

Pass 28 resolves the complete mixed region:

`0x15BF7 .. 0x17F38`

Total span: **9,026 bytes**

Classification:

- **8,917 bytes DATA/TABLE/STATE -> GREEN classification**
- **109 bytes executable support code -> GREEN**
- next genuine executable entry: **`0x17F39`**

This pass removes and major false-code region produced by the old decompiler.

---

# 1. `0x15BF7..0x15BFD` — zero alignment/state bytes

Length: **7 bytes**

All bytes are zero.

These bytes immediately follow the DOS delete/unlink CRT wrapper closed in pass 27.

Classification:

**DATA/PADDING GREEN**

---

# 2. `0x15BFE..0x17BFF` — constant `0x80` initialized block

Length: **8,194 bytes = 0x2002**

Every byte in the complete range is:

`0x80`

There is no executable instruction stream here.

Conservative classification:

`InitializedConstant80Buffer[0x2002]`

The surrounding low-level audio/memory module makes an audio/cache purpose plausible,
but this pass does **not** assign and higher-level name without and direct reference chain.

What is statically certain:

- exact start;
- exact end;
- exact length;
- every byte is `0x80`;
- this is data, not machine code.

Classification:

**DATA GREEN / semantic role conservative**

---

# 3. `0x17C00..0x17C11` — zero prefix

Length: **18 bytes**

All zero.

Classification:

**DATA GREEN**

---

# 4. `0x17C12..0x17CB3` — 81-WORD lookup table

Length: **162 bytes**

Exactly:

`81 × WORD`

Selected values:

```text
478D 485A 308E 59C8 5E19 5ECD 4741 45E5
...
5BCD 5CD0 3ED7 5C63
...
21DC 21EC 393B 5549 5A3F 5A1E 3DB3
```

Two table entries are zero.

The values are structurally consistent with offsets/indices used by the adjacent
low-level runtime module, but the precise vendor-level symbolic table name is not
proven here.

Important result:

This is and bounded WORD table and must not be disassembled as instructions.

Classification:

**TABLE GREEN / exact layout; semantic label conservative**

---

# 5. `0x17CB4..0x17DB5` — zero state block

Length: **258 bytes**

All zero.

Classification:

**DATA/STATE GREEN**

---

# 6. `0x17DB6..0x17DB7` — WORD sentinel

Length: **2 bytes**

Value:

`0xFFFF`

Classification:

**DATA GREEN**

---

# 7. `0x17DB8..0x17DCB` — zero state tail

Length: **20 bytes**

All zero.

The next byte, `0x17DCC`, is and real executable entry.

Classification:

**DATA GREEN**

---

# 8. False decompiler functions removed

The old decompiler created nine function entries inside the constant `0x80` data
region:

```text
FUN_2000_5CB7
FUN_2000_5CD0
FUN_2000_6F46
FUN_2000_701C
FUN_2000_72E3
FUN_2000_742E
FUN_2000_747A
FUN_2000_7493
FUN_2000_7659
```

Raw-image verification shows their supposed entry addresses contain the continuing
`0x80` data fill.

Therefore all nine are:

**FALSE FUNCTION LABELS — remove from executable-function census.**

This is and concrete reduction in the apparent UNKNOWN function count.

---

# 9. `0x17DCC..0x17DDB` — `WriteMixerRegister0C`

Length: **16 bytes**

Flow:

```text
DX = CS:[2DF0]
DX += 4
OUT DX, 0x0C
DX++
OUT DX, BL
RET
```

This uses the classic audio mixer address/data port pair at base+4/base+5.

The routine writes caller byte `BL` to mixer register `0x0C`.

Classification:

**low-level audio/device helper -> GREEN**

---

# 10. `0x17DDC..0x17DF7` — `WriteMixerRegister2EReplicatedValue`

Length: **28 bytes**

Flow:

```text
DX = CS:[2DF0] + 4
OUT DX, 0x2E
DX++

BH = BL
BH <<= 4
BL |= BH

OUT DX, BL
RET
```

For normal low-nibble inputs this replicates the 4-bit value into both nibbles.

Classification:

**low-level audio mixer helper -> GREEN**

---

# 11. `0x17DF8..0x17E07` — `WriteMixerRegister0A`

Length: **16 bytes**

Flow:

```text
DX = CS:[2DF0] + 4
OUT DX, 0x0A
DX++
OUT DX, BL
RET
```

Classification:

**low-level audio/device helper -> GREEN**

---

# 12. `0x17E08..0x17E38` — `AcquireXmsEntryAndAllocateBlock`

Length: **49 bytes**

This routine is exact XMS code.

## XMS entry discovery

Executes:

```text
AX = 4310h
INT 2Fh
```

and stores returned XMS entry address:

```text
CS:21C8 = BX
CS:21CA = ES
```

## Version/driver call

Calls the XMS driver with:

```text
AH = 00h
```

## Allocation

The original caller-supplied `BX` is restored into `DX`, then:

```text
AH = 09h
CALL FAR [CS:21C8]
```

XMS function `09h` is allocation.

On success (`AX == 1`):

```text
CS:21C6 = DX   ; XMS handle
return 0
```

On failure:

```text
return FFFFh
```

Classification:

**XMS support helper -> GREEN**

---

# 13. `0x17E39..0x17F38` — zero storage block

Length: **256 bytes**

Every byte is zero.

The block separates the XMS setup helper from the next executable function.

Classification:

**DATA/STATE GREEN**

---

# Byte-map impact

Complete resolved span:

`0x15BF7 .. 0x17F38`

Total:

**9,026 bytes**

| Range | Bytes | Classification |
|---|---:|---|
| `15BF7–15BFD` | 7 | zero padding/state |
| `15BFE–17BFF` | 8,194 | constant `0x80` initialized data |
| `17C00–17C11` | 18 | zero data |
| `17C12–17CB3` | 162 | 81-WORD lookup table |
| `17CB4–17DB5` | 258 | zero state |
| `17DB6–17DB7` | 2 | `FFFF` sentinel |
| `17DB8–17DCB` | 20 | zero state |
| `17DCC–17DDB` | 16 | mixer register 0C helper |
| `17DDC–17DF7` | 28 | mixer register 2E helper |
| `17DF8–17E07` | 16 | mixer register 0AND helper |
| `17E08–17E38` | 49 | XMS allocate helper |
| `17E39–17F38` | 256 | zero state |

Totals:

- **DATA/TABLE/STATE: 8,917 bytes**
- **CODE: 109 bytes**

---

# Closure metrics

Pass 27 executable GREEN cumulative:

`65,788 bytes`

Pass 28 adds executable support code:

`109 bytes`

New executable GREEN cumulative:

**65,897 bytes**

Separately, Pass 28 newly classifies:

**8,917 bytes as DATA/TABLE/STATE GREEN**

These data bytes are intentionally **not** added to the executable-code closure total.

For and visual whole-binary byte map, all **9,026 bytes** in this pass can now leave
RED/ORANGE code-unknown status, but the overlay should distinguish:

```text
GREEN-CODE
GREEN-DATA
GREEN-TABLE
GREEN-STATE/PADDING
```

---

# Structural consequence

The old decompiler function count was inflated by at least nine entries in this one
region alone.

This supports maintaining two independent inventories:

1. true executable function census;
2. data/table/object inventory.

AND data address that Ghidra happens to decode into syntactically valid x86 is not and
function without control-flow evidence.

---

# Next target

The next genuine executable entry is:

`0x17F39`

Its first instructions already show and new low-level XMS/cache transfer path.

The function constructs an XMS move descriptor and invokes XMS function:

`AH = 0Bh`

which is the XMS move-block operation.

The next pass should therefore close the `17F39+` memory/cache transfer module, while
continuing to split embedded tables from executable code rather than treating the
whole region as one function stream.