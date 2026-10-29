# Complete viewport setter and split-width table — pass 30

## Finding
408 bounded original-code executions across six distinct DOS images now execute the complete viewport setter and both dependencies with no mocked callees. 390 return normally and verify every one of 511 table entries (199,290 entry comparisons). 18 stop at the known first-dependency divide exception. Supplied 1.8/1.9 are one identical image.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Second dependency writes 511 split 24-bit values, index 1..511 | V1.9 1156:0030–008d; per-build bodies in tables.json | High |
| Confirmed | Low words start DS:3052; high bytes at DS:2e50+i | V1.9 stores 0077/007b and loop 0084; exhaustive entry checks on each successful test | High |
| Confirmed | Complete setter returns for 65 tested widths per image | Original setter + both dependencies; SP, DS and far return checks | High within sampled inputs |
| Confirmed | Width -1,0,1 stops in first dependency before table generation | Interrupt 0 hook, 18 tests | High |
| Inferred | Table supplies a renderer scaling/clipping calculation | Caller context and height-based formula | Medium; full consumers not traced |

## Behavior model
H=signed16(width) arithmetic-shift-right 1. For each i from 1 through 511:

```
delta = max(i - H, 0)
numerator = signed32(((delta << 6) & 0xffff) << 16)
value = trunc_signed(numerator / i) arithmetic-shift-right 1
low_words[i-1] = value & 0xffff
high_bytes[i] = (value >> 16) & 0xff
```

The clamp is implemented by testing the high word of signed 32-bit subtraction; because i and H have the tested 16-bit-derived ranges it equals the stated max. The 16-bit shift is material: do not replace numerator with an unlimited-precision delta*4194304. Stored values are only low 24 bits of the shifted signed result.

At default width 304, H152: entries 1..152 are zero and later entries follow the formula. Index zero of the byte array is not written by this routine. First-dependency arithmetic is as documented in pass 29. No new table division by zero occurs because i starts at one.

## Verification
Run `/usr/bin/python3 scripts/verify_viewport_tables.py` with Unicorn 2.x. 68 widths per image, same boundary set as pass 29. All 511 entries checked in each successful path; per-case table SHA-256 records the reconstructed 24-bit output stream encoded as 511 little-endian uint32 values. The script compares original dword outputs from dependency one too. Divide-error hooks stop before DOS handlers. No DOS services, rendering framebuffer, DAC, gameplay or timing parity tested. Input EXEs, Ghidra 12.2 exports and dependencies included in archive. No project database edits.

## Implementation-ready findings
Use exact signed division and 16/32-bit wrapping; preserve separate low-word/high-byte tables and index convention. This closes the previously mocked callees for the local setter. It does not establish input safety for every game path or semantic completion of the renderer.

## Unknowns and next test
Trace reads of the low-word and high-byte tables to identify their precise render role. Menu width adjustment limits and DOS exception response remain unresolved. Verify actual table consumer calculations with controlled depth/height inputs before assigning final semantic names.

## Confidence
High for complete local setter execution and generated table bytes under the sampled widths; medium for table purpose.
