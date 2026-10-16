# Historic compiler/linker provenance — Nitemare 3-D

This is an **evidence inventory**, **not** the game's original build tree and
**not** a redistributable copy of Microsoft toolchains. It is deliberately split
into [DOS](dos/) and [Windows 3.x / Win16](windows/).

- `dos/` — C/C++ DOS Medium-model CRT, linked module fingerprints and the
  hypothesized compiler/linker tool family.
- `windows/` — Visual C++ 1.5-generation 16-bit compiler files, linker 5.60,
  statically linked MFC 2.5, Win16 CRT and direct NE imports.

`FILE_CATALOG.csv` lists historic filenames, evidence level and whether an
artifact is actually provided. **No original `.EXE`, `.LIB`, `.OBJ` or Microsoft
`.ASM/.CPP` files are included.** Fingerprints do not prove that a particular
library pathname appeared in the author's linker command. No original Nitemare
`.MAK` / `.PRJ` / link response / complete OBJ roster has been found.

The purpose is historical RE provenance. The Windows 11 remake does not need
these vendor tools to build. Verify exact binary identity and matching algorithm
before attributing compiler-internal routines to game logic.

Evidence terminology: `B` = game EXE byte evidence; `L` = library fingerprint;
`T` = tool distribution file; `R` = runtime NE import, not proof of linker input;
`H` = historically plausible but unproven. Source: 2026-10-11 through 2026-10-15
static audit, preserved in the platform-specific reports.
