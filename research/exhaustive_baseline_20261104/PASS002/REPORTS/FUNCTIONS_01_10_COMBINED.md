# Function 1/10 — DOS_2_0_0201_000A

100-slot byte initializer

## 1. Identity, build and proof scope

DOS_2_0_0201_000A; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 1,
  "function_id": "DOS_2_0_0201_000A",
  "entry": "0201:000A",
  "last_instruction": "0201:0019",
  "end_exclusive": "0x1a",
  "span_bytes": 16,
  "decoded_instruction_bytes": 16,
  "instruction_count": 6,
  "decoded_ranges": [
    [
      10,
      26
    ]
  ],
  "gaps": [],
  "local_returns": [
    25
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 3,
  "direct_callsites": 0,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0201:000A|bbf250|mov bx, 0x50f2|
|0201:000D|c60701|mov byte ptr [bx], 1|
|0201:0010|83c312|add bx, 0x12|
|0201:0013|81fbfa57|cmp bx, 0x57fa|
|0201:0017|72f4|jb 0xd|
|0201:0019|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0201_000A.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 296
  }
]
```
Callees:

No direct calls in the decoded body.

## 6. Arguments and calling convention

No stack arguments read. Inputs: DS, a valid mapped memory range and a valid far-return stack.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 01_DOS_2_0_0201_000A_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

No frame/local pushes; RETF consumes 4 bytes. BX modified; arithmetic flags final ZF/PF=1, CF/AF/SF/OF=0. Other registers preserved subject to return.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|000D|DS|bx|1|W|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

DS bytes 0x50F2+18*k, k=0..99; no other direct memory access except return stack. Physical DS provenance is conditional: startup establishes DS=load_base+0x2771 but prior callees before this call remain a barrier.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

DS bytes 0x50F2+18*k, k=0..99; no other direct memory access except return stack. Physical DS provenance is conditional: startup establishes DS=load_base+0x2771 but prior callees before this call remain a barrier.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

BX starts at 0x50F2; store byte 1; add 18; repeat while BX<0x57FA unsigned. No loop wrap; exactly 100 iterations. Invariant BX=0x50F2+18*k and all prior target bytes equal 1.

## 14. Reconstructed algorithm

Confirmed local effect: writes 1 to the first byte of 100 slots, each 18 bytes apart. Meaning of that byte and relation to geometry records remain unknown.

BX starts at 0x50F2; store byte 1; add 18; repeat while BX<0x57FA unsigned. No loop wrap; exactly 100 iterations. Invariant BX=0x50F2+18*k and all prior target bytes equal 1.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
BX=0x50F2; // 000A
 do { DS8[BX]=1; BX=u16(BX+18); } while (BX<0x57FA); // 000D–0017
far_return(); // 0019
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed local effect: writes 1 to the first byte of 100 slots, each 18 bytes apart. Meaning of that byte and relation to geometry records remain unknown.

Preconditions: No stack arguments read. Inputs: DS, a valid mapped memory range and a valid far-return stack.

Supported normal effects: BX starts at 0x50F2; store byte 1; add 18; repeat while BX<0x57FA unsigned. No loop wrap; exactly 100 iterations. Invariant BX=0x50F2+18*k and all prior target bytes equal 1.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

All alternate entries, caller-path DS preservation, field meaning, actual in-game invocation.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

128 prior randomized cases plus 72 cross-version cases from PASS001; no new re-test claimed for this body.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

All alternate entries, caller-path DS preservation, field meaning, actual in-game invocation.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 2/10 — DOS_2_0_0201_001A

Fixed-point slope and endpoint-field calculation

## 1. Identity, build and proof scope

DOS_2_0_0201_001A; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 2,
  "function_id": "DOS_2_0_0201_001A",
  "entry": "0201:001A",
  "last_instruction": "0201:012C",
  "end_exclusive": "0x12d",
  "span_bytes": 275,
  "decoded_instruction_bytes": 272,
  "instruction_count": 111,
  "decoded_ranges": [
    [
      26,
      83
    ],
    [
      84,
      109
    ],
    [
      110,
      139
    ],
    [
      140,
      301
    ]
  ],
  "gaps": [
    [
      83,
      84
    ],
    [
      109,
      110
    ],
    [
      139,
      140
    ]
  ],
  "local_returns": [
    300
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 10,
  "direct_callsites": 0,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0201:001A|c8100000|enter 0x10, 0|
|0201:001E|57|push di|
|0201:001F|56|push si|
|0201:0020|8b7e0a|mov di, word ptr [bp + 0xa]|
|0201:0023|8b460c|mov ax, word ptr [bp + 0xc]|
|0201:0026|2b4608|sub ax, word ptr [bp + 8]|
|0201:0029|8946fe|mov word ptr [bp - 2], ax|
|0201:002C|8b4e0e|mov cx, word ptr [bp + 0xe]|
|0201:002F|2bcf|sub cx, di|
|0201:0031|894efc|mov word ptr [bp - 4], cx|
|0201:0034|0bc0|or ax, ax|
|0201:0036|741c|je 0x54|
|0201:0038|99|cwd |
|0201:0039|52|push dx|
|0201:003A|50|push ax|
|0201:003B|51|push cx|
|0201:003C|6a00|push 0|
|0201:003E|6658|pop eax|
|0201:0040|6659|pop ecx|
|0201:0042|6699|cdq |
|0201:0044|66f7f9|idiv ecx|
|0201:0047|8b5e06|mov bx, word ptr [bp + 6]|
|0201:004A|6689470a|mov dword ptr [bx + 0xa], eax|
|0201:004E|8b7606|mov si, word ptr [bp + 6]|
|0201:0051|eb0c|jmp 0x5f|
|0201:0054|8b7606|mov si, word ptr [bp + 6]|
|0201:0057|66c7440a00000000|mov dword ptr [si + 0xa], 0|
|0201:005F|837efc00|cmp word ptr [bp - 4], 0|
|0201:0063|7509|jne 0x6e|
|0201:0065|897c04|mov word ptr [si + 4], di|
|0201:0068|897c08|mov word ptr [si + 8], di|
|0201:006B|eb10|jmp 0x7d|
|0201:006E|837efe00|cmp word ptr [bp - 2], 0|
|0201:0072|7518|jne 0x8c|
|0201:0074|897c04|mov word ptr [si + 4], di|
|0201:0077|8b460e|mov ax, word ptr [bp + 0xe]|
|0201:007A|894408|mov word ptr [si + 8], ax|
|0201:007D|8bc7|mov ax, di|
|0201:007F|2b065445|sub ax, word ptr [0x4554]|
|0201:0083|c7440e0000|mov word ptr [si + 0xe], 0|
|0201:0088|e99b00|jmp 0x126|
|0201:008C|8b46fe|mov ax, word ptr [bp - 2]|
|0201:008F|99|cwd |
|0201:0090|52|push dx|
|0201:0091|50|push ax|
|0201:0092|8bc8|mov cx, ax|
|0201:0094|8b46fc|mov ax, word ptr [bp - 4]|
|0201:0097|8bda|mov bx, dx|
|0201:0099|99|cwd |
|0201:009A|52|push dx|
|0201:009B|50|push ax|
|0201:009C|8946f8|mov word ptr [bp - 8], ax|
|0201:009F|8956fa|mov word ptr [bp - 6], dx|
|0201:00A2|8b4402|mov ax, word ptr [si + 2]|
|0201:00A5|2b4608|sub ax, word ptr [bp + 8]|
|0201:00A8|99|cwd |
|0201:00A9|52|push dx|
|0201:00AA|50|push ax|
|0201:00AB|894ef4|mov word ptr [bp - 0xc], cx|
|0201:00AE|895ef6|mov word ptr [bp - 0xa], bx|
|0201:00B1|6658|pop eax|
|0201:00B3|6659|pop ecx|
|0201:00B5|66f7e9|imul ecx|
|0201:00B8|6659|pop ecx|
|0201:00BA|6699|cdq |
|0201:00BC|66f7f9|idiv ecx|
|0201:00BF|668bd0|mov edx, eax|
|0201:00C2|66c1ea10|shr edx, 0x10|
|0201:00C6|03c7|add ax, di|
|0201:00C8|894404|mov word ptr [si + 4], ax|
|0201:00CB|66ff76f4|push dword ptr [bp - 0xc]|
|0201:00CF|66ff76f8|push dword ptr [bp - 8]|
|0201:00D3|8b4406|mov ax, word ptr [si + 6]|
|0201:00D6|2b4608|sub ax, word ptr [bp + 8]|
|0201:00D9|99|cwd |
|0201:00DA|52|push dx|
|0201:00DB|50|push ax|
|0201:00DC|6658|pop eax|
|0201:00DE|6659|pop ecx|
|0201:00E0|66f7e9|imul ecx|
|0201:00E3|6659|pop ecx|
|0201:00E5|6699|cdq |
|0201:00E7|66f7f9|idiv ecx|
|0201:00EA|668bd0|mov edx, eax|
|0201:00ED|66c1ea10|shr edx, 0x10|
|0201:00F1|03c7|add ax, di|
|0201:00F3|894408|mov word ptr [si + 8], ax|
|0201:00F6|66ff740a|push dword ptr [si + 0xa]|
|0201:00FA|8b4402|mov ax, word ptr [si + 2]|
|0201:00FD|2b4608|sub ax, word ptr [bp + 8]|
|0201:0100|99|cwd |
|0201:0101|52|push dx|
|0201:0102|50|push ax|
|0201:0103|6658|pop eax|
|0201:0105|6659|pop ecx|
|0201:0107|66f7e9|imul ecx|
|0201:010A|668bd0|mov edx, eax|
|0201:010D|66c1ea10|shr edx, 0x10|
|0201:0111|8bcf|mov cx, di|
|0201:0113|2b0e5445|sub cx, word ptr [0x4554]|
|0201:0117|8946f0|mov word ptr [bp - 0x10], ax|
|0201:011A|8bc1|mov ax, cx|
|0201:011C|2bdb|sub bx, bx|
|0201:011E|035ef0|add bx, word ptr [bp - 0x10]|
|0201:0121|13c2|adc ax, dx|
|0201:0123|895c0e|mov word ptr [si + 0xe], bx|
|0201:0126|894410|mov word ptr [si + 0x10], ax|
|0201:0129|5e|pop si|
|0201:012A|5f|pop di|
|0201:012B|c9|leave |
|0201:012C|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0201_001A.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_0201_012E",
    "address": 381,
    "source": "PASS002_recovered_call"
  },
  {
    "function_id": "DOS_2_0_0201_012E",
    "address": 469,
    "source": "PASS002_recovered_call"
  }
]
```
Callees:

No direct calls in the decoded body.

## 6. Arguments and calling convention

Far call, caller cleans 10 bytes: [BP+6]=record offset, +8=x1, +0A=y1, +0C=x2, +0E=y2; BP is frame pointer after ENTER. Record +2/+6 read as x-like inputs. DS:[4554] is a y-like origin.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 02_DOS_2_0_0201_001A_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

ENTER 16,0; saves DI/SI (4 bytes); temporary mixed 16/32-bit pushes balance along normal paths; LEAVE restores BP; RETF consumes 4, args remain. SI/DI/BP preserved; AX final high16(frac). BX/CX/DX and high halves of EAX/ECX/EDX can change. FLAGS path-dependent; IDIV arithmetic flags undefined.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0020|SS|bp + 10|2|R|
|0023|SS|bp + 12|2|R|
|0026|SS|bp + 8|2|R|
|0029|SS|bp + -2|2|W|
|002C|SS|bp + 14|2|R|
|0031|SS|bp + -4|2|W|
|0047|SS|bp + 6|2|R|
|004A|DS|bx + 10|4|W|
|004E|SS|bp + 6|2|R|
|0054|SS|bp + 6|2|R|
|0057|DS|si + 10|4|W|
|005F|SS|bp + -4|2|R|
|0065|DS|si + 4|2|W|
|0068|DS|si + 8|2|W|
|006E|SS|bp + -2|2|R|
|0074|DS|si + 4|2|W|
|0077|SS|bp + 14|2|R|
|007A|DS|si + 8|2|W|
|007F|DS|17748|2|R|
|0083|DS|si + 14|2|W|
|008C|SS|bp + -2|2|R|
|0094|SS|bp + -4|2|R|
|009C|SS|bp + -8|2|W|
|009F|SS|bp + -6|2|W|
|00A2|DS|si + 2|2|R|
|00A5|SS|bp + 8|2|R|
|00AB|SS|bp + -12|2|W|
|00AE|SS|bp + -10|2|W|
|00C8|DS|si + 4|2|W|
|00CB|SS|bp + -12|4|R|
|00CF|SS|bp + -8|4|R|
|00D3|DS|si + 6|2|R|
|00D6|SS|bp + 8|2|R|
|00F3|DS|si + 8|2|W|
|00F6|DS|si + 10|4|R|
|00FA|DS|si + 2|2|R|
|00FD|SS|bp + 8|2|R|
|0113|DS|17748|2|R|
|0117|SS|bp + -16|2|W|
|011E|SS|bp + -16|2|R|
|0123|DS|si + 14|2|W|
|0126|DS|si + 16|2|W|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Reads 5 stack words, record words +2/+6, global DS:4554. Writes record +4,+8,+0A..+0D,+0E..+11. Fields +0/+2/+6 are preserved. Caller examples 0201:017D and 01D5 pass a record and two dword endpoint pairs using PUSH CS/near CALL.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Reads 5 stack words, record words +2/+6, global DS:4554. Writes record +4,+8,+0A..+0D,+0E..+11. Fields +0/+2/+6 are preserved. Caller examples 0201:017D and 01D5 pass a record and two dword endpoint pairs using PUSH CS/near CALL.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

dx=s16(x2-x1), dy=s16(y2-y1). If dx!=0 store slope=(s32(u16(dy)<<16)/dx) at record+0A, using truncation toward zero. dx==0 stores slope 0. dy==0 stores y1 to +4 and +8; else dx==0 stores y1 to +4 and y2 to +8. Otherwise each endpoint uses y1 + trunc(s16(record_x-x1)*dy/dx), with 16-bit wrapping. Fixed-point start +0E/+10 is low32(slope*s16(record[2]-x1) + (u16(y1-origin)<<16)) in general branch; simple branches store 0 low and u16(y1-origin) high. DX:AX operands and 32-bit IMUL/IDIV are preserved exactly; no host-language float replacement.

## 14. Reconstructed algorithm

Confirmed arithmetic on an 18-byte caller-supplied record; geometry/interpolation meaning is strongly inferred from endpoint formulas and caller fields. Not yet connected to rendering pixels.

dx=s16(x2-x1), dy=s16(y2-y1). If dx!=0 store slope=(s32(u16(dy)<<16)/dx) at record+0A, using truncation toward zero. dx==0 stores slope 0. dy==0 stores y1 to +4 and +8; else dx==0 stores y1 to +4 and y2 to +8. Otherwise each endpoint uses y1 + trunc(s16(record_x-x1)*dy/dx), with 16-bit wrapping. Fixed-point start +0E/+10 is low32(slope*s16(record[2]-x1) + (u16(y1-origin)<<16)) in general branch; simple branches store 0 low and u16(y1-origin) high. DX:AX operands and 32-bit IMUL/IDIV are preserved exactly; no host-language float replacement.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
dx=s16(x2-x1); dy=s16(y2-y1); // 0020–0031
slope=(dx!=0)?idiv_s32(s32(u16(dy)<<16),dx):0; // 0034–0057
store32(record+10,slope);
if (dy==0) { outA=y1; outB=y1; frac=u16(y1-origin)<<16; } // 005F–0088
else if (dx==0) { outA=y1; outB=y2; frac=u16(y1-origin)<<16; } // 006E–0088
else { // 008C–0123
 outA=u16(y1+idiv_s32(s16(load16(record+2)-x1)*dy,dx)); // 008C–00C8
 outB=u16(y1+idiv_s32(s16(load16(record+6)-x1)*dy,dx)); // 00CB–00F3
 frac=u32(slope*s16(load16(record+2)-x1)+(u16(y1-origin)<<16)); // 00F6–0123
}
store16(record+4,outA); store16(record+8,outB); store32(record+14,frac); // write-site addresses above, 0126
AX=hi16(frac); restore(SI,DI,BP); far_return(); // 0126–012C
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed arithmetic on an 18-byte caller-supplied record; geometry/interpolation meaning is strongly inferred from endpoint formulas and caller fields. Not yet connected to rendering pixels.

Preconditions: Far call, caller cleans 10 bytes: [BP+6]=record offset, +8=x1, +0A=y1, +0C=x2, +0E=y2; BP is frame pointer after ENTER. Record +2/+6 read as x-like inputs. DS:[4554] is a y-like origin.

Supported normal effects: dx=s16(x2-x1), dy=s16(y2-y1). If dx!=0 store slope=(s32(u16(dy)<<16)/dx) at record+0A, using truncation toward zero. dx==0 stores slope 0. dy==0 stores y1 to +4 and +8; else dx==0 stores y1 to +4 and y2 to +8. Otherwise each endpoint uses y1 + trunc(s16(record_x-x1)*dy/dx), with 16-bit wrapping. Fixed-point start +0E/+10 is low32(slope*s16(record[2]-x1) + (u16(y1-origin)<<16)) in general branch; simple branches store 0 low and u16(y1-origin) high. DX:AX operands and 32-bit IMUL/IDIV are preserved exactly; no host-language float replacement.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Record meaning, input range at all callers, all aliases/entries. First division faults for wrapped dx=-1 and dy=-32768; observed #DE leaves a partial execution, no normal postcondition. DS alias/stack/code overlap excluded from model.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

1,006 fresh model-vs-Unicorn cases, including vertical/horizontal/general branches, signed wrap and one divide overflow. Full 64 KiB DS checked in every normal case.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Record meaning, input range at all callers, all aliases/entries. First division faults for wrapped dx=-1 and dy=-32768; observed #DE leaves a partial execution, no normal postcondition. DS alias/stack/code overlap excluded from model.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.


## PASS002 cross-version evidence update

See ../ASM_DIFF/math_helper_cross_version_CFG.json, INSTRUCTION_LEVEL_DIFF_PASS002.csv and ADJACENT_VERSION_DIFF.json. Local CFG/instruction differences compared from actual bytes; global field equivalence remains unproved. Independent GNU objdump verifies this body's local instruction boundaries and bytes.


---

# Function 3/10 — DOS_2_0_0201_012E

Scan table and assemble 18-byte spans

## 1. Identity, build and proof scope

DOS_2_0_0201_012E; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 3,
  "function_id": "DOS_2_0_0201_012E",
  "entry": "0201:012E",
  "last_instruction": "0201:01DE",
  "end_exclusive": "0x1df",
  "span_bytes": 177,
  "decoded_instruction_bytes": 177,
  "instruction_count": 66,
  "decoded_ranges": [
    [
      302,
      479
    ]
  ],
  "gaps": [],
  "local_returns": [
    478
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 14,
  "direct_callsites": 4,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0201:012E|c8080000|enter 8, 0|
|0201:0132|57|push di|
|0201:0133|56|push si|
|0201:0134|33f6|xor si, si|
|0201:0136|8936644d|mov word ptr [0x4d64], si|
|0201:013A|bf6e4d|mov di, 0x4d6e|
|0201:013D|8b0e4845|mov cx, word ptr [0x4548]|
|0201:0141|8bc1|mov ax, cx|
|0201:0143|03c1|add ax, cx|
|0201:0145|056445|add ax, 0x4564|
|0201:0148|8946fa|mov word ptr [bp - 6], ax|
|0201:014B|3b0e4a45|cmp cx, word ptr [0x454a]|
|0201:014F|7f72|jg 0x1c3|
|0201:0151|894ef8|mov word ptr [bp - 8], cx|
|0201:0154|8b5efa|mov bx, word ptr [bp - 6]|
|0201:0157|3937|cmp word ptr [bx], si|
|0201:0159|7456|je 0x1b1|
|0201:015B|833e644d00|cmp word ptr [0x4d64], 0|
|0201:0160|7e21|jle 0x183|
|0201:0162|8935|mov word ptr [di], si|
|0201:0164|8b46f8|mov ax, word ptr [bp - 8]|
|0201:0167|48|dec ax|
|0201:0168|894506|mov word ptr [di + 6], ax|
|0201:016B|897efc|mov word ptr [bp - 4], di|
|0201:016E|83c712|add di, 0x12|
|0201:0171|66ff7418|push dword ptr [si + 0x18]|
|0201:0175|66ff7414|push dword ptr [si + 0x14]|
|0201:0179|ff76fc|push word ptr [bp - 4]|
|0201:017C|0e|push cs|
|0201:017D|e89afe|call 0x1a|
|0201:0180|83c40a|add sp, 0xa|
|0201:0183|8b5efa|mov bx, word ptr [bp - 6]|
|0201:0186|8b46f8|mov ax, word ptr [bp - 8]|
|0201:0189|8b37|mov si, word ptr [bx]|
|0201:018B|894502|mov word ptr [di + 2], ax|
|0201:018E|56|push si|
|0201:018F|6a00|push 0|
|0201:0191|9a3c143d18|lcall 0x183d, 0x143c|
|0201:0196|83c404|add sp, 4|
|0201:0199|ff06644d|inc word ptr [0x4d64]|
|0201:019D|833e644d32|cmp word ptr [0x4d64], 0x32|
|0201:01A2|7c0d|jl 0x1b1|
|0201:01A4|6a32|push 0x32|
|0201:01A6|686601|push 0x166|
|0201:01A9|9a0c00ba1f|lcall 0x1fba, 0xc|
|0201:01AE|83c404|add sp, 4|
|0201:01B1|8346fa02|add word ptr [bp - 6], 2|
|0201:01B5|a14a45|mov ax, word ptr [0x454a]|
|0201:01B8|ff46f8|inc word ptr [bp - 8]|
|0201:01BB|3946f8|cmp word ptr [bp - 8], ax|
|0201:01BE|7e94|jle 0x154|
|0201:01C0|8b4ef8|mov cx, word ptr [bp - 8]|
|0201:01C3|8935|mov word ptr [di], si|
|0201:01C5|49|dec cx|
|0201:01C6|894d06|mov word ptr [di + 6], cx|
|0201:01C9|8bde|mov bx, si|
|0201:01CB|66ff7718|push dword ptr [bx + 0x18]|
|0201:01CF|66ff7714|push dword ptr [bx + 0x14]|
|0201:01D3|57|push di|
|0201:01D4|0e|push cs|
|0201:01D5|e842fe|call 0x1a|
|0201:01D8|83c40a|add sp, 0xa|
|0201:01DB|5e|pop si|
|0201:01DC|5f|pop di|
|0201:01DD|c9|leave |
|0201:01DE|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0201_012E.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[]
```
Callees:

- 0201:017D → 0201:001A (NEAR; PUSH CS prefix=True)
- 0201:0191 → 083D:143C (FAR; PUSH CS prefix=False)
- 0201:01A9 → 0FBA:000C (FAR; PUSH CS prefix=False)
- 0201:01D5 → 0201:001A (NEAR; PUSH CS prefix=True)

## 6. Arguments and calling convention

No input stack arguments read. Global bounds DS:4548 and DS:454A; source pointer table DS:4564+2*index. Output base DS:4D6E and count DS:4D64.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 03_DOS_2_0_0201_012E_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

ENTER8,0; DI/SI saved. Calls push 10 bytes for 001A and use explicit PUSH CS+near CALL for far-return semantics. Error/helper return behavior affects global paths. Restores local frame and DI/SI on ordinary return.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0136|DS|19812|2|W|
|013D|DS|17736|2|R|
|0148|SS|bp + -6|2|W|
|014B|DS|17738|2|R|
|0151|SS|bp + -8|2|W|
|0154|SS|bp + -6|2|R|
|0157|DS|bx|2|R|
|015B|DS|19812|2|R|
|0162|DS|di|2|W|
|0164|SS|bp + -8|2|R|
|0168|DS|di + 6|2|W|
|016B|SS|bp + -4|2|W|
|0171|DS|si + 24|4|R|
|0175|DS|si + 20|4|R|
|0179|SS|bp + -4|2|R|
|0183|SS|bp + -6|2|R|
|0186|SS|bp + -8|2|R|
|0189|DS|bx|2|R|
|018B|DS|di + 2|2|W|
|0199|DS|19812|2|RW|
|019D|DS|19812|2|R|
|01B1|SS|bp + -6|2|RW|
|01B5|DS|17738|2|R|
|01B8|SS|bp + -8|2|RW|
|01BB|SS|bp + -8|2|R|
|01C0|SS|bp + -8|2|R|
|01C3|DS|di|2|W|
|01C6|DS|di + 6|2|W|
|01CB|DS|bx + 24|4|R|
|01CF|DS|bx + 20|4|R|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Count word at4D64; output spans base4D6E stride18; source table word4564+2*i; pointed source dwords +14/+18. Error string DS:0166 is "MAXSEG exceeded (%d)" under the startup DS mapping, direct byte evidence. This output region differs from initializer base50F2; do not conflate the two lists.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Count word at4D64; output spans base4D6E stride18; source table word4564+2*i; pointed source dwords +14/+18. Error string DS:0166 is "MAXSEG exceeded (%d)" under the startup DS mapping, direct byte evidence. This output region differs from initializer base50F2; do not conflate the two lists.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

Initialize SI=0, count=0, DI=4D6E; CX=start bound. Compute wrapped pointer-table address 4564+2*CX. Signed bound comparison controls scanning. When table pointer differs from SI, close previous record if signed count>0: record[0]=SI, record[6]=index-1, then call 001A(record, dwords SI+14 and SI+18) and advance DI by18. Set SI=new pointer, record[2]=index, call 083D:143C(0,SI), increment count, call error helper when signed count>=50. After loop unconditionally close final record and call 001A. Empty bounds therefore still execute finalization with SI=0; cannot simplify to empty output without proof.

## 14. Reconstructed algorithm

Confirmed local memory/call sequence scans DS word pointers indexed by a signed coordinate range, emits 18-byte records and calls function 0201:001A. Span/geometry terminology is inferred; original object type unknown.

Initialize SI=0, count=0, DI=4D6E; CX=start bound. Compute wrapped pointer-table address 4564+2*CX. Signed bound comparison controls scanning. When table pointer differs from SI, close previous record if signed count>0: record[0]=SI, record[6]=index-1, then call 001A(record, dwords SI+14 and SI+18) and advance DI by18. Set SI=new pointer, record[2]=index, call 083D:143C(0,SI), increment count, call error helper when signed count>=50. After loop unconditionally close final record and call 001A. Empty bounds therefore still execute finalization with SI=0; cannot simplify to empty output without proof.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
SI=0; DS16[0x4D64]=0; DI=0x4D6E; i=s16(DS16[0x4548]); // 0134–0148
if (i<=s16(DS16[0x454A])) do { // 014B–0151
 p=DS16[u16(0x4564+2*i)]; // 0154–0157
 if (p!=SI) {
  if (s16(DS16[0x4D64])>0) {
   DS16[DI]=SI; DS16[DI+6]=u16(i-1); old=DI; DI=u16(DI+18); // 0162–016E
   calc_0201_001A(old,DS32[SI+0x14],DS32[SI+0x18]); // 0171–0180
  }
  SI=DS16[u16(0x4564+2*i)]; DS16[DI+2]=u16(i); // 0183–018B
  far_083D_143C(0,SI); // 018E–0196
  DS16[0x4D64]++; if (s16(DS16[0x4D64])>=50) error_helper(0x0166,50); // 0199–01AE
 }
 i=s16(i+1); // 01B1–01C0; current end bound reloaded each iteration
} while (i<=s16(DS16[0x454A]));
DS16[DI]=SI; DS16[DI+6]=u16(i-1); // 01C3–01C6
calc_0201_001A(DI,DS32[SI+0x14],DS32[SI+0x18]); // 01C9–01D8
restore(SI,DI,BP); far_return(); // 01DB–01DE
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed local memory/call sequence scans DS word pointers indexed by a signed coordinate range, emits 18-byte records and calls function 0201:001A. Span/geometry terminology is inferred; original object type unknown.

Preconditions: No input stack arguments read. Global bounds DS:4548 and DS:454A; source pointer table DS:4564+2*index. Output base DS:4D6E and count DS:4D64.

Supported normal effects: Initialize SI=0, count=0, DI=4D6E; CX=start bound. Compute wrapped pointer-table address 4564+2*CX. Signed bound comparison controls scanning. When table pointer differs from SI, close previous record if signed count>0: record[0]=SI, record[6]=index-1, then call 001A(record, dwords SI+14 and SI+18) and advance DI by18. Set SI=new pointer, record[2]=index, call 083D:143C(0,SI), increment count, call error helper when signed count>=50. After loop unconditionally close final record and call 001A. Empty bounds therefore still execute finalization with SI=0; cannot simplify to empty output without proof.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Source table producers and valid bounds, whether error helper exits, callback/callee memory effects, all entry aliases. If a callee changes bounds the loop is not statically bounded by its original values.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Static closure and cross-checked 001A call arguments. No function-wide runtime test claimed.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Source table producers and valid bounds, whether error helper exits, callback/callee memory effects, all entry aliases. If a callee changes bounds the loop is not statically bounded by its original values.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 4/10 — DOS_2_0_0476_0326

Argument dispatcher with proven 24-entry switch

## 1. Identity, build and proof scope

DOS_2_0_0476_0326; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 4,
  "function_id": "DOS_2_0_0476_0326",
  "entry": "0476:0326",
  "last_instruction": "0476:0515",
  "end_exclusive": "0x516",
  "span_bytes": 496,
  "decoded_instruction_bytes": 441,
  "instruction_count": 159,
  "decoded_ranges": [
    [
      806,
      925
    ],
    [
      974,
      1017
    ],
    [
      1018,
      1025
    ],
    [
      1026,
      1067
    ],
    [
      1068,
      1107
    ],
    [
      1108,
      1197
    ],
    [
      1198,
      1211
    ],
    [
      1212,
      1302
    ]
  ],
  "gaps": [
    [
      925,
      974
    ],
    [
      1017,
      1018
    ],
    [
      1025,
      1026
    ],
    [
      1067,
      1068
    ],
    [
      1107,
      1108
    ],
    [
      1197,
      1198
    ],
    [
      1211,
      1212
    ]
  ],
  "local_returns": [
    1301
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 46,
  "direct_callsites": 16,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0476:0326|c8080000|enter 8, 0|
|0476:032A|57|push di|
|0476:032B|56|push si|
|0476:032C|c646fb00|mov byte ptr [bp - 5], 0|
|0476:0330|b80100|mov ax, 1|
|0476:0333|8946fc|mov word ptr [bp - 4], ax|
|0476:0336|8946fe|mov word ptr [bp - 2], ax|
|0476:0339|9a6e0c7712|lcall 0x1277, 0xc6e|
|0476:033E|0e|push cs|
|0476:033F|e8befc|call 0|
|0476:0342|689f0a|push 0xa9f|
|0476:0345|9a8a24ee21|lcall 0x21ee, 0x248a|
|0476:034A|83c402|add sp, 2|
|0476:034D|0bc0|or ax, ax|
|0476:034F|740b|je 0x35c|
|0476:0351|c606cf3c00|mov byte ptr [0x3ccf], 0|
|0476:0356|c706c23c1200|mov word ptr [0x3cc2], 0x12|
|0476:035C|be0100|mov si, 1|
|0476:035F|397606|cmp word ptr [bp + 6], si|
|0476:0362|0f8e8b01|jle 0x4f1|
|0476:0366|8b7e08|mov di, word ptr [bp + 8]|
|0476:0369|8bde|mov bx, si|
|0476:036B|03de|add bx, si|
|0476:036D|03df|add bx, di|
|0476:036F|895ef8|mov word ptr [bp - 8], bx|
|0476:0372|8b1f|mov bx, word ptr [bx]|
|0476:0374|803f2d|cmp byte ptr [bx], 0x2d|
|0476:0377|740b|je 0x384|
|0476:0379|57|push di|
|0476:037A|ff7606|push word ptr [bp + 6]|
|0476:037D|0e|push cs|
|0476:037E|e893ff|call 0x314|
|0476:0381|83c404|add sp, 4|
|0476:0384|8b5ef8|mov bx, word ptr [bp - 8]|
|0476:0387|8b1f|mov bx, word ptr [bx]|
|0476:0389|8a4701|mov al, byte ptr [bx + 1]|
|0476:038C|98|cbw |
|0476:038D|2d6100|sub ax, 0x61|
|0476:0390|3d1700|cmp ax, 0x17|
|0476:0393|7739|ja 0x3ce|
|0476:0395|03c0|add ax, ax|
|0476:0397|93|xchg bx, ax|
|0476:0398|2effa79e03|jmp word ptr cs:[bx + 0x39e]|
|0476:03CE|57|push di|
|0476:03CF|ff7606|push word ptr [bp + 6]|
|0476:03D2|0e|push cs|
|0476:03D3|e83eff|call 0x314|
|0476:03D6|83c404|add sp, 4|
|0476:03D9|e90d01|jmp 0x4e9|
|0476:03DC|68dc3c|push 0x3cdc|
|0476:03DF|68a60a|push 0xaa6|
|0476:03E2|46|inc si|
|0476:03E3|8bde|mov bx, si|
|0476:03E5|03de|add bx, si|
|0476:03E7|ff31|push word ptr [bx + di]|
|0476:03E9|9ae427ee21|lcall 0x21ee, 0x27e4|
|0476:03EE|83c406|add sp, 6|
|0476:03F1|9a6e0c7712|lcall 0x1277, 0xc6e|
|0476:03F6|e9f000|jmp 0x4e9|
|0476:03FA|c646fb01|mov byte ptr [bp - 5], 1|
|0476:03FE|e9e800|jmp 0x4e9|
|0476:0402|68c03c|push 0x3cc0|
|0476:0405|68a90a|push 0xaa9|
|0476:0408|46|inc si|
|0476:0409|8bde|mov bx, si|
|0476:040B|03de|add bx, si|
|0476:040D|ff31|push word ptr [bx + di]|
|0476:040F|9ae427ee21|lcall 0x21ee, 0x27e4|
|0476:0414|83c406|add sp, 6|
|0476:0417|e9cf00|jmp 0x4e9|
|0476:041A|68bc3c|push 0x3cbc|
|0476:041D|68ac0a|push 0xaac|
|0476:0420|ebe6|jmp 0x408|
|0476:0422|8d46fc|lea ax, [bp - 4]|
|0476:0425|50|push ax|
|0476:0426|68af0a|push 0xaaf|
|0476:0429|ebdd|jmp 0x408|
|0476:042C|68be3c|push 0x3cbe|
|0476:042F|68b20a|push 0xab2|
|0476:0432|ebd4|jmp 0x408|
|0476:0434|8d46fe|lea ax, [bp - 2]|
|0476:0437|50|push ax|
|0476:0438|68b50a|push 0xab5|
|0476:043B|46|inc si|
|0476:043C|8bde|mov bx, si|
|0476:043E|03de|add bx, si|
|0476:0440|ff31|push word ptr [bx + di]|
|0476:0442|9ae427ee21|lcall 0x21ee, 0x27e4|
|0476:0447|83c406|add sp, 6|
|0476:044A|0bc0|or ax, ax|
|0476:044C|0f859900|jne 0x4e9|
|0476:0450|e97bff|jmp 0x3ce|
|0476:0454|c606d03c01|mov byte ptr [0x3cd0], 1|
|0476:0459|e98d00|jmp 0x4e9|
|0476:045C|c606c73c00|mov byte ptr [0x3cc7], 0|
|0476:0461|e98500|jmp 0x4e9|
|0476:0464|c606c83c01|mov byte ptr [0x3cc8], 1|
|0476:0469|68ca3c|push 0x3cca|
|0476:046C|68b80a|push 0xab8|
|0476:046F|46|inc si|
|0476:0470|8bde|mov bx, si|
|0476:0472|03de|add bx, si|
|0476:0474|ff31|push word ptr [bx + di]|
|0476:0476|9ae427ee21|lcall 0x21ee, 0x27e4|
|0476:047B|83c406|add sp, 6|
|0476:047E|48|dec ax|
|0476:047F|0f854bff|jne 0x3ce|
|0476:0483|68cc3c|push 0x3ccc|
|0476:0486|68bb0a|push 0xabb|
|0476:0489|46|inc si|
|0476:048A|8bde|mov bx, si|
|0476:048C|03de|add bx, si|
|0476:048E|ff31|push word ptr [bx + di]|
|0476:0490|9ae427ee21|lcall 0x21ee, 0x27e4|
|0476:0495|83c406|add sp, 6|
|0476:0498|48|dec ax|
|0476:0499|744e|je 0x4e9|
|0476:049B|e930ff|jmp 0x3ce|
|0476:049E|c706d63c0100|mov word ptr [0x3cd6], 1|
|0476:04A4|eb43|jmp 0x4e9|
|0476:04A6|c606c63c00|mov byte ptr [0x3cc6], 0|
|0476:04AB|eb3c|jmp 0x4e9|
|0476:04AE|c606cf3c00|mov byte ptr [0x3ccf], 0|
|0476:04B3|c706c23c1200|mov word ptr [0x3cc2], 0x12|
|0476:04B9|eb2e|jmp 0x4e9|
|0476:04BC|684441|push 0x4144|
|0476:04BF|68be0a|push 0xabe|
|0476:04C2|46|inc si|
|0476:04C3|8bde|mov bx, si|
|0476:04C5|03de|add bx, si|
|0476:04C7|ff31|push word ptr [bx + di]|
|0476:04C9|9ae427ee21|lcall 0x21ee, 0x27e4|
|0476:04CE|83c406|add sp, 6|
|0476:04D1|80264441f8|and byte ptr [0x4144], 0xf8|
|0476:04D6|ff364441|push word ptr [0x4144]|
|0476:04DA|9ac20b7712|lcall 0x1277, 0xbc2|
|0476:04DF|83c402|add sp, 2|
|0476:04E2|eb05|jmp 0x4e9|
|0476:04E4|c606ce3c00|mov byte ptr [0x3cce], 0|
|0476:04E9|46|inc si|
|0476:04EA|3b7606|cmp si, word ptr [bp + 6]|
|0476:04ED|0f8c78fe|jl 0x369|
|0476:04F1|0e|push cs|
|0476:04F2|e8d9fb|call 0xce|
|0476:04F5|8a46fb|mov al, byte ptr [bp - 5]|
|0476:04F8|50|push ax|
|0476:04F9|66ff76fc|push dword ptr [bp - 4]|
|0476:04FD|9a4c27291d|lcall 0x1d29, 0x274c|
|0476:0502|83c406|add sp, 6|
|0476:0505|6a00|push 0|
|0476:0507|8a46fb|mov al, byte ptr [bp - 5]|
|0476:050A|50|push ax|
|0476:050B|0e|push cs|
|0476:050C|e8c1fc|call 0x1d0|
|0476:050F|83c404|add sp, 4|
|0476:0512|5e|pop si|
|0476:0513|5f|pop di|
|0476:0514|c9|leave |
|0476:0515|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0476_0326.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_11EE_0018",
    "address": 218
  }
]
```
Callees:

- 0476:0339 → 0277:0C6E (FAR; PUSH CS prefix=False)
- 0476:033F → 0476:0000 (NEAR; PUSH CS prefix=True)
- 0476:0345 → 11EE:248A (FAR; PUSH CS prefix=False)
- 0476:037E → 0476:0314 (NEAR; PUSH CS prefix=True)
- 0476:04F2 → 0476:00CE (NEAR; PUSH CS prefix=True)
- 0476:04FD → 0D29:274C (FAR; PUSH CS prefix=False)
- 0476:050C → 0476:01D0 (NEAR; PUSH CS prefix=True)
- 0476:04C9 → 11EE:27E4 (FAR; PUSH CS prefix=False)
- 0476:04DA → 0277:0BC2 (FAR; PUSH CS prefix=False)
- 0476:0476 → 11EE:27E4 (FAR; PUSH CS prefix=False)
- 0476:0490 → 11EE:27E4 (FAR; PUSH CS prefix=False)
- 0476:03D3 → 0476:0314 (NEAR; PUSH CS prefix=True)
- 0476:0442 → 11EE:27E4 (FAR; PUSH CS prefix=False)
- 0476:040F → 11EE:27E4 (FAR; PUSH CS prefix=False)
- 0476:03E9 → 11EE:27E4 (FAR; PUSH CS prefix=False)
- 0476:03F1 → 0277:0C6E (FAR; PUSH CS prefix=False)

## 6. Arguments and calling convention

[BP+6]=signed argc-like count; [BP+8]=near pointer to an argv-like near-pointer vector. Locals BP-5 byte mode, BP-4 and BP-2 words initially1; BP-8 pointer-table cursor.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 04_DOS_2_0_0476_0326_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

ENTER8,0, savesDI/SI. Near calls preceded by PUSH CS are far-call-compatible, return address occupies4 bytes. 0476:0314 and format helper stack args explicitly cleaned at callers. AL mode pushed as AX with unconstrained AH; callee byte-vs-word contract not yet proved.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|032C|SS|bp + -5|1|W|
|0333|SS|bp + -4|2|W|
|0336|SS|bp + -2|2|W|
|0351|DS|15567|1|W|
|0356|DS|15554|2|W|
|035F|SS|bp + 6|2|R|
|0366|SS|bp + 8|2|R|
|036F|SS|bp + -8|2|W|
|0372|DS|bx|2|R|
|0374|DS|bx|1|R|
|037A|SS|bp + 6|2|R|
|0384|SS|bp + -8|2|R|
|0387|DS|bx|2|R|
|0389|DS|bx + 1|1|R|
|0398|cs|bx + 926|2|R|
|03CF|SS|bp + 6|2|R|
|03E7|DS|bx + di|2|R|
|03FA|SS|bp + -5|1|W|
|040D|DS|bx + di|2|R|
|0422|SS|bp + -4|2|R|
|0434|SS|bp + -2|2|R|
|0440|DS|bx + di|2|R|
|0454|DS|15568|1|W|
|045C|DS|15559|1|W|
|0464|DS|15560|1|W|
|0474|DS|bx + di|2|R|
|048E|DS|bx + di|2|R|
|049E|DS|15574|2|W|
|04A6|DS|15558|1|W|
|04AE|DS|15567|1|W|
|04B3|DS|15554|2|W|
|04C7|DS|bx + di|2|R|
|04D1|DS|16708|1|RW|
|04D6|DS|16708|2|R|
|04E4|DS|15566|1|W|
|04EA|SS|bp + 6|2|R|
|04F5|SS|bp + -5|1|R|
|04F9|SS|bp + -4|4|R|
|0507|SS|bp + -5|1|R|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Table CS:039E..03CD is48 bytes of DATA, not instructions; padding at039D. Selector byte DS:[argv[i]+1]. Direct globals and formats listed in case table. Under startup DS, string0A9F="windir", decimal/hex scan formats at0AA6..0ABE.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Table CS:039E..03CD is48 bytes of DATA, not instructions; padding at039D. Selector byte DS:[argv[i]+1]. Direct globals and formats listed in case table. Under startup DS, string0A9F="windir", decimal/hex scan formats at0AA6..0ABE.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

Calls initialization helper then 0476:0000. Passes string "windir" to 11EE:248A; nonzero result writes byte3CCF=0 and word3CC2=18. SI starts1; if signed argc<=1 skip loop. Loop checks first byte of arg equals45 ("-"); otherwise calls error helper0314, but if it returns control still reads second byte. CBW sign-extends second byte, subtracts97, JA rejects unsigned values>23. BX=2*index; CS:[039E+BX] dispatches among 24 entries and16 distinct targets. Cases a/c/d/e/f/l/q/w consume extra argv words; q consumes two. All returning paths reach incrementSI then signed loop comparison. Epilogue calls 00CE, 0D29:274C and 01D0; global callee semantics remain open.

## 14. Reconstructed algorithm

Confirmed argument-list dispatcher with lowercase second-character selector. CLI option effects are direct assignments/calls; full user-facing option meanings inferred only where supporting strings exist.

Calls initialization helper then 0476:0000. Passes string "windir" to 11EE:248A; nonzero result writes byte3CCF=0 and word3CC2=18. SI starts1; if signed argc<=1 skip loop. Loop checks first byte of arg equals45 ("-"); otherwise calls error helper0314, but if it returns control still reads second byte. CBW sign-extends second byte, subtracts97, JA rejects unsigned values>23. BX=2*index; CS:[039E+BX] dispatches among 24 entries and16 distinct targets. Cases a/c/d/e/f/l/q/w consume extra argv words; q consumes two. All returning paths reach incrementSI then signed loop comparison. Epilogue calls 00CE, 0D29:274C and 01D0; global callee semantics remain open.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
mode=0; argE=argL=1; // 032C–0336
far_0277_0C6E(); far_0476_0000(); // 0339–033F
if (far_11EE_248A(near_string(0x0A9F))!=0) { DS8[0x3CCF]=0; DS16[0x3CC2]=18; } // 0342–0356
for (i=1; i<s16(argc); ++i) { // 035C–0362,04E9–04ED
 arg=DS16[u16(argv+2*i)]; // 0366–0372
 if (DS8[arg]!=45) error_0476_0314(argc,argv); // 0374–0381
 key=u16(s8(DS8[arg+1])-97); // 0384–038D: CBW, not CWDE
 if (key>23) error_case(); else goto CS16[0x039E+2*key]; // 0390–0398
 // See CLI_dispatch_table.json and CASE_EFFECTS.md for all 24 mappings and case writes.
}
far_0476_00CE(); far_0D29_274C(argE,argL,mode); far_0476_01D0(mode,0); // 04F1–050F
restore(SI,DI,BP); far_return(); // 0512–0515
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed argument-list dispatcher with lowercase second-character selector. CLI option effects are direct assignments/calls; full user-facing option meanings inferred only where supporting strings exist.

Preconditions: [BP+6]=signed argc-like count; [BP+8]=near pointer to an argv-like near-pointer vector. Locals BP-5 byte mode, BP-4 and BP-2 words initially1; BP-8 pointer-table cursor.

Supported normal effects: Calls initialization helper then 0476:0000. Passes string "windir" to 11EE:248A; nonzero result writes byte3CCF=0 and word3CC2=18. SI starts1; if signed argc<=1 skip loop. Loop checks first byte of arg equals45 ("-"); otherwise calls error helper0314, but if it returns control still reads second byte. CBW sign-extends second byte, subtracts97, JA rejects unsigned values>23. BX=2*index; CS:[039E+BX] dispatches among 24 entries and16 distinct targets. Cases a/c/d/e/f/l/q/w consume extra argv words; q consumes two. All returning paths reach incrementSI then signed loop comparison. Epilogue calls 00CE, 0D29:274C and 01D0; global callee semantics remain open.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Real exit/non-return semantics of error helper; argv bounds on options consuming more args; callee preservation of DS; meaning of all global fields; full runtime behavior.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

1,024 exhaustive selector cases: all256 bytes ×4 initial upper-EAX patterns; all outgoing targets and valid indices match. Local static instruction graph grows69→159 rows after table recovery.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Real exit/non-return semantics of error helper; argv bounds on options consuming more args; callee preservation of DS; meaning of all global fields; full runtime behavior.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 5/10 — DOS_2_0_0476_00CE

Subsystem initialization sequence with progress logging

## 1. Identity, build and proof scope

DOS_2_0_0476_00CE; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 5,
  "function_id": "DOS_2_0_0476_00CE",
  "entry": "0476:00CE",
  "last_instruction": "0476:0190",
  "end_exclusive": "0x191",
  "span_bytes": 195,
  "decoded_instruction_bytes": 195,
  "instruction_count": 66,
  "decoded_ranges": [
    [
      206,
      401
    ]
  ],
  "gaps": [],
  "local_returns": [
    400
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 22,
  "direct_callsites": 21,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0476:00CE|685c08|push 0x85c|
|0476:00D1|0e|push cs|
|0476:00D2|e8a3ff|call 0x78|
|0476:00D5|83c402|add sp, 2|
|0476:00D8|6a00|push 0|
|0476:00DA|9aca293d18|lcall 0x183d, 0x29ca|
|0476:00DF|83c402|add sp, 2|
|0476:00E2|686d08|push 0x86d|
|0476:00E5|0e|push cs|
|0476:00E6|e88fff|call 0x78|
|0476:00E9|83c402|add sp, 2|
|0476:00EC|6a00|push 0|
|0476:00EE|9adc002b1c|lcall 0x1c2b, 0xdc|
|0476:00F3|83c402|add sp, 2|
|0476:00F6|687b08|push 0x87b|
|0476:00F9|0e|push cs|
|0476:00FA|e87bff|call 0x78|
|0476:00FD|83c402|add sp, 2|
|0476:0100|6a00|push 0|
|0476:0102|9a0400de1b|lcall 0x1bde, 4|
|0476:0107|83c402|add sp, 2|
|0476:010A|688508|push 0x885|
|0476:010D|0e|push cs|
|0476:010E|e867ff|call 0x78|
|0476:0111|83c402|add sp, 2|
|0476:0114|6a00|push 0|
|0476:0116|9ad8005611|lcall 0x1156, 0xd8|
|0476:011B|83c402|add sp, 2|
|0476:011E|688f08|push 0x88f|
|0476:0121|0e|push cs|
|0476:0122|e853ff|call 0x78|
|0476:0125|83c402|add sp, 2|
|0476:0128|9a0a000112|lcall 0x1201, 0xa|
|0476:012D|6a00|push 0|
|0476:012F|9a24006817|lcall 0x1768, 0x24|
|0476:0134|83c402|add sp, 2|
|0476:0137|689b08|push 0x89b|
|0476:013A|0e|push cs|
|0476:013B|e83aff|call 0x78|
|0476:013E|83c402|add sp, 2|
|0476:0141|6a00|push 0|
|0476:0143|9a3401b016|lcall 0x16b0, 0x134|
|0476:0148|83c402|add sp, 2|
|0476:014B|68a608|push 0x8a6|
|0476:014E|0e|push cs|
|0476:014F|e826ff|call 0x78|
|0476:0152|83c402|add sp, 2|
|0476:0155|6a00|push 0|
|0476:0157|9a8c01b016|lcall 0x16b0, 0x18c|
|0476:015C|83c402|add sp, 2|
|0476:015F|68b308|push 0x8b3|
|0476:0162|0e|push cs|
|0476:0163|e812ff|call 0x78|
|0476:0166|83c402|add sp, 2|
|0476:0169|9a9626291d|lcall 0x1d29, 0x2696|
|0476:016E|50|push ax|
|0476:016F|9a36037712|lcall 0x1277, 0x336|
|0476:0174|83c402|add sp, 2|
|0476:0177|9aa6027712|lcall 0x1277, 0x2a6|
|0476:017C|9ae00a7712|lcall 0x1277, 0xae0|
|0476:0181|c606d13c00|mov byte ptr [0x3cd1], 0|
|0476:0186|68bd08|push 0x8bd|
|0476:0189|0e|push cs|
|0476:018A|e8ebfe|call 0x78|
|0476:018D|83c402|add sp, 2|
|0476:0190|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0476_00CE.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_0476_0326",
    "address": 1266
  }
]
```
Callees:

- 0476:00D2 → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:00DA → 083D:29CA (FAR; PUSH CS prefix=False)
- 0476:00E6 → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:00EE → 0C2B:00DC (FAR; PUSH CS prefix=False)
- 0476:00FA → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:0102 → 0BDE:0004 (FAR; PUSH CS prefix=False)
- 0476:010E → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:0116 → 0156:00D8 (FAR; PUSH CS prefix=False)
- 0476:0122 → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:0128 → 0201:000A (FAR; PUSH CS prefix=False)
- 0476:012F → 0768:0024 (FAR; PUSH CS prefix=False)
- 0476:013B → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:0143 → 06B0:0134 (FAR; PUSH CS prefix=False)
- 0476:014F → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:0157 → 06B0:018C (FAR; PUSH CS prefix=False)
- 0476:0163 → 0476:0078 (NEAR; PUSH CS prefix=True)
- 0476:0169 → 0D29:2696 (FAR; PUSH CS prefix=False)
- 0476:016F → 0277:0336 (FAR; PUSH CS prefix=False)
- 0476:0177 → 0277:02A6 (FAR; PUSH CS prefix=False)
- 0476:017C → 0277:0AE0 (FAR; PUSH CS prefix=False)
- 0476:018A → 0476:0078 (NEAR; PUSH CS prefix=True)

## 6. Arguments and calling convention

No direct stack parameters read; DS provides string offsets and globals. External helpers receive explicit zero words where shown.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 05_DOS_2_0_0476_00CE_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

No frame. Logger uses PUSH CS+near CALL and caller removes one word. Zero-arg callees FAR call; explicit word arguments cleaned2. One AX return forwarded to next callee. Registers depend on all callees; function does not save them.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0181|DS|15569|1|W|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Progress strings DS:085C,086D,087B,0885,088F,089B,08A6,08B3,08BD; only direct data write DS:3CD1=0. Callees have broader unknown side effects.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Progress strings DS:085C,086D,087B,0885,088F,089B,08A6,08B3,08BD; only direct data write DS:3CD1=0. Callees have broader unknown side effects.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

Log Initializing; call083D:29CA(0); log Bootstrap ok; call0C2B:00DC(0); log Sound ok; call0BDE:0004(0); log Timer ok; call0156:00D8(0); log Display ok; call0201:000A(); call0768:0024(0); log Memory ok; call06B0:0134(0); log Keyboard ok; call06B0:018C(0); log Mouse ok; call0D29:2696(); forward AX to0277:0336; call0277:02A6 and0277:0AE0; write byte3CD1=0; log Initialize complete. Exact meaning of first two helpers is inferred from subsequent message labels.

## 14. Reconstructed algorithm

Confirmed fixed sequence of helper calls alternating with debug strings. Sound/timer/display/memory/keyboard/mouse descriptions follow actual nearby strings, but successful return alone does not prove subsystem initialization success.

Log Initializing; call083D:29CA(0); log Bootstrap ok; call0C2B:00DC(0); log Sound ok; call0BDE:0004(0); log Timer ok; call0156:00D8(0); log Display ok; call0201:000A(); call0768:0024(0); log Memory ok; call06B0:0134(0); log Keyboard ok; call06B0:018C(0); log Mouse ok; call0D29:2696(); forward AX to0277:0336; call0277:02A6 and0277:0AE0; write byte3CD1=0; log Initialize complete. Exact meaning of first two helpers is inferred from subsequent message labels.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
log_0476_0078(0x085C); call_083D_29CA(0); // 00CE–00DF
log_0476_0078(0x086D); call_0C2B_00DC(0); // 00E2–00F3
log_0476_0078(0x087B); call_0BDE_0004(0); // 00F6–0107
log_0476_0078(0x0885); call_0156_00D8(0); // 010A–011B
log_0476_0078(0x088F); call_0201_000A(); call_0768_0024(0); // 011E–0134
log_0476_0078(0x089B); call_06B0_0134(0); // 0137–0148
log_0476_0078(0x08A6); call_06B0_018C(0); // 014B–015C
log_0476_0078(0x08B3); AX=call_0D29_2696(); call_0277_0336(AX); // 015F–0174
call_0277_02A6(); call_0277_0AE0(); DS8[0x3CD1]=0; // 0177–0181
log_0476_0078(0x08BD); far_return(); // 0186–0190
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed fixed sequence of helper calls alternating with debug strings. Sound/timer/display/memory/keyboard/mouse descriptions follow actual nearby strings, but successful return alone does not prove subsystem initialization success.

Preconditions: No direct stack parameters read; DS provides string offsets and globals. External helpers receive explicit zero words where shown.

Supported normal effects: Log Initializing; call083D:29CA(0); log Bootstrap ok; call0C2B:00DC(0); log Sound ok; call0BDE:0004(0); log Timer ok; call0156:00D8(0); log Display ok; call0201:000A(); call0768:0024(0); log Memory ok; call06B0:0134(0); log Keyboard ok; call06B0:018C(0); log Mouse ok; call0D29:2696(); forward AX to0277:0336; call0277:02A6 and0277:0AE0; write byte3CD1=0; log Initialize complete. Exact meaning of first two helpers is inferred from subsequent message labels.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Callee error behavior, register/segment preservation, execution timing, global interaction and failure recovery.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Static call ordering and source strings, direct xref to0201:000A confirmed in baseline graph. No full execution test.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Callee error behavior, register/segment preservation, execution timing, global interaction and failure recovery.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 6/10 — DOS_2_0_0476_0078

Conditional variadic debug-file writer

## 1. Identity, build and proof scope

DOS_2_0_0476_0078; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 6,
  "function_id": "DOS_2_0_0476_0078",
  "entry": "0476:0078",
  "last_instruction": "0476:00CC",
  "end_exclusive": "0xcd",
  "span_bytes": 85,
  "decoded_instruction_bytes": 85,
  "instruction_count": 30,
  "decoded_ranges": [
    [
      120,
      205
    ]
  ],
  "gaps": [],
  "local_returns": [
    204
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 11,
  "direct_callsites": 4,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0476:0078|55|push bp|
|0476:0079|8bec|mov bp, sp|
|0476:007B|803ed03c00|cmp byte ptr [0x3cd0], 0|
|0476:0080|7449|je 0xcb|
|0476:0082|833e2c0800|cmp word ptr [0x82c], 0|
|0476:0087|7505|jne 0x8e|
|0476:0089|b82e08|mov ax, 0x82e|
|0476:008C|eb03|jmp 0x91|
|0476:008E|b83008|mov ax, 0x830|
|0476:0091|50|push ax|
|0476:0092|683208|push 0x832|
|0476:0095|9ae606ee21|lcall 0x21ee, 0x6e6|
|0476:009A|8be5|mov sp, bp|
|0476:009C|a32c08|mov word ptr [0x82c], ax|
|0476:009F|0bc0|or ax, ax|
|0476:00A1|750d|jne 0xb0|
|0476:00A3|683c08|push 0x83c|
|0476:00A6|684608|push 0x846|
|0476:00A9|9a0c00ba1f|lcall 0x1fba, 0xc|
|0476:00AE|8be5|mov sp, bp|
|0476:00B0|8d4608|lea ax, [bp + 8]|
|0476:00B3|50|push ax|
|0476:00B4|ff7606|push word ptr [bp + 6]|
|0476:00B7|ff362c08|push word ptr [0x82c]|
|0476:00BB|9a2228ee21|lcall 0x21ee, 0x2822|
|0476:00C0|8be5|mov sp, bp|
|0476:00C2|ff362c08|push word ptr [0x82c]|
|0476:00C6|9afa05ee21|lcall 0x21ee, 0x5fa|
|0476:00CB|c9|leave |
|0476:00CC|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0476_0078.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 210
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 230
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 250
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 270
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 290
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 315
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 335
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 355
  },
  {
    "function_id": "DOS_2_0_0476_00CE",
    "address": 394
  },
  {
    "function_id": "DOS_2_0_0768_0024",
    "address": 471
  },
  {
    "function_id": "DOS_2_0_0C2B_0020",
    "address": 157
  }
]
```
Callees:

- 0476:0095 → 11EE:06E6 (FAR; PUSH CS prefix=False)
- 0476:00A9 → 0FBA:000C (FAR; PUSH CS prefix=False)
- 0476:00BB → 11EE:2822 (FAR; PUSH CS prefix=False)
- 0476:00C6 → 11EE:05FA (FAR; PUSH CS prefix=False)

## 6. Arguments and calling convention

Far-return compatible variadic frame: [BP+6]=format pointer; &SS:[BP+8] is variadic argument area; passes this near offset without explicit segment, so SS=DS or helper-specific interpretation is a precondition to the usual C model.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 06_DOS_2_0_0476_0078_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

PUSH BP/MOV BP,SP, no fixed locals. MOV SP,BP drops variadic helper args. After close, LEAVE drops remaining pushed handle. RETF4. SavedBP restored. Other registers/FLAGS depend on branch/callees.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|007B|DS|15568|1|R|
|0082|DS|2092|2|R|
|009C|DS|2092|2|W|
|00B0|SS|bp + 8|2|R|
|00B4|SS|bp + 6|2|R|
|00B7|DS|2092|2|R|
|00C2|DS|2092|2|R|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Reads3CD0 and082C; writes082C only after open. Last closed handle/pointer retained as boolean choosing append mode on later calls. Does not zero082C after close. DS strings082E="w",0830="a",0832/083C="debug.txt",0846="Error opening file %s".

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Reads3CD0 and082C; writes082C only after open. Last closed handle/pointer retained as boolean choosing append mode on later calls. Does not zero082C after close. DS strings082E="w",0830="a",0832/083C="debug.txt",0846="Error opening file %s".
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

If DS byte3CD0=0 leave immediately. Otherwise choose mode offset082E ("w") when word082C=0, else0830 ("a"); call11EE:06E6(filename0832,mode); reset SP=BP; storeAX at082C. On AX=0 call error helper0FBA:000C("Error opening file %s", "debug.txt") without an unconditional local exit. If helper returns, continue to output helper with handle,format,&arguments, then close helper using082C.

## 14. Reconstructed algorithm

Strongly inferred debug writer using file-open/format-write/close-like helpers, supported by "debug.txt", "w", "a", error text and argument forwarding. Direct control and data effects confirmed; libc names remain inferred.

If DS byte3CD0=0 leave immediately. Otherwise choose mode offset082E ("w") when word082C=0, else0830 ("a"); call11EE:06E6(filename0832,mode); reset SP=BP; storeAX at082C. On AX=0 call error helper0FBA:000C("Error opening file %s", "debug.txt") without an unconditional local exit. If helper returns, continue to output helper with handle,format,&arguments, then close helper using082C.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
push(BP); BP=SP; // 0078–0079
if (DS8[0x3CD0]!=0) { // 007B–0080
 mode=(DS16[0x082C]==0)?0x082E:0x0830; // 0082–008E
 AX=call_11EE_06E6(0x0832,mode); SP=BP; DS16[0x082C]=AX; // 0091–009C
 if (AX==0) { call_0FBA_000C(0x0846,0x083C); SP=BP; } // 009F–00AE
 call_11EE_2822(DS16[0x082C],SS16[BP+6],u16(BP+8)); SP=BP; // 00B0–00C0
 call_11EE_05FA(DS16[0x082C]); // 00C2–00C6
}
leave(); far_return(); // 00CB–00CC
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Strongly inferred debug writer using file-open/format-write/close-like helpers, supported by "debug.txt", "w", "a", error text and argument forwarding. Direct control and data effects confirmed; libc names remain inferred.

Preconditions: Far-return compatible variadic frame: [BP+6]=format pointer; &SS:[BP+8] is variadic argument area; passes this near offset without explicit segment, so SS=DS or helper-specific interpretation is a precondition to the usual C model.

Supported normal effects: If DS byte3CD0=0 leave immediately. Otherwise choose mode offset082E ("w") when word082C=0, else0830 ("a"); call11EE:06E6(filename0832,mode); reset SP=BP; storeAX at082C. On AX=0 call error helper0FBA:000C("Error opening file %s", "debug.txt") without an unconditional local exit. If helper returns, continue to output helper with handle,format,&arguments, then close helper using082C.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Exact helper signatures and ownership, fatal-error termination behavior, validity of retained closed-handle-as-sentinel, DS=SS assumption at variadic area use.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Static bytes + direct source strings + inspected helper wrappers11EE:06E6 and2822. No host file-write execution test.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Exact helper signatures and ownership, fatal-error termination behavior, validity of retained closed-handle-as-sentinel, DS=SS assumption at variadic area use.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 7/10 — DOS_2_0_0476_0000

Conditional defaults and always-reset state

## 1. Identity, build and proof scope

DOS_2_0_0476_0000; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 7,
  "function_id": "DOS_2_0_0476_0000",
  "entry": "0476:0000",
  "last_instruction": "0476:005D",
  "end_exclusive": "0x5e",
  "span_bytes": 94,
  "decoded_instruction_bytes": 94,
  "instruction_count": 24,
  "decoded_ranges": [
    [
      0,
      94
    ]
  ],
  "gaps": [],
  "local_returns": [
    93
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 3,
  "direct_callsites": 0,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0476:0000|803e2a0800|cmp byte ptr [0x82a], 0|
|0476:0005|743d|je 0x44|
|0476:0007|66c706ca3c20020700|mov dword ptr [0x3cca], 0x70220|
|0476:0010|b001|mov al, 1|
|0476:0012|a2c63c|mov byte ptr [0x3cc6], al|
|0476:0015|a2c73c|mov byte ptr [0x3cc7], al|
|0476:0018|a2ce3c|mov byte ptr [0x3cce], al|
|0476:001B|a2cf3c|mov byte ptr [0x3ccf], al|
|0476:001E|b8ffff|mov ax, 0xffff|
|0476:0021|a3bc3c|mov word ptr [0x3cbc], ax|
|0476:0024|a3be3c|mov word ptr [0x3cbe], ax|
|0476:0027|a3c03c|mov word ptr [0x3cc0], ax|
|0476:002A|32c0|xor al, al|
|0476:002C|a22a08|mov byte ptr [0x82a], al|
|0476:002F|a2c83c|mov byte ptr [0x3cc8], al|
|0476:0032|a2d03c|mov byte ptr [0x3cd0], al|
|0476:0035|c706c23c1900|mov word ptr [0x3cc2], 0x19|
|0476:003B|c706d63c0000|mov word ptr [0x3cd6], 0|
|0476:0041|a2dc3c|mov byte ptr [0x3cdc], al|
|0476:0044|c606d13c01|mov byte ptr [0x3cd1], 1|
|0476:0049|c606d23c00|mov byte ptr [0x3cd2], 0|
|0476:004E|66c706d83c00000000|mov dword ptr [0x3cd8], 0|
|0476:0057|c706c43cffff|mov word ptr [0x3cc4], 0xffff|
|0476:005D|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0476_0000.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_0476_0326",
    "address": 831
  }
]
```
Callees:

No direct calls in the decoded body.

## 6. Arguments and calling convention

No stack args; input byteDS:082A is initialization guard.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 07_DOS_2_0_0476_0000_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

No local frame/pushes; RETF4; AX changed toFF00 only in nonzero-guard branch. No calls; all other general/segment regs preserved except return.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0000|DS|2090|1|R|
|0007|DS|15562|4|W|
|0012|DS|15558|1|W|
|0015|DS|15559|1|W|
|0018|DS|15566|1|W|
|001B|DS|15567|1|W|
|0021|DS|15548|2|W|
|0024|DS|15550|2|W|
|0027|DS|15552|2|W|
|002C|DS|2090|1|W|
|002F|DS|15560|1|W|
|0032|DS|15568|1|W|
|0035|DS|15554|2|W|
|003B|DS|15574|2|W|
|0041|DS|15580|1|W|
|0044|DS|15569|1|W|
|0049|DS|15570|1|W|
|004E|DS|15576|4|W|
|0057|DS|15556|2|W|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Writes listed byte/word/dword fields; first branch uses XOR AL,AL, so AX becomesFF00 (AH remainsFF from001E). On guard-zero path AX is preserved. Later instructions leave FLAGS untouched; guarded path final arithmetic flags from XOR (AF undefined), unguarded path from CMP guard,0.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Writes listed byte/word/dword fields; first branch uses XOR AL,AL, so AX becomesFF00 (AH remainsFF from001E). On guard-zero path AX is preserved. Later instructions leave FLAGS untouched; guarded path final arithmetic flags from XOR (AF undefined), unguarded path from CMP guard,0.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

If guard!=0 write dword3CCA=0x00070220; set bytes3CC6,3CC7,3CCE,3CCF to1; set words3CBC,3CBE,3CC0 toFFFF; clear guard082A and bytes3CC8,3CD0; word3CC2=25; word3CD6=0; byte3CDC=0. Then always write byte3CD1=1,byte3CD2=0,dword3CD8=0,word3CC4=FFFF. First and later calls differ intentionally.

## 14. Reconstructed algorithm

Confirmed one-time guarded initialization plus unconditional resets. Semantic labels for most fields remain unknown.

If guard!=0 write dword3CCA=0x00070220; set bytes3CC6,3CC7,3CCE,3CCF to1; set words3CBC,3CBE,3CC0 toFFFF; clear guard082A and bytes3CC8,3CD0; word3CC2=25; word3CD6=0; byte3CDC=0. Then always write byte3CD1=1,byte3CD2=0,dword3CD8=0,word3CC4=FFFF. First and later calls differ intentionally.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
if (DS8[0x082A]!=0) { // 0000–0005
 DS32[0x3CCA]=0x00070220; // 0007
 AL=1; DS8[0x3CC6]=DS8[0x3CC7]=DS8[0x3CCE]=DS8[0x3CCF]=AL; // 0010–001B
 AX=0xFFFF; DS16[0x3CBC]=DS16[0x3CBE]=DS16[0x3CC0]=AX; // 001E–0027
 AL=0; DS8[0x082A]=DS8[0x3CC8]=DS8[0x3CD0]=0; // 002A–0032
 DS16[0x3CC2]=25; DS16[0x3CD6]=0; DS8[0x3CDC]=0; // 0035–0041
}
DS8[0x3CD1]=1; DS8[0x3CD2]=0; DS32[0x3CD8]=0; DS16[0x3CC4]=0xFFFF; // 0044–0057
far_return(); // 005D
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed one-time guarded initialization plus unconditional resets. Semantic labels for most fields remain unknown.

Preconditions: No stack args; input byteDS:082A is initialization guard.

Supported normal effects: If guard!=0 write dword3CCA=0x00070220; set bytes3CC6,3CC7,3CCE,3CCF to1; set words3CBC,3CBE,3CC0 toFFFF; clear guard082A and bytes3CC8,3CD0; word3CC2=25; word3CD6=0; byte3CDC=0. Then always write byte3CD1=1,byte3CD2=0,dword3CD8=0,word3CC4=FFFF. First and later calls differ intentionally.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Names/units of globals and why25 changes to18 when windir is nonzero. Whether all valid calls share same DS.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Static complete local closure, all direct stores enumerated. Whole-program alternate-entry proof open.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Names/units of globals and why25 changes to18 when windir is nonzero. Whether all valid calls share same DS.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 8/10 — DOS_2_0_0768_0008

Word getter at DS:3504

## 1. Identity, build and proof scope

DOS_2_0_0768_0008; SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 8,
  "function_id": "DOS_2_0_0768_0008",
  "entry": "0768:0008",
  "last_instruction": "0768:000B",
  "end_exclusive": "0xc",
  "span_bytes": 4,
  "decoded_instruction_bytes": 4,
  "instruction_count": 2,
  "decoded_ranges": [
    [
      8,
      12
    ]
  ],
  "gaps": [],
  "local_returns": [
    11
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 1,
  "direct_callsites": 0,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0768:0008|a10435|mov ax, word ptr [0x3504]|
|0768:000B|cb|retf |

## 4. CFG and blocks

See ../CFG/DOS_2_0_0768_0008.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[
  {
    "function_id": "DOS_2_0_0476_01D0",
    "address": 720
  }
]
```
Callees:

No direct calls in the decoded body.

## 6. Arguments and calling convention

No stack args; reads word DS:3504.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 08_DOS_2_0_0768_0008_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

No frame. RETF consumes4. AX modified; other registers preserved except CS/IP/SP return state; FLAGS unchanged.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0008|DS|13572|2|R|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

Exactly2 bytes read atDS:3504/3505; no memory writes. Under nominal startup DS maps to module offset0x2AC14, but entry DS cannot yet be universally assumed.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

Exactly2 bytes read atDS:3504/3505; no memory writes. Under nominal startup DS maps to module offset0x2AC14, but entry DS cannot yet be universally assumed.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

MOV AX,word DS:[3504]; RETF. Little-endian word; no sign extension or arithmetic; all FLAGS unchanged.

## 14. Reconstructed algorithm

Confirmed 16-bit state getter. Returned state meaning unknown.

MOV AX,word DS:[3504]; RETF. Little-endian word; no sign extension or arithmetic; all FLAGS unchanged.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
AX=DS16[0x3504]; // 0008
far_return(); // 000B
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed 16-bit state getter. Returned state meaning unknown.

Preconditions: No stack args; reads word DS:3504.

Supported normal effects: MOV AX,word DS:[3504]; RETF. Little-endian word; no sign extension or arithmetic; all FLAGS unchanged.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Global writers, meaning/range, entry aliases, caller-path DS provenance.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Static bytes and baseline direct-call candidate identity; no new runtime test claimed.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Global writers, meaning/range, entry aliases, caller-path DS provenance.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.



---

# Function 9/10 — WIN_1_10_0003_0D9E

Unsigned byte getter at DS:4BE1

## 1. Identity, build and proof scope

WIN_1_10_0003_0D9E; SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 9,
  "function_id": "WIN_1_10_0003_0D9E",
  "entry": "0003:0D9E",
  "last_instruction": "0003:0DA3",
  "end_exclusive": "0xda4",
  "span_bytes": 6,
  "decoded_instruction_bytes": 6,
  "instruction_count": 3,
  "decoded_ranges": [
    [
      3486,
      3492
    ]
  ],
  "gaps": [],
  "local_returns": [
    3491
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 1,
  "direct_callsites": 0,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0003:0D9E|a0e14b|mov al, byte ptr [0x4be1]|
|0003:0DA1|2ae4|sub ah, ah|
|0003:0DA3|cb|retf |

## 4. CFG and blocks

See ../CFG/WIN_1_10_0003_0D9E.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[]
```
Callees:

No direct calls in the decoded body.

## 6. Arguments and calling convention

No stack args. NE segment index3, DS supplied by Windows/caller; do not equate index with a real-mode segment.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 09_WIN_1_10_0003_0D9E_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

No frame, RETF4. AX modified, FLAGS CF/AF/OF/SF=0,ZF/PF=1; other modeled flags preserved. Other registers preserved except return.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0D9E|DS|19425|1|R|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

One byte read atDS:4BE1, no stores. Full AX result0..255; upper16 EAX unchanged by16/8-bit operations in the CPU experiment.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

One byte read atDS:4BE1, no stores. Full AX result0..255; upper16 EAX unchanged by16/8-bit operations in the CPU experiment.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

MOV AL,DS:[4BE1]; SUB AH,AH; RETF. SUB zeroesAH and fixes arithmetic flags unlike a flag-preserving zero-extension instruction.

## 14. Reconstructed algorithm

Confirmed returns unsigned byte in AX; application meaning unknown.

MOV AL,DS:[4BE1]; SUB AH,AH; RETF. SUB zeroesAH and fixes arithmetic flags unlike a flag-preserving zero-extension instruction.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
AL=DS8[0x4BE1]; // 0D9E
AH=0; set_SUB_flags_for_equal_operands(); // 0DA1
far_return(); // 0DA3
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed returns unsigned byte in AX; application meaning unknown.

Preconditions: No stack args. NE segment index3, DS supplied by Windows/caller; do not equate index with a real-mode segment.

Supported normal effects: MOV AL,DS:[4BE1]; SUB AH,AH; RETF. SUB zeroesAH and fixes arithmetic flags unlike a flag-preserving zero-extension instruction.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Field producer and meaning, NE selector validation and protected-mode execution, alternate entries.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Exhaustive all256 byte values in isolated Unicorn with return-stack and zero-write checks.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Field producer and meaning, NE selector validation and protected-mode execution, alternate entries.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.


## PASS002 cross-version evidence update

See ../ASM_DIFF/math_helper_cross_version_CFG.json, INSTRUCTION_LEVEL_DIFF_PASS002.csv and ADJACENT_VERSION_DIFF.json. Local CFG/instruction differences compared from actual bytes; global field equivalence remains unproved. Independent GNU objdump verifies this body's local instruction boundaries and bytes.


---

# Function 10/10 — WIN_1_10_0003_0DA4

Unsigned byte getter at DS:4BE2

## 1. Identity, build and proof scope

WIN_1_10_0003_0DA4; SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Reference version label from supplied filename; release provenance not independently established. Claim labels: Confirmed for machine effects, Inferred for semantic names, Unknown for unproved scope.

## 2. Entries and exact decoded boundaries

```json
{
  "number": 10,
  "function_id": "WIN_1_10_0003_0DA4",
  "entry": "0003:0DA4",
  "last_instruction": "0003:0DA9",
  "end_exclusive": "0xdaa",
  "span_bytes": 6,
  "decoded_instruction_bytes": 6,
  "instruction_count": 3,
  "decoded_ranges": [
    [
      3492,
      3498
    ]
  ],
  "gaps": [],
  "local_returns": [
    3497
  ],
  "local_unresolved_jumps": 0,
  "overlap_detected": [],
  "local_block_count": 1,
  "direct_callsites": 0,
  "full_boundaries_verified": false,
  "all_entry_points_verified": false,
  "complete_behavior_verified": false
}
```
Ranges are half-open. These are exact locally decoded ranges under modeled call returns, not proof of all aliases/external entries. No next-function-end assumption.

## 3. Original bytes and ASM

| Address | Original bytes | Corrected ASM |
|---|---|---|
|0003:0DA4|a0e24b|mov al, byte ptr [0x4be2]|
|0003:0DA7|2ae4|sub ah, ah|
|0003:0DA9|cb|retf |

## 4. CFG and blocks

See ../CFG/WIN_1_10_0003_0DA4.json for all instruction edges, basic-block partition and local returns. Calls have explicit assumed-return continuations; non-returning callee proof is unresolved.

## 5. Caller/callee relationships

Callers:
```json
[]
```
Callees:

No direct calls in the decoded body.

## 6. Arguments and calling convention

No stack args; NE segment index3; DS context external.

## 7. Registers and FLAGS

Complete instruction-by-instruction read/write, FLAGS-action metadata and operand sizes are in 10_WIN_1_10_0003_0DA4_INSTRUCTIONS.csv. Corrections98/99 applied to printed names and register sets. Metadata alone does not prove values/flags across external calls.

## 8. Stack frame and return state

No frame, RETF4. AX result0..255; CF/AF/OF/SF=0,ZF/PF=1, other modeled flags preserved.

## 9. Memory operations and effective addresses

|IP|Segment|Effective address expression|Bytes|Decoder access|
|---|---|---|---:|---|
|0DA4|DS|19426|1|R|

Implicit stack accesses and external callee accesses are additional. Segment defaults use BP/SP→SS; overrides take precedence. String-instruction destination ES context requires explicit review if present.

## 10. Globals and data structure fields

One byte atDS:4BE2; no writes. Difference against0D9E is immediate absolute memory offset+1; algorithms same, inputs distinct.

## 11. Dataflow and alias constraints

DS-origin evidence and caller references are in ../DATAFLOW/. Byte/word/dword aliases remain significant; do not collapse overlapping stores. All high-level models assume code, stack and described data do not destructively alias. Effective16-bit offsets wrap unless a narrower no-wrap argument is stated.

## 12. Constants, tables and strings

One byte atDS:4BE2; no writes. Difference against0D9E is immediate absolute memory offset+1; algorithms same, inputs distinct.
Relevant immediate values and their exact use sites are preserved in the ASM/CSV; numerical constants alone do not establish units.

## 13. Branches, loops and invariants

MOV AL,DS:[4BE2]; SUB AH,AH; RETF. Independent field lookup; no conditional branches, loops, calls, RNG or time read.

## 14. Reconstructed algorithm

Confirmed second adjacent byte getter with same operations as0D9E. It accesses a different field; semantic interchangeability is not established.

MOV AL,DS:[4BE2]; SUB AH,AH; RETF. Independent field lookup; no conditional branches, loops, calls, RNG or time read.

## 15. RAW Ghidra/IDA decompilation

Unavailable. No raw Ghidra/IDA output was supplied or produced. This report preserves decoded bytes and marks hand reconstruction separately.

## 16. Corrected hand pseudocode

```c
AL=DS8[0x4BE2]; // 0DA4
AH=0; set_SUB_flags_for_equal_operands(); // 0DA7
far_return(); // 0DA9
```
Functions named by addresses preserve unknown helper identity. FLAGS and register postconditions are specified separately; do not delete machine-state effects.

## 17. Behavioral reconstruction and pre/postconditions

Confirmed second adjacent byte getter with same operations as0D9E. It accesses a different field; semantic interchangeability is not established.

Preconditions: No stack args; NE segment index3; DS context external.

Supported normal effects: MOV AL,DS:[4BE2]; SUB AH,AH; RETF. Independent field lookup; no conditional branches, loops, calls, RNG or time read.

Fault/non-return paths may invalidate normal postconditions; see unknowns.

## 18. Cross-version matching

See ../ASM_DIFF/BATCH10_CROSS_VERSION_CANDIDATES.json and existing PASS001 matrices. Byte signatures are correspondence candidates. Missing match is UNKNOWN_MATCH, not ADDED/REMOVED. Field-address differences need data-layout mapping before semantic equivalence.

## 19. Instruction additions/removals/modifications

No unproved additions/removals claimed. Candidate signatures and differing operands are retained exactly; Win getter pair differs only in DS address between the two local bodies. Math prototype changes and global displacements are not normalized away without evidence.

## 20. CFG changes and error paths

Field meaning, producers, whether first/second fields relate to input or other state; Win16 runtime selector and calling context.

Local unresolved targets: []. Zero local unresolved jumps is not a whole-program CFG-complete claim.

## 21. Dependencies and platform assumptions

DOS addresses are load-module-relative segment:offset; capture used load_segment0x1000. Win addresses use NE segment index:offset and original physical segment table; copied-code Unicorn execution does not validate Windows selectors. No rendering/platform equivalence implied.

## 22. Timing, RNG and observable state

No supported timing/cadence claim. Direct instruction set and calls are shown; any time/RNG/I/O behavior of called functions remains a dependency. Leaf bodies without such reads have no direct RNG/time access.

## 23. Runtime/emulation evidence

Exhaustive all256 byte values in isolated Unicorn. Cross-version candidate search uses adjacent getter-pair signature.
All new experiments are isolated CPU or startup-prefix simulations, not original game gameplay.

## 24. Unresolved questions and next discriminating tests

Field meaning, producers, whether first/second fields relate to input or other state; Win16 runtime selector and calling context.
Next: establish caller contexts and DS at actual entry, trace producers for each field, validate alternate/tail/shared entries, and compare same inputs against original runtime. Breakpoints at entry/return with stack/segment snapshots distinguish calling-convention hypotheses.

## 25. Verification status and history

2026-11-04 PASS002/BATCH01–10. Static local analysis only unless explicit experiment listed. Complete per-function verification false until all relevant global-entry/boundary/context/runtime gates are met. Original bytes, scripts and output hashes retained. Confidence High for decoded byte-local operations; Medium/Low for semantic naming depending on unresolved data provenance.


## PASS002 cross-version evidence update

See ../ASM_DIFF/math_helper_cross_version_CFG.json, INSTRUCTION_LEVEL_DIFF_PASS002.csv and ADJACENT_VERSION_DIFF.json. Local CFG/instruction differences compared from actual bytes; global field equivalence remains unproved. Independent GNU objdump verifies this body's local instruction boundaries and bytes.
