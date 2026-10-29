# Win16 1.10 — Ghidra12.2 pass26: binary CRT read prefix

## Finding
Confirmed High: binary-mode directDOS read branch1008:5798 performs one AH3F service call, without retrying a short successful read.252 controlled original-instruction cases passed. The actual OS service is stubbed; execution stops at583F before error translator and epilogue.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|Unsignedhandle>=0870 yieldsAX0900,CF1 before checking zero request|57BE..57C6|High|
|Confirmed|Validhandle,request0 returnsAX0,CF0 withoutOS|57C8..57CD|High|
|Confirmed|DescriptorEOFbit02 returnsAX0,CF0 withoutOS|57CF..57D4|High|
|Confirmed|DirectDOS AH3F usesBXhandle,CXrequest,DS:DXdestination|57D6..57F9|High|
|Confirmed|Successful shortAX passes to583F without retry when descriptorbit80 clear|57FB,5801..5806|High|
|Confirmed|ErrorCF setsAH09 preserving errorAL, then reaches translator|57FD..57FF|High|
|Unknown|FinalAX/errno after translator, actualOS error buffer mutation|Stop583F and OSstub|Low|

## Behavior model
Under0A94=0 andCS370Ebit0=0, validate handle against0870. Valid zero request and EOF skipOS. Otherwise callINT21 AH3F once. On error, setAH09 and preserveCF. On success, binary descriptorbit80clear branches directly to shared translator/epilogue entry583F. Textmode bit80set and extended descriptors use other paths and are excluded.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.43 prefix instruction comparisons against native listing. Imported CALLF at57F2 uses the native listing relocation bytes, not the raw chain selector; this branch is not executed. TestCS2000,DS=SS1048.252 valid Cartesian fixtures across handles0/1/3/19/20/FFFF,request0/1/20,EOF0/2,actual0/1/7/20 bounded by request,error0/5/6. OS hook validates registers and injects a prefix on success or no bytes on error. ChecksAX,CF,number ofOS calls and all20 destination bytes. A successful zero/short read leaves untouched suffix unchanged under this controlledOS contract. Error-side partial writes are not modeled.

## Implementation-ready findings
Do not add automatic retry or suffix clearing inside the recovered binary prefix. Combined with pass25, a real short successful read can reach config application with mixed defaults if this binary path is selected; opening descriptor flags and final helper paths still require integrated verification. Actual no-write-on-error is a harness assumption, not a recovered globalOS guarantee.

## Unknowns and next test
Execute3D41/3D59 error translation and epilogue; confirm descriptorbit80 after config open; testDOS3CALL and text conversion separately. Whole-game runtime and first frame afterLOAD remain open.1551 internal entries retain native decompilation success,310 EXTERNAL entries separate;1401 undefined executable bytes remain unresolved.

## Confidence
High for tested prefix control flow and arithmetic; limited for finalCRT return andOS behavior.
