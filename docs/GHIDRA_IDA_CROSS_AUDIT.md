# Ghidra + IDA cross-audit — 2026-09-18

This document records newly recovered facts from the supplied Win16 `NITE3W.EXE`, Ghidra project/listing and IDA database. It deliberately separates **direct evidence** from **working hypotheses**.

## Analysis inventory

The Ghidra listing currently exposes approximately:

- 1,067 unique `FUN_*` candidates
- 4,984 `LAB_*` labels
- 829 `DAT_*` symbols
- ~4,666 CALL/CALLF occurrences
- ~10,958 XREF blocks
- ~308 unique external API symbols

These are analysis-object counts, not counts of original game source functions. MFC, compiler runtime, import thunks and heuristic function boundaries must still be classified.

## Win16 NE layout

- 10 logical NE segments.
- Entry point: logical segment 2, offset `3718h`.
- Auto-data segment: logical segment 10.
- Initial SS: logical segment 10, SP `0000h`.
- Heap allocation: `4262h`.
- Stack allocation: `2EE0h`.
- Target: Windows 3.10 / Win16 protected-mode API.
- Ghidra assigns synthetic selectors `1000h, 1008h, 1010h, ... 1048h`; logical segment 10 therefore appears as `1048h`.

### IDA mapping rule

Do not use Ghidra selectors as literal flat IDA segment bases: 64 KiB Win16 segments would overlap.

For the reconstruction layout based at `0x100000`:

```
logical_index = ((ghidra_selector - 0x1000) / 8) + 1
ida_ea = 0x100000 + (logical_index - 1) * 0x10000 + offset
```

Example: Ghidra `1008:3718` -> logical segment 2 -> IDA `0x113718`.

## Presentation / renderer boundary

Direct GDI anchors include:

- `1000:9504` area -> `GDI::BITBLT`
- `1000:97E4` area -> `GDI::STRETCHDIBITS`
- DIB creation path -> `GDI::CREATEDIBITMAP`
- palette APIs are present in the executable

This strengthens the model:

```
world/raycaster -> indexed software framebuffer -> DIB/palette -> BitBlt/StretchDIBits -> Windows DC
```

The GDI calls are presentation evidence; they must not be mislabeled as the actual wall raycaster.

## Input

Direct imports/references establish separate keyboard and joystick paths.

Keyboard family includes `GetAsyncKeyState`, `GetKeyboardState` and `GetKeyState`.

Joystick family includes WinMM `joyGetDevCaps` and `joyGetPos`.

The exact game-action binding and joystick scaling/dead-zone logic remain to be traced before constants are committed to runtime code.

## Audio

The executable exposes a substantial WinMM output path:

- `waveOutOpen`
- `waveOutWrite`
- `waveOutPrepareHeader`
- `waveOutUnprepareHeader`
- `waveOutReset`
- `waveOutClose`
- wave output device/volume queries
- MIDI output device/volume APIs
- `sndPlaySound`

This supports separate SFX/cache and MIDI/music subsystems. Exact SND.DAT slot policy still needs function-level tracing.

## Runtime resource/cache diagnostics

Recovered strings include object-slot and sound-slot statistics with reload/thrash counters. This is direct evidence for an original runtime cache/slot layer rather than simple one-shot asset loading.

Implementation consequence: reconstructed loaders should preserve the distinction between archive parsing and runtime cache policy. Cache limits/replacement rules must not be invented until the owning functions are traced.

## Doors, panels and pushables

Recovered diagnostics include:

- `Door not in map`
- `Push not in map`
- `MAXDOORS exceeded (%d)`
- `MAXPANELS exceeded (%d)`

Together with the already traced door/panel/push functions, this strengthens the conclusion that these are explicit runtime tables/entities with hard limits, not merely passive map tile values.

## High-value function anchors

| Ghidra address | Current interpretation | Confidence |
|---|---|---|
| `1000:036A` | far C++/MFC helper candidate; 10 callers | medium |
| `1000:9504` | GDI BitBlt presentation path | high |
| `1000:97E4` | StretchDIBits presentation path | high |
| `1010:8CD2` | high-fanout switch dispatcher candidate; 18 callers | medium |
| segment `1048` | primary auto-data/global-state area | high |

Large switch dispatchers are priority targets for recovering object/state/command semantics, but no gameplay name is assigned until caller/data evidence identifies the domain.

## Working coverage after cross-audit

| Area | Working coverage |
|---|---:|
| NE / Win16 executable structure | ~96% |
| MFC / Windows framework boundary | ~82% |
| 2-D/video presentation | ~74% |
| keyboard/input path | ~73% |
| discovered function boundaries | ~72% |
| SFX/audio output | ~69% |
| XREF/call graph | ~68% |
| joystick path | ~67% |
| MIDI/music output | ~63% |
| map/game-object semantics | ~52% |
| global-data semantics | ~51% |
| doors/panels/pushables | ~49% |
| save/load semantics | ~46% |
| raycaster internals | ~48–52% |
| player/weapons overall | ~38% |
| enemy/guard AI overall | ~55–60% for state evidence, lower for exact movement |
| source-level C/C++ reconstruction | ~27% |

Overall direct executable RE is tracked in `RECONSTRUCTION_STATUS.md` at approximately **66–68%**. These are engineering estimates, not byte-count completion.

## Rules for source reconstruction

1. Keep confirmed executable facts separate from hypotheses.
2. Preserve original data formats and constants only when supported by executable/data evidence.
3. Do not copy Ghidra synthetic selectors directly into the flat modern runtime.
4. Do not implement guessed joystick scaling, cache replacement, AI transitions or raycaster branches as if confirmed.
5. Use reconstructed descriptive names while retaining original `segment:offset` anchors in comments/docs.
6. New runtime modules should cite the corresponding RE document/anchor in source comments when behavior is executable-derived.

## Next high-value targets

1. classify all ~1,067 function candidates into game / MFC / CRT / thunk / uncertain;
2. build caller/callee clusters around renderer, input, audio, map/object, combat and AI;
3. name high-fanout `DAT_1048_*` globals from read/write XREFs;
4. trace joystick normalization/action binding;
5. trace object/sound cache allocation and replacement policy;
6. identify the software framebuffer producer immediately upstream of the GDI presentation functions;
7. finish guard movement/AI transitions, enemy->player damage and weapon cadence;
8. finish raycaster traversal, clipping, texture-column, sprite and depth branches.
