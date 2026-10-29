# Win110 pass51 — shared tail5A40 arithmetic and stack contract

## Finding
Confirmed, High for the executed fragment:5A40 computes AX=wrap16(WORD[BP-4]-WORD[BP-6]), restoresSP fromWORD[BP-A],popsSI/DI,and jumps3D41 withCF from that subtraction. It does not preserve the incomingCF.65536 original-instruction cases verify arithmetic, flags and register restoration.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|AX subtracts two frame words|1008:5A40/5A43 original bytes|High|
|Confirmed|CF is unsigned borrow from SUB|All65536 subtrahends with minuend8000|High|
|Confirmed|SP becomes savedSP+4;SI/DI restored from saved stack|5A46..5A4A|High|
|Confirmed|JMP reaches3D41 without adding a return address|5A4B opcodeE9F3E2 and execution|High|
|Unknown|All reachable frame values and full write-path outcomes|Full callers not executed|Low|

## Behavior model
Six original instructions execute. MOV AX,[BP-4];SUB AX,[BP-6];MOV SP,[BP-A];POP SI;POP DI;JMP3D41. MOV/POP/JMP do not overwriteCF, so3D41 receives the arithmetic borrow. Static3D41 startsJNC3D4A; onCF set it calls3D59 then setsAXFFFF and CWD. Thus an underflow is statically capable of selecting error handling. This pass stops before3D41 and does not execute its translator or claim that caller invariants permit underflow in the real game. Preserving the previous DOS-call CF through this tail would be an incorrect reconstruction of the fragment.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. All six instruction encodings match original NE2 bytes(filebaseE8A0) and baseline48 native listing. CS2000,DS=SS1048,BPD000,initialSPB000,savedSPC000,savedSI1234,savedDIABCD. First operand8000; second operand every WORD0..FFFF; incomingCF alternates with its low bit. Check AX,CF,SPC004,SI,DI,unchangedBP/DS and stop address3D41. No helper/API stubs. This is controlled16-bit microexecution, not Windows or full-game runtime. Fixed minuend coverage is explicit; not all2^32 operand pairs tested.

## Implementation-ready findings
Model this as a shared frame-dependent tail, not an ordinary independently callable function. Carry the subtraction's flags into3D41. Do not push a synthetic return address at original59B8, whose E9 JMP was verified inpass50. Keep frame fields as unsigned16-bit arithmetic with wrappingAX and borrowCF. Names/meaning of the two frame words remain TBD until caller write paths are fully traced.

## Unknowns and next test
Execute5902/59DC writer paths with original epilogue and controlled DOS writes, including short writes and text transformations, to establish frame invariants and error routing. No new game-semantic completeness claim or percentage. Overall High confidence for the six-instruction contract, Unknown for complete caller behavior.
