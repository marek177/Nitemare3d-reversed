# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 8

## Finding

Repaired a real instruction/function-boundary error at `1008:3C80`, recovered its CRT error-string lookup and the allocation-failure callback `1000:076A`. Independently modeled the lookup and error translator across all 16-bit inputs. This is static recovery, not runtime or 1:1 parity certification.

Input: `nite3w - 110.exe`, 230400 bytes, SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra 12.2 PUBLIC 20261016, JDK 25.0.2. No executable bytes patched.

## Evidence

| Status | Claim | Primary location | Confidence |
|---|---|---|---|
| Confirmed | Calls at 3C48 and 3CCD targeted 3C80 inside an erroneous four-byte instruction beginning 3C7F | Code2 listing/reference exports before/after | High |
| Confirmed | Fatal routine ends in CALL FATALEXIT at 3C7A..3C7E; byte 3C7F is outside the repaired body; 3C80 begins MOV AX,DS | Code2 bytes; bounded repair script | High for boundary; external termination behavior not runtime tested |
| Confirmed | Lookup reads WORD ID then NUL-terminated bytes, advances to next record, returns first matching payload pointer or zero on unmatched FFFF sentinel | 1008:3C80..3CB6; DS:2242 table | High |
| Confirmed | Compare precedes sentinel test: requested FFFF returns DS:23CF, immediately after sentinel DS:23CD | 3C95..3C9B; exhaustive model | High |
| Confirmed | Mechanical traversal reads ASCII `AB` of `ABNORMAL PROGRAM TERMINATION` as little-endian ID 4241 and returns payload `NORMAL PROGRAM TERMINATION` for that key | DS:2388..23A4; model | High for bytes/traversal; intent Unknown |
| Confirmed | Error translator first writes original AL to byte DS:086E. AH != 0 bypasses table and stores sign-extended AH to word DS:085E | 1008:3D59..3D7E | High |
| Confirmed | AH=0: indices 0..19 retained; 20..31 and 34..255 use 19; 32/33 use 5; table byte is sign-extended into DS:085E | Same; DS:08B8..08CB | High |
| Confirmed | 0772 installs callback far pointer 1000:076A through 601A -> 5FF0, replacing DS:094A/094C | 1000:0777/077A; 1008:5FF0..6023 | High |
| Confirmed | Setter returns prior callback in DX:AX; old decompiler C displayed only AX and therefore omitted material ABI information | 1008:6010/6013 | High |
| Confirmed | Allocator failure invokes nonzero far pointer DS:094A/094C with size argument, cleans argument, retries if AX != 0; zero stops | 1008:5AEA..5AFF | High |
| Confirmed | Callback calls 1000:4564, then XOR AX,AX; RETF on normal return | 1000:076A..0771 | High |
| Inferred | Setter/callback are CRT new-handler-style allocation failure handling, linked into framework exception machinery | allocator + callback -> 4564 -> 4492 -> THROW path | Medium; original names and complete exception ABI unavailable |

## Behavior model

Lookup assumes DS is initialized, DF=0, and strings/table terminate before segment wrap. It receives key at BP+6, returns near DS offset in AX, and uses RETF 2. Ghidra's generated function prototype still guesses extra arguments; use instructions for the ABI. The table has twelve mechanically traversed records, including the anomalous ASCII-derived ID 4241. That record is not described as an intended documented runtime error.

IDs encountered in order: 0, 3, 9, 18, 20, 8, 21, 252, 255, 2, 4241h, 25, then FFFF. The verification JSON contains exact record/payload offsets and strings. Do not treat byte 3C7F as proven alignment merely because it is now left undefined.

The translator lookup bytes are `00 16 02 02 18 0D 09 0C 0C 0C 07 08 16 16 FF 02 0D 12 02 FF`. Returned/stored FF is sign-extended to FFFF, not 00FF. Error-state names `errno` / DOS-error-like storage are inferred; exact byte/word writes are confirmed.

Callback normal return zero causes the allocation routine to stop retrying. If downstream exception code transfers control, that normal-return rule does not describe the exceptional path. No exception execution was performed.

## Validation

- Raw EXE hash, exact 55-byte lookup and 38-byte translator bodies checked independently of decompiler output.
- 65536 lookup keys compared against separately constructed first-match mapping, including FFFF and ASCII-derived ID.
- 65536 AX values checked for translator output byte/word states against independent specification.
- Full explicit unconditional-call offcut audit: two references before, zero after. Scope excludes computed calls, jumps and undiscovered references.
- Ghidra headless repair, coverage, native decompilation and project save completed successfully. Internal code entries: 1551, all decompiled successfully; separate EXTERNAL-block entries: 310. Successful decompilation does not prove correct signatures or semantics.

| Code segment | Instruction bytes | Defined data bytes | Undefined bytes |
|---|---:|---:|---:|
| 1000 | 53731 | 2412 | 403 |
| 1008 | 28814 | 623 | 257 |
| 1010 | 59156 | 1602 | 614 |
| 1018 | 18304 | 3594 | 178 |
| Total | 160005 | 8231 | 1452 |

Pass 7 had 1459 undefined bytes. Callback adds eight instruction bytes; removing the invalid fallthrough leaves one byte undefined: net reduction seven. Counts alone would conceal the boundary repair, which is the main improvement. No candidate alignment bytes were typed as padding.

## Unknowns and next test

Runtime Win16 API ABI and termination behavior, exception unwinding, and allocation-failure retry outcomes remain untested. Discriminating test: force allocation failure, break at 5AF6 and 076A, capture DS:094A/094C, AX and stack before/after callback; test exception and normal-return paths separately. For lookup, break at 3C80 with keys 0, 25, 4241h, FFFF and an absent key to confirm AX/DS behavior. Remaining 1452 undefined bytes, opaque metadata schema from pass 7 and complete behavioral/timing/render parity remain open.

## Confidence

High for bounded static lookup/translation behavior and repaired boundary; Medium for allocation-handler semantic identity. No new runtime evidence was produced.
