# v0.22 RE MAX — version profiles and evidence registry

v0.22 adds a machine-readable boundary between executable identity, reverse-engineering evidence and implementation claims.

## Version profiles

The registry has slots for:

- DOS v1.0
- DOS v1.2
- DOS v1.9
- DOS v2.0
- analyzed Win16 build

Historical v0.22 recorded only the DOS v2.0 unpacked image. As of **v0.32 / 2026-10-14**, direct original-file checks established additional version-specific fingerprints:

| Build | Measured bytes | Hash domain | Confidence |
| --- | ---: | --- | --- |
| DOS 1.0 | 154,448 | unpacked MZ load image | CONFIRMED |
| DOS 1.2 | 115,856 | **packed raw MZ file only** | CONFIRMED only for packed file; unpacked image remains OPEN |
| DOS 1.9 | 171,296 | unpacked MZ load image | CONFIRMED |
| DOS 2.0 | 171,360 | unpacked MZ load image | CONFIRMED |
| Win16 1.10 | 230,400 | **entire raw NE executable** | CONFIRMED |

The build profile registry now includes DOS 1.0 and 1.9 load-image hashes and the identified Win16 1.10 raw-file hash. The old `Win16Unknown` enum member remains for ABI/source compatibility but is bound to the identified v1.10. DOS 1.2 unpacked image profile remains blank/open: its confirmed packed distribution fingerprint lives in `tools/n3d_v032_static_verify.py`. **Do not compare packed raw files with unpacked load-image hashes.** Full instructions and SHA-256 are in [the v0.32 report](V032_REMAX_ORIGINAL_BINARY_CLOSURES.md).

## Evidence registry

Each fact now carries:

- fact ID;
- build ID;
- confidence: CONFIRMED / STRONG / OPEN;
- evidence source;
- short evidence reference;
- closure experiment.

Examples:

- player X/Y: CONFIRMED, DOS v2.0, static disassembly;
- GUARD pool/stride: STRONG, requires runtime iteration proof;
- exact FAST/MAIN interleaving: OPEN;
- `0800:0E50` OBJECT-runtime identity: OPEN;
- projectile `+18/+19` stale-cache behavior: STRONG;
- build-specific address portability rule: CONFIRMED.

## Promotion rule

The helper `mayPromoteToImplementation()` returns true only for CONFIRMED facts.

This is intended to prevent future code from silently turning a hypothesis into a reconstructed gameplay rule.

## Why this matters

Several older addresses were correct only for another build/context. A version profile plus evidence record makes the required sequence explicit:

1. fingerprint executable;
2. select build profile;
3. use only facts scoped to that build;
4. keep STRONG/OPEN items behind runtime verification;
5. promote only after the closure experiment succeeds.

The next version-identity target is the unpacked DOS v1.2 image and any as-yet-unidentified builds. For the identified profiles, attach build-specific symbol maps and original-runtime traces.

## v0.35 direct RNG census correction (2026-10-15)

The `Dos20RngDirectCallsites` fact is now backed by **22** original-byte direct FAR calls to `0FBA:01A0`, rather than the earlier 20-entry static register. Two missing incoming-damage paths at load-image `8860` and `886C` were verified as actual jump-table targets for actor classes `08` and `09/0A`. The scope is one SHA-256-identified unpacked DOS v2.0 image; runtime order and indirect RNG calls remain open. See [v0.35 report](V035_REMAX_RNG_22_CALLSITE_CENSUS.md).

## v0.36 additional DOS v1.7 build profile and damage order

A new direct original image check confirms the DOS **v1.7** unpacked MZ load-image profile (170848 bytes, SHA-256 `df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff`). The appended enum value `BuildId::DosV17` preserves numeric values of existing build IDs. The profile registry now has six records; DOS v1.2 still lacks an unpacked-image SHA, and the DOS v1.7 profile is not a DOS v1.2 alias. The v0.36 evidence registry also distinguishes v2.0 incoming damage producer-before-protection, v1.9 protection-before-producer (also checked in v1.0 and v1.7) and the v2.0 short hit-indicator countdown. See [v0.36](V036_REMAX_PROTECTED_HIT_RNG_ORDER.md). These are narrow static control-flow facts, not runtime parity.

## v0.37 scheduler evidence additions (2026-10-15)

Four **build-scoped local** static records for fingerprinted DOS v2.0 were added: one-count-per-quantized-change in `BEB4` and `BEF4`, a DEMO odd-frame FAST call that passes the slowCounter argument, and unsigned 500-unit legacy clock recovery in `C286..C2B4`. The registry's separate `Dos20ExactFastMainOrder` entry remains **OPEN** because neither full transitive callbacks nor interrupt chronology were traced. Evidence report: [v0.37](V037_REMAX_SCHEDULER_CATCHUP_STATIC_CLOSURE.md).
