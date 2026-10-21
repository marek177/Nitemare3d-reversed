# Nitemare 3D DOS v2.0 — fresh E1M1 combined-key release runtime, V082

**21 October 2026 · Evidence: LIVE ORIGINAL DOS2 EXECUTION, XTest keyboard events, read-only `/proc/PID/mem` guest memory. NOT remake or pixel parity.**

## Identity

- Original unpacked DOS v2.0 `N3D-E-20.EXE`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Unmodified DOS `IMG.1`: `faf0cec3502d8b86ebb30a432b46b467e349864987f91a1c26358a9a5ca58cb1`; `MAP.1`: `3eddb0ad3a29e93d63fa16e9b8cfbb434d3699a84bd5372ed2d6f4a1e89c42fc`.
- Original guest code signatures at load-image offsets `FEFA` (18B) and `1021E` (16B) matched live DOSBox-X RAM. Guest DS `2F95`; player XY `DS:4162/4164`, raw heading `DS:4156`, trig Q10 `DS:41B2/41B4`, render counter `DS:4540`.
- Input was real X11 XTest key-down/up for **Up and Right**, not editing game RAM. All six transitions were accepted. **276 memory observations** were saved to SHA-verified CSV and phase JSON. Files in the user's private ZIP; no original EXE, textures, RAM or framebuffer are committed here.

## Original actual run — combined input and sequential key releases

| Input phase | Player XY initial → final | Heading initial → final | Render-counter advance | Samples |
|---|---|---|---:|---:|
| No keys | (1474,3492) → (1474,3492) | 162→162 | 3 | 13 |
| **Up+Right simultaneously** | (1474,3492) → (1480,3492) | 162→174 | 2 | 18 |
| Up held after Right released | (1480,3492) → (1481,3492) | 174→174 | 1 | 17 |
| Both keys released | (1482,3492) → (1482,3492) | 174→174 | **19** | **101** |
| Right only | (1482,3492) → (1482,3492) | 174→216 | 7 | 58 |
| Right released | (1482,3492) → (1482,3492) | 216→216 | **8** | **69** |

**Observed outcomes:** simultaneous Up+Right changes player position AND raw angle. Holding Right alone rotates without changing player XY; seven observed heading increments are each +6. After releasing both buttons, position and heading remain stable for 101 samples while renderer advances by 19. After releasing the final Right button, heading remains stable for 69 samples while renderer advances by 8.

**Important boundary:** the first sample in the "both released" phase had X=1482 versus X=1481 at the end of Up-only, i.e. a **last +1 X update near the release transition**. This is not proof of instantaneous key cancellation; it may be a previously queued original game update. Further CPU/tick-level input ordering tracing is necessary.

**Timing limitation:** this particular original host session experienced up to **553 ms** between successive memory observations; its initial combined-input phase advanced only two render-counter units. Host wall-clock duration and sampling resolution therefore must not be confused with deterministic original guest ticks. Polling of player fields and timer is not an atomic guest instruction checkpoint.

## Relationship to preceding live E1M1 tests

The immediately preceding independently preserved real DOS2 motion test confirmed Up release at XY (1440,3291), a sustained block at Y=3291 with renderer still ticking, Down release at (1440,3555), right-only raw angle steps +6 and a diagonal movement to (1474,3492) after rotation to angle 162. V082 then starts from that measured player state. This is original engine behavior evidence only, not remake comparison.

## Reproduce / data integrity

Private artifact `N3D_DOS20_LIVE_E1M1_Combo_Input_Release_V082_20261021.zip` contains the actual original runtime test automation, complete CSV, JSON report, SHA256SUMS, a strict offline validator and Slovak report. The offline validator checks the six accepted transitions and both post-release stationary windows; **it is not a replacement for a real emulator run**. Original game files are not part of the artifact.

- Captured CSV SHA-256: `5f8605ffd32f0f516b0ba0cad0139621cc35b4380e69f4ab352d03b5c640dcc8`.
- ZIP SHA-256: `8c33e70843590d7c8a191e8892f4e306e62264081871de22bdafa855ce1dc84a`.
- The active DOSBox-X process was no longer present at the final follow-up check after test completion, so **no further live-process claim is made**.

## Next original runtime obligations

1. Capture keyboard mask and player movement/scheduler **at the instruction-level before/after Up or Right release** and distinguish queued movement from a newly applied key state.
2. Repeat simultaneous movement/turn with a fixed **guest-clock** test horizon, not just host wall time, at multiple headings and blocked vs unblocked positions.
3. Compare original vs remake at identical key event tick stream, including fixed-point step, collision clamp, input autorepeat and release behavior.
4. The rendering pixel-parity gate (64,000 indexed bytes + 768 RGB6 DAC) is **entirely separate** and remains OPEN. The live DDA preview is unchanged.
