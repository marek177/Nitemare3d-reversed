# Nitemare3D: cyclic object cache and first native scaled-sprite pixel parity

2026-11-12. DOS2.0 reference. **PARTIAL**,new DEEP VERIFIED0B. Previous batch profiled all57295PASS320bytes and closed the CRT clock dependency. This batch deepens the existing512B FAR-vector classification,closes0768:04D8 and follows an actual IMG/XMS image through the original scaled-sprite renderer into all four native VGA planes. One draw is verified,not full renderer/gameplay closure. No PE32 work.

## Sources and reproduction

Packed DOS2 `L:\nite3d\nite3\dos\N3D-UNFU.exe`,SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Actual IMG1/2/3,original instruction inventories and1670relocations are pinned separately. Documents/reports provide evidence,not executable instructions.

`audit_replay_object_cache.py IMAGE INVENTORY DECODER EMULATOR OUT` produces whole-function ASM/CFG/execution coverage and1400controlled cases. `audit_object_cache_count_prefix.py IMAGE INVENTORY DECODER EMULATOR OUT` executes only the original count-calculation prefix and exports allocation witnesses. `audit_object_cache_asset_capacity.py GAME_DIR RAW_RECORD_CSV OUT` rechecks actual object header/pixel bytes against the prior pinned catalog.

`prepare_object_cache_native.py OUTPUTS` derives a cache-only capture. `prepare_object_cache_draw_native.py OUTPUTS` extends it through the actual subsequent sprite draw;invoke runtime_watch_object_cache_draw.py with `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. `verify_object_cache_draw_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT` independently verifies cache transfer,original-code replay,mathematical pixels and native VGA planes. Decoder/emulator paths resolve absolutely. Cache-only preliminary capture is not an additional accepted scenario;the stronger combined capture is counted once.

`prepare_object_cache_evidence.py OUTPUTS` emits field/BSS/refinement CSVs and the DOS counterpart audit. `audit_object_cache_versions.py IMAGE REPLAY_DIR DECODER OUT`; `audit_object_cache_flush_versions.py DECODER EMULATOR OUT`. No original game asset or executable is modified. Native process completed and terminated.

## PASS1: concrete refinement of the existing512B vector

Original image[1BE70,1C070),512B,was already PARTIAL as128FAR16 allocation pointers. The selector WORD DS2560 is an actual relocation of segment1BE7;the adjacent0200..0210scratch region is the already typed XMS move descriptor. New consumer04D8 reads one pointer from table[index*4],not a separate sprite resource directory. Native count62,index0;all first62entries are nonnull,all remaining66entries zero. The512B table remains identical across the call. Only the selected target is directly exercised;other61nonnull targets are not described as independently dereferenced/validated here. Zero unused capacity is not padding.

Native DS0C9C,image[283AC,283AE),already typed WORD,changes0->1. The new runtime refinement covers these2B plus the existing512B vector:514already typed NONCODE bytes,**zero new typed-byte coverage**. New separate BSS observations8B:DS3504WORD count62,DS3CB4WORD probe257KiB,andDS:E012DWORD eviction counter0(native unchanged,controlled increment/wrap verified). No allocated cache/record/source memory is counted as file bytes or BSS. The nearDS recordF4DA and FAR slot4F97:E04E are heap observations outside the original interval map.

Original PASS320 map remains892intervals/57295B:PARTIAL57118,CLASSIFIED ONLY149,UNKNOWN28,DEEP0,SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. Prior frozen52snapshot/14session endpoint profiles remain unchanged and are not silently expanded by this new scenario.

## New whole function and corrected ABI

0768:04D8..0580,end exclusive,image[07B58,07C00):62starts,167instructionB in168Bspan. All starts independently decode,match canonical/inventory bytes and execute in the controlled matrix. One gap byte is outside entryCFG and is not globally proven padding. Original0350XMS-reader and07FEmove-wrapper are reused,not counted again. Allocation0024 remains a larger unclosed lifecycle routine;its selected witnesses/prefix do not become a whole-function claim.

04D8 is FAR,takes one nearDS record pointer,caller cleanup,preservesBP/SI/DI/DS/SS. It stores a FAR pixel pointer at record+6. **DX:AX is not a FAR-pointer return contract.** Native success returnsDX0,AXE050 while the stored pointer is4F97:E050. File-fixture tests deliberately returnDX6A6A and confirm it survives,while the stored FAR pointer remains correct. The existing caller0201:072C ignores that register pair and passes the queue record to0156:05DE,which obtains the source from record+6. Wall-cache0402 explicitly setsDX=ES;the two helpers must not share an inferred return ABI.

```text
slot = FAR_vector[WORD_index]          // no local index/capacity validation
index = WORD(index+1)
if signed16(index) >= signed16(count): index=0
if slot.owner_near != 0:
    DWORD DS:[slot.owner_near+6] = 0
    eviction_DWORD++ modulo2^32
record = near_argument
area = unsignedBYTE(record.width)*unsignedBYTE(record.height)
if signed32(record.tag_or_filepos)>0:
    file_reader(FAR(slot+2), record.filepos, area)
else:
    XMS_reader(FAR(slot+2), neg32(record.tag), area)
slot.owner_near = record
record.buffer_FAR = FAR(slot+2)
```

Owner is a nearDS WORD at slot+0,pixel storage begins+2. It invalidates a previous record's buffer pointer but does not free the shared slot payload. No LRU timestamp is used. Under a fixed positive count and valid initial index,the increment/wrap cycles the active prefix;the helper itself does not prove initialization,immutability of count or safety after lifecycle changes. Zero tag follows the XMS branch,as in0402.

File request length is exact area. XMS0350 rounds length to ceil(area/1024)*1024. On managerAX0/BL7Fh,original0350does not take its signed-negative diagnostic branch and04D8still publishes the slot;onBL80h it reaches the diagnostic before publishing the new owner/pointer. Diagnostic handlers are stopped at entry in tests;their return/nonreturn behavior is not assumed. These are controlled manager outcomes,not newly observed native errors.

## Allocation-count prefix and real asset bounds

Original00CE..011E prefix computes signed-truncated `(probe_KiB-70)*1024/3074`,caps signed results above128,and diagnoses count<1. **2048prefix cases**=two loads×every0..1023KiB input,with fullDGROUP and diagnostic arguments checked. These are not2048whole initializer/allocation lifecycles. Witness instructions show each object-slot allocation requests0C02h=3074B,then initializes ownerWORD0. Thus intended pixel capacity is3072B after the owner. Native probe snapshot257KiB gives floor(187*1024/3074)=62,matching count/table prefix. Probe snapshot is not a statement of current free RAM or all allocation sizes observed at their call PCs.

Actual IMG1/2/3 recheck inspects **1383catalog object records**. Header and pixelSHA are compared with real files;all have nonzero area,max logical2961B,max rounded3072B,so all inspected object records fit the intended payload for both transfer paths. Catalog rows can alias physical assets;counts are not file-byte union or distinct visual-image count.

Separate conditional capacity discrepancy:the indexer's signed area comparison accepts high-bit products such as255x255(area65025,signed-511). If such a synthetic record reaches04D8,it has no independent payload-size check:the arguments imply65025B file read or65536B rounded XMS transfer into a nominal3072B payload. No supplied catalog record has this shape;this is not a native corruption reproduction or a claim about every allocator/caller. Synthetic_capacity_conditions.csv distinguishes arithmetic deductions from tested actual assets. Existing IMAGE_RECORD_PIPELINE_REPORT.md retains the original indexer edge-case evidence.

## Controlled whole-cache execution

**1400calls,zero failures**:two loads,counts1/2/5/128,unique first/last indices,dimensions0x0/1x1/16x24/48x64/64x48,four tag/file values,old owner absent/present,three manager outcomes only on XMS paths. File cases do not repeat unused manager variants. Zero area is synthetic;actual assets above are nonzero.

Original04D8/0350/07FEexecute;external file reader/XMSmanager are fixtures. Full57392B DGROUP,all128synthetic3074B slots,the entire512B vector,move descriptor,record pointers,cyclic index,counter carry/wrap,return frame and preserved registers are compared. Synthetic buffers deliberately have sufficient3072B payload for tested dimensions. Old-owner invalidation is executed,but native combined case below has no eviction. 1400whole calls+2048prefix calls add3448to the DOS2controlled count;32cross-version caller cases remain separate.

## Native cache fill and actual source

Accepted combined session retains23unchanged source/copy asset pairs and exact relocated runtime image SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`. Frozen harness SHA256 `f4b7a9b43f5fa03960c3bb6abbb232d06eec23f4e8264e8071c706e229541b3c`.

RecordF4DA before:`1e140010f6ff00000000`=30x20,tagFFF61000h,null buffer. Slot0 is4F97:E04E,owner0. Request1024B,sourcehandle1,offset9F000h(651264),destinationhandle0,FAR4F97:E050. Direct post-manager0815 showsAX1. Full1024B destination after manager equals destination after04D8return. Record becomes`1e140010f6ff50e0974f`;owner becomesF4DA,index0->1,counter stays0. All512table bytes and fullDGROUP except index lowBYTE are unchanged. Caller returns to0201:0749 withDX0,AXE050,preserved registers/frame.

Logical600B prefix equals actual IMG.1 object25h directory-selected first record:payload1348424,pixels1348434..1349034. SHA256 `786323b7128164155c5c69e3495b85570ddd1c7bc217a7518e69ef7363d066c3`. Identical600B also exists in other episodes;content equality alone is not unique episode identity. Native object's captured prefix byte0 is25h. Rounded trailing424B are retained/compared as transfer bytes but are not interpreted as pixels or proven initialized padding.

Original cache re-execution with captured data/request and the native manager result matches all captured registers,frame,DGROUP/vector/record. Its108instruction events comprise107original instructions and one external manager fixture RETF;that fixture is not counted as original code. No native eviction/global heap-lifetime parity claim.

## First native scaled-sprite draw: independent pixel equality

The same session continues directly into original0156:05DE. Queue51EE points to recordF4DA and object prefix25h/flag05h. Object flag bit10h is clear,so depth comparison applies. Source30x20 is exactly the600B just loaded from XMS. Queue rectangle(x1,x2,y1,y2)=(82,96,86,95),clip=(8,311,4,155),depth1529,pageA400. This draw is inside all clip bounds;it does not exercise clipping branches. Scale step=(20<<16)/10=00020000h. Source-width termination stops after15columns despite the initial+2column formula.

Verifier executes the whole original renderer from captured registers/fullDS/source/object input. It observes byte stores and sequencer OUTs and builds four planes from actual pre-draw data. An independent arithmetic loop selects source bytes at `source_column*20+source_row`,uses unsigned depth<=1529,skips byte1Fh,and calculates planar address/bit from target X/Y. **Both models exactly match all4x65536=262144native plane bytes after return.**

67CPU pixel stores;native plane changes20/15/16/16bytes,total67. Original renderer execution1691instructions/143unique starts;all captured return registers,frame and full57392B DGROUP also match. Native queue remains unchanged inside renderer;the caller's later done-flag write is outside this endpoint. Replay/mathematical port sequence has16events(index selection plus15masks),with native final sequencer index2/map_mask01matching. Native intermediate OUT sequence was not independently trapped and is not claimed as a direct native port trace.

Captured VGA configuration supports the simple observational model:write-mode0,unchained,bitmaskFF,no enabled set/reset,data rotation/raster-op0. Read-map selector and GC index are restored before execution after plane readback. Read latches are not claimed restored;full-bitmask writes and the actual plane equality bound the claim. This is **one back-buffer sprite draw**,not a presented/complete frame,physical-GPU parity,all clipping/depth domains or full palette/renderer closure. No screenshot is substituted for byte evidence.

## DOS10 discrepancy: caller architecture differs

Object-cache helper comparison maps DOS11/12/15/17/18/19/20:seven normalized/CFG matches,one raw match(DOS2self). DOS10 has no match for that anchored body;this alone is not global absence proof.

The discrepancy is investigated through original pending-flush callers. DOS10's0200:071A..073C directly draws each pending slot and has **no resident-null cache-fetch gate**. DOS11+ wrappers have the gate and call the mapped cyclic helper before drawing when record+6is zero. DOS10's separate raw object loader0273:039C..042E allocates/loads and leaves its FAR pointer in record+6. These exact bodies explain why forcing the later helper mapping onto DOS10 is wrong;they do not prove every object-cache behavior elsewhere absent.

**32separate cross-version controlled cases**,eight labels×pending0/FF×resident0/nonzero,execute original caller bodies with fetch/draw fixtures. DOS10 draws even the synthetic null-resident state;later wrappers fetch then draw. Natural DOS10 null-resident draw is not asserted. Original producer/group-dispatch evidence retains DOS10's separate two-WORD object-loader ABI.18/19 share one image. No Win16 parity or native DOS10 execution is added.

## Coverage update: 13 areas

Central bounded catalog173functions,7740starts,19532unique codeB,59469typed file-dataB,UNKNOWN_CONTENT92359(not historical reclassification). DOS2controlled calls1061849,native accepted sessions36(overlapping prefixes). New renderer is an already cataloged function,not counted again. BSS5158B,field-role rows94;runtime refinements18records/4636already typed NONCODE bytes. Original NONCODE map/status/DEEP unchanged;new semantic percentages remainN/A without complete denominators.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|Actual1383object header/pixel records fit payload|Other formats/lifecycle gaps|Uncovered map/asset consumers|
|Data types and constants|95%|N/A;514already typedB refined|Vector/cursor native roles and8separateBSSB|149classified/28unknown unchanged|Target new remaining-byte paths|
|Tables and pointers|93%|N/A;128capacity/62nonnull prefix|Source slot/record pointer chain,notDXAXreturn|All targets/lifetime/free path open|Native eviction and reset/LOAD|
|Functions/ASM/CFG|90%|N/A;62newstarts/167B|Whole04D8,all starts exercised|Whole0024allocator modes not closed|Close initialization/free/reset CFG|
|RNG|97%|N/A,semantic denominator absent|No RNG fact added|Seed/DEMO linkage open|Actual RNG writer trace|
|Scheduler|96%|N/A;one linked cache/draw call|Pending flush caller order confirmed|Whole loop/timing remains broader|Trace repeated frames and flags|
|DEMO/input|96%|N/A,semantic denominator absent|No DEMO fact added|Deterministic inputs/playback open|Original DEMO branches|
|Renderer/VGA|94%|N/A;262144nativeB/one draw|Original/model/math planes agree,67stores|Clipped/multiple draws/presentation open|Native clipped/depth/bypass variants|
|GUARD/bosses|93%|N/A,semantic denominator absent|No AI behavior inferred from sprite|Boss/state gaps remain|Uncovered AI branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No damage behavior inferred|Projectile/collision gaps remain|Uncovered projectile transitions|
|Sprites/HUD/palette|92%|N/A;one actual30x20 source|IMG->XMS->record->native planar pixels|Other sprites/HUD/palette domains open|Additional natural source/scale cases|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Cache pointers distinguished from persistence|Restore/invalidation not exercised|Actual save/load cache lifecycle|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 proof|Windows renderer/backend differs|Map exact Win16 sprite consumer|

All13areas remainPARTIAL. 7DOShelper mappings and32caller cases are bounded evidence,not global parity. Campaign remains active.

## Required next runtime tests

Native old-owner eviction,cyclic wrap and count changes after reset/LOAD;first/last pointer lifetime and actual allocation/free calls;clipped top/left/right/bottom draws,depth rejection/equality,bypass and non-integer scales using the same byte-level before/after method. Verify display flip/presentation separately. Continue remaining177byte read/write paths with calibrated instrumentation. Test malformed dimension conditions only in controlled models unless specifically needed;no supplied-asset failure has been found. Win16,AI/projectiles,DEMO andSAVE/LOAD remain separate closure work.
