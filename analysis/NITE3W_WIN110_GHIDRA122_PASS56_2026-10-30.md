# Win110 pass56 — append seek before byte/text write

## Finding
Confirmed, High within controlled OS boundaries:4144 complete5902 executions verify append seek and failure routing. Descriptor bit20 triggersINT21 AX4202 with zero displacement before byte/text dispatch, even when requested length is zero. Seek failure prevents every write and returnsAXFFFF through original3D41/3D59. Seek-successDXAX positions do not change the tested emitted bytes or logical return lengths.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Append requests seek-origin end,offset0|5939..5957; capturedAX4202,CX0,DX0|High|
|Confirmed|Seek occurs even for zero requested bytes|Full5902 entry; empty-input fixtures|High|
|Confirmed|All tested seek errors1..255 bypass output and returnFFFF|5959→5936→3D41/3D59;4080 cases|High|
|Confirmed|Successful seeks permit original byte/text output|64 cases, four32-bit returned positions|High|
|Unknown|Actual file/device side effects,OS error reachability|No real filesystem services|Low|

## Behavior model
5902 checks descriptor bit20 before bit80(text). It seeks to end byAX4202,CX=DX=0. WithCF set,5959 branches to5936, which jumps3D41 without theAH09 rewrite used for write errors. Therefore3D41 receives the raw selected seek error inAX; original3D59 translates it before the finalFFFF return. Tests capture rawAX/CF at3D41 and execute the original translator, but do not independently assert every errno table mapping. WithCF clear, processing continues. Byte mode passes data unchanged; text mode insertsCR beforeLF and returns logical source length. Empty input still seeks and then returns0 withoutAH40.

## Verification
4144=4 descriptors20/60/A0/E0 ×4 inputs(empty,A,LF,512A+LF) ×259 seek responses(4 successes plus255 errors). Successful positionsDXAX=0,FFFF,10000,FFFFFFFF are synthetic32-bit return values chosen to exercise both words, not claims about valid real seek positions. Error fixturesAX1..FF,CF1. Seek invocation count exactly1 and order checked. All failure cases have no write events. Success output compared with original payload or independentLF→CRLF expansion; finalAX equals original input length. Stack/register/source preservation inherited from preservedpass54 complete-caller runner.160 executed instruction starts checked against native Ghidra12.2 listing and rawEXE, with only the declaredCALLF5A9C test-selector adjustment at5987. DirectINT21 selected; no extended handles or DOS3CALL. Original EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Unicorn2.1.4 microexecution; no fresh Ghidra database modification or whole-game runtime claimed.

## Implementation-ready findings
Place append seeking before zero-length early return and before text conversion. Stop immediately on seek failure; retain raw seek error for original translator. Do not reuse a write-errorAH09 path for seek errors. Do not infer physical append positioning or file persistence from this harness: services return selected states and record bytes without real I/O.

## Unknowns and next test
Extended-handle73C5,DOS3CALL,the limited-stack fatal path,real seek/device behavior and actual SAVE writes remain unresolved. Next audit follows alternate descriptor dispatch and original low-stack guard. Confidence High for tested control flow, arguments and returned values; Unknown for actual Windows/file effects. Counts measure fixture coverage, not1:1 game completeness.
