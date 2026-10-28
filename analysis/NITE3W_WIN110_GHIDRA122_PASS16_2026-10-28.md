# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 16

## Finding

Recovered heading-derived step terms and their copy into an eight-slot projectile pool, including first-free selection, resource consumption gate and partial record initialization. Spawn copies the current global error term; movement can mutate it. Thirteen record bytes are not explicitly initialized by this routine. Neither fact alone proves a visible stale-depth or trajectory defect.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016,JDK25.0.2. Runtime tests:0.

## Heading terms and movement use

Confirmed / High,E585..E5D0: using exact trig results from pass15, S=abs(sine),C=abs(cosine),m=min(S,C),M=max(S,C). Writes WORDs:

| Global | Value |
|---|---|
| 4C06 | S>C ?1:0; equality selects0 |
| 4C08 | initial error2m-M |
| 4C0A | increment2m |
| 4C0C | correction2(m-M) |

8604 snapshots the major-axis flag, optionally inverts it for its side-motion argument, and uses collision helper84F4 for axis attempts. Each iteration mutates global4C08: error<0 adds4C0A; otherwise adds4C0C and attempts the secondary axis. Geometry is consistent with integer line stepping (Inferred / High), but the model here verifies axis-attempt recurrence only, not collision acceptance or pixel rendering.

9AAC reads all four current globals, including4C08, directly. It does not callE516 or recompute the initial error. Thus treating spawn as an unconditional fresh2m-M seed is unsupported. To decide actual trajectory consequences, establish whether preceding movement, heading reset and firing order leave that global modified at the call.

## Projectile allocation and resource gate

Confirmed / High,9AAC..9B63. Eight records startDS:4C4A with stride2Ah (42 bytes). Active byte is+0C. Scans in ascending slot order for byte0; any nonzero byte occupies a slot. If all eight are occupied, returns AL0 before callingA97C: no resource consumption through that gate. First-free slot is chosen before the resource call; the routine does not rescan afterwards. A97C returning AL0 also returns failure before local slot writes. Successful initialization returns AL1; AH is not established as a boolean result.

Projectile role is supported by8B06's firing branch: selected weapon notFF, alternate-action flag4C2E checked first, mode4C26==2 invokes9AAC. Mode1 uses a separate target/hit path and is outside this spawn model. Mode2 success reaches7664,B594 and sets4C30=1. This is a static firing path, not measured gameplay reachability or full damage recovery.

A97C (Confirmed / High) returns1 immediately if4BE5!=0, without local decrement/UI. Otherwise weapon byte4C23 selects resource and UI:

| Weapon value | Resource byte | A3B6 selector |
|---|---|---|
| 0 or3 | 4C20 | 8 |
| 1 | 4C44 | 9 |
| 2 | 4C1F | 7 |

It snapshots the resource byte, decrements only when nonzero, invokes UI, then returns the old byte. Return is not normalized0/1; spawn only tests zero/nonzero. Other weapon values return0. UI may write back/clamp values, as shown for other selectors in pass13; this pass's resource fixture stops at the local decrement and does not certify the complete post-UI resource state.

A930 uses local byte table[0,2,0,0] for valid weapon0..3, adds byteDS:8397 modulo256 and returns AL. No local index guard exists. Invalid weapon indices and resource-bypass combinations require separate validity analysis; they are outside the lookup model.

## Record initialization

Confirmed / High,9ADC..9B5F. All offsets relative to selected slot:

| Offset | Write |
|---|---|
| +00,+02,+04,+06 WORDs | current4C06/08/0A/0C |
| +08 WORD | heading<180 ?+1:-1 |
| +0A WORD | heading>90 AND heading<270 ?+1:-1 |
| +0C BYTE | active=1 |
| +11 BYTE | 0 |
| +12 BYTE | A930 result |
| +13 BYTE | (previous byte OR1) AND EFh |
| +16 DWORD | 0 |
| +1A DWORD | current far cell DS:4C10 |
| +1E,+20 WORDs | current coordinates4BF6/4BF8 |
| +28 BYTE | 5 |

Offsets+0D..+10,+14..+15,+22..+27,+29 (13 bytes total) are not explicitly written here. The routine also preserves flag bits other than setting bit0 and clearing bit4. This records literal reuse behavior, without assigning unsupported meanings such as depth or lifetime to untouched fields. Callee mutation/aliasing may add effects beyond the direct-write map.

Direction boundary details matter: at angles90 and270 y-direction is-1, at180 x-direction is-1. Zero trig components can make some signs immaterial in a valid step, but the stored values must not be normalized away for state parity.

## Validation

- Original hash and five critical raw spans verified: pool scan/full return, preserved flag bits and heading term branch arithmetic.
- 92160 error-recurrence fixtures: all360 literal heading pairs across256 iterations, secondary-axis attempt count compared with independent integer rounding formula.
-512 pool/gate cases: all256 occupancy patterns and gate failure/success. No-slot case calls the resource gate zero times.
-92160 record-write fixtures:360 headings ×256 old flag bytes; checked13 untouched bytes with distinct initial markers. These fixtures use fresh heading terms, while the actual routine copies current globals; that limitation is explicit.
-2048 local resource fixtures: valid weapons0..3, all256 resource values, bypass0/1. UI callbacks not executed.
- Ghidra annotated four functions, full native export completed and project saved.1551 internal functions remain, all1551 decompilations completed;310 EXTERNAL-block entries tracked separately.

Coverage unchanged:160005 instruction bytes,8282 data bytes,1401 undefined bytes. No executable patches, new entry creation or padding classification. Static models do not prove complete projectile, damage or rendering parity.

## Unknowns and next test

Trace4C08 through8604, heading setters and9AAC while firing stationary and after movement; record the value actually copied. Fill all eight slots and confirm no A97C call/resource decrement on the ninth request. Reuse a marked inactive slot, dump all42 bytes before/after, then follow reads of the13 preserved bytes in the update/draw path before labeling them. Capture resource state before and after A3B6 for selectors7/8/9. Damage, collision acceptance, stale-depth meaning, lifetime and final rendered output remain unresolved.

## Confidence

High for bounded term arithmetic, pool ordering, direct writes and local resource-return semantics; full scheduling/callee effects and runtime parity remain open.
