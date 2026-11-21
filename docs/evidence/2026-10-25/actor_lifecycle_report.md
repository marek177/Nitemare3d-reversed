# Actor construction and count-writer scope

## Evidence

This follow-up uses the same hash-pinned DOS2 source5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3 and the prior original33-record snapshot. The live session was independently revalidated stopped at1401:0382, revision197, with no breakpoints. No new constructor runtime invocation, count-changing runtime test or guest write was performed in this follow-up.

A scan of unique inherited instruction sites finds26 explicit absolute memory references to displacement6276. Two have a write access:0AEA:096E and0AEA:0A88, both within0958. The other24 are reads/comparisons/pushes. The scan is bounded by inherited instruction membership and explicit operands; register-derived aliases, implicit string operations, bulk save/load writes and unknown code are not closed. It does not prove that these are the only possible writes to the live physical address.

## Construction ordering

0AEA:0958 sets SI=0 and stores it to DS6276 at096E. In its object-building path it tests object flag byte05 bit08. For actor-bearing objects it checks signed count against100 and calls0FBA:000C when count>=100. The global termination contract of that diagnostic call is not proved here; local following bytes do not themselves skip construction if it returns.

At0A5C it stores the low byte of the current count into object byte07. At0A84 it pushes the old count as the actor-slot argument;0A88 increments count;0A8C calls04C7:1692. Across the inherited instruction membership, this is the one literal FAR call site to that constructor. This is construction order, not a natural spawn/remove or reentrant gameplay observation.

## Bounded constructor contracts

Exact spans04C7:1660..1691 and1692..1706 contain62 instructions whose lengths independently agree in Capstone5.0.9 and iced-x86 1.21.0. The local1692 body computes actor offset264E+26*slot modulo16 bits, writes dword02=0, word06=0, word08=object-index argument, byte0D=0 and byte10=FF. It calls lookup00F7:0176 on a dword from the supplied object pointer; a result other thanFFFF stores AL in actor byte0E. A FFFF result skips that local store. Later callees and preexisting byte contents remain relevant; this is not a claim that the final byte is necessarily stale or that a reachable bug exists.

The local body subsequently calls04C7:1660 and083D:117A. The1660 helper writes byte11=(low-byte argument &3)*2 and bytes13/14 from DS tables0B2E/0B36 shifted left3 modulo256. All field offsets in this report are hexadecimal. These writes show partial local initialization; whole-record/callee effects are not closed. The constructor's local FAR return leaves argument cleanup to the caller and restores SI/DI/BP.

## Reciprocal runtime endpoints

For every one of the33 actor records in the prior original snapshot, actor word08 identifies the captured28-byte object record; that object's byte07 equals the actor slot0..32 and its byte05 has bit08 set. This matches the observed static construction linkage. This is endpoint consistency: it does not establish how the constructor executed earlier, generation checks, transient rebinding, or same-slot ABA safety.

The earlier live-count loop proof remains valid:04C7:12B6 reloads DS6276 after each callback. However, a live reload by itself does not establish that actor count naturally changes during that callback. The direct writer evidence currently points to map construction. Actor construction, referenced object records and mutable gameplay-slot pools must be treated as distinct lifecycle questions until alias/callee and runtime evidence connects them.

## Remaining work

Trace the actual mutable OBJECT/projectile slot allocation, activation, removal and reuse paths rather than assume they mutate actor count. Recover register/implicit/bulk writers and save/load restoration for DS6276 and actor references. Exercise any demonstrated reentrant paths, remaining actor states and paired original/remake writer order. Global function boundaries, indirect domains, Win16 runtime and P0 parity remain unfinished.

Public files contain scope, numeric links and bounded analysis only. Original arrays, assets, binaries and raw instruction traces remain in the local checkpoint.

