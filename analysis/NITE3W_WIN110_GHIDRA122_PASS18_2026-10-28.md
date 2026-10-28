# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 18

## Finding

Recovered exact damage arithmetic and checked it by isolated execution of the original16-bit function in Unicorn2.1.4:14061 cases matched the independent model. Damage uses target stored projection depth, consumes RNG even in zero-result branches, applies signed shifts and only an upper cap. The caller discards AH, so negative AX can become a large unsigned damage byte. Normal-game reachability of pathological inputs remains unverified.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; Ghidra12.2 PUBLIC20261016,JDK25.0.2. Isolated original-code execution is distinguished from a full Win16/game runtime test.

## Arithmetic and evidence

Confirmed / High,1010:9FA2..A0C4:

1. Read signed WORD target object+18h through its far pointer; subtract WORD DS:53EE modulo16, SHL3 modulo16.
2. Call1018:32D2 exactly once; signed IDIV25, add remainder modulo16. Original proxy calls6EC8, whose returned range is masked7FFFh. Microexecution stubs RNG in0..32767; original PRNG state transition is not executed.
3. Type byte object+6, current selected weapon4C23 and episode WORD7E52 choose the transform below.
4. Difficulty WORD4C14==2 -> arithmetic shift right1; ==0 -> double modulo16; other values leave it unchanged.
5. Signed result>255 ->255. There is no lower clamp. Return fullAX.

Base B is signed16(((targetDepth-baseline)*8 + RNG%25) mod65536). Every shift below is arithmetic on signed16. Difficulty adjustment and cap follow constants/zero branches as well.

| Target type | Transform of B |
|---|---|
| 0C,1D | B SAR3 |
| 0D | weapon1: SAR1; otherwise SAR3 |
| 0E,11,14 | weapon2: SAR1; otherwise SAR3 |
| 0F,10 | weapon1: SAR8; otherwise SAR1 |
| 12,13 | SAR2 |
| 15 | call083E(DWORD DS:0192), then0 |
| 16 | episode3:3; otherwise0 |
| 17 | weapon1: SAR8; otherwise SAR2 |
| 18 | weapon1: SAR8; weapon2: SAR4; otherwise SAR3 |
| 19 | 0 |
| 1A | weapon1: SAR1; otherwise0 |
| 1B,1C | SAR1 |
| 1E | weapon1:0; otherwise SAR3 |
| 1F | weapon1:0; otherwise SAR2 |
| Other | B unchanged |

Do not rename type IDs to enemy names without asset evidence. All branches consume the RNG call before switching, including0,constant3 and the083E path. The083E side effect is stubbed; only its occurrence and exact DWORD argument are checked.

## Caller and stored depth

Confirmed / High,80F8 at8114 explicitly XORs AH,AH. It compares target health byte+10h with the resulting unsigned AL damage. Health<=damage takes the lethal branch; this includes0<=0 if such a target reaches the routine. Otherwise damage0 returns without subtraction, and positive damage subtracts before reaction branches. Those subsequent kill/reaction/score routines are not emulated here.

Example checked with original instructions: default target type, normal difficulty1, target depth0, baseline1,RNG0 -> AX=FFF8h. Caller interprets AL=F8h (248), not zero. This proves arithmetic for the controlled input, not an observed normal-game248-damage incident. Negative and extreme depth fixtures deliberately exercise width/sign behavior; local wrapping and absence of a lower cap must not be replaced with a floating-point distance formula.

The depth field object+18h is written by successful CC7C render-queue insertion (pass17,CE5E). Damage reads that stored field instead of recomputing physical distance. This establishes a static dependency on the last stored depth, potentially older than the current frame when insertion was skipped. The object supplied to damage is the target, not automatically the projectile's embedded object. Actual age/validity of a target depth and visible gameplay consequences require runtime tracing.

## Original-instruction verification

`scripts/emulate_pass18_damage.py` copies the original EXE function including its CS jump table, applies exactly two internal NE selector fixes to1018, and compares every Ghidra-listed instruction byte in the function to that relocated image. It then executes original instructions in Unicorn16-bit mode with controlled real-mode segmented memory, far calls and RETF.

RNG at1018:32D2 returns a selected test value;083E is a RETF stub that checks its DWORD stack argument. Sentinel far return confirms completion; SP is checked for the original cdecl far return behavior. No instruction of the damage function is replaced by the model.

-14061 cases:20 switch types plus three default types, all four valid weapons, difficulties0/1/2, episodes1/3, five depth/baseline fixtures and five RNG samples; additional all256-type sweep and examples.
-2277 fixtures returned negativeAX, all matching the model.
-Every case consumed exactly one RNG call; type15 consumed the expected083E call with checked argument.
-32768 simple remainder-range arithmetic checks supplement, but are not original-code executions.

RNG state advancement,083E implementation, full damage application, target pointer aliasing, API behavior and Windows execution are excluded. The tests establish bounded original-instruction/model agreement, not complete runtime parity.

## Ghidra and coverage

Annotated three existing functions, full native export completed and project saved. Initial export was interrupted by an executor restart; the recovery export supplies the completed inventory/save evidence.1551 internal function entries remain, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked. Coverage unchanged:160005 instruction bytes,8282 data bytes,1401 undefined bytes. No new functions, padding typing or executable patches. Successful decompilation alone does not certify signatures or semantics.

## Unknowns and next test

Run the original Win16 build with a moving target and trace its CC7C depth writes followed by9FA2 reads, recording visibility and frame order. Capture RNG state and selected weapon at actual impact. Execute80F8 and its kill/reaction callees with real target records to verify health, score and map side effects. Identify target type IDs against assets. In-game stale-depth consequences, complete damage application and overall1:1 parity remain unresolved.

## Confidence

High for the modeled function's arithmetic and caller low-byte interpretation, supported by original-instruction microexecution. Full-game/runtime tests:0.
