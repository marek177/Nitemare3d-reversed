# Win110 pass84 — maintenance counter gate

## Finding
Confirmed / High:2840 treats0824(low)/0826(high) as a32-bit unsigned countdown. It decrements only nonzero values and enters maintenance only on1→0. A guarded3D72 region increments zero to1 and immediately calls2840, triggering that transition.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Zero bypasses decrement and maintenance |2845–284C→2861 | High |
| Confirmed | Nonzero value decremented with SUB/SBB |284E–2853 | High |
| Confirmed | Only resulting zero enters maintenance at2864 |2858–285F | High |
| Confirmed |3D72 branch requires BP+8=1,BP+0A=0,counter0 |3E5B–3E6E | High |
| Confirmed | Branch increments and immediately calls2840 |3E70–3E7A | High |

The numerical words used as guards are established; their Windows-message semantic names are not inferred here.0824/0826 is a maintenance gate/countdown in this captured path, not evidence of elapsed-time measurement or a gameplay tick scheduler.

## Behavior model
2840 prefix: `if(counter!=0) { --counter; if(counter==0) enterMaintenance; } bypass;`.
3D72 local branch: `if(argWord8==1 && argWordA==0 && counter==0) { ++counter; call2840(); }`.

The second path leaves counter0 after the called prefix and reaches maintenance once. Initial counter0 sent directly to2840 does not itself trigger maintenance. Borrow across00010000→0000FFFF works as32-bit arithmetic. The3D72 guard prevents its increment from overflowing a nonzero counter.

## Verification
131,168 original-code cases passed: all65,536 low words with high0 and again high1 through2840 prefix (131,072 cases), plus96 guarded-path cases crossing eight counters including80000000/FFFFFFFF, four guard words and three secondary words. Checks establish resulting counter and exact maintenance/bypass boundary.

No APIs or function bodies are stubbed. Original2840 prefix and3D72 region3E5B execute; tests stop at2864 before maintenance body,291B after bypass, or3E7F before caller continuation. One internal CALLF selector3E7D normalizes to testCS2000. DS1048 and SS4000 are distinct; established caller frame and arguments are synthetic. Prior3D72 control flow, callbacks, return epilogues, full maintenance and real Windows processing are outside this pass.

Run `python3 pass84/verify_idle_counter.py` with Unicorn2.1.4. Script filename uses provisional idle terminology; the confirmed result is the numeric maintenance gate, not a proven Windows idle event. The executable SHA256 is12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Preserved Ghidra12.2 export and original EXE; no fresh database mutation.

## Implementation-ready findings
Do not run maintenance for every zero observation. Distinguish explicit0→1→0 triggering from an already-zero direct call. Use32-bit decrement with borrow and no underflow at zero. Reserve rebuild remains a later condition within maintenance, as separately tested in pass83.

## Unknowns and next test
Resolve the3D72 caller argument meanings and preceding branch reachability. Trace callbacks and cleanup order after2864 to define maintenance effects. Real event timing remains Unknown. Confidence High for isolated counter/guard behavior.
