# Nitemare 3D — PASS 016: original EXE verification

Date: 2026-11-04

## Directly checked source
The previously uploaded `dosbox-n3d(20261103-105917).zip` was retrieved from the user's file Library. The archive SHA-256 is `9105bb79faba1e523fc9bb809d404b5fa4dc6ed3eeee172d021ce7efb3cab9a2`.

The archive contains 20 MZ EXE entries, 14 distinct hashes, with 11 DOS MZ and 9 Windows NE entries. This includes several duplicates.

### Reference originals (direct SHA-256)
- DOS 2.0 `nite3/dos/N3D-E-20.EXE`: 116606 bytes; SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Windows 1.10 `nite3/windows/nite3w - 110.exe`: 230400 bytes; SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

### DOS packed header
DOS 2.0 MZ header = 512 bytes; standard MZ relocation count = 0; initial CS:IP = `1B72:0010`; initial SS:SP = `2ABC:0080`. Packed loader entry in the load image = `0x1B730`, raw-file offset `0x1B930`.

### Windows NE segment table
Win16 1.10 NE header at raw file offset `0x80`; 10 logical segments, alignment shift 4. NE initial CS:IP = `02:3718`. NE segment 2 starts at raw-file offset `0xE8A0` and its declared file length is 29694 bytes. These are exact file metadata decoded from the original EXE bytes, not runtime selectors.

## Critical evidence distinction
The original DOS 2.0 packed executable is now **available and independently hashed**. However the packed stub has not yet been emulated and no expanded original image has been produced during this pass. Consequently, `0x18DFF/0x18E01`, `0x18E04/0x18E06` and `0x126F8/0x126F9` are **not machine-closed**. Ghidra addresses must not be treated as physical file offsets without explicit mapping. None of the 19 overlap-warning pairs is resolved yet.

The historic PASS53 script uses Unicorn, which was not installed in the local Python environment during PASS016. The currently produced audit does not claim original-code execution or runtime parity.

## Outcomes
- Directly verified original EXE files: DOS 2.0 and Win16 1.10, plus other archived EXEs.
- Independent MZ and NE metadata extraction: completed.
- Full DOS2 expansion/relocation replay: pending.
- Newly confirmed function boundaries: 0.
- Overlap conflicts closed: 0/19.
- New gameplay runtime tests: 0.

The audit CSV/JSON and reproducer are in the conversation artifact `N3D_FUNCTION_RESEARCH_PASS016.zip`. Original copyrighted executables are **not** uploaded to GitHub.
