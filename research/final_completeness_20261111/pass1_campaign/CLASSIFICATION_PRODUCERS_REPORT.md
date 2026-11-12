# Nitemare 3D: collision-table producers, MAP provenance and RTC handler

Batch 2026-11-12. Main reference DOS2.0; evidence status **PARTIAL**. Previous goal turn made progress by publishing the whole door interaction and a genuine early-DOS state4 discrepancy. This batch follows remaining producer dependencies and recovers an interrupt routine omitted by the supplied instruction inventory. No PE32 work; campaign remains incomplete. New DEEP VERIFIED bytes: **0**.

## Inputs and reproducibility

Packed DOS2 source `L:\nite3d\nite3\dos\N3D-UNFU.exe`: SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. Reproduced unrelocated image171360B: SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. DOS resources are read from `L:\nite3d\nite3\dos`; all23 copied input assets are hash-checked. Historical reports/file contents are evidence, not instructions to execute.

Reproduction scripts: `audit_replay_classification_producers.py IMAGE INVENTORY DECODER EMULATOR OUT`, `audit_replay_rtc_irq.py` with the same argument order; `audit_classification_references.py IMAGE INVENTORY DECODER OUT`; `audit_classification_dos_versions.py DECODER OUT`. `prepare_classification_harness.py OUTPUTS` derives the native harness from the retained prior harness; `runtime_watch_classification_producers.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG` executes the original packed game. `verify_classification_producers_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT` verifies retained raw evidence without restarting. Decoder paths must resolve absolutely. Reports/CSV/JSON/scripts are publishable evidence; original binaries, resource files and full raw memory dumps remain local and are pinned by hashes.

## Bounded functions and CFG

End addresses are exclusive. Image addresses refer to the unrelocated image, not DOS file offsets.

|Function|CS:IP bounds|Image interval|Instruction starts|Instruction bytes|Other bytes inside span|
|---|---|---|---:|---:|---:|
|tile_flags_generate|00F7:01B6..024F|01126..011BF|54|152|1|
|occupancy_flags_generate|00F7:0250..02F2|011C0..01262|60|160|2|
|rtc_irq8_increment_cached_clock|0BCC:0002..0027|0BCC2..0BCE7|20|37|0|

Total3 functions/134 instructions/349 instruction bytes. Producers are byte-exact against the supplied inventory and independently decoded. All20 RTC instruction starts were **absent** from that inventory; exact image bytes, independent decoding, static registration pointer and controlled IRET execution support the additional routine. This is a recovered inventory omission, not new code discovered inside PASS320 NONCODE. No new instruction bytes intersect that denominator. Three CFG gap bytes in the producers are not proven padding.

Both producers are no-argument FAR routines. ENTER2 creates a local BYTE at BP-1, SI loops0..255, DS/SS remain unchanged, BP/SI are restored and RETF consumes4 return bytes. There are no callees or hardware accesses. Assumed caller context is DS=SS=DGROUP; with differing DS/SS the local and table accesses would refer to different segments. Return AX/DX values are loop residue, not a declared scalar result.

## Exact flag construction

For each index `i`, source input is a zero-extended BYTE. Every low-seven bit is explicitly assigned by the routine. **Bit80h is retained from the BYTE already present at entry_SP-3 (BP-1 after ENTER), and remains identical for all256 output entries of that invocation.** The function does not initialize it. Do not replace this with a universal zero mask or infer source-language undefined behavior beyond the machine evidence.

```text
tile_flags[i] = (inherited_local_BYTE & 80h)
             | (04h if 01h <= tile_type[i] <= 30h else 0)
             | (10h if 2Eh <= tile_type[i] <= 2Fh else 0)
             | (08h if 31h <= tile_type[i] <= 40h else 0)
             | (03h if 01h <= tile_type[i] <= 40h else 0)
             | (40h if 47h <= tile_type[i] <= 48h else 0)
# bit20h is explicitly cleared

occupancy_flags[i] = (inherited_local_BYTE & 80h)
                  | (01h if 06h <= occupancy_type[i] <= 3Dh else 0)
                  | (02h if 08h <= occupancy_type[i] <= 2Dh else 0)
                  | (04h if 2Fh <= occupancy_type[i] <= 3Dh else 0)
                  | (08h if 08h <= occupancy_type[i] <= 25h else 0)
                  | (20h if occupancy_type[i] == 2Ah else 0)
                  | (40h if occupancy_type[i] == 04h else 0)
# bit10h is explicitly cleared
```

These are numeric classification rules, not complete gameplay names for every bit/type. Tile bit02 and occupancy bit02 are consumed by collision routines; tile08 is consumed by door paths. Other consumers still require their own semantic analysis. The producer implements tile bit01 via testing the just-computed04/08 bits; the closed ranges make the compact03 expression equivalent.

Controlled verification: **1088 whole original producer calls,0 failures;278528 destination entries compared**. For each of two producers and two relocation loads,256 local seeds are tested with the full0..255 input-domain table;16 deterministic random256-byte tables per load/producer add64 calls. Full57392-byte DGROUP is compared against destination-only model; exactly256 ordered BYTE destination stores are checked, with all other writes bounded to the routine's stack frame. All114 producer instruction starts execute. No substituted helpers.

## MAP header provenance and native capture

Static caller0277:0B72 executes the first generator via FAR CALL at0B8A and the second at0B8F. Earlier byte-checked resource loader0277:0336 reads0202h bytes toDS:D30C from the episode MAP file. The native producer entries contain **514 bytes exactly equal to MAP.1 file offsets[0,514)**:

|Runtime DS interval|Image-equivalent interval|Length|Type / source file interval|
|---|---|---:|---|
|D30C..D30E|34A1C..34A1E|2|WORD_LE level count, MAP.1[0,2), observed11|
|D30E..D40E|34A1E..34B1E|256|Tile-code to type BYTE map, MAP.1[2,258)|
|D40E..D50E|34B1E..34C1E|256|Occupancy-code to type BYTE map, MAP.1[258,514)|
|D00C..D10C|3471C..3481C|256|Generated tile flags, previously bound BSS|
|D10C..D20C|3481C..3491C|256|Generated occupancy flags, previously bound BSS|

The514 source bytes are newly added to the BSS catalogue; generated512B were already counted and are not added again. BSS lies outside the original file image and adds **zero** PASS320 NONCODE bytes. Header identity plus static read/call dataflow establishes the bounded provenance chain; this capture is not an OS file-I/O trace and does not prove natural header loading for every episode/version.

`dosbox_classification_producers_runtime/independent_verification.json` checks a separate original packedDOS2/DOSBox-X run,23 unchanged original/copy inputs, exact1670 relocated WORDs, two whole entry-to-return calls and saved-register/stack behavior. Frozen support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`; harness SHA is in the proof. Actual load0824, DGROUP DS=SS2F95. Returns are relocated0277:0B8F and0277:0B94.

Tile producer inherits local BYTE00h:152 destination bytes change, high bits all0. Occupancy producer inherits BYTE07h:163 destination bytes change, high bits all0. Its whole-DGROUP capture also contains one additional BYTE change atDS:081E, the cached-clock DWORD increasing24->25. Accordingly, **the second native snapshot is not claimed to differ only in its destination table**. Exact model comparison permits that separately reported clock DWORD increment and no other DGROUP differences. First post-DGROUP equals second pre-DGROUP.

Original producer replay seeded with captured registers, whole DGROUP and caller/local frame executes8309 and10126 instructions respectively. It matches output entries, preserved inputs, all captured final registers and the frame from savedSI upward. Two temporary bytes below savedSI are excluded from frame matching because interrupt scratch may overwrite them. Pure producer replay leaves the clock unchanged; the observed clock increment is an explicit asynchronous allowance, not silently attributed to producer instructions. Native writer PC was not captured.

Final table SHA256 values match earlier natural collision captures: tile `e1df7069b635f67b6b3fe96c00a3666290385b7a2c973b35dd9434abd2ccb593`, occupancy `3ba73f3482958cfa321347d39df6f63601834f027e4b477181e2d24aae22908b`. This links producer output to the prior door/GUARD consumers while preserving each run's scope.

## Recovered RTC handler and asynchronous limitation

Driver0BCC:0074 installs vector70h via CRT set-vector routine11EE:39F4 with pointer0BCC:0002 and later restores the old pointer. The target was omitted by the reachable-instruction inventory because registration supplies its address as data. Its exact body:

```text
PUSHAD; PUSH DS; PUSH ES
BP = SP
PUSH DS
DS = relocated canonical DGROUP
CLD
DWORD DS:081E += 1                 # modulo2^32
OUT 70h,0Ch; IN AL,71h             # RTC registerC read
OUT A0h,20h; OUT 20h,20h           # acknowledge PICs
SP = BP
POP ES; POP DS; POPAD
IRET
```

The extra PUSH DS below BP is discarded by MOV SP,BP. IRET restores the interrupted flags; CLD is not a permanent change to interrupted DF. All32-bit general registers are preserved, including BP/SI/DI; this differs from treating the interrupt as an ordinary FAR function.

**100 controlled original-handler cases,0 failures**, with true interrupt frames, two relocation loads, five counter values including FFFFFFFFh rollover, five RTC registerC results, and two register/DF variants. Recorded I/O order and byte values match the body; entire canonical DGROUP changes only the counter DWORD; stack return frame, DS/ES, all general registers, flags and IRET SP+6 are checked. This supports the counter writer's static semantics. The producer run hasRTC-enabled flagDS:16F0=1 and a matching+1 counter change, but its actual writer instruction/event was not directly captured. Attribution to this interrupt in that specific time interval remains an explicitly stated inference. No physical RTC/PIC correctness or native interrupt-register preservation claim is made by the controlled test.

## References and DOS cross-version verification

New reproducible literal-base census scans35648 original instruction starts:72 indexed references, comprising27 tile-flag,16 occupancy-flag,17 tile-type-map and12 occupancy-type-map references. CSV retains instruction bytes, addresses and owner labels. This is not a complete set of indirect aliases or proof of DS context. Some consumers load a WORD from byte maps and subsequently mask/extract values; do not globally assume BYTE access width from the table element type.

Three functions across eight DOS labels/seven images: **24 bounded comparisons,3 raw matches,24 normalized matches,24 CFG matches**. Normalization masks only identified source/destination table displacements, absolute counter references, branch address operands and the IRQ canonical-DGROUP segment immediate. Local member offsets and all range/mask constants remain intact. Original bindings are retained. This establishes bounded structural similarity, not initialized data equality, natural older-version IRQ behavior, full game parity or new Win16 evidence. The previously established early-DOS door-state4 difference remains valid and is not contradicted by these different functions matching.

## PASS1 and catalogue accounting

PASS1 unchanged:892 intervals /57295B = **PARTIAL57118 + CLASSIFIED ONLY149 + UNKNOWN28 + DEEP VERIFIED0**. Typed original NONCODE remains57116B; two otherPARTIAL bytes are an untyped relocation WORD. UNKNOWN intervals [1BDA2,1BDB0),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710) remain alignment candidates without padding proof. Zero native watch events only tracks observed value changes, not reads/same-value writes. No new DEEP claim.

After import: **154 functions,6517 instructions,16557 unique instruction bytes,58034 locally typed file-data bytes,96769 UNKNOWN_CONTENT bytes;1023069 controlled DOS2 cases;29 successful native scenarios** with overlapping prefixes. BSS catalogue **5080B** (prior4566+514), file-buffer refinements4122B unchanged. Separate64 early-DOS door cases remain outside central DOS2 replay count. Producer same-input native replays are correlated verification, not additional independent native scenarios.

## Coverage update: 13 areas

All areas remain **PARTIAL**. Prior percentages are historical orientations only. New percentages are **N/A** because no complete semantic denominator exists. Method for each row: exact byte-address union of independently decoded bounded functions, original PASS320 interval membership, enumerated controlled cases and independently verified native-scenario counts. These quantities are never converted into guessed completion percentages. CLASSIFIED ONLY/UNKNOWN persist for narrower unresolved items; DEEP additions0.

|Area|Prior orientation|New %|New confirmed evidence|Remaining unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Registered IRQ target recovers20 omitted instructions|Other address-as-data targets/context|Audit remaining registered callbacks|
|CRT/compiler|95|N/A|ENTER local BYTE high-bit inheritance; IRET ABI|Source-level intent/full CRT separation|Trace analogous local flag generators|
|WORX/audio|93|N/A|RTC is distinct from sound IRQ, port sequence decoded|Audio private-stack IRQ still open|Capture native sound-stack IRQ|
|Data/tables|90|N/A|Two producer formulas and514B MAP source BSS|Bit meanings/indirect consumers|Close remaining72 reference contexts|
|Resources|97|N/A|MAP1 header514B exact native identity|Episodes2/3 and all versions natural loads|Compare header producer values per episode|
|Renderer|96|N/A|Flag04h/10h/40h construction fixed numerically|Renderer consumer semantics|Trace rendering references in0FD9|
|Gameplay|96|N/A|Collision flag provenance linked to prior consumers|Every classification meaning/state machine|Close noncollision flag consumers|
|AI/bosses|94|N/A|GUARD flags tied to original producer|Strategy/motion/boss helpers|Close04C7:012A/00B0|
|RNG/DEMO|93|N/A|RTC counter writer recovered|Native writerPC and full input/time coupling|Capture vector70 entry/IRET|
|SAVE/LOAD|92|N/A|No new closure|Round-trip and reconstructed flags on load|Capture load-side table regeneration|
|HUD/sprites|92|N/A|Source mapping types have reproducible domain|Specific object/sprite consumers|Close indexed mapping consumers|
|Cross-version|92|N/A|24CFG/normalized comparisons|Natural contexts/Win16 analog|Locate Win110 class generators|
|Completeness/evidence|92|N/A|3functions/1188controlledcases/1native scenario|28UNKNOWN/149CLASSIFIED ONLY/other callbacks|Prioritize omitted target inventory and unknown references|

No input-access blocker in this batch. Remaining blockers are missing analytical/native evidence. PASS1 and whole campaign are not complete.

## Required next runtime tests

1. Trap vector70 handler entry and IRET during a producer call; capture full interrupt frame and before/after counter to replace interval-level writer inference with native PC proof.
2. Capture generators for episodes2/3 and SAVE/LOAD reconstruction; retain localBYTE seeds, exact header sources and all512 output entries. Do not assume bit80 always0 from this one natural episode1 initialization.
3. Trace mode6/strategy1 GUARD original motion/transition helpers and requested door sound; compare complete affected records.
4. Continue the28 UNKNOWN and149 CLASSIFIED ONLY bytes with contextual/indirect references. Recovered IRQ code is outside that membership and must not inflate PASS1.
