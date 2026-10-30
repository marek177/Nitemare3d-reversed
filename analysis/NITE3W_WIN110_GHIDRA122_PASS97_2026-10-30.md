# Nitemare3D Win16 1.10 — pass97, 2026-10-30

## Finding
Confirmed:1000:2A26 performs object-value cleanup separately from generic map cleanup. It enumerates the owner's second map at+10, clears an object field, dispatches virtual+4 with flag1 for non-null values, then clears the second map. Original63AE iterator now has integrated execution evidence. This uses preserved Ghidra12.2 exports and original EXE in Unicorn, not fresh Ghidra or live Windows/game execution.

## Evidence
| Status | Claim | Source and location | Confidence | Reason |
|---|---|---|---|---|
| Confirmed | Owner+18 (second map active count) selects initial cursorFFFF if nonzero,0 otherwise. |2A2F–2A36|High|Native CMP/CMC/SBB plus empty/nonempty executions.|
| Confirmed |63AE enumerates bucket order ascending, following node.next within a bucket; returns value and key and advances cursor. |63AE–6416|High within valid nonempty cursor precondition|Collision/spread fixtures exercise next-chain and next-bucket paths.|
| Confirmed |Before virtual call, writes zero word at value+owner+22; only mode owner+24==2 also zeros following word. |2A50–2A69|High|Modes1/2/FFFF, poison fields and callback-time assertions.|
| Confirmed |Non-null values receive virtual+4(value,1), then6196 clears owner+10 after enumeration. First map untouched in fixtures. |2A6C–2A83|High|198 original top-level executions with callback/free event order checks.|
| Inferred |This is cleanup of temporary/owned wrapper objects, while first map supports persistent associations. |Separate value loop, adjacent maps from2930, HWND map4250 evidence from prior passes|Medium|Actual owner type and runtime value classes not established here.|
| Unknown |Actual virtual destructor bodies, callback-induced mutations, null-value field clearing side effects, corrupt cursor behavior. |Not executed|—|Synthetic non-null values and inert callback stubs only.|

## Behavior model
2A26 uses a cursor initialized toFFFF for nonempty second map.63AE obtains first occupied bucket or supplied node cursor, computes the successor (node.next or first node in a later bucket), writes successor cursor, then returns current node.key and node.value through near output pointers.2A26 clears a configured member in that value before checking value!=0. It calls virtual slot+4 with flag1 for nonzero values. After the cursor becomes0, it calls6196 on owner+10. Generic6196 alone has no object callback, so ownership behavior belongs to this surrounding routine.

Important boundary: the native zero-value check comes after the configured-member write. This pass deliberately uses only non-null values and does not claim safe null handling.63AE has a valid-current-node precondition; it is not tested as a general empty iterator entry.

## Verification
**198 cases**: counts0..32,7 buckets, all-collision versus distributed layout, field width modes1/2/FFFF. Original2A26/63AE/6196/4302 execute. Virtual call2A75 intercepted before CALLF with callee argument consumption4 bytes; free calls61A0/430F intercepted with cdecl args retained. Objects have poisonAAAA/BBBB at configured member+14/+16. Callback checks confirm only mode2 clears both words. Expected callback order precedes bucket and block release; first16-byte map remains unchanged. DS=SS1048 for near pointers to stack outputs, CS2000, normalized internal selectors2A4E/2A86/61BB. No actual destructor/free or Windows behavior.

EXE SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; NE1 file04C0. Sources:verify_owned_map_cleanup.py,verification.json,native_evidence.json,baseline48/pass48-results/listing.tsv and references.tsv.

## Ownership and destructor references
Direct references to61C8 include27C6,3442,6420,1008:0EFA;6196 additionally called by2A26.27C6 statically destroys global4260 then4250 before other global cleanup.6420 statically invokes61C8 and conditionally5FD0 when deletion-flag low bit is1. These are static call-path findings, not executed in this pass; no claim of full program shutdown validation.

## Implementation-ready findings
Separate generic map storage teardown from value-object cleanup. Preserve callback ordering: member clear, virtual+4(value,1), then container clear after all entries. Enumerator order is bucket ascending and chain order. Width condition is exact equality2; other tested modes clear one word. Treat null values and reentrant mutation as TBD, not validated behavior.

## Unknowns and next test
Trace owner constructor arguments+22/+24 and value factories to identify the cleared member and concrete class. Execute deleting wrapper6420 with flag boundaries and then actual candidate value destructors. Establish if temporary map entries can contain zero or be mutated by destructor callbacks.

## Confidence
High for the tested normal enumeration and member-clear/callback ordering; Medium for temporary/owning map interpretation.
