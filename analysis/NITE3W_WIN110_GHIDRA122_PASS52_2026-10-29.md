# Win110 pass52 — direct write helper partial-progress paths

## Finding
Confirmed, High in scoped microexecution:1152 original59DC cases show full-write local return versus short/error escape through5A40. A successful short write first adds its actual byte count toWORD[BP-4]; an OS error leaves that word unchanged. With the tested nonzero prior totals, both escape through the shared subtraction tail to3D41.

## Evidence
|Status|Claim|Location/test|Confidence|
|---|---|---|---|
|Confirmed|RequestCX=DI-DX; zero skips OS write|59DF..59E3; zero-length fixtures|High|
|Confirmed|Direct DOS serviceAH40 invoked once|59F3..5A05; INT21 capture|High|
|Confirmed|Success addsAX toBP-4 before checking short count|5A08..5A0F; all counts0..request|High|
|Confirmed|Full write restoresAX/BX/CX,setsDI=DX,nearRET|5A11..5A16|High|
|Confirmed|Short/error with nonzeroBP-4 escapes to5A40|5A17..5A1F; original tail executed|High|
|Unknown|Zero-total device/controlZ handling and real OS effects|Excluded branches|Low|

## Behavior model
Tests enter59DC with an existing caller frame and direct INT21 mode(CS370E bit0 clear). Handle1 is below supplied threshold20. Requested bytes areDI-DX. On full success the helper returns locally with savedAX/BX/CX and resetsDI toDX. On failure or success withAX<requested, it abandons that local return frame. IfBP-4 is nonzero, it takes5A40:AX=wrap16([BP-4]-[BP-6]),restores savedSP/SI/DI,and jumps3D41. Therefore an OS error after prior progress is not automatically the immediateAXFFFF path: the shared subtraction determines the flags delivered to3D41. Meaning ofBP-6 as inserted-byte correction is provisional; this pass verifies numeric behavior without establishing its complete caller provenance.

## Verification
1152=3 prior totals1/20/32768 ×3 second-tail operands0/1/20 ×sum(request+1 for request0/1/7/20)=32 ×4 errors0/5/6/255. Error0 means successful service; actual counts enumerate0..request. Nonzero errors are modeled asCF1 and selectedAXerror with no file effects; actual-count fixture is ignored on error. For request0 no service occurs, independent of the unused error fixture. CS2000,DS=SS1048,BPD000,entrySPC800,savedSPC000. Original EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Non-CALLF native instruction encodings in59DC..5A4D checked against rawNE2 bytes. Unexecuted DOS3CALL import bytes are neither normalized nor executed; directINT21 selected. Calls to extended-handle helper73C5 excluded. Both exits stop before3D41 or synthetic near-return targetF000. Cumulative field,OS call count,AX/CF,SP,SI/DI and local-return registers checked. This is original-instruction microexecution with one simulated OS boundary, not an actual file write or full game/Win16 runtime.

## Implementation-ready findings
Keep full-write local continuation distinct from short/error escape. Add actual bytes only onCF-clear service return. Preserve original shared-tail subtraction and its flags rather than returning the last OS error blindly. Retain unverified zero-total and device special cases asTBD. Full5902 caller frame invariants and text conversion remain unproven; synthetic subtraction underflow fixtures are not claims of reachable game errors. Overall confidence High for tested paths. Next: zero prior totals, device bit40/controlZ and full caller assembly.
