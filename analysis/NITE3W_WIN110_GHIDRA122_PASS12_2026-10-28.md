# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 12

## Finding

Recovered two update countdown mechanisms reached through D974: a 22-byte record transition and two byte-sized timed flags. Established exact update-call arguments omitted by earlier decompiler displays. Zero underflows before the expiry test on decrement boundaries. Models cover local state under explicit nonmutation/nonalias assumptions; no runtime or complete scheduler parity claim.

Input `nite3w - 110.exe`,230400 bytes, SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra12.2 PUBLIC20261016, JDK25.0.2.

## Evidence and behavior

### Sampled update call chain

Confirmed / High, 1010:D974..D9C5: calls in order 1D4E,80AA,BB26(DWORD tick),BE56,2210,BE62,BA74(WORD0),A3B6(WORD11h),AA90(DWORD1). If low tick byte &7 is zero, additionally calls A3B6(WORD10h). Raw PUSH widths are material: AA90 receives a DWORD1, not merely a WORD. BA74 receives update-mode0. Earlier generated C displays omitted these arguments; raw listing is authoritative. D974 is reached through the sampled counters of pass11, so its invocation cadence is not automatically a uniform real-time rate.

### 22-byte record countdown

Confirmed / High, 1010:1D4E..1DFF. Initial count is signed WORD1040:0000, records start1040:9DD6, stride0016h. Loop end reloads the count through selector DS:2220 rather than retaining the initial selector/count. A runtime callback or other mutation could therefore affect traversal; the single-record model does not simulate that possibility.

| Field | Supported meaning |
|---|---|
| +00 | first far object pointer; byte+6 used for type exclusion, byte+5 receives OR1 |
| +04 | second far object pointer; byte+5 receives OR1 |
| +08 | far cell pointer; byte+1 tested; full pointer compared to DWORD DS:4C10 |
| +0C | WORD state; only zero enters countdown branch |
| +0E | WORD countdown, decremented modulo65536 |
| +14 | byte tested for optional call E3B0(WORD26h,DWORD0), then cleared on transition |

First-object byte+6 values3Bh and3Ch skip the update. Otherwise state0 decrements countdown; only a resulting zero continues. If cell.byte1!=0 or cell pointer equals player-cell pointer DS:4C10, set countdown4. Otherwise optionally call E3B0 if record.byte14 was nonzero, clear byte14, write state3, then OR1 into byte+5 of both pointed objects. These pointer reads and writes occur in this order; aliases and callee mutation can change outcomes outside the isolated model.

Old countdown0 becomesFFFF with no transition. Old1 reaches the transition/blocked-cell branch. Door-like behavior is Inferred / Medium; exact record/asset identity and sound26h identity remain Unknown. State3 is an observed value, not assigned a guessed animation name.

### Two byte-sized timed flags

Confirmed / High, 1010:BB26..BBC9. Routine snapshots DS:4C42/43, then returns without these updates when byte4BE4!=0. With freeze byte zero:

1. If4C2C!=0 and low tick byte &0Fh==0, DEC byte4C43.
2. If4C2D!=0 and low tick byte &07h==0, DEC byte4C42.
3. If4C2C remains active and4C43 is now0, clear both and call B1A4(WORD3,DWORD0).
4. Then apply the same expiry action to4C2D/4C42, allowing a second B1A4 call.
5. Compare current4C42 with its entry snapshot; if different call A3B6(WORD13h). Then compare4C43 and call A3B6(WORD14h) if different.

These are actual rereads, so B1A4/A3B6 mutation may influence subsequent branches. The independent per-channel models explicitly assume called routines do not mutate these states. A frozen call performs no expiry even for active count0. Active count0 on a decrement boundary wraps toFF and stays active; off-boundary, it is immediately cleared. Effect names, physical durations and gameplay activation sources remain unassigned.

## Validation

- Original EXE hash and12 critical raw instruction spans checked, including exclusions, modulo decrements, live loop-count selector reload and exact D974 argument pushes.
- 2097152 record fixtures: all65536 countdowns, four type values58..61, states0/3 and four occupancy/player/mark combinations. Compared a direct branch model with a separately expressed transition predicate.
- 524288 byte-channel fixtures: all256 counter values, all256 low-tick values, active0/1, frozen0/1 and masks7/15. Compared branch and arithmetic specifications.
- Exact D974 call ordering extracted from Ghidra listing and checked. Tests do not execute any original machine instruction or API.
- Ghidra annotated three existing functions, full native export completed, corrected argument comments were then exported for the three targets and saved. Inventory remains1551 internal entries, all1551 native decompilations completed;310 EXTERNAL-block entries separately tracked.

Coverage remains160005 instruction bytes,8282 defined data bytes,1401 undefined bytes. No new entry, padding classification or binary patch. Successful decompilation does not establish correct signatures or semantic completeness.

## Unknowns and next test

Record pointer validity/aliasing, callback mutations and dynamic loop selector/count need runtime traces. Break at1D88,1DB6 and1DC6 with record countdown0/1 and blocked/unblocked cells; capture record fields and both pointed objects before/after sound dispatch. Break atBB4C/BB5D,BB7C/BB9F andBBB1/BBC3 with active count0/1 on and off modulus boundaries; record mutations caused by callees. Trace activation writes to4C2C/4C2D and associated assets before naming the timed effects. These tests discriminate the isolated model from the complete game scheduler.

## Implementation-ready findings and confidence

Preserve unsigned storage widths, decrement-before-zero testing, two independent expiry calls, exact UI selector arguments, live count rereads and ordered far-pointer writes. High confidence for bounded local operations; Medium for record role, unresolved for asset identity and complete behavioral/timing parity. Runtime tests performed:0.
