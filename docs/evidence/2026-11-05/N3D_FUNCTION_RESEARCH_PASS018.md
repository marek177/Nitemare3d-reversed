# Nitemare 3D — PASS 018: DOS v2.0 expanded image reconstructed

Date: 2026-11-05

## Original source and method
The original `nite3/dos/N3D-E-20.EXE` was read from the user-provided `dosbox-n3d(20261103-105917).zip`. Its independently calculated SHA-256 is `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.

A new **pure Python reconstruction of the original packed loader algorithm** traversed its backward compression tokens and internal relocation stream. This is a static reconstruction, not a full i8086 CPU emulation and not a complete gameplay runtime test.

- Compressed stream: 158 blocks, 82,274 generated output bytes.
- Relocation stream: 1,670 relocated 16-bit targets, grouped 1,234 + 311 + 125, remaining 13 groups zero.
- Reconstructed DOS 2.0 expanded load image: **171,360 bytes** (`0x29D60`), with synthetic MZ load base `0x1000`.
- SHA-256 of this *relocated synthetic load-base-0x1000 image*: `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. Other load bases produce different relocation words and different hashes; this is **not** the original packed EXE SHA.
- Original CRT transfer image offset `0x11EF8` begins with `B4 30 CD 21` (MOV AH,30h; INT 21h).
- **Independent runtime byte-for-byte comparison against a second emulator/unpacker has not been performed.** Do not describe the image as runtime-proven or mark all functions complete.

## Overlap machine-byte audit
The archive `N3D_FUNCTION_RESEARCH_PASS018.zip` holds a 19-row machine-code audit and the reconstructed private expanded image. For the 17 code-space pairs with consistent Ghidra image address translation, direct byte windows are now available; two addresses `0x22025` and `0x2ABEE` require separate segment mapping.

The following are local instruction-boundary witnesses on the reconstructed bytes (not complete global CFG proofs):

```asm
; Ghidra 0x18DFF/0x18E01 maps to image 0x8DFF/0x8E01:
8DFA: 9A 88 01 77 12     CALL FAR 1277:0188
8DFF: 83 C4 02           ADD SP,2
8E02: 2C 05              SUB AL,5

; Ghidra 0x18E04/0x18E06 maps to image 0x8E04/0x8E06:
8DF0: 77 12              JA 8E04
8DF5: EB 0D              JMP 8E04
8E04: 88 46 FF           MOV BYTE PTR [BP-1],AL

; Ghidra 0x126F8/0x126F9 maps to image 0x26F8/0x26F9:
26F4: 9A CE 04 56 11     CALL FAR 1156:04CE
```

At `0x8E01`, `0x8E06`, `0x26F8` and `0x26F9` the candidate alternate entry points lie in the operand bytes of the shown instructions **on these local paths**. Full incoming-branch reachability, alternate overlapping code streams, and function CFGs remain unresolved.

## Metrics
- Original byte-level source acquisition: confirmed.
- Original packed loader static output reconstruction: completed (158 blocks; 1670 relocations).
- Machine-code windows available for 17 of 19 deduplicated Ghidra overlap warnings.
- Locally identified known instruction boundaries for OVL-014 and OVL-015; local encoding for OVL-006.
- Whole-program independently reachability-verified overlap conflicts: **0/19**.
- Fully completed function reports: **0 newly**.
- Original DOSBox-X gameplay runtime tests: **0 newly**.

See downloadable `N3D_FUNCTION_RESEARCH_PASS018.zip` for `PASS018_OVERLAP_MACHINE_AUDIT.csv`, `PASS018_OVERLAP_MACHINE_AUDIT.json`, `PASS018_SUMMARY.json`, `PASS018_REPORT.md`, reconstructive Python scripts, and a **private** binary image. The executable image is not committed to this public GitHub repository.
