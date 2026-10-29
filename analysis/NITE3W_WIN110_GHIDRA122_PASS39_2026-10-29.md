# Win16 1.10 — Ghidra12.2 pass39: signed segment interpolation

## Finding
Confirmed High:882 original6152 cases cover selected positive/negative slopes, flat and vertical branches.864 return successfully with all20 recordbytes matching an independent signed/wrap model.18 fixtures trigger quotientoverflow fordx=-1,dy=-32768 at617C before anyrecordstore. Noactualgame reachability orWin16exceptionhandling is established.

## Evidence
|Status|Claim|Location|Confidence|
|---|---|---|---|
|Confirmed|dx,dy are16-bit endpointsubtractions|615B..6169|High|
|Confirmed|Step numerator is signed32(dyWORD<<16); denominator signed16dx|6170..617F|High|
|Confirmed|Slopedendpointvalues use signeddivision towardzero|61DA..622B|High|
|Confirmed|Startaccumulator uses low32 product(offset*step),then heightorigin addition|622E..625E|High|
|Confirmed|dx=-1,dy=-32768 causes signed32 quotientoverflow beforestores|OriginalIDIV617C|High|
|Unknown|Whether these endpoints survive upstreamprojection/culling|Notexecuted|Low|

## Behavior model
Let dx=s16(x2-x1),dy=s16(y2-y1),a=s16(recordstart-x1),b=s16(recordend-x1). Ifdx!=0,step=trunc_signed(s32(dyWORD<<16)/dx);else0. Fornonzero dx/dy,startY=wrap16(y1+trunc(a*dy/dx)),endY=wrap16(y1+trunc(b*dy/dx)). Startaccumulator=wrap32(wrap32(a*step)+(wrap16(y1-53F0)<<16)). Storestep+0C,endpointheights+6/+A,accumulator+10. Flatdy0 setsbothheightsy1 andfraction0. Verticaldx0 retainsy1/y2 withstep0 andoriginfraction0.

The quotientoverflow numerator80000000 dividedbyFFFFFFFF cannotfit signed32. EmulatedCPU faults before firststepstore; unchangedrecordbytes confirm localnonmutationfor thesefixtures. Thisdiffersfrompass32projectionfaults,whichoccurafterpartialwrites. No sharedfaultpolicyis inferred.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.111instructioncomparisons.882fixtures=7dx[-320,-7,-1,0,1,7,320]×7dy[-32768,-100,-1,0,1,100,32767]×3startoffset[-3,0,2]×2endoffset[0,5]×3y1[0,1280,FFFF]. Endpointx1=100,53F0=1280. Originalfull6152 underCS2000,DS=SS1048; nohelpersstubs. Checksall20recordbytes andSP/BP/SI/DIonsuccess. Faultcases checkinterrupt0,IP617C,allrecordbytesunchanged. FreshUnicorninstanceafterfaultavoids pendingexceptioncontamination. Notexhaustiveparametercoverage.

## Implementation-ready findings
Preserve signedWORDdeltas,divisiontowardzero,low32 multiplication andWORDheightwrap. Fractionalstartaccumulatorandroundedendpointheightsarecomputedseparately; donotderiveonefromtheotherusingfloatingpoint. Recoverupstreamconstraintsbeforeaddingorremovingfaultbehaviorinthemodernimplementation.

## Unknowns and next test
Traceobjectendpointprojection+14/+18 andper-columnpointerproducers;integrate6152with66B0interpolation andconsumeronvalidscene fixtures. ActualWin16render,wholeframeparity andfirstframeafterLOADremainopen.1551internalentries retainnativedecompilesuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
Highfortestedsignedarithmeticandlocalfaultstate;limitedforrealgameconstraints.
