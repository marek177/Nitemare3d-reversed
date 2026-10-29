# Win16 1.10 — Ghidra12.2 pass41: fatal diagnostic termination request

## Finding
Confirmed High:3118's static fatal chain ends bycalling38DB withstatus1.256 original38DB/commoncleanup executions reach directINT21 AH4C withALstatus. The servicehook stops atthatboundary; actualOStermination and3118's completeUI/cleanupchain were notexecuted. Pass40's returningdiagnostic remains an explicit counterfactual fixture, not evidence of normalfatalcontinuation.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|3118 optionallycalls2D9C(4),clears4BE2,callsE0C4(2)|311C..3139|High|
|Confirmed|Formats into512-byte stackbuffer,beeps30 andshowsFatalError messagebox|313C..316A|High|
|Confirmed|Calls0F64 then38DB withstatus1|316F..3176|High|
|Confirmed|38DB setsCX1,skips registeredcallbackrange4608..4688,andrequestsAH4C|38E5..395E|High|
|Confirmed|Directserviceexitcodes0..255 observed|256originalcases|High|
|Unknown|ActualWin16DOS3CALL exit,UIhelperbehavior andOSshutdown|Excluded|Low|

## Behavior model
Static3118 chain: optionaldisplaymodehelper,disablesoundflag4BE2,cleanupE0C4,format64C2,MessageBeep,MessageBox,0F64,termination38DB(1).38DB's modeCX0001 bypassesCL0registeredcallbackwalk;commoncleanuphandlesemptyranges and396B vectorrestoration,thenCH0requestsDOStermination. A normalnonreturningexitservice prevents caller6266 from continuing afterMAXSEG. The binaryhasreturninstructionsafterterminationrequest, but theirpresencealoneisnotproofOSreturns.

## Verification
EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.71instructioncomparisons; unreachableimportCALLFnormalizedfromnativelisting.256 original38DB/commonhelpercases,allbyteexitstatuses. TestCS3000,DS=SS1048,CS370Ebit0clear,20D2callbackcount0. Vectorpointer0850 supplied5000:1234. INT21hook validatesAX2500vectorrestorethenAX4C00+status andstops. Registeredcallbacktablefilledwithinvalidsentinels yetnotcalled,confirmingmodebypass. Nohelperstubs insideexecutedterminationchain. OSserviceboundaryis simulated; noactualprocesswasterminated.

## Implementation-ready findings
Treat3118asanintendedfatalpath requestingexit1,notarecoverablediagnosticbydefault. Keeppriorcapacity/shortreadexperiments' returningdiagnosticconditionexplicit. ThisfindingsupportscontrolflowintentbutdoesnotclosefullWin16terminationparityorallcleanupsideeffects.

## Unknowns and next test
Execute3118withcontrolledUIimports andoriginalcleanup,verifyDOS3CALLrouteanddynamic20D2callback. RecoverB1A4mode0andupstreamrenderendpointconstraints. ActualWin16frame/gameplayparityremainopen.1551internalentries retainnativedecompilesuccess,310EXTERNALentries separate;1401undefinedexecutablebytes remainunresolved.

## Confidence
Highforstaticfatalcallchainandtesteddirectterminationrequest;limitedforactualOS/UIbehavior.
