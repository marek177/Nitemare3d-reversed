# Win16 1.10 — Ghidra12.2 pass24: configuration ownership

## Finding
Confirmed High: flags4BE4..4BE6 belong to the20-byte config block4BD4..4BE7. config.sav reader/writer and temporary mode snapshot use this whole block. Game SAVE player data starts at4BE8, so these flags are outside that explicit saved player range. Do not equate this with proof that no indirect loader effect changes them.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|Default initializer sets4BE4/5/6=0|1010:52AE,52E3..52E9|High|
|Confirmed|config.sav requires lengthDWORD20; reads20 bytes to4BD4 if signed handle>0|5308..533D|High|
|Confirmed|Local config reader return is discarded; size-error diagnostic3118 does not itself prove termination|531E..5334|High|
|Confirmed|Config writer writes20 bytes from4BD4, no local result check|534E..5387|High|
|Confirmed|Modes46B8=1/3 snapshot20 config bytes to3930 and level7E54 to3944|DAA0..DACD|High|
|Confirmed|Before first initialization callee clear4BE0/3/4/5/7, set4BE6=1|DACF..DAE2|High|
|Confirmed|Restore fragment replaces snapshot bytes3934..3937 with current4BD8..4BDB, then copies all20 bytes back; restores saved level|DB43..DB67|High|
|Confirmed|Status text appends letters S/P/A/I for nonzero4BE4/5/6/7|C38C:C4C2 onward|High|
|Unknown|Semantic feature names of S/P/A/I and mode46B8|Setter/UI/resource evidence incomplete|Low|

## Behavior model
Initialization first supplies defaults then optionally reads config.sav. Command parser1118 invokes this initializer; option-p route also invokes it after its string scan. Thus flag values can arrive through a block read even though individual WRITE xrefs show few setters. This is why listing xrefs alone is insufficient to prove all assignments.

Temporary modes1/3 preserve config and level, force4BE6=1 and4BE4/5=0, then call initialization chain and seed-one wrapper. On restoration path, a selective four-byte exception preserves current4BD8..4BDB. Their viewport interpretation is inferred from defaults and other consumers; byte identity and copy behavior are confirmed independently of that label.

BF20 also clears4BE5 when51A6 was zero, after sound call, before three083E calls. This side effect is statically observed only. No feature name is assigned from suggestive S/P/A letters alone.

## Verification
768 original-instruction fragment cases, no callee stubs:512 snapshot cases (mode1/3 ×256 distinct config patterns),256 restoration cases. All43 instruction byte encodings match SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481 EXE. TestCS2000,DS=SS1048,DF0. Check all20 bytes and saved/restored level. Snapshot stops before DAE3; restoration starts atDB43 after90CE and stops beforeDB68. REP MOVSD executes original bytes. No file I/O, intervening helpers or full frame executed.

## Implementation-ready findings
Keep persistent configuration separate from game-save player state. Mirror temporary configuration ownership and the4BD8 DWORD preservation exception. With flags active, apply pass23 finalizer overrides after load. Config size validation compares both AX=14h and DX=0. Diagnostic continuation and partial read behavior require CRT/fatal-path verification before claiming robust rejection.

## Unknowns and next test
Trace mode46B8 and configuration/UI setters to name features; microexecute complete config reader with short/error reads and controlled diagnostic returns; execute full load and next dispatcher. Original whole-game runtime parity remains open.1551 internal entries retain native decompile success;310 EXTERNAL entries are separate.1401 undefined executable bytes remain unresolved; this pass changes comments only.

## Confidence
High for exact block ranges and tested copies; Medium for larger configuration lifecycle because surrounding callees were excluded.
