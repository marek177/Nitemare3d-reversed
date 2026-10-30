# Win110 pass60 — original stack allocator39F2 contract

## Finding
Confirmed, High in controlled original-instruction execution:66,184 cases verify allocation rounding,lower-bound checks,SS-relative low-water update,far-return relocation,and failure routing. The requestFFFF wraps to rounded size0; it does not request65536 bytes. This is a verified edge case,not a demonstrated reachable game defect.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Rounded size=wrap16(request+1)&FFFE|39F4..39F5;all65536 request words|High|
|Confirmed|Success requires rounded<post-popSP and newSP>=SS000A|39F7..3A02|High|
|Confirmed|SS000C becomes min(old,newSP) on success|3A04..3A0B;distinctDS/SS fixtures|High|
|Confirmed|Failure selects default fatal or indirect far handler viaDS08B0|3A14..3A22;204 alternate-entry cases|High|
|Unknown|Real callers ever requestFFFF or activate alternate handler|Not established|Low|

## Behavior model
39F2 pops the far return offset intoBX and selector intoDX. Letbase beSP after these pops. AX increments modulo16 bits and clears its low bit. If rounded>=base,allocation fails. OtherwiseAX becomes base-rounded by NEG after SUB. NewAX must be at least theWORD floor atSS000A. If valid,the routine lowersSS000C only when its prior unsigned value exceeds newAX,setsSP=newAX,pushes the saved selector/offset,andRETF. Successful callerSP is therefore base-rounded. The original far return is copied onto the new stack location; the test executes that return to a synthetic boundary.

On failure the already-popped return frame is not reconstructed before dispatch. DS08B0 offsetFFFF selects fatal3C3D withAX0. OtherwiseJMPF[DS08B0] transfers to the configured alternate handler withSP=base. The alternate body is not executed. DS andSS are deliberately different:DS1048,SS4000. Guard bytes atDS000A..000D remain unchanged whileSS000C is updated. This separates data-segment assumptions from the verified stack-segment operands.

## Verification
65,536 request values atbaseD000,floor1000,previous minimumFFFF. Additional648 boundary cases=4 baseSP values2000/8000/D000/FFF0 ×9 requests0/1/2/3/16/100/1000/FFFE/FFFF ×3 floors ×3 previous minima ×2 handler modes. Floors include base and prospective newSP+1 (clamped tosafe1000..FFFF);previous minima800,base,FFFF. Combined outcomes49,394 returns,16,586 default-fatal handoffs,204 alternate-handler entries. Every case checks destination,SP,BP,DS,SS low-water value,and DS guard bytes;successAX or default-fatalAX also checked. No helper/OS stubs. No actual handler body or Windows stack exception executed.

Native39F2..3A24 instruction encodings checked against original NE2 bytes and preserved Ghidra12.2 listing. EXE SHA25612fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. CS2000,DS1048,SS4000. No code-byte relocation needed in this range. This is microexecution of original code,not a fresh Ghidra database analysis,full-game runtime,or proof of actual memory exhaustion.

## Implementation-ready findings
Use16-bit wrapping before even rounding;requestFFFF maps0,request1 maps2. Equality at the floor is allowed,but rounded==base fails. Keep minimumSP and floor inSS,handler pointer inDS. Preserve the special stack-moving far-return convention instead of modeling39F2 as an ordinary function returning a heap pointer. Do not changeFFFF handling without explicitly accepting a parity difference.

## Unknowns and next test
Caller request constraints,SS control-word initialization,alternate-handler installation,and actual Win16 stack behavior remain open. Next audit traces references toSS000A/000C andDS08B0. Confidence High for tested instruction contract;Unknown for whole-game reachability and OS behavior. Test counts do not measure semantic completeness.
