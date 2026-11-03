# Nitemare 3D — PASS 015: original-image provenance reconciliation

Date: 2026-11-04

## Scope and checked material
- Reviewed local `N3D_FUNCTION_RESEARCH_PASS014.zip` (573 entries) and the original Ghidra-generated text export `N3D-E-20.EXE(5).c` (SHA256 `5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54`).
- Inspected the repository tree of `marek177/Nitemare3d-reversed` (3995 paths on main during inspection); no original binary EXE/ZIP was identified. Original game data are explicitly excluded under `data/original/`.
- Found pre-existing PASS 53 evidence, including an original packed EXE byte extraction + emulated unpacking proof for DOS 1.0–1.9: [report](../../research/dos_ghidra122_original_unpack_pass53/pass53/REPORT_PASS53.md), [evidence](../../research/dos_ghidra122_original_unpack_pass53/pass53/evidence/unpack.json). This was **not rerun** in PASS015.

## Historical original EXE hashes (from PASS53, not independently rehashed here)
| DOS | Original SHA-256 | Packed bytes | Compared expanded bytes |
|---|---|---:|---:|
| 1.0 | `7035d185d27a4629664e9a300b77870577195205bbabcd17bbaf74a9ecf4cd04` | 115152 | 154448 |
| 1.1 | `21659bde829e5ed9917a775bc438cf205ba1ed7b0309e3681eb7fd945adf2bec` | 115768 | 155552 |
| 1.2 | `f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5` | 115856 | 155632 |
| 1.5 | `244e2e9a4abb4455d271562f01d25c38a5f5e1623e9cce653bf314a76bcc5eef` | 115904 | 170672 |
| 1.7 | `6abf5745d1b2862267be16395d6fd37b46c41fc3ad4248973883f5e1db8efcc2` | 116068 | 170848 |
| 1.8 | `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8` | 116556 | 171296 |
| 1.9 | `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8` | 116556 | 171296 |

Historical PASS53 reports 1,149,744 compared bytes with zero differences in controlled unpacking. DOS 1.8 and 1.9 are byte-identical in this set. This does not extend to DOS 2.0 or gameplay behavior.

## DOS 2.0 blocker
The SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` is **previously reported**, not newly verified from the original binary in this pass. The packed original image and expanded executable were unavailable locally. A decompiled C file is not sufficient to recover original opcode bytes.

There remain **19 distinct Ghidra overlap-warning pairs**, **0/19 independently byte-decoded and reachability-verified**. Priority overlaps: `0x18DFF/0x18E01`, `0x18E04/0x18E06`, and `0x126F8/0x126F9`. These addresses refer to the Ghidra analysis address space and should not be assumed to equal original file offsets.

## P0 gates
1. Acquire original DOS v2.0 packed EXE, independently verify SHA256.
2. Reconstruct exact expanded image via original loader, compare resulting bytes against an independently reconstructed image.
3. Establish address translation Ghidra RAM -> image segment:offset -> packed-file provenance.
4. Decode conflicting i8086 instruction streams from raw bytes, then reconstruct inbound CFG edges and verify reachability.
5. Only then update individual function boundaries, pseudocode, and version-diff classifications.

New runtime cases: **0**. New machine-verified function boundaries: **0**. No parity claim is made.
