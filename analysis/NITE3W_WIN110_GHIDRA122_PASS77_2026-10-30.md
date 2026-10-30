# Win110 pass77 — local allocator retry policy

## Finding
Confirmed / High:5AB0 normalizes a zero size to1, wraps each LOCALALLOC attempt between LOCKSEGMENT/UNLOCKSEGMENT, and retries a failed attempt only when the installed handler returns nonzero. There is no retry limit in the captured loop.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Size0 changes the caller's argument word to1 |5AB8–5ABE and all-size sweep | High |
| Confirmed | LOCALALLOC receives size and flags0020 |5ACC–5AD3 and captured arguments | High |
| Confirmed | Each attempt locks and unlocks segmentFFFF |5AC3–5AC7,5ADB–5ADF | High |
| Confirmed | Successful allocation returns saved result even when unlock changes AX |5AD8,5AE4–5AE8,5B01 | High |
| Confirmed | Handler considered absent only when both far-pointer words are zero |5AEA–5AF1 | High |
| Confirmed | Handler receives normalized size; caller removes its argument |5AF3–5AFA | High |
| Confirmed | Nonzero handler AX retries; zero returns failed allocation0 |5AFD–5B01 | High |

## Behavior model
`if(size==0) size=1; do { lock(FFFF); p=LocalAlloc(0020,size); unlock(FFFF); if(p!=0) return p; if(handler==0) return0; } while(handler(size)!=0); return0;`

The caller retains the size argument after RETF. Importantly zero normalization writes into that caller argument slot. Saved allocation result is independent of lock/unlock return values. The handler tests the full16-bit AX as zero/nonzero, not just a low byte or a sign bit. A handler that continually returns nonzero while allocation fails can repeat indefinitely; this follows statically from the loop, and an infinite execution is not claimed as tested.

## Verification
131,117 cases passed:65,536 size WORDs × two outcomes (immediate allocation0 or7000), without handler; plus45 scenarios crossing sizes0,1,7FFF,8000,FFFF, three nonzero far-pointer patterns, and callback sequences stop/retry/two retries. Two pointer patterns have one zero component, verifying that the caller uses an OR of both words rather than requiring each component nonzero. Those pointer values are synthetic and never dispatched to actual callback code.

Checks include normalized API/handler arguments, exact number of lock/unlock attempts, returnAX, caller argument mutation, SPD004 after entryD000, and restored BP/DS. DS1048 and SS4000 are distinct. No code patches are needed. Native non-direct-CALLF bytes of5AB0 are cross-checked against raw EXE and preserved Ghidra12.2 listing.

All four external call sites are intercepted before CALLF: LOCKSEGMENT, LOCALALLOC, UNLOCKSEGMENT and the indirect handler. The imports consume their arguments; the handler leaves its argument for original ADD SP,2. Lock/unlock stubs returnDEAD while allocation and handler results follow declared sequences. No real Windows heap, segment locking, callback side effects or exception throwing occurs. Register-clobber behavior beyond the modeled AX is not tested.

Reproduce `python3 pass77/verify_allocator.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. No fresh Ghidra database update occurred.

## Implementation-ready findings
Preserve zero-size normalization and callback-controlled retry. Keep the saved allocation result separate from API return registers. Do not add an original retry bound or automatically throw on a failed attempt: throwing, if any, depends on the actual installed handler.

## Unknowns and next test
Trace writes to094A/094C to identify the installed allocation-failure handler and whether it retries, throws or returns. Actual Windows LOCALALLOC behavior and live heap pressure remain Unknown. Confidence High for isolated retry policy under declared API/handler models.
