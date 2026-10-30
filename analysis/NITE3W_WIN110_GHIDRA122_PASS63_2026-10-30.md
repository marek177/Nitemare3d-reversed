# Win110 pass63 — dispatch-side stack request selection

## Finding
Confirmed, High in the controlled normal-branch fragment:131,080 cases connect11C2's object fields to the original119E predicate. Default request comes fromobject+7E;only frameWORD+0C=0111 andWORD+06=0 selectsobject+7C. Zero request bypasses the check;rejection reaches the call site4564. Field semantic names remainUnknown.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Object near pointer read fromDS081C|1232,1248|High|
|Confirmed|Default+7E versus special+7C selection|1236..124C;allWORD request values in both routes|High|
|Confirmed|Request0 skips119E|1252..1254|High|
|Confirmed|Nonzero rejection reaches1261 CALLF4564|Original119E result and125D..1261|High|
|Unknown|Field names,real object validity and actual event reachability|Synthetic object;no full event runtime|Low|

## Behavior model
Start1232 in the normal return branch afterCATCH. Read object pointerDS081C. LoadWORD+7E,except exact0111/zero-parameter combination selectsWORD+7C. Save selected value atBP-2. If nonzero,push it and call original119E;POP BX reclaims the argument. A nonzero predicate result proceeds1266;zero reaches1261. Static1261 calls4564,whose native wrapper pushes41BC and1 before4492. This pass stops before1261:neither that exception path nor the subsequent virtual dispatch throughmethod+58 executes. The CATCH error branch remains separate.

## Verification
131,072 exhaustive selection cases=2 branches ×all65536 selected request values. The unselected field uses a distinct complementary value to expose wrong-field selection.8 additional cases use0111 with nonzero first parameter to verify fallback to+7E. SyntheticDS object6000,SS4000,BPD000,callerSPC000,floorSS000A1000. OriginalPUSH argument2 + farCALL4 +119E ENTER6 meanspredicate spaceC000-12-1000=AFF4(45044). Request0 bypasses;nonzero request strictly belowAFF4 passes;equal or greater rejects.90,094 pass/40,986 reject. FinalSP C000 andBP D000 plus saved selectedWORD verified. No helper or API stubs. InternalCALLF119E selectorWORD at125A relocated to testCS2000. Exact sourceEXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481;native listing supplied by savedGhidra12.2 export. No fresh Ghidra database modification or real Windows execution.

## Implementation-ready findings
Keep the exact two-condition field selector,zero bypass,and additional12-byte call/frame cost. Preserve strict unsigned comparison from119E. Do not rename+7C/+7E as heap size or message limits without tracing producers. Do not assume4564 returns normally based on decompiled wrapper alone;4492/exception transfer requires a separate audit.

## Unknowns and next test
Follow4492 and its41BC payload,then object-field initialization and CATCH exception return. Real11C2 full-call reachability and virtual dispatch semantics remain open. Confidence High for field selection and branch outcomes,Unknown for actual game event/exception behavior. No1:1 parity or semantic coverage percentage claimed.
