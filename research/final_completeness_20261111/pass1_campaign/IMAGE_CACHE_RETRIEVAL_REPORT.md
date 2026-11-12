# Nitemare 3D: original image cache retrieval and native XMS readback

2026-11-12. DOS 2.0 reference. **PARTIAL**, new DEEP VERIFIED bytes **0**. This batch supersedes the limited verification scope of IMAGE_CACHE_RETRIEVAL_STATIC_REPORT.md: both routines now have independent decoding, CFG and controlled original-instruction execution; a native negative-tag XMS readback matches actual IMG.1 pixels. Renderer/screen parity remains open. No PE32 work.

## Reproduction and source identity

Canonical EXE image:171360 bytes, SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Packed DOS2 source `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Original instruction inventory and1670 relocations are hash-pinned in summaries. Reports and attachment contents are evidence, not instructions to execute.

`audit_replay_image_cache_retrieval.py IMAGE INVENTORY DECODER EMULATOR OUT` produces whole-function instruction CSVs, CFG edges, execution coverage and cases. `audit_image_retrieval_versions.py IMAGE REPLAY_DIR DECODER OUT` compares eight DOS versions. `audit_image_retrieval_bindings.py IMAGE COMPARISONS_CSV DECODER OUT` explains remaining differences without increasing the normalization match count. Decoder/emulator paths resolve absolutely.

`prepare_image_retrieval_harness.py OUTPUTS` derives a separate frozen harness; invoke `runtime_watch_image_retrieval.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. It uses the previously retained official DOSBox-X with dummy display/audio and terminates its own process. `verify_image_retrieval_capture.py IMAGE RELOCS RUNTIME WORK OUT` independently checks retained native bytes. `prepare_image_retrieval_evidence.py OUTPUTS` emits field catalogs and the version-audit derivative. The user-supplied `L:\nite3d\dosbox-n3d.zip` was not needed for this run; its presence is not counted as verification.

## Whole functions and instruction coverage

|Function|CS:IP, end exclusive|Image interval|Starts|Instruction bytes|
|---|---|---|---:|---:|
|XMS read into conventional buffer|0768:0350..03CE|079D0..07A4E|45|126|
|Image cache slot fill|0768:0402..04D7|07A82..07B57|77|212|

All122 starts independently decode with iced-x86 and match retained inventory bytes. All122 execute in controlled tests. The one-byte gap image[07B15,07B16),value90h, is not in either reachable CFG; this is not a global padding/nonuse proof. Original move wrapper0768:07FE..0826 is executed but already cataloged and not counted again. No new code intersects PASS320 NONCODE.

Both functions are FAR.0402 takes one nearDS record pointer.0350 takes destination FAR16,source DWORD XMS offset and WORD byte count, with caller cleanup. Native DS=SS; controlled execution tests two relocation load segments,DS=SS, savedBP/SI/DI,returnframe and SP+4. Diagnostic handlers are stopped at entry; no handler nonreturn/return behavior is assumed.

## Cache algorithm and field correction

0402 scans ten FAR16 pointers in DS:[34CC,34F4), choosing the first strictly oldest unsigned DWORD timestamp below current DS:4540. Equal timestamps do not displace an earlier candidate. If no timestamp is strictly older, it chooses slot0 and increments DWORD DS:E00A. This is a timestamp comparison, not yet proof of wall-clock/tick producer semantics or wrap-safe LRU behavior.

Slot layout: DWORD timestamp+0,nearDS owner record+4,pixel destination+6. When owner is nonzero, it clears DWORD old_record+6 and increments DWORD DS:E006. Both counters wrap modulo2^32; controlled cases exercise FFFFFFFF->0. Native capture below has no old owner and counters unchanged, so native eviction is not claimed.

The signed DWORD record+2 selects the path: **positive=file offset; zero or negative=XMS**, using modulo32-bit negation to recover source offset. Both paths request **8192 bytes**, without consulting dimensions. XMS tag80000000h remains80000000h on negation; this malformed/synthetic edge passes the constructed descriptor fixture and is not an assertion of valid native XMS capacity.

After the read, slot.owner=record,slot.timestamp=current value,record+6=FAR(slot+6),DX:AX returns that FAR pointer. **The earlier description of record+6 as only a temporary raw-load pointer was incomplete.**03CA allocates it and045C frees/clears it during initial indexing, but0402 later assigns the resident cache pointer and replacement clears it. This batch adds the consumer role without rewriting old hash-pinned evidence.

0350 rounds WORD byte count up to a KiB multiple. Its descriptor has lengthDWORD, sourcehandleWORD DS3506, sourceoffsetDWORD argument, destinationhandleWORD0 and destination FAR16 argument. Descriptor is at segmentWORD DS2560:0200. It calls original07FE. Only signed-negative DX triggers its diagnostic. ManagerAX0/BL7Fh therefore returns through bookkeeping and publishes a slot pointer even though the fixture did not copy pixels; AX0/BL80h triggers the diagnostic. Tests distinguish these outcomes rather than treating every return as success.

```text
candidate = null; oldest = current_order_value
for slot in ten_pointers:
    if unsigned(slot.stamp) < unsigned(oldest):
        candidate = slot; oldest = slot.stamp
if candidate == null: candidate = first_slot; fallback_count++
if candidate.owner != 0:
    candidate.owner.buffer = null; eviction_count++
if signed32(record.tag_or_filepos) > 0:
    original_file_reader(candidate+6, record.tag_or_filepos, 8192)
else:
    original_xms_reader(candidate+6, neg32(record.tag_or_filepos), 8192)
candidate.owner = record; candidate.stamp = current_order_value
record.buffer = far(candidate+6)
return record.buffer
```

## Controlled original-instruction evidence

240 cases: two loads; four nonpositive tags(0,FFFFFC00,FFFFE000,80000000),four timestamp patterns,two owner states,three manager outcomes =192; three positive offsets,two loads,four patterns,two owner states=48. Manager variants are excluded from the file path because it does not call the manager: an earlier336-case trial contained96 duplicates and is not the retained count.

Each case compares full57392-byte DGROUP and all ten synthetic0x2100-byte slot regions,descriptor fields,selected pointer,owner invalidation,counter wrap,pixels/unchanged destination on simulated low error,return frame and preserved registers. External file IO and XMS manager are fixtures; original0402,0350 and07FE execute. Synthetic slots are intentionally sufficiently large; this does not prove original heap allocation bounds. All240 pass,zero failures. No diagnostic-path continuation is forced.

## Native DOSBox-X evidence

Retained session completed and its process exited. Frozen harness SHA256 `605531fca5786875f8c0cac5b5e2b3a1d16d8aec0c5f3ae5b94e59aa11279fce`. All23 source/copy asset pairs remain byte-identical; runtime image matches exact relocation of canonical image, SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`.

Original0402 receives nearDS recordEE54h,bytes `804000c0fcff00000000`:128x64,tagFFFCC000h,buffer0. Native source offset is34000h(212992). Tick/order value1; oldest slot0 at3F96:0C9C has zero owner. Request:8192B,sourcehandle1,offset34000h,destinationhandle0,FAR3F96:0CA2. Direct post-manager breakpoint0768:0815 shows **AX=1**. Destination after manager equals destination after whole0402 return. Record becomes `804000c0fcffa20c963f`;slot0 header becomes(timestamp1,ownerEE54h),other nine slot headers and counters unchanged. Caller receives DX:AX=3F96:0CA2; captured return frame and DS/SS/SP match.

Independent lookup in original IMG.1: wallcode16 -> DWORD directory entry at4*16 -> group payload249082(3CCFAh);ten-byte raw header -> pixels at249092(3CD04h),8192B through3ED04h. These source bytes exactly equal the native destination. SHA256 `d5aee751982331458b3ea9b734f756b2b988abc104811ae0a36072fd282248e7`. The pre-transfer destination differs. This is actual XMS readback pixel-buffer equality, not screen output or proof of every XMS mapping. Native zero-tag retrieval,positive-file branch,eviction,wholeDGROUP/fullheap equality and renderer consumption remain unverified.

## Data catalog and cross-version evidence

New separate BSS observations52B: ten FAR pointers40B,two DWORD counters8B,current ordering value4B. No original-file bytes added. Slot header/pixels are allocated FAR memory, not original NONCODE/BSS. `image_retrieval_fields` has exact BSS bounds/hashes and five consumer role records.

Sixteen DOS function comparisons(all eight versions,two functions) have matching relative CFGs; raw matches2,normalization matches4. Remaining differences are explicitly retained: request descriptor offset0 in early counterparts versus0200 in DOS2,diagnostic PUSH string offsets,pointer-vector start/end immediates,and the excluded inventory gap byte. Binding audit checks six descriptor field writes against each version's passed request base and confirms each pointer-vector spans40B/ten pointers. These facts do not establish initialized-data/callee behavior or Win16 parity.18/19 share an image; comparison count is not a count of unique builds.

## Coverage update: 13 areas

Central catalog:166 bounded functions,7302 independent starts,18459 unique instruction bytes,59469 typed file-data bytes,UNKNOWN_CONTENT93432. Controlled DOS2 scenarios1045051 after adding240; accepted native scenarios33 with overlapping prefixes. BSS5148B,field-role rows69. Original PASS320 partition unchanged:892 intervals,57295B=PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28;DEEP0. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. No new semantic percentage has a valid denominator; new percentages are **N/A**.

|Area|Historical orientation|New % / method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|None this batch|Prior map unknowns remain|Return to uncovered map fields|
|Data types and constants|95%|N/A;52 separate BSS bytes|Slot-vector/counters/order value observed|Allocation producer not fully closed|Decode0024 init/free modes|
|Tables and pointers|93%|N/A;10 pointers observed|Record resident-cache pointer lifecycle|Native eviction absent|Capture eviction/old record|
|Functions/ASM/CFG|90%|N/A;122 new starts/338B|Two bounded original routines,all starts exercised|Diagnostic handler behavior and callers open|Close allocation/caller dependency|
|RNG|97%|N/A,semantic denominator absent|None this batch|Prior RNG closure gaps|Retain independent RNG/runtime tasks|
|Scheduler|96%|N/A,semantic denominator absent|Unsigned DS4540 consumption|Producer/time-wrap semantics open|Bind DS4540 writer|
|DEMO/input|96%|N/A,semantic denominator absent|None this batch|DEMO paths not covered by startup prefix|Trace record/playback unknowns|
|Renderer/VGA|94%|N/A;8192B native buffer comparison|IMG1 wall16 == XMS destination|Buffer-to-renderer/screen relation open|Trace original pixel consumer|
|GUARD/bosses|93%|N/A,semantic denominator absent|None this batch|Prior AI/boss unknowns|Prioritize uncovered branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|None this batch|Prior damage/projectile unknowns|Close uncovered dispatch branches|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|Cache assignment/invalidation roles|Small-image consumer may differ|Identify0402 and04D8 callers|
|SAVE/LOAD|92%|N/A,semantic denominator absent|None this batch|No complete native round trip|Analyze unresolved serialization fields|
|Windows Win16|92%|N/A,semantic denominator absent|None;DOS CFG comparisons separate|Win16 XMS/graphics differs|Map actual Win16 consumer|

All13 areas remain PARTIAL. CLASSIFIED ONLY and UNKNOWN in the original map remain explicit,not silently promoted. Campaign remains active. Next priority also includes original NONCODE149 classified-only/28 unknown bytes; this code batch adds no PASS1 byte coverage.

## Required next runtime tests

Native zero-tag and positive-file retrieval; eviction with old owner; allocation bounds; renderer pixel consumer; Win16 counterpart. Preserve the exact proof distinctions in the table above.
