# Nitemare 3D Win16 1.10 — Ghidra 12.2 pass 9

## Finding

Established instruction-level behavior of three CRT-style primitives and their shared conversion tail: near memcpy, near memset, and 16-bit integer-to-text conversion. Added evidence comments/names in Ghidra without inventing new function entries or classifying unresolved bytes as padding. No runtime parity is claimed.

Input: `nite3w - 110.exe`, 230400 bytes, SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra 12.2 PUBLIC 20261016, JDK 25.0.2.

## Evidence

| Status | Claim | Primary location | Confidence |
|---|---|---|---|
| Confirmed | Copy receives near destination at BP+6, near source at BP+8, WORD count at BP+A; returns original destination in AX, preserves SI/DI, sets ES=DS | 1008:6C80..6CAB | High |
| Confirmed | With DF=0: odd destination consumes one leading byte, followed by count/2 MOVSW operations and an optional final byte | 6C96..6CA4 | High |
| Confirmed | Copy does not execute CLD or detect overlap. Actual word reads matter for overlap | Same; 672 modeled fixtures | High within model assumptions |
| Confirmed | Fill receives BP+6 near destination, low byte BP+8 fill, BP+A WORD count; returns destination in AX, preserves DI, sets ES=DS | 1008:6CAC..6CD8 | High |
| Confirmed | Fill uses optional leading byte, repeated word copies of the fill byte, optional trailing byte; no CLD | 6CBD..6CD2 | High |
| Confirmed | Integer entry receives BP+6 WORD value, BP+8 near buffer, BP+A WORD radix. DX is sign extension only for decimal; otherwise zero | 1008:60E2..60FC | High |
| Confirmed | Entry saves SI/DI, sets BL=1 and JMPs to shared tail 6CE6. The shared tail consumes this saved stack and returns to the original caller | 60E5/60E6/60FA; 6D32..6D38 | High |
| Confirmed | Shared tail sets ES=DS and CLD; decimal signed negative values emit minus and negate DX:AX; repeated two-stage 16-bit division emits reversed digits, then reverses them | 1008:6CE6..6D38 | High |
| Confirmed | Digit values 10..35 map to lowercase a..z; output includes NUL; AX returns original near buffer | 6D13..6D22; 6D32 | High |
| Confirmed | No local radix or output-capacity validation | All four exact bodies | High for local scope |
| Inferred | Original library identities are memcpy, memset and itoa-style routines | Arguments, return values and algorithms | High for behavior; original symbols unavailable |
| Unknown | Executable reachability and intended ABI of undefined prefix 6CDA..6CE5 | Gap after 6CD9, before shared tail | Unresolved; no new function created |

## Behavior model

For valid radices 2..36, entry 60E2 prints decimal words 8000h..FFFFh as -32768..-1. In other bases the same words are unsigned 32768..65535. Zero always emits `0` plus NUL. Examples: FFFFh -> `-1` in base 10, `ffff` in base 16; 8000h -> `-32768` in base 10, `8000` in base 16. The shared tail can also operate on a full DX:AX magnitude, but only the 60E2 entry's signed 16-bit setup has a proved caller chain here.

The explicit reference at 1008:60FA is exported as UNCONDITIONAL_CALL by Ghidra, although the raw opcode E9 and listing say JMP. This is a tail-call flow override, not evidence of an extra return address. The generated C prototype for 6CE6 is incomplete because it treats a shared tail as an independent entry. Use the instruction/stack model, not the declaration.

Copy and fill are near DS operations with caller cleanup (RETF without an immediate). Their memory models require DF=0; the routines themselves leave DF unchanged. Conversion explicitly clears DF. Copy snapshots both bytes of each MOVSW before writing them. For memory initially containing ascending bytes, source=1, destination=2, count=6 produces destination bytes `[1,2,2,4,4,6]`, not a snapshot copy and not the result of a forward byte-at-a-time loop. This is not an implementation promise for overlapping C memcpy calls; it records this executable's operation sequence.

Radix 0 or 1 and values outside the tested radix domain are not normalized by the entry. Do not silently add clamping or a fallback radix in a parity implementation. Runtime divide faults, nontermination and invalid buffer handling were not executed or certified.

## Validation

`scripts/verify_pass9_crt_primitives.py` checks the original EXE hash and exact raw bodies, then independently compares:

- 2,293,760 conversion cases: all 65536 WORD values, every radix 2..36, including NUL and decimal signedness.
- 700 shared-tail cases: ten selected 32-bit boundary values, 35 radices, both sign modes. These are model tests, not proof of an independent callable 32-bit API.
- 672 copy fixtures: selected even/odd/wrapping offsets, zero through FFFF counts, including overlapping operations.
- 420 fill fixtures: five fill bytes, selected offsets and counts.

Memory fixtures use a logical 65536-byte array and wrap offsets. Real Win16 selector limits/access faults and segments shorter than the requested access are not simulated. Counts and operation semantics are verified under the stated valid-memory assumptions; the wrap fixtures do not establish real CPU behavior at a selector boundary. Copy's second model uses a separately constructed operation schedule; this is weaker independence than the numeric conversion's general arithmetic specification.

Ghidra headless annotation, full native export and project save succeeded. The four annotations alter semantic documentation only. Internal entries remain 1551, separately exported EXTERNAL-block entries remain 310. Internal decompilation completion remains 1551/1551; signatures and semantics are not certified by that statistic.

Byte coverage remains 160005 instruction bytes, 8231 defined data bytes and 1452 undefined bytes over 169688 initialized executable bytes. No executable bytes were patched. Unknown-byte coverage is deliberately unchanged.

## Unknowns and next test

The 12-byte prefix 6CDA..6CE5 lacks a proved entry path and compatible complete frame; leave it unresolved. To resolve it, seek NE entry/export targets or a runtime PC hit at 6CDA with captured BP/SP/SI/DI/BL. For the known conversion, trace caller 1008:3E49 into 60E2 and record the arguments, final buffer, AX and stack. For copy/fill, test real DS/ES selectors and DF at actual callers before extending the models to faults or invalid memory. Renderer, scheduler, saves and demos retain their previous parity status.

## Implementation-ready findings

Valid-memory, DF=0 copy/fill and radix 2..36 integer formatting have exact supported local behavior. Preserve word-sized copy operations where binary-level overlap behavior matters. Keep signed decimal conversion distinct from unsigned nondecimal conversion. Do not model the shared tail as an ordinary call with a new return frame. Unsupported exceptional/fault behavior remains TBD.

## Confidence

High for bounded static primitive semantics under the listed preconditions. Runtime, selector-fault, invalid-input and whole-game 1:1 parity remain unverified.
