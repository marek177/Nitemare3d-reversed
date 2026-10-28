# BSF pass22 — real IMG.1 command/load chain and original planar blit

## Finding
Confirmed across six distinct DOS images and their supplied IMG.1 resources: real `%o` commands load raw column-major graphic payloads through original parser/sscanf/indexed loader/record reader/far allocator. Original blitter writes match a plane-mask/address/value oracle for both opaque output and transparent color31. Record byte0 is width and byte1 height, confirmed by the layout argument flow plus original loop/write observations.

## Evidence and scope
402 target executions:134 original load chains and268 original blits. Source indices are every distinct decimal `%o<number>%` found in each actual decoded mode3 BSF resource:23/build for1.0,1.1,1.5,1.7 and shared1.8/1.9;19 for1.2. Mode3 source hashes/metadata come from pass7. IMG.1 is extracted from the same ZIP directory as that build's BSF; exact ZIP paths,size and SHA256 are stored in evidence/real_graphics.json. Five source files are1975616 bytes;1.2 is2244774. All are preserved in the archive for reruns; they are not uploaded as Git tree text.

Original command parser,original sscanf/CRT,original indexed graphic loader,original10-byte record reader and original far allocator all execute in one chain. Only file open/seek/near read/tell/far read/close and DOS INT21 AH48 allocation are simulated. Read hooks serve exact bytes from the supplied IMG.1 with a shared virtual file position. DOS allocation returns segment6000; heap/list globals and failure callback start0. Input command pointer is4000:0200; stack startsf800 with original stack bound checks retained. This is not a real DOS filesystem/process startup test.

Each load asserts record=(width,height,pixel-file-position,6000:0016), exact pixel payload equality to the source file slice, far return/SP, and only one DOS allocation. Total payload loaded79286 bytes across134 chains. Source offset uses the original table contract at1024+index*4; these real selected entries are nonzero. No load failure/malformed real assets are injected in this pass. `%p` class initialization/selection with real class tables is not included.

For each loaded graphic, the original blitter runs twice:transparent wordffff(opaque signed-negative path) and001f(color31 skipped). Position x=index mod4,y=7 exercises all four starting plane alignments across the selected inputs. Actual layout argument flow is reproduced: byte0 supplies draw-column count; byte1 supplies row count and source-column stride. Destination page is controlled segment7000 and pageSelect0. OUT3c4(index2)/3c5(map mask) and memory writes are observed. No renderer function is bypassed in these blit executions.

All138276 observed pixel writes match the independent address/value construction below, including write order, transparency suppression and lower map-mask bits. The destination is ordinary mapped memory; the plane-mask oracle interprets each observed write. This is a direct original blit write-trace check, not a full VGA device,DAC,palette,display timing or final in-game framebuffer test.

## Pixel/layout model
For width W=record[0],height H=record[1], source payload P and column c,row r:

- Source pixel P[c*H+r] (column-major).
- Plane mask1<<((x+c)mod4).
- Destination byte offset(y+r)*80+floor((x+c)/4).
- Emit unless transparency word is nonnegative and equals pixel value; tested nonnegative transparency31 and negativeffff.

Thus byte0 determines horizontal columns and byte1 vertical rows. This closes the axis interpretation left uncertain in pass21 for the tested full-image invocation. Partial width/height,stride variation,clipping,other page selection and border/wrap coordinates remain separate cases.

V1.9 original blitter1156:07de; record reader1277:03ca; object loader1277:19f2; parser1d25:1070. Per-build blitter/record entries are also in the Ghidra audit type specs. The harness extracts the destination-page global independently from each build's blitter instructions (rather than assuming one address for all versions).

## Ghidra12.2 changes
Copied pass21 projects into pass22/projects. Named/typed existing blitter `BlitColumnMajorGraphic`: far source pointerSP+4,then words xSP+8,ySP+10,source-width argumentSP+12,columnStrideSP+14,drawWidthSP+16,drawHeightSP+18,pageSelectSP+20,transparent-index bitsSP+22; analytical returnvoid. Layout passes source width twice; this pass tests full-size shapes and does not assign a broader meaning to the source-width argument. Record-reader comments now distinguish confirmed width/height from prior provisional naming.

All12 targeted stock decompilations complete (blitter+record reader/build). Instruction addresses/bytes and function-entry inventories hash identically before/after. Count stays3479,prior uncertain seeds retained. No global decompiler success-count increase or full parity percentage.

## Confidence and remaining work
Confirmed/High for real-source byte extraction,original successful load chain and tested planar write traces/axis semantics. Simulated file/DOS allocation/device model is explicit. Unknown: actual VGA/DAC/palette and timing,clipping/page variants,real `%p` class-table path,episode IMG.2/3 coverage,full BSF page render and whole-game1:1 parity. Supplied1.8/1.9 still share one executable image.

## Reproduce
`/usr/bin/python3 scripts/verify_bsf_real_graphics.py` with Unicorn. If original inputs/all-nite3d.zip is present it extracts matching IMG.1; otherwise it uses the included pass22/data files. Required EXEs,prior metadata and mode3 resources are archived. `python scripts/run_pass22_types.py` reapplies metadata to copies of pass21 projects using configured Ghidra12.2/JDK25. Updated projects,C,storage audit,hashes and logs included. Next verify partial/clipped blits and real palette/page setup, then full page renderer integration.
