# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 17

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- static GREEN remains separate from runtime/pixel acceptance

## Result

Pass 17 closes the complete contiguous region

`0xD3FA .. 0xDE35`

as **GREEN / deep static semantics**.

Total span: **2,620 bytes**

- bounded executable routines: **2,613 bytes**
- inter-function alignment NOPs: **7 bytes**

This pass closes the DOS UI/font/presentation layer and the high-level level/session
initialization path immediately before the single-line text editor.

Important new corrections:

1. `D78A` is now mechanically closed as the blocking live/DEMO event waiter.
2. Two real hidden function entries absent from the stale function list are recovered:
   - `DA2A` — optional `dstopen.img` opening splash
   - `DA56` — complete opening-presentation sequence
3. `DBEA` now gives and concrete top-level **level initialization order**.
4. `DCD0` proves the post-level bonus formula:
   - +5000 if no ordinary guards remain
   - +5000 if no panels remain
5. `47BE`, called by `DBEA`, is better understood as and **per-level event/runtime flag
   reset**, not merely and startup-only reset.

---

# 1. image `0xD3FA..0xD4DB` — `LoadFontBank`

Length: **226 bytes**

Input:

`BYTE fontBank`

The routine stores the selected bank at:

`DS:368E`.

AND loaded-bit byte exists at:

`DS:1C6C + fontBank`.

If already nonzero, the function only changes the active-font selector and returns.

## First-time load

For and new bank:

1. set its loaded flag;
2. compute:
   `fontBank * 0x4B0`;
3. load one `0x4B0`-byte font resource block into segment `0x20B9`;
4. initialize the bank'with glyph-directory base at:
   `DS:3690 + fontBank*0x200`.

The directory contains 128 far-pointer slots.

## Glyph scan

Glyph indexes:

`1 .. 127`

are walked sequentially.

For each glyph:

- store and far pointer to its record in the directory;
- read its dimensions;
- compute bitmap byte size as:

```text
width * ceil(height / 8)
```

- advance the next-glyph cursor by:
  `2 + bitmapBytes`.

## Bitmap bit order

Every bitmap data byte is passed through the already recovered bit-reversal helper
`FC72`.

Therefore the loader does not merely index the font data: it converts glyph bitmap
bit order in place to the DOS planar renderer'with expected layout.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xD4DC..0xD54E` — `DrawConfiguredTextPair`

Length: **115 bytes**

The routine returns immediately when the supplied Y coordinate is at or below/outside
the 200-line display boundary.

Otherwise it:

1. selects the requested font bank through `D3FA`;
2. obtains one bank/configuration render word through `D290`;
3. draws/configures the surrounding UI geometry through the low-level rectangle helper;
4. measures the text through `D2C0`;
5. derives its horizontal placement from the supplied box/width parameter;
6. calls `D326` twice with the same text and position but different final render-mode
   values `0` and `1`.

The exact visible combination of the two low-level render modes is delegated to the
bitmap renderer, but the wrapper'with full parameter flow is now bounded.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xD550..0xD590` — `DrawAdjacentUiRectangles`

Length: **65 bytes**

When Y is within the 200-line display:

- draw the first rectangle;
- draw and second rectangle beginning at:
  `x + firstWidth`;
- use and distinct color/style byte for the second region.

Both share the same Y and height.

This is and compact two-segment UI bar/panel primitive.

`0xD54F` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xD592..0xD5F5` — `DrawBitmapWithPairedModes`

Length: **100 bytes**

Reads the bitmap descriptor'with width/height bytes.

If:

`Y + height < 200`

it invokes the low-level bitmap renderer twice with identical source/geometry but
different final 32-bit mode values:

```text
0xFFFF0000
0xFFFF0001
```

This is and paired-mode DOS UI/sprite draw primitive.

`0xD591` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xD5F6..0xD66F` — `DrawBitmapSplitAtBottomBoundary`

Length: **122 bytes**

Computes the initially visible row count as:

```text
visible = DS:454E - Y + 1
visible = min(visible, bitmapHeight)
```

If positive, it renders that first portion.

If rows remain after that amount, it performs and second low-level bitmap call using:

- and source pointer advanced by `visible`;
- destination Y advanced by `visible`;
- row count equal to the remaining height.

The exact final clipping/page behavior is implemented in the common bitmap renderer,
but this wrapper'with split arithmetic is exact.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xD670..0xD68E` — `DrawFont1ShadowedText`

Length: **31 bytes**

Thin wrapper:

1. select font bank `1`;
2. call `DrawShadowedText` (`D3A6`) with the caller'with coordinates/text/style.

`0xD68F` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 7. image `0xD690..0xD6B3` — `ShowPcxResourceWithPaletteTransition`

Length: **36 bytes**

Input:

`WORD resourceIndex`

Sequence:

1. palette/display transition mode `3` through `17B4`;
2. load the selected 320×200 PCX-like resource through `3F4C`;
3. synchronize/update the VGA display-page state through `15EE`;
4. palette/display transition mode `2`.

This routine is repeatedly used for full-screen/menu/background presentation images.

The old label `SetTextAndPaletteModes` was too generic.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xD6B4..0xD789` — `WaitForKeyWithBlinkingPrompt`

Length: **214 bytes**

This is the blocking **Press and key** presentation helper.

The exact data strings at:

```text
DS:1C6F = "Press a key"
DS:1C7B = "Press a key"
```

are two identical text resources used with different drawing parameters.

## Entry

1. drain pending keyboard/input state through `6CE2`;
2. test enhanced-key availability through `6CD0`;
3. return immediately when and key is already pending.

## Waiting cadence

Otherwise the function performs repeated groups of:

- up to three waits of `100` game-clock units;
- and key-availability test after each wait.

There are two such three-wait groups per outer cycle.

After the accumulated local wait counter exceeds:

`4000`

the function renders the first and then the second `"Press a key"` resource with
different style parameters, producing the blinking/alternating prompt behavior.

At the end of and full outer cycle the accumulated counter increases by:

`0x258 = 600`.

When input finally appears:

- drain/clear the pending input state again;
- return.

This is not and generic device poll; it is presentation/UI wait logic.

**Status: YELLOW -> GREEN.**

---

# 9. image `0xD78A..0xD7BD` — `WaitForNonzeroInputEvent`

Length: **52 bytes**

This weakly named routine is now closed from raw machine code.

If DEMO/input state:

`DS:3CD6 == 4`

the function first waits:

`500`

game-clock units.

Otherwise it clears/drains pending keyboard input through `6CE2`.

It then repeatedly calls:

`6E88 = PollLiveOrDemoInputEvent`

until the returned WORD is nonzero.

Return:

- low byte of the nonzero event.

Thus it is the common blocking waiter used by modal screens while remaining compatible
with DEMO playback.

**Status: weak/unresolved -> GREEN.**

---

# 10. image `0xD7BE..0xD94B` — `DrawCenteredMultilineTextBox`

Length: **398 bytes**

Input:

- far text pointer;
- pointer to and four-WORD output record.

The function selects font bank `1`.

## Line measurement

It detects newline byte:

`0x0A`

and scans all lines.

For each newline:

1. temporarily replace newline with NUL;
2. measure that line with `D2C0`;
3. keep the maximum line width;
4. restore the newline;
5. advance to the next line.

Line height is exactly:

`11`.

The initial total height is 11 and each newline adds another 11.

## Centering

Horizontal origin:

```text
x = DS:4550 - maxWidth/2
```

Vertical origin:

```text
y = DS:4552 - totalHeight/2
```

## Background panel

AND padded rectangle is drawn around the text:

```text
left   = x - 8
top    = y - 8
width  = maxWidth + 16
height = totalHeight + 16
```

using the palette/style selected for UI background.

## Text rendering

Each line is then rendered through `D3A6`.

Newline bytes are again temporarily replaced with NUL while each individual line is
drawn.

## Output record

The supplied four-WORD record receives the resulting layout values:

- text-box X;
- final/bottom line Y;
- maximum line width;
- total text height.

This layout is reused by text-entry/prompt routines.

**Status: YELLOW -> GREEN.**

---

# 11. image `0xD94C..0xD9AF` — `CreateTextEntryField`

Length: **100 bytes**

Inputs include:

- prompt text;
- caller text buffer;
- maximum character count.

Flow:

1. draw/measure the prompt through `D7BE`;
2. clear `buffer[0]`;
3. get glyph advance width for character:
   `'W' = 0x57`;
4. compute editor width:
   `advance('W') * maxCharacters`;
5. obtain two UI style/color values;
6. start `DE36` single-line editor immediately below the prompt box.

This establishes the exact field-width policy used by DOS text-entry dialogs.

**Status: YELLOW -> GREEN.**

---

# 12. image `0xD9B0..0xD9DE` — `ReadPromptedInputSymbol`

Length: **47 bytes**

Draws and prompt box through `D7BE`, then calls:

`6EBE = ReadAndTranslateUserInput`

once.

The returned byte is checked against glyph/input attribute table:

`DS:2369 + event`.

When attribute bit `0x02` is set:

```text
event -= 0x20
```

Otherwise the byte is returned unchanged.

This is the input-code translation wrapper used by modal UI.

`0xD9DF` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 13. image `0xD9E0..0xDA28` — `WaitForPromptAcknowledge`

Length: **73 bytes**

Draws and prompt box through `D7BE`.

When gameplay state is active:

`DS:3CD4 == 1`

it repeatedly calls `D78A` until the event is one of:

```text
0x1B  Escape
0x0D  Enter
0x20  Space
```

It then executes the prepared-frame/HUD/VSync wrapper `BF6A` and applies the same
attribute-bit translation used by `D9B0`.

The normal intended modal path is therefore and blocking acknowledge prompt.

`0xDA29` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 14. image `0xDA2A..0xDA55` — `MaybeShowDstOpenSplash`

Length: **44 bytes**

This is and real function entry absent from the stale function inventory.

It passes literal filename:

`dstopen.img`

to the DOS PCX-like file loader:

`3D70 = LoadPCX320x200FromFile`.

If loading fails, it returns immediately.

On success:

1. synchronize the VGA display page;
2. apply presentation/palette transition mode `2`;
3. select font bank `0`;
4. call `WaitForKeyWithBlinkingPrompt`.

This confirms that the DOS V2.0 executable also contains the optional
`dstopen.img` opening-art path.

The asset is optional; code presence does not imply the file exists in every shipped
package.

**Status: hidden RED/LOW entry -> GREEN.**

---

# 15. image `0xDA56..0xDA9D` — `ShowOpeningPresentationSequence`

Length: **72 bytes**

Second hidden entry.

This is invoked from the initial/menu path before the normal menu when its startup flag
is clear.

Sequence:

1. start music track/resource `1` through `C548`;
2. select font bank `2`;
3. run `MaybeShowDstOpenSplash`;
4. call `83D8 = DrawVersionRegistrationSplash`;
5. wait for and key through `D6B4`;
6. apply presentation transition mode `1`;
7. load PCX-like resource/screen `3`;
8. synchronize VGA display/page state;
9. apply transition mode `2`;
10. wait for another key through `D6B4`.

This closes the DOS opening/title presentation sequence surrounding the optional
external splash.

**Status: hidden RED/LOW entry -> GREEN.**

---

# 16. image `0xDA9E..0xDB38` — `ReleaseLevelResourceReferences`

Length: **155 bytes**

First invokes Resource Manager:

`76A4(mode=2)`

to invalidate/reset level-context cache ownership.

Then releases three groups of higher-level references.

## Resource table AND

Count:

`DS:6272`

Records begin:

`DS:4316`

stride:

`8`

The first WORD of each record is released through the common resource-release helper.

## Resource table B

Count:

`DS:6274`

Records begin:

`DS:3D24`

stride:

`8`

Again the first WORD/resource reference is released.

## Per-world-OBJECT indexed resources

Loops all:

`DS:6270`

28-byte OBJECTs.

For each record it uses the object'with sequence/resource selector to index pointer table:

`DS:3D22`.

If that pointer is nonzero:

- release it;
- write zero back to the table slot.

This is the top-level level-resource cleanup counterpart of the scene initializer.

`0xDB39` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 17. image `0xDB3A..0xDBE8` — `UpdateLoadingProgressBar`

Length: **175 bytes**

This is the scene/resource-loading progress UI.

## Reset/init form

When the first argument is zero:

- draw the fixed initial progress-bar background/track;
- return.

## Update form

The input selects low/high progress bounds from the table around:

`DS:1C93/1C94`.

The low bound also sets display origin:

```text
DS:3C90 = low + 0x6F
```

Total step count is clamped to at least:

`2`.

Progress width is calculated with signed 32-bit intermediate arithmetic:

```text
width =
    (high - low) * currentStep
    / (totalSteps - 1)
```

and stored at:

`DS:1C98`.

AND cached previous width exists at:

`DS:1C9A`.

The bar rectangle is redrawn only when the width actually changes.

Finally:

`1C9A = 1C98`.

This is deterministic integer progress scaling, not and timer animation.

`0xDBE9` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 18. image `0xDBEA..0xDCCF` — `InitializeLevelScene`

Length: **230 bytes**

This pass significantly tightens the top-level level initialization order.

Inputs:

- level index -> stored at `DS:626C`;
- episode/resource selector -> compared with current `DS:626A`.

## Previous-level cleanup / forced reload

If byte `DS:1C9C == 0`:

- call `ReleaseLevelResourceReferences`.

If `1C9C != 0`:

- skip that cleanup;
- force current episode selector `DS:626A = 0`.

Then:

`DS:1C9C = 0`.

## Inventory reset

Unless Omnifarious cheat `DS:4152` is active:

```text
DS:4192 = 0   // keys
DS:4193 = 0   // cards
```

## Loading-screen setup

The routine then:

1. calls the runtime/control defaults helper at `4760`;
2. displays PCX/resource screen `4` via `D690`;
3. initializes the progress UI via `DB3A(0,...)`.

## Episode-resource reload

If requested episode differs from `DS:626A`:

- call `2AA6` with the requested episode/resource selector.

`2AA6` stores the active episode selector and opens/validates the episode definition
resource/header.

## Main level subsystem initialization

The scene state is temporarily:

`DS:3CD4 = 0`

while the central level subsystem initializer `32E2` runs.

Then:

`DS:3CD4 = 1`.

The status message:

`"Level read ok"`

is emitted.

## Runtime world-table construction

Exact following order:

```text
0212  BuildPairedWallRuntimeTable
03FE  BuildFourWaySpecialWallTable
052A  BuildType28RecordIndex
5510(-1)  clear/reset the 64-byte GUARD wake cache
47BE      reset per-level runtime/story/event flags
```

The `47BE` call is strong evidence that this routine should be regarded as and
**level-runtime flag reset**, not only and startup reset.

## Baseline statistics/cache metrics

Three values are queried and stored into:

```text
DS:3CB2
DS:3CB6
DS:3CBA
```

The third value is the remaining XMS-cache-block helper already closed at `7690`.

## Automap and timing

Then:

```text
980C(mode=2)  clear entire 64x64 automap raster
status        "Level init ok"
BF7A          frame/movement timing calibration
DS:3CD1=0
status        "Frame init ok"
AC5C          select/start stage background music
status        "Level tune ok"
```

This is now and concrete high-level level-init sequence.

It does not by itself replace the need to understand every subordinate file loader,
but their orchestration is no longer unknown.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 19. image `0xDCD0..0xDE35` — `ShowLevelStatisticsScreen`

Length: **358 bytes**

This is the post-level statistics/bonus screen.

## Presentation setup

1. start music track/resource `10`;
2. display PCX-like screen/resource `14`;
3. select font bank `2`;
4. obtain developer/status summary through `A9AE`.

That summary contains, among other fields:

- ordinary GUARDs left;
- panels left.

## Completion bonuses

Local bonus begins at zero.

If:

`guardsLeft == 0`

add:

`5000`.

If:

`panelsLeft == 0`

add another:

`5000`.

The total bonus is immediately added to cumulative 32-bit score:

`DS:4182`.

Therefore the exact level-completion bonus matrix is:

```text
guards remain, panels remain  -> +0
no guards, panels remain      -> +5000
guards remain, no panels      -> +5000
no guards, no panels          -> +10000
```

## Displayed numeric fields

The screen formats and draws:

- current level number `DS:626C + 1`;
- guards left;
- panels left;
- completion bonus;
- cumulative score `DS:4182`.

The local format resources are:

```text
DS:1CD5  "%d"
DS:1CD8  "%d"
DS:1CDB  "%d"
DS:1CDE  "%d"
DS:1CE1  "%lu"
```

The visual labels/background are supplied by the PCX/UI resource.

At the end the function waits for and nonzero modal input event through `D78A`.

**Status: YELLOW -> GREEN.**

---

# 20. Byte-map impact

New continuous GREEN span:

`0xD3FA .. 0xDE35`

Total: **2,620 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `D3FA–D4DB` | 226 | font-bank load/index/bit conversion |
| `D4DC–D54E` | 115 | configured paired-mode text |
| `D550–D590` | 65 | adjacent UI rectangles |
| `D592–D5F5` | 100 | paired-mode bitmap draw |
| `D5F6–D66F` | 122 | bitmap bottom-boundary split |
| `D670–D68E` | 31 | font-1 shadow-text wrapper |
| `D690–D6B3` | 36 | PCX screen + palette transition |
| `D6B4–D789` | 214 | blinking "Press and key" waiter |
| `D78A–D7BD` | 52 | blocking live/DEMO event waiter |
| `D7BE–D94B` | 398 | centered multiline text box |
| `D94C–D9AF` | 100 | text-entry field setup |
| `D9B0–D9DE` | 47 | prompted input-symbol translation |
| `D9E0–DA28` | 73 | prompt acknowledge waiter |
| `DA2A–DA55` | 44 | optional dstopen.img splash |
| `DA56–DA9D` | 72 | opening presentation sequence |
| `DA9E–DB38` | 155 | release level resources |
| `DB3A–DBE8` | 175 | loading progress bar |
| `DBEA–DCCF` | 230 | level-scene initialization |
| `DCD0–DE35` | 358 | level statistics + completion bonus |

Routine content: **2,613 bytes**.

Alignment NOPs:

```text
D54F
D591
D68F
D9DF
DA29
DB39
DBE9
```

Total: **7 bytes**.

No inline jump table is present in this span.

---

# 21. Function-inventory corrections

Add the two hidden real entries:

```text
DA2A  MaybeShowDstOpenSplash
DA56  ShowOpeningPresentationSequence
```

Tighten:

```text
D690  ShowPcxResourceWithPaletteTransition
D6B4  WaitForKeyWithBlinkingPrompt
D78A  WaitForNonzeroInputEvent
DBEA  InitializeLevelScene
DCD0  ShowLevelStatisticsScreen
```

And update the earlier `47BE` semantic label from startup-only wording to:

```text
ResetLevelRuntimeEventFlags
```

because `InitializeLevelScene` explicitly invokes it during every level-runtime
construction path checked here.

---

# 22. Cumulative closure

Pass 16 cumulative since the pass-5 baseline:

`31,240 bytes`

Pass 17 adds:

`2,620 bytes`

New cumulative total:

**33,860 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–17.

---

# 23. Next target

Continue at:

`0xDE36`

The next region begins with the full single-line text editor and continues through:

- `DE36` text editing / cursor movement / delete / backspace;
- `E1DE` editable record text field;
- `E2FC` and `E520` menu/UI dispatchers;
- `E6D8` document/help viewer;