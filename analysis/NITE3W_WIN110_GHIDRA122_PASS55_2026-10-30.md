# Win110 pass55 — complete text-writer short writes across CR insertion

## Finding
Confirmed, High under the documented OS model:144 complete5902 executions verify partial/error escape across128/512-byte temporary buffers. Six controlled cases produce a subtraction underflow because the inserted-CR counter is larger than the number of physical bytes accepted by the OS. The original epilogue then returnsAXFFFF. This establishes behavior of the executable under selected short-write responses, not a demonstrated real OS/game defect.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Successful physical countBP-4 equals sum of modeled accepted write counts|144 full-caller cases, independent OS-event ledger|High|
|Confirmed|Shared tail subtracts the current inserted-CR countBP-6 even on short-write escape|Original5A40..5A43 plus captured frame|High|
|Confirmed|That subtraction underflows in6 cases and selects original error return|BoundaryCF captured before3D41; finalAXFFFF|High|
|Unknown|Actual short-write frequency and game-file reachability|No actual DOS/Win16 OS service|Low|

## Behavior model and concrete example
Input A followed by64 LF bytes has65 logical bytes and expands to129 physical bytes. In the512-byte-buffer path the first write request is129 bytes. Model a successful short write accepting only1 byte. OriginalBP-4 becomes1; originalBP-6 already counts64 inserted CRs in the prepared buffer. TailAX is1-64 modulo65536=65473(FFC1),CF1. Original3D41/3D59 then returnsAXFFFF to the far caller. In particular, this path does not return the one accepted physical byte or automatically clamp the logical difference to zero.

This clarifies the scope of pass52: its generic frame fixtures demonstrated subtraction behavior but had not established the origin of the second operand. Full5902 shows59C7 increments it when preparing CRLF, before the corresponding physical writes necessarily succeed. The result is an original timing relationship between conversion bookkeeping and write completion. Implementation parity requires retaining this behavior rather than silently replacing it with a logical-byte estimate. Whether the behavior matters in an actual game run remains unverified.

## Verification
144 cases=2 buffer-reserve settings ×6 payloads ×3 failure-event indices ×4 policies. Payloads:A+LF,A+64LF,A+256LF,127A+LF,511A+LF,A+1024LF. Writes before event1/2/3 succeed fully; selected event returns0,1,count-1 bytes withCF0,or error5 withCF1. If no such event occurs the whole write succeeds. DescriptorC0,input startsA; Ctrl+Z branch deliberately separate from passes53–54. Captured complete event ledgers are in cases.json.

Full original entry5902,stack helper5A9C,flush59DC,sharedtail5A40,and3D41/3D59 return execute. Reuse the preserved pass54 setup with declared5987 selector relocation and simulatedINT21 AH40. Source immutability and register/stack restoration use the same assertions. Additional checks:attempted output is a prefix of independently expanded CRLF data;BP-4 equals sum of actual acceptedOSbytes;AX/CF follow captured inserted count; finalAX follows original error/success branch. The inserted count is observed from the original caller frame, not claimed independently reimplemented by the oracle. The full emitted stream is independently verified in the2,068 successful cases ofpass54. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

## Unknowns and next tests
Append seek4202,extended descriptors,DOS3CALL,stack fatal path,real OS return behavior,Win16 runtime and full-game parity remain open. This report does not prove a vulnerability, file corruption or reachable game failure. Confidence High for recorded microexecution and numerical contract; Unknown for actual-device behavior. Next: append seek failure before any conversion and the alternate handle routes.
