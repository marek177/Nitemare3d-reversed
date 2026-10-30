# Win110 pass59 — exact text-writer stack availability thresholds

## Finding
Confirmed, High within the fixed caller-stack setup:65536 original5902 prefix executions exhaustively varyWORD082E and verify the stack-space decision. Reported availability0..168 reaches fatal3C3D withAX0;169..551 selects128 bytes;552 and above selects512 bytes. Initial08B0=FFFF selects the built-in fatal route. No OS call or helper is stubbed.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|5A9C returnsSP-082E when082E<SP,otherwise0|Original5A9C..5AAE|High|
|Confirmed|Availability<=A8 takes low-stack path|5989..598C,59D5|High|
|Confirmed|A9..227 chooses80-byte buffer;228+ chooses200|5993..599E|High|
|Confirmed|Low-stack call39F2 reaches3C3D withAX0 under initialized handler|39F2..3A22 and original08B0FFFF|High|
|Unknown|Alternate08B0 handler behavior and actual runtime exhaustion|Not executed|Low|

## Behavior model
The test starts at5902 with text descriptor80 and input A+LF,so it executes the original caller frame and LF detection. Stack helper5A9C executes by relocated far call and observesSP CFEE after temporarily popping the return address. It compares the supplied082E WORD to thatSP:values at or aboveSP yield0,otherwise the difference. The caller rejectsavailability<=168. For accepted values it subtracts2 bytes fromSP and chooses128 or512 based onavailability<552. The test stops at599E before subtracting the selected buffer size.

Low availability reaches59D5,which setsAXFFFC and enters39F2 through PUSH CS/CALL. Original39F2 treats the request with its own alignment/subtraction checks and reaches3A14. Original data initializes08B0 offsetFFFF;3A18 increments that offset and its zero result selects3A1F MOV AX,0,thenJMP3C3D. This proves the error handoff under the supplied original data; it does not execute the fatal body or establish real Windows termination behavior.

## Verification
Every possible082E value0..FFFF tested once. Fixed entrySP D000,BPE000,CS2000,DS=SS1048,handle1,direct threshold20,0A94=0. Original data supplies08B0FFFF. ProbeSP CFEE=53230. Outcomes:12474 fatal,383 small-buffer,52679 large-buffer. Boundary samples available168/169 and551/552 verify inclusivity.73 executed instruction starts match preserved Ghidra12.2 native listing and rawEXE,apart from declared internalCALLF5A9C selector relocation at5987 to testCS. No simulated OS services. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. No new Ghidra database write or actual Win16 runtime claimed.

## Implementation-ready findings
Implement unsigned comparison for the probe and preserve both inclusive threshold boundaries. Do not describe128/512 allocation as unconditional:the2-byte reservation and available-space guard precede it. Under initialized08B0 use original fatal handoffAX0 for this path; keep the alternate handler branch distinct and unresolved. Exhaustive082E coverage at one fixed stack does not prove all16-bit stack-wrap configurations.

## Unknowns and next test
Execute the probe against multiple stack positions and inspect alternate08B0 handler provenance. Separate stack allocation39F2 behavior from OS stack semantics. Real game1:1 parity,Windows exception/termination and undefined code bytes remain open. Confidence High for the observed prefix/thresholds;Unknown for actual exhaustion reachability.
