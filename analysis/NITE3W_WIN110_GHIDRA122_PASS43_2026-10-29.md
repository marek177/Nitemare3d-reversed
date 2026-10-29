# Win16 1.10 — Ghidra 12.2 pass43: integrated segment and map updates

## Finding
Confirmed, High: 4080 controlled cases execute original 6266, 6152, B1A4(mode0), 3736 and the cached path of 2AAC together. Both the render records and map buffer match an independent model. No helper stubs are used. This establishes their shared state behavior for the tested fixtures, not full game runtime parity.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Contiguous pointer runs generate inclusive-X segment records | Original 6266 and 6152 | High |
| Confirmed | Original B1A4(mode0) executes at each new run and updates map cells | Original call at 62EC | High |
| Confirmed | Orientation and flag08 corrections coexist with record initialization | Shared object records, original 3736 | High |
| Confirmed | All 200 record-region bytes and 4096 map bytes match expectations per case | Integrated verification | High |
| Unknown | Palette reconstruction, actual selector allocation and full renderer output | Excluded from this harness | Low |

## Behavior model
6266 scans the supplied per-column far-pointer array. On each change, it finalizes the preceding run through original 6152, starts the next record and invokes original B1A4(mode0). B1A4 obtains cached palette entries through original 2AAC, converts coordinates through original 3736 and marks map cells. The final segment is initialized after the scan.

The object fixtures keep world/map coordinates at +0C..+12 separate from projected endpoint pairs at +14..+1A. Changing map orientation or flag08 does not change the supplied flat projected endpoints. This allows both output regions to be checked independently while the actual call chain shares state.

Repeated appearances of the same object create separate segments when another object occurs between them. Their map marks overwrite the same cells with the same color; the final map is checked against the union of expected writes. No claim is made about order-dependent palette changes because the palette cache remains fixed.

## Verification
Original EXE SHA256: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

675 native instruction comparisons precede controlled selector relocation. 4080 cases = all 510 binary pointer patterns of length1..8 × flags0/8 × orientations0..3. Each run compares a 200-byte record region, including unused trailing records, and all 4096 map bytes. Segment count, SP, BP and DS are checked. No functions or OS services are stubbed.

Test code selectors are 2000 and 4000, DS=SS1048, object selector5000 and map selector6000. Palette cache flag00C4 is zero; color2=42 and color9=99. Projected endpoints are flat at height1400 with origin53F0=1280. Map coordinates differ between the two objects. Actual Win16 selector mapping is not executed.

## Implementation-ready findings
Treat run formation, interpolation setup and map marking as an ordered chain with shared objects. Removing the B1A4 call from a reconstructed renderer would omit the verified map-state effect. Preserve contiguous-run grouping and the exact map orientation rules. The tested cache contract excludes palette rebuilding and its potential effects.

## Unknowns and next test
Trace upstream object endpoint production and height constraints; test palette rebuilding and planar output. MAXSEG boundary handling was deliberately excluded here and remains covered only under the contracts in passes40/41. Full game rendering and the first frame after LOAD remain open.

1551 internal entries retain native decompile success; 310 EXTERNAL entries are separate. The previously measured 1401 undefined executable bytes remain unresolved.

## Confidence
High for the tested combined record/map updates; limited for actual game scenes and hardware output.
