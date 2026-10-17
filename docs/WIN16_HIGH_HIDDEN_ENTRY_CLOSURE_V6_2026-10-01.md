# Win16 High hidden-entry machine closure v6

Date: 2026-10-01. Continues draft PR #33 from `c6e128dd46d55fd21723fc3e6082413cd6953c36`.

## Result and evidence scope

All **70 v5 High candidates** pass independent binary entry/boundary checks and
receive separate machine dossiers: **1.3 = 9, 1.6 = 18, 1.8 = 19, 1.10 = 24**.
Win16 1.0 contributes reference counterparts but **zero new dossiers**, because
its v5 ledger has no High candidate. **No Medium-High or Medium row is promoted**.
These are machine-entry records, not 70 newly proved original source functions.

Primary inputs are the five original NE executables, verified against the exact
SHA-256 values in `analysis/n3d_build_manifest_2026-09-30.csv`. The v5 external
package supplies candidate locations and indexed-entry CFG evidence. Its CSVs
are parsed as data, not imported as executable analyzer code. Input hashes are
recorded in `analysis/win16_hidden_v6/summary.json`.

Each promotion requires:

1. Re-expand the actual executable's NE relocation source chains and resolve the
   incoming far-call target independently of the v5 resolved address columns.
2. Verify that each incoming call is an exact instruction boundary in the v5
   caller CFG and that its instruction bytes match the executable.
3. Disassemble afresh from the candidate entry, follow direct branch targets,
   stop at returns, reject undecodable/overlapping streams and unclosed jumps.
4. Require a return and no reachability from a legitimate preceding indexed entry.
   The one operand-interior old entry described below is explicitly recorded.

All 70 audited bodies have closed direct CFGs with returns; no unsupported
indirect-jump target is guessed. CFG closure is static evidence, not a claim that
every branch executes in ordinary gameplay.

## Addresses and boundaries

`machine_dossiers.jsonl` retains exact analysis selector:offset, NE segment
ordinal, start, exclusive envelope end, reachable byte ranges, file offset/end,
binary/body SHA-256, instruction bytes, incoming relocation records, callers,
callees, previous interval provenance and separate confidence fields.
`dossier_index.csv` is the compact entry/boundary index.

Selectors `1000/1008/1010/1018` follow the existing analysis convention for NE
segments 1/2/3/4. They are **not Windows loader-assigned runtime selectors**.
`runtime_va` is explicitly null: the on-disk NE file provides no stable flat
runtime VA. No address is converted to an invented linear VA. Envelope size and
reachable bytes are separate so internal alignment holes are not called code.

## Boundary correction

In Win16 1.10, `1010:D7C0` has a reachable far call at `1010:D7CA`:
`9A B8 3A 99 D7`, followed by `CB` at `D7CF`. The old mapped start
`FUN_1010_d7cc` lies **inside that call operand**. Decoding from it produced a
spurious `cmp` followed by the actual prologue at `1010:D7D0`.

`HIDDEN_1010_d7d0` is therefore a separately proved machine entry with its own
closed body. Its incoming evidence and boundary note are preserved. Calls in
that body are assigned once to the new entry rather than also to the stale
`FUN_1010_d7cc` interval. This does not silently declare every old mapped start
in the repository valid or invalid; historical v4 intervals remain provenance.

## Cross-version relations

There are **350 directional relation slots** (70 entries × five builds):

- **249 High structural counterpart relations**, including 70 self relations;
- **101 unresolved modified-or-unmapped slots**; no counterpart is invented.

Relations form **34 structural groups**, with no group containing multiple entries
from one build. This is an evidence grouping, **not canonical source/semantic
identity**. Empty cells in `structural_families.csv` mean no High closure from
this pass, not that a routine is absent or build-exclusive.

The matcher checks the full byte envelope with explicitly masked far/near call
operands, drifting absolute/non-stack data locations and large pushed address
operands. It preserves branch displacement, stack offsets and reachable
instruction layout, then checks import module/ordinal sequence. Parent source-1.0
interval anchors and internal callee interval anchors disambiguate repeated
short wrappers. The mask does not prove that changed globals have identical
meaning, or that normalized code has identical source semantics.

Examples of closed structural correspondence:

| 1.0 | 1.3 | 1.6 | 1.8 | 1.10 |
|---|---|---|---|---|
| 1008:6486 | 1008:6486 | 1008:6486 | 1008:6486 | 1008:6486 |
| 1010:D55E | 1010:D56A | 1010:D6DE | 1010:D6DE | 1010:D78C |
| 1010:D592 | 1010:D59E | 1010:D712 | 1010:D712 | 1010:D7C0 |
| 1010:ED0E | 1010:ED5A | 1018:0000 | 1018:00CA | 1018:0132 |
| 1010:EE48 | 1010:EE94 | 1018:013A | 1018:0204 | 1018:026C |
| 1010:EED2 | 1010:EF1E | 1018:01C4 | 1018:028E | 1018:02F6 |
| 1010:EF06 | 1010:EF52 | 1018:01F8 | 1018:02C2 | 1018:032A |

Reference counterparts in 1.0 or lower-confidence ledger locations are **not**
additional promoted dossiers. The individual relation ledger preserves target
entry/end, file offset and body/binary hashes; all semantic-equivalence fields
remain `not claimed`.

## Wrapper, compiler/MFC and application discipline

- **5 confirmed structural call wrappers**: 1.3 `1010:2B94` and the four builds'
  `1010:D59E/D712/D712/D7C0`. They forward calls in short closed bodies. Compiler
  or MFC authorship is **Unknown**, not established by a familiar prologue.
- **3 runtime-or-MFC wrapper candidates**: `1008:6486` in 1.6/1.8/1.10. Binary
  calls bracket `1008:4E24` with near calls to `1008:42FC` and `1008:437A`;
  these exact operations are proved, but the runtime/MFC origin is **Inferred**.
- **62 application-logic candidates** perform additional control/data work in
  application segments 1010/1018. This placement is supporting context, not
  proof of a specific gameplay mechanic. Their semantic purpose remains
  **Unknown**, and no original function name or contract is invented.

In particular, `1010:D78C` increments the dword at DS:`53DC` and makes six far
calls (including the relocation-resolved `1018:3940`). It is **not** classified as
an empty compiler thunk merely because it is short. Its renderer-related purpose
is a follow-up semantic question, not a new confirmed semantic label.

No compiler/MFC-generated routine is newly claimed as confirmed in this pass.
Entry and boundary confidence is High; that confidence does not transfer to
semantic purpose or source authorship.

## Updated CFG-owned callgraph

| Build | Near | Far internal | Far import | Direct total | Indirect | Newly reachable direct sites | Reassigned direct sites |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1.0 | 89 | 1,948 | 757 | 2,794 | 212 | 0 | 0 |
| 1.3 | 89 | 1,942 | 757 | 2,788 | 212 | 14 | 10 |
| 1.6 | 91 | 1,954 | 755 | 2,800 | 212 | 79 | 18 |
| 1.8 | 91 | 1,953 | 759 | 2,803 | 212 | 87 | 18 |
| 1.10 | 91 | 1,951 | 749 | 2,791 | 212 | 107 | 19 |

Counts are distinct static instruction sites, not execution counts or unique
caller/callee pairs. New bodies replace ownership inside their validated
byte envelopes, and direct target offsets remain exact. An internal target
inside an old interval is represented as its address plus containing-interval
provenance, not falsely as a call to that interval's start. Import identity is
module/ordinal; learned API names are not needed to establish these edges.

Far edges retain relocation record index/file offset/raw record bytes, source
fixup offset/type/flags, chain index/next link and target-resolution confidence.
The NE relocation record/site totals stay identical to v5. The v5 baseline
`410/959` trailing-content finding remains historical, not a claimed complete
boundary repair. The new 70 dossiers must not simply be added to old indexed
interval counts and advertised as a count of distinct source functions.

## Reproduction and regression checks

Requires Python 3 standard library and GNU objdump with i8086 support. Original
binaries and the external v5 output directory are supplied separately; neither
is downloaded by the analyzer.

```sh
python tools/win16_hidden_entry_v6.py \
  --binaries /path/to/original-exes \
  --v5-output /path/to/v5/output \
  --output analysis/win16_hidden_v6
python tests/win16_hidden_entry_v6_test.py -v
N3D_WIN16_BINARIES=/path/to/original-exes python tests/win16_hidden_entry_v6_test.py -v
```

Seven regressions cover High-only counts, closed boundaries, site uniqueness,
exact targets, reference-only mapping, the D7CC operand-entry mistake, stateful
routines not being empty thunks, and byte/fixup verification against all five
original executables. CTest registers the artifact regression when Python3 is
available; original-byte validation is enabled by `N3D_WIN16_BINARIES`.

Remaining closure targets are the 101 relation slots, symbol/provenance evidence
for the runtime candidates and independent semantic tracing for the application
bodies. Medium-High/Medium promotion remains gated on new independent evidence.
