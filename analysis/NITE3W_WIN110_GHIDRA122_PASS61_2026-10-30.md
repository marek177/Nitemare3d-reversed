# Win110 pass61 — startup producer of stack-probe boundary082E

## Finding
Confirmed, High within the executed startup fragment:after a nonzeroAX result, original3728 adds0100 toCX and372E stores it atDS082E,provided the addition does not carry.65,542 cases verify success,overflow,and zeroAX bypass. This connects5A9C's probe variable to a concrete producer in the CRT entry sequence,but does not establish the actual Windows-supplied register values.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|372E is captured direct WRITE to082E|Native Ghidra12.2 references|High|
|Confirmed|InputCX0..FEFF becomesCX+0100 at082E|All65536 CX values withAX1|High|
|Confirmed|CXFF00..FFFF carries and bypasses producer stores|256 overflow cases|High|
|Confirmed|AX0 bypasses even the earlierES save|Six zeroAX fixtures|High|
|Unknown|Meaning/range ofCX actually returned byINITTASK|API not executed|Low|

## Behavior model
CRT entry3718 callsINITTASK at371B. The controlled test starts at3720 after that call. OR AX,AX/JZ rejectszero. NonzeroAX first savesES to0864,thenADD CX,0100. Carry transfers to3710 before writing082E or the adjacent startup-register fields. Without carry,372E..3742 write sixWORDs:082E=CX+256,0830=SI,0832=DI,0834=BX,0836=ES,0838=DX. Therefore an overflow leaves082E..0839 unchanged while0864 has already been updated. ZeroAX leaves both areas unchanged.

Original5A9C later reads082E and compares it with current stack position,as established inpasses59–60. The source of082E is not simply the raw inputCX:it includes the verified256-byte increment and an overflow guard. Naming that increment a safety margin is only an interpretation; no Windows API semantic contract is asserted here.

## Verification
65,536 CX values withAX1 plusAX0 atCX0,1,FEFF,FF00,FF01,FFFF=65,542.65,280 successful stores,256 carry exits,6 zeroAX exits. All12 bytes of082E..0839 checked against independently constructed expected fields;0864 checked separately to preserve ordering. DS1048 andSS4000 distinct;CS2000,SP D000. Stops3710 before failure handling or3746 before GETVERSION. No API/helper stubs,actualINITTASK,termination,or whole-startup execution. Native3720..3745 encodings checked against originalNE2 bytes and saved Ghidra12.2 listing. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

## Handler provenance and remaining distinction
The preserved direct-reference export shows082E producer372E and consumer5A9E. For08B0 it captures reads at3A14 and3A1B,no direct setter to that exact address. Original08B0 offsetFFFF still only proves initialized default handler selection. Arbitrary indirect stores,overlapping wider stores,and bulk initialization are not excluded. SS000A/000C are distinct stack control words; their initialization is not resolved by findingDS082E's producer. These variables must not be conflated even where real DS andSS may alias.

## Implementation-ready findings
For this fragment,guardAX before all saves;save0864 before checkingCX overflow;write the six startup words only on carry-clear. UseWORD wrapping and the exactFF00 threshold. Keep the Windows input-register contract,SS floor/minimum initialization,and alternate-handler installation explicitly unresolved. Confidence High for producer arithmetic and ordering,Unknown for full real startup state. Next: inspect the stack-segment setup and INITTASK boundary,then follow remaining indirect initialization candidates. No new decompile coverage percentage or full-game parity claim.
