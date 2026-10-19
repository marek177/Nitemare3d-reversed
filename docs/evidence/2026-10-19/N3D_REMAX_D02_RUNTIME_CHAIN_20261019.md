# Nitemare 3D D02 — original runtime RNG chain, 19 October 2026

**Evidence class:** original DOS 2.0 runtime, scoped / shared RNG wrapper only. **Not** 1:1 clean-room parity.

Examined two independent existing N3DTRC01 DOSBox-X sessions. Capture 1 records eight RNG entries; capture 2 records 18 (the selective tracer continued two entries beyond its target of 16 because the dense recording window did not stop instantaneously). Both have a byte-for-byte-equivalent normalized eight-entry prefix of callsite + LCG state + RNG result.

The verification script independently checks call-before-wrapper-before-state-write ordering, exact 32-bit LCG recurrence from seed 1, return-mask consistency, original build's recorded shared-wrapper count and every direct caller against the known 22-site register. No reordering or realignment is applied.

## First 18 recorded RNG entries (longer run)

| # | Original DOS2 image callsite | RNG result | State after | Known immediate role |
|--:|:--|--:|:--|:--|
| 1 | `0x56A6` | 41 | `0x0029E2C0` | GUARD planner |
| 2 | `0x85AD` | 18467 | `0xC823F683` | damage / projection scalar |
| 3 | `0xA047` | 6334 | `0x18BE873A` | resource table retry loop |
| 4 | `0xA047` | 26500 | `0xE7847115` | resource table retry loop |
| 5 | `0xA047` | 19169 | `0xCAE1DF84` | resource table retry loop |
| 6 | `0xA047` | 15724 | `0x3D6C1037` | resource table retry loop |
| 7 | `0xA047` | 11478 | `0x2CD60A1E` | resource table retry loop |
| 8 | `0xA047` | 29358 | `0x72AE7869` | resource table retry loop |
| 9 | `0x5582` | 26962 | `0x69521988` | GUARD wake timer |
| 10 | `0x5582` | 24464 | `0xDF90722B` | GUARD wake timer |
| 11 | `0x56A6` | 5705 | `0x1649B442` | GUARD planner |
| 12 | `0x573F` | 28145 | `0x6DF109FD` | GUARD planner branch |
| 13 | `0x56A6` | 23281 | `0xDAF1B4CC` | GUARD planner |
| 14 | `0x56A6` | 16827 | `0xC1BBB05F` | GUARD planner |
| 15 | `0x85AD` | 9961 | `0xA6E9C9A6` | damage / projection scalar |
| 16 | `0x9FE3` | 491 | `0x81EB59D1` | resource table retry loop |
| 17 | `0x9FE3` | 2995 | `0x0BB31550` | resource table retry loop |
| 18 | `0x9FE3` | 11942 | `0xAEA69ED3` | resource table retry loop |

## Conclusions and strict scope

- **D02-A closed:** first 8 shared-wrapper calls reproducible across two independent original runs, including exact RNG values and states.
- **D02-B scoped witness:** first 18 shared-wrapper calls in one original run, all internally consistent with seed-1 LCG and recognized callsites; this longer prefix is not independently replicated beyond call 8.
- Consecutive `A047` calls #3–#8 and `9FE3` calls #16–#18 show the importance of conditional retry loops in actual execution. Six repeats do **not** imply six distinct visible objects.
- `5582` occurs twice in a row; this is not a random-draw count for a single GUARD until the record identities are correlated.
- Selective capture saves focused windows and checkpoints, not all instructions between events. The 18 shared-wrapper entries are counted at every CPU callback; other possible direct CRT `rand` paths remain an independent census obligation.
- The semantic meaning of `85AD` and `573F` remains only as specifically characterized by prior static evidence. No class-by-class or all-map reachability assertion is made.
- No clean-room engine comparison, Win16 comparison, framebuffer/audio matching or EOF closure is claimed.

## Next proof obligation D02-C

Run a second original capture that reaches at least entry 18, normalize the complete callsite/state/result sequence and require strict equality. Extend the capture to first applied DEMO record / gameplay input and compute scheduler invocation depth at each RNG entry. Compare with the clean-room port only after original trace is sealed. The existing `n3d_d02_verify_chain.py` accepts multiple session paths and fails on any mismatch in their shared prefix.
