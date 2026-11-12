# Nitemare3D: large CRT allocation, original probe integration and native DOS free

2026-11-12, DOS2.0 reference. PARTIAL; DEEP VERIFIED0new bytes. The previous goal turn was progress: natural whole cache initialization and all57295NONCODE endpoint profiles were verified and published. This batch replaces the large-allocation/zero-fill gap in that evidence with independent arithmetic, original-code tests, a natural257KiB allocation and DOS-free capture. The existing212B allocator is reused, not counted as a new function. No PE32 work.

## Source identity and reproducible inputs

Packed `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Canonical171360B image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`,1670relocations and original instruction inventory are pinned. Native DOSBox-X executable SHA256 `a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832`. Native load0824h, DS=SS2F95h, unpacked runtime SHA256 `6ff79b07a98de8873f60bf2da6d93f55bbc0d3320a1d8adbd90e02e7fde569b6`.

`audit_replay_crt_large_allocation.py IMAGE INVENTORY DECODER EMULATOR OUT` independently decodes the old allocator and new DOS-free wrapper, runs296controlled cases, and compares original stores/fullRAM with separate crt_large_allocation_model.py. `audit_replay_probe_original_crt.py IMAGE RELOCS EMULATOR OUT` runs16whole original game-probe/CRT-allocator/free chains, modeling only DOS48/49 responses.

`runtime_watch_crt_large_allocation.py DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG` captures the natural first successful probe allocation, zero-fill boundaries and DOS-free result. Frozen harness SHA256 `27ed2a0c446cb5be77ef3c7bf8d4c6320f87a177d3ecb681fe973dd50408cf11`; support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`. `verify_crt_large_allocation_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR` independently validates debugger responses/dump origins, then replays the original post-DOS suffix without any dependency replacement. It pins emulator native files.

`prepare_crt_large_allocation_fields.py OUTPUTS` catalogs three already-PARTIAL fields/8B. Raw memory/EXE/assets stay local; source and capture manifests identify exact hashes. Debugger commands are read-only register queries, memory dumps, breakpoints and RUN; no CPU/RAM injection.23original source assets remain unchanged. Reports/documents are analytical evidence, not instructions executed by the campaign.

## Exact functions, dependencies and ABI

|Function|CS:IP end exclusive|Image interval|Starts/code bytes|New counting|
|---|---|---|---:|---|
|Zeroed large FAR allocator|11EE:2A16..2AEA|148F6..149CA|97/212|Existing function reused|
|DOS free wrapper|11EE:2A0A..2A16|148EA..148F6|7/12|One new bounded function|
|Descending game probe|0FBA:0058..009D|0FBF8..0FC3D|22/69|Previous function reused|

Allocator arguments: DWORD count at SS:BP+6, WORD element_size atBP+0A. Return is FAR DX:AX, segment plus alignment offset. The entire candidate instruction union is independently decoded/byte-matched; all97allocator starts execute in the new controlled domain. This does not prove every external callback/DOS state or every possible parameter combination.

Free wrapper argument: FAR offsetWORD atBP+6, segmentWORD atBP+8. It ignores the offset, loads ES from the segment, executes MOV AH,49h / INT21h, POP BP / RETF. DOS-result AX and CF pass through; ES is clobbered to the supplied segment. BP/DS/SS/frame/SP+4 are checked under fixtures. The caller retains the four argument bytes. No null test, heap traversal, coalescing or local free-memory bookkeeping exists in this wrapper. Actual DOS internals are a separate dependency.

This distinguishes CRT/DOS allocation from game cache invalidation and XMS adapters. The XMS release adapter previously shown to returnAX0 is a different routine; its contract must not be substituted for DOS free.

## Reconstructed large-allocation arithmetic

The low32bits of DWORD count x WORD size are retained; no full48bit overflow test exists here. Let p be that low32bit product. Zero or p>000FFFF0h enters failure. For p>20000h, size must satisfy `(size-1)&size == 0`. For 10000h<=p<=20000h with non-power-of-two size, the original WORD arithmetic computes an alignment remainder using the current product highWORD:

```text
layout(count, size):
    p = (count * size) modulo 2^32
    if p == 0 or p > 0xFFFF0: fail
    lo = low16(p); hi = high16(p); offset = 0
    if p > 0x20000 and ((size-1)&size) != 0: fail
    if 0x10000 <= p <= 0x20000 and ((size-1)&size) != 0:
        offset = (hi * 65536) mod size
        if lo + offset carries beyond16bits: fail
        p = 65536 + lo + offset       // original MOV DX,1
    paragraphs = ceil(p / 16)
    repeat DOS AH48(BX=paragraphs) until CF failure or returnedAX > WORD_DS20F8
    if failed: callback/retry path
    end_segment = (returnedAX + paragraphs - 1) modulo65536
    if unsigned(end_segment) > WORD_DS20F6: update DS20F6
    zero every allocated paragraph in <=1000h-paragraph chunks
    return DX:AX = returned_segment:offset
```

The callback null test ORs both WORDs at DS246A/246C. If nonnull, original FAR CALL receives stack WORDs(size,countLow,countHigh), in that order. AX0 ends failure with DX0; nonzero AX, including FFFFh, re-enters the calculation and reloads caller arguments. New callback fixtures mutate those original arguments from invalid count0/size3 to count263168/size1, demonstrating reloading, not just repeating the old request. These are callback *contract tests*; no original nonnull callback implementation is identified or executed.

The model deliberately preserves WORD carries, modulo arithmetic and segmentation. Examples confirmed with original code:

- count21846,size3 gives p65538, alignment1, adjusted65539, paragraph-rounded65552zeroed bytes. count43690,size3 reaches alignment near128KiB; count43691,size3 is rejected by the non-power-of-two gate above128KiB.
- A synthetic count55560000h,size3 has low32product20000h despite a larger full multiplication. The original alignment path sets highWORD to1, yielding65552zeroed bytes and returned offset2. This is a controlled wrap-domain result, not a native asset/allocation failure.
- On successful zero-fill, CLD clears incoming DF. Failure before that path retains input DF under fixtures that preserve it; no universal DOS/callback DF preservation is inferred.
- End-segment comparison wraps to16bits. Synthetic F000/F100/FFF0 segments exercise segmented chunk rollover and high-watermark arithmetic. They are CPU/ASM tests in a2MiB flat emulator map, not proof that DOS can return such conventional allocations or proof about A20 configuration.
- A returned segment at/belowDS20F8 causes another AH48 call with no local AH49 call in this allocator. Tests cover lower/equal rejection followed by acceptance or failure. Natural reachability, resource lifecycle and termination for arbitrary manager replies remain open.

Zero-fill begins at segment:0000, covers alignment prefix and paragraph padding, and advances ES by1000h between up-to64KiB chunks. It does not merely clear the logical count*size bytes. Returning offset may be nonzero. Exact physical spans, ordered writes and dependency replies are exported.

## Controlled cases and original probe integration

296cases =248allocator cases(62distinct configurations x2loads xDF0/1) +48direct free cases(two loads x3ignored offsets x4segmentWORDs x2DOS CF outcomes). The prior552case report remains historical; it had only small successful products. New configurations add large successes through512KiB, 64/128KiB boundaries, odd sizes, product wrap, alignment-carry rejection, high/low watermark cases, segmented rollover, rejected segments and callback argument mutation. Other large-domain cases intentionally return DOS failure instead of inventing a conventional allocation that overlaps code.

All2MiB RAM outside72or74B of synthetic control-stack scratch matches a separate byte model, and every ordered original nonstack store matches. The74B window includes the allocator's six argument bytes; final original return frame and callback-mutated arguments are checked separately. Direct DOS-free cases use72B. External DOS48/49 and callback responses are fixtures; no host or real DOS block is allocated in these controlled tests.

16integrated cases use the original descending probe, original212B allocator and original12B free wrapper together. Only DOS service responses are replaced, with capacities0/64/257/511KiB, two loads and DF0/1. They verify all candidate sizes, paragraph requests, exact zero-fill/high-watermark stores, DOS-free ES, frames and full2MiB RAM outside72stackB.

This resolves the earlier zero-size ambiguity *for this original CRT chain with null callback*: product0 is rejected before AH48. When every positive candidate fails, the probe's zero candidate makes no DOS allocation request and the probe returnsAX0. The earlier fixture-only probe could accept a nonzero zero-size pointer because its allocation dependency was synthetic; that is not the behavior of this original CRT body. Natural failure/callback activation remains untested.

## Native allocation, zero suffix and DOS free

The original game reaches the first accepted probe allocation at11EE:2A87 after the DOS-success and lower-segment gates. Caller frame binds return0FBA:0082, DWORD count263168, WORD size1. Native AX5F98, BX4040, SI0 and CF0 match the independent layout. The allocation spans physical[5F980,9FD80), exactly263168B/257KiB.

**All263168payload bytes were already zero before zero-fill and remain zero afterward.** Native endpoint changes therefore count zero payload positions; they do not directly count native same-value store events. The verifier retains this limitation instead of treating final zero bytes as observed writes.

Original code11EE:2A87..2AE6 is then replayed from the actual before-RAM/register state, with no DOS, CRT, callback or IRQ fixtures.131675original instruction events/28unique starts,131585ordered nonstack stores (131584WORD zeros +one high-watermark WORD) match an independent2MiB RAM model. All captured16bit registers and CF/DF match the native end boundary. These store counts describe the controlled original-code replay, not a directly trapped native write count.

Native scoped comparison checks263168allocation bytes,32guard bytes and57388DGROUP bytes, excluding the captured clockDWORD DS081E. High-watermark DS20F6 changes4F97h->9FD7h, matching original MOV11EE:2A92. Native writer PC for that individual store was not directly trapped.35native/replay residual positions remain in clock/IRQ/audio/stack state and are exported; no whole-native-RAM parity or full interrupt semantics is claimed.293original code bytes (allocator/free/probe) match relocated source both before and after.

The natural free frame passes FAR5F98:0000 to11EE:2A0A. Before DOS, ES5F98/AH49 are captured; after DOS at2A14, **CF0** is captured directly. The preceding16B guard changes `4d140840400000004e33443230000000` to `4d000040400000004e33443230000000`; the trailing16B guard and all263168payload bytes remain unchanged. This is the actual DOS response and observed header delta, not a reimplementation of the DOS allocator's complete free/coalescing algorithm. The probe reaches its9Breturn tail with AX257; that last capture is before LEAVE/RETF, not another whole game-caller return.

Failed predecessor allocations were not individually trapped. The capture does not test native callback activation, large odd-size requests, segment rejection/rollover, corruption, heap exhaustion or Win16 parity. Those remain explicit runtime tests.

## Original NONCODE fields and classification

|Field|Image interval,end exclusive|Bytes|New evidence|Status|
|---|---|---:|---|---|
|DS20F6|29806..29808|2|Unsigned wrapping end-segment high-watermark; native4F97->9FD7 plus exact replay store|PARTIAL,already typed|
|DS20F8|29808..2980A|2|Unsigned returned-segment acceptance lower bound; native0, controlled lower/equal retries|PARTIAL,already typed|
|DS246A/246C|29B7A..29B7E|4|Optional FAR retry callback, bothWORD null test and precise args/reload contract; native0000:0000 at captured endpoints|PARTIAL,already typed|

Three fields/8already-PARTIAL bytes refined,0new file-data bytes. No native nonnull callback writer/body is inferred. Calendar candidate next to the callback and remaining177CLASSIFIED ONLY/UNKNOWN bytes are unchanged; no global nonuse claim is added. The previous all57295B endpoint profile remains frozen.

## Coverage update: 13 areas

Previous catalog182functions/8116starts/20549codeB/1063067controlled DOS2cases/37native. New183functions/8123starts/20561codeB/1063379controlled cases/38native. Additions: new DOS-free wrapper7starts12B,296+16=312controlled cases, one separately verified native allocation/free scenario. Existing97start allocator and22start probe are reused. The native suffix replay is part of native verification, not an additional central controlled-case count. Typed EXE data59469B, BSS5164B, field-role rows108 unchanged. Campaign UNKNOWN_CONTENT91330is not historical NONCODE reclassification.

PASS320 unchanged:892intervals/57295B=57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. New semantic percentages N/A because full area denominators are absent. Prior orientation values remain estimates, not recalculated measurements.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new format behavior|Natural level replacement open|Populated cleanup/map replacement|
|Data types and constants|95%|N/A;8already-PARTIAL field bytes refined|CountDWORD/sizeWORD, wrap/alignment/end-segment roles|177B unresolved/only classified|New calibrated data consumers|
|Tables and pointers|93%|N/A;3field contracts|Retry FAR pointer and caller-argument reload|Nonnull callback body/writer unknown|Callback setter/reference audit and actual activation|
|Functions/ASM/CFG|90%|N/A;new7starts12B,97oldstarts exercised|Large zero-fill and DOS free, original probe chain|Real DOS internals/callbacks not closed|CRT2065 full traversal/native failures|
|RNG|97%|N/A,semantic denominator absent|No RNG inference|Seed/DEMO order open|Original DEMO/RNG transitions|
|Scheduler|96%|N/A;35native residual positions explicit|Native timing/IRQ effects kept separate|Paused timing and IRQ/audio residuals open|Trace relevant IRQ writers|
|DEMO/input|96%|N/A,semantic denominator absent|No input behavior inferred|Playback/input ordering open|Natural DEMO path|
|Renderer/VGA|94%|N/A;263168allocation bytes+32guards checked|Backing-store initialization separated from rendering|No new renderer pixels/parity|Clipped native sprite/depth cases|
|GUARD/bosses|93%|N/A,semantic denominator absent|No AI behavior inferred|Boss/state transitions open|Uncovered state/attack branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No damage behavior inferred|Projectile transitions open|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|Heap zeroing distinguished from resource pixels|Actual resource refill domains open|Reset/refill/draw sequence|
|SAVE/LOAD|92%|N/A,semantic denominator absent|DOS free distinct from cache invalidation|Natural reload/free ordering open|Actual LOAD/populated reset|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 proof|Backend allocation equivalents open|Map Win16 allocation/free counterpart|

All13areas remain PARTIAL. This batch provides no new cross-version or Win16 behavioral equivalence. Full coverage of instruction starts is not DEEP VERIFIED semantics.

## Required next runtime tests

Capture natural CRT2065 heap traversal and DOS allocation/free responses around actual resource buffers, then populated reset/cleanup/refill through level/New-game/LOAD. Identify retry callback writers and bodies before claiming activation behavior; test failure/callback/retry separately from successful native257KiB path. Capture native odd-size large alignment only if real callers exist; synthetic wrap cases remain CPU contracts. Trace the35IRQ/audio/stack residual positions rather than masking them into whole-RAM parity. Continue remaining177NONCODE consumers, Win16 lifetime parity, clipped renderer, projectile/AI, RNG/DEMO and SAVE/LOAD independently. Four postfatal initializer ADD SP starts remain unexecuted and are not forced through a returning fatal fixture.
