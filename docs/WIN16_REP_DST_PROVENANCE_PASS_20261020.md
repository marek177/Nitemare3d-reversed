# Win16 1.10 — REP MOVS/STOS destination provenance, static pass

> **20 October 2026, second-pass supersession:** the latest
> source-local evidence covers **46 fixed/source-bounded REP sites**,
> plus **one symbolically bounded LocalAlloc STOSW**, leaving
> **36 unclosed Ghidra-listed REP sites**. These add 10 literal
> portal/pentagram string copies (combined <=210 bytes into a
> 256-byte local), two 64,000-byte video-selector operations
> and a dynamically sized heap clear that writes n+1 nominal
> bytes for odd n<=65533. Historical 34/49, 25/58 counters
> below are retained as first-pass context. Read the
> [second-pass original-static audit](WIN16_REP_ALIAS_CLOSURE_PASS2_20261020.md).
> Nothing about 1:1 runtime parity or full alias closure has changed.


> **Follow-up on 20 October 2026:** the newer audit has now bounded
> **34/83** original Ghidra REP sites (25 REP32 plus 9 REP16), including
> **7** fixed DGROUP copy/fill spans that do not overlap `DS:00A2` or
> `DS:46B2`; **49** sites remain without complete destination/length
> provenance. Also, all **12 named direct file-builder call paths** have
> a literal suffix (`config.sav` twice, `user.sav` ten times).
> The `-p` command-line directory prefix can be written indirectly
> into `DS:46BE`; its maximum size is still UNPROVEN. See
> [filename/P0 proof](WIN16_FILENAME_PREFIX_P0_STATIC_20261020.md).
> Historical first-25/remaining-58 paragraphs below document the
> earlier, superseded intermediate pass.


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

## High-priority potential alias: string staging at DS:36BE

**New exact address condition:** the original Win16 1.10 function
`FUN_1010_5260` writes a temporary, NUL-terminated string into
`DS:36BE`; the multimedia-timer flag `DS:46B2` is exactly
`0x46B2 - 0x36BE = 0xFF4 = 4,084` bytes beyond that base.
The next declared input string region starts at `DS:46BE`, exactly
4,096 bytes beyond the staging base. The watched flag is thus
*12 bytes before* that next region and inside the final 12 bytes of
the mathematical 4-KiB interval beginning at `DS:36BE`.

Relevant original disassembly:
- `3:5265` sets `DI=46BE`, `3:5268` sets `SI=36BE`.
- `3:526F` sets `CX=FFFFh`; `3:5274` scans the initial string with
  `REPNE SCASB` up to a NUL; `3:527E/5282` copy its bytes into
  `DS:36BE` with `REP MOVSW/MOVSB`.
- `3:5287` loads a caller-provided second string pointer, scans its
  length, then `3:529A` scans the staging buffer for its NUL.
- `3:52A1/52A5` append the second string, replacing the first
  terminator using `REP MOVSW/MOVSB`. The scans begin with
  `CX=FFFFh`; there is **no explicit capacity comparison** in the
  inspected helper body.

For ordinary, nonwrapping NUL-terminated input strings with
`n1` and `n2` *character counts excluding terminators*, the
combined string writes `n1+n2+1` bytes including the final NUL.
The timer byte is at output offset `0xFF4`, so the copy
**could touch `DS:46B2` when `n1+n2 >= 4084`**.
At equality the byte written there would be the final NUL;
larger sums may write a preceding character.
This is a conditional address/length proof, **not evidence that the
original gameplay supplies a string of such length or ever changes
the clock flag through this path**.

**Original DS:101E literal verification:** the existing Ghidra DGROUP
image at `1048:101E` contains the NUL-terminated bytes of
`config.sav` (10 printable characters plus one terminator).
At `3:52F5` and `3:5358`, the helper's argument is the literal
near offset `0x101E`. Therefore for these two direct callers
`n2=10` exactly. A prefix of `n1=0` produces only an
11-byte output and cannot affect the clock byte. More generally
`n1 <= 4073` remains below the timer flag; `n1 >= 4074`
would satisfy the conditional address overlap test.
The preceding global string `DS:46BE` has an original zero
initial byte and is explicitly cleared at `3:0ED9` during the
one-shot reset, but proving that no pointer writer grows this
prefix on every reachable call is a separate obligation.

Five direct callers are named in original Ghidra XREF:
`3:52F5`, `3:5358`, `3:5397`, `3:548C`, `3:5759`.
The first two directly pass a fixed text pointer `DS:101E`,
whereas the remaining callers forward varying function parameters
or a derived register. Complete caller input-length provenance
and any library/environment length guarantee remain OPEN.

The machine-readable ledger now assigns all four REP sites the
class `STRING_DSGROUP_BUFFER_NO_LENGTH_BOUND` while retaining
them among **58 unresolved destinations** (not among the 25
source-bounded destinations). The Python verifier exposes the
threshold and its regression tests reject attempts to mark the
string alias unreachable on the present evidence.

Prioritization: if a future original trace or bounded static
caller proof shows `n1+n2 < 4084` for all reachable invocations,
this candidate can be closed without running arbitrary stress tests.
Otherwise it needs a controlled input-boundary runtime trace, after
static exhaustion, to distinguish merely possible write geometry
from observed flag corruption.

## Automated verification, evidence grades and limits

- `tools/n3d_win16_rep_destination_audit.py` checks 83 unique
  code sites, the six REP operation counts, the 25 local source
  length/destination classes and five fixed DGROUP ranges.
- `tests/test_n3d_win16_rep_destination_audit.py` now includes 21
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

Current status:
**7 original fixed-DGROUP REP intervals exclude the watched flags;
46 fixed/source-bounded REP sites plus one symbolic LocalAlloc case
are now mapped, while 36 remaining REP sites and the complete computed
alias writer graph remain OPEN.** The three parametrized filename
wrappers have fixed user.sav suffixes at their named direct callers;
their directory prefix can still be altered via -p or unknown aliases.
See the second-pass audit above.
No increase in behavior, timing or rendering 1:1 parity percentage.
