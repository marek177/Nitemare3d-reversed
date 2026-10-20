# Nitemare 3D — DOS V2.0 GUARD41 terminal state0A: repeated original scheduler traversals

**Evidence:** New authentic, original unmodified DOS v2.0 **DEMO.1** runtime on 20 Oct 2026, DOSBox-X Advanced History v3 + deferred v0.65. This is **original-vs-original bounded execution evidence** and **not** a clean-room remake 1:1 parity demonstration.

## New milestone V067

Prior captures from the same original engine already verified fatal GUARD41 HP 111→0, score +100, MAP A5→00, post-death state 00→09→0A and RNG19 AX=4827. This milestone moves **beyond the state9 epilogue**: the original updates and re-visits GUARD41 in state0A.

Two independent natural-run, original CPU+memory-W recordings at **fixed 15,000 cycles**:

| Capture | Executed CPU I | Original memory W | Terminal actor update visits | DEMO clock | Actor render stamp |
|---|---:|---:|---:|---|---|
| short | 900,000 | 187,676 | 1 | 91→94 | 91→93 |
| long | 2,200,000 | 445,249 | **2** | 91→96 | 91→96 |

Both end with explicit **INSTRUCTION_BUDGET**, not SIZE_LIMIT. Long capture consists of **two rotated trace chunks from one uninterrupted session**, with a continuous instruction and event sequence. Across the two independent captures: **3,100,000 original CPU instructions + 632,925 memory W events = 3,732,925 inspected original events**.

## Exact executed CPU evidence, long capture

| Ordinal | Runtime origin | Proof |
|---:|---|---|
| 17 | 1061:0322 | GUARD41 state byte **09→0A** |
| 81/82 | 1A12:3213/3216 | RNG19 state **AEA69ED3→12DBCE4A**, AX=4827 |
| 4250→4255 | 0CEB:12B0→12B5 | State9 common epilogue and executed **RETF** |
| 969651 | 1402:037D | First later actor traversal |
| 976819 | 0CEB:0D90 | GUARD41 **AX=000A**, ES segment 2A21, BX offset 2A78 |
| 976823→976824 | 0CEB:0D9A→12B0 | **Actual indirect state0A jump** to shared epilogue |
| 976829 | 0CEB:12B5 | Executed actor-specific RETF, no new state write |
| 1759857 | 1402:037D | Second later actor traversal |
| 1766818 | 0CEB:0D90 | Same GUARD41 again has state **0A** |
| 1766822→1766823 | 0CEB:0D9A→12B0 | Second direct jump to shared epilogue |
| 1766828 | 0CEB:12B5 | Second executed RETF |

**Original MZ static corroboration:** DOS2 unpacked EXE SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` has CPU opcode `2E FF A7 A0 0D` at image offset `0x5A0A` and the indirect table at `0x5A10`. Entries for states **0A** and **0B** both target offset **12B0**. The *runtime actual branch* above confirms the state0A table entry was used on natural gameplay.

## Instrumented writes, not a global nonexistence claim

In the 2.2M I bounded interval there are only **11** recorded writes within GUARD41's 26-byte record:
- one state write **09→0A**;
- five renderer generation stamps at GUARD+02 **91→92→93→94→95→96**;
- five same-value GUARD+04 stores **0→0**.

No further instrumented GUARD41 state, HP, timer or slot-release write occurs. One associated WORLD+0x32 WORD changes **261→260** at original `130E:0259`; its complete semantics are **not** assumed. No subsequent score/map marker write is present in this bounded post-death interval.

**This proves the original GUARD actor remains allocated and state0A is a no-op in the local dispatcher for at least two subsequent measured actor traversals.** It does **not** exclude a later release/drop by other subsystems, uninstrumented memory paths or alternate class/level scenarios. It also does not establish a continuous CPU history bridging earlier state00→09 and state09→0A captures, since they originated in separate sessions.

## Provenance and verification

- Packed original DOS2 EXE SHA256 `a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485`.
- Original DEMO.1 SHA256 `25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840`.
- Built v0.65 deferred DOSBox-X ELF SHA256 `11631a6cb93bc9cbf595d63165be2072bfd76c21530e9e744430f3282d19c42d`.
- Short trace SHA256 `7fae2055be35344aa62384eb441964f8c4a34707a42f8b71ee680d0ce8af0f97`.
- Long trace chunk SHA256 `fb521dac30678d324bfeb75de854ed5239d98399de86e1ed4430599082f30184` and `8134362fc244412268c68d4a55237d686a1e70bfe5390a5eee375e1461a6da2c`.
- Private full proof ZIP: `N3D_GUARD41_TERMINAL_SCHEDULER_V067_20261020.zip`, SHA256 `da569f880d67c8d385af2c91de7c5754ddc2553dedb13d50205852530432c5dd` (49,484,820 bytes; 12 files). The ZIP contains 3 raw original CPU trace chunks, 2 event CSVs, a standalone stdlib Python verifier, screenshots, SHA manifest and detailed Slovak README. It is deliberately **not uploaded to GitHub**.
- Verifier executed locally over **all 3,732,925** I+W events and optional SHA-gated unpacked DOS2 MZ jump-table check. All pass. **20/20 synthetic normalized-evidence mutation tests rejected** correctly; synthetic mutations are not raw-trace replay or actual DOS execution.

Run with separately retained private evidence files: `python3 scripts/verify_v067.py --self-test`. For original MZ static verification add `--exe /private/N3D-UNFU.exe`.

## Next P0

**RE-first:** trace the transitive actor-slot removal, linked WORLD/OBJECT and drop writers (including SAVE/LOAD aliases) and prove whether any such callback can execute after state0A under the observed GUARD class. Runtime only where timing or indirect reachability cannot be decided. Then paired original DOS2 versus modern remake **state, framebuffer, palette and audio** zero-diff tests. Global game parity percentages unchanged.