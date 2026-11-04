# Nitemare 3D — PASS 019: DOS 2.0 expanded-image reproducibility and local CFG witnesses

Date: 2026-11-05

## Reproducibility
Re-executed PASS018's Python decoder against the **original** DOS 2.0 EXE from the user-provided DOSBox archive, then compared every byte against the saved PASS018 expanded load-base-0x1000 image. **171,360/171,360 bytes match.**

- Original packed DOS2 SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- Synthetic relocated image SHA-256: `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`
- Decoder output: 158 blocks, 82,274 decompressed stream bytes, 1,670 relocation writes.

**Important:** this is repeatability of the SAME decoder, **not** an independent CPU-executed original loader or independent unpacker.

## Direct relative branch witnesses from reconstructed bytes

```asm
8DE9: 74 0D            JE 8DF8
8DF5: EB 0D            JMP 8E04
8DFA: 9A 88 01 77 12   CALL FAR 1277:0188
8DFF: 83 C4 02         ADD SP,2
8E02: 2C 05            SUB AL,5
8E04: 88 46 FF         MOV BYTE PTR [BP-1],AL
26F4: 9A CE 04 56 11   CALL FAR 1156:04CE
26F9: 83 C4 0E         ADD SP,0Eh
```

The two short branch targets were independently recomputed using signed rel8 displacement arithmetic on source bytes. On these local decoded paths `8E01` is inside the immediate of `ADD SP,2`; `8E06` inside the displacement of `MOV [BP-1],AL`; `26F8` inside the FAR segment operand. **Correction of PASS018 phrasing:** `26F9` is *not* inside the FAR CALL; it starts the following `ADD SP,0Eh`.

## Verification limits
19 reported overlap pairs are preserved, 17 have candidate code-space byte mapping, two still need segment mapping. These are **local instruction decoding witnesses only**. No global inbound-CFG or alternative-entry exclusion was performed. **0/19 overlaps are globally closed; zero new gameplay runtime tests.**

The cumulative downloadable `N3D_FUNCTION_RESEARCH_PASS019.zip` includes `PASS019_OVERLAP_STATUS.csv`, `PASS019_DIRECT_BRANCH_WITNESSES.csv`, `PASS019_8DE5_8E15.objdump.txt`, `PASS019_VERIFICATION.json`, `PASS019_REPORT.md`, and `pass019_build.py`. Original EXE and expanded image remain private and are not committed here.
