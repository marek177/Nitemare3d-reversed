# Win110 pass79 — reserve rebuild with suppressed allocation handler

## Finding
Confirmed / High:2840 temporarily clears the allocation handler while rebuilding application+7A. It first requests the desired size+78 and, on failure, retries the previous size only if nonzero. Every tested normally returning branch restores the exact old far handler, including when both allocations fail.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Handler cleared, oldAX/DX saved as two local words |28DA–28E9 | High |
| Confirmed | First allocation uses application+78; result stored+7A |28EC–28F5 | High |
| Confirmed | Failed first allocation and nonzero previous size trigger fallback |28F8–2904 | High |
| Confirmed | Old full handler restored after either allocation branch |290D–2918 and24 cases | High |
| Confirmed |2970 installs1008:12D2, rather than disabling handler |29B5–29BB | High |
| Confirmed |2970 saves returnedAX/DX, then restores after object creation/map insertion |29C3–29EB | High, static only |

## Behavior model
For the tested2840 region:
`old=set_handler(0); app.reserve=allocate(app.desired); if(app.reserve==0 && previousSize!=0) app.reserve=allocate(previousSize); set_handler(old);`

Previous size is supplied through localBP-2; earlier2840 code obtains it from5B94 and frees the prior block through5B0C. Those earlier operations are outside this pass's execution scope. The role of+7A as an emergency reserve is Inferred / Medium, supported by12D2's consumption of that block.

The initial description grouping2840 and2970 as handler disabling was too broad.2970 instead selects12D2. Static12D2 calls4564 if no application or reserve pointer exists. Otherwise it measures the reserve and either shrinks it or frees it/zeros+7A, then returns1. The comparison involves16-bit requested+4 arithmetic and needs its own boundary verification before an implementation-ready reserve-release model is claimed.

## Verification
24 cases passed: old handlers0,1000:076A,FFFF:FFFF; previous sizes0,32,FFFF; first result0 or7400; and fallback results0/7500 when eligible. Each executes original2840 region28DA through2918, original601A/5FF0 and original5AB0. Checks include exact requested size sequence, zero handler at each LOCALALLOC attempt, final+7A pointer, exact restored far handler, and restored region-entrySP.

Only Windows lock/allocate/unlock call sites are intercepted. Allocation returns follow declared sequences; lock/unlock returnDEAD. Execution begins with a synthetic established2840 frame, application7000, desired512, previous sizeBP-2, DS1048 and SS4000. Internal far selectors at28E1/28F2/2907/2916 and6026 normalize to testCS3000; NE1 code mapsCS2000. Execution stops at291B before the outer routine's return. This verifies normal local control flow, not exceptional unwinding, reentrancy or full2840 startup conditions.2970 and12D2 are statically inspected only.

Run `python3 pass79/verify_reserve_rebuild.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Evidence comes from original EXE and preserved Ghidra12.2 export; no fresh database update or real Win16 process execution occurred.

## Implementation-ready findings
Keep the handler suppressed across both attempts, preserve both old pointer words, skip previous-size retry when previous size0, and restore the handler even when both attempts return0. Preserve the distinct2970 replacement-handler policy rather than treating it as another null-handler window.

## Unknowns and next test
Verify12D2 request+4 wraparound, reserve-size comparison and shrink/free arguments. Test nonlocal exceptions in2970 before claiming restoration on all exits. Confidence High for tested returning2840 region; emergency-reserve interpretation Medium and real Windows lifecycle Unknown.
