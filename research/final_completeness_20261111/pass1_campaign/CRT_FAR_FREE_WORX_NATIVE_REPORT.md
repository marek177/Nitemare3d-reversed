# Nitemare3D: FAR free marker, native IBK/WORX ownership and DOS10 cleanup callee

2026-11-12. DOS2.0 reference, PARTIAL; new DEEP VERIFIED0B. Previous goal turn made progress by publishing whole FAR malloc and actual DOS4A growth. This batch closes a previously mocked dependency's byte-level contract: CRT11EE:2052marks allocation metadata, rather than calling DOS to release a block. It also binds the naturally released music buffer to actual SND.DAT bytes and the live WORX bank. Full campaign remains incomplete; no PE32 work.

## Source identity and reproduction

Packed `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`,1670relocations and historical inventory are pinned. Native DOSBox-X executable SHA256 `a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832`;native load0824h,unpacked runtime image SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`.

- `audit_replay_crt_far_free.py IMAGE INVENTORY DECODER EMULATOR OUT`: independent ASM/CFG for2052,1408direct marker cases and960original marker-to-malloc reuse cases. Existing crt_far_malloc_model.py and original malloc/helper bodies are reused unchanged.
- `runtime_watch_crt_far_free.py DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`: natural first nonzero-segment call, exact before/after205Dstore stops, whole function return, frames/CF/DF and two640KiB RAM captures. Frozen harness SHA256 `662c367c86a5e2c81fdd96fb0aacbd19923a020dc4f56b602ca7b659777091a6`.
- `verify_crt_far_free_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR`: independently reassembles physical dump chunks/binds register responses, executes the original whole helper without any dependency fixture, and verifies caller/asset/live-bank data.
- `audit_crt_far_free_versions.py IMAGE DECODER EMULATOR OUT`: maps eight DOS bodies and executes24separate original DOS10cleanup-caller/marker cases with explicit cache-reset/near-mark fixtures.
- `prepare_crt_far_free_fields.py OUTPUTS`: records the already-PARTIAL4B DS17D0pointer and separates external/heap data from EXE coverage.

Original23source assets and copied inputs remain hash-checked/unchanged. Debugger commands are breakpoints,RUN,read-only register queries and dumps; no CPU/RAM injection. Raw EXE/assets/RAM remain local. Documents/reports are evidence, not instructions executed by these tools.

## Exact function, ASM and ABI

New bounded function **11EE:2052..2065**,image[13F32,13F45),10starts/19B. All bytes and the entryCFG are independently decoded and matched to original inventory. No gap byte exists inside this19B range.

```text
push bp
mov  bp,sp
push si
les  si,[ss:bp+6]          // FAR offsetWORD,segmentWORD
mov  cx,es
jcxz return
or   byte es:[si-2],1      // 16-bit effective offset wrap
return:
pop  si
pop  bp
retf
```

FAR cdecl argument consists of offset atBP+6 and segment atBP+8. BP/SI/DS/SS/AX/BX/DX/DI are preserved by this body; ES and CX receive the pointer segment. RETF consumes4return bytes, leaving the four argument bytes for the caller. No Boolean success result in AX is defined; AX is unchanged.

The null guard tests **segmentWORD only**. Segment0 with a nonzero offset skips the tag access, even though the DWORD pointer is numerically nonzero. It still changes volatile ES/CX to0; calling this an entirely side-effect-free no-op would be inaccurate. Nonzero segment with offset0targetsES:FFFE, offset1targetsES:FFFF; the offset subtraction wraps16bits. No ownership,alignment,bounds or valid-tag check exists here.

For a valid heap payload pointer, the preceding WORD is the allocator tag and bit0denotes free. Only the lowBYTE is ORed; its adjacent highBYTE is not written. Repeating a marker call is idempotent in final memory, while still executing the BYTE store. Segment-nonzero OR clears CF and preserves DF; segment-zero skipping preserves incoming flags. Other OR flag details/undefined AF are not treated as an application result contract.

No CALL,INT,heap traversal,DOS free,coalescing,payload erase or caller-pointer clearing occurs in this body. A later allocator scan performs merging/reuse. This differentiates2052from the previously analyzed DOS-free wrapper11EE:2A0A (INT21/AH49) and from near-heap marker11EE:3CAE.

## 2368controlled DOS2cases

1408direct cases:

- All256low tag bytes at a normal pointer, two load bases0824/1000 and DS=SS versus deliberately split SS/DS.
- Offsets0/1/2/3/FFFE/FFFF,segments0/6000/8000/FFF0,selected0/7E/80/FF tag bytes, both load/segment contexts.
- Exact ordered BYTE writes include same-value writes for already odd tags. Full2MiB RAM outside72control-stack bytes, unchanged guards/argument frame,preserved registers,CX/ES,SP+4 and CF/DF behavior are checked.

The arbitrary tag bytes and upper synthetic segment responses are instruction/ABI tests, not proof of valid DOS heap ownership or A20 configuration. Tested pointers do not alias executing code or the control frame; arbitrary corrupt pointer consequences are not closed.

960lifecycle cases execute original2052one or more times, then original2065and its original helpers. Valid seeded heaps contain allocated8/16/24B blocks, all combinations of freeing them, optional duplicate marking, four next-fit cursors and requests0/8/9/16/17/24/48/64. Empty duplicate schedules are excluded. The independent model verifies the entire ordered marker+allocator mutation sequence and final RAM. Only DOS48failure is a fixture when the seeded space cannot satisfy the request; no marker or scan routine is replaced. Tests demonstrate later reuse/coalescing, not coalescing by2052itself.

Existing malloc code/model remain pinned rather than rewritten for the new tests. All10new helper starts execute. Complete start coverage does not establish safety for corrupt/aliasing pointers or turn the function into DEEP VERIFIED semantics.

## Natural exact BYTE writer and whole-helper replay

The original game reaches2052with pointer **3F96:0016**. Its physical tagWORD is[3F974,3F976),payload begins3F976. Captured PC **1A12:205D** (canonical11EE:205D) is the OR instruction; the next captured boundary is1A12:2062,exactly five bytes later. ES/SI,SP and all non-flag working registers match across the instruction. The17B before/after window changes only its central tagBYTE:

```text
allocated tagWORD0C84 -> free tagWORD0C85
lowBYTE84 ->85; highBYTE0C unchanged; sixteen surrounding bytes unchanged
```

This is a directly bounded native writer observation, not a BPLM value-change guess. The complete2052entry-to-return capture then matches an original10instruction,one-store replay with no OS/callee fixture. All captured16bit registers and CF/DF match. All655360native after-RAM bytes equal the replay, including stack; residual count0for this particular call. Separately,the replay agrees with a2MiB independent byte model outside72control-stack bytes. Native RAM above640KiB was not captured and is not included in native parity.

Helper19code bytes and the prior WORX bank-loader37code bytes remain equal to relocated original in the before/after captures. Exact dump origins,part reassembly,register/frame bindings and source hashes are checked. The debugger's paused execution is not an uninterrupted timing proof.

## Real caller, SND bank and retained pointer

Return frame binds the caller to **0C2B:02BBFAR CALL2052**,return02C0. The preceding original instruction is PUSH DWORD DS:[17D0]. Native DS17D0equals the passed pointer and retains it at the helper return. The caller frame has music ID1 and enabledBYTE DS414D=1. This extends the static caller evidence in PASS1_MUSIC_RESOURCE_REPORT.md; it does not capture the caller's subsequent new allocation,read,driver calls or full return.

Native3204B payload is unchanged across the free call and matches exactly **SND.DAT[0003C0,001044)**,SHA256 `13f761cfe691e90555c276f67606ab2d627de6b76018e5fbf764699c582136f9`. SND.DAT record0independently declares WORD length3204/signedDWORD offset960 and its payload begins49 42 4B 1A (`IBK` plus1Ah). The match is unique among the23captured input files; native file-read instructions were not trapped in this capture. This is a byte/source/caller binding, not an invented new bank-format analysis.

The old directory-ID0bank is therefore marked while the current caller is selecting ID1. The old DS17D0pointer remains until later caller code replaces it; the callee accepts its value, not the address of that global. No claim that the rest of the music loader succeeds or that every driver consumer has ended its use follows from this one call.

## Live WORX copy survives the marker

The already typed WORX bank image[18103,18683) contains128x11bytes. The previous bounded loader15BF:5973..5998takes11bytes then skips5from each16B source record, after a4B prefix. Its static/control proof remains in WORX_REGISTER_BANK_REPORT.md.

New native evidence: before freeing the IBK heap buffer, all128live records exactly equal the independent projection

```text
live_record[i] = SND.DAT[960 +4 +16*i : 960 +4 +16*i +11]
```

All1408B remain identical after the free call. Projected live-bank SHA256 `aa7f201844944b95f679270f9aa704cabed8126f31cb0f77ee7ef38319a9ae04`;1181byte positions differ from the canonical EXE's default bank, demonstrating that this is current mutable runtime data rather than merely an unchanged default. The live-bank and source heap ranges are disjoint. WORX_live_bank_records.csv retains each source/destination boundary and11B hash.

This proves a distinct live table matching the bank projection and surviving this free. The actual bank-copy PC/history was not trapped, and no new audible audio/port-output correctness or complete driver ownership claim is made. Five skipped bytes per record and the remaining source bytes are not assigned new semantics here. The1408B bank was already typed,outside original PASS320 NONCODE; no new EXE-data coverage is counted.

## DOS version verification and DOS10cleanup dependency

Eight labels DOS1.0/1.1/1.2/1.5/1.7/1.8/1.9/2.0,seven unique images,contain the exact same19B helper body. Every mapped entry and all10instruction starts are verified against each image/inventory. All eight raw-body/relative-CFG comparisons match. Exact per-version CS:IP/image boundaries and hashes are in function_comparisons.csv;1.8/1.9share the same image.

For DOS1.0,the extra per-image FAR-release dependency in0CDC:07DEcleanup resolves directly to this helper (image13AFE).24separate original caller/marker cases cover empty/zero/one/three-image layouts,even/odd tags and distinct/shared/zero-segment pointers. The actual helper body now executes; its behavior is not guessed from a replacement named far_pixel_release. Ordered calls/stores,full2MiB RAM outside72stackB and frames/registers match expected results. Shared/already-free pointers demonstrate repeated same-value BYTE stores; zero-segment pointers still call the helper but make no tag store.

Cache-reset and near-mark dependencies remain explicit fixtures in these24cases, so they are not full DOS1.0callee/gameplay closure or natural DOS1.0runtime. The bounded difference from later cleanup callers is refined: DOS1.0additionally marks each image-buffer allocation tag. It does not call DOS49or physically erase/release those payloads in this helper. Corresponding record pointers remain unchanged by2052. Later callers omit that per-image path,as previously established; complete lifetime/parity across versions remains open. No Win16 counterpart or behavior is proved here.

## Original NONCODE and data catalogs

DS17D0is image[28EE0,28EE4),4already-PARTIAL bytes,initialDWORD0. The new pointer-field catalog records its native3F96:0016value,callee-by-value use,retention at return and external SND binding. The2B heap tag and3204B payload are runtime heap/external asset data,not new original-file or BSS bytes. Neither the1408B WORX bank nor the4B pointer receives a status promotion.

Adding the new bounded helper changed the central instruction CSV hash. The retry-reference census and its dependent field summaries were regenerated against that input; independent hash checks had correctly rejected the stale dependency. The scanned instruction union/counts remain35813because this helper was already in the historical inventory. Historical published snapshots retain their own hashes; no old report's semantic results are silently recast as new findings.

Original map remains892intervals/57295B,all current boundaries/hashes preserved. Remaining149CLASSIFIED ONLY+28UNKNOWN bytes receive no new nonuse/padding inference from this heap analysis.

## Coverage update: 13 areas

Previous183functions/8123starts/20561codeB/1064251controlled DOS2cases/39native. New184functions/8133starts/20580codeB/1066619controlled cases/40native. Additions: one19B/10start function,2368controlled cases,one verified native free observation.24DOS10caller cases are separate,not added to DOS2count. Native whole-helper replay belongs to native verification,not another central case. Typed file data59469B,BSS5164B,central field-role rows108 unchanged;4existing pointer bytes refined and external3204B/live1408B bindings do not inflate those unions. Campaign UNKNOWN_CONTENT91311is not historical NONCODE reclassification.

PASS320 unchanged:PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28+DEEP VERIFIED0=57295B. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. New semantic percentages N/A because complete per-area denominators are absent. Historical orientation values remain estimates.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new map format behavior|Natural map replacement open|Populated cleanup/map replacement|
|Data types and constants|95%|N/A;4already-PARTIAL pointer bytes|BYTEfree flag,segment-only guard,SND record0binding|177B unresolved/only classified|New actual data consumers|
|Tables and pointers|93%|N/A;128native11B records and4Bpointer|LiveWORX projection survives heap marker;DS17D0retained|Full driver ownership/copy PC untrapped|Capture original bank-copy call/consumers|
|Functions/ASM/CFG|90%|N/A;10newstarts19B/2368cases|Original marker+mallocreuse,all marker starts|Invalid aliasing/PSP/callback domains open|Whole lifetime/callback provenance|
|RNG|97%|N/A,semantic denominator absent|No RNG behavior inferred|DEMO/ordering open|Original RNG/DEMO transitions|
|Scheduler|96%|N/A;one native call/full640KiB equality|Marker has no DOS/callee dependency|Paused timing/other paths open|Natural resource replacement timing|
|DEMO/input|96%|N/A,semantic denominator absent|No input behavior inferred|Playback/input order open|Actual DEMO path|
|Renderer/VGA|94%|N/A;DOS10extra buffer-marker path|Marking distinguished from erasing/releasing payload|No new pixel/clipping parity|Refill/reuse and clipped draws|
|GUARD/bosses|93%|N/A,semantic denominator absent|No new AI behavior|Boss/state paths open|Uncovered original state/attack branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No damage behavior inferred|Projectile transitions open|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A;8DOSbodymatches/24separatecases|DOS10per-image mark has original callee proof|Full cleanup dependencies/asset lifetimes open|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Pointer/tag persistence separated from DOSfree|Actual LOAD/free ordering open|LOAD/populated reset capture|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 proof|Backend free/lifetime counterparts open|Map Win16 equivalent routines|

All13areas remain PARTIAL. Raw body identity proves this bounded helper's code contract under stated memory assumptions,not full heap/game behavioral parity.

## Required next runtime tests

Capture the complete music ID1replacement through new allocation/read/WORX driver calls and caller return,then bind the new buffer to its actual source. Trap original bank-load15BF:5973entry/return if naturally reached to distinguish source/data equality from executed copy history. Trace subsequent allocator reuse and driver consumers before asserting complete ownership closure. Execute natural populated level/New-game/LOAD cleanup/refill and actual shutdown; extend PSP growth/callback bodies separately. Continue remaining177NONCODE consumers,Win16 lifetime parity,clipped renderer,AI/projectiles and RNG/DEMO/SAVE/LOAD. Four postfatal initializer starts remain unexecuted; fatal handlers are not forced to return merely for coverage.
