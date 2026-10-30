# Win110 pass91 — map unlink and node recycling

## Finding
Confirmed / High:6356 removes the first matching key from a bucket chain, then6266 recycles the node into map+0A free list and decrements map+08 count. No heap free occurs in these functions. Key/value bytes are retained.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |Null bucket array returns0 before division |635F–6363→63A6 | High |
| Confirmed |Bucket=(key>>4)%map.bucketCount |6365–6374 | High |
| Confirmed |Pointer-to-link traversal supports head/middle/tail unlink |6377–6396 | High |
| Confirmed |Found node passed to6266, then return1 |6398–63A1 | High |
| Confirmed |6266 prepends node to free list and decrements count |6266 native/decompiled export | High |

## Behavior model
`link=&buckets[hash(key)]; while(*link) { node=*link; if(node.key==key) { *link=node.next; node.next=map.freeHead; map.freeHead=node; --map.count; return1; } link=&node.next; } return0;`

This is node recycling, not destruction of the mapped window object or heap deallocation. Node+4 key and+6 value remain intact; node+0 is repurposed as free-next. The search returns at its first match; duplicate-key behavior beyond that follows static structure but duplicate fixtures are not included here.

Unlike lookup6280, removal6356 checks bucket-array pointer before division. Therefore null array with zero bucket count returns0 safely in this original routine. Nonnull array and zero bucket count remains invalid/unverified and must not be normalized into a valid map.

## Verification
65,537 original-code cases passed without stubs: everyWORD key tested against a fresh three-node chain with colliding keys0011,0091,0111, covering head/middle/tail removal and all misses; one null-array/zero-count case. Checks cover ordered remaining chain, count decrement, free-list head/next, retained key, booleanAX, finalSPD008 and preservedBP/SI/DI. The source also shows value is untouched by removal/recycling.

Original6356→6266 executes. Only internal selector639F normalizes to testCS2000. DS=SS1048, synthetic map4250, eight buckets5000, nodes6000/6010/6020, prior free-head6F00. The prior free-head is stored but never dereferenced. No Windows, heap allocation/free, object destructor or real HWND executes.

Run `python3 pass91/verify_map_remove.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Original executable and preserved Ghidra12.2 export; no fresh database update.

## Implementation-ready findings
Maintain separate bucket and free chains, decrement count once for a found node, leave misses unchanged, and recycle without clearing key/value. Do not call the mapped object's destructor merely because this map association is removed.

## Unknowns and next test
Execute62F4 insertion and free-node reuse to verify overwritten fields and count restoration. Live HWND ownership remains Unknown. Confidence High for isolated map unlink/recycle under valid map preconditions.
