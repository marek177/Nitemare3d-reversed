# Win110 pass67 — original cleanup chain to LOCALFREE boundary

## Finding
Confirmed, High at the import boundary:65,568 cases verify5FD0→5B0C plus integrated4612 cleanup. Nonzero values are forwarded once to importedLOCALFREE;zero skips it. Direct5FD0 preserves the API returnAX,whereas4612 restoresAX to the original object pointer regardless of that API result. Actual Windows heap release remainsUnknown.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|5FD0 forwards its WORD argument to5B0C|5FD0..5FDE|High|
|Confirmed|5B0C calls nativeLOCALFREE0010 iff argument!=0|5B11..5B1F;all65536 values|High|
|Confirmed|5B0C restoresDS from its stack save|5B10/5B22;stub deliberately changesDS|High|
|Confirmed|4612 returns object pointer independent of API result|24 integrated cases|High|
|Unknown|Actual LocalFree validity,return behavior and heap effects|API stub only|Low|

## Behavior model
5FD0 pushes the argument and calls5B0C;its MOV SP,BP discards the forwarded argument beforefar return.5B0C savesDS,comparesWORD argument with0,andfor nonzero pushes it to importedLOCALFREE. It restoresDS andBP beforeRETF without overridingAX. The caller still owns its original argument. Thus direct5FD0 withnull does not promiseAX0:with initialAXABCD it returnsABCD because no API call writesAX. With nonzero input the selectedAPI return propagates through these two wrappers.

In the original4612 chain,theobject table is first reset to1018:48BC. Odd cleanup flags execute5FD0→5B0C→LOCALFREE;even flags skip delegation. Then4612 overwritesAX with savedSI(object) andRETF4 consumes its two arguments. Therefore cleanup-return success/failure is not surfaced by this wrapper. Whether callers depend on any real API result remainsunresolved.

## Verification
65,536 direct5FD0 cases exhaust argumentWORD0..FFFF withAPIreturn0.8 additional directcases useAPIreturnFFFF atselectedpointer values including0.24 integratedcases=8 flags0/1/2/3/80/FF/FFFE/FFFF ×3APIreturns0/1/FFFF atobject7000. Total65,568. CS2000 containsNE1 cleanup;CS3000 containsNE2 wrappers;DS1048,SS4000,SP D000. Internal far-call selectors relocated for these testCS values;461D table-selector immediate normalized to native1018. No native wrapper replaced. Hook interceptsLOCALFREE beforeCALLF at5B1A,checksargument,pops2bytes as documentedharness assumption,returnsselectedAX,setsDS5000,and resumes5B1F. OriginalDS restore executes. It performs no heap mutation. Counts,AX,SP,BP,SI where applicable,and16objectbytes checked. Full directwrapper leavescallerargument onstack(SPD004);4612 consumesarguments(SPD008). OriginalEXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. ExistingGhidra12.2 native import name/listing supplies static target evidence;no fresh Ghidra database run or real Windows execution claimed.

## Implementation-ready findings
Keep null guard,value forwarding,andwrapper-specific return semantics.5FD0/5B0C are not a custom heap algorithm in the executed path:they delegate toLOCALFREE. Do not claim real handle validation or releasedmemory from the no-effect stub. Keep flagbit0 semantics from4612 distinct from arbitrarynonzero tests. RestoringDS is observed original behavior,whilethe stub's clobber is deliberatelyadversarial test input,not a claim thatWindowsdoes so.

## Unknowns and next test
ActualLocalFree semantics andheap state requireWindows runtime. Staticconstructor/payloadownership,initializer registration,andotherexceptionroutes remainopen. Next:trace41BC constructionregistration andverifyrecord+6 callback path without conflatingitwithTHROW. ConfidenceHigh fororiginalwrappercontrolandreturncontract;UnknownforactualOSmemoryeffects. No full-gameparity claim.
