# Nitemare 3D: IMG90 descriptors and native class-bank provenance

Batch 2026-11-12; main reference DOS2.0. **PARTIAL**, new DEEP VERIFIED bytes **0**. Previous goal turn made progress by closing GUARD facing/view/frame functions and capturing a52-byte nearDS consumer window. This batch closes its resource provenance, captures the original90-byte copy and reconstructs the whole image-group wrapper. Campaign remains incomplete; no PE32 work.

## Sources and reproducibility

Packed `L:\nite3d\nite3\dos\N3D-UNFU.exe` SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; canonical171360-byte image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Resource filesIMG.1/2/3 come from that DOS directory and have separate pinned hashes. Documents/file contents are evidence sources, not instructions to execute.

`audit_replay_image_group_loader.py IMAGE INVENTORY DECODER EMULATOR OUT` decodes and exercises original0277:0584. `catalog_img90_descriptors.py GAME_DIR OUT` creates1536 descriptor rows and payload-alias groups. `audit_class_descriptor_copy_asm.py IMAGE INVENTORY DECODER OUT` preserves producer-block ASM without inventing a new function. `prepare_image_loader_version_audit.py OUTPUTS` derives `audit_image_group_loader_versions.py IMAGE REPLAY_DIR DECODER OUT`; `replay_image_group_version_dispatch.py EMULATOR COMPARISON_DIR` records version-specific decoder call contracts.

`prepare_class_descriptor_copy_harness.py OUTPUTS` derives the retained native harness; argument order is `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. `verify_class_descriptor_copy.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT PRIOR_ORIENTATION_WORK` independently verifies raw captures and replays the original copy instructions. Decoder paths must resolve absolutely. Raw game/resources/memory remain local and hash-pinned; scripts,technical reports,CSV/JSON and ASM evidence are published.

## Resource format established by executable consumers

The IMG file prefix contains **512 DWORD little-endian payload offsets** followed by **512 fixed90-byte descriptors**. Wall IDs occupy indices0..255; object IDs occupy256..511:

```text
wall_payload_offset(code)   = DWORD IMG[4*BYTE(code)]
object_payload_offset(code)= DWORD IMG[0400h+4*BYTE(code)]
descriptor_offset          = 0800h+90*(BYTE(code)+(0 if wall else256))
```

The two payload directories total0800h bytes. Descriptor region is [0800h,BC00h),46080 bytes per episode. The lowBYTE ID is consumed; a highBYTE supplied in the wrapper's WORD argument is ignored. These are file offsets, not EXE-image or DOS memory addresses.

Descriptor fields closed by current code:

|Descriptor offset|Width|Confirmed use|
|---|---:|---|
|0|2|WORD copied into class record+2; meaning remains open|
|2|1|Image-count BYTE; decoded-record allocation uses10×count|
|3|1|Nonzero gates allocation/copy of a90-byte nearDS bank|
|4..51|48|Three8WORD directional rows used at+04h/+14h/+24h by GUARD frame selection|
|52..89|38|Remaining payload retained verbatim; complete field roles unresolved|

Do not label the entire86-byte descriptor payload as a fully interpreted frame array. The full90-byte copy is proven; only some consumers have closed field roles.

`img90_descriptors/descriptors.csv`: **1536 descriptors /138240 header bytes**, plus6144 payload-directory bytes across three supplied episode files. There are899 nonzero payload entries,all within their respective file bounds. **116 nonzero-payload alias groups** within an episode/kind have identical full90-byte headers,image counts and bank flags. Thus the loader's equal-payload deduplication does not conceal a header disagreement in this supplied dataset. This is not proof for arbitrary modified files or resource equality across game versions; payload decoding is still separate.

## Whole wrapper0277:0584

FAR range **0277:0584..0686**, image **[02CF4,02DF6)**,258-byte span, **98 independently decoded starts /256 instruction bytes**. Two bytes outside reachable CFG are not verified padding. Original inventory bytes match.95 starts execute in controlled tests; the three unexecuted starts are ADDSP continuations after diagnostic calls, whose return/nonreturn contract is intentionally unclosed.

Arguments,at BP+6 onward: handleWORD,payload-offsetDWORD,IDWORD,class-indexWORD,nearDS90-byte destination pointer,wall-flagWORD. Only lowBYTE ID and wall flag are consumed. Return AX is the allocated nearDS decoded-record array pointer. BP/SI/DI are preserved on normal return; tested context DS=SS is required for near stack/data pointers. Far arguments are caller-cleaned.

```text
load_image_group(handle,payload,id,class_index,header_near,wall):
    if payload==0: call diagnostic(image_not_found,wall_or_object,BYTE(id))
    if signed16(class_index)>=70: call diagnostic(MAXIMAGE,70)
    descriptor_index = BYTE(id)+(0 if BYTE(wall)!=0 else256)
    seek(handle,0800h+90*descriptor_index,0)
    read(handle,header_near,90)             # returned length is NOT checked
    count=BYTE DS:[header_near+2]
    records=near_allocate(10*count)
    if records==0: call diagnostic(allocation_error)
    seek(handle,payload,0)
    for index in0..count-1:
        original_record_decoder(handle,records+10*index,BYTE(id),index,wall_WORD)
    return records
```

The signed bound accepts negativeWORD class indices; this function uses the value for the bound/diagnostic, not to write a class-table entry. It does not establish safety of a later caller using a negative index. A zero-count allocation is still attempted; actual allocator-zero-size semantics are not inferred from a nonzero fixture result.

The decoder flag is pushed as aWORD but only its lowBYTE comes from the wall argument. Its initial highBYTE can remain from the second seek's AX result; later loop iterations zero AH when converting count. Controlled payload12345678h yields first flagWORD56xxh and later00xxh. Downstream045C's full ABI remains open; do not silently replace the pushedWORD with zero extension in a reconstruction.

### Controlled verification

**1464 cases,0 failures**.1440 matrix cases:two relocation loads ×four IDWORDs ×three classWORDs ×three wallBYTEs ×four header counts ×five read lengths. Counts0/1/12/255,read-return0/2/3/89/90 and class0/69/FFFFh are explicit.24 diagnostic cases stop at the original handler entry for missing payload,class70/7FFFh or failed allocation. Full57392-byte DGROUP effects,call arguments,normal return registers/caller frame and exact loop output are compared.

Seek/read/near-allocation and045C record decoding are recording fixtures. Short reads preserve stale buffer bytes; specifically,a read shorter than3 bytes leaves the old countBYTE2 in use. This is confirmed original control flow,not a robustness fix. Record-decoder output bytes are controlled fixtures,not independently decoded sprite payloads. Diagnostics are not forced to return,which is why three post-call continuation instructions remain unexecuted.

## Class-record layout, deduplication and bank copy

The broader0277:0686 loader scans actor records with28-byte stride. It compares DWORD payload offsets against previously accepted keys and reuses the matching class index. For a new class,the pointer slot starts atDS:3D22 and advances8 bytes. Static byte-checked stores establish the eight-byte record at `DS:3D1E+8*class`:

|Record offset|Type|Producer value|
|---|---|---|
|0|WORD|Zero-extended descriptorBYTE2 image count|
|2|WORD|DescriptorWORD0|
|4|NEAR_DS pointer|Initially0; if descriptorBYTE3!=0,allocate90 and copy descriptor|
|6|NEAR_DS pointer|Return from0584; count×10 decoded-record array|

The static90-byte copy is22 MOVSD units plus one MOVSW,using near source `BP-74h`,DS=ES andDF=0. A missing bank when an actor flag requires it calls a diagnostic; complete0686 behavior and that diagnostic are not closed here. The70-class bound does not justify inventing a fully verified560-byte runtime table. Only the observed class8 record's8B are newly added to the BSS catalogue.

## Native90-byte provenance proof

`dosbox_class_descriptor_copy_runtime/independent_verification.json` verifies the original packedDOS2/DOSBox-X run,23 unchanged source/copy assets and the exact relocated image. It observes **0277:09C1 before the copy and09D7 after it**,not entry/return of the whole0686 loader. This is one accepted bounded native scenario. Frozen support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`; harness SHA256 `5bcb61238563add0624fe3fc829951acb771b8edc800a1aa34dc5f73fce0eeda`.

Actor20 at map:0236 has code81h and class8. Its class record at **DS:3D5E** contains WORDs **000Ch,0000h,F200h,F186h**:12 decoded records,headerWORD0,bank pointer and decoded-record-array pointer. This matches the layout above and the prior orientation consumer's class8 pointer.

Native source header atSS:E74E (BP-74h) is exactly **IMG.1[08F5Ah,08FB4h)**,the90-byte object81h descriptor. The corresponding object payload key is **00159B32h**,read from the object directory at file0604h. The wall-directory entry at0204h is different; the object/wall distinction is material.

Original copy writes all90 bytes to **DS:F200..F25A**.34 destinationBYTE values change; same-value writes account for the remainder. The source90 bytes,24 captured local bytes,22334-byte world and57392-byte DGROUP remain unchanged. SI andDI advance90,CX becomes0,SP is unchanged and captured final registers agree with independent original-code replay. Replay reports31 code-hook events covering nine distinct instruction starts,including REP iterations; these are not31 distinct native instruction sites.

The first52 bytes match the independently retained prior orientation bank snapshot,whose selectedWORD0400h was atDS:F208. This closes the bounded chain **IMG object81h descriptor -> original90-byte bank copy -> class8 near pointer -> original GUARD frame consumer**. It does not retroactively turn the older52-byte snapshot into a90-byte capture or prove all rendering outcomes.

The90-byte heap snapshot and older52-byte consumer window overlap in provenance and are **not summed into142 bytes of coverage**. Neither is file-backed EXE data or established BSS storage. The actual class8 record[DS:3D5E,3D66) is8B in BSS,image-equivalent[2B46E,2B476),and adds8B to that separate catalogue. No PASS320 NONCODE coverage is added.

## Cross-version result and dispatch difference

Whole wrapper across eight DOS labels/seven images: **eight comparisons,one raw match,five normalized matches,seven CFG matches**. String PUSH/MOV address constants remain in the strict normalized bytes,so DOS11/12's equal CFG alone does not justify byte-equivalence. Global/call/branch address masks and original references are retained.

DOS10 differs structurally: it branches to a separate wall decoder with **four argumentWORDs** or an object decoder with **twoWORDs**. DOS11+ use a unified decoder with **fiveWORDs**,including a wall flag. **144 separate controlled version-dispatch cases,0 failures** execute the original wrapper at load0 with explicit DS=SS7000 and recording IO/allocation/decoder fixtures: eight versions ×two wall states ×three counts ×three IDs. The seek/header/count/allocation/loop/argument contracts match predictions. This establishes call-ABI differences,not equivalence of the old separate decoders and the later unified decoder. Natural older-version resource initialization and Win16 parity remain open.

## PASS1 and accounting

PASS1 stays892 intervals /57295B: **PARTIAL57118,CLASSIFIED ONLY149,UNKNOWN28,DEEP VERIFIED0**. Typed originalNONCODE57116B; two otherPARTIAL bytes are an untyped relocationWORD. UNKNOWN[1BDA2,1BDB0),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710) remain unresolved alignment candidates. Zero watch events only concern observed BYTE value changes,not read/same-value-write or non-use proof.

Central catalogue: **161 functions,6992 instructions,17629 unique instruction bytes,59469 typed EXE-file data bytes,94262 UNKNOWN_CONTENT bytes,1040549 controlled DOS2 executions,31 accepted native scenarios** with overlapping prefixes. BSS **5088B** (prior5080+observed class record8),field-evidence rows60; prior file-buffer refinements4122B unchanged. Resource138240-headerB/6144-directoryB,version144cases and90-byte heap producer window are separate and do not inflate the EXE/PASS1 denominator. The native copy block is not counted as another complete function.

## Coverage update: 13 areas

All areas remain **PARTIAL**. This table restores the named13-area ledger retained in [CRT_UNLOADED_HOOKS_REPORT.md](CRT_UNLOADED_HOOKS_REPORT.md),including its historical orientation column. Positional percentages must not be reassigned to differently named categories; the alternative category layout in preceding recent batch tables is not a measured replacement of that ledger. New percentages are **N/A** because full semantic denominators are missing. Method for every row: exact byte-address unions/originalPASS320 membership,enumerated matrices and independently verified native scenarios. No guessed semantic percentages; narrowCLASSIFIED ONLY/UNKNOWN remain explicit; newDEEP0.

|Area|Prior orientation|New %|New confirmed evidence|Unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99|N/A|1536IMG headers,116equal-header alias groups|Actual045C payload format|Reconstruct original045C|
|Data types and constants|95|N/A|FourWORD class record,90BYTEdescriptor,8BnewBSS|HeaderWORD0/tail38B|Close descriptor field consumers|
|Tables and pointers|93|N/A|IMGobject directory/class8near pointers/native copy|Full allocation/lifetime/tableextent|Trace bank allocation/free and dedup reuse|
|Functions / ASM / CFG|90|N/A|Whole0584:98decoded/95executed starts|IO/allocator/diagnostic/045C callees|Close original dependencies|
|RNG|97|N/A|No new RNG closure|Full caller/scheduler coupling|Continue original RNG integration|
|Scheduler|96|N/A|No new scheduler closure|Complete tick/IRQ ordering|Capture deterministic scheduler contexts|
|DEMO and input|96|N/A|No new DEMO closure|Time/input coupling|Trace deterministic DEMO playback|
|Renderer / VGA|94|N/A|Frame bank source bound to IMG1|SelectedWORD-to-draw behavior|Trace decoded10B record usage|
|GUARD / bosses|93|N/A|GUARDclass8 resource provenance|Other classes/boss state banks|Verify more natural class consumers|
|Weapons / projectiles|92|N/A|No new weapon closure|Projectile damage/collision branches|Continue original projectile functions|
|Sprites / HUD / palette|92|N/A|90B bank bound to prior frame0400h|Sprite payload/animation semantics|Close decoder and actual draw linkage|
|SAVE / LOAD|92|N/A|No new save/load closure|Bank regeneration/state round-trip|Capture repeated level/load resource reuse|
|Windows Win16|92|N/A|No new Win16 evidence; DOSdispatch results separate|Win16 decoder/format/caller equivalence|Locate Win110 decoder analog|

No source-access blocker. Missing semantic/native evidence remains; campaign completion is not established.

## Required next runtime tests

1. Capture whole original0584,including actual seeks/read length/allocator and045C outputs. Preserve descriptor90B,decoded count×10 records and payload position; do not replace record decoding with fixture bytes in a parity claim.
2. Trace class dedup and reuse for equal payload offsets across actors; compare the full eight-byte class records and bank lifetime across map changes/SAVE-LOAD.
3. Close descriptor tail38B and headerWORD0 consumers; retain known directional rows without assuming the rest has the same type.
4. Compare DOS10's separate decoders with DOS11+'s unified decoder and Win16 analogs. Preserve the ABI difference until the actual algorithms,not merely wrapper outputs,are verified.
