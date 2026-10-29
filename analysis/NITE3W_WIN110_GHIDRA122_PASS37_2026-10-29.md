# Win16 1.10 — Ghidra12.2 pass37: column caller index bounds

## Finding
Confirmed High: caller66B0 supplies bottom=(previous accumulator highWORD>>4)+53EE. Combined with consumer formula, index=2*(previoushigh>>4)+1, range1..8191. All65536 highWORD values passed original fragment execution. Generated step table supports this index only for previoushigh<=2047; clipping table for<=4095. Upstream reachability remains Unknown; this is not a demonstrated game out-of-bounds bug.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Only captured directcaller of3E44 is66B0:68CB;3E44 fallback calls366A|Native instructionreferences|High|
|Confirmed|Old recordWORD+12 copied before recordDWORD+10 increment|684E..6858|High|
|Confirmed|LogicalSHR4 then centerY addition supplies bottom|685C..6866|High|
|Confirmed|Index formula requires priorhigh<=2047 for255stepentries|Consumer3679..3683 and2930 count|High|
|Confirmed|Priorhigh<=4095 fits511clippingentries|2960 count and consumerindex|High|
|Unknown|Whether upstream scene construction/nearclip excludes higher values|Not executed here|Low|

## Behavior model
Copy record[+12] tolocalBP-2. Add recordDWORD+0C into recordDWORD+10 modulo32. Compute bottom from the saved old highWORD, not updated accumulator. Later68C2 pushes this bottom to3E44; consumer computes oddindex2*(bottom-centerY)+1. Center addition/subtraction is16-bit modulo, preserving this index arithmetic for ordinary validcenter; testedcenter80 producesbottom80..4175 andindices1..8191.

The fragment has no rangeguard. This does not establish wholeengine absence of guarding. Captured instructionreferences only cover directcalls; indirectentries cannot be excluded from thisaudit alone.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.8 instructionencodings match nativeGhidra listing.65536 originalfragmentcases684E..6868; stopbefore6869. SuppliedBPframe,record6000,DS=SS1048,testCS2000. OldDWORD=(input<<16)|FFFE,delta10003 exercises lowWORDcarry and highWORDwrap. Checks savedprevioushigh,computedbottom and updatedDWORD. Consumerindex derived independently afterfragment; renderer notcalled. Bounds counts2048 and4096 reflect inclusive inputranges, not realgamecoverage.

## Implementation-ready findings
Preserve preincrement accumulator sampling to avoid shifting interpolation byonecolumn. Guardanalysis must trace recordcreation rather than adding unsupported clamps to recoveredrenderer. Stepandclippingtables have differentvalidindexlimits; do not assume the511entrytable extendsstepcoverage.

## Unknowns and next test
Trace writers of20-byte records5E88 and upstream projectedheight/nearclip limits; executecaller with controlled validscene data. Planar3E44 output,actualWinG andwholeframeparity remainopen.1551internalentries retainnativedecompile success,310EXTERNALentries separate;1401undefined executablebytes remainunresolved.

## Confidence
High for tested local state/order and conditional arithmeticbounds; limited for gameplayreachability.
