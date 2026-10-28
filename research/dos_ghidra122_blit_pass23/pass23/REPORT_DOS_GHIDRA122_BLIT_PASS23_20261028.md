# Blit pass23 — stride, page selection, source wrap and unclipped coordinates

## Finding
Confirmed for six distinct supplied DOS images: the original column-major blitter uses explicit draw width/height and source column stride. Its extra source-width word did not affect the tested output, and static code contains no read of that argument. Page selection tests zero versus nonzero, destination row uses y low8, and tested off-screen coordinates are not clipped by this routine. Source offsets wrap16-bit.

## Evidence
3024 passing executions:7 coordinate pairs x3 page words x2 source strides x3 transparency words x2 source offsets x2 source-width words x6 builds. Coordinates:(0,0),(1,7),(3,199),(319,199),(320,200),(ffff,255),(4,256). Page words0,1,ffff; strides3/5; transparencyffff,31,255; source offsets0200/fffc; extra source-width words0/99. Draw region3columns x2rows throughout. Original routine executes; no code hook substitutes its logic. OUT and memory-write hooks only observe.

Source bytes use a repeating10,31,255,40,50,60,70 pattern to exercise transparency and stride padding. Both source positions are populated with16-bit offset wrapping, including reads pastffff into0000. Page globals are extracted separately from each build and assigned segments7000/8000. Tests compare every observed lower plane mask,physical destination byte address and pixel value, plus far return,SP and DS restoration. All samples use mapped ordinary memory; this is not a hardware VGA/DAC test.

Exact routine entry,page-global addresses and EXE SHA256 are in evidence/blit_boundaries.json, followed by all actual write traces and parameters. V1.9 routine1156:07de; its page globals are DS:012e(primary) andDS:012c(alternate). These addresses are not assumed identical in older builds.

## Behavior model
Let sx=x unsigned16,y8=y&ff,initial byte base=(y8*80+(sx>>2)) mod65536. For columnc starting0:

- Plane mask=1<<((sx+c)&3).
- Column destination byte=base+floor(((sx&3)+c)/4), reduced modulo65536.
- Rowr destination offset=columnByte+80*r, reduced modulo65536.
- Source offset=(sourceOffset+c*columnStride+r) mod65536.
- Destination segment=primary if page word0,alternate otherwise.
- Negative signed transparency word bypasses comparison (ffff tested). Otherwise suppress equal pixel (31 and255 tested).

Changing stride from3 to5 changes source columns independently of draw size3x2. Source-width argument at entrySP+12 was0/99 with identical output for otherwise matching cases; original routine has no reference to this argument. It is retained for ABI/caller compatibility. The actual layout passes its source width here but also supplies drawWidth separately.

Examples: y256 selects the same initial row as y0; y199 with two draw rows writes into row200. x319 can advance into following byte columns for the2nd/3rd drawn columns, and x320 still emits writes. The routine therefore supplies no320x200 clipping for these calls. This does not prove that game callers permit these coordinates; upstream clipping/validation remains a separate contract.

The highest tested destination offsets do not crossffff; destination-offset modulo behavior is visible in16-bit instructions and the model but a physical destination wrap boundary is not dynamically exercised here. Source-offset wrap atfffc is directly tested. No zero draw counts are tested; original LOOP/DEC behavior requires separate bounded analysis before supporting zero-size calls.

## Ghidra relationship
Uses exact reconstructed EXEs and Ghidra12.2 instruction exports, with blitter ABI from pass22. No project metadata/code mutation was required; latest projects remain pass22. Function count3479 and unresolved seed status are unchanged. No new global decompiler completion or parity percentage is claimed.

## Confidence and open questions
Confirmed/High for tested nonzero3x2 draws,stride/page/transparent choices,source wrap and lack of internal clipping at sampled coordinates. Unknown: zero sizes,large draw counters,destination wrap,other negative transparency words,actual VGA address/memory mode,DAC,palette and upstream clipping. Supplied1.8/1.9 remain identical. Whole-game/pixel-perfect display parity remains open.

## Reproduce
`/usr/bin/python3 scripts/verify_blit_boundaries.py` with Unicorn. Required pass7 specs,EXEs,instruction exports and pass18 blitter-call metadata are archived. Next test zero/large draw counters with bounded execution and identify caller clipping before integrating complete VGA/page/palette behavior.
