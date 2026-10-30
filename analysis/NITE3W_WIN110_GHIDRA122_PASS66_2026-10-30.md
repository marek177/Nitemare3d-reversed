# Win110 pass66 — low-stack exception object table and actual cleanup wrapper

## Finding
Confirmed, High for bytes and tested wrapper:static constructor4542 leaves near object41BC with far table1018:48E4. Its cleanup slot+4 at48E8 contains offset4612 and a selector relocation at48EA targetingNE1.65,536 executions of original4612 verify base-table reset and conditional delegation to5FD0.5FD0's body remains an intercepted boundary;no actual deallocation or Windows exception transfer is demonstrated.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|4542 calls036A then ultimately writes41BC/41BE=48E4/1018|Native constructor listing|High|
|Confirmed|Table slot+4 resolves to1000:4612|OriginalNE4 offset48E8 and selector relocation48EA→NE1|High|
|Confirmed|4612 rewrites object to base table1018:48BC|4619..461D;all flagWORD values|High|
|Confirmed|Delegates5FD0 iff argument low bit1|4622..4629,32768 delegated cases|High|
|Confirmed|ReturnAX is original object pointer;RETF4 removes arguments|462F..4633|High|
|Inferred|This is a polymorphic cleanup/destruction wrapper|Virtual call slot and base-table transition|Medium|
|Unknown|Actual memory release and runtime object ownership|5FD0/5B0C not executed|Low|

## Behavior model
Original constructor036A writes two base table values;4542 then writes48D0 followed by48E4 to the same object pointer. The last far table is used by the static low-stack payload41BC identified inpass64. Its cleanup slot is resolved using originalNE selector-chain metadata,not by treating raw chain-link words as loaded selectors.

4612 takes near object pointer andWORD flag,stores base table48BC:1018 into the first4 object bytes,and tests onlybit0 of the low argument byte. If set,it pushesobject and calls5FD0;callerPOP BX reclaims that single argument. The5FD0 returnAX is ignored;AX is reset from savedSI toobject. SI/BP restored andRETF4 completes. Even nonzero flags have no delegation;odd flags do. A generic flag!=0 reconstruction would differ. Static5FD0 itself forwards to5B0C;its actual resource effects remain unresolved here.

This distinguishes two guard levels:4446 tests the record-stateWORD as nonzero,then invokes the virtual cleanup with argument1.4612's own argument is a separate bitmask. The static payload from4564 is stored with record state0,so its ordinary4446 path does not call this cleanup. The table association does not prove the static41BC object is ever passed to5FD0 during real gameplay.

## Verification
All65536 argumentWORD values;object7000 with16 sentinel bytes;CS2000,DS1048,SS4000,SP D000. Match first4 output bytes to48BC/1018 and remaining12 unchanged;delegation count matchesflagbit0;argument at5FD0 call boundary isobject7000. Hook skips originalCALLF at4629,doesnot create a return frame or consume argument,andreturnsAXDEAD to demonstrate it is discarded. OriginalPOP BX then executes. CheckfinalAX7000,SP D008,BPE000,SI1234. Native instruction bytes normalized at461D(selector immediate) and4629(far target) to savedGhidra12.2 loaded listing;other instructions matchrawEXE. RawEXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Constructor association is static,not a newly executed constructor test. No fresh Ghidra database write claimed.

## Implementation-ready findings
Preserve base-table rewrite before conditional delegation,low-bit guard,caller cleanup of5FD0 argument,andreturn oforiginalobject. Keep record ownership/state distinct from cleanup-call flags. Mark actual5FD0 effects and construction/runtime registration provenanceTBD rather than replacing them with assumedfree behavior.

## Unknowns and next test
Execute5FD0→5B0C with allocator metadata boundaries documented,then inspect actual heap effects. Trace constructor4542 registration and whether any distinct-payload unwind can select this static object for cleanup. ActualWin16THROW/CATCH and whole-game parity remain open. Confidence High for table relocation and wrapper semantics;Medium for destructor label;Unknown for actual deallocation.
