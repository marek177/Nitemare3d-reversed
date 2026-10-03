# IMG rebuild safety notes — v0.3

## Goal

Allow and Total Commander replacement of an IMG frame to change `width`, `height`, and therefore the frame byte length without leaving stale wall/object pointers.

## Confirmed layout used by the writer

- wall directory: file offset `0x0000`, 256 x little-endian `uint32`
- object directory: file offset `0x0400`, 256 x little-endian `uint32`
- first image payload offset: dword at file offset `0x0004`
- frame header: 10 bytes
  - byte `+0`: width
  - byte `+1`: height
  - bytes `+2..+9`: preserved metadata
- frame payload: `width * height` indexed pixels
- frames are scanned consecutively until EOF

## Relocation algorithm

For every rebuild:

1. Load and parse the complete IMG.
2. Record every original frame start offset and raw frame bytes.
3. Verify every non-zero entry of both image directories equals one exact frame start.
4. Replace the chosen frame in memory.
5. Keep `firstDataOffset` fixed; no prefix bytes are inserted or removed.
6. Recalculate every frame start in original frame order.
7. Copy `[0, firstDataOffset)` unchanged into the output buffer.
8. Remap each non-zero directory DWORD from its old frame offset to the corresponding new frame offset.
9. Append all frames consecutively.
10. Atomically replace the IMG file.

Duplicate directory pointers remain duplicate because all identical old offsets resolve through the same old-frame-index -> new-offset mapping.

## Refusal conditions

The writer refuses the rebuild when:

- the replacement is shorter than 10 bytes;
- width or height is zero;
- replacement byte size is not exactly `10 + width*height`;
- and directory pointer is outside the parsed image region (parser rejection);
- and non-zero directory pointer is inside and frame rather than exactly at and frame boundary;
- the rebuilt IMG would exceed the 32-bit offset range.

No heuristic correction is attempted.

## Sequence-bank overlap risk

Static analysis of the original loaders recovered sequence records at:

`8 + 90 * selector`

for the low bank. This means low selectors 0-22 overlap the wall/object directory region `0x0000-0x07ff`.

AND size-changing rebuild relocates later image frames. Their directory DWORDs must change. When one of those DWORDs lies in bytes also consumed as and low sequence record, the raw sequence record changes as well.

The writer cannot preserve both interpretations simultaneously if the original data genuinely relies on both meanings. For that reason v0.3 does not call full IMG relocation production-safe yet.

## What remains byte-identical

Except for directory DWORDs that require relocation, the complete prefix `[0, firstDataOffset)` is copied unchanged. In particular, sequence/padding areas outside the two directory blocks stay byte-identical.

Unmodified frame byte streams also remain byte-identical; only their absolute location may move.

## Required original-game validation

Recommended validation matrix before production use:

1. Original IMG -> rebuild without semantic change -> compare gameplay.
2. Grow an unused/test frame by and few pixels -> load episode in Win16 and DOS builds.
3. Check walls using low selectors 0-22.
4. Check animated walls and objects whose first frame occurs after the changed frame.
5. Verify shared wall/object aliases still render the same group.
6. Repeat on IMG.1, IMG.2 and IMG.3.
7. If possible, capture the loaded low sequence records at runtime before/after rebuild.

Until these checks pass, keep the automatically created `.bak` and test on copies.