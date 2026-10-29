# Win16 1.10 — Ghidra12.2 pass36: original generators to linear column

## Finding
Confirmed High:3600 sequences execute original2930 and2960 before original366A. The renderer consumes their actual generated tables without replacement. Every65536-byte controlled destination matches an independent outputmodel across fiveviewport widths. This closes the generator-to-consumer connection for the tested inputs, not fullgame/WinG pixel parity.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|2930 generates255 DWORDsteps forindices1..255|2930..295E,2482..2C7D|High|
|Confirmed|2960 generates511 clippingbyte/WORD pairs fromsuppliedheight|2960..29BD|High|
|Confirmed|366A directly uses originalgeneratedsteps andclippingtables|Sharedmemory,3600sequences|High|
|Confirmed|Full64KB destination matches model,includingpaletteandclipping|Buffercomparison|High|
|Unknown|RealWinG selector/frame setup andcallerconstraints|Controlledbuffers/geometry|Low|

## Behavior model
For eachfixture, supplyviewportgeometry, execute original2930 tobuildstepDWORDs, then original2960 tobuildclippingtables, then original366A todrawacolumn. No generatedtable is altered byharness betweenfunctions. Model independentlyusesstep=floor(4194304/index) andtherecoveredclippingformula, thenfractionalADD/ADC sourceadvance. Optionalpalette mapscolor→255-color.

Important range distinction: stepgenerator2930 produces255entries, clippinggenerator2960 produces511entries. Thispass usesindices3..183, withinboth. Earlierpass35 suppliedstepentries beyondtheoriginalrange asfixturedata; its executedindices also stayedwithintheoriginalrange, so itsreportedoutputs donotdependonthoseextras. No claim ismadeaboutreadingstepindices256..511 inrealcallers.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.145 instructioncomparisonsacross2930/2960/366A.3600sequences=widths128/256/304/319/320 ×bottom81..170 ×remap0/1 ×stackflaghigh0/1 ×sourcecolumn0/3.10800 originalfunctioninvocations. TestCS2000,DS=SS1048,source5000:0,destination7000:0. Everysequence comparesall65536destinationbytes andchecksreturnstate. Nohelperstubs orOSservices. Geometryissuppliedfromrecoveredformulas;5208/E4B2 arenotexecutedinthispass. Source64KBpatternandreversepalette arecontrolledfixtureassets.

Highbyteoflocalflag tested0/1 aspass35; noreportedfixtureoutputdifference arisesfromit. Actualcallerstackreachability remainsunknown. Pixelcomparisonhereisoriginalroutineversusindependentmodel,notoriginalgameversusremake/framecapture.

## Implementation-ready findings
Generateindependentstepandclippingtableswithexactcountsandrounding,thenusetheoriginalsplitinteger/fractionalcolumnadvance. Maintain16-bitpointerwrap,destinationstride320,paletteorderandlowBYTEstartY. TreatallowedindicesasTBDuntilcallerboundsareverifiedratherthanextendingtablesimplicitly.

## Unknowns and next test
Auditcallersforstepindexbounds;executeplanar3E44withVGAplanemodel;integrate5208andactualassets/frameconditions. WholegameSAVE/LOADfirstframe andWin16hardware/runtime comparisonremainopen.1551internalentries retainnativedecompilationsuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
Highfortestedgenerator-consumerbyteoutput;limitedforrealgameandhardwareconsequences.
