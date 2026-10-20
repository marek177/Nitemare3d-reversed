# v0.77 — DOS1.9/2.0 bulk-copy provenance and remaining OBJECT+18 scope

Date: 20 October 2026. Integration of the NEXT7 original-static report and its
exported DOS2 tables. No original binary is executed or independently reopened
by this integration. `IMG` addresses are headerless, unrelocated load-image
offsets; do not substitute runtime segment:offset addresses.

## What the source narrows

The linear census has 29 REP MOVS sites per build, grouped into 21 logical
copies (eight MOVSW/MOVSB pairs). All 29 immediate destinations are locally
classified. The former “13 dynamic destinations” interpretation is corrected:
ten global-text sites and two record-text sites use FAR pointers as sources,
then copy into local buffers after XCHG and segment transfers.

One classified logical copy per build still has a record FAR destination with
an open transitive owner: DOS1.9 `E268`, DOS2 `E2A4`, 41 bytes. Its local near
caller belongs to a type-4 UI editor record with stride 18, FAR field +0E/+10;
this is not evidence for a generic gameplay OBJECT pool copy. Pointer-field
writers, bounds, indirect callers and allocator failures remain OPEN.

Five original initialized text lengths, including NUL, are 130/19/21/20/22.
Across the 16 optional-append combinations, replacing each previous NUL gives
maximum `130+18+20+19+21 = 208` bytes in a 258-byte local frame: 50 bytes spare.
This depends on unchanged source text and DS=SS; it does not prove safety for
mutated strings, all callback contexts or external inputs.

## Build-scoped anchors

| Field | DOS1.9 | DOS2 |
|---|---|---|
| Projection WORD writer | IMG:B47A | IMG:B4B6 |
| Damage WORD reader | IMG:8592 | IMG:859C |
| Depth reference | DS:4550 | DS:4552 |
| UI editor entry / near caller | IMG:E1A2 / ECC3 | IMG:E1DE / ECFF |

NEXT7 adds no second confirmed OBJECT+18 writer. Neither the typed REP census
nor local stack provenance excludes global aliases from other MOV instructions,
helpers, constructors, SAVE/LOAD, heap lifetime or cull-preserved depth. Natural
accepted-hit use of stale projection depth remains OPEN. See the archived
remaining-proof table for these P0 obligations and the independent INT63 scope.

## Integration validation

`python3 tools/n3d_next7_table_check.py` verifies 29 unique ordered DOS2 rows,
the nine family counts, 21 grouped transfers, the still-open record owner, and
all 16 reported-length combinations. Every exported row retains global
OBJECT18 exclusion = NO. This is exported-table consistency and independent
length arithmetic, not a fresh original-EXE proof.

The CSV files preserve the extracted tabular source content without the
Library's parsed-sheet wrapper. Their archive hashes identify these exported
texts, not the original on-disk CSV encoding or missing original executable.

## Renderer evidence boundary

Two V070 source reports are archived for provenance. The existing DOS2 FEFA/CAB8
contract on main remains the applicable research checkpoint. The separate
Exact Components V070 package reports six CTest cases and 26 Python checks
(one skipped without private data), but its component headers/installer were
not inspected or imported here. Those source-session counts are not current
checkout tests. No active-renderer or pixel-parity claim follows from archiving
these reports; Raycaster.cpp and main.cpp are unchanged.
