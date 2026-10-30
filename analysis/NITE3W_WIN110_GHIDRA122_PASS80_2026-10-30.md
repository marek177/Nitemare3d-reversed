# Win110 pass80 — reserve release boundaries

## Finding
Confirmed / High:12D2 compares the returned reserve size against wrap16(request+4), strictly unsigned. If capacity is greater, it calls5BA8 with reserve and wrap16(capacity-request-4); otherwise it calls5B0C and clears application+7A. Both paths returnAX1 regardless of helper return value.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Missing application or reserve reaches exception call4564 |12D8–12E8,132E; boundary tests | High |
| Confirmed | Threshold wraps at16 bits and equality chooses free |12F8 LEA,12FB CMP,12FD JA | High |
| Confirmed | Resize arguments are reserve and capacity-request-4 |1315–1321 | High |
| Confirmed | Resize result ignored; pointer+7A retained |1326–1329 | High |
| Confirmed | Free result ignored; pointer+7A cleared |1305–1313 | High |

## Behavior model
`if(!app || !app.reserve) call4564; else { cap=size(app.reserve); if(cap > word(request+4)) resize(app.reserve,word(cap-request-4)); else { free(app.reserve); app.reserve=0; } return1; }`

The exception call is not executed here. Its following code would return0 if4564 returned normally; real exception transfer is a separate question.

At capacity512, request507 shrinks to1;508 and509 choose free. RequestsFFFC,FFFD,FFFE,FFFF wrap the threshold to0,1,2,3 and thus choose resize at capacity512, producing sizes512,511,510,509 respectively. These are original arithmetic outcomes under synthetic inputs, not evidence that real allocation pressure produces these requests or capacities.

## Verification
65,638 cases passed: all65,536 request words with capacity512 and helper return0;100 cases crossing ten boundary requests, five capacities and two helper results0/FFFF; two missing-application/reserve boundary cases. Checks cover exact size/free/resize argument sequence, resulting+7A, returnedAX1, caller-cleanedSPD004 and preservedBP/SI/DI.

Original12D2 instructions execute with no code patches. Calls5B94/5B0C/5BA8 are intercepted before CALLF, returning declared synthetic capacity/results and leaving cdecl arguments for original cleanup. Missing-state cases stop at132E beforeCALL4564. DS1048 and SS4000 are distinct; CS3000 maps NE2. No actual size query, reallocation, free, Windows heap or exception executes. The interpretation of5BA8 as resize follows prior/static context; this pass verifies the caller's exact arguments and ignored result, not that helper's body or heap effect.

Non-CALLF native bytes are checked against raw EXE. SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Reproduce `python3 pass80/verify_reserve_release.py` with Unicorn2.1.4. Uses preserved Ghidra12.2 export; no fresh database update.

## Implementation-ready findings
Use WORD wrapping and unsigned strict comparison; do not clamp request+4 or change equality into resize. Preserve reserve pointer on resize path even if the helper reports0. Clear it after the free call regardless of its result. Returning1 requests an allocator retry; it does not prove memory was released successfully.

## Unknowns and next test
Execute5BA8 to identify its exact API flags, result contract and failure behavior. Establish runtime request ranges before labeling arithmetic wrap a reachable defect. Confidence High for isolated handler behavior; real heap effects and reachability remain Unknown.
