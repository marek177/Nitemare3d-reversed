# Win16 1.10 — Ghidra12.2 pass40: segment run builder

## Finding
Confirmed High:513 controlledcases execute original6266 withoriginal6152. Contiguous equalnonzero pointers collapse into20-byte records withinclusiveXbounds. A diagnostic occurs at50runs,notonlyabove50; ifthe diagnosticreturns,51strun isstillwritten. Actualfataltermination andrealcapacitysafetyarenotestablished.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Runidentity comparesoffsetandselectorWORDs|6297..62A1|High|
|Confirmed|Eachnewrun storesstartX andcallsB1A4(mode0,farobject)|62D3..62F1|High|
|Confirmed|Previousrun closesatcurrentX-1 andcallsoriginal6152|62AA..62D0|High|
|Confirmed|Countincrement precedes signedcount>=50diagnostic|62F4..6309|High|
|Confirmed|Finalrun closesafterloopwithoriginal6152|6320..6340|High|
|Unknown|Real3118termination,initialnullpointerandemptyviewportbehavior|Excluded/stubbed|Low|

## Behavior model
Reset5E7E=0,recordpointer5E88. Scanper-columnfararray53FE+4*x from53E4through53E6inclusive. Onpointerchange,finalizepreviousrun ifcountexists,advancerecordby20,thenstartnewrunandcallB1A4mode0. Incrementcount;count>=50calls3118(MAXSEG,50). Afterloop,finalizecurrentrununconditionally. Thislaststepmakesinitialnull/emptyviewport behavioraseparatequestion; no validinputassumptionis silentlyadded.

For flatendpointfixtures(10,1400)→(20,1400),original6152 fillsheights1400,step0,accumulatorhigh120 at53F0=1280. Equalpointersmerge; recurringpointerafteranotherpointercreatesanewrun,notaglobaldeduplication.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.190 instructioncomparisonsbeforecontrolledfarselectorrelocation.513cases:all510 binarypointerpatterns oflength1..8,plus49/50/51distinctrunscenarios. Pointersnonzero inselector5000,offset1000+32*identity;selectorcomparisonisconfirmedstaticallybutselectoronlydifferencesarenotseparatefixtures. Original6266and6152execute;B1A4and3118areRETFstubswithargument/callchecks. Diagnosticdeliberatelyreturns. Check52×20Boutputregionincludingunchangedtrailingrecords,count,runstart/end,callbacksequence,SP/BP. TestCS2000,DS=SS1048.

Boundarydiagnosticcounts:49runs→0,50→1,51→2. Thisisnotproofthatactualgamecontinuespastitsdiagnostic. B1A4sideeffectsareexcluded,soempty/nullrecordbehaviorisnotgeneralizedfromthisharness.

## Implementation-ready findings
Preservecontiguousrunsemantics,inclusivebounds,20-byte stride,finalizationorderandthreshold50. Do nottreatdiagnosticcallaloneasaguaranteedboundscheckwithoutrecovering3118termination. Segmentrecordformationisnowverifiedwithitsactualinitializerforthesecontrolledinputs.

## Unknowns and next test
RecoverB1A4mode0and3118fatalpolicy;traceupstreamper-columnpointer/endpointproductionandheightconstraints. PlanarrendererandactualWin16frameparityremainopen.1551internalentries retainnativedecompilesuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
Highfortestedrunformationandconditionaldiagnosticcontinuation,limitedforwholeenginecapacityandreachability.
