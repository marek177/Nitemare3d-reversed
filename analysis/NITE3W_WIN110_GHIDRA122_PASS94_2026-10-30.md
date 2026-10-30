# Nitemare3D Win16 1.10 — pass94, 2026-10-30

## Finding
Confirmed: original 1000:61EC expands an empty free list through 1000:42D0, builds eight-byte nodes after a six-byte block header, then returns nodes in ascending address order. This pass uses preserved Ghidra12.2 exports and original EXE machine code in Unicorn; no fresh Ghidra database run or live Windows/game execution.

## Evidence
| Status | Claim | Source and location | Confidence | Reason |
|---|---|---|---|---|
| Confirmed | Empty map+0A triggers block allocation using map+0E elements of size8 and block-list address map+0C. | 61F5–6204; verify_map_expansion.py | High | Native listing and executed code agree. |
| Confirmed | Header is old block head, count, zero at offsets0,2,4; nodes begin at block+6. | 42D0; 620B–6238 | High | Three expansions per sequence, header and full remaining free chain checked after every allocation. |
| Confirmed | Free-list construction visits nodes backwards; allocation returns them forwards with stride8. | 6221–6238 | High | Counts1..128, even/odd block bases, two complete drains and third expansion. |
| Confirmed | Allocation increments map+8 modulo65536 and clears node+4 and node+6. Node+2 remains A5A5 in the fixture. | 623B–625B; original1008:6CAC | High | Initialized poison bytes distinguish writes from untouched fields. |
| Unknown | Zero/high block-count behavior, genuine heap failure and which constructors supply these counts. | Not exercised | — | Successful bounded allocation fixture only. |

## Behavior model
For positive bounded count n and successful block address B, 42D0 prepends header `(oldBlockHead,n,0)` to map+0C. 61EC creates `B+6 -> B+14 -> ... -> B+6+8*(n-1) -> 0`, removes its head, increments map+8, clears returned node words+4/+6, and returns its address in AX. Subsequent calls use the remaining free list without allocating. After exhaustion another block is prepended to the block list. The returned node's next word is not cleared and can retain its old free-list successor; callers may overwrite it.

## Verification and limits
256 sequences, **33,280 original calls**, 768 simulated successful allocations. Each sequence makes 2*n+1 calls, covering two full blocks and the first node of a third. Initial active countFFFF verifies wraparound. BP/SI/DI and RETF2 stack restoration checked. Original61EC/42D0/6CAC executed; only allocator call at1000:42E1 is intercepted before CALLF, preserving cdecl arguments for original cleanup. Internal selector operands6207/6249/6259 are normalized to synthetic code segments2000/3000. DS1048, SS4000, DF0, synthetic mapped memory.

EXE SHA256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. NE1 file04C0; NE2 fileE8A0. Sources: baseline48/pass48-results/listing.tsv; native_listing.json; verification.json; reproducible script.

## Implementation-ready findings
Under the tested positive bounded precondition, use six-byte block headers and eight-byte nodes; map+08 active count, +0A free head, +0C allocated-block head, +0E block element count. Do not clear node+2 in the model for61EC. The full map insertion path supplies bucket/key fields separately. This result establishes container memory behavior, not game-visible behavior or allocator failure semantics.

## Unknowns and next test
Trace constructors/callers setting map+0E and inspect whether zero or large values can occur. Then execute a bounded integrated62F4 insertion with bucket creation and block expansion together, followed by collision removal/reuse. Actual Windows allocation and exception behavior remain separate tests.

## Confidence
High for the stated bounded microexecution behavior; unsupported outside those preconditions.
