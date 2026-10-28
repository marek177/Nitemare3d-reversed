# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 14

## Finding

Recovered the push-record initialization, activation and movement chain, including collision gating and ordered spatial-list repair. Diagnostic strings identify the table as push-related; the exact moving texture/asset is still unknown. Blocked moves consume no remaining step. Successful moves preserve strict coordinate-order ties. No runtime or full scheduler parity claim.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016,JDK25.0.2. No EXE patches or new function entries.

## Evidence and activation chain

Confirmed / High,181C: clears signed count1040:0004 and scans28-byte objects at1040:6D66, bounded by signed DS:7E58. Object byte+6==28h emits one six-byte record at1040:A616, storing WORD object index and byte+4=0. At existing count>11 it calls3118 with string DS:0DE0 `MAXPUSHES exceeded (%d)` and argument12. This is a checked capacity of12, not proof that writes remain safe if the diagnostic returns. The initializer does not explicitly initialize dx/dy or byte+5.

Confirmed / High,133A: finds a record by comparing the full associated object's far cell pointer with the supplied pointer. Missing match calls3118 with DS:0DA0 `Push not in map`. These exact strings and their consumers establish the push-table role without needing a guessed asset name.

Confirmed / High,21B6: calls133A, then activates only if remaining byte+4==0 and DS:7E94[probe.byte0]&02h==0. Copies dx/dy bytes from DS:[word4BEC+0A4]/[word4BEC+0AC], writes remaining8 and callsACDC. Probe is a supplied far pointer. ACDC effects and actual directional delta values remain unresolved. Eight is a step count, not a proven displacement or duration.

## Movement record and object fields

Confirmed / High,2210..2333:

| Record field | Meaning |
|---|---|
| +00 WORD | index into28-byte object array1040:6D66 |
| +02 signed BYTE | dx |
| +03 signed BYTE | dy |
| +04 BYTE | remaining accepted movement steps |
| +05 BYTE | unassigned in this pass |

Associated object fields: far current cell+0C, WORD x+10/y+12, coordinate-list indices+14/+16. Nonzero remaining starts a step; additions wrap to16 bits. The caller does not validate the object index or pointer ranges locally.

Target cell selector is1040. Exact offset calculation, including signed x behavior:

    target = A69Eh + 2 * (64 * (newY_u16 >> 6) + floor(newX_s16 / 64)) mod65536

Raw code clears CL bit5, arithmetic-shifts CX by5, masks AL low6 bits and doubles AX. For valid coordinates0..4095 this reduces to a64×64 grid of64-coordinate-unit cells with two-byte records. Negative/out-of-domain coordinates must not be silently clamped in a parity implementation.

Before comparing cell pointers the code reads target.byte1, indexes DS:7F94 and obtains its flag byte. Acceptance is `same full far cell pointer OR (targetFlags &06h)==0`. Thus same-cell movement bypasses blocking flags, but does not bypass that earlier target read. Invalid pointers can still matter before the branch.

If blocked, no coordinate, cell payload or remaining-step write occurs locally. If accepted and the cell differs, copy oldCell.byte1 -> newCell.byte1, then zero oldCell.byte1. Next write new x,y,current far cell; call C9A6 with object far pointer and sign-extended dx/dy; decrement remaining byte after the call. The target's previous payload can be overwritten if its classification flags permit the move. Aliasing and callee mutation are not erased by this simplified description.

Initial signed record count uses1040:0004. Loop-end count is reread through selector DS:2220. Blocked records retain their remaining count for later invocations; no timeout is added here.

## Coordinate lists

Confirmed / High,C9A6: object+14 indexes the far-pointer list DS:839E for signed x; object+16 indexes DS:8916 for signed y. Signed WORD DS:839C provides bounds. Negative delta bubbles left only while moved coordinate is strictly less than previous; positive delta bubbles right only while strictly greater than next; zero skips the axis. Each adjacent swap updates both objects' index words. X repair precedes Y repair.

Equal coordinates are not swapped. The independent sort fixtures assume a valid initially sorted list and no signed coordinate overflow. After signed overflow, delta direction can disagree with signed coordinate order, so this directional repair is not a general sort guarantee. Live pointer/count reads and aliases remain relevant for corrupted states.

## Validation

- Original hash and six critical raw spans checked: address arithmetic, collision decision, accepted-only decrement and activation guards/count.
- 286720 address fixtures including full16-bit sweeps and valid-grid row/column boundaries; exact bitwise expression checked against arithmetic formula.
- 131072 remaining-count/classification/same-cell gate fixtures.
- 65536 activation remaining-count/probe-flag fixtures.
- 5040 sorted-list fixtures with repeated coordinates, both delta signs and zero; adjacent swaps compared with an independent stable sort and all index fields checked.
- Both diagnostic strings verified directly in original Data10 bytes.
- Ghidra annotations cover five existing functions, followed by complete native export and project save. Internal inventory remains1551, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked. Decompiler prototypes are not certified by completion.

Coverage unchanged:160005 instruction bytes,8282 data bytes,1401 undefined bytes. Models execute no original CPU instructions or game callbacks and assume valid, disjoint pointers and nonmutating callbacks for their isolated decisions.

## Unknowns and next test

Capture21B6 on a real push: cell/probe far pointers, direction object and dx/dy, remaining8 and ACDC effects. Step2210 through an open boundary and a blocked boundary, recording old/new byte1, coordinates and remaining count. Capture both sorted pointer arrays and object index fields before/afterC9A6, including equal-coordinate neighbors. Identify the type28h asset from loader/MAP records before calling it a specific wall or object. Tick duration, physical displacement, render consequences and complete push parity remain unverified.

## Implementation-ready findings and confidence

Preserve accepted-only decrement, modulo widths, signed x cell arithmetic, same-cell bypass, copy-before-clear order, full far-pointer comparison and strict stable neighbor swaps. High confidence for bounded static operations and push-table identity; exact assets, invalid-state behavior and runtime parity remain open. Runtime tests:0.
