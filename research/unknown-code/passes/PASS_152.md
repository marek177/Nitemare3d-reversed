# Nitemare 3D — PASS 152: 53-pair DS operand shift audit

Date: 2026-11-09. Scope: retrospective, independently recomputed comparison using `N3D_PASS150_evidence.json` from the user's Library. No original EXE executed and no fresh disassembly of raw binary was performed.

## Verified result

- The two series labeled `DOS_1.8` and `DOS_2.0` contain **53 direct references each**.
- Pairing references in their provided order, **all 53 of 53** refer to a DS absolute address exactly **two bytes higher** in the DOS 2.0 record. Thus `int(new_field,16) - int(old_field,16) == 2` for every record.
- `matches_image` is `true` for all **106** listed instructions; this is a consistency property of PASS150 evidence, not independent EXE re-verification in PASS152.
- Reference instruction forms are overwhelmingly `mov es, word ptr [absolute]`. The last two pairs use `mov cx, word ptr [absolute]` and `ljmp [absolute]` (FAR pointer), therefore the data block is **not** merely an untyped list of 15 interchangeable segment pointer variables.

## Correspondence by field

| Older offset | DOS 2.0 offset | Reference count |
|---|---|---:|
| 2550 | 2552 | 1 |
| 2552 | 2554 | 1 |
| 2554 | 2556 | 6 |
| 2556 | 2558 | 4 |
| 2558 | 255A | 3 |
| 255A | 255C | 1 |
| 255C | 255E | 3 |
| 255E | 2560 | 5 |
| 2560 | 2562 | 6 |
| 2562 | 2564 | 7 |
| 2564 | 2566 | 2 |
| 2566 | 2568 | 3 |
| 2568 | 256A | 10 |
| 256A | 256C | 1 |

The older report calls the older file DOS 1.8; its normalized image SHA-256 `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` was historically identified as DOS 1.9. This identification conflict remains unresolved at the provenance/label level. The DOS 2.0 normalized image SHA-256 is `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

## Address-family consistency and caution

The family `0000:*` retains identical segment:offset coordinates in both records for ten references, but some other routines move to different logical segments/offsets. Mapping memory-variable offsets is thus more reliable for this specific comparison than assuming address identity for every instruction.

The final entry's `ljmp [0x2550]` vs `ljmp [0x2552]` reads a **4-byte** FAR pointer starting at that offset (offset + segment), and the adjacent `mov cx, [0x2552]` / `mov cx, [0x2554]` overlaps its second word. Treat these as a related two-word entity in the data layout, not as unrelated scalar variables. Which runtime value is installed is unproven.

## Interpretation

Strong evidence of a uniform +2-byte relocation/shift in this subset of global data references. This could result from a WORD inserted earlier, a shifted global layout, or equivalent linking changes. None of those mechanisms is established by the present evidence. No confirmed writer was discovered in this pass.

## Next targeted proof

1. Find all writes, including `mov [reg+disp]`, `stosw`, copies, relocations and aliases, to each word from DS:2550 through DS:256C.
2. Establish the source/last writer of the FAR pointer pair used by `ljmp` (older DS:2550; DOS 2.0 DS:2552).
3. Trace startup, LOAD and map changes before first frame; record DS and all 15 words at each checkpoint.
4. Validate original build identities using package hashes and independently decompressed binaries.

## Reproducibility

The following Python 3 fragment reproduces the paired-operand test from the published PASS150 JSON:

```python
import json
x = json.load(open('N3D_PASS150_evidence.json'))['direct_references']
a, b = (x[k]['references'] for k in ('DOS_1.8','DOS_2.0'))
assert len(a) == len(b) == 53
assert all(int(y['fields'][0],16) - int(z['fields'][0],16) == 2 for z,y in zip(a,b))
assert all(r['matches_image'] for r in a + b)
print('PASS: 53/53 +2-byte displacement; 106/106 published byte checks')
```
