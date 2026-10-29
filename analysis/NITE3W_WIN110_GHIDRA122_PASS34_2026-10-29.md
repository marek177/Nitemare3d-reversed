# Win16 1.10 — Ghidra12.2 pass34: integrated viewport rebuild chain

## Finding
Confirmed High: original5208→E4B2→2960 executes as one chain without helperstubs.649 widthfixtures produce646 fullreturns and3 dividefaults.330106 tableentries match independent wrap-aware expectations. Faultwidths0/1/FFFF stop before2960, leaving the full1538-byte table region unchanged while geometry and the first three projectionDWORDs are already written.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|5208 generated geometry is consumed directly by E4B2 and2960|OriginalCALLF5254/5259,sharedDGROUP|High|
|Confirmed|646 fullchains match18 geometrybytes,16 projectionbytes and1538 table-regionbytes|Integratedverification|High|
|Confirmed|Fault0/1/FFFF leaves3A76 and table region unchanged after partial priorwrites|FaultIP E50C,statecomparison|High|
|Confirmed|Successfulchain restoresSP,BP,SI,DI|Finalfarreturn checks|High|
|Unknown|RealUI widthconstraints and pixeloutput|No UI/renderconsumer execution|Low|

## Behavior model
5208 reads globalWORD4BD4, writes53E0..53F0, calls E4B2, then2960. The chain now uses original internalfarcall selectors relocated to a controlled testCS; no harness supplies intermediate height or projectionfields. Geometry uses16-bit wrap and signedSAR. Projection uses signeddivision and32-bit shiftwrap.2960 generates511 byte/WORD pairs. Their exact formulas are preserved in evidence script and passes31–33.

If projection denominator iszero, execution faults before finalprojectionstore and before2960. Therefore the local update is not atomic: geometry and first3 projectionDWORDs change, finalprojectionDWORD and tables remain old. This is controlledCPU-state evidence, not proof of a visible game defect or actualWin16 exception recovery.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.109 instruction encodings checked against nativeGhidra listing before testselector relocation.649 widths=0..640 plus4095,4096,8191,8192,32767,32768,65534,65535. TestCS2000,DS=SS1048. Original52xx arithmetic/calls,E4B2 and2960; nohelpersstubs.646 successfulchains×511 entries=330106 entries. Check complete outputregions, untouched table gaps and returnstate. Faultcases verify interrupt0/IP E50C and untouched tablebytes. Unicorn instance recreated afterfault to avoid pendingexception contamination. Renderer,OS and UI notexecuted.

## Implementation-ready findings
Preserve orderedstate writes and callee order when reproducing configuration widthrebuild. Donot treat separately recovered formulas as independent updates that may be reordered. The validinput policy remainsTBD; malformed fixtures are not established reachable gameinputs. The testedstate chain is stronger than isolatedfunction agreement but is not framebufferparity.

## Unknowns and next test
Audit consumers of2C7F/2E80 and connect generatedentries to sprite/wall clipping or scaling with directevidence. Trace realUI widthrange; integrate configloader with5208chain. WholegameSAVE/LOAD firstframe andactualWin16render remainopen.1551internalentries retainnativedecompilationsuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
High for testedintegratedstate transitions, limited for fullgame consequences.
