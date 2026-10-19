# Nitemare 3D RE MAX v0.50 — GUARD41 death outcome and RNG #16–#18

**Date:** 19 October 2026

## Evidence boundary

This release records a new bounded original-runtime trace from the unchanged DOS v1.2 executable during natural DEMO.1 playback. No debugger memory patch was used to force game state, RNG, HP or the death branch.

The capture begins at the lethal HP write for GUARD index 41 and ends at the map-byte commit at the end of the measured death handler. It is not a proof of later animation completion, pool release, item-drop behavior, audio parity or other classes.

## Closed runtime path

The bounded trace contains 3,642 original CPU instructions, 8,198 memory reads, 867 memory writes and 12,707 total events. It ends by USER_STOP rather than the recorder size limit.

Observed writes for GUARD41:
- HP: `111 -> 0`;
- byte +0x00: `0x10 -> 0x29`;
- timer +0x06: `2 -> 3`;
- state +0x0B: `0x06 -> 0x00`;
- next-state +0x0C: `0x05 -> 0x09`;
- score: `0 -> 100`;
- linked map marker: `0xA5 -> 0x00`.

## RNG rejection loop is now executed through acceptance

Three consecutive RNG draws are present in the same bounded trace:

| RNG | before | after | result | mod 7 | result |
|---:|---|---|---:|---:|---|
| 16 | A6E9C9A6 | 81EB59D1 | 491 | 1 | rejected |
| 17 | 81EB59D1 | 0BB31550 | 2995 | 6 | rejected |
| 18 | 0BB31550 | AEA69ED3 | 11942 | 0 | accepted |

This supersedes the v0.49 frontier where RNG #17 had only an observed entry/pre-state and a predicted post-state. RNG #17 and #18 are now actually executed in the original trace.

## What remains open

- visual completion of the death animation;
- eventual GUARD/OBJECT slot cleanup;
- item-drop conditions and payload;
- scoring for other classes/difficulties;
- DOS v2.0 and Win16 equivalents;
- later DEMO RNG draws and complete end-to-end replay;
- audio, timing and pixel zero-diff.

No proprietary game binary, commercial asset, RAM dump or raw original trace is added to the repository.
