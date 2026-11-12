# Nitemare 3D: GUARD facing, view octants and frame selection

Batch 2026-11-12; main reference DOS2.0. Status **PARTIAL**, new DEEP VERIFIED bytes **0**. Previous goal turn made progress by linking the remaining raw reference candidate to WORX bank data and publishing new functions/data. PASS1 remains the primary completeness denominator; this batch closes dependencies previously substituted in GUARD tests and adds natural frame-selection evidence. Campaign is incomplete; no PE32 work.

## Sources and reproduction

Original packed `L:\nite3d\nite3\dos\N3D-UNFU.exe` SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; canonical171360-byte image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Original instruction inventory35648 starts is byte-checked. Existing documents are evidence sources, not instructions to execute.

`audit_replay_guard_orientation.py IMAGE INVENTORY DECODER EMULATOR OUT` independently decodes three whole functions and runs no-stub models. `prepare_guard_facing_integration.py OUTPUTS` derives `audit_replay_guard_with_facing.py`, extending the earlier shared-world movement/validator replay with original00B0. `audit_guard_orientation_versions.py IMAGE REPLAY_DIR DECODER OUT` compares bounded DOS functions; `replay_guard_orientation_versions.py EMULATOR COMPARISON_DIR` checks the real DOS10 discrepancy. `export_guard_orientation_fields.py OUTPUTS` writes eight consumer-role rows.

`prepare_guard_orientation_harness.py` and its v2 supplement derive the native harness. Argument order follows retained support: `DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG`. `verify_guard_orientation_capture.py IMAGE RELOCS RUNTIME WORK EMULATOR OUT` verifies retained captures and reruns original code using actual memory/registers. Raw EXE/resources/memory remain local, pinned by hashes; scripts/ASM/CFG/CSV/JSON are published. Decoder directories must resolve absolutely.

## Bounded functions and semantic correction

Previous recording-stub labels `motion` and `transition` were provisional. Whole bodies now establish that **04C7:00B0 sets a facing BYTE, not coordinates**, while **04C7:012A selects a relative directional frame**. This changes the dependency description without inventing additional movement effects.

|Function|CS:IP interval,end exclusive|Image interval|Instructions|Instruction bytes|CFG gap bytes|
|---|---|---|---:|---:|---:|
|Facing from signed vector|04C7:00B0..0129|04D20..04D99|55|116|5|
|Relative frame update|04C7:012A..0217|04D9A..04E87|89|237|0|
|Actor-to-player view octant|0AEA:0C0A..0CC0|0BAAA..0BB60|93|180|2|

Three new functions /237 starts /533 instruction bytes, all byte-exact and independently decoded; every start executes in controlled cases. Seven CFG gap bytes are not proven padding. No instruction byte intersects original PASS320 NONCODE. Instruction/CFG CSVs retain exact addresses/bytes.

All three are FAR functions. Facing arguments: guardFAR, signedWORD dx,dy; it preservesBP/SI and does not access coordinates. Relative update arguments: guardFAR,actorFAR,forceWORD; it preservesBP/SI/DI and expects DS=SS in the tested near-data context. View helper arguments: lowBYTE flag in a WORD,actorFAR; result is **AL**, with no general AX boolean/scalar contract. ES and volatile temporaries are not promised restored.

## Facing algorithm

Write only guardBYTE+11h:

|dx sign|dy<0|dy=0|dy>0|
|---|---:|---:|---:|
|negative|7|6|5|
|zero|0|preserve previous|4|
|positive|1|2|3|

SignedWORD branches are used, including8000h as negative. Zero/zero performs no facing store. This is a direction selector, not a velocity generator. The separately known0218 routine generates velocities from direction tables; it is not silently folded into00B0.

## View octant and finite-width arithmetic

Let `dx=signed16(player.x-actor.x)`, `dy=signed16(player.y-actor.y)`, `ax=abs(dx)&FFFFh`, `ay=abs(dy)&FFFFh`. Player coordinates come fromDS:4162/4164 and actor+10h/+12h. The mode parameter is tested as a BYTE, not a fullWORD.

```text
if flag != 0:
    if ((2*ay)&FFFFh) < ax unsigned: return AL=(2 if dx>0 else6)
    if ((2*ax)&FFFFh) < ay unsigned: return AL=(4 if dy>0 else0)
    if dx>0: return AL=(3 if dy>0 else1)
    else:    return AL=(5 if dy>0 else7)
else:
    if dx<0:
        if dy<0: return AL=(7 if ay>ax unsigned else6)
        else:    return AL=(4 if ay>ax unsigned else5)
    else:
        if dy<0: return AL=(0 if ay>ax unsigned else1)
        else:    return AL=(2 if ay<=ax unsigned else3)
```

Do not replace this with an assumed symmetric atan2 rounding rule. Ties and zero matter: zero/zero returns2 forflag0 and7 for nonzero flag. Absolute8000h remains8000h; doubled magnitudes wrap16bits before unsigned comparisons. These arithmetic edges are preserved in the model; they do not prove that natural map coordinates reach every synthetic extreme.

## Relative frame algorithm and data dependencies

```text
view = original_C0A(guard.byte0F, actorFAR)
relative = ((3 if guard.byte0F==0 else4)+guard.byte11-view)&7
if guard.byte12 == relative and BYTE(forceWORD)==0: return
guard.byte12 = relative
row = 14h if guard.mode in {8,16,17}
      else24h if guard.mode==6 and guard.strategy!=2
      else04h
descriptor = WORD DS:[3D22h+8*actor.byte4]
frameWORD = WORD DS:[descriptor+row+2*relative]
guard.WORD0 = frameWORD
actor.byte3 = LOWBYTE(frameWORD)
```

`forceWORD=0100h` has the same skip behavior as0 because only its lowBYTE is checked. The class structure has stride8 and the firstWORD is a nearDS pointer; this does not close the remaining six bytes or all class entries. The consumer requires up to52 bytes: four-byte header plus three eight-WORD rows; header meaning, producer, allocation size and frameWORD resource interpretation remain open. Eight new field-evidence rows are consumer refinements, not eight newly unique fields or whole-record closure.

## Controlled verification and increased integration

`guard_orientation_replay`: **4666 cases,0 failures**:50 facing tests cover signed sign partitions including extrema under two relocated loads;2312 view tests cover17×17 deltas, four lowBYTE flags0/1/2/255 and two loads;2304 frame tests cover two loads, two view flags,eight headings,six modes,two strategies,three forceWORDs and equal/different cached octants. Original012A calls originalC0A; no callees are substituted. Full22334-byte world,57392-byte DGROUP, caller frame and saved registers are compared. Descriptor banks are controlled fixtures; natural producer identity is not inferred from them.

`guard_move_original_facing_replay`: **5184 cases,0 failures**. Original0422 movement now calls original0254 collision validator and original00B0 facing setter. This removes one more substitution from the prior shared-world matrix and checks its actual direction-field effect along with full8192-byte map/guard/actor results. Five dependencies remain substituted: preprocessing, vector helper, propagation,RNG and lookup. Tilebit08 door interactions remain outside that movement matrix. Mode6 reversal can supply localWORD+128 from stored signedBYTE80h; facing uses the localWORD sign, not a presumed storedBYTE interpretation.

New central controlled-execution count adds9850, while the separate cross-version256 cases are reported outside the DOS2 sum. These are bounded tests, not full AI/pathfinding parity.

## Native whole-call evidence and rejected preliminary capture

Initial native capture completed the original call but omitted an indirect bank atDS:F200 outside itsDGROUP0..E030 dump. It has no independent accepted proof and counts **zero additional verified native scenarios**. The original files are retained; completing a harness alone is insufficient to verify indirect data inputs.

The v2 capture includes the52-byte nearDS bank before/after. `dosbox_guard_orientation_runtime_v2/independent_verification.json` verifies original packedDOS2/DOSBox-X,23 unchanged source/copy assets, exact relocated image, actual FAR caller frame, BP/SI/DI restoration, DS=SS and SP+4. Frozen support SHA256 `64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89`; v2 harness SHA256 `210061f36627e1e392ecbac300412a0145beba2715f42dd38b9f585ac932adc5`.

Actual sample: **GUARD0 at map:264E,actor20 at map:0236,class8,mode7,strategy0,flag0,heading2,force1**. Actor coordinates(416,1440),player(1440,3616),delta(1024,2176),view3 andrelative2. Class entry points to nearDS:F200; selectedWORD is atF208 and equals0400h. Note this is a mode7 initialization, not a natural mode6 strategy2 test.

Exact world changes:

|Map offset|Before|After|Meaning|
|---|---:|---:|---|
|264Fh|00h|04h|HighBYTE of guard frameWORD0=0400h|
|2660h|00h|02h|Guard relative-octantBYTE+12h|

ActorBYTE3 is rewritten as00h and therefore has no value delta. All other world bytes, all57392DGROUP bytes and all52 bank bytes are unchanged. Original012A+C0A replay using captured inputs executes92 distinct instructions, uses no stub and matches entire world/DGROUP/bank and all captured final registers. This is correlated verification of one native case, not another native scenario. No asynchronous clock allowance was needed in this capture.

The52-byte snapshot is catalogued separately as a near-heap consumer window. Image-equivalent DS:F200 lies beyond the established BSS extent, so it is **not** added to file-data coverage,BSS5080B or originalNONCODE. Full heap allocation extent and lifetime are not established. Zero watch events for28UNKNOWN bytes are still value-change-only observations, not absence-of-read/use evidence.

## Real DOS1.0 discrepancy

Three functions across eight DOS labels/seven images: **24 comparisons,12 raw matches,23 address-aware normalized matches,23 CFG matches**. The unmatched function is DOS10 relative-frame updater,85 instructions/225-byte span versus DOS2's89/237. Masked global/indexed bindings and call/branch operands are recorded; record-field offsets and mode constants remain intact.

DOS10 selects row24h for mode6 regardless of strategy. DOS11/12/15/17/18/19/20 test strategy2 and select row04h for that case. **256 controlled original-version cases,0 failures**, execute the unrelocated original frame/view routines with explicit DS=SS9000 and version-specific global/table bindings. Product eight versions ×two flags ×modes6/8 ×strategies0/2 ×force0/1 ×equal/different cache. Controls verify skips and unchanged later-compatible cases. This proves a bounded machine-behavior difference; natural DOS1.0 mode6/strategy2 occurrence, initialized data and Win16 parity remain unproven. The earlier door-state4 version discrepancy is a separate result.

## PASS1 and catalogue accounting

PASS1 unchanged:892 intervals /57295B = **PARTIAL57118 +CLASSIFIED ONLY149 +UNKNOWN28 +DEEP VERIFIED0**. Typed originalNONCODE57116B; twoPARTIAL bytes remain an untyped relocationWORD. UNKNOWN spans [1BDA2,1BDB0),[1D0EC,1D0F0),[20B88,20B90),[2770E,27710) remain unresolved alignment candidates. No byte is promoted from a zero pattern or negative reference search.

Central results after import: **160 functions,6894 instructions,17373 unique instruction bytes,59469 file-data bytes,94518 UNKNOWN_CONTENT bytes,1039085 controlled DOS2 executions,30 accepted native scenarios** with overlapping prefixes. BSS5080B and prior file-buffer refinements4122B unchanged; near-heap snapshot52B is separate; field-evidence rows53. New bytes533 are code outside originalNONCODE. Cross-version256 is separate from central DOS2 cases.

## Coverage update: 13 areas

All areas remain **PARTIAL**. Previous percentages are historical orientation; new percentages are **N/A** because complete semantic denominators are absent. Method for every row: exact bounded instruction/data unions, original PASS320 membership, enumerated controlled matrices and independently verified native scenarios. These counts are not guessed semantic percentages. Narrow CLASSIFIED ONLY/UNKNOWN remain explicit; new DEEP0.

|Area|Prior orientation|New %|New confirmed evidence|Unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|NearDS:F200 dependency captured outsideDGROUP dump|Allocation/context/lifetime|Trace descriptor allocation/producer|
|CRT/compiler|95|N/A|No new CRT closure|149classified byte roles|Actual consumers/object provenance|
|WORX/audio|93|N/A|No new audio closure|Resolver/callback/native sound|Continue original sound-bank resolver|
|Data/tables|90|N/A|Stride8 class-pointer consumer,three8WORD rows|Header/producer/full class record|Trace DS3D22 pointer writes|
|Resources|97|N/A|Natural frameWORD0400h and bank snapshot|WORD resource identity|Bind frame bank to source resource|
|Renderer|96|N/A|Relative frame selection and lowBYTE propagation|Visible draw consequences|Trace actorBYTE3 renderer consumer|
|Gameplay|96|N/A|Facing is not coordinate movement|Full state-machine behavior|Close remaining movement helpers|
|AI/bosses|94|N/A|OriginalB0 integrated with movement+validator|D80 controller/bosses/modes|Decode remaining controller branches|
|RNG/DEMO|93|N/A|Reversal localWORD sign retained|Complete timing/input coupling|Original RNG/scheduler integration|
|SAVE/LOAD|92|N/A|No new closure|Descriptor regeneration/state round-trip|Capture load-side banks|
|HUD/sprites|92|N/A|Native relative2/frame0400h update|Sprite index/animation lifetime|Connect to real sprite draw|
|Cross-version|92|N/A|DOS10 strategy2 discrepancy,256cases|Natural old-version/Win16 context|Find Win110 relative-frame analog|
|Completeness/evidence|92|N/A|3functions/9850controlledcalls/1native scenario|28UNKNOWN/149CLASSIFIED ONLY/other dependencies|Continue unresolved true producers/callers|

No source-access blocker for this batch. Remaining limitations are missing semantic/native contexts. Campaign completion is not established.

## Required next runtime tests

1. Capture natural mode6/strategy2 and mode8/16/17 selection,including skips and forceBYTE0/1; retain descriptor bank and actual caller context.
2. Trace DS:3D22+8*class pointer initialization and nearDS bank allocation/copy. Capture sufficient memory beyond a fixedDGROUP dump; distinguish snapshot window from allocation extent.
3. Continue original door validator with original facing/frame update and original interaction; close downstream sound/descriptor producers rather than only replacing recording stubs.
4. Bind selectedWORD and actorBYTE3 to actual sprite draw/animation. Keep DOS1.0 difference explicit until natural caller reachability is verified; no Win16 or full-gameplay parity claim.
