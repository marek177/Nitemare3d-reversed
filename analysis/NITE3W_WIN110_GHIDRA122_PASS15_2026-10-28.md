# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 15

## Finding

Resolved push direction bytes, heading-index setup, exact quadrant lookup tables and activation sound dispatch. DS:4BEC is a direction index, not a pointer to a direction object. The two trig quarter tables differ at one mirrored sample and must both be preserved. No runtime parity claim.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016,JDK25.0.2.

## Direction evidence

Confirmed / High: E516 stores heading atDS:4BEA, adds360 once if signed negative, then subtracts360 once if signed>=360. Stores signed quotient heading/45 to4BEC. Valid post-normalization domain0..359 is guaranteed for input-360..719 only. This is not arbitrary-input modulo normalization; values outside this range can leave the trig/direction index domain. Additional writes to4BEC exist (player reset and load path), so this setter alone does not prove every runtime value is valid.

Push activation21B6 uses the index as DS:00A4[index] for dx and DS:00AC[index] for dy. The raw signed-byte tables are:

| Index | Heading range after normalization | dx | dy |
|---|---|---:|---:|
| 0 | 0..44 | 0 | -8 |
| 1 | 45..89 | 8 | 0 |
| 2 | 90..134 | 8 | 0 |
| 3 | 135..179 | 0 | 8 |
| 4 | 180..224 | 0 | 8 |
| 5 | 225..269 | -8 | 0 |
| 6 | 270..314 | -8 | 0 |
| 7 | 315..359 | 0 | -8 |

The push direction is cardinal with boundaries45/135/225/315. Eight accepted steps sum to64 coordinate units on one axis. Under valid map coordinates this corresponds to the64-unit cell geometry recovered in pass14. This is not a guarantee that every activated push completes: blocked steps retain remaining count, and invalid edge access/callbacks are not modeled.

E516 also stores `(1 << directionIndex) &99h` to4BF0. A separate rounded octant4BEE is computed from the doubled WORD heading, signed IDIV45, INC AL, AND0Eh, SAR1. For valid angles its intervals are0..22 ->0,23..67 ->1,68..112 ->2,113..157 ->3,158..202 ->4,203..247 ->5,248..292 ->6,293..337 ->7,338..359 ->0. Do not substitute this rounded index for the push-table index.

## Exact trig lookup

Confirmed / High, ECAC and ECF8: separate91-WORD signed tables atDS:025E..0313 and0314..03C9, endpoints0/1024 and1024/0. For valid angle a:

| Angle | ECAC output | ECF8 output |
|---|---|---|
| 0..89 | S[a] | C[a] |
| 90..179 | S[180-a] | -C[180-a] |
| 180..269 | -S[a-180] | -C[a-180] |
| 270..359 | -S[360-a] | C[360-a] |

Sine/cosine names are inferred from quadrant structure and endpoint scale; literal results are confirmed. `S[30]=512` while `C[60]=511`. This is the only mismatch among all91 reverse-table comparisons. A single synthesized reversed quarter table would change the executable's numeric results; ideal floating-point trig or a newly rounded table is not a demonstrated replacement.

E516 stores ECAC/ECF8 results at4C46/4C48, then derives additional error terms. Those later terms are outside this pass's numerical model; no raycaster/pixel parity is inferred from the trig lookup alone. Complete literal quarter arrays and all360 pairs are preserved in the verification JSON.

## Activation sound

Confirmed / High, ACDC: pushes DWORD00020000h and WORD0043h, calls E3B0 and cleans six argument bytes. This follows21B6's remaining8 write. Sound/sample identity, playback success and precise timing remain Unknown. The hex command43h is not assigned an asset name.

## Validation

- Original hash, raw heading arithmetic/rounded-index spans and sound argument pushes checked.
- All65536 signed-WORD input representations checked for single-adjust normalization;1080 inputs produce0..359.
- All360 valid headings checked for cardinal table step, rounded octant and two exact quadrant outputs using a separate fold/index formulation.
-2520 eight-accepted-step arithmetic fixtures, including map-coordinate boundaries. Wrap fixtures prove the mathematical model only, not legal map access.
- All91 quarter-table mirror pairs checked; exact one-unit asymmetry retained.
- Ghidra annotated five existing functions, completed full native export and saved project.1551 internal entries remain, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked.

Coverage remains160005 instruction bytes,8282 defined data bytes,1401 undefined bytes. No binary patch or new code/data classification. Models are static and do not execute original instructions, APIs or rendered frames.

## Unknowns and next test

Capture4BEA/4BEC/4BEE and21B6 dx/dy at boundary angles44/45,134/135,224/225,314/315. Step eight accepted moves and a blocked move to verify displacement and remaining count in runtime. Trace load writes to4BEC for validation. Compare ECAC(30) and ECF8(60) in the original runtime before deciding on a trig replacement, and inspect later E516 error terms before making renderer claims. Identify sound43h against supplied sound resources. Full movement/render/audio parity remains unresolved.

## Confidence

High for literal tables, valid-domain lookup/indices and sound call arguments; runtime state validity, audio identity and whole-game parity remain open. Runtime tests:0.
