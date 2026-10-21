# Nitemare 3D DOS v2.0 — E1M1 LIVE runtime: simultaneous opposing inputs (v0.84)

**2026-10-21. Evidence: NEW ORIGINAL GAMEPLAY RUNTIME, not a synthetic model and not original-vs-remake parity.**

The original unpacked DOS v2.0 `N3D-E-20.EXE` (SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`) was running in the modified Linux DOSBox-X N3D Advanced History. The real active E1M1 guest state was inspected read-only through `/proc/PID/mem` (DS `2F95`); the original FEFA and 1021E machine-code windows matched the binary. X11 XTest delivered actual key-down/key-up events; no guest memory modification, save patching, or original-game binary modification occurred.

**New experiment:** 13 consecutive test phases, **16 accepted keyboard events**, **1,600 original guest-memory samples**, 27 unique direction/Q10 pairs. The original `DS:4540` render counter increased by **314** over the experiment. Host polling median 12.539 ms; **maximum gap 1,077.703 ms**, therefore intermediate ticks can be missed and host milliseconds do not establish game tick cadence. This was one original E1M1 position sequence rather than reset-identical A/B runs.

## Measured opposing key behavior

| Experiment | X/Y original | Raw heading | Observed behavior |
|---|---|---|---|
| Baseline, no keys | (1371,3604) → (1371,3604) | 228 → 228 | stable while renderer advances |
| Up then Down, both held | (1371,3604) → (1382,3606) | 228 → 228 | near-cancellation, transitional 11-step and ±1 Y movements |
| Keep Down only | (1382,3606) → (1505,3437) | 228 → 228 | movement resumes |
| Down then Up, both held | (1505,3437) → (1505,3438) | 228 → 228 | near-cancellation, net +1 Y |
| Keep Up only | (1505,3438) → (1371,3587) | 228 → 228 | movement resumes |
| Left then Right, both held | (1371,3587) → (1371,3587) | 228 → 222 → 228 | net zero; one -6 and one +6 step |
| Keep Right only | (1371,3587) → (1371,3587) | 228 → 18 | **25 × +6** modulo 360 |
| Right then Left, both held | (1371,3587) → (1371,3587) | 18 → 18 | no rotation |
| Keep Left only | (1371,3587) → (1371,3587) | 18 → 312 | **11 × -6** modulo 360 |
| Final no input | (1371,3587) → (1371,3587) | 312 → 312 | stable while renderer advances |

Four additional idle phases separating the key groups were also recorded: position and heading remained stable while render counters continued increasing.

**Important:** Opposing rotation practically cancels; opposing forward/backward does **not** create a perfectly bitwise-stationary player. Original micro-movement and transition effects were observed. Do not implement a blanket `if(up && down) return;` in the remake until the DOS player movement/collision scheduler is proved.

## Original DS:3F50 bit-mask runtime evidence

The original current key-mask WORD `DS:3F50` exhibited:

| Input | DS:3F50 |
|---|---|
| no input | `0x0000` |
| Up | `0x0002` |
| Down | `0x0004` |
| Up+Down | `0x0006` |
| Left | `0x0008` |
| Right | `0x0010` |
| Left+Right | `0x0018` |

**1,580/1,600 host key-status samples matched the guest input WORD immediately.** The remaining 20 were at the beginning of changed-input phases, before the game processed the new XTest transition. This is not a measurement of zero-latency polling or an exact 8086 dispatcher trace. All 27 observed heading values had consistent Q10 sine/cosine pairs.

## Reproducible private evidence / independent audit

The user-facing v0.84 ZIP contains: the **1,600-row original CPU state observation CSV**, original-execution JSON (including 16 XTest key events and CSV SHA-256), the actually executed Python3 live harness, independent `verify_runtime_v084.py`, its `runtime_e1m1_opposing_keys_v084_verified.json` output and **10/10 mutation tests**. The independent verifier does **not** rerun DOSBox-X. Do not distribute original commercial EXE/IMG/MAP or guest-memory dumps.

The harness deliberately retains the original experiment's one-time PID, memory-base and X11-window IDs. **Re-detect all these addresses before reusing it**. It is not a drop-in general DOSBox-X test runner.

**Current blocker:** no deterministic original 8086 input-dispatcher/per-game-tick call ledger for opposite keys and no C++ remake behavior comparison. An accurate follow-up should instrument original input latching, player update and collision at instruction-level breakpoints, under matching start states and both key press orders.

**Status:** `NEW ORIGINAL RUNTIME TEST PASSED`, `DS:3F50 BITS MEASURED`, `REMAKE 1:1 NOT TESTED`.
