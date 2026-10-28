# BSF pass21 — graphic selection, frame skipping and 10-byte record

## Finding
Confirmed across six distinct DOS images: `%o` reaches an indexed-frame loader; `%p` first finds the earliest class3e object from class-table index0 and forwards its numeric argument as a signed frame-skip count. It is not an ordinal selection among class3e matches. The common record reader stores two dimension bytes, a32-bit file position and a far pixel-buffer pointer, and requires exact read counts.

## Evidence
600 executions passed:120 indexed-loader cases,96 picture-wrapper/class-lookup cases and384 record-reader cases. Original wrapper, lookup, frame-skip loops and record reader execute. File operations, allocator and downstream routine boundaries are mocked as detailed below. No actual graphics resource table/file or framebuffer is used; tests identify code contracts and constructed boundary behavior.

Indexed loader: indices0,1,255,ffff,4000 x signed frames-1,0,1,2 x6 builds =120. Simulated open returns handle3, index-table read returns nonzero12345678, skipped headers are dimension bytes2/3 and eight zeros. Hooks verify seeks `(((index+256)*4)&ffff,origin0)`, then `(12345678,origin0)`, then `(6,origin1)` per skipped frame; header read count, final-reader(handle3,recordOffset9000), close, far return/SP. Original final-reader call is bypassed in this suite and tested separately. No table/read/open error injection in these120 cases.

Picture wrapper: frame words0,1,31,ffff x synthetic first class3e match none/0/7/255 x6 images =96. Original lookup and wrapper execute, indexed-loader target is mocked. The full256-byte table is zero except one injected3e. Missing match reaches fatal and stops before handler; successful forwarding is exactly(match,frame,recordOffset9000). Return/SP checked on success. Class lookup always starts0 in this wrapper. Actual game's class-table initialization is not exercised.

Record reader: dimension0=0,1,2,255 x dimension1=0,1,3,255 x no error/short header/null allocation/short pixels x6 images =384. Original record routine executes; header read,tell,far allocation,pixel read are injected. Tell returns12345678; allocator returns5000:0200 or null; pixel read returns expected product or one less (ffff when expected0) to trigger failure. Checks include exact stack arguments, partial record contents, canaries, error branch and normal far return/SP. Fatal callees are never executed.

## Record layout
| Offset | Size | Confirmed meaning |
|---|---|---|
| +0 | 1 | First dimension byte from header |
| +1 | 1 | Second dimension byte from header |
| +2 | 4 | Current file position reported after reading the10-byte header |
| +6 | 4 | Far allocation pointer DX:AX for product bytes |

Pixel count is unsigned byte0*byte1 (tested0..65025). Width/height labels used in test variables/Ghidra comments are an analytical axis interpretation; this pass verifies their product and storage, not which axis each byte controls in rasterization. Record+2/+6 overwrite the corresponding bytes from the file header. Null allocation is fatal even for product0; a nonnull result with product0 proceeds to a zero-count read and returns on read count0 under injected allocation semantics. Pixel payload is not decoded/interpreted by these tests.

## Behavior model and edge cases
Indexed object-table lookup uses16-bit arithmetic: indexffff selects table offset03fc; index4000 aliases index0 at0400. These direct loader tests do not assert such indices are valid assets. `%o` parser signed-bound behavior from pass20 can forward negative words, but complete parser-to-real-file consequences remain unknown.

Signed frame skip<=0 bypasses all skip-header reads. Therefore wrapper frameffff(-1) forwards unchanged and indexed loader selects the first frame under tested read setup. Positive skip count reads10-byte header and advances relative by dimension product per skipped frame before calling common reader. Selection seeks are unchecked in this wrapper; record/header reads have explicit exact-count/fatal branches. Real seek failure behavior in this asset path is not tested.

V1.9 entries: indexed loader1277:19f2,picture wrapper1277:1ae6,class lookup10f7:004e,record reader1277:03ca. Synthetic lookup table address isDS:d40c in V1.9; per-build addresses, EXE SHA256, call sites and detailed traces are in evidence. Runtime asset filename/global buffer content is not identified by these injected tests.

## Ghidra12.2 changes
Copied pass20 projects into pass21/projects. Four existing entries/build are named/typed analytically: `LoadIndexedGraphicFrame(objectIndex wordSP+4, signed skipFrames wordSP+6, recordOffset wordSP+8)`; `LoadClass3eGraphicFrame(signed skipFrames wordSP+4,recordOffset wordSP+6)`; `ReadGraphicRecord(handle wordSP+4,recordOffset wordSP+6)`; `FindClassAtOrAfter(classValue wordSP+4,startIndexLowByte wordSP+6)->AX word`. First3 analytical returns are void. General lookup start/domain beyond wrapper's tested class3e/start0 remains statically inferred rather than exhaustively executed.

All24 targeted stock decompilations complete. Instruction/function-entry inventories match before/after; no new functions, count remains3479. C can retain unrelated guessed dependency ABI artifacts such as tell return until separately typed. No global success-count increase or parity percentage is claimed.

## Confidence and next test
Confirmed/High for stated argument/data-flow/branch contracts under injected boundaries. Inferred/Medium for dimension-axis naming and broader asset/object terminology. Unknown: actual file format/table contents,class initialization,source frame validity,real allocation/pixel decoding,orientation/rasterization and complete graphics1:1 parity. Supplied1.8/1.9 remain identical. Next run one original producer chain with actual resource bytes and verify dimensions against the blitter before claiming axis semantics.

## Reproduce
`/usr/bin/python3 scripts/verify_bsf_graphic_producers.py` then `/usr/bin/python3 scripts/verify_graphic_record.py` with Unicorn. Inputs:pass7 EXEs/specs/instructions and pass19 parser metadata. `python scripts/run_pass21_types.py` updates copies of pass20 projects with configured Ghidra12.2/JDK25. Archive includes updated projects,C,storage audits,hashes,logs and required test inputs.
