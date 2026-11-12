# Nitemare3D: whole cache initialization, natural allocation/XMS capture and all NONCODE endpoints

2026-11-12. DOS2.0 reference, PARTIAL. The preceding goal turn made measurable progress by publishing six XMS adapters and controlled whole shutdown, leaving143unexecuted initializer starts. This batch executes the original mode0 caller, adds one bounded memory-probe function, and independently verifies a natural original-EXE initialization. No PE32 work; full campaign remains incomplete.

## Source identity and reproduction

Packed source `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`;1670relocations and historical inventory are pinned. Native DOSBox-X binary SHA256 `a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832`. Native unpacked runtime image SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`, load0824h, DS=SS2F95h.

- `audit_replay_cache_initialization.py IMAGE INVENTORY DECODER EMULATOR OUT` runs186whole mode0 entry paths, using independent byte model cache_init_model.py. Existing dispatcher and six adapter bytes are checked against canonical image/inventory. No new dispatcher function is counted.
- `audit_replay_cache_memory_probe.py IMAGE INVENTORY DECODER EMULATOR OUT` independently decodes/proves the new probe entryCFG and runs60controlled cases.
- `runtime_watch_cache_initialization.py DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG` captures natural first mode0 using the original packed EXE and23unchanged source assets. Frozen harness SHA256 `2d762746f050c3b8b1741285782c4aa516bf0d38067ba5e45691297dc24e1a1a`;support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`.
- `verify_cache_initialization_capture.py IMAGE RELOCS RUNTIME WORK` independently binds captured registers/frames to actual debugger responses and reassembles physical RAM dumps. The model checks cache-owned final targets, not all callee effects.
- `audit_pass1_cache_init_endpoints.py OUTPUTS_DIR` rechecks every current PASS320 interval in both verified RAM endpoints and writes CSV/JSON profiles plus62native vector records. The older52capture profile remains frozen.

Scripts pin inputs by absolute path/SHA. Raw memory dumps, original assets and executable binaries remain local; published scripts and manifests identify their exact inputs. Debugger commands are restricted to breakpoints, run, register queries and memory dumps; no CPU/RAM injection or modified game assets. Documents/reports are evidence, not instructions executed by this campaign.

## Mode0 ASM, data layout and pseudocode

Existing FAR caller0768:0024..0293,image[076A4,07913),219starts/619codeB, receives WORD mode at SS:BP+6. Mode0 begins0040. Callee conventions use real FAR CALL or PUSH CS/NEAR CALL to FAR-return adapters. DS=SS game DGROUP is an explicit tested context. The caller saves BP/SI/DI; the adapter and allocator bodies have separately scoped contracts. Mode0's full AX result is not treated as a Boolean: the common tail only replaces AL from enabledBYTE.

```text
for i in 0..9:
    wall_slots[i] = far_allocate(8198)
    if pointer == 0: fatal(DS:0B86)
    pointer.word_at_4 = 0
    pointer.dword_at_0 = 0
for i in 0..3:
    sound_slots[i] = far_allocate(8198)
    if pointer == 0: fatal(DS:0BBA)
    pointer.word_at_4 = 0
    pointer.dword_at_0 = 0
probe = descending_allocation_probe()         // stored DS:3CB4
second_probe_word = CRT_2990()                // stored DS:3CB0; units open
n = trunc_toward_zero((probe - 70) * 1024 / 3074)
DS:3504 = min(n, 128)                         // signed upper comparison
if n < 1: fatal(DS:0BEE)
for i in 0..stored_count-1:
    [mutable_segment_DS2560]:4*i = far_allocate(3074)
    if pointer == 0: fatal(DS:0C22)
    pointer.word_at_0 = 0                     // owner prefix only
if enabled_BYTE_3CCE != 0:
    if not detect_manager(): enabled = 0
    else:
        q = query_adapter_AX()
        raw_query_3CB8 = q
        used_350A = 0
        limit_3508 = signed_min(q, 2048)
        if signed16(limit) < 64: enabled = 0
        else:
            r = allocate_adapter(limit)
            if signed16(r.DX) < 0: enabled = 0
            else:
                handle_3506 = r.AX
                locked = lock_adapter(handle)
                if signed16(locked.DX) < 0:
                    release_adapter(handle)
                    enabled = 0
                    warning(DS:0C56)
saved_initialized_BYTE_350C = enabled_BYTE_3CCE
```

The pseudocode's `fatal` continuation is conditional on the existing error handler contract, not an invented explicit branch in this caller. Diagnostic paths in this batch stop at original0FBA:000C. The four caller ADD SP instructions after those calls remain unexecuted; the campaign does not force a fatal return. Existing PASS1_ERROR_PATH_REPORT.md separately establishes normal CRT DOS AH4Ch exit intent, with callback/cleanup qualifications.

The512B object vector is original NONCODE image[1BE70,1C070). Initialization uses mutable DS2560; prior reset mode2 uses a relocated code immediate for1BE7. Controlled selector-override cases distinguish these bindings. DS0C9C cyclic index is not reset by this initializer. Disabled/absent-XMS paths leave prior handle/limit/used fields untouched; query paths zero used350A even before rejecting a too-small signed capacity. Saved350C copies the full enabledBYTE value, including80h in tests, rather than canonicalizing it to1.

Wall/sound block8198 =6B header +8192B payload. Object block3074 =2B owner +3072B payload. Original caller stores only headers/vector/globals; actual allocator/probe callees may also change their own memory. No claim that native allocator pixel payloads stay unchanged follows from this mode0 proof.

## Signed XMS branches, explicit external fixtures and error paths

186controlled cases at load0824/1000 include probe0/69/70/72/73/74/76/77/257/454/455/456/1023/32767/65535, enabled0/1/80, detection AL0/1/7F/80/81/FF, query0/1/63/64/65/2047/2048/2049/32767/32768/65535, allocation/lock success and failure replies, null allocations at first/last wall/sound/object and128-slot tail, release-failure replies and mutable table selector changes. Configurations are deduplicated before the two loads.162paths return,24stop at a fatal entry.

Original mode0 and all six original XMS adapters execute. Only CRT far allocator2065, game probe0058, CRT second probe2990, warning0078, INT2F replies and external manager responses are fixtures in this suite. The separately tested probe body is original in its own60case suite. Fixtures do not allocate actual DOS/XMS resources. Synthetic storage can extend above640KiB and is not evidence of DOS conventional capacity.

Full1MiB RAM except72B synthetic control-stack scratch matches the independent model; every ordered nonstack store matches, including duplicate count/limit writes whose final values alone would hide them. Original dependency arguments/order, return frames and preserved registers are checked. No same-value native store count is derived from this controlled trace.

Important confirmed caller distinctions:

- Query capacity is compared signed.8000h/FFFFh remain in raw_query and limit, then fail signed minimum64; they are not treated as huge unsigned capacity.
- The allocation wrapper checks manager AX, but the caller checks signed DX. A synthetic AX0/BL7F/DX3456 reply yields caller-visible DX7F56/AX0, allowing a lock request with stored handle0. This is a controlled response contract, not a demonstrated native manager failure.
- Successful lock returns a physical DWORD split DX:AX, whose highWORD is also used by the caller's signed test. A synthetic successful highWORD8000 triggers release/warning; actual native highWORD0017 passes. A failed lock with BL<80 also produces nonnegative DX. The caller does not save the physical DWORD.
- Release response is ignored on the warning branch. The warning callee's returning fixture is an explicit dependency assumption; its complete natural output/error contract is not closed here.

Combined with prior mode1/mode2/invalid-mode cases,215of219retained dispatcher starts have executed.139of the143previously unexecuted starts are newly exercised. Remaining images076E1,07720,0779B,077CE are the four3B ADD SP,2 instructions after fatal calls. Their absence is reported, not repaired with unrealistic return fixtures. Four90h gaps outside retained entryCFG remain separately classified, not globally proven padding.

## New bounded descending allocation probe

0FBA:0058..009D,image[0FBF8,0FC3D),22starts/69B,all independently decoded/byte-matched and exercised. It initializes a DWORD local1024, decrements it before each request, and passes DWORD count=(candidateKiB<<10) plus WORD element_size1 to CRT11EE:2A16. Returned FAR DX:AX is tested by OR. A nonzero pointer is passed to CRT11EE:2A0A, then AX returns the candidateKiB. Requests are1023,1022,...,0KiB; it never requests1024KiB. If every request fails, AX0 returns after1024attempts. Zero can also be a successful zero-size candidate under a returning nonzero fixture.

60cases =two loads x ten allocation-response patterns x three nonnull FAR forms (offset-only,segment-only and F000:FFFE). Patterns include thresholds0/1/63/64/257/1022/1023/1024,sparse success at0/257/900,and all failure. All request widths/order, first1023limit, freeing of the selected exact FAR pointer, no direct nonstack writes, all RAM outside72stackB and return frame/registers are checked. No pixel memory is dereferenced by the probe itself under fixtures.

This is the maximum successful candidate in a bounded sequence of CRT allocations, **not total free conventional RAM**. The complete CRT2A16/2A0A implementation and DOS allocation behavior are not closed by these fixture tests. Static neighboring ASM shows the relevant DOS AH48/49 service boundaries and count-times-size parameter use, but those CRT bodies are not newly counted as closed functions. Native probe AX257 is the result of the real probe path in this scenario; internal failed-attempt replies were not individually trapped.

## Natural DOSBox-X initialization, independently checked

The actual game reaches original mode0 and returns to its original caller, preserving captured BP/SI/DI/DS/SS and SP+4.85callee records retain entry/return registers and FAR frames, bound to debugger responses and original CALL continuations. They comprise76far allocations, one game probe, one second CRT probe, detect/query/allocate/lock adapters and three nested external manager calls. No synthetic manager or allocator is used in this native run. Native pausing affects timing; this is not an uninterrupted timing test.

|Native fact|Observed result|Scope|
|---|---|---|
|Conventional allocations|10walls+4sounds,8198B each;62objects,3074B each|76returned FAR pointers,disjoint305360B requested union within captured640KiB|
|Game probe / object count|257KiB /62slots|Original truncation formula matches; probe is bounded allocation result|
|Second CRT probe|AX1736h=5942|StoredWORD only; units not inferred|
|XMS detection entry|C3FF:0010|Original detector returnsAX1; exact INT2F AL not directly trapped|
|XMS query|14912KiB /3A40h|Native manager reply, capped to2048 by caller|
|XMS allocate|Request2048KiB, managerAX1/handle1|Original adapter returns handle1/DX0|
|XMS lock|ManagerAX1, physicalDWORD00170000h|Original lock returns DX0017/AX0000; caller accepts nonnegative highWORD|
|Final cache globals|count62,handle1,limit2048,used0,enabled1,saved1,index0|531distinct cache-owned final bytes match independent model|

Actual allocator returns are preserved as segment:offset, without silently canonicalizing offsets above15. All62active vector entries match those returns, and every final owner/header field matches the model. The model describes254store events, but native same-value stores were not directly instruction-traced.531is a final-byte target union, not a count of directly observed native writes.

Before/after full640KiB RAM is reassembled from40actual MEMDUMPBIN chunks with verified physical origins. Across these snapshots864byte positions change;316are cache-owned target positions and548are outside modeled cache stores. All deltas are exported. CRT heap bookkeeping, probe memory and stack/IRQ effects are not silently attributed to cache stores or declared closed.862original code bytes (dispatcher+six adapters+new probe) match relocated original both before and after. Manager body above640KiB and complete CRT heap semantics remain separate dependencies.

## All 57295 original NONCODE bytes at the new endpoints

892intervals x2complete endpoints =1784full-interval samples. Profiles retain exact start/end,length,status and both hashes; byte delta CSV retains253changed positions across6intervals.245positions lie in the active248B object vector; eight others lie at27F2E,297FA,29806..29808,29A4C..29A4E,29A50..29A52. Their exact changes are exported without inventing a native writer-PC trace for clock/CRT state.

All62active vector records (248B of512B capacity) now have a natural whole-initializer allocation-return binding. The unused264B capacity is not thereby proven unused. Remaining149CLASSIFIED ONLY+28UNKNOWN=177B have zero endpoint changes here, not zero reads or stores. Neither debugger endpoints nor these profiles establish global nonuse, transient writes or same-value writes. Previous52capture profiling evidence remains unchanged; this separate native session adds one runtime scenario, not an extra scenario per dump/profile.

Four identical52B diagnostic strings at image[28296,282CA),[282CA,282FE),[282FE,28332),[28332,28366) are bound respectively to wall/sound/count/object failure calls. They contain `Insufficient conventional ram available to run game` plusNUL. Image[28366,2837A) contains `Unable to lock xms` plusLF/NUL, used by warning0476:0078. Already PARTIAL objects are refined by these caller paths; no new original-file typing or status promotion is counted.

## Coverage update: 13 areas

Previous catalog181functions/8094starts/20480codeB/1062821controlled DOS2cases/36native. New182functions/8116starts/20549codeB/1063067controlled cases/37native. Exact additions: one bounded probe22starts69B,186mode0+60probe cases, one accepted native whole-init. Existing dispatcher/adapters reused. Typed file data59469B,BSS5164B,field-role rows108 unchanged; campaign UNKNOWN_CONTENT91342is not historical reclassification.

PASS320 unchanged:892intervals,57295B=PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28+DEEP VERIFIED0. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. New semantic percentages N/A: no complete per-area semantic denominator exists. Historical orientations below remain historical estimates.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new format semantics|Natural level replacement open|Capture populated cleanup/map replacement|
|Data types and constants|95%|N/A;57295B x2endpoint samples|Probe/count/WORDerror/physicalDWORD distinctions|177B unresolved or only classified|Calibrated new read/write consumers|
|Tables and pointers|93%|N/A;62native records/248B active vector|Natural allocation-to-vector/header binding; mutable selector|264B inactive capacity not nonuse proof|Different counts/reinit/cursor cases|
|Functions/ASM/CFG|90%|N/A;new22starts69B;215/219dispatch starts exercised|Full mode0 paths and bounded probe|4postfatal starts; CRT bodies not closed|Original CRT allocation/DOS/error cleanup contracts|
|RNG|97%|N/A,semantic denominator absent|No RNG inference|Seed/ordering domains open|DEMO/RNG state transitions|
|Scheduler|96%|N/A;native entry/return plus85callee records|Actual initializer completes with preserved frame|Paused timing/IRQ effects separate|Natural repeated-level timing|
|DEMO/input|96%|N/A,semantic denominator absent|No new input semantics|Playback/order open|Actual DEMO path|
|Renderer/VGA|94%|N/A;76native allocations/305360B union|Real wall/sound/object backing storage|No new pixel/presentation parity|Clipped/depth/scale native draws|
|GUARD/bosses|93%|N/A,semantic denominator absent|No new AI evidence|Uncovered AI/boss transitions|Original state/attack branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No new damage evidence|Projectile transitions open|Original projectile/impact behavior|
|Sprites/HUD/palette|92%|N/A;62object buffers initialized|Owner/vector/header setup matches native|Other sprite/HUD/palette paths open|Post-reset refill/draw|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Initializer preserves cyclic index in controlled paths|No natural reload/reinit ordering proof|Trace LOAD/populated reset and cursor|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 proof|Equivalent initialization/backend unmapped here|Map Win16 lifetime/allocation equivalents|

All13areas remain PARTIAL. Cross-version cleanup comparisons remain prior independent evidence; this batch does not claim these mode0/probe contracts across other DOS versions or Win16.

## Required next runtime tests

Capture natural populated reset/cleanup through level change/New-game/LOAD, then refill with retained cursor; verify allocator/frame/state ordering. Capture actual shutdown unlock/release outcomes and saved-flag lifecycle without forced double invocation. Reconstruct original CRT2065,2A16,2A0A and2990 dependencies with real DOS responses where feasible, plus qualified fatal cleanup callbacks. Continue remaining177NONCODE consumers, Win16 initialization equivalents, clipped renderer, projectile/AI, RNG/DEMO and SAVE/LOAD independently. Four postfatal ADD SP instructions remain explicit, not artificially exercised for a coverage percentage.
