# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 13

## Finding

Connected the two timed flags from pass12 to toggles, resource refills, overlay dispatch and UI writeback. A key composition result: BB26's byte underflow FF can become100 through the immediately following A3B6 selector13h/14h clamp. Pass12's FF result was explicitly an isolated model with nonmutating callees; it is not the full update's final state.

Input `nite3w - 110.exe`,230400 bytes, SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016, JDK25.0.2. No binary changes or runtime tests.

## Evidence

| Status | Finding | Location | Confidence |
|---|---|---|---|
| Confirmed | Count4C43 gates XOR1 of flag4C2C, then UI selector14h always runs; new flag0 clears overlay through B1A4 mode3 | 1010:BC6A..BC8F | High |
| Confirmed | Count4C42 gates XOR1 of flag4C2D, then UI selector13h always runs; new flag0 clears through B1A4 mode3 | 1010:BC90..BCB5 | High |
| Confirmed | Input78h reaches BC6A,79h reaches BC90 when game-state46B4==1; toolbar800E/800F share these key paths | 9806 input branch; pass10 command map chain | High for static path |
| Confirmed | A3B6 selector13h jumps directly to A787,14h to A847, clamping4C42/43 to unsigned min(value,100), writing it back | CS:A3F6 jump table; A787..A792,A847..A852 | High |
| Confirmed | UI then computes floor(count*18/100) for its display span | A795..A79F,A855..A85F | High |
| Confirmed | ABFC item case4 sets4C43=100; case5 sets4C42=100; both add250 modulo32 to4C16 and call UI0/sound30h | AC66..AC79,common carry/update/call path | High |
| Confirmed | These refill cases do not locally activate4C2C/2D | Same raw branches | High for direct writes only |
| Inferred | First flag is a map-overlay aid; second is an object-marker/radar-like aid | B1A4 cases5/6,BBCA dispatch | High for algorithmic role, original names Unknown |

## Toggle and UI composition

The toggles test count before the always-run UI update. Count0 leaves the flag unchanged, including a stale nonzero flag. Nonzero count XORs only bit0; this is not boolean normalization: flag2 becomes3, not0. Turning a normalized flag1 off calls B1A4(WORD3,DWORD0), then A3B6 with the appropriate selector. Both toggles always invoke UI even when count0.

The two switch-table targets bypass the preceding `DI!=0` fallthrough exits and enter the clamp directly. Thus the explicit selector13h/14h calls issued by BB26 can mutate the counters. Under a nonfrozen active zero counter on its modulus boundary: DEC gives255; expiry test sees nonzero; UI is called because the byte changed; its clamp writes100. Off-boundary active zero is cleared by the expiry branch. A frozen update does neither. A later render callback could still mutate state; full external effects are not assumed pure by the binary.

The composed model includes this clamp and does not assert that all rendering/sound behavior has been recovered. This pass corrects the interpretation of the intermediate value without changing the original instruction-level underflow finding.

## Overlay dispatch

Confirmed / High, 1010:BBCA..BC69. Treat4C0E as signed WORD:

- If nonnegative, decrement modulo16 and call B1A4 mode3 if new signed value is negative, otherwise mode4. In this branch,0 producesFFFF and mode3; positive values select4. Overlay flags are not considered on this path.
- If negative and both flags are zero, return.
- Map flag4C2C -> mode5.
- Object flag4C2D -> first mode3 if no map flag, then mode6 if4C42>15 or odd.
- Then mode9.
- If map flag remains set and4C43<=15, mode7.

All mode calls use DWORD0 as their additional argument in this dispatcher. Fields are reread between calls; the model's fixed-input sequence assumes no callee mutation.

B1A4 mode5 toggles a marker in a64×64 byte map, clamps crop offsets based on player coordinates, and calls41A2 with source64×64 and a62×36 destination viewport at coordinates256,162. Mode6 walks26-byte records at offset93AE, associates28-byte records at6D66 through an index, excludes record byte+0B==0A and A0C6-filtered object types, and plots accepted coordinates. This supports map/object-marker roles; exact assets and original UI labels remain unassigned. No pixel or rendered-frame comparison was performed.

Mode7's random-point iteration count, for unchanged count1..15, is floor(500/count^3):500,62,18,7,4,2,1,then0 for8..15. This positive domain has no intermediate WORD-cube overflow. Each iteration chooses a point using two RNG calls and plots a value obtained from2AAC. A direct count0 entry has a zero arithmetic divisor; whether the normal game's reachable state ever reaches that path is Unknown. This is not a report of an observed crash.

## Validation

- Original hash, exact raw toggle prefixes and clamp instruction spans checked; both UI jump-table targets verified against original WORDs.
- All256 byte values checked for clamp identity min(value,100).
- All65536 count/flag pairs considered for both channel toggles, including nonboolean flags.
- 262144 composed countdown/clamp fixtures across all byte counts/low ticks, both active states and both decrement masks. Freeze behavior remains established in pass12's separate fixtures.
- 262144 signed-dispatch countdown/flag fixtures, using count16 for both resources; lower-count overlay branches are recorded separately from disassembly and formulas, not represented as exhaustive dispatch tests.
- Ghidra annotated five functions, full native export and project save succeeded.1551 internal entries remain, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked.

Byte coverage unchanged:160005 instruction bytes,8282 data bytes,1401 undefined bytes. No new function, data typing or padding designation. Pure models do not execute the EXE or establish whole-game parity.

## Unknowns and next test

Break atBB4C/BB5D and A792/A852 with active count0 to capture255 intermediate and100 writeback, including any intervening initialization/render effects. Trace ABFC cases4/5 back to actual pickup assets before assigning original item names. Record BBCA mode sequence and B1A4's62×36 viewport buffer with each flag separately and together. Test warning counts1,7,8,15; examine count0 reachability without assuming it occurs normally. Runtime pixels, exact labels, external mutations and complete scheduler parity remain unresolved.

## Confidence

High for literal toggles, refill writes, clamp composition and local mode sequencing; Medium for human-readable map/radar naming. Runtime evidence produced:0.
