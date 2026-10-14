# v0.33 RE MAX — correction: 0E50 is PUSH updater, not generic OBJECT scheduler

**14 October 2026.** This is a *new direct original-byte static audit* of the same
fingerprinted DOS v2.0 and Win16 v1.10 images registered in v0.32.
Original games were not executed. No 1:1 gameplay timing/pixel claim and no
global project percentage increase.

## Decisive result

DOS v2.0 *unpacked MZ load-image* routine at **0x0E50** is the updater for
**six-byte PUSH records**. It is called directly by DOS FAST at load-image
**0xC172** (call target \`0:0E50\` before load relocation). Win16 v1.10
**NE segment 3 offset 0x2210** is the matching updater.

Both updater bodies contain exactly **0x124 = 292 bytes** (through RETF).
**272 bytes are equal**, while the remaining **20 differing bytes all
belong to nine known address-operand fields**. Mask only those operand
bytes and the complete bodies match byte for byte. None of the prefixes,
opcodes, branch offsets, gameplay constants, stride values or ordering
instructions differ.

Fingerprint gate:
- DOS v2.0 **MZ load image**, size 171,360, SHA-256
  \`e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297\`.
- Win16 v1.10 **full NE EXE**, size 230,400, SHA-256
  \`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481\`.

Do not apply these build-specific offsets to DOS v1.0/v1.2/v1.9 or other
Windows executables. The matching static routine is not proof that every
caller has matching cadence, external helpers have identical internals or
every interactive scenario is reachable across builds.

## Relocated operand-only differences

All offsets in this table are *relative to the 292-byte updater*, NOT
absolute file offsets:

| Relative offset | Length | Encoded operand |
| --- | ---: | --- |
| \`+0x007\` | 2 | PUSH/OBJECT data segment |
| \`+0x00E\` | 2 | six-byte PUSH record-array base |
| \`+0x02F\` | 2 | runtime OBJECT array base |
| \`+0x032\` | 2 | OBJECT array segment |
| \`+0x070\` | 2 | MAP cell-byte array base |
| \`+0x073\` | 2 | MAP array segment |
| \`+0x091\` | 2 | destination OBJECT property-byte table |
| \`+0x101\` | 4 | far target for sorted-list update helper |
| \`+0x115\` | 2 | load/reload selector for pool segment |

The entire remaining 272-byte body is identical. A whitelist containing
even one instruction opcode or condition is invalid, so the verifier rejects
differences outside these *exact* 20 operand positions.

## Original in-memory layout

| Field | DOS v2.0 | Win16 v1.10 |
| --- | --- | --- |
| PUSH array | data segment \`21FDh\`, offset \`36B6h\` | segment \`2242h\`, offset \`A616h\` |
| Live PUSH count | \`es:[0004h]\`; checked before/after iterations | same instruction form with version-specific segment |
| PUSH record | 6 bytes, repeated | identical six-byte layout |
| \`+0\` | u16 runtime OBJECT index | same |
| \`+2/+3\` | signed i8 world-X/Y increments | same |
| \`+4\` | countdown (8 at activation; decrement after successful step) | same |
| OBJECT entry | index × 28 plus build-specific pool base \`+6\` | same 28-byte index operation |
| OBJECT world X/Y | \`OBJECT+10h/+12h\`, u16 | same |
| OBJECT MAP pointer | \`OBJECT+0Ch\`, full 32-bit far pointer | same |
| MAP layer | two bytes/cell: \`+0\` wall ID, \`+1\` object ID | same |
| property lookup | start: wall flag bit \`02h\`; update: target OBJECT flags \`06h\` | same conditions; differently located arrays |

This is **not** a general 28-byte OBJECT scheduler; it iterates only the
*active six-byte PUSH records* indexed into the separate OBJECT array.
The complete generic OBJECT/animation scheduler remains unlocated/unclosed.

## Instruction-exact branch and write sequence

DOS v2.0 addresses are **offsets in the unpacked MZ load image**:

| Offset | Recovered effect |
| --- | --- |
| \`0DF8\` | StartPush, retrieves six-byte record via helper |
| \`0E12\` | refuse if \`PUSH+4 != 0\` |
| \`0E21\` | test the target **wall** property byte \`& 02h\`; reject when nonzero |
| \`0E33/0E3F\` | copy signed movement components to \`PUSH+2/+3\` |
| \`0E43\` | set \`PUSH+4=8\`; invoke separate helper at \`0E48\` |
| \`0E50\` | updater entry; walks six-byte PUSH array |
| \`0E65/0E71\` | live count / active-\`+4\` checks |
| \`0E7A\` | object reference \`index*28+6\` |
| \`0E8C..0EB0\` | signed 8-bit step added to 16-bit OBJECT X/Y |
| \`0EB3..0EC2\` | coordinate → MAP-cell far pointer computation |
| \`0EDF/0EF5\` | target OBJECT property table and conditional \`&06h\` block test |
| \`0EFB..0F1E\` | if MAP pointer changed, transfer source object-layer byte to destination and clear source |
| \`0F23..0F38\` | write OBJECT X/Y and updated 32-bit MAP pointer |
| \`0F50\` | far-call spatial X/Y sorted-index reorder helper |
| \`0F5B\` | **only after accepted commit/helper:** decrement \`PUSH+4\` |
| \`0F5F..0F6C\` | advance record pointer by **6**; reread live pool count |
| \`0F73\` | RETF |

Win16 v1.10 exact matching instruction positions:
\`21B6\` StartPush, \`21E0\` wall bit \`02h\`, \`2202\` countdown 8;
\`2210\` updater, \`2231\` active check, \`223A\` object index,
\`2273\` map-offset formula, \`22B5\` object property \`06h\`,
\`22CC..22DE\` byte transfer, \`22E3..22F8\` object commit,
\`2310\` sort-helper far call, \`231B\` counter decrement,
\`231F\` stride 6 and \`2333\` RETF.

## Exact independent update contract (pseudocode)

\`\`\`text
for i = 0 while i < read_live_push_count():  # count reread
    p = PUSH_ARRAY[i]                         # six-byte entry
    if p.remaining == 0:
        continue

    obj = OBJECT_ARRAY[p.objectIndex]        # 28-byte OBJECT entry
    newX = wrap_u16(obj.worldX + sign_extend_i8(p.dx))
    newY = wrap_u16(obj.worldY + sign_extend_i8(p.dy))
    newCell = cell_far_pointer(newX, newY)

    prop = OBJECT_PROPERTIES[newCell.objectLayerByte]
    if newCell != obj.savedCellFar and (prop & 0x06) != 0:
        continue                             # NO decrement; NO sort/commit

    if newCell != obj.savedCellFar:
        newCell.objectLayerByte = obj.savedCellFar.objectLayerByte
        obj.savedCellFar.objectLayerByte = 0

    obj.worldX = newX
    obj.worldY = newY
    obj.savedCellFar = newCell
    update_sorted_spatial_indices(obj, sign_extend_i8(p.dx),
                                       sign_extend_i8(p.dy))
    p.remaining -= 1
\`\`\`

Important: \`prop & 0x06\` is a flag test, not a test of whether the target
object byte is nonzero. The original update may **overwrite an existing
nonblocking object-layer byte**. In contrast, modern
\`LevelState::cellAllowsPushTarget()\` and the v0.31 defensive blocked-step
check currently require an empty destination; that is a **known parity
divergence in the abstract model** unless the target property's exact
flag construction makes all occupied cells block in every reachable case.
Do not silently force the "empty" assumption into the original reference.

Also, the map-cell old/new test is a **full far-pointer equality**, not a
comparison of tile coordinates. The updater uses live count, not a
pre-captured immutable count. Potential callback-driven count changes and
far-pointer consistency must be tested separately.

### MAP cell formula

Original register sequence at DOS \`0EB3..0EC2\` / Win16 \`2273..2282\`:

\`\`\`text
CX := newX
CL := CL & DFh
CX := SAR(CX, 5)
AX := newY
AL := AL & C0h
AX := AX * 2 + CX + mapBase  (mod 65536)
\`\`\`

For valid world coordinates \`0..4095\`, simplifies to:

\`MAP_byte_offset = mapBase + 128 * floor(y/64) + 2 * floor(x/64)\`

DOS mapBase \`373Eh\`, Win16 mapBase \`A69Eh\`, with different data
segments. \`N3DV033PushScheduler.hpp\` preserves the *register-level*
16-bit signed-shift/word-wrap behavior, not only this valid-range shortcut.

## Additional static closure: X/Y sorted-list update

The DOS \`0F50\` far-call target \`0AEA:015E\` maps to unpacked MZ
load-image offset **0xAFFE**. Its direct disassembly shows:

- \`AFFE\`: entry; OBJECT \`+14h\` indexes **X-sorted** far-pointer list
  \`DS:D516h\` (four bytes/entry).
- \`B014..B0BC\`: signed X delta drives forward or backward adjacent-pointer
  swaps; compare neighbor OBJECT \`+10h\` with current X, update both cached
  ordinal indices.
- \`B0BE\`: OBJECT \`+16h\` indexes **Y-sorted** far-pointer list
  \`DS:DA8Eh\`.
- \`B0CE..B17D\`: signed Y delta drives analogous strict-neighbor swaps
  and index adjustments; equal coordinates do not cause swaps.

Thus the order is **OBJECT coordinate/MAP commit → X sorted-list adjustment
→ Y sorted-list adjustment → decrement PUSH countdown** for the accepted
branch. The updater's Win16 callsite has the same structure, but the target
helper binary has **not** independently been compared instruction-by-instruction,
so this is not proof of entire transitive Win16 helper parity.

## FAST chronology correction

DOS FAST direct call chain in v0.29 remains:

\`\`\`text
C51A → 0A40 → 5F26 → A19A → A4A2 → 0E50[PUSH]
      → A4AC → A0CC → 89A2 → 9026 → (conditional 89A2)
\`\`\`

Only **the direct target identity of 0E50** is now closed, not the
whole call graph or tick order. \`0E50\` may invoke the spatial reorder
helper, and other FAST callees may invoke nested work. Do not treat
\`0E50\` as an OBJECT-wide scheduler or claim the exact global
FAST/MAIN order is now proven.

## Tools, tests and evidence boundary

The new strict verifier independently parses DOS MZ and Win16 NE bytes,
requires both exact SHA-256s **before** applying offsets, and checks all
292 bytes with the nine whitelisted relocation-operand spans:

\`\`\`sh
python tools/n3d_v033_push_verify.py \
    --dos20 /path/to/N3D_DOS_v2.0_IDA.EXE \
    --win16 /path/to/nite3w_v110.exe
\`\`\`

It also validates short original-code witnesses for StartPush,
blocked/accepted update, MAP object-layer copy, post-commit callback,
counter decrement, direct FAST call and the DOS X/Y sorted-list helper.
Synthetic C++/Python tests use no original assets; original executable
bytes must stay private. No original CPU runtime trace was made.

**Statically closed:** exact 0E50 identity and its per-record branch/field
semantics; 292-byte cross-build updater control-flow equivalence (masked
address operands); signed block mask; accepted-map-layer transfer; step
deadline; and DOS X/Y list-reorder helper structure.

**Still open:** generic OBJECT scheduler identity, full writer/callback
chronology, live reachable cases where nonblocking object contents are
overwritten, exact runtime count mutation, other historical build pairing,
DEMO seed/RNG total order, and pixel-perfect renderer. No parity-percentage
increase is warranted for full game 1:1.
