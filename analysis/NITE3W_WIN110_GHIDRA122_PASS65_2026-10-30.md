# Win110 pass65 — exception record push/pop lifecycle

## Finding
Confirmed, High within controlled cleanup boundaries:65,811 original function calls verify4422 registration and4446 removal. Normal removal updates head41B8 but leaves removed-record bytes unchanged. This differs from4492 rethrow unlinking,which explicitly clears link/payload. Virtual cleanup executes only when both payload+2 andflag+4 are nonzero;the actual cleanup body remainsUnknown.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|4422 zeros+2/+4/+6,links previous at+0,and installs head|4422..4443,nested chain checks|High|
|Confirmed|4422 preserves bytes+8 onward and returnsrecordAX|24-byte record sentinel fixtures|High|
|Confirmed|4446 invokes cleanup iff payload andflag nonzero|All65536 flag values withpayload7000;3 zero-payload cases|High|
|Confirmed|Normal removal preserves record bytes and advances head|4446..4471,full record comparisons|High|
|Unknown|Cleanup destructor semantics and actual exception transfer|Stub/no Win16 transfer|Low|

## Behavior model
4422 accepts a near record pointer,clears three control WORDs at+2/+4/+6,copies currenthead41B8 into+0,then setshead to the new record. It returnsAX=record andRETF2 consumes the pointer argument. The area+8 onward is preserved for later path-specific data rather than initialized here.

4446 assumes a valid head. Ifrecord+2 and+4 are nonzero,it pushes1 andpayload,loads a far table pointer from the payload object,and invokes the far target atES:[BX+4]. Native encoding26FF5F04 includes explicitES override even though the exported instruction text omits it. A synthetic callbackRETf4 consumes these4 argument bytes and preserves other state. Then4446 uses originalSI to loadprevious intohead,pops savedSI/DI,andRETF. It does not clear removed+0/+2/+4. The unchanged-record finding is conditional on the no-effect cleanup stub;actual cleanup could change external data.

Do not merge this normal-pop behavior with4492 rethrow:pass64 observed that route clearingold+2 andold+0 while changinghead. Different state cleanup at these entry points is evidence,not an inconsistency to normalize away.

## Verification
65,536 pop cases exhaust allflagWORD values withpayload7000;3 more pop cases usepayload0 andflags0/1/FFFF. Nested chains ofdepth1..16 contribute136 original4422 calls and136 original4446 calls:272 calls,total65,811. Each push verifies first8 bytes,16 sentinel bytes after+8,AX,SP,andBP. Each nested pop verifies exact removed bytes and previoushead. Virtual-pop cases verify invocation count,stack arguments(payload7000,1),head,removed24-byte record,andSP/SI/DI restoration. DS1048,SS4000 distinct,CS2000,SP D000. No real CATCH/THROW or OS call. Synthetic virtual callback at2000:E000 executesCA0400 RETF4;its return convention is a declared harness assumption,not recovered cleanup implementation. Native4422..4471 encodings checked against originalEXE and preservedGhidra12.2 listing. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. No fresh Ghidra database update or whole-game parity claim.

## Implementation-ready findings
Use separate register,pop,andrethrow operations. Preserve+8 data on registration;normal pop alone must not zero the removed node. Model both payload/flag guards,correctES-based virtual call,andcallee argument cleanup explicitly. Keep semantic ownership/destructor labels provisional until target recovery.

## Unknowns and next test
Identify payload41BC's table andactualcleanup target,trace field+6 callback records,andtest real Windows transfer when available. Empty-head4446 behavior,aliasing records,andcleanup side effects excluded. Confidence High for direct instruction lifecycle and guarded call setup;Unknown for actual virtual cleanup and Windows exception behavior.
