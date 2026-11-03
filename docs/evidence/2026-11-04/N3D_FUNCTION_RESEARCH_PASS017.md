# Nitemare 3D — PASS 017: Original Win16 callback walker byte identity

Date: 2026-11-04

## Original-source verification
Source: previously supplied `dosbox-n3d(20261103-105917).zip`, retrieved from user file Library. Five original Windows NE EXEs opened and parsed directly, with NE segment-table alignment and physical offsets verified. DOS 2.0 original packed EXE also opened.

## Exact machine-code finding
The complete **known instruction sequence** in logical NE segment 2 at **02:3994–02:39A6 inclusive (19 bytes)** is byte-identical in Windows versions 1.0, 1.3, 1.6, 1.8 and 1.10:

`3B F7 73 0E 83 EF 04 8B 05 0B 45 02 74 F2 FF 1D EB EE C3`

SHA-256 of the 19-byte sequence: `74680ca64af09085fff449de667b5cd14c9314f721f8db65040de1f1c42e9a32`.

Independent GNU objdump i8086 decode:

```asm
02:3994  3B F7        CMP SI,DI
02:3996  73 0E        JAE 02:39A6
02:3998  83 EF 04     SUB DI,4
02:399B  8B 05        MOV AX,[DI]
02:399D  0B 45 02     OR AX,[DI+2]
02:39A0  74 F2        JE 02:3994
02:39A2  FF 1D        CALL DWORD PTR [DI]
02:39A4  EB EE        JMP 02:3994
02:39A6  C3           RET
```

Classification for these exact 19 original bytes: **IDENTICAL_BYTES** across all five supplied Win16 versions. This is stronger than the older C-only evidence; it confirms actual encoded instructions, immediate branch targets and termination at RET for this entry. It does **not** prove all callers, FAR callback targets, ABI preservation or behavioral equivalence.

Physical source offset of Win16 1.10 segment 2: `0xE8A0`. The other four references have segment 2 at `0xE880`.

### Adjacent region
The actual raw byte ranges for `02:38DB–02:39A6` were compared against Windows 1.10. Across four version-pair comparisons, there are **49 individual byte mismatches** (not necessarily 49 changed instructions or changes in semantics). See `PASS017_WIN_EXIT_REGION_BYTE_DIFF.csv` in the local PASS017 archive.

## DOS2 original packed loader
Directly decoded the packed original's loader entry at image offset `0x1B730`, file offset `0x1B930`. This is **packed loader code**, not the expanded game image. No decompression execution has been performed here; Unicorn/Capstone are not installed and network installation failed. Therefore the 19 original Ghidra overlap-warning pairs remain **0/19 byte-and-reachability verified**.

## Artifacts and reproducibility
In `N3D_FUNCTION_RESEARCH_PASS017.zip`: `PASS017_WIN_FUNCTION_IDENTICAL_BYTES.csv`, `PASS017_WIN_EXIT_REGION_BYTE_DIFF.csv`, `PASS017_WIN110_CALLBACK_WALKER.asm`, `PASS017_DOS20_PACKED_LOADER_ENTRY.hex`, `PASS017_DOS20_PACKED_LOADER_ENTRY.asm`, `PASS017_EVIDENCE.json`, `pass017_build.py`, plus previous cumulative reports. Original copyrighted EXE bytes are not committed to GitHub.

New gameplay runtime tests: **0**. Full callback function graph: **unverified**. DOS2 expanded byte conflicts resolved: **0/19**.
