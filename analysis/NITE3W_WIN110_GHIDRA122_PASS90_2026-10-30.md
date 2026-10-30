# Win110 pass90 — HWND attachment and detachment contract

## Finding
Confirmed / High:132C attaches nonzero HWND by storing object+14 then writing the object pointer into a map4250 value slot. HWND0 returns false without modifying the old field.1356 requests removal of the stored nonzero HWND, clears+14 unconditionally, and returns the old HWND.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |Attach0 bypasses field/map writes and returns0 |1330–1339 | High |
| Confirmed |Nonzero HWND stored before requesting map slot |133B–1345 | High |
| Confirmed |Object pointer written through returned slot, then returns1 |134A–1353 | High |
| Confirmed |Detach nonzero invokes2A14(map4250,old HWND) |135E–136C | High |
| Confirmed |Detach clears field and returns saved HWND regardless of remove return |1371–137B | High |

Static2A14 delegates to6356. Slot creation62F4 and removal6356 internals are outside this pass.132C has no explicit check of the returned slot pointer before storing through it; an allocation/exception failure inside62F4 must be investigated separately.

## Behavior model
`attach(obj,h): if(!h) return0; obj.hwnd=h; *mapSlot(4250,h)=obj; return1;`
`detach(obj): old=obj.hwnd; if(old) remove(4250,old); obj.hwnd=0; return old;`

Attach does not explicitly remove an earlier nonzero HWND association before replacing+14. Therefore stale old mappings are possible under an invalid repeated-attach sequence unless62F4 or caller preconditions prevent it; actual reachability is Unknown. Do not claim132C enforces uniqueness. Detach itself does not destroy a Windows window.

## Verification
131,072 cases passed: each of65,536 HWND WORDs through both original wrappers. Attach begins with object+14=AAAA and output slotBBBB, checking unchanged values on zero and exact writes on nonzero. Detach checks conditional removal, ignored removalAX=DEAD, cleared field and exact returned HWND. Each run checks argument cleanup, restoredBP/SI and finalSP.

Only62F4 and2A14 call sites are stubbed beforeCALLF. The slot stub validates map/key and verifies object+14 was already updated, returning synthetic writable slot6000. Remove stub validates map/key and returnsDEAD without modifying any real map. No actual map insertion/removal, allocation, Windows HWND or destruction executes. DS1048, SS4000, CS2000; no instruction patches.

Run `python3 pass90/verify_window_attach.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Includes preserved Ghidra12.2 export, without fresh database mutation.

## Implementation-ready findings
Keep attach0 separate from detach. Preserve field-write-before-map-slot order and old-HWND return on detach. Do not equate map removal with DestroyWindow, and do not add an unobserved old-association cleanup to132C.

## Unknowns and next test
Execute62F4/6356 to recover insertion/removal, duplicate keys and ownership. Trace callers before asserting repeated-attach preconditions. Writes to preferred application+20 remain unresolved in this pass. Confidence High for wrapper contract; real map/Windows lifetime Unknown.
