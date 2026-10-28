# Nitemare3D Win16 1.10 — Ghidra12.2 pass21

## Finding

Verified original seed-setting instructions for every16-bit seed and the fixed seed1 wrapper. Accounted all55015 bytes of the fixed save slot and identified no reserved RNG state field in that layout. Load repairs far pointers and rebases two object arrays' deadlines, but its projectile-pool repair does not locally rebase projectile deadlines. Full save/load execution and first-frame parity remain open.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016,JDK25.0.2; Unicorn2.1.4 isolated seed microexecution.

## Seed lifecycle evidence

Confirmed / High,1008:6EB0..6EC7: state DWORD DS:0A90 becomes unsigned WORD argument, high WORD DS:0A92 becomes0. All65536 seeds were executed in original code with prior stateFFFFFFFFh. State, far return SP and restored BP matched. Proxy1018:32D8 pushes1, calls6EB0, cleans2 and returns; five prior states all became1.

The captured direct call to the wrapper is1010:DAFC, in DAA0's initialization branch for WORD46B8 modes1 and3. Other mode branches do not contain that direct reset. This is not a proof that all runtime seed writes have been found: indirect calls, bulk writes and deeper caller effects remain possible. The mode names are left numeric rather than guessing demo/replay identities.

## Fixed save-slot layout

Confirmed / High for sizes and arguments in5466 and corresponding read path574C. Seek offset is slot index multiplied byD6E7h (55015). First DWORD value is alsoD6E7h and the reader checks it. All section sizes sum exactly to55015, without an unexplained trailing region. Names for opaque sections remain descriptive.

| Relative offset hex | Bytes | Section/source |
|---|---:|---|
| 0000 | 4 | fixed DWORD D6E7h |
| 0004 | 41 | caller-supplied buffer, caption-like role inferred |
| 002D | 2 | DS:7E52 episode |
| 002F | 2 | DS:7E54 level |
| 0031 | 4 | saved clock snapshot |
| 0035 | 8192 |1040:A69E map cells |
| 2035 | 94 |1048:4BE8 player-state block |
| 2093 | 28000 |1040:0006 record array |
| 8DF3 | 9800 |1040:6D66 object array |
| B43B | 2600 |1040:93AE actor records |
| BE63 | 1408 |1040:9DD6 records |
| C3E3 | 32 | collected per-record state bytes |
| C403 | 336 |1048:4C4A eight projectile records |
| C553 | 8 |1048:51A4 |
| C55B | 72 |1040:A616 twelve push records |
| C5A3 | 4096 |1028:0000 map buffer returned by B1A4 |
| D5A3 | 64 |1040:A65E |
| D5E3 | 256 |1048:8094 palette-remap bytes |
| D6E3 | 1 |1048:7E62 |
| D6E4 | 1 |1048:7E63 |
| D6E5 | 2 |1048:7E60 |

DS:0A90/0A92 is outside every explicit Data10 block. The caller-supplied41 bytes have no assigned RNG semantics; arbitrary caller-buffer aliases are not globally excluded. Thus the finding is no explicit serialized RNG field in this accounted layout, not a claim that every indirect operation or possible caller can never preserve/modify RNG.

One ABI detail explains an otherwise incomplete decompile: at5684 the caller pushes DWORD10000000h and DWORD8, callsB1A4, then cleans only6 bytes. The remaining WORD1000h serves as the following write's count. Returned DX:AX is1028:0000, as shown by B1A4's epilogue; pushesDX,AX,handle complete31E4's arguments. Treating B1A4's generated scalar0 return as the whole value loses the buffer segment and4096-byte section. Original NE selector metadata also ties DS:222C to NE segment6 (Ghidra1028), separate from Data10.

## Load repair scope

Confirmed / High for local574C body: reads raw blocks, rebuilds current player/object far cell pointers, recomputes heading-derived globals withE516, rebuilds coordinate lists and restores collected record-state words. It repairs projectile embedded-object cell pointers at slot+1Ah from saved coordinates. The raw336-byte pool includes the projection depth and absolute deadline fields from passes16/17.

After obtaining current clock, two28-byte record-array loops (bases1040:0006 and1040:6D66) repair DWORD deadline+8:

    oldDeadline < savedClock unsigned ->0
    otherwise -> oldDeadline + nowClock - savedClock modulo2^32

The projectile pointer-fixup loop only updates its far cell pointer, not deadline slot+16h. These explicit timestamp loops do not traverse the projectile pool. This establishes local asymmetry; later callers/callees may add effects. A first-frame trajectory/animation or stale-depth consequence is not certified.512 selected clock/deadline boundary fixtures checked the split-WORD addition model, not the original full loader execution.

## Validation and limits

-65536 original seed-setter executions and5 original wrapper executions passed.
-Exact slot-size accounting55015; source ranges checked for absence of a reserved Data10 RNG block.
-Original retained-stack-count instruction spans and segment6 metadata checked.
-512 pure timestamp repair fixtures; save/load I/O itself was not emulated. Error paths, partial I/O, malformed counts and pointer validity remain outside scope.
- Ghidra annotated four existing functions, completed full native export and saved project. Internal inventory1551, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked.

Coverage unchanged:160005 instruction bytes,8282 data bytes,1401 undefined bytes. No EXE patch, new entry or padding designation. Static layout recovery and seed microexecution are separate from full Win16/game runtime tests.

## Unknowns and next test

Capture actual save bytes and compare each section, including projectiles and RNG state before/after load. Trace DAFC's mode transitions and any indirect seed setters. Load with a projectile in flight and record old/saved/current clock, its unchanged local deadline, first9E20 invocation and any intervening callbacks. Verify partial-I/O handling and real caption data. Complete deterministic replay, save/load restoration and first-frame parity remain unverified.

## Confidence

High for seed instructions, fixed layout arithmetic and local repair asymmetry. Full load/RNG lifecycle and runtime consequences remain open; full-game runtime tests0.
