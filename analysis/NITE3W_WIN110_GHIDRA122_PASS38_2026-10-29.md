# Win16 1.10 — Ghidra12.2 pass38: render segment setup and flat height

## Finding
Confirmed High:6266 builds20-byte render records starting5E88 and invokes6152 to initialize endpoint heights and interpolation.65536 original6152 executions on its flat-endpoint branch show no local heightclamp: fullWORD endpoint heights pass into record+6/+A, and record+12 becomes(y-53F0)mod65536. This does not prove arbitrary endpoints reach the realrenderer.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|6266 scans per-column farpointers at53FE+4*x, starts new run when farpointer changes|6266 native/decompiled|High|
|Confirmed|Runs use20-byte records, farpointer+0,startX+4,endX+8|6266→6152|High|
|Confirmed|6152 deltaX0 setsstep0; equalY setsstep0 and equalstoredheights|616C..61A3|High|
|Confirmed|Flatbranch fraction0,highWORD=y-53F0|61B5..61BB,625E|High|
|Confirmed|Noheightclamp observed in any65536 flatYfixtures|Originalfullfunctionexecution|High|
|Unknown|Endpointproducer clipping and realgame reachability|Upstreamnotexecuted|Low|

## Behavior model
6266 groups contiguous equal farpointers into rendersegments. It resetscount5E7E and starts atviewportleft53E4 throughright53E6; records carryfarobjectpointer andinclusiveXbounds. Forfinishedruns itcalls6152 using farobjectDWORDs+14/+18 asendpointdata. Count>=50 calls3118 withMAXSEGdiagnostic; diagnostictermination/safety is notverifiedhere.

6152 subtracts endpointX/Y in16-bit arithmetic. For flatY, stepDWORD+0C=0, WORD+6=WORD+0A=y, fractionWORD+10=0, highWORD+12=(y-53F0)mod16. This directlyfeeds theprevious-highWORDconsumer recoveredpass37. IfarbitraryYwereallowed,thisinitializerwouldnotensurethatconsumer's2047bound; actualendpointconstraintsremainunproven.

Nonflatbranch statically computesfixedpoint slope, interpolatedstart/end andaccumulator. Its completeedgecases havenotbeenexecutedinthispass. Do notpromote flatbranchcoverage tofull6152coverage.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.111instructioncomparisonscover6152body.65536 originalfullfunctioncases withx1=10,x2=20,recordstart10/end20,y1=y2=eachWORD,53F0=1280. TestCS2000,DS=SS1048,record6000. Compareall20recordbytes,includingunchangedpointer/Xfields;checkSP,BP,SI,DIrestoration. Nohelpersstubs,OS,gameframeoractualassets. AllYbitpatternsarecontrolledfixtures,notestablishedvalidcoordinates.

## Implementation-ready findings
Preserve20-byte recordlayout andflatbranchWORDwrap; donotaddanunsupportedlocalheightclampwhenreconstructing6152. Recoveryofupstreamendpointprojectionisrequiredtoproveindexbounds. Segmentgroupingsemanticsarestaticfindingsandwerenotmicroexecutedhere.

## Unknowns and next test
TracewritersofobjectendpointDWORDs+14/+18 andper-column53FEfararray;verifynearclip/heightboundsbefore6266. Testnonflat6152withsigneddelta/overflowfixtures,thenconnectrealisticrecordstoconsumer. ActualWin16renderandfirstframeafterLOADremainopen.1551internalentries retainnativedecompilesuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
Highfortestedflatbranch;Mediumforstaticrecordgrouping;Unknownforupstreamvalidityconstraints.
