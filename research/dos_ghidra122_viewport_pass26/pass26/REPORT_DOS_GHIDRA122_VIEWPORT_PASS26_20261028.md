# Viewport pass26 — split-boundary provenance and default caller chain

## Finding
Confirmed across six distinct DOS images: the split boundary is computed from the configured viewport-width word. Default304 gives height152,left8,top4,bottom155. All three direct split-wrapper callsites found per build pass y4 and transparency0. Under this arithmetic/default combination,the split height min(152,imageHeightByte) cannot be negative. This narrows the synthetic negative-boundary concern from pass25 without proving all startup/configuration paths safe.

## Evidence
492 target cases completed:312 original viewport arithmetic setter cases and180 setter-to-split-to-original-blitter chains. Ghidra12.2 instruction exports supply addresses/call contexts; reconstructed EXEs execute in Unicorn. Two downstream setter dependencies are mocked. No full DOS/VGA/DAC or whole-game reachability test.

Setter matrix:52 width words x6 images. Values include aligned0..328 step8,plus1,7,15,199,255,319,321,32767,32768,65535. Original setter runs through both downstream callsites,which are skipped. Every one of its nine output words is compared against the signed/wrapped model; far return,SP,DS and both dependency-call occurrences are checked. This verifies local arithmetic before/around mocked dependencies,not all eventual global state after real downstream execution.

Chain matrix: x8/290/139 x graphic width1/16 x height0/1/152/153/255 x6 images =180. Each run executes original setter at configured width304,checks boundary155,then original split wrapper and original blitter. Only the same two setter dependencies are mocked. Source is a deterministic i mod61 byte pattern,record points to6000:0200,primary page segment7000. OUT/map-mask and all pixel writes are observed and compared in original two-phase order. Full far return/SP/DS checked. Synthetic image heights255 are boundary probes,not claimed real loaded HUD asset sizes.

## Provenance model
Let W=signed16(sourceWidth),H=W arithmetic-shift-right1,L=(320-W) signed32 arithmetic-shift-right1,T=signed16(L)>>1. Original writes nine16-bit output words:

| Offset from output base | Value |
|---|---|
| +0 | Original width bits |
| +2 | H |
| +4 | L |
| +6 | L+W-1 |
| +8 | T |
| +10 | T+H-1 (split boundary) |
| +12 | L+H |
| +14 | T+(H>>1) |
| +16 | Previous word<<4 |

All stored results wrap16-bit. At width304:304,152,8,311,4,155,160,80,1280. Output meanings beyond rectangle/counter arithmetic are analytical labels; related projection dependencies were not executed.

V1.9 setter1277:0bc2,source widthDS:4144,output baseDS:4542,boundaryDS:454c. DOS1.0 setter1273:0b62,sourceDS:3f9c. All build addresses/hashes,full setter instructions,direct boundary/width references and split caller contexts are in evidence/viewport_boundary.json.

Each build's exported instructions contain13 explicit direct references to the split-boundary global,including one matching direct store by the setter. This is an instruction-reference inventory,not proof of no indirect/aliased writes. The width references show an initialization dword304 and a separate parsing path that masks the width low byte withf8 before calling the setter. Alignment masking alone does not establish a valid range. Config file reads and menu pointers can also affect the source; their complete validation/reachability remains open.

## Actual direct split callers
Across all6 exports,the three direct callsites use(x,y)=(8,4),(290,4),(139,4),transparency0,with distinct near record offsets. V1.9 callsites183c:0947,095a,096d. The context includes immediate argument pushes; caller branch preconditions and actual record initialization are not fully run.

With boundary155 and y4,first portion height n=min(152,Hbyte). If Hbyte<=152,the whole nonzero image is drawn with transparent color0. If Hbyte>152,the first152 rows use transparent0 and remaining rows use opaqueffff from the appropriately advanced source pointer. Height0 emits no blit through this split wrapper under default arithmetic. The chain verifies these cases and exact pixel order. This does not make zero width safe: the chain deliberately uses nonzero width1/16 and pass25 shows the wrapper forwards width0 when a draw is selected.

## Classification and remaining uncertainty
Confirmed/High: local setter arithmetic,default output,immediate direct caller arguments,and original chain writes with injected source/page memory. Confirmed local implication: the pass25 negative n case is excluded for those direct y4 calls if boundary155 holds. Unknown: complete allowed viewport range,configuration/parser failures,actual downstream setter effects,all indirect callers,real loaded HUD dimensions and full game/device parity. Extreme widths in the matrix are probes,not claimed reachable settings. Supplied1.8/1.9 remain one identical image.

## Ghidra/artifact scope
Uses preserved Ghidra12.2 instruction exports; no project/EXE metadata mutation or new function/decompiler-count claim. Current project snapshots remain pass22; this pass supplies reproducible local contracts and callsite evidence. It does not reclassify global1:1 parity as complete.

## Reproduce and next step
`/usr/bin/python3 scripts/verify_viewport_boundary.py` then `/usr/bin/python3 scripts/verify_default_split_chain.py` with Unicorn. Required EXEs,specs,instruction exports and pass25/pass23 metadata are archived. Next trace viewport-width configuration/menu range checks and original downstream setter functions,then verify real record dimensions at the three direct calls.
