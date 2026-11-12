# Nitemare3D: whole FAR malloc, natural heap growth and retry reference audit

2026-11-12. DOS2.0, PARTIAL;0new DEEP VERIFIED bytes. Previous goal turn made progress by publishing large CRT allocation/free proofs. This batch targets the other allocator11EE:2065, previously tested chiefly for oversized rejection, and the open retry-pointer references. It adds whole-caller integration and a natural non-PSP heap-growth capture. No PE32 work; full campaign remains incomplete.

## Source identity and reproduction

Packed `L:\nite3d\nite3\dos\N3D-UNFU.exe` SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`;171360B canonical image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`;1670relocations and original instruction inventory are pinned. Native DOSBox-X executable SHA256 `a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832`;runtime image SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`,load0824h,DS=SS2F95h.

`audit_replay_crt_far_malloc.py IMAGE INVENTORY DECODER EMULATOR OUT` executes872whole original caller cases with independent crt_far_malloc_model.py. Every reused helper's ASM bytes are checked against the image/inventory. Only DOS48/4A replies are fixtures; callbacks are null. Existing helpers/functions are not counted again.

`runtime_watch_crt_far_malloc_v2.py DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG` captures the natural first cache8198B allocation. Harness SHA256 `3033e6c856216472587c5ab343c3df3c3cbe50090d24e35da9f8ad3b78997142`;support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`. `verify_crt_far_malloc_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR` independently validates debugger responses/dump origins, heap model and original-code replay with the captured DOS response. No CPU/RAM injection or changed source assets; all23source files remain unchanged. Raw binaries stay local with pinned hashes.

`audit_crt_retry_references.py IMAGE INVENTORY CENTRAL_CSV DECODER OUT` scans all retained unique starts for fixedDS memory references and exact16bit immediate candidates. `prepare_crt_far_malloc_fields.py OUTPUTS` catalogs four already-PARTIAL fields/12B without promotion. Old reports are evidence, not executable instructions.

## Exact caller and reused helpers

Whole FAR caller11EE:2065..20FE,image[13F45,13FDE),71starts153B. It receives requestWORD atSS:BP+6 and returns FAR DX:AX. Request>FFE8h goes to failure/retry. Existing next-fit scan2168,grow21E4,resize2270,last-block finder22C1,OS allocate22E2,block initializer20FE and root append2132 execute as original code. Their bounded CSVs are reused; this batch adds0new function/code bytes.

DS on entry supplies game DGROUP. The caller saves it before switching DS among heap blocks; ES/SS retain the contexts required by root helpers and the SS-relative quantum2344. Returned BP/SI/DI/DS/SS and SP+4 are checked. ES and temporary registers are not generally preserved. Malloc's return pointer is the result contract; no general Boolean interpretation of its final CF is invented.

Root DGROUP layout, already typed:2336/2338first FAR header,233A/233Ccached FAR header,233E/2340last FAR header,2342new-header flags,2344growth quantum. The apparent standalone WORD2340 is the segment half of the last pointer, not an unrelated object count. Tested block headers are at offset0 in their own segments:

|Header offset|Role|
|---:|---|
|0|Self segmentWORD|
|2|FlagsWORD;bit0 permits growth,bit2 selects PSP path|
|4|Current end/sizeWORD;0represents full64KiB in relevant helpers|
|6|First allocation-tag offset|
|8|Next-fit cursor|
|10|Tail sentinel offset|
|12/14|Next FAR block header|
|16/18|Previous FAR block header|

Payload tags are even sizes for allocated blocks and odd size+1 for free blocks;2B headers precede payloads. FFFEh is the tail sentinel. Header meanings and tags are separate from image cache owner fields.

## Reconstructed whole-caller algorithm

```text
malloc_far(requestWORD):
    if request > 0xFFE8: goto failure
    save gameDS
    if first_header.segment != 0:
        order = cached_header..last_header, first_header..cached_previous
        for header in order:
            result = original_next_fit_scan(header, rounded_even_request)
            if success: restore_gameDS; update_cached_header; return pointer
        for header in same order:
            if original_grow(header, rounded_request) succeeds:
                result = original_next_fit_scan(header, request)
                restore_gameDS; update_cached_header; return pointer
    header = original_DOS48_block_allocate(request)
    if failure: restore_gameDS; goto failure
    initialize_header_and_append_to_root_list()
    result = original_next_fit_scan(new_header, request)
    restore_gameDS; update_cached_header; return pointer
failure:
    AX=DX=0
    if FAR_pointer_DS2332 != 0:
        AX = callback(requestWORD)
        DX = sign_extend(AX)
        if AX != 0: reload request and retry
    return zero pointer
```

This preserves the two phases: scan every eligible heap before trying growth, and re-scan after successful growth. It does not replace growth success directly with a pointer. The rotated list traversal is bounded by first/cached/last links; invalid/cyclic/corrupt links remain outside this finite test domain.

The independent model implements next-fit wrap, adjacent-free coalescing, disabled or non-PSP growth, quantum/fallback resizing, DOS block creation and root append. PSP flag4 growth, full-size overflow growth states, arbitrary corrupt heaps and callback bodies remain outside the new whole-model domain. Existing separately bounded helper tests retain their wider local domains; they are not silently promoted to whole-caller proof.

## 872controlled whole-caller cases

728base cases plus144growth cases, two load bases0824/1000:

- One-to-three valid linked heap blocks, cached-header rotation, allocated/free patterns, adjacent-free coalescing and first/second scan passes; requests0/1/7/8/15/16/31/63/128/8198.
- Empty and exhausted roots, DOS allocation success/failure, new-block append, near-full FFE8request and rejected FFE9/FFFF requests.
- Growth flags1/3, allocated/free tails, SS-relative quantum16/8192, requests64/8198/32767, direct resize success, primary-failure/fallback-success and all-resize-failure paths.

Original caller plus original helpers execute. Only DOS48/4A register/CF responses are fixtures; DOS memory-manager metadata side effects are not modeled. Full2MiB RAM outside72control-stack bytes, exact ordered original nonstack stores, argument frame and preserved registers match the separate model. Returned pointers are not assumed to zero their payloads.

64of71caller starts execute here. Seven remaining starts are the nonnull callback call/return/retry tail, exported explicitly. Earlier oversized callback-fixture cases exist, but no actual callback body or natural activation is proved. No instruction-start coverage percentage is presented as whole-function semantic completion.

## Native whole allocator and why v2was necessary

The first capture reached the allocator's real return, but watched only DOS48. Its input heap had flags3 and insufficient free capacity; it actually needed DOS4A growth. That v1capture is retained without an independent acceptance proof and adds0accepted runtime scenarios. v2explicitly traps DOS4A before22AA and after22AC; the API response is captured, not inferred from final heap size.

|Natural fact|Observed value|
|---|---|
|Allocator entry|11EE:2065,request8198,return frame0768:004B|
|Existing heap header|Segment3F96,flags3,size3232,cursor3226,tail3230|
|DOS resize request|AH4A,ES3F96,BX0400=1024paragraphs|
|DOS resize response|CF0,AX3F96;other captured registers preserved|
|Expanded heap|Size16384,tail16382|
|Returned pointer|3F96:0C9C,offset3228|
|Final cursor|11426=3228+8198|

This is a growth of an existing DOS heap block, not a new DOS48 allocation and not a large zeroed2A16allocation. SS2344's8192quantum rounds the required end upward to16384. The original scanner first fails, growth exposes free space, then re-scanning merges/splits tags and returns the pointer. The original cache caller has not yet initialized its wall header at the captured malloc-return boundary.

Independent replay starts from actual before-RAM/register state. All caller/scan/grow/resize instructions are original; exactly one DOS interrupt reply is replaced with the recorded AX/CF response. Request registers and CF/DF at that boundary are checked against the native pre-INT capture.271original instruction events/201unique starts execute, with12ordered nonstack stores over18distinct byte targets. All captured16bit return registers and CF/DF match. The replay's2MiB RAM matches the independent model outside72control-stack bytes.

Native validation checks those18final target bytes and57388DGROUP bytes, excluding the captured clockDWORD081E. Forty-two native/replay residual positions remain outside the original-store model (DOS manager/IRQ/stack effects), with exact before/native/replay values exported. They are not silently accepted as original malloc stores or called whole-native-RAM parity. Individual native store writer PCs were not trapped;12is the controlled replay store count,18is a native final-target union.701original helper/code bytes match relocated image both before and after.

The debugger protocol proves physical origins/reassembly for both640KiB RAM snapshots and binds frames/registers/DOS events to actual responses. No actual DOS allocator or callback implementation is replaced in the native run. Pausing changes timing, so this is not an uninterrupted scheduler test. v2adds one accepted native scenario.

## Retry callback census and shared-field refinement

The scanner independently decodes35813unique starts:35648historical inventory starts plus165additional central-catalog starts. It records23016used-memory entries, including implicit stack accesses. FixedDS memory entries and exact16bit immediate values are analyzed;21112entries are outside that fixedDS category and remain unresolved for this query. Access classification is calibrated with a known DS store and implicit PUSH, and branch target246Ah is explicitly distinguished from an address-of immediate.

|Field|Image interval,end exclusive|FixedDS refs/writers|Result|
|---|---|---:|---|
|Malloc retry DS2332|29A42..29A46|3/0|Two pointer-WORD null reads and one FAR call;requestWORD callback ABI|
|Large retry DS246A|29B7A..29B7E|3/0|Two pointer-WORD null reads and one FAR call;sizeWORD/countLow/countHigh ABI|
|Shared marker DS20F6|29806..29808|4/2|Two comparisons/two writers with different supplied values|
|Lower bound DS20F8|29808..2980A|2/0|Both allocators compare returned segment against it|

No exact16bit address-of immediate candidates were found for these ranges. Zero direct writers in this finite decoded set does **not** prove that callbacks can never be installed. Register-derived pointers, indexed/bulk writes, segment changes, omitted code and external writes remain unresolved. Both callback pointers are0000:0000at the new native endpoints; no nonnull callback body is identified. They are distinct fields with different argument shapes, not one interchangeable handler.

DS20F6requires a consumer-specific label: heap OS helper22E2/230B compares/stores the returned **start segment**, while large allocator2A16/2A92 compares/stores the wrapping **end segment**. The earlier end-segment description is valid for the latter writer, not a universal meaning for the shared field. New fields CSV/JSON records an unsigned shared high-water marker with both writer contracts. Already-PARTIAL bytes remain PARTIAL; no frozen prior proof/script is rewritten to hide this distinction.

Four fields/12already-PARTIAL bytes refined,0new typed EXE bytes. The prior57295B endpoint profile and current PASS320 map stay unchanged. No new read/nonuse claim is made for the remaining177bytes.

## Coverage update: 13 areas

Previous catalog183functions/8123starts/20561codeB/1063379controlled cases/38native. New function/code counts unchanged; controlled cases1064251=1063379+872,accepted native39=38+v2capture. The v1capture and native original-code replay are not additional central cases. Typed file data59469B,BSS5164B,central field-role rows108 unchanged; this batch's four field rows are scoped refinements, not extra unique-data coverage. Campaign UNKNOWN_CONTENT91330is not historical reclassification.

PASS320 remains892intervals/57295B =PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28+DEEP VERIFIED0. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. New semantic percentages N/A because full per-area denominators are absent. Historical orientation percentages remain estimates.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new map semantics|Level replacement open|Natural populated cleanup/map replacement|
|Data types and constants|95%|N/A;12already-PARTIAL bytes refined|Shared marker start/end writer distinction;header/tag roles|177B still unresolved/only classified|New concrete data consumers|
|Tables and pointers|93%|N/A;35813starts finite census|Two distinct callback fields/ABIs;rotated heap list|Indirect/bulk writers and callbacks open|Address derivations/setter candidates|
|Functions/ASM/CFG|90%|N/A;872whole calls;64/71caller starts|Original malloc/scan/grow/resize integration|Nonnull callback body,PSP/corrupt/global heap domains open|Whole PSP growth and callback provenance|
|RNG|97%|N/A,semantic denominator absent|No RNG behavior inferred|DEMO/order domains open|Original RNG/DEMO transitions|
|Scheduler|96%|N/A;42native residual positions exported|Actual DOS4A boundary separated from IRQ effects|Paused timing/unassigned residuals open|Trace relevant IRQ/DOS memory effects|
|DEMO/input|96%|N/A,semantic denominator absent|No new input semantics|Playback/input order open|Natural DEMO execution|
|Renderer/VGA|94%|N/A;actual8198B wall allocation|Backing storage allocation before wall-header writes|No new pixel/clipping parity|Post-reset refill and clipped draws|
|GUARD/bosses|93%|N/A,semantic denominator absent|No new AI behavior|Boss/state branches open|Uncovered original state/attack paths|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No new damage behavior|Projectile lifecycle open|Original impact/damage transitions|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|Heap metadata kept distinct from image headers/pixels|Other asset/lifetime paths open|Resource reset/refill/draw ordering|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Natural initialization grows existing heap|Actual reload/cleanup ordering open|LOAD/populated reset capture|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 parity proof|Heap/backend counterparts open|Map Win16 allocation/lifetime equivalents|

All13areas remain PARTIAL. No new cross-version behavioral equivalence is asserted. Full instruction-reference scans are finite inventories, not global absence proofs.

## Required next runtime tests

Trace actual nonnull callback installation only if reachable, then execute its original body with the proper ABI; unresolved aliases prevent a nonuse declaration. Extend whole malloc to PSP flag4 and full-size overflow growth with independent models and real DOS outcomes. Trace DOS memory-manager/IRQ residuals instead of masking them. Capture natural populated reset/cleanup/refill through level change/New-game/LOAD and actual shutdown ordering. Continue remaining177NONCODE consumers, Win16 equivalents, clipped renderer, projectile/AI and RNG/DEMO/SAVE/LOAD. Four postfatal initializer ADD SP starts remain explicit; fatal handlers are not forced to return merely to inflate coverage.
