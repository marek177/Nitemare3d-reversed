# Nitemare 3D DOS v2.0 — V081 fresh E1M1 live original-player runtime

**21 Oct 2026. Evidence: FRESH_ORIGINAL_DOS2_EXECUTION + READ_ONLY_GUEST_RAM observation.** This is **not** original-vs-remake behavior parity nor 64,000-pixel framebuffer parity.

## Provenance

- Unpacked original `N3D-E-20.EXE`: SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` (116606 bytes).
- Original `IMG.1` SHA256 `faf0cec3502d8b86ebb30a432b46b467e349864987f91a1c26358a9a5ca58cb1`; `MAP.1` SHA256 `3eddb0ad3a29e93d63fa16e9b8cfbb434d3699a84bd5372ed2d6f4a1e89c42fc`.
- Actual original EXE loaded into Linux DOSBox-X 2026.10.01 N3D Advanced History v3 and navigated to E1M1. Guest RAM base identified using an 18-byte original FEFA machine-code signature and independently checked against the 1021E image. Real-mode DS=2F95.
- X11 XTest input held/released **Up, Down and Right**, while a read-only Linux /proc/PID/mem sampler polled actual DOS2 DS:4162/4164 player position, DS:4156 heading, DS:41B2/41B4 Q10 trig, and DS:4540 render counter every ~11–12ms.
- No original executable, MAP, IMG, DEMO, guest RAM, or proprietary original trace bytes are distributed by this repository. The full private derived 5-CSV/JSON evidence, lab scripts and optional original screenshot remain in a user-local artifact ZIP, SHA256 `8bbeb1e440457cae82eaa2a2672248fb62169f2632dff17a35d7245ea08532c2`.

## Original runtime behavioral observations

| Controlled original game input | Actual guest-memory result |
|---|---|
| Idle | XY stays (1440,3396) |
| Hold Up from (1440,3396) | 9× Y−11, then a shorter −6 step, stopping at **Y=3291** |
| Release Up | XY stays (1440,3291) while render counter advances 36 |
| Hold Down | 24× Y+11, returning to Y=3555 |
| Release Down | XY stays (1440,3555), render counter +33 |
| Repeat Up from Y=3555 | 24× Y−11, returning to **Y=3291** |
| Hold Up at contact | **171 read-only memory observations** all at (1440,3291); rendering counter advances **38** |
| Hold Right | **27 increments of +6 angle units**, heading 0→162, XY unchanged |
| Release Right | heading stays 162, Q10 sine/cosine **(316,−973)** |
| Hold Up at heading162 | XY **(1440,3291)→(1474,3492)**, net (ΔX=+34, ΔY=+201); position stable after release |

The Y=3291 contact is repeatable. The last 6-unit forward step strongly suggests collision clipping, but the precise blocking MAP surface and collision predicate have **not** yet been shown instruction-for-instruction. Raw XY polls can straddle separately written X/Y words; do not promote each intermediate 2D sample as an atomic guest game tick. Host milliseconds are not deterministically equivalent to the game's clock.

An initial test with accidentally repeated key-downs during the release phase was discarded; its contaminated release observations are **not** included in the accepted 5-CSV evidence set.

## New original renderer state at another camera angle

After movement and rotation, an original DS snapshot was accepted only with a stable DS:4540 frame counter and **304 aligned valid near owner pointers**, with contiguous DOS2 18-byte span runs:

- Position **(1474,3492)**, angle **162°**, Q10 trig **(316,−973)**.
- Active VEC **592**, owned screen columns **304/304**, **three** spans across X `8..110`, `111..222`, `223..311`.
- Real original owner SHA256 `dbaaa6411a9fea206eac6db8e7e68c140eda1bd16e76d1d1f27909d64a09dd89`.
- Real original active span SHA256 `24043e0acff7532e6c2b6aaeb1515c054e1a65d83eb676efc99720f4769b8ec2`.

The existing **compiled native C++20** `n3d_dos20_wall_replay` was then executed with that original DS and corresponding original IMG.1, using an **explicit synthetic zero-valued background**. It produced **304 wall columns**, **26,764 generated wall pixels**, three spans, and no invalid IMG frame selection. **wall_pixels_compared=0; wall_pixel_mismatches=null; no original post-wall framebuffer was available at this exact camera state.** Successful rendering does not imply byte-perfect output.

## Next statics/runtime blockers

1. Identify the actual MAP surface and exact binary collision check producing forward stop at Y3291, including why the last update is −6 and normal updates −11.
2. Port/tick-align X/Y movement, heading increments and collision response in the remake; record first original↔port divergence using the same world state and input key ledger.
3. Compare the new original 3-span scene to a same-tick authentic BF5F post-wall indexed frame. The 531 pixel differences found in a **different** E1M1 state remain a separate, unresolved renderer case.
4. Production `src/renderer/Raycaster.cpp` DDA and `src/main.cpp` remain untouched.

**Reproducibility:** private evidence includes 5 SHA-pinned CSVs, integrity validator, native wall output, machine-readable summaries, and original screenshot; only derived facts and hashes are public here.
