# Nitemare 3D RE MAX v0.48 — DEMO bootstrap / first-input runtime closure

**Date:** 18 October 2026

## Evidence boundary

This pass consolidates five original-runtime DEMO.1 evidence bundles for the tested DOS runtime executable SHA-256 `32029326da3e9e356f5d17ca98e420dee178486f1384af8e7ccc662671c12511`.

The captures use DOSBox-X DEBUGBOX and natural menu input. They do not patch gameplay state or code. They close the DEMO bootstrap, seed reset, first record load/apply and first resulting movement for the captured path. They do **not** close the complete RNG consumer order, EOF behavior, all later DEMO records, DOS↔Win16 determinism, wall-clock timing or pixel parity.

## 1. Natural DEMO.1 open

Selecting Demo from the main menu naturally reaches playback mode 4 and loads:
- episode 1;
- map index 10 (E1M11 / the demo map);
- header words `15, 7, 30`;
- first 8-byte record `E0 48 02 00 08 00 00 00`.

The first record is therefore:
- key = `0x48E0`;
- input mask = `0x0002`;
- record counter = `8`.

The captured 8192-byte map buffer exactly matches the expected MAP.1 demo-map block for this build.

## 2. RNG seed reset location and arithmetic

During natural demo startup, after demo-map initialization, the original explicitly seeds the 32-bit DOS RNG state to `1`.

The verified local generator contract is:

```c
state = state * 214013 + 2531011;  // uint32 wrap
result = (state >> 16) & 0x7fff;
```

The seed reset occurs after map initialization and before the demo gameplay loop. Therefore any earlier loader RNG use is overwritten by this seed reset for later playback determinism.

The arithmetic is statically closed, but the complete dynamic sequence of RNG consumers after the reset remains open.

## 3. Scheduler mode 3 and mode 4 checkpoints

The alternate demo scheduler update was observed returning successfully in both states:

- mode 3 at render counter 1, update argument 1;
- mode 4 at render counter 3, update argument 2.

The parity test uses the current render counter before the later counter increment. In the captured paths the alternate update is taken on odd counters.

An implementation must not assume that all demo updates begin only after mode 4: a mode-3 update is observed before the demo header/record loading transition has completed.

## 4. First record application

The first loaded record is not immediately applied merely because it has been read.

The input path applies the record when the live render counter reaches the record counter. At counter 8:
- key `0x48E0` is taken from the current record;
- input mask `0x0002` is written to the demo-input field;
- only after that write does the routine proceed to load the next record.

The captured routine applies at most one record per invocation in this local path.

## 5. First movement caused by DEMO.1

A paired original-runtime capture around the movement call proves that the first applied input produces:

- angle = 90;
- step = 15;
- world position `(1056,3168) -> (1071,3168)`;
- delta `(+15,0)`;
- cell coordinates remain `(16,49)`.

This is a concrete first-input behavior witness, not a universal movement/collision proof.

## 6. Bounded implementation contract

The v0.48 C++ evidence model records only:
- the observed DEMO.1 header and first record;
- map index 10;
- modes 3 and 4;
- record application threshold `renderCounter >= recordCounter`;
- odd-counter alternate-update parity;
- the DOS RNG recurrence and seed=1 reset;
- the first movement witness.

Do not infer untested later records, EOF repetition, all-angle movement, collision/sliding or complete deterministic playback from this model.

## 7. Remaining DEMO P0

1. Capture the **first natural RNG consumer after seed=1**, including caller, subsystem, state-before, state-after and result.
2. Continue the ordered RNG ledger through the first gameplay-input boundary with no unexplained gaps.
3. Trace subsequent DEMO records and determine exact held/edge/toggle semantics for every input bit.
4. Close EOF / last-record behavior.
5. Compare normalized DOS builds and then Win16 using the same logical checkpoints.
6. Couple DEMO state to renderer/framebuffer zero-diff and projectile/AI side effects.

No original commercial executable or data file is distributed by this release.
