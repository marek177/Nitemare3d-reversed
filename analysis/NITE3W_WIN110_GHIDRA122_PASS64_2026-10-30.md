# Win110 pass64 — exception record preparation and rethrow unlinking

## Finding
Confirmed, High before the Windows boundary:65,542 cases verify original4492 state changes and4564's low-stack wrapper up toTHROW call451E. An empty record receives payload at+2 and boolean inverse of caller flag at+4. Rethrowing a current payload unlinks its record and passes the payload to the next empty record. Actual Windows THROW/CATCH transfer remainsUnknown.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Head pointer isDS41B8; record+0 links previous|4492 native instructions|High|
|Confirmed|Empty record gets argumentBP+8 at+2,boolean(flag==0) at+4|4506..4514;all65536 flag words|High|
|Confirmed|THROW call-site stack contains1,record+8,DS|4517..451E capture|High|
|Confirmed|Rethrow clears old+2,updates global head to old+0,clears old+0|44A3..44FC;3 cases|High|
|Confirmed|4564 supplies payload41BC,flag1;record+4 becomes0|3 wrapper fixtures|High|
|Unknown|Actual exception transfer,destructor behavior,callback bodies|Not executed|Low|

## Behavior model
4492 is a frame-chain traversal with multiple paths. The executed empty-record route requireshead nonzero,record+2 zero,andrecord+6 zero. It stores the nonzero payload,normalizes caller flag to its boolean inverse,and pushesDS,record+8,and1 before importedTHROW. The test stops at451E beforeCALLF. If the real import unexpectedly returned,the following callback route would be relevant;this is not executed or modeled as an ordinary return.

Payload argument0 selects rethrow preparation:read payload andflag from current head. The same-payload comparison skips the distinct-payload cleanup call. Original code clearscurrent+2,loadshead=current+0,clearscurrent+0,andloops. A next empty record receives the original payload and normalized nonzero status of the oldflag. This proves linkage and numeric state transitions,not ownership/destructor semantics.

Original4564 pushes41BC then1 and calls4492. Its observed output record containspayload41BC,flag0. This connects pass63's rejection call site to a concrete exception payload without executing Windows transfer or naming the payload class. Three wrapper fixtures vary an otherwise unused trailing caller-stack word;they are repetition/robustness checks,not three different exception semantics.

## Verification
65,536 caller flags0..FFFF withpayload41BC and one empty record;3 rethrows withold flags0/1/FFFF,current record6000 and next6100,payload1234;3 original4564 wrapper runs. CS2000,DS1048,SS4000,entrySP D000. Data and stack distinct. Entire relevant record prefix and global head checked;THROW stack arguments checked for exhaustive empty-record cases. No OS/helper stubs:execution stops beforeTHROW,callback4524,or empty-head452A call site. The tested cases reachTHROW only. InternalCALLF4492 selector at456C relocated to testCS2000. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Original bytes and preservedGhidra12.2 listing are primary static evidence;no fresh database update or full-game runtime claimed.

## Implementation-ready findings
Represent the observed record prefix aspreviousWORD+0,payloadWORD+2,boolean stateWORD+4,routeWORD+6;interpretation of the remainder ispath-dependent andTBD. Preserve boolean normalization for allnonzero WORD values rather than copying the caller flag verbatim. On observed rethrow unlink both payload and previous link in the removed record. Keep the distinct-payload cleanup and callback paths separate until their indirect targets/contracts are recovered.

## Unknowns and next test
Decode payload41BC and its producers,trace4422/4446 record lifecycle,and inspect actual CATCH/THROW boundary in Win16. Empty-head handlerDS0510,distinct payload destruction,andcallback record+6 routes remain unresolved. Confidence High for numeric/link state and wrapper;Unknown for actual Windows transfer and ownership semantics. No1:1 game-parity or completion percentage claimed.
