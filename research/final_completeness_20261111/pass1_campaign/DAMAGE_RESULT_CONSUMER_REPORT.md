# Damage-result consumer: target health, death and reaction dispatch

## Evidence and exact boundaries

Reference DOS2 reproduced image SHA256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297; every decoded instruction matches historical inventory bytes. Whole FAR caller04C7:1304..1510 spans image[5F74,6180),524B. It contains484 reachable instruction bytes/182starts,38B CS jump table[60B2,60D8),and two unexecuted90h bytes at5FE1/6047. Those two bytes remain outside this function's proven CFG/code union; no universal nonuse or padding proof is claimed.

Reproduce audit_replay_damage_result_consumer.py IMAGE INVENTORY DECODER EMULATOR OUT. Outputs damage_result_consumer_replay/{damage_result_consumer.csv,CFG_edges.csv,jump_table.csv,execution_coverage.csv,cases.csv,dependency_events.csv,summary.json}. audit_damage_result_versions.py VERSION_ROOT DECODER OUT yields per-version byte-matched instructions,masked operands,normalized differences and graphs. prepare_damage_result_fields.py writes12 consumer-role refinements. Summaries pin source inputs and scripts. No native scenario added. All nine callee implementations remain AX-only preserving-register/no-memory-effect response fixtures in this batch; this is not full gameplay or callback closure.

## ABI, records and damage truncation

Arguments BP+6/+8 are FAR recordA pointer; BP+A/+C are FAR recordB pointer. A is a26B target-like record; B is28B source/context record. The original effect083D:01C0 receives these same four WORD arguments. Caller SUB AH,AH discards its high return BYTE, so effectiveDamage=AX&FFh. It zero-extends A.BYTE10h and compares it with effectiveDamage; both operands are0..255 even though the branch is signedJG. Returned0100h becomes0,FFF0h becomes240,FFFFh becomes255. These are caller-contract facts under the response fixtures; natural damage metric domains and all effect inputs remain unclosed.

If health<=damage, even health0/damage0, the death path writes health0. Otherwise damage0 returns without caller-owned data writes. Positive nonlethal damage subtracts the lowBYTE without wrapping under this branch condition and writes A.BYTE12h=8. State7 additionally calls083D:1AE4 before subtraction. Callee side effects could alter later reads in real execution and are not modeled away as proven absent.

## Death path and precise effects

After health0,083D:1BE4 returns a frame/indexWORD. When DS:4190!=1,083D:1922 is additionally called. Signed B.BYTE1Ah>0 selects low mode18,otherwise0. B.BYTE4 selects class table atDS:3D22+8*class; its near bank pointer plus2*index supplies WORD+4Ah. FAR-style near body04C7:0868 receives seven WORDs (Aoff,Aseg,Boff,Bseg,frame,lowMode,9). Original PUSH CS/CALL builds a FAR return frame; the fixture RETF is therefore deliberate.

083D:012E then returns a signed16 score delta. CWD and ADD/ADC add this delta modulo32bits to DS:4182/4184.083D:05D2 receives WORD4 in DOS2; its implementation is not executed here. Finally A.BYTE0Dh is copied to BYTE+1 through the FAR cell pointer atB+0Ch. The fixture-dependent ordered writes are health0,scorelow,scorehigh,cellBYTE. No caller-side pointer erasure or broader target removal is inferred.

## Nonlethal kind/state reactions and DS/SS

After subtraction/countdown, A.BYTE0Ah kind4 returns. Kind2 obtains index from083D:1C48 and dispatches frame from DS-bank WORD+3Ah with lowMode0/highMode8. Other kinds obtain the same index and use A.BYTE0Bh state. Table for states3..21 contains19 near targets:3/4/11 return;7/8/21 invoke04C7:06D2 with six WORDs(Aoff,Aseg,Boff,Bseg,0,1),store its AL toA.BYTE17h,then dispatch DS-bank WORD+3Ah with mode0/5. Other states3..21 and all out-of-range BYTE states take the default transition.

Default transition temporarily setsDS=Bseg,reads Bclass there,uses **SS:**[3D22+8*class] and **SS:**bankWORD[3Ah+2*index],writes that WORD toA+0,its lowBYTE toB+3,and saves nonzero old Astate toA+0Ch. Then Astate=21. PUSH SS/POP DS returns withDS=SS,not with an independently saved entryDS. Shared and split DS/SS runs deliberately give the two bank domains distinct frames: DS starts1100h; separate SS starts2200h. This verifies which segment supplies each frame and the branch's DS postcondition. Native callers commonly haveDS=SS; arbitrary split-context gameplay compatibility is not claimed.

Pseudocode: d=effect(A,B)&255; if A.health<=d: A.health=0; index=deathIndex(A,B); optionalDeathExtra(); dispatch(bankDS[index,+4A],signed(B.flag)>0?18:0,9); score+=signed16(scoreDelta(A,B)); updateSelector(4); B.cell[1]=A.token; return. If d==0:return. If A.state==7:extra(); A.health-=d; A.timer=8; if A.kind==4:return. index=hurtIndex(A,B); if kind2:dispatch(bankDS[index,+3A],0,8); else if state in3/4/11:return; else if state in7/8/21:A.special=lowBYTE(special(A,B,0,1));dispatch(bankDS[index,+3A],0,5); else:A.frame=bankSS[index,+3A];B.state=lowBYTE(A.frame);if A.state:A.saved=A.state;A.state=21;DS=SS.

## Controlled verification and remaining assumptions

4048 cases pass,all182 starts exercised: loads0824/1000,DS/SSsame orsplit,health0/1/127/128/255,raw damage0/1/127/255/0100/FFF0/FFFF,kind0/2/4,all19 jump-table entries,states0/22/255,mode0/1,signed Bflag boundaries,class0/1/7,index0/2/3,negative/zero/positive score deltas and32bit accumulator wrap. Original call order/complete argument frames,ordered nonstack writes,full2MiB RAM outside80 control-stack bytes,unchanged incoming argument frame and BP/SI/DI/SP/DS/SS postconditions match independent expectations. FinalAX/ES are volatile and not promoted to semantic outputs. Aliasing records,invalid FAR pointers,arbitrary callee clobbers,mutating callbacks and natural index/capacity bounds remain unclosed. Original effect/RNG code was not executed in these4048 cases; prior isolated effect evidence remains separate.

## Cross-version result

Eight DOS labels10/11/12/15/17/18/19/20 share the182-start CFG and19-entry target mapping. Six labels12/15/17/18/19/20 match normalized code. DOS10 and11 have one retained immediate difference: instruction index64 PUSH5 where DOS2 PUSH4. Masked call targets/global displacements are retained as explicit bindings; the immediate is not hidden. This proves a changed argument passed to the corresponding late death-path dependency,not its resulting HUD/game behavior. Actual callee equivalence and Win16 counterpart remain open; no separate cross-version runtime case is counted.

## Original NONCODE and catalogs

PASS1 review found no new consumer proof for remaining zero gaps or the alternate26B calendar pattern.

The new38B jump table is outside original PASS320 NONCODE. Its19 unsigned near offsets and state3..21 selector are proved by original CS indirect jump and exercised destinations. Twelve record roles refine existing structures,not new file/BSS unions. No record capacity,natural health domain,or original remaining177B nonuse is claimed.

## Coverage update: 13 areas

Previous188functions/8241starts/20864codeB/59469typeddataB/1068583controlled cases/41native. New189functions/8423starts/21348codeB/59507typeddataB/1072631controlled cases/41native. Add484codeB,38tableB and4048cases; record-role rows108 to120. BSS5164B unchanged. Campaign UNKNOWN_CONTENT91027 to90505. Newly bounded code/table is outside historical NONCODE; instruction union census35813 unchanged because this body was in historical inventory.

Original map unchanged:892 intervals/57295B =57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED. SHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. New whole-area percentages N/A without complete semantic denominators; historical orientation estimates retained.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|38B original CS jump table newly typed outside PASS320;12 record-field roles|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|19 state entries/3 table targets; DS versus SS class-bank provenance|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|New484B/182-start caller;4048 fixture-dependent cases/all starts|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|Target state transition21 and kind-specific reactions; no whole AI closure|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|LowBYTE damage,zero/death/nonlethal paths and score/cell writes|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|Frame-dispatch mode9/8/5 and opaque refresh argument4 versus early5|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|Eight DOS CFGs equal;DOS10/11 differ in one immediate; no Win16 proof|PARTIAL; callee algorithms,natural domains and runtime witnesses incomplete|Locate Win16 resource-reader and driver counterparts|

All13areas remain PARTIAL. A fixture-dependent caller proof is narrower than full damage,death,projectile or AI parity.

## Required next runtime tests

Trap natural04C7:1304 entry/return and its actual083D:01C0 result; capture A/B/class banks and caller states for zero,nonlethal,lethal paths. Trap original callee mutations before assuming them preserved. Execute effect+caller together with original RNG and actual source records; reconstruct083D:1BE4/1C48/1922/1AE4 and04C7:0868/06D2. Map the late death-path selector dependency for DOS10/11 argument5 versus later4 before asserting behavioral parity. Continue177 remaining NONCODE bytes via real consumers,full projectile/boss paths,Win16 and renderer/RNG/DEMO/SAVELOAD. No PE32 port.
