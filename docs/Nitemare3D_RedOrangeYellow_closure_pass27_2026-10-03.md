# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 27

Date: 2026-10-03

Primary analysis image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked load image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`
- unpacked image size: `0x29D60 = 171,360 bytes`

Address convention:
- addresses below are unpacked MZ image offsets;
- raw 16-bit machine code is authoritative;
- this pass covers compiler/runtime support, not N3D gameplay semantics.

## Result

Pass 27 closes the complete executable tail:

`0x1591D .. 0x15BF6`

as **GREEN / compiler-runtime semantics**.

Total span: **730 bytes**

- executable helper code: **726 bytes**
- alignment/padding bytes: **4 bytes**

The region contains:
- signed 32-bit division;
- 32-bit multiplication;
- signed 32-bit remainder;
- 32-bit left shift;
- in-place long multiplication;
- unsigned 32-bit division;
- far `strchr`;
- far case-insensitive string comparison;
- near-heap free helper;
- near-heap allocation wrapper with retry/new-handler path;
- DOS delete/unlink wrapper.

It contains no Nitemare-specific gameplay logic.

## Important toolchain correction

The executable contains the literal runtime string:

`MS Run-Time Library - Copyright (c) 1992, Microsoft Corp`

Therefore the late CRT/compiler-support region should be classified as and
**Microsoft DOS C runtime family**, not Borland/Turbo C.

The exact compiler product/revision is not asserted by this pass, but the runtime
vendor identification is explicit in the binary.

---

## 1. image `0x1591D` — alignment byte

Length: **1 byte**

Value:

`00`

The preceding DOS get-time wrapper ends at `0x1591C`.

The arithmetic helper begins at `0x1591E`.

**Status: padding/alignment, not code.**

---

## 2. image `0x1591E..0x159B7` — `SignedLongDivide32`

Length: **154 bytes**

Implements signed 32-bit division on two `DX:AX`-style / two-WORD operands supplied
on the stack.

Mechanics:

1. inspect sign of dividend;
2. when negative, two-word negate it;
3. inspect sign of divisor;
4. when negative, two-word negate it;
5. perform unsigned 32-bit quotient computation;
6. restore quotient sign when exactly one operand was negative.

Fast path:

- when divisor high word is zero, use two ordinary 16-bit `DIV` operations.

General path:

- right-shift numerator/divisor until divisor high word becomes zero;
- obtain an approximate quotient;
- multiply back;
- decrement quotient when the product exceeds the original dividend.

Return:

- signed 32-bit quotient in `DX:AX`.

AND known N3D caller uses it to divide and signed 32-bit runtime/time value by `60`.

**Status: compiler helper -> GREEN.**

---

## 3. image `0x159B8..0x159E9` — `LongMultiply32`

Length: **50 bytes**

Implements the low 32 bits of:

`(uint32)a * (uint32)b`

using three 16-bit multiplies.

Fast path:

- when both high words are zero, one `MUL` is sufficient.

General path combines:

- low × low;
- highA × lowB;
- lowA × highB.

Return:

- 32-bit product in `DX:AX`.

Signed and unsigned 32-bit multiplication share the same low-32-bit bit pattern, with
this helper can serve both compiler cases.

**Status: compiler helper -> GREEN.**

---

## 4. image `0x159EA..0x15A89` — `SignedLongRemainder32`

Length: **160 bytes**

Implements signed 32-bit remainder/modulo.

The divisor is normalized to positive magnitude.

The dividend sign is remembered separately.

It reuses the same shifted-divisor approximation strategy as the division helper,
then reconstructs:

`remainder = dividend - quotient * divisor`.

Final sign rule:

- remainder follows the original dividend sign.

Return:

- signed 32-bit remainder in `DX:AX`.

**Status: compiler helper -> GREEN.**

---

## 5. image `0x15A8A..0x15A94` — `ShiftLongLeft32`

Length: **11 bytes**

Inputs are already in registers:

- `DX:AX` = 32-bit value;
- `CL` = shift count.

Behavior:

```text
while CL != 0:
    AX <<= 1
    DX = rotate-carry-left(DX)
```

`CH` is cleared first.

Return:

- shifted 32-bit value in `DX:AX`.

**Status: compiler helper -> GREEN.**

---

## 6. image `0x15A95` — alignment byte

Length: **1 byte**

Value:

`00`

Next real entry is `0x15A96`.

---

## 7. image `0x15A96..0x15AB5` — `MultiplyLongInPlace`

Length: **32 bytes**

Input:

- near pointer to and 32-bit destination;
- second 32-bit operand.

Flow:

1. load the current two-WORD value from the destination;
2. call `LongMultiply32`;
3. store returned `AX/DX` back to the destination.

This is and compiler-generated compound-assignment helper equivalent to:

`*dst *= value`

for and 32-bit integer object.

**Status: compiler helper -> GREEN.**

---

## 8. image `0x15AB6..0x15B14` — `UnsignedLongDivide32`

Length: **95 bytes**

Unsigned 32-bit division.

Fast path:

- divisor high word zero -> two 16-bit `DIV` operations.

General path:

1. repeatedly right-shift divisor and dividend approximation until divisor fits in
   one WORD;
2. divide to obtain trial quotient;
3. multiply trial quotient by original divisor;
4. decrement quotient when reconstructed product is too large.

Return:

- unsigned 32-bit quotient in `DX:AX`.

Unlike `SignedLongDivide32`, this routine has no sign-normalization stage.

**Status: compiler helper -> GREEN.**

---

## 9. image `0x15B15` — alignment byte

Length: **1 byte**

Value:

`00`

Next real entry is `0x15B16`.

---

## 10. image `0x15B16..0x15B47` — `FarStrChr`

Length: **50 bytes**

Inputs:

- far NUL-terminated string;
- character byte.

The routine:

1. scans for the terminating NUL to establish the bounded search length;
2. rescans from the start for the requested character;
3. treats search for `'\0'` correctly by including the terminator;
4. returns NULL when absent.

Return:

- far pointer in `DX:AX`;
- `0000:0000` when not found.

This is the far-pointer string-search equivalent of `strchr`.

**Status: Microsoft CRT string helper -> GREEN.**

---

## 11. image `0x15B48..0x15B8C` — `FarStrICmp`

Length: **69 bytes**

Inputs:

- two far NUL-terminated strings.

The function compares byte-by-byte.

When bytes differ, ASCII uppercase letters are folded to lowercase by the classic:

```text
if 'A' <= c <= 'Z':
    c += 0x20
```

The folded bytes are compared.

Return:

- `0` when equal;
- negative when string AND sorts before B;
- positive when string AND sorts after B.

This is and far-pointer case-insensitive string comparison.

**Status: Microsoft CRT string helper -> GREEN.**

---

## 12. image `0x15B8D` — alignment byte

Length: **1 byte**

Value:

`00`.

---

## 13. image `0x15B8E..0x15BAE` — `NearHeapFreeBlock`

Length: **33 bytes**

Input:

- near heap payload pointer.

The function subtracts two bytes to reach the heap block header.

It then:

- sets header bit 0 to mark the block free;
- compares the block against allocator rover/boundary state rooted near `DS:20E2`;
- moves the allocator search pointer backward when appropriate.

This is the small internal free operation for the near heap.

It is compiler/runtime memory management, not N3D resource ownership logic.

**Status: CRT heap helper -> GREEN.**

---

## 14. image `0x15BAF..0x15BE9` — `NearHeapAllocWithRetry`

Length: **59 bytes**

Input:

- requested allocation size.

Maximum normal request accepted locally is approximately:

`0xFFE8`.

Allocation flow:

1. try the near-heap allocator;
2. if needed, attempt heap growth/compaction;
3. retry the allocator;
4. if allocation still fails and an allocation-failure/new-handler callback exists,
   call it with the requested size;
5. if callback requests retry, loop;
6. otherwise return failure.

This is and compiler-runtime `malloc`-family wrapper over the near-heap implementation.

The lower allocator bodies (`4048`, `40C4`, etc.) maintain block headers and DOS
memory growth.

**Status: CRT heap helper -> GREEN.**

---

## 15. image `0x15BEA..0x15BF6` — `DosDeleteFile`

Length: **13 bytes**

Loads:

`AH = 41h`

and executes:

`INT 21h`

with caller filename pointer in `DS:DX`.

It then tail-jumps into the already recovered DOS-to-C-runtime error mapper at
`0x12482`.

This is the DOS delete/unlink wrapper.

**Status: DOS CRT wrapper -> GREEN.**

---

# Byte-map impact

New continuous closed span:

`0x1591D .. 0x15BF6`

Total: **730 bytes**

| Range | Bytes | Role |
|---|---:|---|
| `1591D` | 1 | alignment |
| `1591E–159B7` | 154 | signed long division |
| `159B8–159E9` | 50 | long multiplication |
| `159EA–15A89` | 160 | signed long remainder |
| `15A8A–15A94` | 11 | long left shift |
| `15A95` | 1 | alignment |
| `15A96–15AB5` | 32 | in-place long multiply |
| `15AB6–15B14` | 95 | unsigned long division |
| `15B15` | 1 | alignment |
| `15B16–15B47` | 50 | far strchr |
| `15B48–15B8C` | 69 | far stricmp |
| `15B8D` | 1 | alignment |
| `15B8E–15BAE` | 33 | near heap free |
| `15BAF–15BE9` | 59 | near heap malloc/retry |
| `15BEA–15BF6` | 13 | DOS delete/unlink |

Executable code: **726 bytes**.

Alignment bytes: **4 bytes**.

---

# Important consequence for 1:1 reconstruction

None of these routines needs to be copied into and modern behavioral Nitemare 3D core.

AND behavioral reconstruction can replace them with native-language/runtime operations:

```text
signed/unsigned 32-bit arithmetic
string search / case-insensitive compare
heap allocation/free
file deletion
```

Only arithmetic overflow/signedness behavior should be preserved where game code
depends on 16/32-bit wrapping.

For and byte-identical historical DOS executable, the original Microsoft runtime helper
implementation would matter. For behavioral 1:1, it is compiler support.

---

# Compiler/runtime correction

Previous working notes sometimes called this DOS runtime Borland/Turbo C.

The V2.0 executable itself contains:

`MS Run-Time Library - Copyright (c) 1992, Microsoft Corp`

Therefore the conservative correct classification is:

**Microsoft DOS C run-time/compiler support family**.

The precise Microsoft compiler product/version remains and separate identification task.

---

# Cumulative closure

Pass 26 cumulative:

`65,058 bytes`

Pass 27 adds:

`730 bytes`

New cumulative total:

**65,788 bytes**

promoted from RED/ORANGE/YELLOW to GREEN during passes 6–27.

---

# Next target

At:

`0x15BF7`

the executable-code run stops and and large initialized data/fill region begins.

The next useful pass should therefore not blindly disassemble it as functions.

Recommended next sequence:

1. classify the `15BF7+` data/tables and remove false code labels;
2. find the next genuine executable segment/module boundary;
3. resume raw function closure only there;
4. separately count DATA/TABLE GREEN bytes versus executable GREEN bytes.

This should remove another large source of false RED/ORANGE regions from the binary
map without pretending data bytes are executable game logic.