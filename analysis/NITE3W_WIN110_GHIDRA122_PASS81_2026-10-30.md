# Win110 pass81 — LocalReAlloc wrapper and reserve caller

## Finding
Confirmed / High:5BA8 calls LOCALREALLOC(handle,sizeOrOne,0060), returns its saved AX after UNLOCKSEGMENT, and does not retry or invoke the allocation-failure handler. Integrated12D2 retains the original reserve pointer and returns1 regardless of that result.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | LOCKSEGMENT(FFFF) precedes allocation |5BB0–5BB4 | High |
| Confirmed | Size0 forwarded as1; caller size word not modified |5BBC–5BCB | High |
| Confirmed | Flags0060, normalized size and handle passed to LOCALREALLOC |5BB9–5BD0 | High |
| Confirmed | Return AX preserved across UNLOCKSEGMENT(FFFF) |5BD5–5BE1 | High |
| Confirmed |12D2 discards returned handle/result and keeps application+7A |1321–1329,20 integrated cases | High |

The flags are reported numerically. No claim about real Windows permission to move this particular block is needed to establish caller behavior. An alternate API return in the tests is synthetic and does not prove Windows actually moves the reserve.

## Behavior model
`lock(FFFF); result=LocalReAlloc(handle,size ? size : 1,0060); unlock(FFFF); return result;`

This differs from5AB0:5BA8 has no handler/retry loop. Its zero-size normalization occurs only in a register and does not rewrite the caller argument slot as5AB0 does. RETF leaves both caller arguments present.

For reserve shrink,12D2 calls this actual wrapper with reserve and wrap16(capacity-request-4), then returns1 without checking or adopting the wrapper result. This pass removes the5BA8 stub used in pass80 and moves the declared simulation boundary down to the Windows imports.

## Verification
131,092 cases passed: all65,536 size words with API results0/FFFF through original5BA8; plus20 integrated shrink cases through original12D2→5BA8, crossing requests0,1,507,FFFC,FFFF at synthetic capacity512 with API results0,7400,7500,FFFF. Checks include exact call order, all API argument words, AX, finalSP, BP/DS, and retained reserve pointer in integrated cases. EntrySPD000 returnsD004 with caller arguments still present. UNLOCKSEGMENT returnsDEAD to verify saved result restoration.

DS1048, SS4000, CS3000. One internal selector at1324 normalizes to3000 for the integrated call. Windows LOCKSEGMENT/LOCALREALLOC/UNLOCKSEGMENT call sites are intercepted, consume their own arguments and return synthetic results. The12D2 size-query5B94 call is also intercepted, returns512, and leaves its argument for original POP BX. No heap state, copying, Windows imports, or actual reserve relocation executes. Native non-CALLF bytes of5BA8 are checked against original EXE and preserved export.

Run `python3 pass81/verify_local_realloc.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Preserved Ghidra12.2 export; no fresh database mutation.

## Implementation-ready findings
Preserve flags0060, zero-size-to1 forwarding, caller-cleaned argument ABI, API return preservation and lack of retry. Model12D2's retained pointer separately from the result of reallocation. Do not equate handler return1 with a proven successful heap change.

## Unknowns and next test
Determine the reserve's actual LOCALALLOC flags/handle semantics in a real Win16 heap and whether alternate reallocation handles are possible on this path. Follow the next allocator retry after a failed resize to establish repeated-handler behavior. Confidence High for wrapper/caller control flow; actual heap movement and runtime reachability Unknown.
