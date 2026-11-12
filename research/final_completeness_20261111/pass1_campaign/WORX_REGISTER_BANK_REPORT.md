# Nitemare 3D: remaining-reference audit and WORX register bank

Batch 2026-11-12; DOS2 main reference. **PARTIAL**, new DEEP VERIFIED bytes **0**. Previous goal turn made progress by publishing classification-table producers and an omitted RTC handler. This batch returns to remaining PASS1 references and follows a raw candidate into its actual sound-bank consumers. No PE32 work; campaign remains incomplete.

## Inputs and new evidence

Packed source `L:\nite3d\nite3\dos\N3D-UNFU.exe`, SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; reproduced171360-byte image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Supplied DOS inventory35648 instruction starts is byte-checked; original PASS320 membership remains57295B. File/report contents are evidence rather than executable instructions.

The current149 CLASSIFIED ONLY bytes include single-byte zero neighbors, the uncalled-looking floating-point hook slot, numeric arrays and other storage without sufficient consumer proof. Previously recognized leap-calendar values are not repeated as a new discovery and remain CLASSIFIED ONLY. No zero byte is promoted to padding merely because no reference was found.

New `audit_remaining_omitted_memory_candidates.py IMAGE MAP INVENTORY CENTRAL DECODER OUT` checks299 exact literal displacement values for remaining62 intervals/177 bytes (149CLASSIFIED ONLY+28UNKNOWN), excluding93377 instruction bytes belonging to the original and pre-batch central inventories. It searches raw omitted bytes below1BDA2h, tests candidate instruction boundaries/operand locations and retains DS/SS context assumptions. The central input is frozen at `work/frozen_inputs/campaign_instructions_before_bank.csv`, recoverable from the preceding published catalogue. This avoids silently replacing a hashed input when the central catalogue is regenerated.

Result: one raw candidate, image **1812Dh**, bytes `00 06 32 01`, hypothetical `ADD BYTE DS:[0132h],AL`. This byte pattern was known in the older omitted-code report; the **new evidence is its bank storage and executed consumers**, not rediscovery of the same raw disassembly. Candidate-only scans never prove code or a DS context and never promote status.

## Bank layout and candidate context

WORX segment15BF contains a bank at offset2513h, image **[18103,18683)**: **128 records ×11 bytes =1408B**. Original loader explicitly copies128 records with11 copied bytes and5 skipped bytes per16-byte source record, after a four-byte source prefix. Original per-record override copies11 bytes to `2513h +11*BX` after checking source signatureWORD4253h (bytes `SB`). Original programmer computes its source as `2513h +11*BL` and consumes all11 bytes as register data.

Candidate1812Dh is **record3, byte9**. Its first two bytes are the last two bytes of record3, while the next two are the first two bytes of record4. This supplies a reproducible data interpretation supported by original writers and consumers. It does not prove that arbitrary alternate execution of those bytes is impossible; it supplies no executable reference to the unresolved DGROUP mask bytesDS:0130..0138.

|Field|CS-relative interval|Image interval|Bytes|Status/type|
|---|---|---|---:|---|
|Default bank|2513..2A93|18103..18683|1408|PARTIAL,128×11 register-parameter records|
|Operator-offset maps|2B66..2B78|18756..18768|18|PARTIAL,twoBYTE9 maps|
|RecordBYTE3 cache|2BD0..2BD9|187C0..187C9|9|PARTIAL,mutableBYTE9|
|Optional callback|3896..389A|19486..1948A|4|PARTIAL,FAR16 offset/segment; already typed previously|

First operator map:00,01,02,08,09,0A,10,11,12; second:03,04,05,0B,0C,0D,13,14,15. Tested voice domain is0..8. The routines themselves do not validate all instrument/voice indices; this report does not establish that every natural caller is within that domain. The bank count128 is directly established by the loader loop.

All1439 field bytes are file-backed but **outside original PASS320 NONCODE**. Four callback bytes already had local data evidence. Therefore the data union grows by **1435**, not1439; original NONCODE typed coverage grows by **0**.

## Bounded functions, CFG and ownership

End addresses are exclusive. Instruction CSV/CFG edges are independently decoded and byte-checked against the canonical image and original inventory.

|Function|CS:IP bounds|Image interval|Instructions|Instruction bytes|Central ownership|
|---|---|---|---:|---:|---|
|SB-record bank override|15BF:3792..37C4|19382..193B4|31|49|New|
|Bank-to-voice register programmer|15BF:37D1..3896|193C1..19486|93|197|New|
|Port callback setter|15BF:389A..38A7|1948A..19497|5|13|Previously owned; not counted twice|
|Delayed port writer|15BF:38A7..38D2|19497..194C2|24|43|Previously owned; new integration evidence|
|128×11 bank loader|15BF:5973..5998|1B563..1B588|16|37|New|

Five analysed functions169 instruction starts/339 code bytes; **three new central functions140 instructions/283 code bytes**. One byte in the override span is outside its reachable CFG and is not proven padding. The callback dataWORDs3896/3898 are outside both adjacent functions, not a gap to decode as instructions.

These are low-level external sound-driver operations in the already identified WORX segment. This separates them from gameplay decisions; it does not identify the precise external library build from a name alone or close every driver entry/callback.

## Algorithms and segment/ABI context

The bank routines are **NEAR**, unlike many gameplay FAR routines. Tests useDS=CS andDF=0, plus a separateSS stack. The override swapsDS/ES temporarily to copy from its caller's source record into the driver bank, then restores both segments. Programmer depends on driver-localDS and uses CS overrides for maps/cache/callback fields. Its finalLODSB depends onDF. No general proof for arbitrary entry segment contexts is claimed.

```text
override_ES_DI(BX):
    if WORD ES:[DI] != 4253h: CF=1; return
    copy11 bytes from ES:DI+24h to driver:2513h+11*BX
    restore savedBX/CX/SI/DI/DS/ES; CF=0

load_bank():
    call resolver4630                  # substituted only in controlled tests
    SI=2513h; DI+=4
    repeat128:
        copy11 source bytes into driver bank
        DI+=5
    AX=0

program(BL=instrument,BH=voice):
    data = driver[2513h+11*instrument : +11]
    a=operator_map0[voice]; b=operator_map1[voice]
    send(20h+a,data0); send(20h+b,data1)
    send(40h+a,data2); cache[voice]=data3; send(40h+b,data3)
    send(60h+a,data4); send(60h+b,data5)
    send(80h+a,data6); send(80h+b,data7)
    send(E0h+a,data8); send(E0h+b,data9)
    send(C0h+voice,data10)
    restore saved registers

send(AL=register,AH=value):
    saveAX/BX/CX/DX
    OUT388h,register
    repeat6: IN388h
    OUT389h,value
    repeat35: IN389h; IN389h            #70 reads, not35
    restoreAX/BX/CX/DX
    if callback.segment != 0: FAR CALL callback
    NEAR return

set_callback(BX=offset,DX=segment):
    CLI; callback=(BX,DX); STI; NEAR return
```

The setter forces IF=1 rather than restoring the entry IF. The port writer restores registers **before** the optional external FAR callback; a real callback's effects/ABI remain unclosed. Tests use an explicit preserving callback fixture. Segment zero disables the callback; offset zero alone is not the tested gate. The11 register-address formulas and I/O sequences are code observations; no acoustic rendering or physical chip behavior is established here.

## Controlled verification and limits

`audit_replay_worx_register_bank.py IMAGE INVENTORY DECODER EMULATOR OUT` executes all five original functions; programmer calls the original delayed writer. **6166 calls,0 failures**, all169 bounded instruction starts execute:

- 512 override cases: two relocated loads ×128 indices ×valid/invalid source signature.
- 4608 programmer cases: two loads ×128 instruments ×nine voices ×callback disabled/enabled. One load uses the original bank, the other deterministic replacement record bytes. Full driver64KiB memory, register preservation, cache update, all11 register/value pairs and callbackAX arguments are compared.
- 1024 writer cases: two loads ×256 register/data combinations ×callback disabled/enabled. Exact twoOUTs and76INs per register/value pair are verified; controlled IN values vary.
- 16 setter cases: two loads ×four pointer pairs ×two entryIF values; exact pointer writes/IF=1 are checked.
- Six loader cases: two loads ×three source patterns; all1408 output bank bytes and untouched driver memory are compared. Resolver4630 is substituted with a source pointer fixture, not a closed resource/DOS operation.

The duplicate central ownership check initially caught the two previously catalogued port helpers; imports now retain their original owners and count only three new functions. Replay count describes this batch's controlled executions, including integration/revalidation, not a global set of unique semantic scenarios. No native DOSBox test is added in this batch; the total remains29. Physical sound, mixer output, original resolver/callbacks, IRQ interaction, invalid-index safety and complete WORX behavior remain open.

## DOS cross-version comparison

`audit_worx_register_bank_versions.py IMAGE REPLAY_DIR DECODER OUT` independently locates the bank and each function, validates CS:IP/owner bounds against each version's inventory and compares actual bytes/CFG. Versions10/11/12/15/17/18/19/20 are eight labels/seven images.

**40 function comparisons:20 raw matches,40 normalized matches,40 CFG matches. All eight1408-byte default banks match exactly.** Early versions have different internal bank/entry offsets, so a fixed DOS2 segment-offset assumption was rejected and replaced by independent function anchors plus actual inventory segment/offset. Address-aware normalization masks CS memory displacements, SI/DI address immediates and call/branch operands; it retains port values, range/count constants and data-copy strides. Masked bindings still require semantic comparison in natural contexts. This is no new Win16/native cross-version parity claim.

## PASS1 and catalogue accounting

The new candidate scan supplies a stronger storage/consumer context for1812Dh but no supported promotion of the149 CLASSIFIED ONLY bytes. PASS1 remains892 intervals /57295B: **PARTIAL57118,CLASSIFIED ONLY149,UNKNOWN28,DEEP VERIFIED0**. Typed original NONCODE57116B; the remaining twoPARTIAL bytes are an untyped relocation WORD. Four UNKNOWN spans remain [1BDA2,1BDB0),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710); zero/alignment appearance and no-reference scans are not padding/non-use proofs.

Central catalogue now **157 functions,6657 instructions,16840 unique instruction bytes,59469 file-data bytes,95051 UNKNOWN_CONTENT bytes,1029235 controlled DOS2 executions,29 native scenarios**. BSS5080B, file-buffer refinements4122B and field-evidence-row counts remain unchanged. New code283B/data1435B are disjoint and outside original NONCODE; duplicate code/data is not counted twice.

## Coverage update: 13 areas

All areas remain **PARTIAL**. Prior percentages are historical orientation only; new percentages are **N/A** because complete semantic denominators are missing. Method for every row: exact instruction/data byte unions, PASS320 membership, enumerated controlled cases and independently verified native scenarios, without translating counts into guessed semantic percentages. Narrow CLASSIFIED ONLY/UNKNOWN items remain explicit; new DEEP0.

|Area|Prior orientation|New %|New confirmed evidence|Unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Independent WORX bank/entry segment anchors across8labels|Other callbacks/DS contexts|Continue address-as-data targets|
|CRT/compiler|95|N/A|No new CRT closure; stale leap-table pattern not promoted|149classified storage/padding roles|Find actual consumers/proven unused object provenance|
|WORX/audio|93|N/A|128×11 bank,programmer,original delayed writer integration|Resolver4630/real callback/acoustic output|Close resolver and natural bank load|
|Data/tables|90|N/A|1435new file-data bytes outsideNONCODE|DGROUP mask block still lacks consumer|Trace alternate/contextual references|
|Resources|97|N/A|11-of16 source record conversion|Source resource identity/lifetime|Trace original4630 input|
|Renderer|96|N/A|1812D raw mask reference now has sound-data context|DS0130 mask users unresolved|Keep interval CLASSIFIED ONLY|
|Gameplay|96|N/A|No new gameplay closure|Complete damage/projectile/door state updates|Continue original gameplay callees|
|AI/bosses|94|N/A|No new AI closure|GUARD strategy/motion/boss branches|Close04C7:012A/00B0|
|RNG/DEMO|93|N/A|No new closure|Native time/input ordering|Capture RTC entry/IRET|
|SAVE/LOAD|92|N/A|No new closure|Recreated state/resource round-trip|Deterministic native comparison|
|HUD/sprites|92|N/A|No new closure|Remaining sprite/HUD branches|Continue true rendering callers|
|Cross-version|92|N/A|40CFG/normalized,8whole-bank byte matches|Natural initialized state/Win16|Locate Win110 sound bank/consumer analog|
|Completeness/evidence|92|N/A|3new functions,1435new dataB,6166executions|28unknown/149classified and downstream scopes|Prioritize remaining actual consumers|

No source-access blocker. The true limitations are missing segment/caller/runtime evidence. These are not grounds to mark the campaign complete.

## Required next runtime tests

1. Capture original resolver4630 and natural bank loader5973 input ES:DI; identify the resource and compare128 source16-byte records to the1408-byte bank.
2. Trap programmer37D1 and writer38A7 for a natural voice; retain DS=CS/DF/index/channel, real callback pointer and finalOUT trace. Do not equate matching register writes with audible parity.
3. Watch the bank's11-byte records and actual copied source buffers during audio initialization; keep callback and IRQ effects distinct.
4. Continue remaining149 CLASSIFIED ONLY/28UNKNOWN without treating this raw-candidate rejection as a global no-code/no-read proof.
