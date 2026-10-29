# Win16 1.10 — Ghidra12.2 pass27: binary read return/error chain

## Finding
Confirmed High: the direct binary CRT read path now executes through original583F tail jump,3D41 epilogue and3D59 error translator to far return.21504 controlled cases passed. Failed calls returnDX:AX=FFFFFFFF and storeWORD9 at085E, while086E receives raw errorAL. Successful reads preserve prior error fields.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|Read-service errors forceAH9 before translator|5798:57FD|High|
|Confirmed|Invalid descriptor synthesizesAX0900 andCF1|57C2..57C6|High|
|Confirmed|Translator savesAL to086E and nonzeroAH sign-extends to085E|3D59..3D7D|High|
|Confirmed|CFerror yieldsAXFFFF,CWD→DXFFFF|3D43..3D49|High|
|Confirmed|Success skips translator, leaves085E/086E unchanged|3D41→3D4A|High|
|Confirmed|Common epilogue restoresDS,BP,SP and returns far|3D4A..3D52|High|
|Unknown|ActualWin16DOS3CALL service behavior and error-side memory writes|OSstub; directINT21only|Low|

## Behavior model
Binary prefix producesCF andAX. Error service results haveAH replaced by9, preserving rawAL. Translator storesAL and usesAH9 directly, so its generalAH0 lookup table does not participate in these error cases. Common error epilogue sets returnAXFFFF and sign-extends with16-bitCWD. On success,AXcount survives and previous errno-like state remains stale; callers must use return result rather than assuming error state cleared.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.73 instruction comparisons, with unreachable importedCALLF57F2 represented by native Ghidra relocation bytes as inpass26. Original prefix and tail/translator/epilogue executed underCS2000,DS=SS1048.21504 Cartesian cases over handles0/1/3/19/20/FFFF,request0/1/20,EOF0/2,bounded actual0/1/7/20,error-selector0..255. Selector0 means success;1..255 meanCFerror with that rawAL. This does not claimCFerrorAL0 was tested. NoCRT helper stubs; onlyINT21 service simulated. Checks complete20-byte destination,OS call count,AX,errorfields,DS,BP,SP and far-returnIP;DXFFFF asserted on errors. SuccessDX is not asserted as a contract. No-write-on-error is suppliedOS behavior, not a universalDOS guarantee.

## Implementation-ready findings
For this recovered path, failed read returns signed-1, records rawAL andWORD9; valid zero-length/EOF returns0 without clearing error fields. Short successful read remains short without retry. Config controller pass25 ignores this-1 return, but integrated config-open descriptor flags remain unverified. Do not generalize these findings to textmode or extended descriptor branch.

## Unknowns and next test
Verify actualconfig-open flags and DOS3CALL route, then integrate52AE with original read path. WholeLOAD first frame, actualWin16 runtime and parity remain open.1551 internal entries retain native decompilation success;310 EXTERNAL entries counted separately.1401 undefined executable bytes remain unresolved.

## Confidence
High for tested return/error chain. Limited for actualOS and fullconfig/game execution.
