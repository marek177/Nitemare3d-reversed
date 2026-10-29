# Win16 1.10 — Ghidra 12.2 pass30: integrated config controller/open/read

## Finding
Confirmed High: 1134 integrated microexecutions connect original controller1010:52AE, CRT open1008:54D4, read5798 and return/error chain3D41/3D59. Short reads leave a mixture of supplied bytes and default suffix. A read failure returning-1 is ignored by the controller, which still calls the application helper. Actual OS services and five remaining helpers are simulated; this is not full configuration application or game runtime.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Controller mode8000 passes into original open and creates binary descriptor used by original read|52AE→54D4→5798, shared state|High|
|Confirmed|Positive handles read20 once; short actual0..20 preserves default suffix|Integrated destination comparison|High|
|Confirmed|Errors5/6 traverse original translator and return chain; controller still closes and applies|Exact helper/service order|High|
|Confirmed|Successful handle0 causes controller to skip size/read/close, then apply defaults|Integrated handle0 cases|High|
|Confirmed|Size mismatch continues into read only when diagnostic returns|Controlled returning diagnostic|High|
|Unknown|Whether actual diagnostic returns and effects inside5208|Stubbed|Low|

## Behavior model
Controller initializes20 config defaults, obtains a path via stub5260 and invokes original54D4. OS hooks return a controlled successful handle/device/attributes. Original open creates0876+handle flags. Controller checks signed handle>0, queries supplied size, invokes diagnostic on mismatch, then calls original5798. OS hook supplies bounded prefix or no-write error. Original read and translator return to controller. Stub close returnsFFFF; controller ignores that return and calls stub5208 with the current first configWORD. No descriptor reset or read-result substitution occurs between original routines.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.51 controller and406 CRT instruction comparisons against native listing. Imported encodings in unreachable branches normalized from native listing. Controller testCS2000, CRT testCS3000, DS=SS1048. Original controller internal NE selectors relocated to controlled test selectors.1134 cases=3 handles[0,1,19]×3 sizes[19,20,10014]×21 prefix lengths[0..20]×3 error selectors[0success,5,6]×2 device values[0,80]. Full20-byte config checked, helper and OS service order checked, apply firstWORD argument checked, finalIP/SP checked. Size mismatches use deliberately returning diagnostic. OS errors are supplied as no-write, not a universal OS guarantee.

Five helper stubs: path5260,size6664,diagnostic3118,close53B0,apply5208. OSINT21 hook handles3D00/4400/4300/3F00. Original54D4/5798/3D41/3D59 remain active. Attribute response0,0945default0,0A94remapping0,CS370Ebit0=0. Closed-handle descriptor mutation is excluded because close is stubbed.

## Implementation-ready findings
Under the tested branch conditions, controller-level lack of rollback is now confirmed through actual CRT open/read, rather than composition of isolated models. Reproduce selective default retention after short reads and ignored read failure if matching this behavior. Keep error handling changes in a remake explicit; do not claim complete parity until actual file/diagnostic/apply routes are tested. Handle0 behavior remains a controller quirk whose real reachability depends on process handles.

## Unknowns and next test
Recover5208 application side effects, real close/size paths, diagnostic termination and DOS3CALL branch. Whole game-save LOAD first frame and actual Win16 runtime remain open.1551 internal entries retain native decompile success;310 EXTERNAL entries separate.1401 undefined executable bytes remain unresolved.

## Confidence
High for the integrated controller/open/read path within the stated simulation contract. No full-game or real-OS parity claim.
