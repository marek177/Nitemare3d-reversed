# Nitemare 3D Win16 1.10 — Ghidra12.2 pass19

## Finding

Verified the damage-to-health boundary through original caller instructions, then executed its full lethal branch with controlled helper stubs and the original reward function. Equality is lethal, AH is discarded, surviving positive damage subtracts health and writes reaction counter8. Reward type15 is signed-1000 and score arithmetic wraps modulo32 without a floor. Full helper effects and in-game reachability remain outside these tests.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra12.2 PUBLIC20261016,JDK25.0.2; Unicorn2.1.4 isolated16-bit original-code execution.

## Health boundary

Confirmed / High,80F8..81F8. Calls9FA2, cleans arguments, XORs AH,AH. Damage is therefore unsigned AL regardless of returned high byte. Compares health byte at actor+10h against this0..255 damage:

- health<=damage: writes health0 and enters lethal branch, including controlled health0/damage0.
- health>damage and damage0: takes zero-damage exit, leaving health/reaction counter locally unchanged.
- health>damage>0: if status byte+0Bh==7, callsB862 first; then subtracts damage from the current health byte and writes byte+12h=8. It next reads reaction mode+0Ah. Mode4 exits after those writes, not before them. Later reaction branches remain unexecuted in this pass.

B862 is a stub in the tests. In the real code it runs before subtraction and may alter state; the tests do not silently assume its implementation has been recovered.

196608 original-prefix executions covered all256 health values × all256 low damage bytes × high damage bytes00/12/FF. Checked branch choice, health and reaction byte.30 additional selected status7/non7 fixtures checked B862 occurrence. Prefix stops occur after the relevant writes or at zero exit; these are not full nonlethal reaction executions.

## Lethal branch order and direct writes

Confirmed / High,8127..81CB:

1. Set health0.
2. B94E(actorfar,objectfar) returns an index.
3. If WORD4C26!=1, callB6A0(actorfar,objectfar).
4. Read object.byte1Ah as signed; positive -> DWORD flags00090012h, otherwise00090000h.
5. Select a WORD through object.type-byte+4 descriptor pointerDS:4748+type*8, offset4Ah+2*index. Pass this value, both far pointers and flags to762C.
6. Call9F10(actorfar,objectfar), CWD sign-extends its AX, then ADD/ADC into DWORD scoreDS:4C16/18 modulo32.
7. CallA3B6(WORD4).
8. Reread current actor.byte0Dh, follow current object far cell pointer+0Ch, write cell.byte1 with that byte. Return AL containing it; AH is not a stable boolean result.

Record/pointer reads after helper calls are live. The controlled helper stubs do not mutate them; actual helper behavior can therefore change the final values. The test does not certify drops, death animation selection, UI or map logic inside helpers.

200 complete lethal executions covered selected score/reward boundaries, modes1/2 and signed height values0,1,127,128,255. Checked exact helper order,762C's14 argument bytes, UI selector4, health0, signed score update, final cell payload, AL and cdecl-far return stack.

## Original reward function

Confirmed / High,9F10..9FA0. The controlled test switches the reward stub to original code, invalidates its emulator translation cache, then executes full lethal callers for all256 type values, four score boundaries and two modes (2048 cases). Other helpers remain stubs, so object type remains controlled during these fixtures. Real helpers may alter it before the reward call; no entry-type invariance is assumed.

| Type bytes | Signed reward |
|---|---:|
| 08,1A | 25 |
| 09 | 75 |
| 0A,20 | 50 |
| 0B,0F,10,17,1B,1C | 100 |
| 0C,1D,1E | 250 |
| 0D,12,13 | 150 |
| 0E,14,18,1F | 200 |
| 15 | -1000 (AX=FC18h) |
| 16 | 1000 |
| Other | 0 |

Score0 plus type15 reward producesFFFFFC18h, not0. No saturating floor or unsigned16 addition is performed by the caller. This is controlled original-instruction behavior, not an observed normal-game event. Original enemy/asset names are not assigned from type numbers.

## Reproduction and limits

`emulate_pass19_health.py` builds caller code from original EXE bytes, applies its internal NE selector relocations and checks179 listed caller instructions against Ghidra bytes. Controlled real-mode segmented memory contains separate actor, object, descriptor, cell and stack. Calls9FA2/B94E/B6A0/762C/A3B6/B862 are explicit RETF stubs;9F10 is stubbed for boundary cases and restored to original for the final2048 cases. All assertions completed without mismatch.

The total198886 original-code cases comprise196608 prefixes,30 status fixtures,200 complete stub-reward lethal branches and2048 complete original-reward lethal branches. A prefix case is not a full function execution; labels and counts preserve that distinction. Damage computation itself is stubbed here and was separately tested in pass18. No full Win16 OS, frame, RNG stream, kill/drop helpers or nonlethal post81F8 reaction execution is included.

Ghidra annotated two existing functions, completed full native export and saved project.1551 internal entries remain, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked. Coverage remains160005 instruction bytes,8282 data bytes,1401 undefined bytes. No new entry, binary patch or padding classification.

## Unknowns and next test

Execute real B94E/B6A0/762C/UI helpers and record changed actor/object/cell fields around each call. Identify type15 assets before giving the penalty a gameplay label. Verify actual score display/load behavior for wrapped values, and execute the remaining nonlethal reaction branches. Couple pass18's original damage code to the real caller/callees before claiming end-to-end damage parity. Whole-game runtime tests remain0.

## Confidence

High for tested health boundary, direct lethal-call arguments/order, reward table and signed score arithmetic under documented stubs. Full death/reaction and runtime parity remain open.
