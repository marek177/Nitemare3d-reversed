# Win110 pass89 — preferred main object and permanent HWND lookup

## Finding
Confirmed / High: getter3EA6 returns application+20 when nonzero, otherwise+1E.130E searches map4250 through original62C8→6280 and returns mapped value or0. The lookup does not create a wrapper for an unmapped HWND on this path.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed |Application table+6C targets3EA6 |NE4:554C+6C, prior raw inspection | High |
| Confirmed |+20 has priority over+1E, no pointee dereference |3EAC–3EB7 | High |
| Confirmed |130E uses map4250 and returns lookup output on success |1312–1329 | High |
| Confirmed |Bucket=(unsigned key>>4) modulo map.word+6 |6280 native/decompiled evidence, original execution | High |
| Confirmed |Map+4 holds bucket-array near pointer; node+0 next,+4 key,+6 value |6280/62C8 and colliding-chain fixture | High |

The map is called permanent by its lookup-only role (Inferred / Medium). This pass does not establish all insertion/removal or lifetime policies, and does not claim every map4250 entry is currently live in Windows. Main-object field labels are role descriptions; no runtime type assertion is made.

## Behavior model
`main = app.word20 ? app.word20 : app.word1E;`
`bucket=(key>>4)%bucketCount; node=buckets[bucket]; while(node && node.key!=key) node=node.next; return node ? node.value : 0;`

62C8 writes the output only on a found node.130E returns0 on failure without consuming uninitialized local output. A found node whose value is0 is indistinguishable from a missing key to130E's caller. Valid nonzero bucket count is a lookup precondition: modulo occurs before the bucket-array pointer null check in the captured code; bucketCount0 is not tested and must not be silently treated as an empty valid map.

## Verification
131,072 cases passed without function stubs: all65,536 preferred+20 words with fallback7400 through original3EA6; all65,536 HWND words through original130E→62C8→6280 using a synthetic eight-bucket map. Keys0011 and0091 collide,FFFF tests high unsigned key; values7400/7500/7600. Every other key returns0. Each run checks far-returnSPD006 and restoredBP.

DS=SS1048 intentionally supports near pointers to local output words used by62C8/130E. CS2000 maps NE1; selectors131F/62D9 normalize to2000. Synthetic map/node/bucket memory is not a captured Windows HWND registry. No allocation, Windows API or object creation occurs.

Run `python3 pass89/verify_window_lookup.py` with Unicorn2.1.4. EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Uses original executable and preserved Ghidra12.2 export; no fresh database update.

## Implementation-ready findings
Preserve preferred-object fallback, unsigned key hashing and chained collision lookup. Return0 for missing HWND in this pretranslation lookup. Do not create temporary objects here or conflate node+4 key with node+6 value. Preserve SS=DS assumptions for near local pointers in this model.

## Unknowns and next test
Trace writes to application+20 and map4250 insertion/removal to identify object ownership/lifetime and temporary-map alternatives. Concrete virtual+54 filters and actual Windows handles remain unverified. Confidence High for getter/hash lookup under valid synthetic map preconditions.
