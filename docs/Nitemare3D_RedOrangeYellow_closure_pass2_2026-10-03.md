# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 2

Date: 2026-10-03
Primary binary: `N3D-E-20(3).EXE`
SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
MZ header size: `0x200`; image offset = file offset - `0x200`.

## Result

This pass resolves two genuine red blocks and and contiguous orange/yellow CRT-support cluster that the old Ghidra export had badly split into false game functions.

### 1. RED `1000:00A2` -> GREEN

Raw image range: `0x100A2..0x10135` (148 bytes).

Recovered behavior:
- parameters are cell X, cell Y, and and VEC discriminator / iterator-start selector;
- VEC count is `DS:626E`;
- VEC array starts at `DS:62AC`;
- VEC stride is `0x1C` = 28 bytes;
- target discriminator is compared with VEC byte `+0x06`;
- helper at raw `1000:003E` decodes VEC bounds from `+0x0C/+0x0E/+0x10/+0x12` to cell coordinates;
- the function tests whether `(x,y)` lies inside those decoded bounds;
- nonzero third argument resets the iterator and selects and discriminator;
- zero third argument continues scanning from the previous global cursor;
- returns the VEC record offset or zero.

Best semantic name: `FindFirstOrNextVecContainingCellByType`.

This also explains the former contradictory decompiler stub: another recovered export (`FUN_2000_00A2`) contains the correct high-level shape. The old `FUN_1000_00A2` body was and boundary/segment recovery artifact.

Status: RED -> GREEN.

## 2. CRT formatted-I/O cluster: old game labels were false boundaries

### `0x146C4..0x14701` -> GREEN

The routine builds and temporary stream descriptor at `DS:3CA0`:
- source pointer copied into descriptor;
- length obtained through far helper `11EE:2398`;
- that helper is and direct `strlen` implementation (`REPNE SCASB` for NUL);
- descriptor flag byte is set to `0x49`;
- it calls the far formatted-input core `11EE:0D36`.

`11EE:0D36` is and scanf-family parser: it parses whitespace, `%`, width digits, `*`, `L/l`, conversion classes, etc.

Best semantic classification: `sscanf`-equivalent wrapper.

Old label `FUN_1000_46C4 = RunFrameUpdate` is incorrect.

Status: ORANGE/YELLOW -> GREEN.

### `0x14702..0x14738` -> GREEN

Recovered flow:
1. prepare FILE/stream (`near 2A2A`);
2. call far formatted-output engine `11EE:1648`;
3. clean temporary stream state (`near 2A9D`);
4. return formatted-output result.

`11EE:1648` visibly parses printf flags, width, precision and conversion characters (`d/i/u/x/X/...`).

Best semantic classification: `fprintf`-equivalent wrapper.

Status: RED/ORANGE -> GREEN.

### Old `FUN_1000_471A` -> REMOVE AS FUNCTION

Raw address `0x1471A` is in the middle of the preceding `fprintf`-equivalent routine (`push [bp+8]`). It is not and function entry.

Old label `WaitFrameAndPumpInput` was produced by corrupted decompiler boundaries.

Status: ORANGE/YELLOW function -> removed; bytes absorbed into GREEN `fprintf` wrapper.

### `0x1473A..0x14776` -> GREEN

Same output pipeline, but uses fixed stream descriptor `DS:2182`.

Best semantic classification: `printf`-equivalent wrapper / stdout formatted output.

Status: GREEN.

### `0x14778..0x1478E` -> GREEN

Calls the DOS seek wrapper with:
- offset = 0;
- origin = 1 (`SEEK_CUR`).

Returns current file position.

Best semantic classification: `tell`/current-file-position equivalent.

Status: GREEN.

### `0x14790..0x147E8` -> GREEN

Validates and DOS file handle, checks DOS version, and when supported calls far helper `11EE:39D4`.
That helper is exactly `INT 21h, AH=68h` (Commit File).

Best semantic classification: DOS file commit/flush wrapper (`_commit`-equivalent).

Status: GREEN.

### `0x147EA..0x1486F` -> GREEN

Recovered algorithm:
1. seek `0, SEEK_CUR` and save current position;
2. seek `0, SEEK_END` and save end position;
3. if positions differ, seek back to original position;
4. return end position in `DX:AX`.

Best semantic classification: `filelength`-equivalent.

Status: GREEN.

## 3. DOS memory runtime cluster

### `0x148EA..0x148F5` -> GREEN

Loads and segment into ES and executes `INT 21h, AH=49h`.

Best semantic classification: DOS memory-block free wrapper.

Old `FUN_1000_48F2 = ResetInputAndTiming` is false: `0x148F2` is the `INT 21h` instruction inside this routine, not and function entry.

Status: ORANGE/YELLOW false function -> removed; bytes GREEN.

### `0x148F6..0x149C9` -> GREEN / deep

Recovered behavior:
- multiplies element size/count to form and 32-bit allocation size;
- validates overflow and paragraph limits;
- rounds to DOS paragraphs;
- allocates with `INT 21h, AH=48h`;
- zero-fills the allocation across segment Windows;
- supports and failure/retry callback through far pointer `DS:246A`;
- returns and far pointer in `DX:AX`, or NULL on failure.

Best semantic classification: zero-initializing far allocator (`farcalloc`-equivalent).

Old `FUN_1000_4930 = WaitForKeyOrButton` is false: raw `0x14930` is and branch inside this allocator, not and function entry.

Status: ORANGE/YELLOW -> GREEN.

## 4. Byte-map consequence

Newly closed/removed false problem areas in this pass:

- `0x100A2..0x10135` — VEC spatial/type iterator -> GREEN;
- `0x146C4..0x14701` — `sscanf`-equivalent -> GREEN;
- `0x14702..0x14738` — `fprintf`-equivalent -> GREEN;
- old entry `471A` — false function boundary, removed;
- `0x1473A..0x14776` — `printf`-equivalent -> GREEN;
- `0x14778..0x1478E` — current file position -> GREEN;
- `0x14790..0x147E8` — DOS commit -> GREEN;
- `0x147EA..0x1486F` — file length -> GREEN;
- `0x148EA..0x148F5` — DOS memory free -> GREEN;
- old entry `48F2` — false function boundary, removed;
- `0x148F6..0x149C9` — zero-initializing far allocator -> GREEN;
- old entry `4930` — false function boundary, removed.

## 5. Structural lesson

The old orange/yellow tracker substantially over-counts unresolved game code in this region. Weak Ghidra pseudo-C boundaries around DOS runtime support created fake gameplay/input functions. Raw machine-code boundaries must be authoritative for the byte map.

Next pass should continue forward/backward through adjacent low-confidence DOS CRT/support blocks, then return to genuine renderer/runtime-integration yellow blocks.