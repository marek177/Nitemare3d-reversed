# Win110 pass92 — map insert, existing key and recycled-node reuse

## Finding
Confirmed / High:62F4 returns node+6 as a writable value slot. Existing keys preserve value/count/free list. Missing keys consume a free node through61EC, clear its key/value words, record bucket/key, prepend to bucket chain and increment count. A removed node is reused and its old value cleared.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |Found key bypasses insertion and returns existing node+6 |630C–630E→634D | High |
| Confirmed |Free node popped and count incremented |6233–623B | High |
| Confirmed |Node+4/+6 zeroed by original6CAC calls |623E–625B | High |
| Confirmed |Bucket index stored+2,key+4; node prepended |6327–634B | High |
| Confirmed |Remove/reinsert reuses same slot and clears retained old value |256 four-call sequences | High |

## Behavior model
`node=find(key); if(!node) { node=popFreeNode(); ++count; node.key=0; node.value=0; node.bucket=hash(key); node.key=key; node.next=bucketHead; bucketHead=node; } return &node.value;`

62F4 itself does not overwrite an existing mapped value.132C's later store through the slot performs that update.6266 removal retained key/value in pass91;61EC clears them when the node is reused, explaining where stale data ceases to be visible through a newly inserted slot.

## Verification
256 sequences pass, totaling1,024 original calls. For each key0000..007F andFF80..FFFF: insert→write7777 to returned slot→request same key again→remove→reinsert. Checks include exact returned6006, initial/reused zero value, preserved existing7777, count and free-head transitions, bucket index/head, key, far-return stack and preservedBP/SI/DI.

Original62F4,6280,61EC,6356,6266 andNE2 memset6CAC execute without function stubs. Prepopulated eight-bucket array and two free nodes avoid bucket allocation6152 and node-block expansion42D0. Those branches are not executed. DS=SS1048, CS2000/3000; internal selectors6308/6323/639F normalize2000 and6249/6259 normalize3000. DF=0 is explicit. No real heap, Windows objects or expansion failure behavior occurs.

Run `python3 pass92/verify_map_reuse.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Preserved Ghidra12.2 export and raw executable; no fresh database mutation. A local script syntax typo was corrected before the successful run; reported counts refer to that completed run.

## Implementation-ready findings
Return a value-slot address rather than the value itself. Reuse existing keys without count increment or clearing. Clear recycled key/value before insertion, then set key/bucket and link at bucket head. Keep actual HWND association store in the caller.

## Unknowns and next test
Execute bucket initialization6152 and free-node expansion42D0 to establish capacity/growth and failure paths. Multi-node insertion ordering and duplicate invalid-map fixtures remain separate coverage. Confidence High for initialized-map/free-node path; allocator expansion Unknown.
