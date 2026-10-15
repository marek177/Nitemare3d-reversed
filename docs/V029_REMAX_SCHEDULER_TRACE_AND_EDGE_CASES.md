# v0.29 RE MAX — FAST direct-call evidence, trace checks and October edge cases

Date: 2026-10-14. Additive update after v0.28; no original binaries or copyrighted
assets are committed. This pass **does not claim new original-game runtime captures**.
It codifies observations reported in the October 12–14 static-analysis notes and
provides independent, synthetic-fixture-tested checks for later captures.

## Evidence policy and scope

- **Reported static:** previous disassembly/static audit reports a direct edge or
  branch behavior. The binary was **not re-disassembled in this change**; the
  finding must be re-checked against a fingerprinted original to promote it.
- **Strong inference:** branch/control-flow interpretation with possible
  callbacks, build differences or unresolved preconditions.
- **Runtime open:** no accepted chronological trace of the original was supplied.
- **Runtime confirmed:** reserved; **zero** newly confirmed runtime entries here.

Do not copy DOS v2.0 `1000:offset` addresses to DOS v1.2 or Win16 NE segments.
Do not equate a known direct call sequence with complete simulation timing.
See [v0.20](V020_REMAX_VERIFICATION_HARNESS.md),
[v0.21](V021_REMAX_SUBSYSTEM_EVIDENCE.md) and
[v0.28](V028_EXTERNAL_EVIDENCE_BSF_DEMO.md) for earlier scope boundaries.

## 1. DOS v2.0 FAST static direct-call sequence (reported)

`1000:C150` — normalized targets, in direct-call order:

```text
C51A -> 0A40 -> 5F26 -> A19A -> A4A2 -> 0E50
     -> A4AC -> A0CC -> 89A2 -> 9026
     -> 89A2   only on the reported (tick & 7) == 0 branch
```

Identified consumers: `0A40` door auto-close, `5F26` GUARD pass (existing
v0.21 confidence is STRONG), `0E50` **PUSH updater** (identity statically
resolved in v0.33), `89A2` action dispatcher and `9026` weapon/cadence.
The original v0.29 label "moving-OBJECT candidate" was superseded by the
new [v0.33 original-byte proof](V033_REMAX_PUSH_SCHEDULER_BINARY_CLOSURE.md).
This direct call does NOT identify the complete generic OBJECT scheduler.

**Critical distinction:** this is the order of calls *issued directly* by a
single FAST invocation. A target may itself call other subsystems, or re-enter
another scheduler. Therefore the sequence cannot be used as a flat total order
of RNG, collision, simulation, rendering and input events. The late gated
`89A2` branch requires recording the counter **at that branch**, not assuming
it equals the counter at entry.

## 2. DEMO / RNG scheduler routing (strong, not runtime closed)

Previous static audit reports DOS v2.0 scheduler sites `1000:C1A8` and
`1000:6D04`, with:

| Address | Recorded interpretation |
|---|---|
| `DS:3CD6` | DEMO mode/state, values `0..5` |
| `DS:4540` | frame counter; increment site `1000:BF36` |
| `DS:34C2` | DEMO next-record / event time |
| `1000:C150` | FAST routine |
| `1000:C1A8` | outer scheduler |
| `1000:9806` | first input-path target for pre-input trace |

The reported control flow routes normal FAST work through a slow bucket and
may route DEMO FAST through an odd-frame branch (`DS:4540 & 1`). The **exact**
number of FAST invocations per elapsed time unit, catch-up behavior, and all
nested paths are still open. Do not impose a universal odd/even gate on all
DEMO modes or all versions.

Existing LCG validation is in
[`N3DV020VerificationHarness.hpp`](../src/re/N3DV020VerificationHarness.hpp).
A seed-1 mathematical sequence is **not** evidence that the original DEMO
made the same *number and order* of draws. The pending capture needs caller,
RNG before/after, result, consumer, scheduler invocation/depth and build hash.

## 3. Interaction and version-specific edge cases

| Observation from prior static work | Scope / status | Runtime closure requirement |
|---|---|---|
| PUSH accepted activation advances for eight *successful* movement steps (8 world units each in earlier build-scoped evidence); an obstructed step preserves position/remaining steps | DOS v2.0; reported static | Break `0DF8`, `0E50`, `0EF5`, `0F50`; record blocked and unblocked consecutive ticks |
| Auto-close blocked by player/object re-arms retry counter to **4** | DOS v2.0 `0A40`; reported static | Log state/timer each attempted close and event ordering |
| A state-4 paired-door path may synchronize the counterpart in v1.2, while v2.0 has an early-return path | DOS v1.2 versus v2.0; strong cross-build lead | Fingerprint both builds and compare wall-pair state transitions |
| E2M10 twentieth special-hit branch may invoke nested scheduler before outer collision completes | Build pairing not yet independently reproduced; strong lead | Trace call depth, triggering hit count, nested tick, RNG and outer collision continuation |
| Initial graphics-buffer segment alias after LOAD is mapped, but first post-LOAD tick timing remains unresolved | Win16; open | Capture last LOAD writes and first gameplay clock/render/OBJECT/GUARD updates |

In particular, **do not flatten** a nested E2M10 branch into a single
subsystem pass. It is recorded as an investigation target, not a newly
reproduced gameplay event.

## 4. New code and diagnostics

- [`src/re/N3DV029SchedulerEvidence.hpp`](../src/re/N3DV029SchedulerEvidence.hpp):
  build-scoped direct-call registry, gated last call, unpromoted finding ledger,
  `checkFastDirectCalls()` that compares only *immediate* children of the
  specified FAST invocation ID. It does not synthesize game ticks.
- [`tools/n3d_trace_audit.py`](../tools/n3d_trace_audit.py):
  read-only CSV diagnostics for normalized FAST child calls and ordered DOS
  v2.0 LCG draws. Prints first divergence and returns exit status 1 on a
  mismatch; exit 2 on malformed input.
- [`tests/v029_scheduler_evidence_test.cpp`](../tests/v029_scheduler_evidence_test.cpp)
  and [`tests/test_n3d_trace_audit.py`](../tests/test_n3d_trace_audit.py):
  **synthetic tests**, including nested/interleaved invocation filtering,
  conditional last call, missing/extra/reordered calls, seed mismatch,
  RNG discontinuity and unknown caller.

### FAST trace CSV

```csv
invocation,caller,target
7,0xC150,0xC51A
7,0xC51A,0x1234
7,0xC150,0x0A40
```

The example is intentionally **incomplete**. Log an *immediate caller* and a
unique invocation ID per FAST entry, including recursive entries. Do **not**
assign one ID to every FAST call occurring within a rendered frame. Separate
nested calls by invocation ID, not by timestamps alone.

```sh
python tools/n3d_trace_audit.py fast /path/to/fast.csv --invocation 7 --tick-at-gate 0x8
```

`--tick-at-gate` is the observed value at the `(tick&7)` condition. A capture
without this counter cannot close the gated branch.

### RNG trace CSV

```csv
caller,before,after,result
0x2478,1,2745024,41
```

This too is merely a mathematically valid **synthetic example**. For a full
DEMO proof, collect *every* RNG draw, in exact order, beginning with state 1.
`--strict-callers` is appropriate only if all observed caller offsets should
belong to the re-audited 22-entry DOS v2.0 direct-call census (v0.35); indirect call paths
must be investigated rather than discarded.

```sh
python tools/n3d_trace_audit.py rng /path/to/rng.csv --seed 1
python tools/n3d_trace_audit.py rng /path/to/rng.csv --seed 1 --strict-callers
```

Both modes accept decimal and `0x`-prefixed hexadecimal numbers and emit JSON.
A passing test means **the supplied trace is internally consistent with the
specified model**, not that the original game was executed or 1:1 parity was
reached. Fingerprint the original DOS/Win16 binary and attach raw debugger
capture before promoting any status.

## 5. Explicitly open after v0.29

Complete FAST/MAIN and input/render chronology; nested catch-up; true DEMO
seed-1 draw ordering and original DOS record byte semantics; PROJECTILE FB–FE
collision/multi-hit/pool-full behavior; Multi Plasma fire-state transitions;
first tick after LOAD; secret/remote-door per-tick motion; E2M10 nested branch
runtime reachability; rendering rounding/clipping and rare-version dead code.
No parity percentage is increased by this static registry or synthetic tests.

## v0.33 post-audit note

New fingerprint-gated binary audit upgrades the exact `0E50` identity and the `(destinationObjectProperties & 0x06) != 0` blocked-step skip from a reported hypothesis to **VerifiedStatic**. The six-byte PUSH pool loop is 292 masked-instruction-equivalent bytes to Win16 `3:2210`. The accepted path commits the OBJECT/MAP reference, calls an X/Y sorted-list updater and *then* decrements the remaining push count. Complete transitive timing, nested calls and generic OBJECT scheduling remain OPEN; no new original-game CPU runtime capture was produced.

## v0.34 original-binary correction (2026-10-15)

The first DOS v2.0 FAST target `C51A` is a **RETF-only empty hook**, verified from the canonical unpacked MZ load image; it is not a hidden OBJECT updater. Frame animation/visual updates are split across `C1A8 → BF36 → 2500 → 241E` (span path) and `BF36 → 21F0 → B2D4 → B22C/B17E` (projected objects). `B2D4` also has a projectile caller from `8230`. The **DEMO FAST check on the existing `DS:4540` low bit at `C221` precedes the `BF36` increment of that render-generation counter.** Details and precise conditional gates are in [v0.34](V034_REMAX_OBJECT_ANIMATION_RENDER_BRANCHES.md). Full generic OBJECT writer census and end-to-end runtime order remain OPEN.

## v0.35 RNG census correction

An original-byte scan demonstrates **22**, not 20, inline direct far RNG callsites in DOS v2.0. Two legitimate incoming damage sites `8860` and `886C` were omitted by the old list, causing false strict-trace rejections. The class dispatcher table proves their targets, and the updated Python/C++ registries accept them. See [v0.35](V035_REMAX_RNG_22_CALLSITE_CENSUS.md). This changes static caller validation only, not proof of DEMO seed=1 chronology.

## v0.37 — original DOS v2.0 quantized counters and local catch-up closure

The earlier v0.29 note that *all* catch-up behavior remained open is now narrowed by direct original-byte proof. Slow quantizer `BEB4` computes `low32(clock*8)/1000`, caches `DS:16FA` and increments `DS:16F6` **once** when the key differs. Frame quantizer `BEF4` uses signed `DS:3CC2` calibration, low32 product and /1000, caches `DS:1702` and increments `DS:16FE` **once**. At outer `C1A8`, `DS:1738/173C` due thresholds are unsigned compared against those counters and, after a due branch, each set to **observed counter+1**, not incremented until all elapsed intervals are replayed. The normal FAST `C1EA` is allowed only with DEMO mode=0; frame DEMO FAST `C22E` only with mode!=0 and old `DS:4540` odd. Both take **slowCounter** as argument. The guarded recovery tail `C286..C2B4` checks unsigned legacy clock delta >500 and may resample BDF8 after BDE4(1/0) toggles.

This is **VERIFIED STATIC for these direct routines**, not a claim of no nested callbacks/interrupts elsewhere. Exact global original runtime order, RNG seed=1 and pixel parity remain OPEN. See [v0.37](V037_REMAX_SCHEDULER_CATCHUP_STATIC_CLOSURE.md).
