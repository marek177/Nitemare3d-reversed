from pathlib import Path
import json
r=Path('outputs');s=json.loads((r/'campaign_catalog/summary.json').read_text());old=(r/'MAP_BOUNDS_POSITION_COMMIT_REPORT.md').read_text(encoding='utf-8');table=old[old.index('|Area|Previous orientation|'):old.index('\nAll13areas remain')];repl={'31level slots/7812border cells/31interior spawn markers;6kind44border exceptions':'7688 original paired-cell border cases:7682 reject,6top kind44 cells admit unit delta','19field roles;36additional BSSbytes bound to existing native snapshot':'No new typed bytes;negative-angle WORD read includes CLASSIFIED ONLY28EF7','Original cursor tables andfixedrecord cellFAR;new2770E lookup consumer':'Two27-unit corner probes;original collision reads UNKNOWN2770E/F under synthetic open boundary','Four new bodies668B/233starts;two existing kindhelpers reused':'Four new bodies933codeB/359starts;12558controlled contexts','Caller requestingY+704 observed statically;its scheduling/bounds remain open':'Freeze BYTE4154 short-circuits movement wrapper;transition scheduling stillopen','48DOS comparisons,38normalized/45CFGmatches;64separate cache cases,Win16open':'32DOS bodies:25normalized matches,32CFG matches;56differences only fixedsegment pushes','ordinary collision/caller bounds,mutable state':'trigger/pickup bodies,transition/caller domains,mutable state','Global position invariant still requires load/teleport/collision paths':'Collision resolver closed under stated fixtures;global load/teleport/transition invariant open'}
for a,b in repl.items():table=table.replace(a,b)
text='''# Player movement, collision and conditional NON-CODE consumers

## Evidence boundary

Four original DOS2 bodies are reconstructed and executed against an independent model. This closes their tested instruction/CFG contracts,not whole-game movement safety. Trigger083D:2250,pickup0AEA:0718 andlateHUD083D:05D2 remain preserving RETF fixtures. Original sound dispatcher executes with DS414E=0;door lookup/state helpers,trig functions,position commit,cursors andkind44 helpers are original code. No new nativeDOSBox session or DEEP VERIFIED byte is claimed.

## Exact function catalog

|Function|CS:IP half-open range|Image half-open range|Code bytes / starts|
|---|---|---|---:|
|paired_cell_step|0637:0008..0117|[6378,6487)|270/95|
|movement_resolve|0637:0118..02C6|[6488,6636)|426/169|
|player_heading_prepare|0C7D:0068..0127|[C838,C8F7)|191/76|
|player_move_wrapper|0637:05A4..05D2|[6914,6942)|46/19|

The933codeB/359starts match reproduced image and provided inventory byte-for-byte with independent iced-x86 decoding. Unreached bytes inside function spans are not silently counted as code or proven padding. Every newly retained start executes in the controlled matrix. Existing dependencies keep their prior function ownership.

## Paired-cell contract and ordering

FAR args atBP+6/+A designate two cells;BP+E is signed-unit-compatible WORD delta,not a Boolean. Both terrain BYTEs are read first. Either terrainflag4 calls original disabled sound(1,0,0) andreturns0;bit2 is not required. Each terrainflag8 invokes original doorlookup andpredicate accepting states0or4. A missingdoor stops at original fatal entry;it is not forced to return. Failed doorstate yields sound+0. Doorlookup restoresDS=SS,which affects subsequent classifications in split-context tests.

Then each terrainflag40h calls the unresolved trigger with terraintype LOWBYTE;upperAH is volatile. Both object BYTEs andflags are read before pickup callbacks. Objectflag4 calls pickup(FARcell);objectflag2 rejects movement after pickup callbacks. Otherwise AX is the original supplied delta WORD,includingFFFFh. Terrain-trigger/pickup fixture effects on real level state are not modeled away as a whole-game guarantee.

## Unit-step resolver pseudocode

Two probes use perpendicular offsets +/-27fine units;the proposed moving axis uses28=27+1. Actual FAR argument order is minus-perpendicular first,plus second because of stack push order. Coordinates and pointer offsets wrap16bits.

```text
outX = playerFineX; outY = playerFineY
sx = signed(angle) < 180 ? +1 : -1
sy = 90 < signed(angle) < 270 ? +1 : -1
major = BYTE[4172]
if LOWBYTE(axisToggle) != 0: major = (major < 1)
repeat max(0, signed(steps)) times:
    attempt major axis with original paired_cell_step(delta=+1 or -1)
    add returned WORD to that output coordinate,including zero
    if signed(WORD[4174]) < 0:
        WORD[4174] += WORD[4176]
    else:
        WORD[4174] += WORD[4178]
        attempt the other axis and add returned delta
```

X probe addresses use mapbase373Eh+2*tile(X+28*sx)+128*tile(Y-/+27*sy). Y probes use373Eh+128*tile(Y+28*sy)+2*tile(X-/+27*sx). Tile uses signedSAR6,with equivalent original low-byte masks/SAR5/doubling arithmetic. Segment is relocated fixed21FDh. Error and steps advance even when a movement axis is rejected;there is no wall break or coordinate clamp. Toggle changes localmajor without recomputing error increments. Near output pointers require valid DS storage;the ordinary wrapper passes SS-local addresses and is tested with DS=SS.

Wrapper returns immediately if BYTE4154!=0. Otherwise it calls resolver with locals atBP-4/-2,then original position commit with resulting fineXY. Original commit/cursor/selector8 behavior is reused from the prior batch;not newly counted. Changed-tile lateHUD remains explicit fixture.

## Heading preparation and out-of-domain read

Heading setter stores rawWORD4156,adds360once if negative,then subtracts360once if >=360. This is not a full modulo for all WORD inputs. It stores signedquotient(angle/45) at4158;415C=((1<<(quotient&31))&FFFF)&99h. For415A,it divides signed16(2*angle) by45,truncating towardzero, increments ALonly,anduses(AX&0Eh)>>1.

Original sin/cos scale1024 results go to41B2/41B4. With a=abs16(sin),b=abs16(cos),majorWORD4172=(b<a). Major1 sets error=2b-a,incNeg=2b,incPos=2(b-a);major0 sets error=2a-b,incNeg=2a,incPos=2(a-b),all WORDwrapped. Angles0..359 and boundary inputs-360,-1,360,719,720 are exercised. Raw-361 normalizes only to-1. Original sine MOV AX,[SI+17E8] atimageCFC2 usesSI=FFFEh andreadsDS17E6..17E7,not the sine table beginning17E8.

DS17E6/image28EF6 is the already-PARTIAL soundpriority BYTE;adjacent28EF7 remains CLASSIFIED ONLY. Sixteen pre/postAX WORD observations across two load bases,DS=SS/split contexts and4seeded neighbor combinations establish a conditional consumer. They do not establish intended WORD data type or naturalnegative-heading reachability.

## Border geometry and conditional UNKNOWN reads

With immutable/coherent all-solid border terrain,valid starting fine coordinates91..4004 inboth axes andunit steps imply a useful conditional margin:outward probe atlower91 becomes63(tile0);atupper4004 becomes4032(tile63). Orthogonal +/-27 remains64..4031. Thus the outward step is rejected before the center leaves that margin. This lemma requires solid borders and benign/correct callbacks anddoes not prove all natural states satisfy its hypotheses.

The real31levelslots include six nonsolid top border cells inMAP.3,zero-basedlevel2,X34..39.7688 original paired-cell calls test allnoncorner border cells:7682return0 andsix returnFFFFh(outwardN delta). No trigger/pickup/HUD fixtures execute in those cases. Twelve original resolver contexts atthose six cells/two loads move synthetic fineY91->90;no claim that a real player can reach or survive this state before atransition is made.

Synthetic flat-open boundary case starts fine(4068,4064),angle90,8steps. Original paired-cell loads reach UNKNOWN image2770E/F:32terrain and32object observations. These do not use the shipped solid right border. verify_movement_conditional_reads.py independently binds source MOVs,nextPCs,originaladdresses,load relocation,case domain andloaded values to unchanged ledger membership. Four new consumer PCs are6387/6396(terrain),6421/6431(object). Original UNKNOWN union remains2bytes,now with additional conditional consumers;neither is padding-verified.

## Verification and cross-version limits

12558contexts:1476heading,2020collision,7688asset-border,1134resolver,240wrapper.12554return and4stop at original fatal entry. Full2MiB memory outside184control-stack bytes,exact ordered nonstack stores,calls,cell loads,loaded registers,frames andretained register contracts match. All359newstarts execute. Fixtures are confined to trigger/pickup/HUD returns;not a substitute for full nativegame behavior. Two load bases are0824/1000;heading/collision include DS!=SS,joined resolver/wrapper use DS=SS.

Eight DOS versions yield32bounded bodies with32matching CFGs and25normalized byte matches. All56remaining normalized differences are eight fixed record-segment PUSH immediates in each ofseven older movement resolvers. These are relocation/layout differences;masked call targets andglobaladdresses mean byte-normalization does not prove allcallee orbehavioral parity. Win16 counterpart remains open. No PE32 port.

Existing independently verified native DGROUP snapshot has heading0,sin0,cos1024,major0,error-1024,incNeg0,incPos-2048,consistent with the reconstructed zeroheading formula. This is corroboration from an existing capture,not a new runtime test or new BSS ownership. The supplied runtimeZIP is readable andincludes a Linux DOSBox-X build;availability metadata records archive identity without counting execution.

## Reproduction

Run audit_replay_player_movement_collision.py with IMAGE INVENTORY DECODER EMULATOR GAME OUT as documented in its header. Outputs include exact instruction CSVs,CFG_edges,execution_coverage,cases,collision_calls,cell_reads,conditional_NONCODE_loads andhash-pinned summary. Run verify_movement_conditional_reads.py OUTPUTS DECODER and audit_player_movement_versions.py VERSION_ROOT DECODER OUT. Rebuild the central instruction catalog,then both CRTretry/playerposition reference censuses andthe dependent far-malloc field metadata before full catalog verification. SourceEXE/rawRAM are not published.

## Coverage update: 13 areas

Previous203functions/9242starts/23431codeB/59653typedfiledataB/1107203controlledcases/41native/BSS5200B. New207functions/9601starts/24364codeB/59653typedfiledataB/1119761controlledcases/41native/BSS5200B. Campaign UNKNOWN_CONTENT88276->87343 solely by933newcodeB. Record-role count159unchanged. NoNONCODEstatus,typebyte orDEEPpromotion.

Original PASS320892intervals/57295B=57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED;mapSHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. Counts are measured distinct bytes/starts or enumerated contexts,not area-semantic percentages. No complete area denominator is available.

'''+table+'''
All13areas remain PARTIAL. Historical percentages are orientation only;new semantic percentages remainN/A. Finite instruction/asset coverage does not imply complete game behavior.

## Required next runtime tests

Trace original trigger083D:2250 andpickup0AEA:0718,including the six MAP.3 top-border cells,checking actualtransition timing,position andwhether further probes execute. Trace wrapper0637:05A4/resolver0118/commit051C inDOSBox-X andwatch2770E/F. Establish actual angle-writer domains before excludingnegative sine indices;watch28EF7 loads duringnaturalinput/DEMO/SAVELOAD. Replace lateHUDfixture with originalconsumer orcapture. Continue portal/endsequence +704 caller,SAVELOAD/teleportposition setters,remaining26UNKNOWN/149CLASSIFIED ONLYbytes,Win16/projectiles/bosses/renderer/RNG/DEMO. NoPE32.
'''
(r/'PLAYER_MOVEMENT_COLLISION_REPORT.md').write_text(text,encoding='utf-8')
assert s['functions']==207 and s['independent_instruction_count']==9601 and s['independent_instruction_bytes']==24364
print({k:s.get(k) for k in ('functions','independent_instruction_count','independent_instruction_bytes','controlled_instruction_replay_cases','runtime_tests')})
