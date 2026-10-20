# Nitemare 3-D Windows 3.x — Wise Installer static audit

**Date:** 20 October 2026. **Status:** original Wise NE installer identified; Windows 1.10 game EXE not extracted or independently matched.

## Provenance

Public shareware/installation source:
https://archive.org/download/win3_Nite3d3x/win3_Nite3d3x.zip

| File | Bytes | SHA-256 |
|---|---:|---|
| win3_Nite3d3x.zip | 2,346,509 | 4d8d66d6fce0564d00e407f921957c87c6a45a5671e810450a783cb0f9ff3246 |
| INSTALL.EXE | 1,208,320 | cf92833c2606e4734737a1582fd57f307004cda9a60e5104773ef4bd9682b239 |
| INSTALL.W02 | 1,062,651 | ac736f928b9a3f76b35f58d1e96954997cccfd0982ea3d2d5dbfe3632c281338 |

Other ZIP members: DIRINFO (149 B) and WINGDLL.rar (106,577 B).

INSTALL.EXE has the MZ/NE signature for Windows 3.1, and strings containing
"WiseInst" and "%TEMP%\\WISE0002.DLL". INSTALL.W02 has no directly
recognized ZIP, Microsoft CAB, InstallShield or RAR header. It appears
to be a companion Wise installer volume, but its compression remains unknown.
A raw signature search in both files did not reveal a separate plaintext
NITE3W.EXE; absence does NOT preclude compressed content.

## Decoder tests (all static; original installer/game never executed)

- 7-Zip, unshield and cabextract could not enumerate INSTALL.EXE/W02.
- Built the open-source exwise v0.5 from https://github.com/lmop/exwise.
  Compilation succeeded, but extraction reported:
  "Unknown WISE stub version OR not a WISE installer".
- Built the open-source REWise v0.3.1 from https://codeberg.org/CYBERDEV/REWise.
  Compilation succeeded, but extraction reported:
  "Advertised WiseScript.bin size looks insane" on INSTALL.EXE;
  "not a PE file ... header signature doesn't match (not MZ)"
  when W02 was incorrectly interpreted as a standalone executable.
- REWise documentation says its known working range concentrates on
  PE Wise installers from 1999–2004; this earlier NE release need not
  follow their data layout.

These diagnostic GitHub Actions jobs succeeded as shell tasks but
**did not successfully unpack any original game executable**:
[Archive fingerprint / format](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39424758844),
[exwise v0.5](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39425208996),
[REWise v0.3.1](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39425481696).

The corresponding reproducible source workflows are
.github/workflows/win16-install-w02-forensics.yml,
.github/workflows/win16-wise-unpack-exwise.yml and
.github/workflows/win16-wise-rewise-static.yml.

## Scope against Nitemare Windows 1.10

The target Windows 1.10 EXE is 230,400 bytes, SHA-256:
12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.
Nothing above proves that the 1994-era Internet Archive installer has that
build inside. If a payload is ever extracted, it must first be fingerprinted
and treated as a distinct version if its SHA differs.

Windows 1.8 original pinned bytecode has timeEndPeriod reading WORD [BP-2]
from a fresh ENTER 6,0 local frame. In Windows 1.10, the decompiled
timer routine is textually equivalent after symbol normalization and the
five imported MMSYSTEM/USER callsite locations are all shifted +0xAE;
nevertheless exact original code at NE3:D6BB..D6BE is still unverified.
Do not claim Windows 1.10 has the same defect without its original bytes.

## Next evidence-first work

1. Prefer the already-owned exact Windows 1.10 EXE or original ZIP and run
   tools/n3d_win16_timer_binary_proof.py --version 1.10 locally.
2. Reconstruct Wise Win3.x NE installer data container + W02 header only
   if the old installation payload is independently needed.
3. Finish raw Win16 1.10 timeEndPeriod argument and fixup-backed callers
   of NE3:D66C, then do deterministic original runtime verification if needed.
4. Keep pixel/timing/behavior parity percentages unchanged until evidenced.
