# Blit pass24 — zero counters and destination-offset wrap

## Finding
Confirmed across six distinct DOS images: a single zero draw counter does not mean an empty draw. With the other dimension1, original opaque blitter performs65536 pixel writes and returns. Destination16-bit offset wrap is also directly demonstrated by completed2x1000 draws. Both-zero cases are observed only through a bounded64-write prefix.

## Evidence
204 passing target cases, split as follows:

| Cases | Setup and completion |
|---|---|
| 48 | Width0/1 x height0/1 x transparencyffff/31 x6 builds. Single1x1 returns; any zero counter is stopped after64 writes |
| 12 | Complete opaque draws0x1 and1x0 across6 builds, each65536 writes and normal far return |
| 144 | Completed2x1000 draws: x0/3/ffff,y0/255,page0/1,transparencyffff/31 across6 builds |

Original blitter instructions execute with mapped synthetic source/destination memory. OUT/memory-write hooks only observe; prefix tests call emu_stop after64 observed writes. Completed zero cases check every write incrementally against an independent pointer/mask formula and require exactly65536 writes,normal CS:IP return,SP restoration and DS restoration. This accounts for786432 verified writes in those12 cases alone. Prefix observations are not counted as completed calls.

Source is65536 repeated byte10 for zero-counter cases. Since transparent color31 differs, each visited pixel emits a write in the prefix tests. Opaque full-zero tests bypass comparison. Normal1x1 baselines emit one write. For width0,height1,plane mask cycles1,2,4,8 and destination byte advances after every fourth column. For width1,height0,plane stays1 and destination offset advances80 per row modulo65536. These actual traces establish the16-bit wraparound counter behavior rather than relying only on assembly interpretation.

For destination-wrap tests, source is a deterministic4096-byte i mod61 pattern,source offset0,column stride1007,draw width2,height1000. Expected addresses are generated modulo65536; every observed plane/address/value and transparency-suppressed count matches. Both primary/alternate page segments7000/8000 are exercised. This creates a draw taller than the8-bit dimensions used by normal BSF records; actual caller reachability is not claimed.

Exact routine entry and EXE SHA256 are in evidence/blit_zero_wrap.json. Page globals are inherited from pass23's separately extracted per-build addresses. The tests do not patch code or replace blitter logic. No full VGA/DAC,palette or display timing emulation.

## Behavior model and limits
Original LOOP/DEC counters are entered without a zero-size precheck. Starting at0 wraps throughffff and eventually reaches0 after65536 decrements. A single zero dimension therefore expands that loop to65536 iterations. For both dimensions0,the64-write observed prefix is consistent with nested wrapping loops; the entire nested case is not executed and no completed-runtime duration or final framebuffer result is claimed.

Destination DI is16-bit,so vertical row increments crossffff and continue at0000 in the same destination segment. Completed1000-row cases directly test that wrap,extending pass23's previously only-static destination-wrap model. Source wrap and page selection remain covered by pass23. None of this establishes upstream acceptance of zero or very large draw dimensions.

## Ghidra relationship
Uses original EXEs and Ghidra12.2 instruction/ABI evidence from pass22/23. No metadata change was necessary; current projects remain pass22 and function count3479. Eight uncertain candidate seeds remain retained. No global decompiler completion or parity percentage is inferred.

## Confidence and next test
Confirmed/High for completed single-zero opaque cases,observed64-write prefixes and completed destination-wrap cases. Unknown: completed both-zero behavior under actual VGA,zero sizes combined with all-transparent inputs,caller validation,actual device address modes/palette/timing and complete game parity. Supplied1.8/1.9 still share one image. Next identify and verify clipping/dimension checks in actual blitter callers,then page/palette setup.

## Reproduce
`/usr/bin/python3 scripts/verify_blit_zero_wrap.py` with Unicorn. Inputs include pass7 EXEs/specs and pass23 entry/page metadata; required Ghidra instruction exports are also archived. Output separates stopped prefixes from returned calls explicitly.
