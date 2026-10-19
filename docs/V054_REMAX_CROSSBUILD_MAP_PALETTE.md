# Nitemare 3D RE MAX v0.54 — DOS/Win map-marker and palette cross-build delta

**Date:** 19 October 2026

## Scope

This pass records a reproducible cross-build data/code audit plus a controlled DOS v2.0 A/B visual test.

It is not a complete DOS-vs-Win gameplay or pixel-parity result.

## 31-level high-byte marker census

Across all 31 levels, four selected MAP high-byte codes `0x25,0x26,0x27,0x28` appear once each in the player-start region in the audited DOS data while the corresponding Win16 v1.10 map form clears those high bytes.

That yields:
- 31 levels;
- four selected markers per level;
- 124 changed high-byte positions total;
- all 124 within Chebyshev distance <= 4 from the player start;
- 29/31 levels with maximum selected-marker distance <= 2;
- 112/124 positions sharing the same low-byte base cell as the player-start base cell.

The Win16 engine still contains other uses of those numeric IDs; this is not evidence that IDs 0x25..0x28 disappeared globally.

## Controlled E1M1 A/B runtime

The same DOS v2.0 executable/data set was run repeatedly while only the four E1M1 high bytes were selectively cleared in laboratory copies.

Repeated baseline vs baseline produced zero screenshot difference at the compared checkpoints.

Clearing individual markers produced visible scene differences:
- ID 0x25 at map offset 0x1E2D: 5,576 differing pixels;
- ID 0x26 at 0x1DAD: 5,548;
- ID 0x27 at 0x1D2D: 8,000;
- ID 0x28 at 0x1C2D: 6,592.

Therefore these four high-byte markers have a causal visible effect in the DOS E1M1 scene. The exact resource mapping and semantic class path are handled separately; v0.53 closes the Win16 class36 pickup path but does not prove the DOS path identical.

## DOS 1.9 -> 2.0 main loaded-code band

The examined loaded code band grows from 46,832 to 46,880 bytes (+48). Sequential alignment gives 44,108 equal bytes.

This ratio is a structural diff signal, not a behavior-completion percentage. Concrete changed branches need version-specific analysis.

## Win16 v1.8 -> v1.10 palette rule

The checked v1.10 palette manager can reserve 10 entries at the beginning and 10 at the end for the system palette.

- reserve disabled: copy 256 RGB entries;
- reserve enabled: copy the 236 middle entries.

This version/platform difference matters directly for WinG/DIB pixel comparisons.

## Open

- exact DOS resource/class path for the selected map markers;
- whether Win16 removed markers are compensated by another inventory/loadout path;
- full normalization of all DOS1.9/2.0 and Win1.8/1.10 changed functions;
- canonical DOS-vs-Win framebuffer and palette zero-diff.

No proprietary game data or executable is added by this release.
