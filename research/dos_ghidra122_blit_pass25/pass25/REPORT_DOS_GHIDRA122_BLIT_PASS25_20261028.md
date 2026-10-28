# Blit pass25 — caller page gate and signed split boundary

## Finding
Confirmed for six distinct supplied DOS images: two actual direct blitter callers implement different policies, neither a general safe rectangle clip. One conditionally draws the entire image to both pages using signed16-bit(y+height)<200. The other splits height at a global boundary but does not clamp the split height at0, so a negative split can move the second source pointer backward and increase its draw height. Neither tested wrapper checks x or rejects width0.

## Evidence
4536 passing executions of original caller instructions:504 dual-page cases and4032 split cases. Blitter callsites alone are intercepted; tests record and compare every20-byte argument block,then emulate the far call's return by skipping it. No pixel writes or original blitter execute in this pass. Blitter behavior itself was covered by passes22–24. Combining these results does not establish real caller reachability for all injected coordinates.

Inputs: y=-32768,-1,0,198,199,200,32767; height byte0,1,2,255; width byte0,1,255; fixed x319. Dual-page wrapper uses84 combinations/build. Split adds boundary word0,198,199,255 and transparency31/ffff,for672 combinations/build. Near graphic-record offset9000 contains width,height and far pointer6000:fffc. Using source offsetfffc also checks argument arithmetic across16-bit boundaries without executing an invalid pixel read. Every case asserts original far return,SP and DS restoration.

Routine discovery comes from exact Ghidra12.2 instruction patterns plus two direct references to the known blitter entry,not assumed identical addresses. Per-build entries,boundary global,complete wrapper instruction bytes and EXE SHA256 are in evidence/blit_callers.json. V1.9 dual-page wrapper1d25:0306,split wrapper1d25:036a,boundary wordDS:454c. Earlier DOS1.0 uses1cdc:0302/0366 and boundaryDS:43a4.

## Supported models
Treat all additions/subtractions as16-bit wrap and comparisons as signed where specified. W,H are unsigned record bytes, P is its far buffer pointer.

### Dual-page wrapper
Arguments:x wordSP+4,y wordSP+6,recordOffset wordSP+8. If signed16(y+H)>=200,return without either blit. Otherwise call the blitter twice,first page0 thenpage1,both opaqueffff,full drawW x H,source-column strideH,original sourceP. It does not partially reduce height at the bottom edge. Equality200 rejects both calls.

Examples: y198,H1 draws both; y199,H1 rejects both. Width0 or height0 can still be forwarded when the sum passes. Positive y32767 plus nonzero H may wrap negative and pass. Those calls are observed argument contracts; this pass does not execute the huge/zero blits or assert valid game inputs.

### Split-boundary wrapper
Arguments:x wordSP+4,y wordSP+6,recordOffset wordSP+8,transparency wordSP+10. Let n=min(signed16(boundary-y+1),H). If n>0,drawW x n at(x,y),page0,sourceP,strideH,caller transparency. If H>n,drawW x (H-n) at(x,y+n),page0,source offset(P+n) mod65536 with unchanged source segment,strideH,opaqueffff. Both calls retain original W/H as source-width/stride words.

| boundary,y,H | n | Forwarded split behavior |
|---|---|---|
| 198,198,2 | 1 | Two1-row draws,source offsetsfffc thenfffd |
| 198,199,2 | 0 | Only full2-row opaque draw at original pointer/y |
| 198,200,2 | -1 | Only3-row opaque draw at y199,source offsetfffb |

There is no n=max(n,0) in the original path. x319,width255 is forwarded unchanged whenever a draw is selected. Width0 is likewise forwarded. Height0 can produce no draw in ordinary split cases,or a positive second draw if n is negative. These rules do not validate the full pixel region; upstream setup/preconditions remain unknown.

## Classification and confidence
Confirmed/High for original instruction flow,exact blitter arguments,edge arithmetic and return contracts under interception. Inferred/Medium: these wrappers' broader UI purpose; analytical dual/split labels are not recovered source names. Unknown: real runtime coordinate/boundary ranges,which caller paths guarantee valid dimensions,other direct/indirect blitter callers,actual final pixels for malformed inputs,VGA/DAC and whole-game parity. Supplied1.8/1.9 remain one identical image.

## Ghidra/artifact scope
Analysis uses preserved Ghidra12.2 instruction exports and original reconstructed EXEs. No project metadata or executable bytes are modified in this pass; no function-count/decompiler-completion increase is claimed. Other blitter callers (BSF layout,transitions,and additional graphics wrappers) are not asserted to share these guards.

## Reproduce and next step
`/usr/bin/python3 scripts/verify_blit_callers.py` with Unicorn. Archive includes exact EXEs,pass7 specs,Ghidra instruction exports and pass23 target/page metadata. Next trace writers and reachable range of the split-boundary global and callers of these two wrappers,then test one valid full caller-to-blitter path. The current results establish local contracts,not universal clipping safety.
