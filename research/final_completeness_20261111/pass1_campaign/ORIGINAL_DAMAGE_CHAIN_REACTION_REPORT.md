# Original damage chain, reaction indexes and score dispatch

## New boundaries and sources

DOS2 reproduced image SHA256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297 is independently matched against historical instruction bytes. Three newly cataloged bodies: target_score_delta083D:012E..01BF image[84FE,858F),87codeB/42starts in145B span; death_frame_index083D:1BE4..1C47 image[9FB4,A017),99B/43starts; hurt_frame_index083D:1C48..1CAB image[A018,A07B),99B/43starts. Total285codeB/128starts. The score body contains25 WORD near targets image[851C,854E),50B,SHA2564a4bb65dc9adc150bf105e6b7a172f1f059641d3fa32586aaa3d43e0251235bf. Eight remaining span bytes are outside the discovered score CFG/table; no universal padding/nonuse assertion. Both code and new table are outside original PASS320 NONCODE.

Reproduce audit_replay_reaction_selectors.py IMAGE INVENTORY DECODER EMULATOR OUT, audit_replay_damage_chain.py with the same argument contract, audit_reaction_selector_versions.py VERSION_ROOT DECODER OUT, prove_reaction_rng_range.py, summarize_reaction_chain.py and prepare_reaction_selector_fields.py. OUT folders reside under campaign outputs so prior pinned instruction CSVs are available. Input files/relocations/scripts/prior instruction CSVs are hash-pinned. Native runtime count does not increase. Original source EXE and reproduced image remain local; no binary patch result is treated as natural runtime.

## Reaction selectors: exact reads and RNG consumption

Both FAR selectors receive recordA pointer atBP+6/+8 and recordB atBP+A/+C. A.BYTE12h is the gate. If it is zero, B.BYTE4 selects8B class slot atDS:3D22+class*8; the near WORD pointer addresses a frame bank. Death tests bankBYTE59h; hurt tests bankBYTE49h. Nonzero returns index7 immediately with no RNG call or nonstack writes. Values80h/FFh are accepted; the test is zero/nonzero,not signedpositive.

Otherwise original0FBA:01A0 wrapper calls original CRT LCG and original32bit multiplication. LCG state atDS:24B8/24BA advances state=(state*214013+2531011)mod2^32; return=(state>>16)&7FFFh. Selectors loadCX7,CWD,IDIV CX and use signed remainder0..6 as index. They accept only a nonzero **HIGH BYTE** at bank[4Bh+2*index] for death or bank[3Bh+2*index] for hurt. Low BYTE alone is irrelevant; test banks deliberately contain low34h with zero high bytes in rejected entries. An unavailable entry retries RNG,advancing state again. The random path cannot choose7.

prove_reaction_rng_range.py matches original MOVAX,DX/AND AH,7Fh/RETF suffix and exhaustively enumerates32768 returned integers. Remainders are0..6; remainder7 has0 witnesses. Consequently CMP SI,CX/JZ retry-for-equal7 trueedge is impossible under this original RNG contract. This is a static arithmetic proof,not32768 extra instruction cases. No patched RNG is used to force that edge.

With a stable bank whose candidates0..6 all have zero high BYTE and with the fast7 path unavailable,the original loop has no accepting exit.448 controlled runs stop before their33rd RNG entry after32 original iterations,checking64 ordered stateWORD stores. They establish bounded nonreturn observations alongside that conditional control-flow fact; they are not actual DOSBox freezes,natural bank-validity proof,forced success returns,or complete asynchronous behavior analysis.

The original selectors preserve BP/SI/DI/DS/SS and use FAR caller cleanup. Successful random return isAX=index withCX7/DX=remainder under original helper behavior; AX is the semantic output. Other volatile registers/flags are not promoted to preserved contracts. Complete RAM/store/frame checks distinguish same-value stores and RNG-free fast paths.

## Original signed score map

083D:012E reads unsigned B.BYTE6; recordA does not supply this selector. Type8..32 indexes25 CS near offsets; outside that range returns0. Signed16 results are:8/26=>25;9=>75;10/32=>50;11/15/16/23/27/28=>100;12/29/30=>250;13/18/19=>150;14/20/24/31=>200;21=>-1000;22=>1000;17/25=>0. All256 BYTE types are exercised. This routine itself does not update global score; the original caller later CWD-sign-extends AX into its ADD/ADC accumulator.

The25-way table,all output constants and case-target mapping are independently decoded. Type21's negative score is not confused with effect-type21's zero damage/message behavior; integrated zero-health examples can still enter the caller's death path with damage0. Full gameplay meaning of each source/context type remains broader than this arithmetic contract.

## Joined original caller/effect/selectors/score/RNG

4532 integrated cases execute whole04C7:1304 caller,whole083D:01C0 effect,newscore,bothindex routines,original RNG wrapper/LCG/multiply. Four previous AX response substitutions are removed: effect,death_index,hurt_index,score. Their actualAX is checked at original RETF together with restored entrySP. Call order/arguments and original stores are independently predicted. Five preserving-AX/no-memory-effect fixtures remain:083D:1922 death_extra,083D:1AE4 state7_extra,04C7:0868 frame_dispatch,04C7:06D2 special,083D:05D2 late selector/HUD-like dependency. Type21 text/message target0D29:0750 has a separate preserving RETF fixture. None of these remaining implementations is claimed closed or harmless in natural gameplay.

The chain covers4532 returns with500 death,368 nonlethal default DS-restored-to-SS,228 zero and3436 other nonlethal outcomes. It executes21280 original RNG calls,with up to16 calls in a selection retry;348 negative16bit effect results reach the original lowBYTE damage consumer.304 death cases return fixed7;0 integrated hurt selections return7. The latter follows the original caller's preceding A.BYTE12h=8 write: under the remaining preserving-state fixtures,the hurt selector cannot take its zero-gate fast path. This is not an assertion that index7 is globally unreachable in hurt selector calls elsewhere.

Both relocation loads0824/1000 and shared/split DS/SS execute. Negative metric deltas,damage truncation,score penalty/wrap,nonpositive signed flags,class/bank choices and special/reaction modes are retained. All182 caller instruction starts execute. Of435 available unique original starts across eight bodies,404execute in this integrated matrix;31 remain unexecuted here. Separately the3856 selector/score cases execute all128 starts of the three new bodies; that does not inflate integrated coverage. Compiler helper and full effect domains remain governed by their separate prior evidence.

Exact ordered original nonstack stores and all2MiB RAM outside144 control-stack bytes match the integrated model. Incoming argument frames and BP/SI/DI/SP/DS/SS postconditions match; volatile finalAX/ES/flags are not generalized. Independent selector/score cases check2MiB outside112 stack bytes. Each RNG step writes two WORDs,not a fabricated native write count. Invalid pointers,record aliasing,natural bank sizes,mutating callbacks,full frame dispatch/HUD work and native timing remain outside these proofs.

## Cross-version and data-role evidence

All24 bodies across DOS10/11/12/15/17/18/19/20 match normalized code/CFG and score table-to-case mapping. Masked FAR calls/global/CS-table displacements are retained in explicit bindings; semantic constants/record offsets remain compared. This bounded equivalence does not erase the prior caller's DOS10/11 late argument5 versus later4 difference. No actual Win16 runtime/counterpart established.

Five consumer roles refine existing A.BYTE12h,B.BYTE4,B.BYTE6 and8WORD hurt/death candidate windows atbank3Ah/4Ah. These32 near-bank bytes are not new file/BSS coverage or proof of full bank capacity. The new50B file-backed CS score table is separately typed. Remaining original149 CLASSIFIED ONLY+28 UNKNOWN bytes receive no new status/absence/padding inference from this work.

## Coverage update: 13 areas

Previous189functions/8423starts/21348codeB/59507typeddataB/1072631controlled cases/41native. New192functions/8551starts/21633codeB/59557typeddataB/1081019controlled cases/41native. Add285codeB/128starts,50dataB and8388controlled cases=3856 isolated+4532joined. Of these new cases7940return and448are explicitly budget-stopped nonreturns. No separate count for32768 arithmetic checks or reused RNG/effect/caller functions. Record-role rows120to125; verification found duplicate source registrations in the working catalog generator and removed them before publication. The earlier field-preparation script now only writes its own outputs; regeneration rejects duplicate refinement sources. No duplicate rows count as coverage. BSS5164Bunchanged. Campaign UNKNOWN_CONTENT90505to90170. Reference census remains35813because new bodies were in historical inventory; central/dependent hashes regenerated.

Original PASS320 unchanged:892intervals/57295B =57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED. MapSHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. No evidence-derived full-area semantic denominator exists; new percentages N/A and historical orientation estimates retained.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|50B CS score jump table,5 existing structure roles;no PASS320 promotion|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|Two8WORD banks;HIGH BYTE eligibility and fixedindex7 context|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|Three new bodies285B/128starts;4532 original chain returns|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|Original LCG/rejection chain;21280 calls;remainder7 bounds proved|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|Death/hurt index mechanics; broader state/AI dependencies remain fixtures|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|348 negativeWORD effect results flow through actual lowBYTE consumer|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|Original reaction-index selection; actual dispatch/HUD bodies still fixtures|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|24DOS normalizedcode/CFG/table matches;Win16 counterpart open|PARTIAL; natural runtime,remaining callee effects and whole-area denominator incomplete|Locate Win16 resource-reader and driver counterparts|

All13areas remain PARTIAL. Original-code integration removes four dependencies but leaves the five named bodies,text callback,natural runtime and broad gameplay parity open.

## Required next runtime tests

Capture natural04C7:1304 and original selector/RNG entry-returns with complete A/B/class-bank windows90B minimum and pre/post RNGDWORD. Include lethal/nonlethal/zero paths and actual bank rejection histories before inferring natural distributions or freezes. Reconstruct remaining state7/death-extra/dispatch/special/HUD-like bodies and repeat joined execution with their real writes. Establish natural metric/record/alias bounds;map Win16 equivalents. Continue177 original remaining NONCODE bytes through actual consumers,projectiles/bosses,renderer/RNG/DEMO/SAVELOAD. No PE32 port.
