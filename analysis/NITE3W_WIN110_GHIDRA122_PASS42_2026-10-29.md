# Win16 1.10 — Ghidra12.2 pass42: render run map side effect

## Finding
Confirmed High: B1A4(mode0), called for each new render run by6266, writes mapbuffer cells through selector222C.144 original executions include original3736 coordinate conversion and2AAC cached palette lookup, with no helper stubs. All4096 destinationbytes match independent expectations. Exact visible map presentation is not tested.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|Mode0 requests paletteindex2, then converts object endpoints|B1D4..B1FD|High|
|Confirmed|Coordinates are signedWORD arithmetic-shift6|3736|High|
|Confirmed|Flag08clear: orientation2 sets bothX endpoints to originalstartX-1; orientation1 sets bothY endpoints to originalstartY-1|3736|High|
|Confirmed|Flag08clear writes cachedcolor2 across half-open increasing span|B528..B587|High|
|Confirmed|Flag08set mode0 writes cachedcolor9 to onecell|B214..B230|High|
|Confirmed|Returns farpointer selectorNE6:0|B589..B592|High|
|Unknown|Actual palette rebuild and map display|Excluded|Low|

## Behavior model
For objectfarptr, derive A=s16(obj+0C)>>6,B=s16(obj+0E)>>6,C=s16(obj+10)>>6,D=s16(obj+12)>>6. If flag08clear: orientation2 makesA=C=oldA-1; orientation1 makesB=D=oldB-1. If A==C, writecolor2 at64*A+j forj in[B,D); otherwise writecolor2 at64*j+B forj in[A,C). Decreasing/empty spans write nothing locally. Flag08set bypasses these orientation corrections and writescolor9 once at64*A+B.

Initial expected model incorrectly subtracted1 independently from both endpoints. Originalexecution exposed the mismatch; raw3736 confirms both endpoints receive the adjustedstartcoordinate, and finalmodel/tests use that behavior. This matters when malformed or unusual endpoints are supplied.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.485 instructioncomparisons acrossB1A4,3736,2AAC before controlledselectorrelocation.144 cases=2flagvalues0/8 ×4orientations0..3 ×6endpointpatterns ×3color2values0/42/255. Color9=99. Endpoints use cellcoordinates plus subcelloffsets31/17. Palettecache00C4=0, so original2AAC directlyreads327E+index; paletteconstructionexcluded. TestCS2000,helperCS4000,DS=SS1048,object5000:1000,map6000:0. Mapselector relocation avoids realmode physicalaliasing; actualWin16selector allocation is nottested. Checksall4096mapbytes andreturnAX0,DX6000,SP,DS. NoOS/hooks/helperstubs.

## Implementation-ready findings
Runformation6266 has a concrete mapstate sideeffect throughB1A4mode0. Preserve axis/orientation corrections, half-open endpoints, flag08 specialcell and cachedpalettevalues. This doesnotestablish semanticasset names or fullautomaprendering. OtherB1A4modes remain outside thispass.

## Unknowns and next test
Integrate6266 with actualmode0 and6152, then trace projectedendpointconstraints. Recoverpalettecachebuild andactualmapdisplay;planaroutput/fullWin16runtime remainopen.1551internalentries retainnativedecompilesuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
High for tested mapbuffer mutations, limited for visiblegame output and untestedcoordinates.
