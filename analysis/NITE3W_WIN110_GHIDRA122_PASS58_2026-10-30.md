# Win110 pass58 — initialized descriptor mode and direct-reference audit

## Finding
Confirmed, High: raw EXE data initializes0A94=0,0870=20,0872=20,0874=40. With that initialized data state, all65536 possible handle WORD values through original5902 validation accept only0..19, and reject20..FFFF withAX0900/CF1 at3D41. No extended remapping occurs. This is not proof that startup or indirect code never changes the mode.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Initial mode0A94 zero and limits20/20/40|Original NE10 filebase2C040 plus offsets|High|
|Confirmed|Captured direct instruction references to0A94/0870/0874 are all READ|Preserved native Ghidra12.2 reference export|High|
|Confirmed|Original validation accepts20 handles and rejects65516|65536 controlled prefix executions|High|
|Unknown|Indirect setters,bulk copies,startup mutation and actual runtime mode|Not executed/audited completely|Low|

## Behavior model
Original5902 stores direct threshold0870,reads0A94,and with its initialized zero value skips alternate upper limit0874 and the remapping of handles0..2. BX is compared unsigned against0870=20. BX0..19 reach5939 before descriptor processing; higher values loadAX0900,setCF,and jump3D41. The alternate initialized upper limit40 therefore does not by itself enable40 direct writable handles. Pass57's fatal extended-mode routes used explicitly injected global configurations; they were controlled possibilities, not observations of a real startup mode.

The captured direct-reference audit found no direct setter among instruction references to these exact three addresses. That scoped absence does not cover arbitrary indirect destinations,overlapping wider stores,or loader/startup bulk writes. No setter is invented, and no whole-program once-only or permanently-disabled claim is made.

## Verification
Original EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. NE2 original bytes loaded unchanged;NE10 initialized bytes loaded unchanged. Synthetic frame atD000 supplies each handleWORD and length1. TestCS2000,DS=SS1048. Original code5902 executes until5939 or3D41; no OS/API/helper service executes or is stubbed. BX retains supplied handle in every fixture. Rejected fixtures assertAX0900/CF1 at the boundary. Boundary hooks stop before descriptor access or error translation. This is original-instruction microexecution at initialized data, not execution of full Windows startup. Existing native exports supply direct-reference evidence; no fresh Ghidra run or database modification claimed.

## Implementation-ready findings
Initialize the mode/limits from verified EXE data and use unsigned direct validation0..19 under that state. Keep alternate40 limit conditional on0A94, not universally active. Preserve actual configuration provenance in future parity tests; synthetic mode1 tests must not be presented as real game initialization.

## Unknowns and next test
Trace CRT initialization around mode-related globals and audit indirect/bulk writes. Then inspect low-stack path and real Windows DOS3CALL behavior. Full game1:1 parity and semantic coverage remain open. Confidence High for initialized values,exact direct-reference audit,and exhaustive handle prefix test; Unknown for whole-lifetime mode reachability.
