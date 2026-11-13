# Original damage sound events, bearing and frame-state writes

## Sources and new exact function boundaries

Reference DOS2 reproduced image SHA256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Every newly discovered instruction matches historical inventory bytes. Functions: death_sound_event083D:1922..19E4,image[9CF2,9DB4),135codeB/53starts; state7_sound_event083D:1AE4..1BD0,[9EB4,9FA0),173codeB/68starts; source_pan_sector04C7:0044..00B0,[4CB4,4D20),105codeB/46starts; source_relative_bearing04C7:0006..0043,[4C76,4CB3),60codeB/23starts; apply_frame_state04C7:0868..08A0,[54D8,5510),56codeB/22starts. Total529 reachable codeB/212starts. The655B aggregate spans also contain96B near jump tables and30B outside the discovered CFG/table unions; these30B are not promoted to executable code or universally proven padding.

Two24WORD CS tables: death[9D14,9D44),SHA2566e6fa287d6c296f1c32e20cd89fe64257fc0a3c6bbd77143af9fa014c5abee8c; state7[9ED6,9F06),SHA256a4c1aa298631d1a1314d7575a28520f2fe4ccd0730d23d2322d56fa26ae7b4a3. Newly typed96B and code are outside original PASS320 NONCODE. No existing NONCODE byte changes status.

Reproduce audit_replay_damage_sound_frame.py IMAGE INVENTORY DECODER EMULATOR OUT; audit_replay_damage_event_frame_chain.py with the same arguments; audit_damage_sound_frame_versions.py VERSION_ROOT CALLER_INSTRUCTIONS_CSV DECODER OUT; summarize_damage_event_frame.py; prepare_damage_sound_frame_fields.py. Output folders reside under campaign outputs to use pinned prior instruction catalogs. Per-function ASM/CFG,event tables,cases,argument traces,instruction coverage and hash manifests are emitted. Raw image/source binaries remain local. No new native runtime observation is counted.

## Sound-event selection and RNG

The old names death_extra/state7_extra in damage caller fixtures describe callsites,not their algorithms. Original083D:1922/1AE4 select event sound IDs from unsigned B.BYTE6. Both use range8..31 and24-way near tables; outside-range and explicit default cases chooseID0. They still call the downstream dispatcher forID0; silence or asset validity is not inferred.

Death map:8/20=>35;9=>8;10/18/19=>7;11=>36;12=>4;13=>19;14=>14;15/16=>11+rand()%3;23/24/30/31=>70;26=>74;27/28=>2;29=>9;all other BYTE types=>0. State7 map:8=>34;9/10=>56+rand()%3;11=>59;12=>20;13=>21;14=>16;15/16=>54+rand()%2;17=>6;18=>63;19=>60;22=>18;23=>72;24=>71;26=>73;27/28=>13;29=>56;30/31=>61;others=>0.

Only the listed random cases consume one original RNG call. Original wrapper0FBA:01A0,CRT LCG and32bit multiplication execute,without random-result substitution. Other cases leave RNG state unchanged. Event tables and every typeBYTE0..255 are exercised; sound resource existence/content and real playback are not thereby established.

## Direction, relative bearing and stack-carried priority

Both event wrappers PUSH WORD2,then FAR B pointer,then FAR A pointer and call04C7:0044. That routine uses B.WORD10h−DS:4162 and B.WORD12h−DS:4164 as wrapped16bit source-relative coordinates. A and the extra priorityWORD are not read by its original body. It calls04C7:0006,which executes prior original0C7D:08C6 integer ratio/angle lookup,then subtracts facingWORD DS:4156. If signed16(angle−facing)>180 it subtracts360 once; otherwise,if signed16(facing−angle)>180 it adds360 once. This is the actual branch algorithm,not a universal modulo360 operation for arbitrary WORD-facing values.

Pan result1 when relative bearing is strictly35<r<145; result2 when strictly−145<r<−35;otherwise0. Boundary values±35/±145 fall in0. The original angle lookup's zero vector yields90,so source at player position with facing0 produces sector1 under this code/model. Natural validity of that degenerate geometry remains open. The labels0/1/2 describe dispatcher arguments; actual left/right acoustic mapping is not proved by a silent stub.

After the direction FAR return,ADD SP,8 discards only A/B pointers,leaving the earlier priority2 on stack. PUSH AX(direction),PUSH SI(soundID),then FAR0C2B:03D6 creates a three-WORD argument frame(soundID,pan,2). ADD SP,6 removes these arguments. Exact entry frames verify the priority reuse; it is not guessed from a prototype. Original0C2B:03D6 remains a **preserving RETF fixture** in this batch. Its separate prior bounded dispatcher evidence does not turn this chain into audible WORX proof.

## Original frame/state writer and volatile return

04C7:0868 receives FAR A,B pointers,frameWORD,lowModeWORD,highModeWORD. It makes exactly five ordered nonstack stores: A.WORD0=frame;B.BYTE3=lowBYTE(frame);A.WORD6=(zeroExtend(highBYTE(frame))−1)mod65536;A.BYTE0Ch=lowBYTE(highMode);A.BYTE0Bh=lowBYTE(lowMode). The high bytes of modeWORDs are ignored. Frame high0 gives WORD6=FFFFh; this is independently exercised for all256 frame highBYTE values.

The function does not explicitly form a success value. Its finalAX is(lowMode&FFh) withAH=FFh only when frame highBYTE was0,otherwiseAH0. This follows DEC AX and later lowBYTE loads; callers must not reinterpret it as Boolean success. SI/BP/DS/SS and tested caller-owned registers/frame are preserved; BX/ES/flags are volatile. The exact store/frame claims assume distinct valid nonaliasing records and argument storage; arbitrary FAR wrapping/stack aliasing/natural record domains remain unclosed.

## Isolated and expanded-chain verification

7200 isolated cases pass:1888 per event wrapper,1500 pan,360 relative bearing and1564 frame writer. All212 new instruction starts execute. Event/bearing paths use original direction/angle/RNG/multiply plus one silent sound-dispatch return fixture. Frame writer has no callee fixture. Complete2MiB RAM outside184 control-stack bytes,ordered original stores,AX and return frames/register postconditions match independent models. Geometry matrix includes signed coordinate limits,normal/large facingWORDs,zero vectors and sector boundaries,with player-relative coordinate origins fixed at0 in these cases.

4532 additional joined cases execute original damage caller/effect/score/reaction selectors/RNG as before,now also original death/state7 event wrappers,bearing/pan/angle and frame writer. Three prior caller-entry AX substitutions are removed; one shared deeper sound-dispatch return fixture is introduced. Remaining substitutions are04C7:06D2 special and083D:05D2 late HUD-like dependency as preserving-AX fixtures,plus sound dispatcher and type21 text/message as preserving return fixtures. These four stub sites are explicit. Sound fixture does not rewrite AX:incoming direction,stack arguments and original wrapperAX return are checked.

The chain returns500 death,368 nonlethal default DS=SS,228 zero and3436 other nonlethal cases.1236 sound calls have pan histogram0:504,1:288,2:444 and priority2 throughout.21368 original RNG calls include88 event-selection draws; their ordering is interleaved with reaction-index selection and checked through exact state stores. All182 damage-caller starts execute;628 of709 available original starts across the expanded chain execute in this matrix.81 remain unexecuted in the joined matrix even though separate isolated new-body coverage is complete. Record/state writes from the original frame routine are now included in the model,not assumed absent.

Expanded-chain full2MiB RAM outside144 control-stack bytes and exact ordered original nonstack stores match; original effect/selector/score/event/frame AX at their RETF and entrySP are checked. Natural callback/dispatch/HUD writes,record aliases,capacity bounds,actual audio and IRQ/timing effects remain open. These are instruction replays,not new DOSBox sessions.

## Cross-version binding and data roles

Five actual dependencies are bound from the previously verified182-start caller instruction positions for each DOS label,then through the original wrappers' direction call. Forty bodies across DOS10/11/12/15/17/18/19/20 match normalized instruction shapes,CFG and24-way table mapping. Call/global/CS-table operands are masked only with explicit bindings; sound IDs,record offsets,priority and arithmetic constants remain compared. This does not prove external callee/Win16/audio parity or erase the earlier caller's DOS10/11 argument5 versus later4 difference.

Eight consumer roles refine existing records: A.WORD0/WORD6/BYTE0Bh/BYTE0Ch,B.BYTE3/BYTE6/WORD10h/WORD12h. They add no file/BSS union bytes. Existing angle lookup table and LCG state are reused without duplicate function/data count. New96B event tables are separately cataloged. Remaining original149CLASSIFIED ONLY+28UNKNOWN bytes receive no promotion/nonuse/padding claim from this analysis.

## Coverage update: 13 areas

Previous192functions/8551starts/21633codeB/59557typeddataB/1081019controlled cases/41native. New197functions/8763starts/22162codeB/59653typeddataB/1092751controlled cases/41native. Add529codeB,96tableB and11732returned controlled cases=7200isolated+4532joined. Reused caller/effect/RNG/angle/helper functions and40cross-version structural comparisons add no duplicate case count. Record-role rows125to133;BSS5164Bunchanged. Campaign UNKNOWN_CONTENT90170to89545;new code/table outside original NONCODE. Reference census35813 unchanged,new central/dependent hashes regenerated. Prior448 budget-stopped index cases remain separate historical evidence within the campaign count,not new successful returns here.

Original PASS320 map unchanged:892intervals/57295B=57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED. MapSHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. New semantic percentages N/A without complete area denominators;historical orientation estimates retained.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|96B CS event tables,8 structure-field roles;no PASS320 promotion|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|24type slots per event;stack priorityWORD reused across FAR calls|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|Five new bodies529B/212starts;4532 expanded-chain returns|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|88 original event RNGcalls interleave with reaction-index RNG|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|State7/death callsites identified as sound wrappers;AI body still open|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|Original health chain plus real frame/state stores;special/HUD remain fixtures|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|Original five-store frame/state routine,highBYTE minus1 semantics|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|40DOS normalizedcode/CFG/table comparisons;Win16/audio parity open|PARTIAL; natural runtime,remaining implementations and full semantic denominator incomplete|Locate Win16 resource-reader and driver counterparts|

All13areas remain PARTIAL. Expanded original instruction integration is narrower than natural target death/state/audio/gameplay or Win16 parity.

## Required next runtime tests

Trap natural damage caller,frame writer and both event wrappers;capture records before/after,player coordinates/facing,RNGDWORD,class-bank90B minimum and exact soundID/pan/priority. Observe actual0C2B:03D6/WORX entry/return and resource binding before claiming playback. Reconstruct remaining04C7:06D2 and083D:05D2 writes;replace or execute the lower sound/text paths with their real side effects. Verify natural aliases/record/angle limits and DOS10/11 late selector difference. Continue177 original remaining NONCODE bytes through actual consumers,Win16 equivalents,projectiles/bosses,renderer/RNG/DEMO/SAVELOAD. No PE32 port.
