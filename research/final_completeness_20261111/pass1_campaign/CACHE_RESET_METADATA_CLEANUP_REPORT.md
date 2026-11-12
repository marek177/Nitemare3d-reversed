# Nitemare3D: cache reset and metadata cleanup with native-RAM-seeded replay

2026-11-12. DOS2.0 reference. **PARTIAL**,new DEEP VERIFIED0B. Previous batch verified one natural cache-to-sprite draw. This batch reconstructs the reset and level-cleanup paths and re-executes them from an actual paused640KiB RAM snapshot. **Reset/cleanup are controlled original-code replays,not natural DOSBox reset invocations.** The repeated native prefix supplies data only and adds0accepted native scenarios. Campaign remains incomplete;no PE32 work.

## Source identity and reproduction

Packed DOS2 `L:\nite3d\nite3\dos\N3D-UNFU.exe`,SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`;canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Original inventories,1670relocations,assets,models,harnesses and captures are pinned. Prior reports/documents are evidence,not executable instructions.

`audit_replay_cache_reset.py IMAGE INVENTORY DECODER EMULATOR OUT` independently decodes both bounded functions and runs238synthetic cases. `cache_reset_model.py` is a separate byte-level model of the observed reset/mark operations. `audit_cache_cleanup_boundaries.py IMAGE REPLAY_DIR OUT` records exact instruction unions and gap bytes.

`prepare_cache_reset_seed.py OUTPUTS` derives runtime_watch_cache_reset_seed.py. Invoke it with `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. It follows the already verified first-sprite prefix,then dumps physical00000..9FFFF while paused. `verify_cache_reset_seed_replay.py IMAGE RELOCS RUNTIME WORK EMULATOR REPLAY_OUT` independently verifies the data capture and executes two original-code paths with synthetic call frames. Decoder/emulator paths resolve absolutely. No game EXE,host state or original asset is changed.

`prepare_cache_cleanup_fields.py OUTPUTS IMAGE INVENTORY DECODER` creates field/caller catalogs. `audit_cache_cleanup_versions.py IMAGE DECODER EMULATOR OUT` maps16DOS counterparts and runs32separate caller cases with explicit dependency fixtures. All raw RAM/asset binaries remain local;published scripts/manifests reproduce their verification.

## Exact function boundaries and honest execution coverage

|Function|CS:IP,end exclusive|Image interval|Decoded starts|Instruction bytes|
|---|---|---|---:|---:|
|Cache lifecycle dispatch|0768:0024..0293|076A4..07913|219|619|
|Level resource cleanup|0D29:080E..08A9|0DA9E..0DB39|57|155|

Two new bounded ranges276starts/774codeB. All starts are independently decoded and byte-matched,**not all semantically executed**:synthetic reset/invalid-mode/cleanup cases execute119new starts(62dispatch/reset and all57cleanup). The remaining157dispatch starts belong to initialization/shutdown and related continuations;they remain explicitly unexecuted by this batch. Existing near-heap mark helper11EE:3CAE..3CCF is reused,not counted again.

The623B lifecycle span has four1-byte gaps,outside retained entryCFG instruction union:images076BF,07825,07861,07885,each90h. They are not globally proven padding or non-executable. Cleanup's155B span is entirely covered. CSVs retain every instruction,edge,execution flag and gap. No instruction byte intersects original PASS320 NONCODE.

## Lifecycle modes and unresolved scope

The lifecycle function is FAR,cdecl WORD mode at BP+6,with savedBP/SI/DI. Dispatch tests the wholeWORD:0initialization,1shutdown,2reset;other values return through the early exit. Tests include3,0100h,FFFFh;lowBYTE alone is not the mode contract.

**Mode0,static reconstruction only here:**allocates ten wall and four sound slots with2006h-byte requests,probes allocation capacity,computes/clamps object count and requests0C02h-byte object slots;initializes their headers. Existing count-prefix evidence remains separate. It conditionally detects/queries/allocates/locks XMS,limits its configured capacity,sets flags and has diagnostic/warning/failure branches. Whole initialization/error-handler/allocator outcomes are not executed or closed by this batch.

**Mode1,static reconstruction only here:**tests saved initialized flagDS350C,then calls unlock/release helpers0844/07E4 with the handle. It does not directly clear the flag/handle/cursor afterward. This is not a claim about all callee side effects or successful natural shutdown;those contracts remain open. The gate is350C,not merely the current enabledBYTE3CCE.

**Mode2,executed:**invalidates image record buffers,clears cache slot headers and sets XMS used cursor350A to0. It does not call an allocator,XMS manager or OS. It retains the cyclic index0C9C,count3504,handle3506,feature flags and FAR pointer vectors for the tested states. PreservedDS in tested calls depends on normal DS=SS:object processing temporarily switches DS to the relocated cache-table segment and restores it fromSS. SS is unchanged;ES and working registers are not a general preserved contract. Mode2 ends withAX0;that is not generalized to all modes or to level-cleanup returnAX.

Important address distinction:mode2 loads **code-relocated immediate segment1BE7**,rather than rereading mutable DS2560 for its object table. Normal captured state makes the two agree. Four additional synthetic cases deliberately change DS2560 and confirm reset/cleanup still use the fixed relocated table. The independent model uses that fixed binding;other helper paths that load DS2560 retain their own contracts. No changed-selector natural state is asserted.

## Exact reset operations

```text
for each of10wall slot pointers atDS34CC:
    if WORD slot+4!=0: DWORD DS:[owner+6]=0
    WORD slot+4=0; DWORD slot+0=0
for each active object slot in fixed relocated1BE7 vector:
    if WORD slot+0!=0: DWORD SS:[owner+6]=0
    WORD slot+0=0
DS=SS after the positive object loop
for each of4sound slot pointers atDS34F4:
    WORD slot+4=0; DWORD slot+0=0
WORD DS350A=0
```

Object-loop count comparison is signed;count<=0 skips the object loop while still resetting wall/sound headers. The sound marker is not interpreted as an image-record pointer:there is no corresponding record+6clear in that loop. Timestamp/owner headers are reset;pixel payloads are not cleared by these operations. XMS used cursor0 does not prove erased/released XMS backing bytes. Retained pointer vectors do not prove every target's global lifetime.

## Whole level cleanup and near-heap meaning

Level cleanup is FAR,no arguments,savedBP/SI/DI and normalDS=SS. It first calls mode2,then marks WORD near pointers atDS4316+8*i for signed count6272(wall metadata),andDS3D24+8*i for count6274(object metadata). It scans count6270actors through world selectorDS256C,28Bstride,reading classBYTE at world offset0A+28*i. Class bank pointer isDS3D22+8*class. Nonzero bank is passed to the mark helper and then zeroed,so repeated actors of one class do not mark that bank again.

```text
reset_cache(mode2)
for wall metadata slot: mark_near(WORD class_record8+6)
for object metadata slot: mark_near(WORD class_record8+6)
for actor:
    bank = object_class_record8[actor.class].bank_near_at_plus4
    if bank!=0:
        mark_near(bank)
        class_record8.bank_near_at_plus4=0
```

The existing mark helper returns without writes when unsigned lower-bound20E8>=pointer. Otherwise it ORs bit0 into the byte at(pointer-2)and lowers20EA if needed. This is a block-tag/minimum update,**not physical deallocation,coalescing or a DOS free call**. Metadata-array pointers at class_record8+6 remain unchanged after marking. They are different fields from image_record10+6,which reset invalidates. Record counts and cache index also remain unchanged;future overwrite/reload/lifetime must be checked separately.

Static caller evidence:0D29:095A testsBYTE DS1C9C;when zero,PUSHCS+NEAR CALL at0964/0965 invokes cleanup080E. The exact flag writer/lifecycle meaning is not inferred from that test alone. Startup0476:012D/012F passes mode0;0476:01C4/01C6 passes mode1. Caller contexts are exported,not treated as new natural executions.

## Synthetic tests:238cases,zero failures

Two loads;reset counts0/1/2/5/62/128/-1,owner patternsnone/distinct/shared,cursors0/7;cleanup layouts empty,wall metadata,object/duplicate-class metadata and combined;invalidWORD modes;four changed-selector cases. Shared-owner cases deliberately cause repeated zero stores,not only first-value changes. Inputs outside ordinary initialized count/index relations are synthetic,not natural-game findings.

Original reset entry,whole cleanup and original mark helper execute without stubs or OS calls. Each case compares the entire flat1MiB fixture RAM except72B of synthetic call/scratch stack,plus the exact ordered nonstack writes including unchanged-value stores. All expected data targets are checked disjoint from that excluded stack interval. Return frame,SP+4,BP/SI/DI/DS/SS are checked. This flat fixture memory is not a proof of actual DOS allocation capacity. Mode0/1 remain unexecuted;full lifecycle is not closed.

## Paused native640KiB seed and controlled original-code results

The data-only session repeats the first-sprite prefix and captures physical00000..9FFFF. All23source/copy assets remain identical;initial unpacked image matches exact relocations,SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`. Frozen harness SHA256 `02034e6dc4c74fd72190744484c247cea0646ee239d506ed5a10f9640f3bc440`.

Verifier reconstructs20actualMEMDUMPBIN parts in exact physical order,with no RUN between parts. Seed matches the captured post-draw fullDS64/DGROUP. Lifecycle,cleanup and mark-helper code in liveRAM equals original relocated instruction bytes. The DOSBox process terminated after capture. **No native reset call or injected DOSBox function invocation occurs.**

Two fresh controlled replays start from that seed with explicit synthetic frames. No callee is replaced;no interrupt/OS/manager call executes. Each compares **655288RAMbytes**,excluding only72B synthetic control stack,and exact ordered nonstack stores. All modeled targets are outside the exclusion. The seed contains62object slots,222actors,34wall metadata slots,28object metadata slots,cyclic index1,XMS handle1 and used1074KiB.

|Controlled path|Original instruction events|Nonstack stores|Changed byte positions|Invalidated resident refs|Mark calls|
|---|---:|---:|---:|---:|---:|
|Mode2 reset|745|96|36|5|0|
|Whole level cleanup|5175|166|109|5|66|

Four live wall references and one live object reference are invalidated. Both paths retain cursor1/count62/handle1/flags1 and set used1074->0. Whole cleanup marks34wall+28object metadata pointers and four unique class banks(classes8,14,15,22),while scanning222actors. All66marked pointers in this seed are nonzero and unique. Class8bankF200 becomes0,but its metadata pointerF186 remains;the other bank rows are retained in class_bank_cleanup.csv. These are controlled outcomes,not natural post-cleanup snapshots.

All conventional cache pixel regions remain byte-identical:10*8192wall+4*8192sound+62*3072object=**305152B**,checked disjoint. Both paths have81store events whose values already equal the initial seed bytes;RAM differences alone would have missed them. This does not imply native BPLM reports those writes. Source XMS storage is not read back after reset;no erased-XMS claim.

## Calibrated references to the original NONCODE table

For each RAM-seeded path,the verifier also executes a restricted-read pass. It must reproduce the exact baseline instruction sequence,write order and RAM results. Positive control reads the active248B prefix(62FAR entries)of original512B vector[1BE70,1C070). The unused264B capacity is not read by these particular loops. Exact CS:IP/addresses/sizes are exported in restricted_reads.csv. Remaining149CLASSIFIED ONLY+28UNKNOWN=177B produce0read events **in these two controlled paths only**. This is not global nonuse or direct native read tracing. Restricted ranges avoid the previously reproduced RETF-stack memory-hook issue.

New separate BSS6B records signed loop counts6270/6272/6274 with actual seed values222/34/28. Fourteen field-role refinements distinguish image buffers,class bank/metadata pointers,headers,cursor and counts. No new original-file bytes or PASS320 statuses are added. Frozen prior endpoint profiles remain unchanged.

## Cross-version evidence and DOS10 release difference

All16function counterparts are mapped using version-specific prologues and cleanup's mode2callee linkage. DOS10 lifecycle starts0739:0028,has136starts/384codeB;its cleanup0CDC:07DE..08AA has71starts/204B. Later lifecycle/cleanup bodies have matching relativeCFGs:14matches across the seven later labels,two raw/two normalized matches(DOS2self). Different indexed/literal bindings are not silently normalized into behavioral equivalence.18/19 share one image.

DOS10 cleanup has an extra per-image loop:for each object class,it passes each image_record10+6DWORD to a FAR pixel-release dependency before marking the class metadata near block. Later DOS callers omit this per-image release and use the cyclic-cache design analyzed previously. This aligns with DOS10 raw object loading retaining per-image allocation and its direct-draw flush path. It is bounded evidence for these functions,not global cache absence.

**32separate caller-only cases**,eight labels x empty/zero-image/one-image/three-image layouts,execute original cleanup callers with cache-reset/near-mark/FAR-release fixtures. Exact argument widths,order,bank-pointer deduplication and fullDGROUP are checked. DOS10three-image/two-class layout makes six FAR release calls;later versions make none. Dependency bodies/natural DOS10 cleanup/Win16 are not executed. These32cases are separate from the centralDOS2count.

## Coverage update: 13 areas

Central bounded catalog175functions,8016independent starts,20306codeB,59469typed file-dataB,UNKNOWN_CONTENT91585(not historical reclassification). DOS2controlled cases1062089=prior1061849+238synthetic+2RAM-seeded paths. Accepted native sessions remain36;data-only seed adds0. BSS5164B,field-role rows108;runtime buffer refinements remain18records/4636already typedB. Partial decoding/branch execution is not semantic completion.

PASS320 unchanged:892intervals,57295B=PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28,DEEP0. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. New semantic percentages remainN/A because complete denominators are absent.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|222actor/34wall/28object loop counts fromreal seed|Not full map format/lifecycle|Natural populated cleanup/map replacement|
|Data types and constants|95%|N/A;6separateBSSB/14roles|Bank-vs-metadata-vs-image pointer roles|177B still unresolved/only classified|New calibrated read/write paths|
|Tables and pointers|93%|N/A;248activevectorB read|Fixed reset segment,cursor retention,5refs invalidated|Other lifecycle/target validity open|Initialize/reconfigure/reset counts|
|Functions/ASM/CFG|90%|N/A;276decodedstarts/774B|Whole cleanup exercised,mode2/invalid paths|157init/shutdown starts unexecuted here|Mode0/1 full dependency replay|
|RNG|97%|N/A,semantic denominator absent|No RNG behavior inferred|Seed/ordering open|Actual RNG writer/DEMO path|
|Scheduler|96%|N/A,semantic denominator absent|Cleanup call order/invalidation before marks|No natural IRQ/interleaving proof|Native repeated-level transition|
|DEMO/input|96%|N/A,semantic denominator absent|No DEMO/input behavior added|Natural navigation/timing open|Reproduce transition controls|
|Renderer/VGA|94%|N/A;305152payloadB retained|Conventional pixel buffers not cleared bymode2|No new draw/presentation proof|Clipped/depth/scale native cases|
|GUARD/bosses|93%|N/A;222actor traversal|Class bank deduplication across actors|No AI behavior closure|Uncovered AI/state branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No damage behavior inferred|Projectile lifecycle open|Original projectile transitions|
|Sprites/HUD/palette|92%|N/A;4bankptrs cleared|Image cache and descriptor cleanup distinguished|Other sprites/palette domains open|New natural source/scale cases|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Stale metadata pointers retained,bank pointers cleared|Natural SAVE/LOAD not exercised|Trace actual restore/reload ordering|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 proof|Win16 lifetime/backend unknown|Map Win16 equivalent cleanup|

All13areas remainPARTIAL. Mode0/1 and natural reset are explicit open requirements. Campaign active;full goal completion unproven.

## Required next runtime tests

Capture natural populated cleanup after a second level/New-game/LOAD transition;compare direct native stores/RAM with this model and distinguish possible IRQ clock changes. Execute mode0/1 helper outcomes,allocation failures,XMS unlock/release statuses and saved-flag gates. Verify post-reset refill with preserved cursor/count and correct XMS record reconstruction. Continue remaining177B,Win16,clipped renderer,AI/projectiles,DEMO and SAVE/LOAD closure independently.
