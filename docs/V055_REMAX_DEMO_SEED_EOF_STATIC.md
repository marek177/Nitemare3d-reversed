# Nitemare 3D RE MAX v0.55 — DEMO seed gate and EOF-path narrowing

**Date:** 19 October 2026

## Scope

This pass records a SHA-gated original-static audit of the DOS DEMO seed/reset and record-reader path. It complements, but does not replace, the separate original-runtime RNG captures.

## Seed helper vs random draw

The audited code distinguishes two operations:
- the seed helper path, including a callsite at image offset `F9AC`;
- the actual random-number draw helper.

The seed helper is not itself an RNG draw. The checked path passes constant seed 1 into the seed routine and returns to a post-seed boundary at `F9B1`.

This distinction prevents falsely counting the seed reset as the first random consumption.

## DEMO reader local ordering

The audited local DEMO path includes:
- mode dispatcher at `6D04`;
- first 8-byte record read near `6DC9`;
- mode=4 transition;
- render-counter comparison and input write in `6DE4..6DF9`;
- read of the next record after applying the current one.

At the local return site near `6E07`, the caller does not immediately TEST/CMP the read-count return value. This narrows the EOF question but does not close it because CRT read semantics, errors and the surrounding state machine still matter.

## DEMO.1 payload endpoints

The checked DOS DEMO.1 contains:
- 275 records after the 6-byte header;
- first record: key `0x48E0`, input `0x0002`, counter `8`;
- last record: key `0x74E0`, input `0x0090`, counter `1074`;
- four adjacent equal-counter pairs;
- nondecreasing record counters.

The last raw counter is not automatically the exact playback EOF frame.

## Capture-quality correction

Three older large experimental N3DT sessions totaling more than 3.6 GB did not contain the required seed-helper/post-seed/first-draw interval.

That absence is **not** evidence that the game omitted the seed or RNG call. It only proves those particular captures did not document the required interval and should not be merged into one chronology.

## Still open

- one continuous original trace from seed reset through the first post-seed RNG consumption;
- CRT read behavior at EOF/short read/error;
- exact last-record / demo-end transition;
- later input-record semantics and held/edge/toggle behavior;
- DOS/Win16 deterministic replay equality.

No original executable, DEMO file or raw capture is added by this release.
