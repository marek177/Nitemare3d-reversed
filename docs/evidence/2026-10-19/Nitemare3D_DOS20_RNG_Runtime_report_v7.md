# Nitemare 3D DOS v2.0 — RNG runtime closure (2026-10-19)

## Scope and provenance

- Game: original DOS Nitemare 3D v2.0 from user-provided `all-nite3d.zip`; gameplay runs using compressed `N3D.EXE` with its original data files.
- Reference static executable: `N3D-E-20.EXE`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Instrument: modified DOSBox-X 2026.10.01 N3D Advanced History v3, debug CPU + memory write history, Xvfb Linux environment.
- This report distinguishes binary disassembly, actual I/W runtime events, and not-yet-proved hypotheses.

## Result: CLOSED for the observed random-event timer branch

The **breakpoint-first run v7** stopped Nitemare at **runtime CS:IP `1061:1D56`**, *before* changing the phase flag. The debugger showed `DS:[3636] == 1` and `DS:[3634] == 0xFFFF`. We enabled N3DTRACE at that breakpoint and configured **`N3D_TRACE_STOP_CSIP=1061:1D71`** so it captured only relevant instructions. It automatically stopped at that PC.

**Minimal real trace:** 43 CPU instruction events (`I`), 17 memory-write events (`W`), 4,756 raw bytes, stop reason `STOP_CSIP`. All assertions in `verify_rng_phase_v7.py` PASS.

| Executed PC | Write / control operation | Old | New |
|---|---|---:|---:|
| `1061:1D56` | `DS:[3636]` phase byte | `01` | `00` |
| `1061:1D5B` | `CALL 17DE:01A0` (RNG wrapper) | — | — |
| `1A12:3213` | `DS:[24B8]` RNG low word | `0001` | `E2C0` |
| `1A12:3216` | `DS:[24BA]` RNG high word | `0000` | `0029` |
| `1061:1D6A` | `DS:[3634]` countdown word | `FFFF` | `00C9` (201) |

All four writes have `hasold=true`, showing *previous* memory contents, and occur in the indicated execution order in one trace. Runtime `DS=2F95`; linear addresses: phase `0x32F86`, countdown `0x32F84`, RNG state low `0x31E08`, RNG state high `0x31E0A`.

The exact generator, independently reconstructed from `N3D-E-20.EXE` at `1A12:31F8`, is:

```c
uint32_t next = (uint32_t)(state * 0x000343FDu + 0x00269EC3u);
uint16_t result = (uint16_t)((next >> 16) & 0x7FFFu);
```

With observed old state `0x00000001`, calculated next state is **`0x0029E2C0`**, exactly matching both recorded word writes. At `1A12:321F`, the recorded AX is **41** (0x0029); it remains 41 on return to `1061:1D60`. The instruction sequence performs signed division by 240 and adds 160: **`160 + (41 % 240) = 201`**, which matches the countdown write.

### Independent longer trace v4

A separate run broke at `17DE:01A0` and began tracing directly from the RNG wrapper. It recorded **805,890 instructions and 181,126 memory-write events**, with one RNG execution. `assert_rng_v4.py` verified the *same* old/new RNG state, result, and first countdown values.

- RNG wrapper → RNG generator → return to **`1061:1D60`**.
- New countdown **201**, subsequent recorded decrements **201→200→199**.
- Global tick written as **85→86→87→88** during this sequence.
- Independently checks return AX=41, memory writes, and source SHA-256. `strict_runtime_validation.json`: **PASS**.

The longer trace is truncated by the intentional 80 MiB recording limit. The minimal v7 trace is complete *within its chosen start/stop addresses*, not for the remainder of the game.

### Position within the top-level tick

Previously recorded E1M1 trace found the top-level update starting at `1402:0370`, with 10 regularly ordered call sites. Its call at `1402:039E` targets the timed/random-effects routine `1061:1CFC`. The newly observed RNG caller `1061:1D5B` belongs to that routine, so **the confirmed random timer draw belongs to the `039E` substep**, after the `1402:037D` 26-byte actor-list traversal, in this call order. This does **not** imply that all possible RNG consumers or all GUARD/projectile scheduler updates follow the same fixed pattern.

## Static phase logic (not all branches runtime tested)

`1061:1CFC` has gating on game mode `DS:[626A]`, sub-mode/tick fields, and an input parameter. On the countdown path, it reads the old 16-bit countdown, decrements the stored value, and checks whether the **old value was zero**. If zero and phase `DS:[3636]` is **0**, it sets phase **1** and countdown **3**; if phase is **1**, it sets phase **0**, calls RNG, computes `rand() % 240 + 160`, stores the new countdown and proceeds to other side effects. The latter branch is now proved end-to-end by the v7 runtime trace. In the former previously recorded 12-tick window, the countdown went 44→32 but its expiry was not yet observed.

## Incomplete / open proof obligations

1. **Where the state value 1 was initialized**: both live RNG captures show state 1 before the draw. They do **not** capture an execution of the static seed setter `1A12:31E6` or the seed-1 wrapper `17DE:01A6`. An exploratory seed-wrapper breakpoint did not produce a confirmed hit during normal E1M1 launch. Its source, including the hypothesis about DEMO seed, remains **OPEN**.
2. **Full RNG ordering:** the 22 statically located direct wrapper calls include actor/animation, event, weapon/combat candidates; the observed run covers only *one* timer-related draw. These consumers must be individually reached and assigned to a tick and caller chain.
3. **Version comparisons**: DOS 1.9 and Win16 engines not verified by this trace.
4. **DEMO replay determinism**: no complete DEMO-input/RNG state sequence or final CRC established in this cycle.
5. **Renderer/weapon/projectile parity**: not part of this test.

## Reproduction and data

The proof bundle includes source scripts, full 60-event minimal trace (`trace-000000.n3dt`), SHA-256 checks, extracted event JSON, and breakpoint screenshots. The optional second bundle contains the four original binary chunks (~80 MiB uncompressed) of the longer 805,890-instruction trace.

For the v7 minimal capture: launch the modified emulator with `N3D_TRACE_AUTOSTART=0` and `N3D_TRACE_STOP_CSIP=1061:1D71`, set the breakpoint `BP 1061:1D56` before `RUN`, reach E1M1, then issue `N3DTRACE START` and `RUN` from the paused debugger. The trace automatically ends just before `1061:1D71`. Run `verify_rng_phase_v7.py` against the captured trace and reference EXE. The provided scripts have environment-specific paths and must be adapted if run in another filesystem.

**Next priority:** locate the initialization writer(s) for `DS:[24B8]` from startup or DEMO path via static xrefs, then confirm with a targeted memory watch; only then correlate seed/numbered draws with DEMO input tick ordering.
