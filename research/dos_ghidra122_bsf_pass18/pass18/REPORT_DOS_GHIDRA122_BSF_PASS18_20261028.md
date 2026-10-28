# BSF pass18 — page layout, line rules and function recovery

## Finding
Confirmed across six distinct DOS images: the BSF page layout starts at(x12,y7), advances lines by11, uses fixed6-pixel space advance, tab stops based on four logical columns, and asks a separate width helper for other byte advances. '#' ends the page only when encountered at a new line start; inline '#' is sent to the glyph renderer. A line starting at y>=205 takes the fatal branch.

## Evidence
156 passing executions:13 inputs x two injected glyph widths3/7 x6 images. Inputs:empty,ABC,A space B,A tab B,tab B,A CR LF B,A#B,#ABC,A LF #B,two empty lines thenB,e9 Z,18 lines,19 lines. Twelve19-line cases stop at the fatal call site before executing the fatal handler. Original complete layout routine executes; UI rectangle/header formatting,color queries,glyph renderer,width helper and final flush are mocked. Percent-format/bitmap commands are not entered.

Assertions cover every submitted glyph byte,x,y; low-byte color5d and flags0; width-helper call count; fatal versus normal exit; flush count; and normal far return/SP. Header sprintf is mocked to write H NUL into its stack destination. The tests use page2,total9 to exercise argument presence without relying on original numeric heading formatting. No actual framebuffer,font table,DOS console or header rendering is executed.

V1.9 entry1d25:1294; character call1d25:13de; width query1d25:13fb; tab arithmetic1d25:1406..1422; space1d25:1424; line step1d25:1436; fatal1d25:133f; flush1d25:1443. Exact per-build entries/calls/hashes and glyph traces are in evidence/text_layout.json. The prior exports leave this routine unowned in five builds; DOS1.2 already has its function entry. Pass17 viewer calls it directly.

## Behavior model (plain byte path only)
Start at text pointer. Empty text performs no body glyph calls. Initial y=7. At each new line: if current byte is'#', stop; if y>=205, call fatal handler; x=12,column=0. Read bytes until NUL or LF. For every ordinary byte, including space,tab,CR and inline'#', submit a one-byte NUL-terminated stack string to the text renderer first. Then:

| Byte | Next position |
|---|---|
| Tab09 | column +=4-(column mod4); x=6*(column+2) |
| Space20 | x+=6; column++ |
| Other tested byte | x+=injected width-helper return; column++ |
| LF0a | No glyph submission; y+=11; advance text and begin new line |

Tab x is recomputed from logical column, not aligned from accumulated variable-width x. Example with width7: A starts12,tab starts19,then B starts36. With width3: A12,tab15,B36. The tab byte itself is still submitted to the glyph renderer; visual interpretation by that renderer is not established here. CR is likewise submitted and gets width-helper advancement; LF is the actual line delimiter in this routine.

Line start y values7,18,...194 are accepted(18 lines). The nineteenth nonterminated/new line starts205 and reaches fatal before drawing its first byte. An inline '#' is drawn, whereas '#ABC' and 'A LF #B' terminate at the marker. These are page-layout semantics, not pixel-perfect output.

## Ghidra12.2 changes
Copied pass17 projects into pass18/projects. Created five function entries and typed/renamed the existing DOS1.2 entry as analyst-named `LayoutBsfPage`, with far-call void signature: text pointer dwordSP+4,pageNumber ushortSP+8,totalPages ushortSP+10. Comments explicitly limit evidence to plain-text layout. All six new target stock decompilations complete. Every prior function entry remains; one entry added in each of five images and none in DOS1.2. Instruction addresses/bytes hash identically before/after. Candidate inventory increases3474->3479; no global decompiler count or parity percentage is inferred. Eight prior uncertain seeds remain retained.

## Confidence and unknowns
Confirmed/High for tested plain-text positioning, line/page delimiters, error threshold and function recovery under mocked glyph/UI dependencies. Unknown: actual glyph width lookup/rasterization,font changes,percent commands/inline bitmaps,header formatting and clipping,real UI/framebuffer behavior. Supplied1.8/1.9 still share one image. Full render/gameplay1:1 parity remains open.

## Reproduce and next step
`/usr/bin/python3 scripts/verify_bsf_text_layout.py` with Unicorn. Inputs:pass7 specs,EXEs,instruction exports and pass17 viewer call metadata. `python scripts/run_pass18_recovery.py` recreates metadata from pass17 with Ghidra12.2/JDK25 at configured paths. Updated projects,C,creation/storage/body information,hashes and logs are archived. Next recover percent-command parser and original width helper, then execute text-to-framebuffer path with real font data.
