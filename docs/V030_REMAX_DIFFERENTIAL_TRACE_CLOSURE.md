# v0.30 RE MAX — differential FAST/RNG traces and evidence-seal gate

Date: 2026-10-14. Revision after
[v0.29](V029_REMAX_SCHEDULER_TRACE_AND_EDGE_CASES.md).

**Scope:** New *verification infrastructure* for the highest-priority open
runtime questions. The exact DOS v2.0 RNG LCG and 20 direct caller offsets
come from the already documented v0.20/v0.22/v0.26 audits. **No newly captured
original-game CPU trace is included or claimed.** No percentage increase is
justified by this version.

## Why v0.29 needed a second-pass audit

The previous [single-trace verifier](../tools/n3d_trace_audit.py) can establish
that the **provided** RNG rows satisfy the 32-bit LCG and the known direct
callsite census. It cannot establish the expected number or identities of
all draws. For example, a reconstruction can use the same seed and LCG but
replace the second GUARD draw with an animation draw; both streams can be
internally consistent and end in the same RNG state if they each contain the
same number of draws.

Likewise, filtering only the *direct* children of the FAST routine can miss
a difference inside a nested/reentrant helper, and a complete-looking sequence
of 11 direct calls can be captured before the original invocation actually
returns.

**Correction of the verification claim:**
> Valid LCG transitions, matching final state, or matching FAST direct
> children do not establish 1:1 call order, interval completion or origin.

This is a diagnostic/tooling discovery, not newly recovered game logic.

## Added differential checks

- [tools/n3d_trace_compare.py](../tools/n3d_trace_compare.py) reads two ordered
  CSV traces (reference versus candidate). It checks each against the v0.29
  format validator, then compares all rows **in capture order without sorting**.
  Reports the zero-based index and full expected/observed records at the
  first difference, or a length mismatch even when one trace is an exact
  prefix.
- For RNG, records are `caller,before,after,result`. Both streams must
  satisfy the DOS v2.0 LCG and contiguous states from the supplied seed.
  The comparator detects a changed callsite **even if the final RNG state
  is identical**.
- For FAST, records are `invocation,caller,target`. The earlier direct
  `C150` model still runs, but the differential comparator also checks
  **nested** events, so a change inside a helper is no longer invisible.
  The `--invocation` and `--tick-at-gate` options select the reported
  direct-call model, NOT the complete nested scheduler.
- A one-row lookahead may emit `candidate_record_maybe_missing` or
  `candidate_record_maybe_extra` as a **logger diagnostic**, not proof that
  original gameplay skipped/added a draw. No guesses are used to realign or
  suppress the first divergent event.
- [src/re/N3DV030TraceClosure.hpp](../src/re/N3DV030TraceClosure.hpp) adds an
  equivalent strict, constexpr-capable C++ comparison over the already
  recorded `v020::RngTraceEntry` layout. Missing/invalid/short streams
  cannot accidentally pass as matching prefixes. Attestation is separate
  from numerical equality.

## Executable fingerprint and build boundary

The original DOS v2.0 **unpacked** executable-image profile, already recorded
in [v0.22](V022_REMAX_VERSION_EVIDENCE_REGISTRY.md), is:

| Property | Expected |
|---|---|
| Byte length | 171,360 |
| SHA-256 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |
| Version scope | DOS v2.0 unpacked image only |

Pass `--reference-image PATH` to hash a locally owned unpacked image. A
different build, packed release binary, Win16 executable, or corrupted
unpacked image fails that check. No original game bytes are added to GitHub.
Importantly, **matching this fingerprint establishes image identity, not
that a particular CSV was genuinely recorded from that image**.

## Capture boundary envelopes

CSV files contain event rows, not proof of the start/end of a capture.
A separately produced JSON envelope can be checked for consistency:

```json
{
  "schema": "n3d-trace-envelope-v1",
  "trace_type": "rng",
  "build": "dos-v2.0",
  "row_count": 3,
  "csv_sha256": "<actual SHA-256 of the CSV file>",
  "begin": "demo_seed_1",
  "end": "first_gameplay_input",
  "closed": true
}
```

For the candidate, set `build` to the actual reconstruction build name.
The comparator validates each declared row count, SHA-256 digest, version,
marker nonemptiness and `closed:true`; it requires identical begin/end
names on both sides. The "closed" field is a **recorder assertion**, not an
independent observation that all CPU instructions/events were captured.
A truthful envelope must only be emitted by instrumentation that **actually
observed** the entry and return boundary. Capture producers must preserve
the raw debugger trace, original binary hash, timestamp and test fixture.

Without both envelopes and the verified unpacked reference image, a matching
result is labeled `trace_match_unsealed`. The optional
`--require-provenance` gate rejects unsealed matches. A sealed match is still
only `trace_match_with_attested_provenance`; `original_runtime_verified`
remains **false** until independent real-game capture validation.

## Usage

```sh
# Offline comparison; useful during development, NOT a complete original proof
python tools/n3d_trace_compare.py rng /path/ref-rng.csv /path/port-rng.csv --seed 1

# Require declared beginning/end boundaries and exact DOS v2.0 image identity
python tools/n3d_trace_compare.py rng /path/ref-rng.csv /path/port-rng.csv --seed 1 \
  --reference-envelope /path/ref-rng.json \
  --candidate-envelope /path/port-rng.json \
  --reference-image /path/unpacked-dos-v20.bin --require-provenance

# Compare complete event ordering within FAST capture; nested helper events
# are compared too, while direct children get the known static-order check
python tools/n3d_trace_compare.py fast /path/ref-fast.csv /path/port-fast.csv \
  --invocation 7 --tick-at-gate 8
```

The reference and candidate CSVs must each have the header for their trace
type; numeric cells use decimal or `0x` hexadecimal. The comparator emits
JSON and returns 0 only for an accepted match, 1 for mismatches/insufficient
required provenance, 2 for malformed options or input. A passing result is
never automatically a promotion to `VERIFIED_EXE` or `BEHAVIORAL`.

## Tests

- [tests/test_n3d_trace_compare.py](../tests/test_n3d_trace_compare.py):
  synthetic RNG equality, same-final-state/wrong-caller, lost draw versus
  missing *logged* row, one-step logger clues, empty and truncated traces,
  FAST nested differences, gated last call, wrong build, checksum/row-count/
  boundary failures, incorrect binary fingerprint and provenance gate.
- [tests/v030_trace_closure_test.cpp](../tests/v030_trace_closure_test.cpp):
  compile-time and runtime tests for same-state/different-caller,
  incomplete captures, seed mismatch, bad result, unknown caller and
  unsealed versus attested equality.
- CI compiles and tests C++ v0.30 and runs Python tests on Windows/Linux
  with two supported Python versions, without shipping original assets.

## Runtime experiment now made measurable

1. Fingerprint the exact DOS v2.0 executable/unpacked image **before**
   loading symbols. Do not transfer `1000:C150`, `DS:4540` or RNG offsets
   to Win16 or other DOS builds.
2. Instrument RNG far-target calls at `0FBA:01A0` (not only a wrapper),
   record every `caller,before,after,result` from DEMO seed 1 to
   the first observed gameplay input.
3. Capture FAST direct and nested call events, a unique invocation ID
   per FAST entry, and the *observed* tick at the gated call. Do not flatten
   reentrant or E2M10 callback paths.
4. Preserve the raw debugger trace; export ordered CSV and boundary records.
   Build and validate capture envelopes only after observing both boundaries.
5. Compare original and reconstruction; if divergent, isolate the **first**
   caller/state/step difference, then the instruction write/branch.
6. Advance evidence confidence only after another controlled reproduction.
   The project still has unclosed scheduler catch-up, projectile FB–FE,
   Multi Plasma, rare event paths, LOAD resume and pixel-perfect renderer.

**No new original-game runtime trace, new original enemy rule, or 1:1 parity
claim is made by v0.30.**
