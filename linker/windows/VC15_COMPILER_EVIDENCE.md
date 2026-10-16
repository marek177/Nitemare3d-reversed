# Nitemare 3D — Win16 compiler and MFC fingerprint

**Evidence snapshot:** 2026-10-14  
**Scope:** original Windows 3.x `NITE3W.EXE` (NE), six uploaded executables, Visual C++ 1.50 and 1.52c ISOs, and additional Visual C++ 2.0/4.x/5.0 archives.  
**Evidence class:** original-binary static comparisons; no original source code recovered.

## Finding

The original Windows V1.8 and V1.10 binaries were linked with **Microsoft 16-bit Windows C/C++ runtime and static MFC 2.5-family code**. Available code fingerprints match **the `MAFXCW.LIB` shipped with Visual C++ 1.50 more closely than the 1.52c library**, including three distinctive contiguous code signatures absent from the 1.52c and 2.0-bundled older-toolchain editions inspected here. The NE linker version is 5.60.

**Crucial limitation:** `CL.EXE`, `C13216.EXE`, `C1XX3216.EXE`, `C23216.EXE`, and `C33216.EXE` are **SHA-256 byte-identical** across the supplied Visual C++ 1.50 ISO, 1.52c ISO, and `MSVC15` subdirectory on the Visual C++ 2.0 ISO. Therefore **original compiler 1.50 versus 1.52c cannot be uniquely identified from game code generation alone**. The linked MFC library looks like 1.50; the IDE and linker may have been a different patch.

## Original binaries

| Embedded version | Bytes | SHA-256 |
|---|---:|---|
| `NITE3W V1.10` | 230,400 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |
| `NITE3W V1.8` | 230,224 | `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22` |

Six uploaded Windows executables resolve to **two unique binary hashes**: five identical V1.10 files and one V1.8. Both are 16-bit Windows NE executables, with **NE linker version bytes 0x05, 0x3C = 5.60**, 10 segments, and nine import modules (`KERNEL`, `WING`, `DISPDIB`, `GDI`, `USER`, `KEYBOARD`, `COMMDLG`, `MMSYSTEM`, `SHELL`). There is no imported MFC250 DLL; MFC code is statically linked.

Both EXEs contain `NITE3W MFC Application`, `_AFX_VERSION` and MFC class names (`CObject`, `CCmdTarget`, `CFont`, `CScrollView`). These strings and the static MFC binary matches prove use of MFC/C++ in the Windows shell; the underlying game logic may still include C.

## Static MFC library comparisons (`MAFXCW.LIB`)

| Toolset | File | Bytes | SHA-256 |
|---|---|---:|---|
| VC++ 1.50 | `v1.50_MSVC_MAFXCW.LIB` | 942,169 | `2de986ed1234fe354dcbb0c91c054b7fe386447929a9da4fec77e82505a23694` |
| VC++ 1.52c | `v1.52c_MSVC15_MAFXCW.LIB` | 1,001,137 | `01c352fcf7e5b04e7dda8e90633b78585420d8019b71cce00c0690055de7f889` |
| VC++ 2.0 disc / MSVC15 | `v2.0old_MSVC15_MAFXCW.LIB` | 944,733 | `2798ddb5956d4f1aac31c36ab57b1599026584ca7262f0124ce1cbb86b62163e` |

### Contiguous code matches within NE code segments

Lengths count exact non-overlapping runs >=32 bytes, discovered by 24-byte anchors and extension to the maximal available exact match. **These are analytical comparison scores, not full program coverage or a code equivalence proof.**

| Library | V1.10 match runs | V1.10 summed bytes | V1.8 match runs | V1.8 summed bytes |
|---|---:|---:|---:|---:|
| Visual C++ 1.50 `MAFXCW.LIB` | 426 | 22,959 | 426 | 22,957 |
| Visual C++ 2.0 ISO `MSVC15/MAFXCW.LIB` | 421 | 22,721 | 421 | 22,719 |
| Visual C++ 1.52c `MAFXCW.LIB` | 413 | 22,291 | 413 | 22,289 |

### Three version-discriminating signatures

The following 64+ byte signatures are present verbatim in both original executables and in **Visual C++ 1.50** `MAFXCW.LIB`, but absent as contiguous byte sequences from the **1.52c** and **2.0-bundled `MSVC15`** `MAFXCW.LIB` tested. Library provenance names derive from OMF `THEADR` module boundaries. File offsets are absolute (not `CS:IP` runtime addresses).

| MFC OMF module | Exact bytes | NITE3W V1.10 file offset | NITE3W V1.8 file offset | VC++ 1.50 MAFXCW file offset |
|---|---:|---|---|---|
| dcprev.cpp | 112 | `0xBB72` | `0xBB5E` | `0x2FFB5` |
| winfrm.cpp | 68 | `0x78DE` | `0x78CA` | `0x22294` |
| dcprev.cpp | 66 | `0xBA08` | `0xB9F4` | `0x2FE4B` |

**Independent comparison outcome:** in the tested runs >=64 bytes, three signatures are specific to 1.50 relative to both alternative `MAFXCW.LIB` editions; there were no equivalent signatures found to be specific to 1.52c relative to the other two. This supports older MFC linking. It does not prove the original programmer installed *only* Visual C++ 1.50.

## CRT and compiler identity

The three versions' `MLIBCAW.LIB` are byte-identical with SHA-256 `76742685bb8dd714c6d97c9e5ec04c453c06ee6942ec200b586b6e8014027c01`. The executable has long CRT exact matches with this library, including examples of 334, 300 and 277 contiguous bytes in code segment 2. CRT matches establish the toolchain family but **cannot discriminate revisions** where CRT bytes are identical.

| 16-bit compiler stage | SHA-256, identical across 1.50 / 1.52c / MSVC15-on-2.0 |
|---|---|
| `CL.EXE` | `e228f976c4d0c1d668e4259195ad4feca73ab87b99f26fb168f7e3fbd5992627` |
| `C13216.EXE` | `f81c6d5daff5e46acb35ba529f48f792336a116f7099ee943c5fee0dd6c4e951` |
| `C1XX3216.EXE` | `2e0f8330dd3410a2393aa32b379d51e97a84bbf0f389f5c045696fe0bf2b1f76` |
| `C23216.EXE` | `2350c5189a2adcf542f3428aa2a7c0c51d8f85e5e20a186b84b6a59fc63882cf` |
| `C33216.EXE` | `988e9f9e8b08895597b7a7abbbfe86ba379ebb5e71ade2a73e09e19b044adf94` |

`LINK.EXE` differs between the CD editions: Visual C++ 1.50 (`64daf6bed43d2536`) versus 1.52c (`d588036a7446bf0d`). The latter embeds `Microsoft (R) Segmented Executable Linker Version 5.60.339 Dec 5 1994`; the former identifies the segmented linker as 5.60. The NE header records only 5.60, so it does not distinguish them.

## Other supplied toolchains

- **Visual C++ 2.0 ISO:** main `MSVC20/BIN/CL.EXE` and `LINK.EXE` are PE-format Win32 programs. The disc additionally contains an older `MSVC15/` 16-bit toolchain, relevant to Win16 binaries.
- **Visual C++ 4.0 archive:** Disc 1 has PE `MSDEV/BIN/CL.EXE`; Disc 2 is a separate `MSVC152c.iso`, providing the legacy 16-bit toolchain. The 16-bit CRT and compiler files are equivalent to the independent 1.52c ISO in checked binaries.
- **Visual C++ 4.1 / 4.2 / 5.0 ISOs:** principal `CL.EXE` and `LINK.EXE` are PE programs, with Win32/MFC4x libraries; no checked `MSVC15` 16-bit static toolset present. Their direct compiler output is not a plausible source of this NE-format executable, absent use of separate historic 16-bit tools.

## Conclusion and 1:1 implications

**Best defensible label:** `Microsoft Visual C++ 1.5-generation 16-bit compiler + linker 5.60 + static MFC 2.5, with MFC code matching the Visual C++ 1.50 distribution`.

1. Do not overlabel this as *definitively VC++ 1.50 compiler*. The 1.50, 1.52c, and bundled 16-bit 2.0-CD compiler executables are identical.
2. In code recovery, tag identified `MAFXCW.LIB` MFC routines and `MLIBCAW.LIB` CRT as compiler/framework support, not Nitemare-specific game logic.
3. To identify the exact linker build, build a controlled fixed-object Win16 test against the vintage linkers, compare the full NE headers / relocation conventions / startup and library inclusion order, and test any discriminating behavior against V1.8 and V1.10. The current 5.60 header alone cannot decide.
4. These results do not identify the DOS executable's compiler; that is a separate Microsoft C/C++ 7.0-family runtime analysis in the 2026-10-11 archive.

**Methodological note:** Static executable and original-library byte inspection only; no emulated compilation or live gameplay/runtime trace was carried out in this pass.
