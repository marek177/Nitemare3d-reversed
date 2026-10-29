# Ownership-to-span preparation — pass40

## Finding
66 scenarios across six distinct DOS images recover ownership-run grouping,18-byte records and the50th-span failure threshold. Original preparation and interpolation producer execute together. One external notification is mocked without side effects; fatal handling is not executed.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Scan compares current per-x owner to prior owner, initially0 | V1.9 1201:0134–0159 | High |
| Confirmed | Transition finalizes previous record, starts next, notifies owner and increments count | V1.9 0162–0199; original producer output checked byte-for-byte | High under notification mock |
| Confirmed | 50th started span invokes fatal call;49 completes | V1.9 019d–01a9;48/49/50/51-run patterns | High local branch |
| Confirmed | Leading owner0 is skipped until first nonzero transition; later owner0 transitions are retained | Pattern tests with internal/terminal zero owners | High under mock |
| Unknown | Notification mutates object geometry or other state | V1.9 call183c:1442 not executed | Unresolved |

## Behavior model
Scan viewport left..right inclusive. Prior owner starts0. On owner change, finalize previous span if count>0: write previous owner/right=x-1 and invoke original interpolation producer with that owner's four endpoint words at+14..+1a. Advance record pointer18. Start next record.left=x, update owner, call notification(0,owner), increment count. count>=50 calls fatal. After scan finalize current record at right edge and interpolate once more.

At V1.9 count DS4d62, records DS4d6c, ownership array DS4562 (word indexed by x). Producer1201:001a receives endpoint pairs from owner record. Direct preparation entry1201:012e. Exact per-build addresses in spans.json.

If there are no transitions (all zero or empty viewport), count remains0 but the routine still writes/finalizes the current record with owner0 and invokes producer using DS offsets14..1a. Its left field is not initialized by this preparation path. Tests initialized that field to a5a5 and confirmed it remains so; consumers normally use count, but their zero-count behavior is outside this pass. This is a local side effect, not a proven gameplay defect.

## Verification
`/usr/bin/python3 scripts/verify_span_prepare.py` with Unicorn2.x. Eleven patterns per image: empty, all zero, constant owner, internal zeros, alternating/repeated runs and48/49/50/51 transitions. Viewport left8; endpoints for owner1 rising and owner2 falling; owner0 record bytes zeroed. Tests verify count, ordered notification args, fatal threshold, completed18-byte records including slope/accumulator, normal far return/SP/DS and zero-count tail writes.Exactly12 cases stop at fatal (two patterns ×six),54 return. The50th record is started but not finalized when stopped. Notification mock may hide state effects; no complete scene traversal, resource/VGA/DAC or full-game parity claim. Ghidra12.2 preserved export has a misaligned tail decoding at V1.9 01da; raw EXE bytes show normal add-sp10,pop-si,pop-di,leave,retf, and emulation returns correctly. No EXE or project edits. Supplied1.8/1.9 identical.

## Implementation-ready findings
Preserve run boundaries, record stride18, leading-zero treatment, zero-owner transitions and strict count<50 successful path. Keep interpolation tied to each owner's endpoint record. Do not silently permit50 records if matching this original branch.

## Unknowns and next test
Recover notification call side effects and repeat with original dependency. Connect real ownership-array producers, then span preparation through rendering. Determine zero-count handling in outer renderer and actual maximal scene spans. Menu limits remain open.

## Confidence
High for bounded run-building behavior under mock; notification/full scene effects unresolved.
