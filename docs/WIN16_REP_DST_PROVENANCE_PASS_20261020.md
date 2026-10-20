# Win16 1.10 — REP MOVS/STOS destination provenance, static pass

**Audit:** 20 October 2026. **Scope:** the user's pre-existing original
Win16 1.10 Ghidra disassembly `nite3w(1).docx`, original code paths and
the whole-file NE segment table. No new original game runtime and no
fresh SHA check for the 230,400-byte v1.10 EXE in this pass.

## 83 original Ghidra-listed REP write sites

| Original 16-bit instruction | Sites |
|---|---:|
| `REP STOSB` | 7 |
| `REP STOSW` | 17 |
| `REP STOSD` | 11 |
| `REP MOVSB` | 14 |
| `REP MOVSW` | 20 |
| `REP MOVSD` | 14 |
| **Total** | **83** |

All 83 addresses and opcode prefixes (F3 AA/AB/A4/A5,
F3 66 AB/A5) are recorded in:
`other/n3d/builds_12/static_byte_evidence/N3D_Win110_Ghidra_REP_destination_register_20261020.csv`.
This is a census of original Ghidra **listed/discovered** sites, not proof
that code islands, unrecognized instructions, non-REP accesses or 16-bit
indirect pointer paths are globally complete.

### First 25 source-bounded REP sites: all MOVSD (14) and STOSD (11)

Reviewing their preceding ES, DI, ECX instructions yields these
destinations and nominal byte lengths:

| Site group | Sites | Destination provenance and bounds |
|---|---|---|
| Stack-local | 14 | ES=SS and DI=BP-relative stack locals; 16/20/768/1,024 bytes depending on site |
| LocalAlloc | 2 | `3:4E21`, `3:500E`; near heap `LocalAlloc(0x20,90)` return; 22 MOVSD + one MOVSW = **90 B** |
| Fixed DGROUP | 5 | Exact ranges listed below, disjoint from both watched flags |
| Other NE segment | 2 | `3:7688` (original Ghidra ES selector 1040, 64 B); `4:2264` (ES selector 1030, 24 B) |
| WinG bitmap bits | 1 | `3:2FDB`; 16,000 DWORDs = **64,000 B** in WinG bitmap storage |
| GlobalLock heap | 1 | `3:E1D5`; 8 DWORDs = **32 B** in returned GlobalLock far pointer |
| **Inspected** | **25** | Conditional on original segment/allocator contracts, not observed runtime |

The above classification is disjoint by source: each inspected entry
belongs to exactly one category. The remaining **58** Ghidra REP sites
have not yet had sufficient destination or copy-length provenance
established. Some of those 58 have a symbol annotation at the target,
but this is not an actual complete bounds proof.

### Fixed DGROUP writes: exact arithmetic exclusion

The five fixed destination intervals are:

| REP site | First byte | Last byte | Bytes |
|---|---|---|---:|
| `3:5102` | `DS:4C74` | `DS:4C9D` | 42 |
| `3:DACA` | `DS:3930` | `DS:3943` | 20 |
| `3:DB65` | `DS:4BD4` | `DS:4BE7` | 20 |
| `3:51C5` | `DS:8E90` | `DS:8EAD` | 30 |
| `3:BA27` | `DS:4BE8` | `DS:4C45` | 94 |

The word immediately beyond `3:51C5`'s zero-fill is
`DS:8EAE`, **exactly the exclusive end of the file-backed Win16
v1.10 DGROUP/NE segment 10**, whose original segment table records
36526 bytes = `0x8EAE`. This is a useful static offset/length cross-check,
not proof of a total segment allocation or of all DGROUP writers.

For each of these five intervals,
`DS:00A2` (one-shot flag) and `DS:46B2` (timer mode) are outside
the written ranges. Thus these five fixed REP writes **cannot directly
overwrite the watched flags** in this original address model.

The `STOSD` copies at `3:51C5` and `3:BA27` include one
trailing `STOSW`, reflected in the 30/94-byte total, and
`MOVSD` at `3:5102` includes one trailing `MOVSW`, reflected
in the 42-byte total. Counting only REP DWORD operations would
understate those written bounds.

### Two heap copies: KERNEL.LOCALALLOC provenance

The original helper `FUN_1008_5AB0` on its normal path uses:

    1008:5ACC PUSH 0x0020
    1008:5AD0 PUSH [BP+6]       ; requested bytes
    1008:5AD3 CALL FAR KERNEL.LOCALALLOC
    1008:5AD8 MOV [BP-4],AX

The caller passes `0x5A` (90 decimal). At both `3:4E21`
and `3:500E`, the returned 16-bit AX is loaded into DI,
ES receives DS, ECX=22 and the code performs:

    REP MOVSD         ; 22 * 4 = 88 bytes
    MOVSW             ; 1 * 2 = 2 bytes
                       total = 90 bytes

Under the ordinary Windows 3.x LocalAlloc API contract, successful
nonzero fixed local allocations represent separately allocated valid
heap blocks, not aliases of the static global bytes containing
`00A2` or `46B2`. This is a conditional memory-manager
contract, not a fresh measured heap-range assertion.

If allocation returns AX=0, the caller invokes the Win16 fatal
message helper before the copy. If that helper were to return, the
literal destination DI=0 would instead write DS:0000..0059 (90 B),
which still does **not** cover the two flags (00A2 or 46B2), while
introducing an obvious separate low-memory-corruption concern.
Do not label this branch as normal successful execution.

### Known high-priority unclosed destinations

- Generic `REP MOVSW/MOVSB` helpers in `1008:605F/6063`,
  `1008:6092/6096`, `1008:6CA0/6CA4` and other wrappers:
  destination pointers are partly caller-provided.
- `3:527E/5282` and `3:52A1/52A5`: string-block copies in
  `FUN_1010_5260`, with ES:DI destinations around `DS:36BE`
  and lengths derived by scanning for NUL. A global
  `DS:46B2` overlap is not established, but neither is an
  exhaustive input-length bound.
- Additional `REP STOSB/STOSW` graphics/memory routines with
  parameter-derived ES:DI or loop lengths.
- Calls to other memory-move routines, singly executing STOS/MOVS,
  indexed/ES-based scalar stores and writable function pointers:
  outside this 83-site REP text census.

A REP destination annotation like `ES:DI=>DAT_1048_3A7A` is
not sufficient to assert that its variable length stays within
the identified symbol.

## Automated verification, evidence grades and limits

- `tools/n3d_win16_rep_destination_audit.py` checks 83 unique
  code sites, the six REP operation counts, the 25 local source
  length/destination classes and five fixed DGROUP ranges.
- `tests/test_n3d_win16_rep_destination_audit.py` includes 12
  deterministic synthetic tests, including deliberately corrupted
  sites/opcodes, invalid lengths, 16-bit wrap, and a hypothetical
  copied region overlapping DS:46B2.
- `.github/workflows/win16-timer-ne-proof.yml` executes the tests
  in CI. It does NOT execute or freshly hash original Win16 v1.10
  in its synthetic-only job.
- Previous `tools/n3d_win16_raw_fixed_store_candidates.py`
  scanned all four file-backed code NE segments of **original SHA-pinned
  Win16 v1.8**, but that earlier scalar-pattern scan does not exclude
  any of the 58 newly tracked REP/pointer-flow cases.

Status:
**5 original fixed-DGROUP REP intervals excluded from overwriting the
two watched flags; 25 source-level REP destinations classified with
stated assumptions; 58 REP destinations and the complete computed
alias writer graph remain OPEN.**
No increase in behavioral/timing/rendering 1:1 parity percentage.
