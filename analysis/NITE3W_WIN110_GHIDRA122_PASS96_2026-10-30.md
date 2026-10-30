# Nitemare3D Win16 1.10 — pass96, 2026-10-30

## Finding
Confirmed: 1000:6196 clears map storage while preserving bucket count and block size; 1000:61C8 surrounds that operation with map/base vtable writes. Original4302 walks and frees the block chain after saving each successor. This is machine-code microexecution using preserved Ghidra12.2 exports, not a fresh Ghidra run or live Windows execution.

## Evidence
| Status | Claim | Source and location | Confidence | Reason |
|---|---|---|---|---|
| Confirmed | Calls5FD0 on map+4, then sets +4/+8/+A to0. | 619D–61B0 | High | Listing and event-time snapshots from original execution. |
| Confirmed | Passes map+0C to4302, clears map+0C after it returns. | 61B5–61BD | High | Original helper executed for 0..64 blocks; head remains old during block frees. |
| Confirmed | Reads successor before calling free and follows saved successor afterwards. | 430C–4317 | High | Stub poisons freed16-byte storage including old next link; original traversal still follows the expected order. |
| Confirmed | +6 bucket count and +E block size survive; repeated clearing passes null to5FD0 and frees no blocks. | 6196/4302 | High | 520 paired sequences, including empty maps. |
| Confirmed |61C8 writes4990:1018 before cleanup and48BC:1018 after normal return. | 61CF–61E2 | High | Static writes plus final vtable checks. |
| Inferred |61C8 is the map destructor body. | Vtable transition and cleanup sequence | Medium | Behavior strongly supports destructor role; deleting wrapper/whole program lifecycle not executed here. |
| Unknown | Real allocator return effects, exception interruption, cyclic/corrupt block chains. | Not exercised | — | Synthetic successful free callbacks and bounded acyclic fixtures only. |

## Behavior model
`clear(map)` calls free(map.bucketArray), zeros bucketArray/activeCount/freeHead, calls freeBlocks(map.blockHead), then zeros blockHead. It preserves bucketCount and blockCount. `freeBlocks(head)` repeatedly saves next=[head], calls free(head), and advances using saved next. It does not need intact storage after free returns. Cleanup order is buckets first, then blocks in linked-list order.61C8 changes vtable to map type before this operation and base type afterwards. No explicit value destructor or per-node callback appears in these routines.

## Verification
**520 sequences / 1,040 original calls**, with **17,680 free-call interceptions**. Fixtures use0..64 blocks, ordered/shuffled links, null/non-null bucket array, both6196 and61C8 entries, followed by a second cleanup. Checked free order, fields at each callback, preserved configuration, final vtable, BP/SI/DI and RETF2 stack restoration. Every non-null freed pointer is overwritten withDD bytes to test saved-successor traversal. This poison operation is a test fixture, not an asserted behavior of the real heap.

Only callsites61A0/430F to1008:5FD0 are stubbed before CALLF; cdecl arguments remain for original POP. Internal CALL selectors61BB/61DC normalized to synthetic2000. Vtable selector immediates61D6/61E5 normalized to1018 from native relocation view. Initial attempt omitted those two immediate relocations and failed its vtable assertion; correcting the fixture produced the reported passing run. DS1048, SS4000, mapped synthetic memory. No real free/API or exception execution. AX is not treated as a supported cleanup result.

EXE SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; NE1 file04C0. Sources: verify_map_cleanup.py, verification.json, native_listing.json, baseline48/pass48-results/listing.tsv.

## Implementation-ready findings
Keep configuration after clearing: map+6 and+E survive while+4/+8/+A/+C become0. Free entire blocks through header.next, not through free-node links. Save header.next before releasing its storage. Repeated normal cleanup is structurally empty; the real5FD0 null handling is separate evidence from pass67. No owning-value destruction is supported by these routines alone.

## Unknowns and next test
Trace deleting wrapper/vtable references and owners invoking6196/61C8. Establish whether map values are borrowed object addresses, then analyze the surrounding owner's destructor and any separate value cleanup. A real nonlocal allocator failure remains outside this successful teardown model.

## Confidence
High for bounded normal cleanup and mutation order; Medium for destructor naming; no whole-program parity claim.
