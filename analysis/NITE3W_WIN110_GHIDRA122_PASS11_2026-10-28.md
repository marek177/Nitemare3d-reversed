# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 11

## Finding

Recovered the clock selection, resolution lifecycle, absolute-deadline busy wait, two sampled counters and their immediate dispatch gates. The counters increment once per observed quantization change, not by elapsed quantum count. Identified wrap-sensitive waiting and an uninitialized local argument in timer teardown. These are bounded static findings, not measured runtime failures or complete scheduler parity.

Input: `nite3w - 110.exe`, 230400 bytes, SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra 12.2 PUBLIC 20261016, JDK25.0.2.

## Evidence

| Status | Finding | Source | Confidence |
|---|---|---|---|
| Confirmed | DS:46B2 selects timeGetTime when nonzero, otherwise GetTickCount; DX:AX is both returned and stored DS:0096/0098 | 1010:D6C6..D6E0 | High |
| Confirmed | Mode0 calls timeGetDevCaps with size4, sets flag iff AX=0, requests unsigned max(periodMin,10) if flag true, ignores timeBeginPeriod result | D66C..D6B2 | High |
| Confirmed | Mode1, with flag nonzero, pushes current-frame WORD BP-2 to timeEndPeriod. ENTER6 allocates locals, and this path contains no write to that word. Flag is not reset | D66C prolog, D678/679, D6B4..D6C5 | High for local dataflow |
| Unknown | Actual teardown word and runtime effect of unmatched resolution request | Requires Win16 stack/API trace | Unresolved |
| Confirmed | Delay target is clock32 + unsigned WORD duration modulo2^32; exit when unsigned subsequent clock >= target | D6E2..D709 | High |
| Confirmed | D70A computes q=((time32<<3) mod2^32)/1000 unsigned, increments DWORD DS:0228 once only when q differs from DS:022C; returns DX:AX | D70A..D748 | High |
| Confirmed | D74A sign-extends WORD DS:53F4, performs unsigned multiplication with time32, discards product high32, divides low32 by1000, increments DWORD DS:0230 once when quotient differs from DS:0234 | D74A..D78A | High |
| Confirmed | D9C6 takes one clock snapshot for both counters and uses unsigned counter>=threshold guards, at most one local dispatch per branch | D9C6..DA85 | High for local branch structure |
| Inferred | D70A is nominally eight samples per second under millisecond clock units; D74A uses a calibrated rate | Arithmetic plus D7D0 writing53F4 | Medium for operational rate; actual polling/callback timings not measured |

Five API references were checked independently in the NE imports: MMSYSTEM ordinals604/605/606/607 and USER ordinal13, with module names decoded from the original import-name table. Function names also appear in Ghidra's imported symbols. The generated void/WORD return declarations omit meaningful DX:AX values; this report follows the instructions.

## Behavior model

The eight-unit counter is a sample-change counter:

    q = ((time_u32 << 3) & FFFFFFFFh) / 1000
    if q != last_q:
        last_q = q
        counter = (counter + 1) & FFFFFFFFh
    return counter

With initial q=counter=0, input times `[0,124,125,1000,1000,1125]` yield counters `[0,0,1,2,2,3]`. The jump125 ->1000 adds one, not seven. The left shift wraps before division: q repeats after2^29 input units. This is not the same as multiplying an unbounded timestamp by8 then dividing. Counter overflow itself is also modulo32.

The scaled counter preserves sign extension and low-product truncation. A negative WORD factor becomes its sign-extended unsigned32 representation for MUL; the code does not clamp it. Real calibrated factors and exceptional/corrupt-state reachability remain unmeasured.

Busy wait reads the clock at least twice overall, even for duration0. Its local loop contains only clock reads/comparisons, no message pump or explicit yield. It compares absolute unsigned times. Example: startFFFFFFF0h, duration32 -> target00000010h; a first poll still atFFFFFFF0h already satisfies now>=target and returns immediately. This is an arithmetic fixture, not an observed in-game incident.

Timer teardown uses an unspecified current stack value, not a recovered persistent copy of the requested period. Mode0 requests max(minimum,10) and may select the multimedia clock even if timeBeginPeriod itself fails, since its result is not checked. No claim is made that resolution cleanup always fails: the stack word may happen to match, and actual API behavior must be traced.

## Immediate dispatch order

D9C6 stores the eight-unit counter to DS:3928. If unsigned counter>=DS:0238, it calls D974 only when DS:46B8==0, then sets threshold=counter+1 modulo32. Next it stores the scaled counter to DS:392C. If unsigned counter>=DS:023C, it optionally calls D974 when46B8!=0 and pre-update53DC is odd, then calls in order D8FC, D78C, BBCA, BA54, 1E00, 9E20, optionally3AB8 if46B6!=8, then9806; finally threshold=scaled counter+1. D78C itself increments53DC. This pass establishes local order, not the effects or loop counts inside those callees. D974's direct callees include the palette-flash updater from pass6, but its complete object scheduling semantics are still open.

## Validation

- Hash and exact raw arithmetic/comparison bodies checked, plus import module/ordinal fixups.
- 1,376,256 split-WORD unsigned deadline comparisons checked against independent u32 comparisons.
- All65536 minimum-period words checked against max(minimum,10); all65536 capability return words checked for flag iff zero.
- All65536 signed factor words at nine selected timestamps:589824 arithmetic comparisons.
- 432 selected immediate dispatch guard fixtures. These check predicates/order construction, not called function behavior or arbitrary callee mutation.
- Ghidra annotated six existing functions, full native export completed and project saved. No new code/data classification or executable bytes changed.

Function inventory remains1551 internal entries, all1551 decompilations completed;310 EXTERNAL-block entries separate. Coverage remains160005 instruction bytes,8282 data bytes and1401 undefined bytes. Neither decompilation success nor these pure-model checks certify runtime parity.

## API sources and scope

The original Microsoft Windows3.1 SDK Multimedia Programmer's Reference (April1992), printed section3-77, documents the period argument and matching begin/end requests: https://bitsavers.trailing-edge.com/pdf/microsoft/windows_3.1/Microsoft_Windows_3.1_SDK_1992/PC30212-0492_Multimedia_Programmers_Reference_199204.pdf . Search-retrieved text was available; full PDF retrieval failed due size, so no claim of full manual inspection is made. Microsoft's timeGetTime reference documents millisecond units and DWORD rollover: https://learn.microsoft.com/en-us/windows/win32/api/timeapi/nf-timeapi-timegettime . That current reference corroborates API units, not the original Win16 runtime's accuracy. No Windows10/11 resolution behavior is projected onto this binary.

## Unknowns and next test

Run Win16 with breakpoints at D6AA and D6BB: record requested begin period, actual BP-2 teardown word, flag and both API results. Capture D9C6 input time, counters/last-quotients and thresholds around a deliberate pause to distinguish sample-change behavior from catch-up scheduling. Inject near-wrap clock samples to verify wait return sequence. Capture actual calibrated53F4 and calls inside D974 before claiming tick-exact object scheduling. Runtime stack data, timer resolution, full scheduler, rendering and whole-game1:1 parity remain unverified.

## Confidence

High for bounded static arithmetic, branch order and local uninitialized read; Medium for timing roles and operational rate. No new runtime evidence.
