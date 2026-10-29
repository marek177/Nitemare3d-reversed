# Win16 1.10 — Ghidra12.2 pass29: original open→read sequence

## Finding
Confirmed High:864 sequenced microexecutions connect original54D4 open to5798 binary read and3D41/3D59 return chain. The handle returned inAX and descriptor flags created by open are retained unchanged between calls. Successfulshortcounts and controlledOS errors behave as previously recovered in isolated tests. This is a two-function sequence, not a completeconfigloader or actualWin16game run.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Mode8000 originalopen produces binary descriptor used directly by originalread|54D4→5798,sharedmemory|High|
|Confirmed|Read uses actualopenreturnedhandle, not a manually substitutedhandle|Harness capturesAX afteropen|High|
|Confirmed|Device41 and disk01/11 descriptorflags all reachoneAH3Fservicecall forrequest20|Originalread+OSservice sequence checks|High|
|Confirmed|Successful0/1/7/20bytes returncount and retainuntouchedsuffix|864fixturegroup|High|
|Confirmed|Errors5/6 returnAXFFFF,DXFFFF,085E=9,086E=rawerror|Original3D41/3D59|High|
|Unknown|Complete52AE controller,sizequery,closeandapplyeffects|Excluded|Low|

## Behavior model
Execute originalopen withpathpointer6000,mode8000 andcontrolledOS success. Preserve descriptor memory. CaptureAXhandle, constructcallerstack forread(handle,6100,20), execute originalread throughfarreturn. No reset ofdescriptorflags occurs. OSservices simulateopen3D00,devicequery4400,optionalattributes4300,thenread3F00. NoCRTfunctionstub is used.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.406 instructioncomparisons acrossopen/read/translator/epilogue; unreachableimport encodings normalized fromnativeGhidra listing.864cases=3defaults0945[0,80,FF]×2devicevalues[0,80]×4attributes[0,1,2,FF]×3handles[0,1,19]×4actualcounts[0,1,7,20]×3errorselectors[0success,5,6].CS2000,DS=SS1048,directINT21branch,0A94=0. Check20descriptorbytes afteropen,exactOSsequence,all20destinationbytes,AX,errorfields,DS,BP,SP andDXFFFFonerror. OSerrors are modeledasno-write. Harness suppliesOSresults; noactualfilesystem wasopened.

Handle0 is deliberatelyincluded atCRTlevel. Configcontroller52AE wouldskipreadingandclosing0; thissequence thereforedoesnotrepresentthatcontrollerpath forhandle0. Devicefixtureattributesareunusedbecauseitsbranchskips4300; Cartesianfixturecount includes those repeats.

## Implementation-ready findings
Keepdescriptorstate producedbyopen whenreconstructingread; explicitbinarymode survivesdefaulttextmodeanddevice/readonlyclassification. Preserve shortreturnsandstaleerrorfields onsuccess. Theseclaimsapplyonlytothetestedroute. Completeconfigloadingstillrequiresconnecting52AE andremaininghelpers ratherthanassumingindependenttestsprovewholeloaderparity.

## Unknowns and next test
Integrate52AEcontroller withoriginalopen/read; verify0A94/370Einitialization andDOS3CALL path. Close,size,applyandfataldiagnosticremainpartiallyunverified. WholeLOADfirstframe andgameplayparityremainopen.1551internalentries retainnativedecompilationsuccess;310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
Highfortestedtwo-functionsequence; nofullgameoractualOSparityclaim.
