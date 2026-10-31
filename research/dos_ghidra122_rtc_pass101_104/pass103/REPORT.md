# Pass103 — animation state1 unsigned deadline/update region

## Finding
Confirmed, High for the isolated native region:5376 cases pass across six distinct EXEs. The original state1 animation block advances at most one frame per invocation, reschedules from current cached time and compares absolute deadlines as unsigned32. This is a region-level test, not complete scheduler/function/render parity.

## Evidence
locations.json preserves original hashes, containing function, exact region entry/stop and native bytes. Ghidra12.2 freshly decompiles the containing eight-slot update function for all6 builds. For supplied1.8/1.9 the containing function is17ed:0356, region17ed:0388→03bc, cache376d:081e. Full cases are in deadline_tests.json.

## Behavior model
With record ES:SI, frame at+3, deadline u32 at+8, and descriptor pointerCX: if deadline>now unsigned, leave these fields unchanged. Otherwise increment frame as u8; compare zero-extended result with descriptor word0 using signed16 comparison; reset frame0 when result>=signed count. Reschedule deadline=wrap32(now+descriptor.word2). Delay is an unsigned16 add with carry. Equality is due; missed intervals do not trigger catch-up in this block. Subsequent position/render helper calls lie outside the tested region.

5376 =6 EXEs ×8(now,deadline) pairs ×4 frames(0,1,254,255) ×7 descriptor counts(0,1,2,255,256,8000h,FFFFh) ×4 delays(0,1,10,FFFFh). Artificial count edge values do not imply such assets occur in the game. Entry registers, record and descriptor are fixtures; native instructions run until the original branch join, with no function mock and no IRQ interleaving. Assertions cover exact frame/deadline effects and allowed write locations.

## Boundary consequences
Unsigned absolute comparison is not modular elapsed-time comparison: deadlineFFFFFFFEh with now2 is not due. With nowFFFFFFFEh and delay10, a due block stores deadline8; before counter wrap, the same simple unsigned comparison can treat8 as already due. These are demonstrated numeric consequences, not a measured whole-game freeze or glitch. Rescheduling uses now, not prior deadline, so behavior differs from interval accumulation after a stall.

## Implementation-ready findings
For exact region compatibility: due=(u32 deadline<=u32 now); frame=wrap8(frame+1); if signed16(count)<=frame then frame0; deadline=wrap32(now+u16(delay)). Preserve single-step behavior. Asset validity and whole function state1/state2 dispatch must be separately established before calling this a complete object scheduler.

## Unknowns and next test
State2 control flow, actual descriptor contents/slot classification, helper side effects and a full frame/gameplay trace remain unresolved here. The unprotected mixed-width time reads can also be interrupted; pass104 directly tests the counter wrapper, not this whole region.

## Confidence
High for the executed region and explicit fixtures; incomplete for whole-function reachability, hardware scheduling and observable rendering.
