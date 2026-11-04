# Nitemare 3D — PASS 022: extended DOS2 function tail and FAR-call entry mapping

Date: 2026-11-05

## Direct byte-level evidence
Input: DOS 2.0 expanded synthetic relocated image, size 171360 bytes; SHA256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. It was reconstructed from the original packed EXE in PASS018 and repeated with the same decoder in PASS019, **not independently verified by original-loader CPU emulation**.

GNU objdump i8086 decoded three anchored windows:
- `0x8D50..0x8EC5` (extended caller tail; start 8D50 is an arbitrary audit start, **not** a confirmed function boundary)
- `0x28F8..0x2A1F` (callee entry neighborhood)
- `0x8EC6..0x8EEB` (following function-entry candidate)

Total: **267 recorded instruction rows, 18 FAR-call sites and 20 direct branch instructions**, counted only in the three inspected windows and not as whole-program metrics.

## Shared epilogue and neighboring entry
```asm
8EC2: 5E           POP SI
8EC3: 5F           POP DI
8EC4: C9           LEAVE
8EC5: CB           RETF
8EC6: C8 04 00 00  ENTER 4,0
```
Several conditional edges in the preceding window reach the same `0x8EC2` epilogue. `0x8EC6` is a **candidate** separate function entry; callers and alternative entries have not been globally resolved.

The earlier PASS021 window ended at `0x8E20`, but the continuation contains a FAR call at `0x8E27` and conditional branch from `0x8E31` to `0x8EC2`. Thus the previous local window was incomplete by construction.

## FAR target arithmetic (synthetic loader base = 0x1000)
- `1277:0188` -> image offset `0x028F8` (`C8 10 00 00`, `ENTER 10h,0`)
- `1D29:02C0` -> `0x0D550` (`55 8B EC`)
- `1D29:03E0` -> `0x0D670` (`55 8B EC`)

Mapping formula `(segment-0x1000)*16+offset`; **do not infer runtime callee side-effects from this address resolution**.

## Verification limits and artifacts
- No FAR callee fully analyzed or emulated in this pass.
- Global overlapping-instruction conflicts closed: **0/19**.
- New gameplay runtime tests: **0**.
- No function upgraded to complete verification.

Downloadable conversation archive: `N3D_FUNCTION_RESEARCH_PASS022.zip` with `PASS022_INSTRUCTIONS.csv`, `PASS022_FAR_CALLS.csv`, `PASS022_DIRECT_BRANCHES.csv`, `PASS022_SUMMARY.json`, source windows' ASM and `pass022_build.py`. Original game executable bytes are deliberately excluded from the public GitHub commit.
