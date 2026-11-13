# Map bounds, position commit and an additional UNKNOWN-tail consumer

## What is proved and what remains open

The provided31level slots contain one player-start marker each,all interior. This does not establish a permanent player-coordinate invariant. The original position commit writes supplied WORD coordinates and derives tiles with signed SAR6;its near/far helpers update ordered cursors rather than replacing those coordinates. A separate source-to-cell lookup then reads the terrain BYTE. Controlled tile(64,63) commits produce96 original loads of UNKNOWN image2770E,including72paths with no executed HUD fixture. Original2770F receives no additional consumer in this batch. Neither byte is promoted:the observations still start from synthetic out-of-grid state/arguments,not a natural movement witness.

Ordinary movement resolver0637:0118,portal/action callers,load/recovery and scheduling remain necessary before global bounds can be claimed. A provided-inventory caller083D:2512 conditionally requests playerY+02C0h(704fine units/11tiles);its calling state and whether visibility continues afterward remain unclosed. No inference of a naturally reachable map-tail read follows from that constant alone.

## Exact asset audit

MAP.1/2/3 hashes match the prior asset manifest. Header is WORD levelcount,256terrain-class BYTEs,256object-class BYTEs,then8192B per64x64two-BYTE level. New map_bounds_assets CSVs enumerate every one of7812border cells,31start cells,level payload boundaries/hashes and exceptions. They reuse the independently verified classification-producer low7 truth table;uninitialized inherited bit80 is irrelevant to consumed bits2/4/8.

7806border cells immediately block the original ray via terrain bits2+4. Six exceptions are MAP.3,zero-basedlevel2,top rowY0,X34..39,file terrain offsets16966,16968,16970,16972,16974,16976. Each terrainBYTE193 maps toclass68(44h),whose low7flags0 do not immediately block or require a door query. This is a precise terrain-flag fact,not proof of open movement,absence of object obstacles,or a broken boundary. Class44 has a separate variant/transition-related consumer;complete transition behavior remains open.

All31asset start markers map toobject class2 and satisfy1<=x,y<=62. Original0AEA:0958 contains a64x64spawn scan writing centers32+64*x/y and requiring one match before returning normally. This scan code and the exact asset markers support initialization bounds under matching header/grid and callee assumptions;the whole180-instruction initializer and all callbacks are not newly closed here. Level slots are counted,not asserted to be31distinct payloads.

## Four newly cataloged functions and reused dependencies

DOS2 reproduced image SHA256e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Every instruction independently matches original inventory bytes.

|New function|Exact range|Code bytes / starts|
|---|---|---:|
|player_near_geometry_cursors|0637:02C6..03FD,image[6636,676D)|311/102|
|player_far_actor_cursors|0637:03FE..04B4,image[676E,6824)|181/62|
|player_position_commit|0637:051C..05A3,image[688C,6913)|135/52|
|player_position_reindex|0637:05D2..05FB,image[6942,696B)|41/17|

Total668newcodeB/233starts. One span BYTE outside the discovered far-cursor CFG is not newly promoted to code or proven universally unused padding. Existing class_primary_search00F7:0004 andclass44_relative_id00F7:0176 remain under their prior ownership;their136B/57starts are not counted as new functions/code. New aliases terrain_kind_search/terrain_kind44_variant identify reuse in this harness. Prior4608helper cases are not counted again. Two reused postfatal starts image0FBB/0FBC remain unexecuted here;fatal handlers are not forced to return.

The original083D:143C selector8 dependency path is also executed. Its22instruction CSV is integration-only evidence,not closure of the whole320-instruction dispatcher or an extra catalog function. It clears BYTE ES:[oldTileX*64+oldTileY] through segmentDS:2564,then returns. The byte plane's broader gameplay meaning is not inferred.

## Cursor algorithms, commit order and return contracts

Near helpers update four WORD cursors4166/4168/416A/416C against counts57FA/57FC/57FE/5800 and near pointer tables5800/5A9A/5D34/5FCE. Far helper updates416E/4170 against shared countD514 and FAR pointer tablesD512/DA8A. Record thresholds are WORD+0Ch/+0Eh for near records and+10h/+12h for far actors. On decreasing coordinate,while cursor>0 and current threshold>new,the cursor decrements. On increasing coordinate,while cursor<count and next threshold<new,it increments. Equal coordinates skip updates;equal thresholds stop. Comparisons are signed. The tested model assumes sorted valid tables and0..count cursor inputs;full capacities,malformed counters and aliased storage remain open.

Commit receives fineX/Y WORDs atBP+6/+8 and keeps them inDI/SI. After selector8 and both original cursor helpers,it stores those exact WORDs toDS:4162/4164. SAR6 produces tile WORDs;when changed,it storesDS:415E/4160 and calls083D:05D2 with selector16h(22) inDOS2. This late HUD-like dependency is a preserving RETF fixture in these cases. Stores before that call are original instructions;the fixture's missing global effects are not assumed harmless in actual gameplay.

The map FAR pointer atDS:417C/417E is offset=(373Eh+2*(tileY*64+tileX))mod65536,segment=relocated fixed21FDh. This is distinct from a general mutable map-segment read. Existing class44 helper then examines terrainBYTE;only AX!=FFFFh causes AL toreplace BYTE DS:4188. Nonmarker cells retain the previous variant BYTE. The setter/cursor code does not supply a whole-program boundary guarantee:callers may have validated coordinates,or other routines may alter state afterward.

Reindex05D2 saves current fine coordinates,zeroes DWORDs4162,416A,4166,416E in that order,then calls original commit with the saved values. It rebuilds position/cursor state;it does not simply leave the player atfine(0,0). FAR frames,SP+4,BP/SI/DI/DS/SS preservation are checked. Cursor-only volatileAX/ES/flags are not assigned Boolean contracts.

## Additional conditional UNKNOWN2770E reads

Original00F7:0196 image1106,bytes268A1F,MOV BL,ES:[BX],now has96pre/post-load observations at canonical2770E;nextPC0199/image1109 verifiesBL. ES=load+21FDh,BX=573Eh. Cases commit/reindex supplied fine coordinates deriving tile64/63;loaded values include original00 and explicitly seeded193/201.72observations occur without executing the HUD fixture,butbegin from controlled invalid-coordinate state. They therefore strengthen the conditional consumer catalog without proving an inside-to-outside natural transition.

verify_unknown_position_tail_reads.py independently binds raw MOV,ES/BX/linear addresses,source case/coordinate derivation,loadedBL and UNKNOWN interval membership. pass1_map_tail_position_refs contains CSV/JSON and independent_verification.json. This adds a second terrain-consumer PC to the earlier ray observations,not a third distinct UNKNOWN byte. Original map bounds/status/hash are unchanged;intended padding/type remains unknown.

## Verification, finite writer census and existing native fields

1308deduplicated contexts pass:252near-cursor,252far-cursor,264commit,120reindex,224search and196variant contexts. Of these1212return and96stop at original fatal entry. Reset unused coordinate parameters are normalized before deduplication. All233new starts execute. The two existing helper functions are reused for joined full-memory/error contracts. All2MiB RAM outside184control-stack bytes,exact ordered original stores,callee frames and tested register postconditions match. Fatal search cases stop at0FBA:000C with message argumentDAh;no forced return. The only response fixture is lateHUD on changed-tile paths.

The decoded union census35813unique starts finds7fixed-DS writer instructions touching the four positionWORDs:0637:0545/0549/0560/0564,0637:05DF(DWORD zero of fineXY),0AEA:0B27/0B31(initialization). References are conditional on actualDS being DGROUP. Indexed/bulk/alias writes,omitted code and external restores are not closed;this is not an all-writers or invariant proof. The ordinary collision resolver and other caller control states remain explicit next work.

Nineteen field roles include2already-PARTIAL file bytes atDS012A and36additional BSS scalar bytes. Native values are rebound from existing independently verified dosbox_guard_orientation_runtime_v2/dgroup_final.bin,not a new runtime session or new setter-writer PC capture. The sample has tile22/56,fine1440/3616,pointer2A21:536A,episode cache1 andclass44base186,matching MAP.1's start/header. Native cursors lie within their captured counts;near counts148/144/152/148 andfar count222 do not prove global maximum capacities. Source snapshot hashes/provenance are verified before extraction. Each new BSS interval is PARTIAL and nonoverlapping with prior catalog rows;original NONCODE contribution0.

## Cross-version differences retained

48bounded bodies across8DOS labels(4new+2reused perversion) yield38normalizedcode matches and45CFG matches. Semantic immediates are retained:position commit passes selector7 to the earlier dependency inDOS10..19 versus8 inDOS20;lateHUD selector17h(23) inDOS10/11 versus16h(22) later. Meaning of the earlier dependency's selector is not assumed fromDOS20's selector8 path.

Class44 local-cache code differs: DOS10/11/12 test only cachedBYTE==0;DOS15/17/18/19/20 compare cached episodeWORD tocurrent episode and refresh the base on change.64separate cross-version original-helper/search scenarios pass without fixtures. Retaining base186 while switching to MAP.2's header/current episode2 yields variant6 for type192 in the earlier local helper,versus refreshedbase192/result0 later. With a synthetic validbase0,repeated calls rescan in the earlier sentinel design but not in the later same-episode cache. These are local retained-cache scenarios;other caller invalidation/reset paths and historical asset compatibility are not closed,so no whole-game episode bug is asserted. The64cases remain separate from the canonical campaign case count. Win16 remains unverified.

## Reproduction and artifacts

Run audit_map_bounds_assets.py OUTPUTS GAME_DIR; audit_replay_player_position_commit.py IMAGE INVENTORY DECODER EMULATOR OUT; audit_player_position_versions.py VERSION_ROOT DECODER OUT; audit_replay_kind44_cache_versions.py VERSION_ROOT VERSION_OUTPUT DECODER EMULATOR GAME_DIR OUT; audit_player_position_references.py IMAGE INVENTORY CENTRAL_CSV DECODER OUT; verify_unknown_position_tail_reads.py OUTPUTS DECODER; prepare_player_position_fields.py. Outputs include full border/start/level CSVs,ASM/CFG,original store/frame cases,conditional byte CSV/JSON,version/cache differences,writer census andnative-bound BSS field catalog. Input,script andcapture hashes are pinned. Original binaries/raw RAM remain local.

## Coverage update: 13 areas

Previous199functions/9009starts/22763codeB/59653typeddataB/1105895controlled cases/41native/BSS5164B. New203functions/9242starts/23431codeB/59653typeddataB/1107203controlled cases/41native/BSS5200B. Add4functions/668codeB/233starts and1308contexts;reused136B/57starts andselector8integration path do not inflate function ownership.64version cases and7812asset-border records are separate measurements. Record-role rows140to159. Campaign UNKNOWN_CONTENT88944to88276 by newly owned code only. Existing UNKNOWN-byte union with controlled read witnesses remains2;new96observations affect2770E only.

Original PASS320 remains892intervals/57295B=57118PARTIAL+149CLASSIFIED ONLY+28UNKNOWN+0DEEP VERIFIED;mapSHA256497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe. No new full-area semantic percentage is calculated without a denominator;historical orientation estimates retained.

|Area|Previous orientation|New % / method|New confirmed findings|Unknowns / blockers|Next step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A; complete semantic denominator absent|31level slots/7812border cells/31interior spawn markers;6kind44border exceptions|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Uncovered map replacement consumers|
|Data types and constants|95%|N/A; complete semantic denominator absent|19field roles;36additional BSSbytes bound to existing native snapshot|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Resolve remaining 149 classified-only and 28 unknown bytes through actual consumers|
|Tables and pointers|93%|N/A; complete semantic denominator absent|Original cursor tables andfixedrecord cellFAR;new2770E lookup consumer|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Trace driver MIDI event consumers and buffer lifetime|
|Functions/ASM/CFG|90%|N/A; complete semantic denominator absent|Four new bodies668B/233starts;two existing kindhelpers reused|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Open fatal/callback bodies and remaining unknown functions|
|RNG|97%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Capture RNG/DEMO ordering|
|Scheduler|96%|N/A; complete semantic denominator absent|Caller requestingY+704 observed statically;its scheduling/bounds remain open|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Capture natural resource replacement timing|
|DEMO/input|96%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Capture actual DEMO playback|
|Renderer/VGA|94%|N/A; complete semantic denominator absent|Original selector8 byte-plane clear dependency path;not whole dispatcher closure|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Exercise clipped draws|
|GUARD/bosses|93%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Uncovered boss/attack transitions|
|Weapons/projectiles|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Original impact/damage lifecycle|
|Sprites/HUD/palette|92%|N/A; complete semantic denominator absent|No new behavior proved in this batch|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Native populated cleanup/refill|
|SAVE/LOAD|92%|N/A; complete semantic denominator absent|Global position invariant still requires load/teleport/collision paths|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Actual LOAD/reset ordering|
|Windows Win16|92%|N/A; complete semantic denominator absent|48DOS comparisons,38normalized/45CFGmatches;64separate cache cases,Win16open|PARTIAL; ordinary collision/caller bounds,mutable state and full semantic denominator incomplete|Locate Win16 resource-reader and driver counterparts|

All13areas remain PARTIAL. Initial asset bounds,cursor mechanics andcommit behavior do not establish the global natural-coordinate invariant required to classify the map tail as unused padding.

## Required next runtime tests

Trace ordinary movement0637:05A4/0118 through commit,including the six MAP.3 boundary-class44cells and any level-transition ordering. Capture pre/post position/cursors/cell pointer/cache inDOSBox-X. Analyze portal/action/end-sequence andSAVE/LOAD writers before asserting0..63always holds. Capture actual class44 cache behavior on episode changes andthe earlier selector7 dependency;observe actualHUD effects. Continue both UNKNOWN map-tail bytes andremaining26UNKNOWN/149CLASSIFIED ONLYbytes,Win16,projectiles/bosses,renderer/RNG/DEMO/SAVELOAD. No PE32 port.
