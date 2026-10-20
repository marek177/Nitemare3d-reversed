# Nitemare 3-D Win16 v1.10 — REP destination closure, second pass

Date: 20 October 2026. Primary evidence: the user's already-archived original
Win16 Ghidra ASM listing nite3w(1).docx and original v1.10 C decompilation.
No new original EXE SHA recheck or Windows 3.11 runtime test in this pass.

## Status (83 original Ghidra-listed REP instructions)

| Class | Sites |
|---|---:|
| Already source/destination bounded in prior pass | 34 |
| Newly source-bounded portal/pentagram literals | 10 |
| Newly source-bounded 64,000-byte video operations | 2 |
| Newly symbolically bounded LocalAlloc fill | 1 |
| Still lacking complete pointer or length proof | 36 |
| **Total** | **83** |

Fixed-size/source-bounded = 46; symbolic size = 1; open = 36.
These grades must not be conflated with whole-program 1:1 parity.

## Ten literal-copy REP sites in FUN_1010_C126

Original function begins NE3:C126 ENTER 0x102,0. Decompiled original C
identifies char local_104[256]. Five fixed DGROUP strings are concatenated
using five pairs of REP MOVSW/MOVSB.

| Fixed source | DGROUP starting offset | Next literal | Upper bytes incl. NUL | REP pair |
|---|---|---|---:|---|
| Portal introduction | 1360 | 13E2 | 130 | C158/C15C |
| Red Pentagram | 1242 | 1256 | 20 | C190/C194 |
| Green Pentagram | 1256 | 126C | 22 | C1C8/C1CC |
| Blue Pentagram | 126C | 1280 | 20 | C200/C204 |
| Yellow Pentagram | 1280 | 1296 | 22 | C238/C23C |

Source pointers in original DGROUP at 017A, 014E, 0152, 0156,
015A hold the above offsets and selector 1048. Their recovered
Ghidra direct XREFs show reads in the original C126 function; this
does not prove absence of alias-based pointer corruption.

Each optional append replaces the last NUL of accumulated text.
Maximum full output including the final NUL, conditional on original
literal pointer values:

    130 + (20-1) + (22-1) + (20-1) + (22-1) = 210 bytes
    intended local buffer size = 256 bytes
    conditional remaining space >= 46 bytes

This is a source-local, original-literal bound, not an unconditional
stack/DGROUP-selector alias exclusion. The compiler uses BP-relative
destination offsets and DS/ES segment swaps; the intended stack-local
destination interpretation must hold. Ten original REP sites are
locally bounded by these literal lengths, but a damaged source pointer
or abnormal segment alias lies outside this local proof.

## Two video-segment operations, exactly 64,000 bytes

Original NE3:3A73:
- load ES from word DS:[51A0]
- DI=0, CX=0x7D00; REP STOSW => ES:0000..F9FF.

Original NE3:4719:
- load ES from word DS:[51A0]
- DI=0, DS is switched to selector 00BC, SI=0
- CX=0x7D00; REP MOVSW => 64,000 bytes written ES:0000..F9FF.

The selector word DS:[51A0] is written in WinG/video setup at
NE3:2FC5. The lengths and address provenance are statically known,
but the selector is not independently proven non-aliasing with DGROUP
in every invalid/reentrant state. The two sites are therefore
source-bounded with an explicit selector-provenance caveat.

## One LocalAlloc zero-fill with a nominal 1-byte round-up

Original FUN_1008_66FE, only named Ghidra caller
FUN_1000_542A at 0:5446:

    2:6709 MOV AX,[BP+6]          ; unsigned parameter
    2:670C MUL WORD [BP+8]       ; unsigned word product n
    2:670F JNC 6716              ; overflow branch returns failure
    2:6716 PUSH AX
    2:6717 CALL FAR FUN_1008_5AB0 ; LocalAlloc(n)
    2:671C POP CX                ; original n
    2:671D OR AX,AX              ; checks allocation result
    2:6722 MOV DI,AX             ; allocated block
    2:6724 MOV AX,DS
    2:6726 MOV ES,AX
    2:6728 XOR AX,AX
    2:672A INC CX
    2:672B SHR CX,1
    2:672D REP STOSW

On successful allocation only, original requested allocation bytes
n versus written bytes obeys this exact uint16 equation:

    words = (((n + 1) & 0xFFFF) >> 1)
    bytes_written = 2 * words

- Even n from 0 to 65534: writes n bytes.
- Odd n from 1 to 65533: writes n+1 bytes, 1 beyond nominal request.
- For n=65535: INC CX wraps and REP STOSW writes 0 bytes.

This does not establish damage to an adjacent heap object: original
Win16 LocalAlloc may round up block size and allocation success may
depend on the memory manager. It is not safe to emulate a stray
host C++ write without its sandbox/heap model.

### Newly recovered interprocedural reachability gate

Importantly, the original Ghidra callgraph identifies one direct
caller of the underlying LocalAlloc-fill function at 0:5446,
inside FUN_1000_542A. That function itself has exactly two
Ghidra-named direct callers:

| Direct caller | Pushed element width | Product reaching 2:66FE |
|---|---:|---|
| 0:5588 (FUN_1000_557A) | 0x000A = 10 | 10 * count |
| 0:5865 (FUN_1000_5856) | 0x0006 = 6 | 6 * count |

Both products are mathematically even for every 16-bit count.
If MUL overflowed, the original helper branches to failure
rather than allocating. Otherwise LocalAlloc is passed an
**even** nominal byte count, and the original zero-fill writes
exactly that count. The odd-size one-byte-extra branch therefore
does **not** arise from either currently known direct gameplay caller.

This is a higher-level conditional static reachability result,
not an exhaustive proof against unrecognized, address-taken or
indirect calls to the allocation helpers. Original code also
may pass zero count; its separate helper substitutes one byte
for LocalAlloc(0) while the zero-fill loop still writes zero,
which is not the odd-size overrun case.

The regression tests exhaustively check all 65,536 count values for
both direct caller element widths, including product overflow.

## Regression and provenance limits

- Original Ghidra REP evidence ledger:
  other/n3d/builds_12/static_byte_evidence/
  N3D_Win110_Ghidra_REP_destination_register_20261020.csv
- Static consistency auditor:
  tools/n3d_win16_rep_destination_audit.py
- Synthetic deterministic unit tests:
  tests/test_n3d_win16_rep_destination_audit.py
- CI: .github/workflows/win16-timer-ne-proof.yml

The test suite sweeps all 65,536 possible uint16 allocation sizes for
the exact round-up arithmetic, validates the five original literal
source lengths, the 210-byte worst-case string, and 64,000-byte
video operations, and rejects deliberately altered lengths/opcode classes.
These tests do not execute original Windows code.

The seven previously closed fixed-DGROUP REP intervals remain disjoint
from clock DS:46B2 and one-shot latch DS:00A2.

## Remaining P0 work

36 Ghidra-listed REP sites still lack complete destination/extent
provenance. Prioritize generic memory/string helpers near
2:605F/6063, 2:6092/6096, 2:6CA0/6CA4, 2:7264/7268,
2:738B/738F, four filename staging sites at 3:527E..52A5
and unbounded rectangle fills.

Also separately verify source literal pointer table aliases, DS:[51A0]
video-selector identity across setup/teardown, odd LocalAlloc behavior
under historical Win16 heap semantics, and global indirect FAR writers.

No new 1:1 gameplay, render or timing parity percentage is asserted.
