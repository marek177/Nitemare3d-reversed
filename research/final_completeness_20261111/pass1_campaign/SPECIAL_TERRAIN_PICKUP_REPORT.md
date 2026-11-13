# Special terrain and pickup: original handlers, records and collision integration

## Result and evidence limits

This batch replaces the two upper response fixtures used by the movement analysis with original code in controlled integration paths. The special-terrain dispatcher, six latch handlers, sound-event wrapper, sound-bank selection, pickup-record lookup, record/cell clearing and pickup dispatcher are independently decoded and tested. All 413 newly cataloged instruction starts execute. Remaining text, screen, driver, HUD-like and item callbacks are explicit fixtures. No native DOSBox session, full transition behavior or DEEP VERIFIED byte is added.

The 8,320 new contexts comprise 4,204 special-terrain and 4,116 pickup contexts. Original instructions match the reproduced DOS2 image and supplied instruction inventory. Every non-stack write and callback frame is compared in order, together with full 2 MiB RAM except the declared control-stack windows. Tests use load segments 0824h and 1000h with both DS=SS and split DS/SS. The tested segment behavior is part of the contract, not an assumption that every helper preserves DS.

## Exact newly cataloged bodies

Image intervals below are half-open spans; code-byte counts exclude gaps and embedded data.

|Function|Image span, hex|Code bytes / starts|
|---|---|---:|
|special_terrain_dispatch|[A620,A6E2)|189 / 83|
|terrain_ep1_level7|[A53E,A568)|42 / 14|
|terrain_ep1_level10_A|[A568,A5B7)|79 / 21|
|terrain_ep1_level10_B|[A5B8,A5D2)|26 / 7|
|terrain_ep3_level10|[A5D2,A5EC)|26 / 7|
|terrain_ep2_level10|[A5EC,A606)|26 / 7|
|terrain_ep3_level1|[A606,A620)|26 / 7|
|sound_event42|[9270,9281)|17 / 5|
|sound_bank_selection|[AC00,AC5B)|87 / 26|
|pickup_record_find|[B548,B5A1)|87 / 42|
|pickup_cell_clear|[B5A2,B5B7)|21 / 8|
|pickup_apply|[B5B8,B7F8)|534 / 186|

Total: 12 functions, 1,160 code bytes and 413 starts. Pickup dispatcher contains a 30-byte CS-relative jump table that is separately classified as PARTIAL data, not code. All new bytes lie outside the original PASS320 NON-CODE baseline. Existing paired-cell and sound dispatcher functions retain their prior ownership and are not counted again.

## Special-terrain dispatcher: 083D:2250

The argument is a terrain type in LOWBYTE(BP+6). The upper byte is ignored. A class BYTE is read from DS:D30E[type]. Current displayed level is WORD(DS:626C + 1), with 16-bit wrap; episode is DS:626A. Dispatch uses these exact selectors:

|Episode|Displayed level|Terrain class|Action|
|---:|---:|---:|---|
|1|7|71|083D:216E, shared one-shot latch|
|1|9|71|If BYTE4198 is zero, set it to 1 and request sound44h|
|1|9|72|If BYTE4198 is nonzero, clear it and request sound44h|
|1|10|71|083D:2198, shared latch and movement freeze|
|1|10|72|083D:21E8, separate one-shot latch|
|2|10|71|083D:221C|
|3|1|71|083D:2236|
|3|10|71|083D:2202|

Other combinations return without these effects. Controlled arguments include nonzero upper bytes, invalid episodes, wrapped level inputs, class68, class255 and initial latch values 0/1/255. Stateful sequences distinguish repeated one-shot calls from the reversible level9 toggle. In particular, this dispatcher does not process class68. The six MAP.3 top-border class68 cells from the prior audit therefore do not gain a transition/bounds explanation from this dispatcher.

### Latch handlers and exact ordering

All handlers except 21E8 test shared BYTE430A. Any nonzero value suppresses their actions. Handler21E8 instead tests BYTE430B. Reset and lifetime of these latches across level changes remain open.

* 216E: if430A=0, call original sound-event42 wrapper; set430A=1 and430E=1; call original bank selector2830; call screen dependency0BDE:018A; pass DWORD pointer DS:0E62 to text dependency0D29:0750.
* 2198: if430A=0, request original sound12h; set430A,430C and4154 to1; clear4151; pass three DWORD pointers from0F74,0FC8 and0FFA to the text dependency, in that order. BYTE4154 is the freeze byte consumed by the original movement wrapper. This proves the write/caller relationship, not the natural scheduling or duration of the freeze.
* 21E8: if430B=0, set430B=1 and pass pointer103C to text.
* 2202,221C,2236: if430A=0, set it to1 and pass pointer10B8,11A2 or135A respectively.

Each sound request passes (event WORD, DWORD00020000h), represented as WORD arguments(event,0,2). Original sound priority dispatcher executes with BYTE414E=0, so the tested path does not invoke a backend. Sound-event42 at083D:0EA0 is executed as original code, not replaced with a response stub.

### Original bank selector: 083D:2830

If430E is nonzero, write WORD6278=6 and BYTE627A=BYTE627B=0. Otherwise read signed WORDs3CBC/3CBE/3CC0. A negative input gives defaults2/2/7; a nonnegative input gives the full WORD for6278 and its low BYTE for627A/B. Nonnegative values larger than255 are truncated for the BYTE destinations. The final driver call0156:016E remains a preserving RETF fixture. Its actual resource and audio effects are not inferred from these scalar writes.

Special-terrain cases: 3,240 dispatcher, 480 bank-selector, 384 joined paired-cell, 72 direct handler, 24 stateful sequence and 4 sound-wrapper contexts. All177 new starts execute. Text/screen/driver return fixtures preserve registers and memory; their real behavior must be verified separately.

## Pickup record lookup and removal

### Lookup: 0AEA:06A8

Input is FAR cell pointer atBP+6/+8. Records begin at relocated fixed segment21FDh, offset0006h, with stride001Ch (28 bytes). Initial signed count is read atDS:6270. If count<=0, return DX:AX=0 without switching DS. With a positive count, comparisons require record WORD+0C equal cell offset, WORD+0E equal cell segment, and record BYTE+0 equal the current cell object BYTE atcell+1. The first matching record returns its FAR address inDX:AX. A miss returns zero. The loop does not test record bit0 or any other activity flag.

For positive counts, DS is restored to SS on either hit or miss; subsequent count comparisons explicitly use SS:6270. Thus split DS/SS callers can observe a segment change. Tests cover first/last match, wrong offset, wrong segment, wrong identity, negative/zero/one/three counts and split contexts. Capacity and malformed/aliased record arrays remain outside this bounded contract.

### Clear: 0AEA:0702

Inputs are FAR cell and FAR record pointers. It writes cell object BYTE+1=0, then clears only bit0 of record BYTE+5 with AND FEh. Other bits are retained. The semantic name of bit0 is not assumed solely from this clear. The helper does not decrement count6270 or compact the array.

### Dispatcher: 0AEA:0718

The function first calls the original lookup. A null result returns without effects. Otherwise it obtains kind BYTE+6 and subtype BYTE+1 from the found record. Default removal flag starts as1. Kind47..61 selects fifteen NEAR targets through CS:[BX+0756h] after subtracting47, unsigned checking<=14 and doubling the index. Outside that range, execution reaches default removal. The exact table is image[B5F6,B614), 15 WORDs/30 bytes, with all targets inside the original decoded function.

|Kind|Original local effect|Acceptance / following selector|
|---:|---|---|
|47|OR BYTE4192 with low BYTE of1<<(subtype&31)|HUD-like selector13|
|48|OR BYTE4193 with the same bit|Selector14|
|49|Add200 to DWORD4182, modulo2^32|Selector4|
|50|If signed BYTE418E<99, add the bit to BYTE418E|Accepted only when precondition holds; selector11|
|51|If unsigned BYTE4189<100, add low BYTE of20 SAR(subtype&31)|Accepted only when precondition holds; selectors5,4|
|52|If unsigned BYTE4189<100, add30 there and250 to DWORD4182|Accepted only when precondition holds; selectors5,4|
|53|Set BYTE4189 and418C to100; add500 to DWORD4182; increment BYTE418A|Selectors5,8,6,4|
|54|OR BYTE4194 with the bit; call083D:0CAC(subtype), then083D:0BA6(subtype,1)|Selector12|
|55|OR BYTE4195 with the bit|Selector15|
|56|If signed BYTE418D<100, add20 there|Accepted only when precondition holds; selector10|
|57|Call083D:0BA6(subtype,0)|Its returned AL becomes removal flag;0 rejects, any nonzero accepts|
|58|If unsigned BYTE41AE<100, add20 there|Accepted only when precondition holds; selector19|
|59|If unsigned BYTE41AF<100, add20 there|Accepted only when precondition holds; selector20|
|60|OR BYTE41B1 with the bit|No HUD-like selector in this branch|
|61|Call083D:2804(subtype)|Default removal remains enabled|

All BYTE/DWORD operations wrap at their original widths. Preconditions test the old value; these paths do not generally clamp the result to100. Values128..255 differ between signed and unsigned checks. Shift counts use386 masking to five bits; a BYTE mask becomes zero for masked counts8..31. These are instruction-level facts for controlled inputs. Natural subtype/stat domains and item names require further caller/asset/runtime evidence.

If removal flag is nonzero, call original clear with both FAR pointers, then reload record kind BYTE+6 and call083D:1A7E(kind). That notification remains a fixture. Weapon-like and special-item callback names are aliases only; full behavior and UI mapping are not closed here. Their fixture inputs and reply domains are explicit. The0BA6 reply AL is exercised at0,1 and255, so it is not assigned a whole-AX Boolean contract.

## Original collision integration

The 720 pickup integration contexts execute original paired-cell collision, original record lookup, the complete original pickup body and original clear. Both collision arguments point to the same controlled cell, exercising two pickup calls after both object flags have already been loaded. An accepted first pickup clears the cell; the second lookup then misses its original nonzero record identity. Repeated direct pickup contexts independently check that behavior.

Objectflag4 alone allows the supplied unit delta to be returned. Objectflags6 (4+2) still reject the step even after the pickup removes the object, because the paired-cell routine retains the pre-callback flags. This does not predict effects of an unmodeled lower item callback that changes other world state. The special-terrain integration likewise replaces its upper trigger fixture while retaining the declared final text/screen/driver responses.

Pickup cases: 3,272 direct dispatcher, 720 paired-cell integration, 80 lookup, 28 repeated pickup and16 clear contexts. All236 new starts execute. Full2MiB RAM except152control-stack bytes, exact non-stack writes, call arguments and frames match. Original lookup/clear register contracts are retained. HUD-like083D:05D2, callbacks0CAC/0BA6/2804 andnotification1A7E remain fixtures. No natural gameplay or enabled-audio run is counted.

## Data catalog and independent verification

Seven new record/cell field roles are cataloged: record offsets0,1,5,6,0C,0E and map-cell offset1. They describe consumed widths and operations, not a fully known28-byte record format. verify_pickup_table_fields.py independently binds original jump instruction, bounds check, table bytes andtargets to decoded starts. The30table bytes are PARTIAL and outside the original57,295-byte NON-CODE set. Original NON-CODE statuses and interval hashes remain unchanged. No additional BSS extent or native capture is claimed.

## Cross-version verification

Eight DOS versions produce96bounded bodies. All96CFGs match, including fifteen table edges per pickup dispatcher. Eighty-seven normalized bodies match DOS2 bytes. The40 retained differences comprise26HUD-like selector immediates (13each inDOS1.0/1.1, one higher thanDOS2) and14record-lookup layout bindings (fixed recordsegment andexplicit SS count address in seven older versions). The normalized comparisons mask stated global/table/call bindings; they do not prove matching lower callback implementations or assets. Win16 counterpart analysis remains open. NoPE32 work is performed.

## Reproduction and outputs

Run audit_replay_special_terrain.py and audit_replay_pickup.py with IMAGE INVENTORY DECODER EMULATOR OUT. Each writes exact per-function instruction CSVs,CFG_edges,execution_coverage,cases,calls,stores andsource-hash summary. Pickup additionally writes data_intervals andpickup_jump_table. Run verify_pickup_table_fields.py OUTPUTS DECODER. Run audit_terrain_pickup_versions.py VERSION_ROOT DECODER OUT for the96body comparison. Rebuild central instructions, both dependent reference censuses andCRTfar-malloc metadata before the full catalog check. Cases and large generated tables may be omitted from GitHub transport with hashes;the pinned scripts regenerate them locally. Original EXE andRAM captures are not republished.

## Coverage update: 13 areas

Previous207functions/9601starts/24364codeB/59653typedfiledataB/1119761controlledcases/41native/BSS5200B. New219functions/10014starts/25524codeB/59683typedfiledataB/1128081controlledcases/41native/BSS5200B. The delta is12functions/413starts/1160codeB,30table bytes and8320controlled contexts. Record-role rows159->166. Campaign UNKNOWN_CONTENT87343->86153 by1160codeB+30dataB,all outside the historical NON-CODE baseline. Distinct existing dependencies andold cases are not counted again.

Original PASS320 remains892intervals/57295B=57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED,with mapSHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. These are distinct-byte andenumerated-test measurements. No new area-semantic percentage is assigned without a complete denominator.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|Special-cell dispatcher consumes classes71/72;class68 border cells use another path|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|30B CS jump table outside NONCODE;7 record/cell roles;no NONCODE promotions|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|15 bounded CS targets;record lookup checks FAR pointer andidentity BYTE|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|12 new bodies1160codeB/413starts;8320 controlled contexts|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|Episode1/level10 handler writes freeze4154=1;shared latches430A/B|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|Original selector8 byte-plane clear dependency path;not whole dispatcher closure|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|Original pickup andspecial-cell writes closed under fixtures;global load/teleport invariant open|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|96DOS bodies:87normalized matches,96CFG matches;Win16 counterparts open|PARTIAL; lower UI/text/driver callbacks,transition domains,mutable state and full semantic denominator incomplete|Locate Win16 resource-reader and driver counterparts|

All13areas remain PARTIAL. Historical percentages remain orientation estimates;new percentages areN/A. Static and controlled instruction evidence is distinct from a natural runtime witness.

## Required next runtime tests

Capture actual lower text/screen/driver andHUD-like/item/notification callbacks,including record removal andpreloaded collision flags. Trace class68/variant state4188 andthe scheduler/transition callers to explain the six MAP.3 border cells;classes71/72 do not explain them. Capture shared-latch reset430A/B/C/E,freeze4154 lifetime,andlevel9toggle4198 during normal play. Establish native item subtype/stat/count domains andrecord ordering,including accepted versus rejected pickup callbacks. Continue natural-angle domains,UNKNOWN2770E/F andCLASSIFIED ONLY28EF7 watches,SAVELOAD/teleports/endsequence+704,remaining unknown intervals,Win16/projectiles/bosses/renderer/RNG/DEMO. NoPE32.
