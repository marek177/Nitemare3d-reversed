# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 17

## Finding

Recovered the eight-slot projectile update, unit-step movement and impact transition. Movement is independent of animation deadlines; animation advances at most once per call. Impact uses the current selected weapon and inherits the flight deadline. Identified a preserved spawn WORD as projection depth written only on successful render-queue insertion. These are static findings, not complete damage/render/runtime parity.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016,JDK25.0.2.

## Movement and impact transition

Confirmed / High,9D30..9E1E. Reads current coordinates at slot+1E/+20 and signed WORD DS:53FA as movement iteration bound. For each positive-bound iteration: increment major coordinate by its stored direction; update signed error and, when error>=0, increment secondary coordinate; derive the map cell with the same signed-x/two-byte-cell arithmetic as pass14; call9B64(cellfar,x,y). Collision result is tested through AL only.

Nonzero result breaks immediately after storing state+0C=2, frame+11=0, A956 result into type+12 and OR10h into flags+13. The final coordinates include the collision point. The routine does not locally reset deadline DWORD+16. Error was updated before the collision query. Collision logic9B64 and its callbacks are not executed by this pass's models.

Even when step bound is zero or signed negative, the routine still increments byte+28 once and commits coordinates. The clamp is signed: increment modulo256, then if signed result>20 set20. It is not an unconditional unsigned min(value+1,20);127 becomes128, which is signed negative and is not clamped. For valid spawn value5, repeated normal updates rise to20 and stay there.

A956 (Confirmed / High) selects from local bytes[1,3,1,1] indexed by current weapon byte4C23, adds DS:8397 modulo256. It does not read a saved launch weapon from the projectile. Invalid weapon indices remain outside the valid lookup domain. This identifies impact graphic-type selection, not damage amount.

## Eight-slot update states

Confirmed / High,9E20..9F0E. Iterates all eight42-byte records in address order. Computes type descriptor DS:4744+type*8 from entry type. Relevant descriptor fields are signed WORD frame count+0 and unsigned WORD period+2.

| Entry state byte+0C | Behavior |
|---|---|
| 1 | Flight: if unsigned deadline<=clock, increment frame BYTE, reset0 when frame>=signed count, set deadline=clock+period modulo32. Always call9D30 regardless of deadline. Afterwards callCC7C only if either signed absolute coordinate difference from player exceeds20. |
| 2 | Impact: if deadline<=clock, increment frame once and reschedule from current clock. Then, even if not due, frame>=signed count clears state0; otherwise callCC7C. No9D30 movement call. |
| Other | No local update/draw call for this slot. |

Frame arithmetic is byte-sized. No catch-up loop advances multiple frames after a pause. Deadline comparison is absolute unsigned32, carrying the same wrap concerns as other clock users. Transition to state2 inside9D30 does not restart state dispatch in the same call: the flight branch still performs its post-movement distance/queue decision, and the next slot-update call enters the impact branch.

Signed absolute differences use16-bit subtraction/absolute arithmetic. The8000h input remains8000h, a signed negative value, and therefore does not satisfy >20. Model fixtures record this invalid/extreme-state arithmetic without claiming ordinary-map reachability.

## Preserved depth field

Confirmed / High,CC7C, write at1010:CE5E: successful insertion into an18-byte render queue record stores depth `(transformed local_a arithmetic_shift_right4)` at embedded object+18h. Embedded object starts projectile slot+0Eh, so this is slot+26h. Pass16 established that spawn does not directly overwrite this WORD. Early flag, projection and visibility exits do not perform this write.

This proves a depth field can retain its prior value until insertion succeeds. It does not prove a visible stale-depth artifact or a damage dependency for this projectile. Other object classes use the shared object layout; distinguish the owner of any depth read. Initialization elsewhere, aliases and callback mutation still require inspection. Remaining untouched spawn bytes are not automatically uninitialized memory.

## Validation

- Hash and six critical raw spans checked, including transition state, signed byte clamp, unsigned deadline branches and depth write.
-16384 animation fixtures: states0/1/2/3, all256 frames, eight signed frame-count values, due/not-due. Invalid counts are arithmetic fixtures, not asserted asset values.
-256 byte increment/clamp fixtures;65536 signed absolute-distance fixtures.
-12960 unit-step fixtures across360 exact trig headings, selected step counts and scripted first-collision positions. Compared positions with a separate integer stepping formula; collision response is a stub, not original9B64 execution.
-1024 current-weapon/type-base fixtures, preserving byte wrap.
- Ghidra annotated four existing functions, full native export and project save completed.1551 internal entries remain; all1551 decompilations completed.310 EXTERNAL-block entries separate.

Coverage remains160005 instruction bytes,8282 data bytes,1401 undefined bytes. No binary patch, new entry or padding typing. Pure models do not certify runtime parity or correct decompiler signatures.

## Unknowns and next test

Trace one projectile through9D30 collision and9E20's same-call queue decision; capture state/frame/type/deadline and current weapon. Switch weapon during flight and verify which impact type is selected. Reuse a slot with marked+26h, exercise CC7C visibility rejection and successful insertion, then trace actual consumers before claiming stale-depth consequences. Capture real frame-count/period descriptors and compare sparse/dense update schedules. Collision acceptance, exact damage, sprite pixels and complete projectile parity remain unresolved.

## Confidence

High for local update order, width/sign behavior, deadline inheritance and depth write location; runtime effects and full projectile/render/damage parity remain open. Runtime tests:0.
