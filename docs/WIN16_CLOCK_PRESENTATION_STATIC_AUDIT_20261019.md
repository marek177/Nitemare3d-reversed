# Win16 clock + presentation contract (static-first)

Date: 2026-10-19. Scope: Win16 Nitemare 3-D 1.0, 1.8, 1.10.
This note distinguishes *direct decompiler evidence*, *previous original-byte audit*,
and *remaining proof obligations*. It does not raise 1:1 parity percentages.

## Material and evidence boundary

- Win16 1.0: `NITE3W -10.EXE.c`; timer `3:D43E/D498`, window-size selector
  `FUN_1010_2D64`, presentation `FUN_1010_3006`.
- Win16 1.8: `NITE3W-18.EXE.c`; timer `3:D5BE/D618`, window-size selector
  `FUN_1010_2D50`, presentation `FUN_1010_300C`.
- Win16 1.10: `nite3w110.exe(20260927-130639).c`; timer `3:D66C/D6C6`,
  window-size selector `FUN_1010_2D9C`, presentation `FUN_1010_3080`.
- NE import/fixup anchors: `other/n3d/builds_12/static_byte_evidence/`.
- Binary-backed prior resource/MFC handler map:
  `docs/NITE3W_Menu_HUD_BINARNY_rozbor_2026-09-25.md`,
  resource type 4 ID 2, executable commands 0x8003/0x8004/0x8017.
- Prior original Win16 runtime scope: `docs/V051_REMAX_WIN16_WING_RUNTIME.md`
  reaches E1M1 in all five builds, but is **not** a pixel/timing parity oracle.
- Current work did not read raw original Win16 bytes or run the original game.
  The decompiled source excerpts and prior byte/fixup evidence were inspected.

## Timer contract: exact observed local decisions

The Win16 1.10 `FUN_1010_D66C(param)` decompilation shows:

1. `param == 0`: call `MMSYSTEM.604/timeGetDevCaps`; assign
   `DS:46B2 = (MMRESULT == 0)`.
2. On success, call `MMSYSTEM.605/timeBeginPeriod` with the decompiled
   local expression equivalent to `max(wPeriodMin, 10)`.
3. `param == 1`: if flag nonzero call `MMSYSTEM.606/timeEndPeriod`.
4. `FUN_1010_D6C6`: flag zero selects `USER.13/GetTickCount`;
   flag nonzero selects `MMSYSTEM.607/timeGetTime`.

Win16 1.8 uses flag `DS:46B2`, 1.0 uses `DS:45F2`.
The explicit flag write in the capability branch is NOT conditioned on the
return of `timeBeginPeriod` (which the decompiler does not check).

**Open:** the C export has one named direct reference
`FUN_1010_0F64 -> FUN_1010_D66C(1)` (cleanup) and no named direct call
`FUN_1010_D66C(0)`. This is negative evidence *only for recovered functions
in that decompilation*. Missing handler bodies in the same export prove that
decompiler call-site completeness cannot be presumed. Check original NE
near/far calls, relocation-backed targets, function pointers, and writable
callback aliases before claiming that the multimedia path is unreachable.

**Open:** the exact 16-bit argument pushed for `timeEndPeriod`. The C
decompilation elides it; do not silently assume it equals the requested
`timeBeginPeriod` resolution. Recover it from raw instructions at
`NE3:D6B0..D6C6` with the MMSystem Pascal ABI before exact emulation.

## Presentation contract: observed logic

- Win16 1.10 selector `3:2D9C`: mode 0 -> 320x200, mode 1 -> 640x400,
  mode 2 -> 960x600, mode 3 -> `DisplayDib` fullscreen, mode 4 ->
  return/reapply stored window dimensions. `DAT_1048_46B6 == 10`
  blocks entry into mode 3 locally.
- Win16 1.0 and 1.8 selector families lack the explicit 960x600 case:
  mode 2 -> fullscreen, mode 3 -> return/reapply dimensions.
  This is a *version-sensitive numeric ABI*.
- `3:3080` (1.10): client width == 320 AND height == 200 chooses
  `WING.1010/WinGBitBlt`; otherwise `WING.1009/WinGStretchBlt`.
  The `GetDC -> SelectPalette -> RealizePalette -> blit -> ReleaseDC`
  order is visible in all three compared decompilations.
- Fullscreen enters `DISPDIB.1/DisplayDib` with flag word `0x8200`,
  exits with `0x4040`; presentation uses VGA ports 0x3DA/0x3D4,
  palette DAC 0x3C8/0x3C9, quantizing RGB bytes with `>>2` only at
  DAC output.
- Prior **binary** MFC message-map analysis demonstrates size command IDs
  `0x8003 -> selector 0`, `0x8004 -> 1`, `0x8017 -> 2`.
  `0x8005` (DOS Mode menu) and `0x8016` (Alt+Enter accelerator)
  are distinct entry paths. The decompiled C omits short MFC functions
  around `3:0A6E..0AB0`, so searching C for direct `2D9C(0/1/2)`
  alone falsely suggests those modes are unused.

## New bounded, executable subset

`src/re/Win16ClockPresentationContract.hpp` and
`tests/win16_clock_presentation_contract_test.cpp` expose **only**:
the capability-success boolean; period clamp; clock-backend selection
from the stored flag; versioned mode-selector mapping; menu size command
mapping; WinG transfer selection by width/height; RGB8->VGA6 quantization;
and observed DisplayDib flag constants.

The tests use synthetic fixtures, compile-time assertions and a bounded
value sweep. These are **not** original binary-instruction tests and do
not prove render/timing parity.

## Required next static closures

1. All direct/indirect references to `NE3:D66C`, including startup loader,
   library/MFC initialization and NE relocation-backed aliases.
2. Raw bytes and Pascal stack-layout for `timeBeginPeriod` and
   `timeEndPeriod`, especially cleanup parameter and error return path.
3. Original command handler instructions and fixups for
   `3:0A6E/0A94/0AA2/0AB0`; check MFC dispatch reachability under
   menu enable/disable states, then optional runtime check.
4. Framebuffer snapshots **before** WinG presentation and **after** WinG/VGA
   palette conversion in an identical source-frame scenario.

For overall proof tracking, V058-10 (Win16 indirect FAR/fixup-backed
callgraph) stays OPEN. No claimed 100% behavior or pixel correctness.


## Further static pass: Alt+Enter key path (three-version delta)

Read the original Win16 decompilations from the archived Ghidra exports:
- 1.0 `NITE3W -10.EXE.c`, `FUN_1010_8ACA` (near `3:8ACA`);
- 1.8 `NITE3W-18.EXE.c`, `FUN_1010_8C2E` (near `3:8C2E`);
- 1.10 `nite3w110.exe(20260927-130639).c`, `FUN_1010_8CD2`
  (near `3:8CD2`).

All three implement a local key interpretation:
- Key-event `param2 & 0x8000` nonzero denotes a release; only the
  opposite branch handles `Enter` mode toggles.
- `VK_MENU` `0x12` sets/clears bit 0 of the ALT/modifier byte.
- A key-down `VK_RETURN` `0x0D` with that bit set selects the
  fullscreen action when currently windowed, and restores the window
  when fullscreen; the resulting mode-selector numbers are
  `2/3` (1.0/1.8) versus `3/4` (1.10).
- After the selector call the keyboard route considers render
  calibration. This should not be confused with a separate native
  MFC DOS Mode menu command or proof of keyboard event delivery.

**Important moved gate (instruction-path equivalent, bounded scope):**

| Release | keyboard caller | calibrator | eligible state tuple |
|---|---|---|---|
| 1.0 | guarded call `D5A2` | unguarded local body | screen=1, game=1, scheduler mode=0 |
| 1.8 | unconditional call `D722` | guarded body | screen=1, game=1, scheduler mode in {0,1,3} |
| 1.10 | unconditional call `D7D0` | guarded body | screen=1, game=1, scheduler mode in {0,1,3} |

For 1.0 the caller reads `DS:45F6 / DS:45F4 / DS:45F8`.
For 1.8 and 1.10 the callee reads `DS:46B6 / DS:46B4 /
DS:46B8`. The callee gate moves and broadens across releases.
**Scheduler mode 3 is not the same field as presentation selector 3.**
The 1.10 `FUN_1010_D7D0` eligible branch executes a preparatory
render followed by five `D7C0` render/HUD/presentation calls
before recomputing frame calibration values. This is not five AI steps.

The new `altEnterKeyTransition`, `invokesCalibrationAfterAltEnter`,
and `performsCalibrationAfterAltEnter` functions in the standalone
Win16 contract reproduce only this bounded decision logic. Synthetic
tests pin known key-down/release, ALT-state, mode-selector, and mode-gate
cases. Key-repeat dispatch, re-entrancy, display driver behavior and
actual clock ticks remain outside the test.

**Do not infer** the 1.10 multimedia timer is never initialized merely
because the Ghidra export only contains a named direct `D66C(1)`
reference: the nearby MFC menu dispatchers also have short handlers
missing from the recovered C function body catalog, while a separate
raw-binary message-map audit recovers those handlers. This is a concrete
reason to keep V058-10 (fixup/indirect callgraph completion) OPEN.

The `timeEndPeriod` argument remains unresolved. In the Ghidra C
exports it appears as `TIMEENDPERIOD()` without a trustworthy
argument list even though the Win16 ABI expects a WORD. No original
raw-byte stack walk was completed in this pass.
