# Win16 1.10 — Ghidra12.2 pass25: config read controller

## Finding
Confirmed High:1010:52AE initializes20 config bytes, then opens config.sav and proceeds only for signed handle>0. Read and close return values are discarded.2268 original-controller microexecutions verified this with controlled helper returns. These are not actual file-system or full-game runtime tests.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|Defaults are300100004001c80032323c460001010000000000|52AF..52EC;verification JSON|High|
|Confirmed|Handle0 and signed-negative handles skip size/read/close, retain defaults, still call5208|5308..530A,5340|High|
|Confirmed|Positive handles require sizeDXAX=00000014; other sizes call3118|5315..5326|High|
|Confirmed|If diagnostic returns, execution continues into read20 bytes, then close|5329..533D|High|
|Confirmed|ReaderAX and closeAX do not affect subsequent controller branches|5334..534D|High|
|Confirmed|Controlled short-prefix writes preserve default suffix, with no rollback|Original controller2268 fixtures|High|
|Unknown|Whether actualCRT can produce every supplied prefix/AX combination; actual diagnostic termination|Helpers stubbed here|Low|

## Behavior model
Set defaults. Build path5260, open54D4. If signed handle<=0, call5208 with default firstWORD. Otherwise query length6664, compare both16-bit halves to20; call diagnostic3118 on mismatch. If execution continues, request read5798(handle,4BD4,20), close53B0(handle), then call5208(currentWORD4BD4). The final apply helper may alter downstream state and is excluded here.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.51 instruction encodings verified against native Ghidra listing before testCS relocation.2268 cases =6 handles[0,1,2,7FFF,8000,FFFF] ×6 lengths[0,19,20,21,10014,FFFFFFFF] ×21 injected prefixes0..20 ×3 readerAX[0,20,FFFF]. Seven helpers stubbed: path,open,size,diagnostic,read,close,apply. Hooks validate arguments and exact call order. All20 config bytes, finalIP and stack checked. Close always returnsFFFF to prove local independence. Diagnostic deliberately returns. Reader writes controlled prefix; no claim all such fixtures are realisticCRT outputs.

## Implementation-ready findings
Preserve initialization before file access and local lack of rollback. A strict modern loader that rejects all short reads before applying any bytes would differ from this controller if the original read mutates a prefix and returns. Full parity requires executing actual5798 and fatal/error paths first; do not introduce hypothetical behavior as established fact.

## Unknowns and next test
Execute binary-mode5798 with controlledDOS3CALL/INT21 service to determine actual short-read and error writes. Trace3118 termination policy and5208 side effects. Whole LOAD first frame and Win16 runtime comparison remain open. No new byte classification; previously measured1401 undefined executable bytes remain unresolved.

## Confidence
High for controller branches, defaults and ignored helper returns; limited for real I/O because helpers are replaced.
