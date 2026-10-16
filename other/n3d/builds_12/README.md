# 12 original Nitemare 3D binaries: statically verified audit (2026-10-16)

See [12-build report](N3D_REMAX_12build_original_BYTE_STATIC_AUDIT_2026-10-16.md)
and [original-free evidence tables](static_byte_evidence/).
The 9,811-entry DOS relocated FAR CALL CSV is distributed as deterministic
`static_byte_evidence/N3D_DOS_reloc_anchored_FAR_CALLs.csv.gz` to keep the
repository small; decompress it to obtain the original 441,570-byte text table.
Includes seven DOS (1.0/1.1/1.2/1.5/1.7/1.9/2.0) and five Win16
(1.0/1.3/1.6/1.8/1.10) **binary identities**. These do not imply an
exhaustive historical release census nor gameplay runtime parity.

- `n3d_re_12build_byte_audit.py`: optional read-only verifier that requires
  user-provided original binaries, checks SHA-256 and EXEPACK/NE structures.
- `static_byte_evidence/`: generated JSON/CSV indices only, no raw code image.
- `N3D_REMAX_StaticPrimitives_12build.hpp` +
  `n3d_remax_static_primitives_test.cpp`: C++17 synthetic models/tests.

Hash domains: DOS = unpacked, unrelocated MZ load image; Win16 = whole
original NE executable. The 11,856 reported FAR CALL records include repeated
sites across versions, not 11,856 unique engine functions. Full CFG, indirect
calls, hardware and time-sensitive behavior remain OPEN.
