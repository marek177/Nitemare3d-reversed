# Nitemare 3D RE MAX — DOS v2.0 DEMO RNG 229-draw acceptance

**Date:** 2026-10-20  
**Evidence class:** new independent re-audit of **previously captured** original DOS v2.0 runtime evidence (D02-D). No new DOSBox-X execution in this update. This is not a 1:1 original-vs-port comparison.

## A. Source and provenance

Source files from the user's 19-Oct D02-D archive:

- N3D_REMAX_D02D_COMPLETE_EOF_AND_POSTEOF_20261019.md
- N3D_REMAX_D02D_RNG_LEDGER.csv — 229 derived original-execution records
- N3D_REMAX_D02D_CLOCK_CONTEXT_220.csv
- N3D_REMAX_D02D_SOURCE_AND_EVIDENCE_20261019.zip

Original DOS v2.0 packed N3D.EXE SHA256: a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485. Unpacked N3D-UNFU.exe SHA256: 552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301. DEMO.1 SHA256: 25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840.

The original game, raw CPU traces, and private emulator snapshots have not been published in this PR.

## B. Independent derived-ledger checks

All **229/229** stored entries were reparsed in original file order. Verified:

1. Ordinals 1–229 with no gaps, sorting, or realignment.
2. First RNG state 1; every before-state equals previous after-state.
3. Every after-state equals (before * 214013 + 2531011) modulo 2^32.
4. Every AX equals (after >> 16) & 0x7fff.
5. All 229 store-observed, return-observed, and instruction-complete flags true.
6. Captured CPU event ordering strictly increasing; scheduler/DEMO context monotonic.
7. Last RNG state **0xD0643564**, AX **20580**.

Observed direct RNG callsite counts, using **MZ load-image offsets**:

| Callsite | Calls | Callsite | Calls |
|---|---:|---|---:|
| 0xA047 | 93 | 0x9FE3 | 62 |
| 0x85AD | 24 | 0x56A6 | 22 |
| 0x573F | 15 | 0x525E | 5 |
| 0x5582 | 2 | 0x9D6E | 2 |
| 0xA12B | 2 | 0x9F36 | 1 |
| 0x9C98 | 1 | **Total** | **229** |

Longest identical-callsite runs: 32 at 0xA047 (draws 150–181), 23 at 0xA047 (114–136), 15 at 0x9FE3 (21–35), 14 at 0x9FE3 (80–93). These are RNG callsite bursts, **not** counts of distinct actors or logical frames. Only 11 of the 22 literal static FAR RNG callsites execute in this particular DEMO; the unvisited ones are not proven dead code.

## C. GUARD41-related death-window RNG evidence

| Draw | Caller | AX | State after | Scheduler entries before | DEMO record |
|---:|---|---:|---|---:|---:|
| 15 | 0x85AD | 9961 | 0xA6E9C9A6 | 83 | 11 |
| 16 | 0x9FE3 | 491 | 0x81EB59D1 | 83 | 11 |
| 17 | 0x9FE3 | 2995 | 0x0BB31550 | 83 | 11 |
| 18 | 0x9FE3 | 11942 | 0xAEA69ED3 | 83 | 11 |
| 19 | 0x9D6E | 4827 | 0x12DBCE4A | 91 | 12 |

All five calls numerically match the existing DOS1.2 GUARD41 death/post-death RNG chain at corresponding functional callsites. **The DOS2 RNG ledger does not identify actors or show every intervening instruction.** Independent original DOS2 before/after snapshots show GUARD41 HP 111→0, score 0→100, MAP marker A5→00, and the same RNG endpoints. Combining these two types of evidence **does not** prove a single instruction-exact DOS2 death sequence.

Statically established DOS2 path anchors: damage receiver image 0x5F74, damage helper call 0x5F88, shared RNG caller 0x85AD, lethal HP writer image 0x5FA3 (**physical file offset 0x61A3**), death reaction helper caller 0x5FAD, and selector RNG callsite 0x9FE3. Do not confuse image offsets with file offsets or live segment:offset after relocation.

## D. DEMO EOF and clock constraints

D02-D reports original 275/275 DEMO input records, original reader AX=0 on the first EOF, and an independently witnessed **276th input-mask store after EOF** (saved last buffered mask 0x0090). This establishes **at least one** post-EOF reapplication, not an eventual termination policy.

At fixed 3000 vs 7000 CPU cycles, two original runs retain exactly the same first 220 RNG caller/value/state triples but differ in scheduler entry counts at RNG #211 (1051 vs 1059), and applied DEMO record context at RNG #219 (267 vs 273). The 7000-cycle sample reaches EOF with 220 rather than 229 draws. The first responsible clock/due-branch divergence remains OPEN: these are **not** differing LCG algorithms.

## E. Portable verification

Run against the privately supplied derived CSV:

    python3 tools/verify_d02d_rng229.py /private/N3D_REMAX_D02D_RNG_LEDGER.csv --json /tmp/d02d.json

The verifier rejects altered order, arithmetic, completeness markers, recognized callers/counts and death-window scheduler context. It does **not** parse raw .n3dt files or re-execute Nitemare 3D. Source provenance must be kept with the original capture package.

## F. Remaining P0 — DOS2 GUARD41 instruction-exact death

At the naturally reached lethal HP writer, confirm runtime opcode 26 88 64 10, matching actor pointer and HP=111. Start a bounded original-game trace **there**, not at BIOS. Record real CPU and memory write order for:

- HP→0 and exact actor identity; RNG draws 15–18 and their rejection/acceptance decisions;
- 32-bit score DS:4182/4184, linked MAP A5→00, WORLD/OBJECT updates, guard-specific handler return;
- subsequent state 0→9→0A, RNG #19, first later scheduler pass, and drop or pool release if any.

Compare DOS1.2 and DOS2 using normalized actor identities, callsite families and event ordering, not raw segment offsets.

**Closure:** D02-D exported 229-draw arithmetic and event-order checks PASS. Original execution is attributed to the prior D02-D captures. Complete V2.0 GUARD41 death CPU ordering, indirect RNG census, post-EOF termination, and original-vs-clean-room 1:1 parity all remain OPEN.


## G. Strict order regression and GitHub Actions result (20 Oct 2026)

A review of the first verifier revealed a false-acceptance gap: checking 11 callsite totals and the death-related #15–19 window alone could permit two unrelated callsites to be swapped while leaving all LCG outputs and call counts unchanged.

That gap is now closed with two compact, source-derived reference sequences:

- **229/229 original callsite IDs in exact ordinal order**, stored in a nibble-coded literal. Callsite permutations fail even when totals are unchanged.
- **52 unchanged scheduler/DEMO context runs**, expanded to 229 exact tuples of (scheduler entry count, last DEMO record ordinal, key, input mask). This is specifically the D02-D canonical reference run; it is not an expectation that different cycle settings must match it.

All reference tokens and tuples were independently cross-checked against the user-owned 229-row exported CSV in their original order: **229/229 matches, zero mismatches**. The CSV itself is not republished here.

GitHub Actions workflow \`.github/workflows/d02d-rng229.yml\` completed **SUCCESS** (run ID \`39441850584\`). It executed **9/9 Python unittest cases**: one positive synthetic reference plus eight deliberately modified negative cases (caller swap preserving counts, scheduler context, DEMO mask, AX, LCG state, missing original-instruction witness, event reordering, missing row). These are **verifier regression tests using synthetic fixtures**, not executions of original Nitemare 3D.

CI and the independent exported-CSV re-audit are complementary, but neither claims original CPU-trace replay or original-versus-port behavioral/timing/rendering parity. The P0 death writer-to-epilogue trace of DOS v2.0 remains OPEN.
