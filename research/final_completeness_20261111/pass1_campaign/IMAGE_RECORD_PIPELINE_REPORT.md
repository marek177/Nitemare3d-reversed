# Nitemare 3D: image records, raw pixel loading and XMS tags

Batch2026-11-12. DOS2.0 main reference. **PARTIAL**, new DEEP VERIFIED bytes **0**. Previous goal turn made progress by establishing90-byte IMG descriptor provenance and class-bank copying. This batch closes the previously substituted record routines and connects actual IMG bytes to a native XMS request. The campaign remains incomplete; no PE32 work.

## Sources and reproduction

Packed `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; canonical171360-byte image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. IMG.1/2/3,original instruction inventory and relocation CSV are pinned separately. Attached documents/historical reports are evidence rather than executable instructions.

`audit_replay_image_record_pipeline.py IMAGE INVENTORY DECODER EMULATOR OUT` decodes three whole routines and executes component/edge cases. `catalog_img_raw_records.py GAME_DIR DESCRIPTOR_CSV OUT` follows actual resource streams. `audit_replay_IMG_group_pipeline.py IMAGE INVENTORY DECODER EMULATOR GAME_DIR GROUP_CSV OUT` integrates original0584 with original record/raw/cache/XMS routines for actual groups. `audit_image_record_versions.py IMAGE REPLAY_DIR DECODER OUT` independently maps bounded DOS counterparts.

`prepare_image_record_harness.py OUTPUTS` derives the native harness,whose arguments retain the support order: `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. `verify_image_record_capture.py IMAGE RELOCS RUNTIME WORK OUT` verifies retained records,pixels,requests,counters and earlier matching XMS evidence. Decoder paths must resolve absolutely. Scripts,ASM/CFG,CSV/JSON and reports are published; original assets/raw memory remain local and hash-pinned.

## Functions and corrected terminology

The earlier name `record decoder045C` was provisional. **045C indexes/caches image metadata;03CA reads raw area-sized pixel bytes. These routines do not perform pixel decompression.** Interpretation of the byte order by the actual renderer remains a separate task.

|Function|CS:IP bounds,end exclusive|Image interval|Instructions|Instruction bytes|
|---|---|---|---:|---:|
|Raw record and pixel loader|0277:03CA..045C|02B3A..02BCC|51|146|
|Image-record indexer/cache adaptor|0277:045C..0584|02BCC..02CF4|112|294|
|Negated-XMS-offset tag adaptor|0768:03CE..0402|07A4E..07A82|25|52|

Three new functions,188 decoded starts,492 instruction bytes;182 starts execute in controlled cases. Six unexecuted starts are continuations after diagnostic calls; those handlers are not forced to return. Two bytes inside045C's bounded span are outside reachable CFG and are not proven padding. All instruction bytes match the canonical image/original inventory. Original XMS append0294 and move wrapper07FE are reused,not counted again as new functions. No new instruction byte intersects PASS320 NONCODE.

All three functions are FAR. Raw loader takes handleWORD and nearDS record pointer,preservingBP/SI. Indexer takes handle,near record,IDWORD,image-indexWORD,wall-flagWORD,preservingBP/SI/DI; only the flag's lowBYTE controls branches. Tag adaptor takes a nearDS record and returns status in **AL**,not a guaranteed meaningful WORD in AX. Tests use DS=SS where near stack/data pointers require it. Volatile/allocator/manager effects are not generalized beyond the explicit fixtures/captures.

## Ten-byte runtime record and stream format

|Offset|Width|Confirmed runtime meaning|
|---|---:|---|
|0|1|WidthBYTE|
|1|1|HeightBYTE|
|2|4|Pixel file offset,or negated XMS byte offset **including valid zero**|
|6|4|Temporary FAR16 pixel buffer pointer; freed and cleared by045C|

The file contains a ten-byte header followed by exactly `unsignedBYTE(width)*unsignedBYTE(height)` bytes. The loader copies all ten serialized bytes but overwrites the eight position/pointer bytes; their serialized values are not assumed valid runtime addresses. A group contains the descriptorBYTE2 count of these header/payload pairs.

`img_raw_records/raw_image_records.csv` records **1870 image records in589 unique(ep,kind,payload,count) groups** across supplied IMG.1/2/3. Every parsed record remains within its source file and passes the original dimension checks;none has zero area or area>=8000h. Sum of logical pixel lengths is5176595 bytes. This sum can overlap across groups and is explicitly **not a file-byte union or semantic-coverage percentage**. Directory aliases are retained in group code lists. Headers/file offsets/hashes are evidence for the raw stream,not visible renderer orientation,palette/transparency behavior or Win16 equivalence.

## Original algorithms and finite-width behavior

```text
raw_load(handle,record):
    read_near(handle,record,10)
    if returned_count!=10: diagnostic(...)
    area=unsignedBYTE(record.width)*unsignedBYTE(record.height)
    record.position=tell(handle)
    record.buffer=far_allocate(WORD(area))
    if record.buffer==0: diagnostic(...)
    read_far(handle,record.buffer,WORD(area))
    if returned_count!=area: diagnostic(...)

index_or_cache(handle,record,id,index,wall):
    if global_cache_BYTE3CCE!=0:
        original raw_load(handle,record)
        cached=original tag_XMS(record)
        increment matching wall/object cached/uncached WORD counter
        far_free(record.buffer)
    else:
        read_near(handle,record,10)
        if returned_count!=10: diagnostic(...)
        record.position=tell(handle)
        area=width*height
        seek_relative(handle,sign_extend16(area))
        increment wall/object uncached counter
    record.buffer=0
    if BYTE(wall)!=0:
        if height!=64: diagnostic(...,id,index+1)
        if width not in {64,128}: diagnostic(...,id,index+1)
    else:
        if signed16(width*height)>3072: diagnostic(...,id,index+1)

tag_XMS(record):
    offset=original XMS_append(record.buffer,WORD(width*height))
    if signed16(highWORD(offset))<0: return AL=0
    record.position=-offset modulo2^32
    return AL=1
```

Dimension checks occur after bookkeeping and temporary-buffer release; do not reorder them in a faithful reconstruction. The product is unsigned8×8,but the uncached seek sign-extends its16-bit result and the object-size test uses signedJLE. Synthetic255×255 therefore produces65025,passes the signed object limit,and causes an uncached relative seek of-511. This is verified machine arithmetic in controlled fixtures,not proof of a naturally valid image or actual DOS huge-buffer behavior. The real1870-record dataset has no such high-bit products.

The XMS append routine rounds request length upward to KiB and increments usedKiB. If capacity is rejected,it returnsFFFFFFFFh and the tag adaptor preserves the positive file offset. If capacity is accepted,the external manager result is filtered by the original wrapper's signedDX condition: managerAX=0 with BL<80h can still proceed through append bookkeeping. Tests preserve this behavior and do not treat usedKiB growth as proof that an external transfer succeeded. A fatal diagnostic path is stopped at entry; its hypothetical return behavior remains open.

The position representation is **negated cache offset**,not necessarily a strictly negative number. Offset0 produces tag0;the first native image demonstrates this case. Consumer handling of zero/nonpositive tags must be reconstructed from its own code before claiming complete cache-retrieval parity.

## Controlled execution and integration

`image_record_pipeline_replay`: **728 cases,0 failures**.720 matrix cases cover two relocated loads,two cache flags,ten dimension pairs,three wallBYTE values and six used/limit/manager-result combinations. Eight added cases cover short ten-byte header reads,failed far allocation and short pixel reads. Counters are seededFFFFh to verify16-bit wrap. The original raw loader,indexer,tag adaptor,XMS append and move wrapper execute; external DOS reads/seek/tell,heap allocation/free and the XMS manager are fixtures. Full57392-byte DGROUP,ten-byte record,counters,request descriptors,normal return registers/caller frame and diagnostic argument tuples are checked. Six post-diagnostic continuations are not falsely counted as executed.

`IMG_group_pipeline_replay`: **3534 scenarios,0 failures** =589 actual groups ×two loads ×three modes(file indexing,cache-all,cache enabled with no capacity). For each scenario,the original0584 wrapper calls original045C/03CA/tag/XMS code. The former record-decoder substitution is removed. Actual IMG headers and pixels feed file-service fixtures;near/far allocation requests,logical pixel prefixes,XMS requests,final record arrays,file cursor,counters,usedKiB and fullDGROUP are compared. Each mode/load covers1870 record calls;these internal calls are not added as extra central test scenarios.

Only external DOS/heap/XMS services remain substituted in this integrated test. Rounded XMS source-block padding is not declared initialized or safe from a logical-payload comparison. Neither mode is physical XMS/readback,full malformed-input or renderer-output verification.

## Native full-call trace

`dosbox_image_record_runtime/independent_verification.json` verifies original packedDOS2/DOSBox-X,23 unchanged source/copy assets,the exact relocated image and actual045C entry/caller return. Frozen support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`; harness SHA256 `b2f5824c95dba7091fe4ea45846d371ba487678ca801f68b46eaf35d62dd929e`.

Actual case: **wallID1,image-index0,record nearDS:ECC8,wall argumentBC01h**. The high argumentBYTE is residual caller state;the lowBYTE1 controls classification. Original return is0277:066D inside0584. BP/SI/DI and caller frame are preserved,DS=SS remains2F95h andSP advances4 for RETF.

Five stages are retained:045C entry,03CA return0277:0474,original XMS wrapper0768:07FE entry,XMS-append return0768:03E4 and actual caller return. Observations:

1. IMG.1 wall directory index1 points to fileBC00h. Width128,height64;the raw payload is **IMG.1[BC0Ah,DC0Ah)**,8192 bytes.
2. Loaded record is `80 40 0A BC 00 00 CA 65 9B 8D`:file pixel positionBC0Ah and temporary FAR8D9B:65CA. Captured raw pixels equal both that IMG slice and the captured XMS source bytes exactly. SHA256 `80f788fca6bd8e3ae32997918f6adac74d3a32348a75b1d35f6e107eec480cfa`.
3. Actual move request:length8192,source handle0,sourceFAR8D9B:65CA,destination handle1,byte offset0. UsedKiB changes0->8 under limit2048.
4. At append returnDX:AX=0000:0000. The final record is `80 40 00 00 00 00 00 00 00 00`:tag0 and cleared temporary pointer. Cached-wall counterDS:E010 increases0->1;the other captured counters remain0.

The current trace does not trap the manager-return instruction itself. The independently retained earlier `dosbox_xms_request_runtime` proof verifies the **identical request fields** and wrapper returnAX1/DX0 in a separate run;its entire pinned evidence is rechecked. That is corroborating earlier evidence,not another newly counted scenario and not a claim that the current managerAX was directly captured. Neither run supplies XMS-memory readback or a visible image golden comparison.

The native proof verifies records/pixel source/request/counter stages;it does **not** claim that all CRT/heap memory is unchanged or reproduce opaque allocator internals. The original free call lies on the verified code path and its record pointer is cleared;complete allocation-lifetime behavior remains separate. Watchpoints on28 UNKNOWN bytes remain value-change-only observations,not no-read/same-value-write proof.

## Data catalogue and cross-version limits

Four new record-field evidence rows describe the ten-byte record. Four mutableWORD counters atDS:E00E,E010,E01A,E01C add8B to the BSS catalogue;only cached-wall increment is directly observed natively,while other branches are code/model-confirmed. They are outside the EXE-file/PASS1 denominator. BSS physical bounds and nonoverlap are independently checked.

Version mapping attempts24 function pairs across eight DOS labels/seven images. **22 bounded counterparts are compared:9 raw matches,9 conservative normalized matches,22 CFG matches.** String-address constants remain in normalized bytes,so equal CFG does not imply equal data/callee bindings. The DOS10 unified indexer is not forced onto its already-established separate wall/object functions;DOS10's tag adaptor remains unlocated by the bounded anchor. These **two mappings remain UNKNOWN**,not evidence that functionality is absent. No new initialized-data,Win16 or runtime cross-version parity is asserted.

## PASS1 and accounting

PASS1 stays892 intervals /57295B: **PARTIAL57118,CLASSIFIED ONLY149,UNKNOWN28,DEEP VERIFIED0**. Typed originalNONCODE57116B;two otherPARTIAL bytes are an untyped relocationWORD. UNKNOWN[1BDA2,1BDB0),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710) remain unresolved alignment candidates. No padding/non-use promotion follows from zeros or a negative scan.

Central catalogue now **164 functions,7180 instructions,18121 unique instruction bytes,59469 EXE-file data bytes,93770 UNKNOWN_CONTENT bytes,1044811 controlled DOS2 scenarios,32 accepted native scenarios** with overlapping prefixes. BSS5096B,field-evidence rows64;prior file-buffer refinements4122B unchanged. New492 codeB are outside originalNONCODE. The1870 resource records and5176595 summed logical pixel bytes are separate external-asset evidence,not extra EXE coverage or a semantic percentage.

## Coverage update: 13 areas

The named13-area ledger and historical orientation column are preserved from the preceding corrected report. All areas remain **PARTIAL**;new percentages are **N/A** because complete semantic denominators are missing. Method for every row:exact instruction/data address unions,originalPASS320 membership,enumerated controlled scenarios and independently verified native scenarios. No guessed semantic percentages;CLASSIFIED ONLY/UNKNOWN remain explicit and newDEEP0.

|Area|Prior orientation|New %|New confirmed evidence|Unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99|N/A|1870raw records in589actual groups|Renderer byte ordering/other resource types|Trace raw-buffer renderer consumer|
|Data types and constants|95|N/A|Record10 field roles/counterWORDs/tag0|Other descriptor fields/149classifiedB|Continue actual consumers|
|Tables and pointers|93|N/A|File-position versus negated-XMS tag,temporaryFAR lifetime|Zero-tag retrieval/real heap lifetime|Close cache retrieval helpers|
|Functions / ASM / CFG|90|N/A|3whole functions,182/188executed starts|Six diagnostic continuations/external services|Close original error/allocator contracts|
|RNG|97|N/A|No new RNG closure|Full caller/scheduler coupling|Continue original RNG integration|
|Scheduler|96|N/A|No new scheduler closure|Tick/IRQ ordering|Native deterministic contexts|
|DEMO and input|96|N/A|No new DEMO closure|Playback/time coupling|Trace deterministic DEMO|
|Renderer / VGA|94|N/A|8192native pixel bytes bound to IMG/XMS source|XMS readback and actual draw output|Capture cache read and visible output|
|GUARD / bosses|93|N/A|Actual object groups pass original metadata path in model|Natural other classes/boss behavior|Link object record arrays to sprite draws|
|Weapons / projectiles|92|N/A|No new projectile closure|Damage/collision branches|Continue original projectile functions|
|Sprites / HUD / palette|92|N/A|Original pixel load/index/cache chain|Color/layout/animation/palette parity|Close actual sprite renderer consumer|
|SAVE / LOAD|92|N/A|No new save/load closure|Recreated cache/bank state|Capture repeated load resource reuse|
|Windows Win16|92|N/A|No new Win16 result;DOSmapping limits explicit|Win16 counterpart behavior|Locate Win110 record/cache path|

No source-access blocker. Full campaign completion remains unproven.

## Required next runtime tests

1. Trap cache retrieval for the zero-tag first image and a strictly negative tag;capture descriptor lookup,actual XMS readback buffer and final pixels before renderer use.
2. Capture current manager return status directly for successful/declined requests and compare it with bookkeeping;do not infer transfer success from usedKiB or a cache tag alone.
3. Follow object81h's twelve records from its class near-pointer through animation-base/span selection and actual sprite drawing. Preserve image counts,raw bytes,palette and VGA destination planes.
4. Map DOS10's unmatched cache adaptor and compare its separate indexers to DOS11+'s unified path. Continue28UNKNOWN/149CLASSIFIED ONLY with actual evidence;no PE32 port.
