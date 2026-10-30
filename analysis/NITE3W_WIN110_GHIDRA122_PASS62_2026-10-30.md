# Win110 pass62 — game-side stack predicate and raw stack metadata

## Finding
Confirmed, High: game-side function1000:119E returns1 exactly when its unsignedWORD argument is less than wrap16(entrySP-6-SS000A).65,608 original-instruction cases verify strict comparison,frame restoration,and unchecked subtraction underflow. Raw EXE data has zero words atNE10 offsets000A/000C;that is not evidence of runtime zero after Windows initialization.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Predicate reads floor viaSS,notDS|1000:11A2;DS1048/SS4000 distinct fixtures|High|
|Confirmed|ENTER4 consumes6 bytes before capturingSP|119E..11AD and execution|High|
|Confirmed|Unsigned strict comparison; equality returns0|11B0..11BD;all65536 argument values|High|
|Confirmed|Subtraction wraps rather than clamps if floor exceeds capturedSP|Boundary fixtures|High|
|Confirmed|Captured direct caller is1257 inside11C2|Native Ghidra12.2 reference export|High|
|Unknown|Runtime floor values and loader/INITTASK modifications|No actual Windows trace|Low|

## Behavior model
119E ENTER4 pushesBP and reserves4 bytes,then readsSS000A. It saves currentSP,subtracts the floor modulo16 bits,and compares the resultingWORD with caller argumentBP+6. JBE returns0;otherwiseAX1. LEAVE/RETF restores the caller frame and leaves argument cleanup to the caller. This predicate is different from5A9C:5A9C returns0 when its DS082E boundary is at or aboveSP,while119E does not clamp its SS000A subtraction. Do not collapse them into a single generic stack-availability function.

## Verification
65,536 request values atentrySP D000,floor1000,plus72 boundary cases=3 stack positions100/2000/D000 ×4 floors0/SP-6/SP-5/FFFF ×6 requests0/1/2/255/8000/FFFF. CS2000,DS1048,SS4000. OriginalNE1 code loaded unchanged. Every case checksAX,SP(entry+4 after far return),restoredBP,and unchangedSS control words plusDS guard bytes. No API or helper stubs;no whole caller11C2 execution. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Native listing and caller references are from preserved Ghidra12.2 export;no fresh database change claimed.

## Raw metadata and unresolved initialization
OriginalNE header offset80 has initial SP/SS word pair atNE+18 equal0/10. OriginalNE10 initialized bytes atfile2C040+000A and+000C are both0000. These byte observations do not establish the effective Windows loader stack pointer or contents of runtime stack control words. No captured explicit MOV SS/POP SS was found in the scoped listing search;that does not exclude loader setup,indirect writes,segment aliases,or imported initializer effects. The earlier discoveredDS082E producer372E remains separate fromSS control-word provenance. No setter or loader semantics is invented to fill the gap.

## Implementation-ready findings
Preserve strict unsigned request<available and16-bit wrap for119E. Its six-byte frame cost matters at the comparison boundary. KeepSS floor distinct fromDS082E. Underflow behavior is verified in synthetic fixtures;the real caller may maintain stronger invariants and a reachable-game defect is not claimed.

## Unknowns and next test
Inspect11C2 and its1257 request construction,then follow real Windows stack initialization or an independently available runtime trace. SS000A/000C producer and alternate-handler installation remain open. Overall confidence High for predicate and raw bytes,Unknown for runtime initialization and full caller reachability. No semantic completeness percentage or whole-game parity claim.
