# Win110 pass93 — map allocation arithmetic and unchecked result paths

## Finding
Confirmed / High under declared returned-pointer model:42D0 requests wrap16(elementSize*count+6), writes a six-byte block header and prepends it to the block list without checking allocation result.6152 frees old bucket storage, clears its pointer, requests wrap16(2*bucketCount), zero-fills through a helper and stores the original bucket count, also without a local null-result check.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |42D0 uses lowAX fromMUL and adds6 |42D8–42E1 | High |
| Confirmed |Header words are old head,count,0; list head becomes returned pointer |42E7–42F8 | High |
| Confirmed |6152 frees old array before requesting replacement |615E–6174 | High |
| Confirmed |Bucket allocation/fill length wraps at16bits; stored count does not |616C–618C | High |
| Confirmed |Neither caller checks returned allocationAX before use |Native42D0/6152 | High |

## Behavior model
42D0: `p=allocate(word(size*count+6)); p.next=*head; p.count=count; p.word4=0; *head=p; return p;`.
6152: `free(map.buckets); map.buckets=0; n=word(count*2); p=allocate(n); map.buckets=p; memset(p,0,n); map.bucketCount=count;`.

For map nodes,61EC calls42D0 with elementSize8. Header6 precedes the node storage. This pass does not execute61EC's expansion loop or prove safe node-count bounds. For count8000, bucket allocation length wraps0 while bucketCount remains8000; actual reachable constructor counts and allocator treatment require separate evidence.

Null returned pointers in these tests deliberately write into mapped synthetic DS:0000 for42D0, or are forwarded to the memset stub for6152. This proves absence of a local guard, not a valid null pointer or a real Windows corruption event.5FE0 delegates to5AB0, whose installed failure handler may transfer control through an exception rather than return0. That path is not simulated here.

## Verification
131,086 cases passed: all65,536 block counts at elementSize8 × allocation results0/7000;14 bucket cases crossing counts0,1,17,512,7FFF,8000,FFFF and both pointer results. Checks include exact allocation size, all block-header words/list head/return, bucket free/allocate/fill call order/arguments and final bucket fields. Far-returnSP andBP are checked.

Original42D0 and6152 execute without instruction patches.5FE0 allocation,5FD0 free and6CAC fill call sites are intercepted beforeCALLF and leave cdecl arguments for original cleanup. Fill is recorded but not performed; bucket zeroing effects are therefore not dynamically verified here. DS1048, SS4000, CS2000. No real heap, block expansion, memset body or Windows API executes.

Run `python3 pass93/verify_map_allocations.py` with Unicorn2.1.4. Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Preserved Ghidra12.2 export plus raw EXE; no fresh database mutation.

## Implementation-ready findings
Keep16-bit size arithmetic and six-byte block header in the original model. Bucket replacement frees old storage before allocation. Distinguish unchecked returned0 from nonlocal allocation failure. Do not claim arbitrary counts are safe simply because the original code acceptsWORD arguments.

## Unknowns and next test
Execute bounded61EC expansion with a successful block fixture to verify first-node address, eight-byte stride and linking order. Trace actual constructor bucket/block counts and real exception failure behavior. Confidence High for caller arithmetic and ordering; live heap failure and safe runtime limits Unknown.
