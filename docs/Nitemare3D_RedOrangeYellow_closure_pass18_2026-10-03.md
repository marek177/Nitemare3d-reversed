# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 18

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- far runtime targets are linearized as `segment*16 + offset` only when the actual
  machine call establishes that mapping

## Result

Pass 18 closes the complete contiguous range:

`0xDE36 .. 0xE9DB`

as **GREEN / deep static semantics**.

Total span: **2,982 bytes**

- bounded executable routine content: **2,978 bytes**
- inter-function alignment NOPs: **4 bytes**

The span contains:

- the complete DOS one-line text editor;
- editable menu/text-row wrapper;
- instruction-markup directive parser;
- formatted instruction/document page renderer;
- BSF paged document/help/order viewer;
- BSF order/purchase text output helper;
- gameplay-screen preparation;
- the complete gameplay-session loop and post-session ending/statistics routing.

This pass also corrects an important coordinate mistake retained in an older audit:
`E2FC`'with formatted-input call is **not** the base-image FLI area around `46C4`.
The actual far call is `11EE:27E4`, which maps to high image `0x146C4`, the already
closed `sscanf`-equivalent runtime wrapper.

---

# 1. image `0xDE36..0xE1DD` — `EditSingleLineText`

Length: **936 bytes**

This is the full DOS single-line editor.

The caller supplies:

- near text buffer;
- display X/Y;
- field width/height parameters;
- maximum character count;
- two style/color bytes.

## Initial draw

The routine:

1. draws the editor field/background;
2. draws the existing string;
3. measures its pixel width through `D2C0`;
4. computes current string length;
5. starts the cursor at the end of the existing string.

## Cursor blink / idle polling

When no input event is available:

- the editor alternates two tiny cursor-draw states;
- between them it waits `50` game-clock units;
- it polls twice before returning to the normal edit loop.

The acceptance-width calculation explicitly reserves the advance width of:

`'_' = 0x5F`

for the cursor.

## Plain key handling

Exact direct events:

```text
0x08  Backspace
0x0D  Enter
0x1B  Escape
0xE0  extended-key prefix
```

### Enter

Sets accepted flag and returns the original buffer pointer.

### Escape

Returns NULL/zero.

### Backspace

If cursor position is nonzero:

1. move cursor one character left;
2. subtract that glyph'with advance from pixel cursor X;
3. shift the remainder of the string left;
4. redraw the changed portion.

## Extended-key handling

After `0xE0`, it reads one more event.

Recovered scan codes:

```text
0x4B  Left
0x4D  Right
0x47  Home
0x4F  End
0x53  Delete
```

### Left / Right

Move the logical cursor and update pixel X by the selected glyph'with advance width.

### Home

Reset cursor index to zero and pixel X to field start.

### End

Recompute the full current text width and move cursor to the terminating NUL.

### Delete

If not already at end:

- shift the remaining bytes left by one;
- redraw the changed suffix.

## Printable insertion

For other key values the routine requires:

1. the input/glyph attribute byte at `DS:2369 + key` to pass mask `0x57`;
2. `currentPixelWidth + newGlyphWidth + cursorWidth < fieldWidth`;
3. current string length `< maxCharacters`.

If accepted:

- shift the suffix one byte to the right;
- insert the character at the current cursor index;
- redraw;
- increment cursor position.

There is no hidden dynamic allocation: the caller owns the text buffer.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xE1DE..0xE2FB` — `EditMenuTextRow`

Length: **286 bytes**

Input is and far pointer to and menu/record structure.

Relevant fields:

```text
record+0x0A  display-position pair
record+0x0E  far pointer to current text
```

AND 41-byte local buffer is initialized to zero.

If the existing record text differs from the routine'with sentinel/default text resource,
the current value is copied into the local buffer.

The routine then invokes `EditSingleLineText` with:

- the record'with display position;
- fixed editor dimensions;
- maximum editable length;
- style values derived from the UI palette helper.

If editing is accepted:

- exactly 41 bytes from the local editor buffer are copied back to the record'with text
  storage.

Finally the field/frame and current text are redrawn.

Return is boolean-like:

- `1` when the editor accepted the value;
- `0` when it was cancelled/not accepted.

This is the function used by interactive-menu row type 4.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xE2FC..0xE51E` — `ParseInstructionMarkupDirective`

Length: **547 bytes**

This is not gameplay logic.  It parses `%` directives embedded in the game'with
instruction/help/order text.

## Runtime parser correction

The raw formatted-input calls are:

`CALL FAR 11EE:27E4`

which maps to image:

`0x146C4`

The high-image routine is the already closed `sscanf`-equivalent wrapper.

Therefore old pseudo-C references to base `FUN_1000_46C4` must not be used here.

## Recognized directive letters

The parser accepts:

```text
B
C
b
c
d
o
p
```

Each directive increments the caller'with parsing counters and can update:

- current drawing/color state;
- and caller-provided byte state;
- and small output/resource descriptor.

## Numeric validation

The directive families use formatted numeric parsing and enforce exact ranges including:

- selected color/index values `<= 15`;
- one object/resource value `<= 255`;
- another selector value `<= 31`.

Out-of-range or malformed values enter the executable'with instruction-format fatal/error
path.

## Fixed-color directive

One directive routes directly through palette/color index:

`8`

without parsing and caller-supplied numeric value.

## Resource/image directives

Two directive classes call different resource/image helper paths and can populate the
output descriptor later consumed by the page renderer.

## Literal tail

After processing and directive the function advances through following literal bytes
until:

- NUL; or
- the next `%`.

It tracks the literal/directive-line length and rejects and value of eight or more
through the `"Too many instr..."` fatal path.

Return is the far pointer to the next parsing position plus the updated caller
counters/state.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xE520..0xE6D7` — `RenderInstructionMarkupPage`

Length: **440 bytes**

This renders one page of the game'with instruction/help/order markup language.

## Header

The routine:

1. obtains the configured text/UI color;
2. draws the page background/frame;
3. formats and short heading into and local 40-byte buffer;
4. draws that heading.

## Page body

Rendering starts at approximately:

`Y = 7`

and advances by:

`11`

for each text row.

The page terminator is:

`'#'`

AND NUL also terminates the text stream.

## Markup

When `%` is encountered:

- call `ParseInstructionMarkupDirective`.

If that directive produces and temporary far bitmap/resource:

- draw it through the DOS bitmap renderer;
- free the temporary far buffer immediately afterward.

## Literal characters

Ordinary bytes are drawn through `D326`.

Special spacing rules:

### Space

Advance horizontal position by exactly:

`6`

pixels.

### Tab

Align the logical text column to the next four-column boundary, then convert the
resulting column position to the renderer'with horizontal spacing.

### Newline

Advance to the next 11-unit row and reset horizontal position.

The routine protects the screen-page bounds and has and fatal path for instruction text
that would create too many lines.

On completion it restores/synchronizes display state through the VGA page helper.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xE6D8..0xE8BB` — `RunPagedBsfDocumentViewer`

Length: **484 bytes**

This is the generic viewer for BSF text blocks.

Recovered ABI:

```text
param1 = PCX/background resource index
param2 = BSF selector
```

The second parameter is passed directly to:

`BsfDispatch`

closed in pass 12.

Therefore the viewer can be used for the known BSF text classes such as HELP,
order/purchase text and Episode-1 transition/ending text.

## Resource acquisition

1. select font bank 1;
2. load the selected BSF text block;
3. keep its far pointer for the life of the viewer;
4. count `'#'` delimiters to determine page count.

Page numbering begins at 1.

## Initial page

The function:

- switches presentation mode;
- loads the caller-selected PCX/background;
- calls `RenderInstructionMarkupPage`;
- applies the matching display/palette transition.

## Input loop

Input comes from the already closed high-level DOS input translator.

### Escape (`0x1B`)

Sets the viewer exit flag.

### Event `0x44`

Runs and special prompt/delay/external-output path and redraws the current page.

This is associated with the order/help document machinery; the exact user-facing key
label is not required to reproduce the machine behavior.

### Previous-page family

Events in the `0x48/0x49` family search backward for the preceding `'#'`.

The page counter is decremented.

### Next-page family

Events in the `0x50/0x51` family search forward for the next `'#'`.

The page counter is incremented.

Navigation does not use and prebuilt page-offset table; it searches the resource text.

## Cleanup

On exit:

- run the viewer/status cleanup path;
- free the BSF text block through the recovered far heap;
- restore font bank 2.

The raw function ends at `E8BB`.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xE8BC..0xE914` — `EmitBsfOrderBlockCharacters`

Length: **89 bytes**

This routine requests:

`BsfDispatch(4)`

which is the BSF **order/purchase/exit text block**.

It walks the returned byte stream and, while the current/next bytes satisfy the
terminating conditions, sends each character to and formatted-output runtime wrapper.

The formatted-output callee is and high-image CRT output routine, not the unrelated
base-image renderer function once suggested by stale decompiler xrefs.

After output:

- free the allocated BSF block through `FarHeapFree16`.

This is the engine-level character-output path for the BSF order block.

**Status: YELLOW -> GREEN.**

---

# 7. image `0xE916..0xE962` — `PrepareGameplaySessionDisplay`

Length: **77 bytes**

This formerly weak routine now resolves cleanly because every major callee is known.

Exact sequence:

1. send one fixed status/log resource through `47D8`;
2. `RunPaletteTransitionEffect(3)`;
3. load PCX/resource screen `5`;
4. `BF6A` — prepared frame + HUD + VGA synchronization;
5. load PCX/resource screen `5` again;
6. `RedrawHudSection(0)`;
7. `RunPaletteTransitionEffect(2)`;
8. `TickLightningPaletteFlash(1)` — reset/init its palette-flash state.

This is the visual/runtime setup immediately before the scheduler-driven gameplay
session begins.

**Status: weak/unresolved -> GREEN.**

---

# 8. image `0xE964..0xE9DA` — `RunGameplaySessionAndPostSequence`

Length: **119 bytes**

This is the complete high-level gameplay-session loop.

## Session start

1. call `PrepareGameplaySessionDisplay`;
2. set:
   `DS:3CD4 = 1`
   — active gameplay state.

## Scheduler loop

Repeatedly run:

`C1A8 = RunPeriodicGameScheduler`

until game state becomes either:

- `0`; or
- `3`.

If state is `3`:

- apply palette/display transition mode `4`.

## Immediate cleanup

After leaving the scheduler loop:

- clear `DS:3CD1`;
- stop active SFX through `C51C`;
- select/start music track `12` through `C548`;
- restore/select font bank `2`.

## Special post-death story/statistics path

If:

```text
DS:430C != 0
and
player HP DS:4189 == 0
```

the routine calls the paged BSF viewer with packed arguments:

```text
background resource = 16
BSF selector         = 5
```

Selector 5 is the known Episode-1 ending/transition BSF block.

After the document:

- display the level/session statistics screen `DCD0`.

## Ending animation

If:

`DS:430D != 0`

call:

`AC98 = PlayEndingFliSequence`

which enters the already closed `ENDING.FLI` path.

Therefore the high-level flow is now explicit:

```text
prepare gameplay display
    ↓
active scheduler loop
    ↓
audio/presentation cleanup
    ↓
optional BSF story/ending page
    ↓
optional statistics
    ↓
optional ENDING.FLI
```

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 9. Byte-map impact

New continuous GREEN span:

`0xDE36 .. 0xE9DB`

Total: **2,982 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `DE36–E1DD` | 936 | full single-line text editor |
| `E1DE–E2FB` | 286 | editable menu/text row |
| `E2FC–E51E` | 547 | instruction-markup directive parser |
| `E520–E6D7` | 440 | formatted instruction-page renderer |
| `E6D8–E8BB` | 484 | paged BSF document viewer |
| `E8BC–E914` | 89 | BSF order-block character output |
| `E916–E962` | 77 | gameplay display preparation |
| `E964–E9DA` | 119 | gameplay session + post-sequence |

Executable routine content: **2,978 bytes**.

Inter-function alignment:

```text
E51F
E915
E963
E9DB
```

Total: **4 bytes**.

NOPs inside the large editor/parser bodies are internal branch-alignment bytes and are
already part of those function ranges.

---

# 10. Important old-analysis corrections

## `E2FC`

Old descriptions that name and call to:

`FUN_1000_46C4`

are coordinate artifacts.

The actual machine call:

`11EE:27E4`

maps to:

`image 0x146C4`

which is the `sscanf`-equivalent runtime routine.

Base `0x46C4` belongs to the already closed FLI decoder/player neighborhood and must
not be connected to this parser.

## `E916`

Replace weak generic label:

`InvokeFixedResourceAndStatusSequence`

with:

`PrepareGameplaySessionDisplay`

because all major called operations are now individually identified.

## `E964`

The function is not merely an opaque session wrapper.  Its complete scheduler exit and
post-session story/statistics/FLI routing is statically explicit.

---

# 11. Cumulative closure

Pass 17 cumulative since the pass-5 baseline:

`33,860 bytes`

Pass 18 adds:

`2,982 bytes`

New cumulative total:

**36,842 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–18.

---

# 12. Next target

Continue at:

`0xE9DC`

The next continuous region is the actual menu engine:

- `E9DC` — draw one 18-byte menu row;
- `EB44` — move menu selection while skipping disabled/type-6 rows;
- `EBD6` — full interactive-menu input engine;
- `EDA2` — dynamic level/list selector;
- `EE64`, `EF06`, `F040` — specialized choice dialogs;
- `F114` — flagged card/control action;
- `F150/F1F2/F33A` — hardware/control/cheat settings;
- then save/load and in-game menu paths.

Because these functions are already strong cross-version matches, the next pass should
be able to convert another large UI/menu band to GREEN and directly reduce the
remaining YELLOW count.