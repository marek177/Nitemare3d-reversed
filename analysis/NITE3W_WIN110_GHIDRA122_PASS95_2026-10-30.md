# Nitemare3D Win16 1.10 — pass95, 2026-10-30

## Finding
Confirmed: 1000:6118 initializes a map with 17 buckets (initially unallocated) and caller-selected block size. Original map insertion now has integrated microexecution evidence from construction through bucket creation, three node-block allocations, collisions, removal and reuse. Preserved Ghidra12.2 native export plus original EXE in Unicorn; no fresh Ghidra run and no live Win16 game execution.

## Evidence
| Status | Claim | Source and location | Confidence | Reason |
|---|---|---|---|---|
| Confirmed | Constructor sets vtable4990:1018; map+4=0, +6=17, +8/+A/+C=0, +E=caller argument. Returns map address. | 1000:6118–614E | High | Original constructor executed for block sizes1..64. |
| Confirmed | Caller2930 creates first map at object+0 with block count10, second at object+10 with block count4, then initializes second to7 buckets. | 2938–2950 | High for static call arguments | Listing directly shows pushes10/4/7 and receiver arithmetic; caller not executed in this pass. |
| Confirmed | First insertion creates a zeroed34-byte bucket array and first node block. Existing keys retain slot/value without extra allocation. | 62F4→6280/6152/61EC/42D0; original6CAC | High | Poisoned allocator buffers distinguish original zero-fill from fixture content. |
| Confirmed | Collision insertion prepends bucket chain. Removal followed by LIFO reinsertion reuses corresponding value slots, zeroing values without allocating. | 62F4/6356/6266/61EC | High | 64 integrated sequences with all keys deliberately hashing to bucket0. |
| Unknown | Runtime identity of both2930 maps, actual allocation failure behavior, arbitrary constructor argument reachability. | Not established | — | Static layout and bounded successful fixtures do not prove object roles or Windows behavior. |

## Behavior model
Constructor6118 accepts `(map,blockCount)` as stack words and returns AX=map, RETF4. Lazy insertion computes `(key>>4)%bucketCount` before allocation. With default17 buckets, key sequence `272*i` produces collisions at bucket0. Bucket storage is allocated and zero-filled once. Node blocks use size `8*blockCount+6`. New node becomes bucket head with bucket index at+2, key at+4 and zero value at+6; existing-key insertion returns the existing value address unchanged. Removing alternating keys and reinserting in reverse removal order reuses the original slots.

## Verification
**64 sequences / 12,800 original calls**, block counts1..64. Each sequence executes constructor, inserts2*n+1 distinct colliding keys (three blocks), revisits every key/value, removes alternating keys, and reinserts them in reverse order. Checks include bucket zero-fill, head pointers, exact slot addresses, key/bucket fields, active counts, allocation event count, value preservation/reset and stack/BP restoration.

Original routines6118/62F4/6280/6152/61EC/42D0/6356/6266/6CAC execute. Only free call6161 and allocator calls6174/42E1 are intercepted before CALLF, with cdecl arguments retained. Free receives0; allocations return disjoint synthetic5000/6000/7000/8000 buffers prefilledA5. DS=SS1048 allows original near-pointer stack outputs; code selectors normalized at6308/631D/6323/639F/6207→2000 and6184/6249/6259→3000. DF0. No real allocator, heap exception or Windows API effects.

EXE SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; NE1 file04C0, NE2 fileE8A0. Sources: native_listing.json, verification.json, verify_integrated_map.py, baseline48/pass48-results/listing.tsv.

## Implementation-ready findings
Represent constructor block count separately from bucket count: default17 buckets does not imply17 nodes per block. Caller2930 explicitly uses `(block10,buckets17)` and `(block4,buckets7)` for its adjacent maps. Preserve lazy allocation and existing-value semantics. The integrated successful path is verified for the stated bounded fixtures; zero counts, out-of-memory and actual application map roles remain TBD.

## Unknowns and next test
Trace callers2930 and global4250 initialization to establish which map holds HWND associations. Test actual block10/bucket17 and block4/bucket7 constructor paths with their surrounding object initialization. Inspect destructive map cleanup and block freeing to complete lifecycle evidence.

## Confidence
High for static constructor arguments and bounded integrated map operations; no claim of full application or game parity.
