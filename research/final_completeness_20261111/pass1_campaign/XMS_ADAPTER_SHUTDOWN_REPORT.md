# Nitemare3D: original XMS adapter contracts and cache shutdown

2026-11-12. DOS2.0, PARTIAL. Previous cache-cleanup batch was progress: independently reproduced reset/cleanup paths, published verified evidence and retained the explicit mode0/1 gap. This batch closes six bounded adapter bodies and the shutdown caller under controlled external responses. No new native execution, no XMS manager memory-service emulation, no DEEP VERIFIED promotion, no PE32 work.

## Source identity and reproduction

Original packed EXE `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Inventory and1670 relocation entries are hash-pinned in summary.json, together with this script and prior dispatcher execution evidence.

Reproduce: `audit_replay_xms_lifecycle_wrappers.py IMAGE INVENTORY DECODER EMULATOR OUT`, with canonical image, historical N3D-20/instructions.json, work/decoder and work/emulator, OUT=outputs/xms_lifecycle_wrappers_replay. Decoder/emulator paths resolve absolutely. It independently decodes16-bit ASM/CFG and byte-matches the historical inventory before executing original bytes relocated to0824h and1000h. Data/code gaps are exported separately, not classified as padding. Existing audit_replay_cache_reset.py evidence is read without rewriting it.

## Bounded functions and contracts

All entry points are FAR/cdecl; argument-bearing wrappers read WORD BP+6. Actual DS is preserved and must supply the manager pointer at350E:3510; SS supplies call frame. BP/SI/DI/SS and caller stack frame are checked. AX/BX/DX/ES/FLAGS are otherwise volatile unless a contract below specifies a result. The entry blocks are game-side XMS adapters, not execution of the external manager, CRT allocator or WORX driver. Original compiler/library provenance of each instruction is not inferred merely from its prologue.

|Name|0768:IP end exclusive|Image interval|Starts/code bytes|Observed static result|
|---|---|---|---:|---|
|Detect manager|0784..07A9|07E04..07E29|15/36|INT2F AX4300, test AL bit7; absent AX0; present INT2F AX4310, store ES:BX at DS3510:350E, AX1|
|Query capacity|07AA..07C2|07E2A..07E42|11/24|Manager AH08; success AX unchanged, DX0; AX0 failure gives DX=BL<<8|
|Allocate handle|07C2..07E3|07E42..07E63|14/32|AH09, DX=argument; nonzero manager AX => AX=manager DX, DX0; failure AX0, DH=BL while manager DL survives|
|Release handle|07E4..07FE|07E64..07E7E|12/26|AH0A, DX=argument; always returns AX0; DX0 on success, BL<<8 on failure|
|Lock handle|0826..0844|07EA6..07EC4|14/30|AH0C, DX=argument; success DX:AX=manager DX:BX; failure AX0, DX=BL<<8|
|Unlock handle|0844..085E|07EC4..07EDE|12/26|AH0D, DX=argument; success AX remains manager AX, DX0; failure AX0, DX=BL<<8|

Success means the original `OR AX,AX` is nonzero, not exactly AX1. BL is consulted only on the failure branch. An AX0/BL0 fixture can therefore return DX0 despite failure; callers must not reinterpret DX0 alone as universal success. The allocation error's retained DL is a byte-level exception to a uniform error<<8 abstraction. The tests seed manager DX3456h, so failed allocation returns error:56h; the preserved-low-byte dependency is also explicit in ASM. Release's unconditional AX0 differs from unlock's retained successful AX.

Two unvisited gap bytes inside wrapper spans are recorded in span_gaps.csv; their bytes are not asserted globally non-executable. All78 decoded instruction starts/174instruction bytes execute in this batch. Complete entryCFG execution is narrower than proof for every possible external response or interrupt interleaving.

## Controlled test matrix and memory verification

**732cases, zero failures**:12detect cases(two loads, AL0/1/7F/80/81/FF),24query cases(two loads x AX0/1/FFFF x BL0/7F/80/FF),384argument-bearing direct cases(four wrappers x same responses x argument0/1/7FFF/FFFF),and312whole shutdown cases. Query argument duplicates are excluded.

The external manager fixture consists of RETF at6000:0100, with controlled AX/BX/DX responses and no allocation, release or lock memory effects. Only INT2F responses are injected for detection; all adapter and dispatcher instructions are original. Every manager call's AH, inputDX, order and fixture response is exported. All1MiB RAM except72bytes of synthetic control-stack scratch is compared with an independent expected image. Every nonstack store is checked in order. Only successful detection writes two manager-pointer WORDs; its initial1234:5678 pointer differs from the returned6000:0100, ensuring the write assertion is not a same-value coincidence. Absent detection preserves the old pointer.

Synthetic entry frames and return registers are verified. RETF consumes4bytes and leaves the argument on caller stack. Native environment state, XMS service correctness and actual manager error behavior are outside this fixture proof.

## Whole shutdown caller and reconstructed pseudocode

Original0768:0024 mode1 branches to01E2. SavedBYTE DS350C gates shutdown, while current enabledBYTE DS3CCE is not consulted. Tests include saved0/1/80, current0/1, handles0/1/FFFF, success/failure with BL0/80/FF, and one/two successive calls using the same state. Disabled saved0 cases make zero manager calls; nonzero saved cases make unlock then release on each invocation, including when unlock fails.

```text
shutdown_cache():
    if saved_initialized_byte_350C != 0:
        unlock_handle(word_3506)   // original wrapper, return ignored
        release_handle(word_3506)  // still called after unlock failure
    return                         // no direct flag/handle/cursor stores
```

The original caller and these original adapter bodies perform no nonstack stores on shutdown. With a manager fixture that leaves RAM unchanged, the flag, handle and all RAM outside control-stack scratch stay unchanged. The second call therefore repeats both manager requests. This proves caller order/stale-gate behavior under fixtures; it does not demonstrate a natural double-free or manager resource corruption. Manager/private state and actual application shutdown ordering remain unverified.

Fourteen dispatcher starts newly execute relative to the prior mode2/invalid-mode batch. Combined_dispatch_execution.csv retains the union:143of219dispatcher starts remain unexecuted across these two batches, all in mode0-related paths. Previous historical report's157was correct for its earlier scope; it is not silently rewritten.

## Coverage update: 13 areas

Previous catalog175functions/8016starts/20306codeB/1062089controlled DOS2cases. New catalog181functions/8094starts/20480codeB/1062821controlled cases: exact addition6functions/78starts/174B/732cases, dispatcher is reused. Typed EXE data59469B, BSS5164B, field-role rows108, accepted native scenarios36 unchanged. Campaign UNKNOWN_CONTENT91411is not a reclassification of historical NONCODE.

PASS320 remains892intervals/57295B =57118PARTIAL +149CLASSIFIED ONLY +28UNKNOWN +0DEEP VERIFIED; map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. No original NONCODE byte becomes code or receives a new status. Historical orientation percentages below remain historical; new semantic percentages are N/A because full denominators are absent.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new map semantics; prior seed counts retained|Not full map format/lifecycle|Natural populated cleanup/map replacement|
|Data types and constants|95%|N/A; exact six wrapper return contracts|Explicit register-width/error contracts for six wrappers|177B still unresolved/only classified|New calibrated read/write paths|
|Tables and pointers|93%|N/A; 4-byte manager-pointer write contract|Detect writes manager FAR pointer only when AL bit7 is set|Other lifecycle/target validity open|Initialize/reconfigure/reset counts|
|Functions/ASM/CFG|90%|N/A;78 new starts/174B; all78 exercised|Six wrappers and whole shutdown caller exercised|143 init-dispatch starts remain unexecuted across batches|Whole mode0 with original wrappers and explicit dependency fixtures|
|RNG|97%|N/A,semantic denominator absent|No RNG behavior inferred|Seed/ordering open|Actual RNG writer/DEMO path|
|Scheduler|96%|N/A,semantic denominator absent|Unlock then release even when unlock fails; saved gate unchanged|No natural IRQ/interleaving proof|Native repeated-level transition|
|DEMO/input|96%|N/A,semantic denominator absent|No DEMO/input behavior added|Natural navigation/timing open|Reproduce transition controls|
|Renderer/VGA|94%|N/A, semantic denominator absent|No new rendering evidence; prior pixel checks retained|No new draw/presentation proof|Clipped/depth/scale native cases|
|GUARD/bosses|93%|N/A, semantic denominator absent|No new AI evidence; prior class-bank evidence retained|No AI behavior closure|Uncovered AI/state branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No damage behavior inferred|Projectile lifecycle open|Original projectile transitions|
|Sprites/HUD/palette|92%|N/A, semantic denominator absent|No new sprite evidence; prior cleanup distinction retained|Other sprites/palette domains open|New natural source/scale cases|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Shutdown does not clear saved flag/handle; controlled state only|Natural SAVE/LOAD not exercised|Trace actual restore/reload ordering|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 proof|Win16 lifetime/backend unknown|Map Win16 equivalent cleanup|

All13areas remain PARTIAL. This batch adds no new cross-version or Win16 parity claim. Prior sixteen cleanup comparisons and32caller-only cross-version cases remain independent evidence, not coverage of these newly bounded wrappers.

## Required next runtime tests

Execute whole mode0 initialization through original adapters, real allocator/probe/error dependencies where feasible, and controlled failure responses; reconcile143unexecuted dispatcher starts. Capture natural saved-flag/handle states around actual shutdown and XMS unlock/release replies, without treating controlled double invocation as native behavior. Continue natural populated reset/level replacement, remaining177NONCODE bytes, Win16 counterparts, clipped renderer, AI/projectiles, DEMO and SAVE/LOAD. Full campaign remains active.
