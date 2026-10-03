# Nitemare3D Win16 — analysis all 40 areas

Date: 24. september 2026. Follow audit registra from file `Nitemare3D_Win16_all_available_versions_audit_2026-09-24.md`.

## Result and range

Passed som all 40 required areas. Each has specific static conclusion or vymedzenú medzeru, source addresses, status evidence, implement consequence and distinguish next test. Analysis priniesla also fix older main referencie. **40 analyzed areas does not mean 40 completely closed subsystem.**

Work som with original EXE 1.3/1.6/1.8/1.10, their C exportmi and provided shareware assetmi 1.3/1.6/1.8. Depth semantic check uses 1.10 as referenciu; cross-version valid is during each finding listed separate. Nemám supported all historical release Windows build nor all their registered package. Was not running original Win16 runtime, therefore tu are not claim o execute framebuffer, audio whether save/load runtime test.

**Confirmed** = directly supported listed static property; **Inferred** = interpretation or consequence; **Unknown** = remain question. **High/Medium** value evidence, nie percent completion. C export is analytical underlying, nie original source code; its segment casty, parametre and boundary needs to check v NE byte.

## Most important new findings

- **DEMO time:** timestamp is render-generation index. Its writer and comparison during play are raw confirmed in all four EXE. Provided file has 203 events; last timestamp 1157 is not automaticky time v ms nor end entire playback.

- **Score:** old table obsahovala incorrect assign class. Priamym read jump table is teraz verify 25 class × 4 build, total 100 values. Classes 12/29/30 give 250; penalizácia −1000 belongs class 21.

- **Contact damage:** difficulty 2 multiplies guard→player damage dvoma, difficulty 0 ho divide dvoma. Main referencia uvádzala repeat; deep audit small this part already correctly.

- **Input:** 0x71/0x72 are F2/F3, 0x73 is F4. C literals q/r/with must not be read as písmenové skratky. Alt+F4 branch posiela WM_CLOSE 0x0010.

- **GUARD and doors:** +0x0D retain underlying object byte map whole v check movement and smrtiacej path; write during smrti nepatrí to OBJECT+1. AI status 9 writes status door 4. Status 0x0AND writes completion animations smrti; status 0x0B sa writes during fatal kontakte guard with player; status 0x13 during strategy 3 has confirmed countdown also during block movement. All four available dispatchery have same 20 explicit vetiev `0x00–0x09, 0x0C–0x15`; complete meaning others state and their writer→handler graf remain open.

- **Weapon and HUD:** cooldown sa can consume also during failed pokuse; HUD executes also clamping state and moves weapon automatic.

- **Save/load:** check loader rebazuje VEC/world OBJECT deadlines, restores current pointer door and recalculate map pointer. Projectile deadline potrebuje separate runtime test.

- **BSF:** differences troch provided package sa after decode concern distributora and environment text block; first and third block are identical. CONFIG has v four check read exactly 20 bytes.

## Identita primary EXE

| Version | Size | SHA-256 |
|---|---:|---|
| 1.3 | 229136 B | `926c0001944b9822cdae10b35c92c2d6cd3772bc774c4c88fb17df7465d1f156` |
| 1.6 | 230128 B | `5851849bacd8b03e93444d8a8f34d51c23fecddc73d6b8df7f016885c3b9d418` |
| 1.8 | 230224 B | `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22` |
| 1.10 | 230400 B | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |


Addresses `3:xxxx` and `4:xxxx` denote NE segment:offset, nie physical file offset nor arbitrary runtime selector. Until is not explicit listed otherwise, addresses v opise finding patria 1.10. Each raw excerpt has v header also SHA-256 and physical offset.

## What was check

- 40 thematic areas and 120 assign reference functions k oblastiam. Jedna function can patriť multiple oblastiam.

- 480 version assign: 120 reference, 210 unique candidates according to normalize C tvaru and 150 candidates search according to okolia and similar. Is **search catalog, nie automatic evidence semantic parity**.

- 424 different version functional okien was extracted as C + disassembly, with supplementary window parsera, CONFIG, MFC and key handlerov. Extrakcia sa nerovná manual verify each instructions. Range confirm determine nasledujúcich 40 records.

- New verification skript passed: 100 score values z raw jump tables; 12 raw check for damage, DEMO and CONFIG; three DEMO files; nine decoded BSF block with check boundaries and XOR headers.

- Register RNG contains v each build 22 syntaktických callsite-ov through game wrapper v 15 C bodies. Is not runtime count odberov.

## Register 40 areas

| # | Area | Main result tohto priechodu |
|---:|---|---|
| 1 | Complete versions | 4 EXE identify; complete historical release open |
| 2 | Functional boundary | Raw parser and CONFIG missing in FUN exporte |
| 3 | MFC, vtable and message maps | Constructor → vptr 3:0792 → specifically sloty |
| 4 | Initialization and termination | Cleanup order and difference program/level reset |
| 5 | Argumenty and debug path | 11 switch; -r launch recording DEMO |
| 6 | Main plan | DEMO zálohuje CONFIG and reset seed/generation |
| 7 | Timing | 8 Hz without dobiehania; arithmetic wrap after 2^29 ms |
| 8 | RNG | RNG is linked also with visible animation |
| 9 | Keyboard and input | Correction F2/F3/Alt+F4 and order súbežných input |
| 10 | Mouse and joystick | Joystick dead-zone ±5; menu uses ±8 |
| 11 | Player movement | Unit axis sondy 27/28, preserve sliding order |
| 12 | Doors and secret panel | Found writer door state 4 |
| 13 | Push objects | Block push does not reduce timer |
| 14 | USE, safe, trunk and radio | Kontajnery frame 0/1/content; radio only E1M9 branch |
| 15 | Teleporty and elevator | Order output N/E/WITH/W and result cardinal uhol |
| 16 | HP, death and obnovenie | Corrected difficulty multiplier; different death stavy |
| 17 | Inventory and pickup | Neprijatý pickup remains; part limitov is v HUD |
| 18 | GUARD arrays | GUARD+0D restores mapCell[1] |
| 19 | GUARD AI | Dispatcher: 20 vetiev 0x00–0x09/0x0C–0x15 in all buildoch; 0x0AND/0x0B without case; confirmed writery 0x0AND/0x0B and eight pokusov stavu 0x13 |
| 20 | Percepcia and sluch | Wake cache without LOS/range; proximity is square |
| 21 | Bossovia and transform | Exact arrays transform and radio state 14 |
| 22 | weapon kadencia | Cooldown sa reset before result shot |
| 23 | Damage and hitscan | Hitscan loop does not have break after prvom successful damage |
| 24 | Projectiles | Impact hold slot; load projectile deadline open |
| 25 | Projection cache | Cache writer is condition; row is not slot-clamp |
| 26 | Fire and hazardy | Fire does not have v this branch difficulty scaling |
| 27 | Special walls | ONE_SHOT and demolácia are difference completion branches |
| 28 | Level triggery | Episode/level/class dispatch and save/reset flagov |
| 29 | IMG and SEQDEF | Jedna anim. frame; RNG retry according to packed alternative |
| 30 | VEC geometria | VEC sa zneaktívňuje flagom without local kompakcie |
| 31 | Projection and clipping | Depth 0x4000, screen X clamp and endpoint swap |
| 32 | wall pixely | Column sampler, U mask, walls without alpha test |
| 33 | Sprity | 100 slotov; bypass reads OBJECT flag |
| 34 | Palette and shade | Blackout prepisuje shade also two fill bytes |
| 35 | HUD and automapa | HUD changes status; power-upy use masky 7/15 |
| 36 | SFX and MIDI | Same SFX priorita can override active sound |
| 37 | USER.SAV | Pointer restore and specific deadline rebasing |
| 38 | CONFIG and BSF | CONFIG 20 B; BSF differences decode |
| 39 | DEMO | Timestamp = generation; EOF remains runtime question |
| 40 | Postup, score and final | 100 score items raw verify; final partial |


## 01. Complete versions

Confirmed are four unique Win16 EXE: 1.3, 1.6, 1.8 and 1.10. Numeric VERSIONINFO 1.0.0.1 their does not distinguish; decide SHA-256 and embedded text versions. Attached shareware data are supported for first three versions. Complete all historical release Windows build is not demonstrated.

**Status:** Confirmed / Unknown. **Confidence:** High for identitu, Unknown for complete. **Range:** 1.3, 1.6, 1.8, 1.10.

**Evidence:** verification40.json → inputs; previous ne_metadata.json and shareware_asset_hashes.csv.

**implement consequence:** Build identify hashom; data package record separate. Do not confuse release game with version Windows 3.10/3.11.

**Remains / next test:** Add missing release and exactly pair data package 1.10; up to then possible say o all release.


## 02. Functional boundary

C register is not complete list machine functions. V 1.10 call 3:0088 vedie on parser 3:1118, which v exporte does not have FUN block. same missing read CONFIG on 3:52AE. Relocation prechod found v 1.10 275 candidate far CALL miest direction on 173 different targets mimo registered start. To is not 173 automatic confirm new functions.

**Status:** Confirmed / Inferred. **Confidence:** High for listed missing bodies; Medium for candidate list. **Range:** all four EXE; specifically addresses tu 1.10.

**Evidence:** far_call_targets_outside_C_registry.csv; v*/command_parser.asm.txt; v*/config_read.asm.txt.

**implement consequence:** C export add o raw entrypointy; targets uprostred tela, thunky and data references lead separate. Linear disassembly switch tables is not code.

**Remains / next test:** Each from 173 targets classify check boundaries instructions and caller/callee; zapojiť near calls, NE entry table and indirect calls.


## 03. MFC, vtable and message maps

Closed jedna specific link: constructor 3:0670 after initialize podobjektov +0x4E and +0x80 writes far vptr on 3:0792. Destruktor 3:06AND0 writes same vptr and calls cleanup. First sloty tables direction on 3:0664, 3:076E and 3:0464; additional through NE relocations on segment 1. Podivné stringové casty v decompile tu represent segment selektory.

**Status:** Confirmed. **Confidence:** High for vptr and addresses; Medium for pomenovanie classes. **Range:** 1.10.

**Evidence:** mfc_vptr_1_10.asm.txt; mfc_vtable_1_10.csv; 3:0670/06AND0 and relocations 3:0792….

**implement consequence:** Vptr model as segment:offset, member +0x4E/+0x80 as separate podobjekty. Original change classes so far do not replace odhadom.

**Remains / next test:** All message-map records decode with size record and napojiť their on specifically callbacky; remain other classes.


## 04. Initialization and termination

Cleanup 3:0F64 calls v order audio E0C4(1), timer D66C(1), message source 4:465C(1) and grafiku 2F36(1). Calls ho destruktor also fatálna error path. Reset level eventov 0EF6 sets 51AND5=1 and others seven bytes 51AND4–51AB on 0. Is other operation than element initialization programu.

**Status:** Confirmed. **Confidence:** Medium–High; priame callsite-y and writes, without test failure device. **Range:** 1.10; older analog v catalog.

**Evidence:** 3:0F64, 06AND0, 0E9E, 0EF6; 4:3118.

**implement consequence:** Separate program init, level reset and cleanup; retain order restore sound and grafiky. Nevynulovať all eventy same value.

**Remains / next test:** Close ownership each allocate and repeated cleanup during partially completion initialize.


## 05. Argumenty and debug cesty

All four raw parsery use second znak tokenu after '-'. Branches b,c,d,e,f,l,o,p,r,with,w are supported table. V 1.10 -b sets 46AE; -d píše shade verify 4698, -f fill 469AND, -c fill 469C; -l loads number and subtracts 1; -o enables logger; -p sets prefix path and znovu reads CONFIG; -r sets DEMO mode=1; -w mask nízke three bits width. During -e and -with is safe so far preserve only exact write to array.

**Status:** Confirmed / Inferred. **Confidence:** High for table and writes; Medium for final meaning some switch. **Range:** raw parser all four; semantic names fields 1.10.

**Evidence:** 3:1118–1295; command_switch_targets.csv; 3:C5E2, 5260; config_read.asm.txt.

**implement consequence:** -r is nahrávacia branch DEMO, nie general cheat. Numeric parametre are additional tokeny; not consider all switches for bezargumentové.

**Remains / next test:** Add final readable 46AND8 and 46AA, exact valid tokenov and behavior during missing call intro file.


## 06. Main plan

D9C6 hold frame branch and slow branch separate. DEMO start DAA0 zálohuje 20-byte CONFIG block, vypína mouse/joystick and selected verify flags, initializes scénu, sets RNG seed 1 and render generation=0. During terminate restores configuration and original level selector. This záloha sama osebe nedokazuje restore entire game sveta.

**Status:** Confirmed. **Confidence:** Medium–High; priama sequence call and write. **Range:** 1.10; correspond DEMO štarty 1.3/1.6/1.8 check.

**Evidence:** 3:D9C6, DAA0; older D87E/D9F2/D9F2; 4:32D8.

**implement consequence:** DEMO startup/teardown implement as separate state prechod with zálohou configuration. Generation reset v same bode as seed.

**Remains / next test:** Original trace during pause, strate fokusu and return z change; determine, which timery sa zachovávajú through each branch.


## 07. Timing

Remains valid raw confirmation 8 Hz slow bucketu and calibration frame timeru. Calculation ((uint32(ms)<<3) mod 2^32)/1000 has own arithmetic prelom every 2^29 ms, approximately 6,21 dňa, still before complete 32-bit wrapom source time. During change bucketu sa adds one step; nor large skok does not invoke dobiehaciu loop.

**Status:** Confirmed / Inferred. **Confidence:** High for instructions; High for derive arithmetic, runtime Unknown. **Range:** 1.3, 1.6, 1.8, 1.10.

**Evidence:** 3:D70AND/D74AND/D7D0 v 1.10; previous verification.json; timing_boundary_model.json.

**implement consequence:** During compatibility model preserve 32-bit arithmetic and distinguish raw calibration priemer from local clampu 40 ms.

**Remains / next test:** Measure timer latenciu and real tempo during overload; separately verify prechod through prelom timeru and DEMO modes.


## 08. RNG

LCG remains state=state*0x343FD+0x269EC3, result (state>>16)&0x7FFF. V each C exporte is 22 syntaktických odberov through game wrapper v 15 bodies. Between call are also animations stien/object and visually effect, nielen AI and damage. CC7C calls CBD4 up to after successful projekcii and add sprite slotu; CBD4 can remove RNG repeated during selection nonempty alternative.

**Status:** Confirmed / Inferred. **Confidence:** High for algoritmus and syntaktické counts; Medium for complete replay model. **Range:** algoritmus and register all four; link projekcie detailne 1.10.

**Evidence:** 2:6EB0/6EC8; 4:32D2/32D8; 3:65AND6, CBD4, CC7C; rng_direct_callers.csv.

**implement consequence:** Deterministická reconstruction potrebuje order odberov including visible animation. Itself seed and AI tick are not enough.

**Remains / next test:** Log each odber with callsite-om during same DEMO and dvoch size viewportu; measure element deviation state.


## 09. Keyboard and input

Corrected incorrectly read C character literals: values 0x71/0x72 are Windows VK_F2/VK_F3 and call prepnutie music/sound; 0x73 with Alt posiela WM_CLOSE 0x0010. Is not Q/R/Alt+WITH. Input 9806 processes mouse, joystick, arrow, shoot and USE v specific order. Right Shift doubles steps; left their later overwrite on 1, so during concurrency has this write prednosť.

**Status:** Confirmed. **Confidence:** High for 1.10 branches, raw VK values and WM_CLOSE; runtime repeated Unknown. **Range:** 1.10; older candidate listed v matici.

**Evidence:** 3:8CD2, 9806, DDB2, DDFC; raw 8E55–8EC5; Microsoft virtual-key-codes / WM_CLOSE.

**implement consequence:** V API layer use virtual codes key, nie ASCII 'q'/'r'. Súbežné input execute v finding order.

**Remains / next test:** Press/hold/pustenie during prepnutí fokusu and change; verify, whether all callbacky clear 3756/3757 also edge latch 012C.


## 10. Mouse and joystick

Joystick v game movement has after normalize inactive interval -5 up to +5 including. For prahom is posun min(abs(axis)-5,2*moveStep); otáčanie min((abs(axis)-5)>>1,4*turnStep). Second button changes horizontálnu os on strafing. Change uses other boundary, ±8, and separate repeated. Mouse uses field appearance on stred and rectangle neaktívnej zóny derived from viewportu, nie this joystickovú boundary.

**Status:** Confirmed. **Confidence:** Medium–High; condition joystickovej branches compare in all four C exportoch. **Range:** joystick 1.3/1.6/1.8/1.10; detail mouse 1.10.

**Evidence:** 3:8F86, 9268, 9392, 963E, 96F6; analog 94D4/9648/9648.

**implement consequence:** Use separate rules for change and gameplay; dead-zone sa uplatňuje on normalize osi, nie directly on raw value driver.

**Remains / next test:** Trace centrovania and range JOYGETDEVCAPS; boundary values -8,-6,-5,5,6,8 and strata zariadenia.


## 11. Player movement

8604 executes unit steps through major/minor os and shared error accumulator. Collision sondy use values 28 and ±27 world jednotiek. Axis movement call 84F4 separate; zablokovanie jednej osi therefore does not have to block second. Subsequent 8AND20 update sort lists, world coordinate, whole and its far pointer. Input dopredu/dozadu sa handle postupne, nie one vector sum.

**Status:** Confirmed / Inferred. **Confidence:** Medium; explicit static branch, exact rohový result without runtime. **Range:** 1.10.

**Evidence:** 3:8604, 84F4, 8AND20, 87B6, 8902, 9806.

**implement consequence:** Preserve integer krokovač and order axis. Numbers 27/28 are not evidence kruhového collidera with one field.

**Remains / next test:** Rohy and diagonal test on whole with door, guard and push object; compare coordinate after each podkroku.


## 12. Doors and secret panel

Added writer state 4: GUARD dispatcher v state 9 after death/object helperi and during corresponding wall-property bit 8 finds paired controller and writes controller+0x0C=4. Door toggle during this state immediately returns and passability helper ho accepts. Previous claim, that writer is not known, is for this path invalidation. Auto-close during zablokovanej whole sets new timer 4.

**Status:** Confirmed / Inferred. **Confidence:** High for write and read; Medium for all game reason state. **Range:** writer v C all four; raw and detail 1.10.

**Evidence:** 3:7B56 case 9 → 1296; 3:1476, 188AND, 1D4E, 1E00.

**implement consequence:** Status 4 retain as zvláštny passable/nezapínateľný status this path. Nezredukovať automatic on ordinary open/closed.

**Remains / next test:** Check save/load with mŕtvym guard during paired door; verify result geometriu and adjacent controllers.


## 13. Push objects

21B6 launch only nečinný slot, copies two directional values and sets timer 8. 2210 decrements timer výlučne v accepted branch: update world coordinate, far pointer map, move object byte and modify sort. If target whole block prechod, timer remains unchanged. Eight update call therefore does not guarantee completion move.

**Status:** Confirmed. **Confidence:** Medium–High; priame read/write branches. **Range:** 1.10; analog extracted for all four.

**Evidence:** 3:21B6, 2210, 133AND, C9AND6.

**implement consequence:** Distinguish count accepted krokov from uplynutého time; blocked move sa repeat. Move map object only during change whole.

**Remains / next test:** Block target guard during movement, save/load and subsequently target free; check timer also old/new map whole.


## 14. USE, safe, trunk and radio

AD9E distinguishes class 0x26/0x27 and frame 0, 1 and higher: safe during 0 opens combination; second class sets frame z variant+2 and hrá SFX 0x32. Frame 1 message empty content; higher frame pass content ABFC and overwrite ho on 1. Radio B010 launch AE56(0) only for episode 1, level index 8. This is specific strážny test, nie general property each rádia.

**Status:** Confirmed. **Confidence:** Medium; priame C branches, UI and all combinations without runtime. **Range:** 1.10.

**Evidence:** 3:1AND22, AD9E, ABFC, B010, AE56.

**implement consequence:** Frame kontajnera is simultaneous its state. After odobratí obsahu preserve value 1; map class do not replace name graphic assetu.

**Remains / next test:** Close callback combinations including cancel, repeated USE and save open kontajnera.


## 15. Teleporty and elevator

2800 searches required wall ID with X as external and Y as internal slučkou. Helper 264AND test adjacent whole v order sever, east, juh, west; reject player current whole and wall/object property bit 2. Success umiestni player to stredu whole and sets uhol according to result: sever→0°, east→90°, juh→180°, west→270°. When nevyhovie nothing, calls C37C without move.

**Status:** Confirmed. **Confidence:** Medium–High; jasné condition v C, without original move. **Range:** 1.10; prenosový helper has identical normalize tvar also v older troch.

**Evidence:** 3:2800, 264AND; 4:1F6AND, 20CE; 3:C126.

**implement consequence:** Preserve deterministickú prioritu output and cardinal facing. Param=0 is no-op. Occupied sa posudzuje property bitom, nie only zero ID.

**Remains / next test:** Test four block susedstvá, viac same target ID and cancel; missing target not consider without test for safely ošetrený.


## 16. HP, death and obnovenie

Correction main referencie: guard→player AND1EA during difficulty=2 škodu doubles, during 0 ju divide dvoma. Raw confirmed in all four EXE. Contact death 8C0AND sets game state 2 and stores index attacker; fire BE62 sets state 3. Loader on conclusion calls B128, which during active verify flagoch can restore HP/ammo/inventory on fixed values.

**Status:** Confirmed. **Confidence:** High for multiplier and state; Medium for all restore combinations. **Range:** multiplier all four; detail restore 1.10.

**Evidence:** verification40.json; 3:AND1EA → AND2AF/AND2C5; 3:8C0AND, BE62, 574C, B128.

**implement consequence:** Nezdieľať one difficulty multiplier for oba direction damage. Load is not always only byte copy store player block.

**Remains / next test:** Round-trip save during active 4BE4/4BE5/4BE6 and comparison smrti kontaktom vs fire.


## 17. Inventory and pickup

CF60 necháva kapacitne rejected pickup on mieste: remove CF4AND is condition success. Health class 0x33 adds 20>>variant only pod 100; class 0x34 adds 30 and 250 point; class 0x35 sets HP also select ammo on 100, adds 500 point and one life. Multiple upper limity sa application up to in call HUD dispatcheri AND3B6, which writes back to state.

**Status:** Confirmed. **Confidence:** Medium–High for static data tok. **Range:** detail 1.10; CF60 has identical normalize tvar v four exportoch.

**Evidence:** 3:CF60, CF4AND, AND9E0, AND3B6.

**implement consequence:** Pickup acceptance and remove separate. During refaktoringu nestratiť clamp only therefore, that sa move or vypne render HUD.

**Remains / next test:** Test during 99/100 HP and takmer full ammo, repeated kontakt, prechod level and znovunačítanie before/after remove.


## 18. GUARD arrays

GUARD+0x0D has v movement and death path specific role zálohy object byte map whole. 71DC v starej whole restores +0x0D, v novej loads original byte to +0x0D and writes ID guard. Death branch 80F8 through OBJECT+0x0C far pointer restores map[1]. Is not to write to OBJECT+1; precede formulácia main referencie was incorrect.

**Status:** Confirmed. **Confidence:** High for raw death store; Medium–High for lifecycle cycle array. **Range:** 1.10; correspond functions older versions v catalog.

**Evidence:** 3:71DC; raw 3:81B9–81C4 v 80F8; GUARD+8 selects OBJECT index.

**implement consequence:** During movement and smrti preserve underlying object whole. Do not confuse GUARD+0x0D with projectile slot+0x0D.

**Remains / next test:** Process other class verify tohto byte and test prechod guard through pickup; range all verify remains open.


## 19. GUARD AI

Status 0x0AND writes AND0EE after animation smrti; class 0x11 and class 0x16 have separate complete branches. Also status 0x0AND does not have own case v AI dispatcheri and v normal update jednotlivého guard sa therefore further does not change.

**New uzavretie for status 0x0B:** in all four Win16 C exportoch is single found writer corresponding state-setter (`FUN_1010_7ED2` in V1.3, `FUN_1010_8046` in V1.6/V1.8 and `FUN_1010_80EA` in V1.10). Each z nich writes `GUARD+0x0B = 0x0B`. Single priamym callerom v each exporte is function obsluhy damage guard player; setter sa calls only in branch, where current HP player are not larger than compute damage. This branch sets HP on nulu, global game state on 2, stores index guard and calls path sound events. Raw disassembly V1.10 confirms order v `3:8C0A`: HP comparison `8C41–8C47`, write HP=0 and game state=2 `8C49–8C54`, save guard index `8C59–8C60` and distance call on `3:80EA` on `8C69`.

Dispatcher does not have `case 0x0B` in V1.3 (`3:793E`), V1.6/V1.8 (`3:7AB2`) nor V1.10 (`3:7B56`). **Confirmed:** status sa writes during fatal kontakte guard and does not have separate AI obsluhu. **Derived:** is final status guard during prechode game to smrti player; visually display guard and entire subsequent priebeh z code itself does not follow.

**Uzavretie set state dispatchera:** all four C exporty have match set 20 explicit vetiev: `0x00–0x09` and `0x0C–0x15`. V range `0x00–0x15` are therefore single values without separate `case` state `0x0A` and `0x0B`. Raw V1.10 dispatcher `3:7B56` reads `GUARD+0x0B`, compares ho with upper boundary `0x15` (`3:7B63–7B70`) and uses jump table. Thereby is closed set dispatchovaných values, nie semantic all dvadsiatich handlerov nor their reach on each map.

**Evidence set vetiev:** `NITE3W13.EXE.c:24255–24485` (`FUN_1010_793E`), `NITE3W16.EXE.c:24359–24589` and `NITE3W18.EXE.c:24363–24593` (`FUN_1010_7AB2`), `nite3w110.exe.c:24376–24606` (`FUN_1010_7B56`); raw `v1.10/FUN_1010_7b56.asm.txt` v evidence ZIPe, with compare state on `3:7B63–7B69` and indirect skokom on `3:7B70`.

**Uzavretie set state dispatchera:** all four C exporty have match set 20 explicit vetiev: `0x00–0x09` and `0x0C–0x15`. V range `0x00–0x15` are therefore single values without separate `case` state `0x0A` and `0x0B`. Raw V1.10 dispatcher `3:7B56` reads `GUARD+0x0B`, compares ho with upper boundary `0x15` and uses jump table; C bodies all versions determine its explicit branches. Thereby is closed set dispatchovaných values, nie semantic all dvadsiatich handlerov nor their reach on each map.

**Confidence:** High for set dispatcher vetiev and static tok state 0x0B and 0x13; Medium for runtime/visible result these vetiev. **Range:** V1.3/V1.6/V1.8/V1.10 static C exporty; raw dispatcher and call death handler V1.10, raw update state 0x13 V1.10.

**Uzavretie movement v state 0x13:** for all four Win16 exporty strategy 3 can from state 7 set status 0x13; its timer initializes on `RNG % 0x50 + 8` and divide loads according to direction. Update helper najprv subtracts timer. When new timer reach 8, sends sound event and nepohybuje sa. During novom timere pod 8 executes candidate movement; to corresponds to exactly ôsmim pokusom during original value 8…1. If target whole neprejde condition occupied or map pointer, helper finish without write X/Y, pointer current whole nor its byte occupied; timer however further klesá. After eight failed pokusoch following update, which enter with original timerom 0, sets `GUARD+0x0A=0`, `GUARD+0x0B=2`.

**Raw evidence V1.10:** `3:7A44` reads and dekrementuje timer `7A50–7A64`; sound branch is `7A6F–7A97`; collision condition is v `7AEC–7B00`; failed branches direction on epilogue `7B4F`, before successful write coordinates and occupancy `7B16–7B4B`. Cross-version C telo has correspond structure in V1.3 `FUN_1010_782C`, V1.6/V1.8 `FUN_1010_79A0` and V1.10 `FUN_1010_7A44`.

**Evidence:** `NITE3W13.EXE.c:24516, 25107, 24204–24250`; `NITE3W16.EXE.c:24618, 25205, 24310–24356`; `NITE3W18.EXE.c:24622, 25209, 24314–24360`; `nite3w110.exe.c:24635, 25226, 24323–24365`; raw `v1.10/FUN_1010_8c0a.asm.txt` (`3:8C41–8C79`) and `v1.10/FUN_1010_7a44.asm.txt` (`3:7A50–7B4B`) v `Nitemare3D_Win16_40_oblasti_evidence_2026-09-24.zip`; dispatchery `FUN_1010_793E`, `FUN_1010_7AB2`, `FUN_1010_7AB2`, `FUN_1010_7B56`.

**implement consequence:** For all four Win16 build distinguish animation smrti v state 9 → 0x0AND, fatal guard kontakt → 0x0B and movement branch strategy 3 status 7 → 0x13 → 2. During status 0x13 neobnovovať timer after block cieli; field/occupied change only during successful prechode collision condition.

**Remains / next test:** Complete status × strategy × class table, semantic larger handlerov, other links write → user and natural reach remain open. Runtime test for 0x0AND, 0x0B and 0x13 handle visible frame, sound and exact map context; their static supported prechody are described above.


## 20. Percepcia and sluch

Wake 7664 skips selector 0. During element nonzero selectore marks cache still before skenom and activation only strategy=0, same area selector and status 7/8; timer sets rand()%8. V this branch is not distance nor LOS. Perception wrapper 7594 separate save LOS and near; near is square test abs(dx)<=64 and abs(dy)<=64.

**Status:** Confirmed. **Confidence:** Medium–High; priame filtre and read/write string. **Range:** 1.10; wake analog v four exportoch.

**Evidence:** 3:7664, 7494, 7594; cache AND65E; GUARD+0x0E/+0x17/+0x18.

**implement consequence:** Audio prebudenie nemodelovať as universal kruh počuteľnosti. One-shot cache can potlačiť later skenovanie tej istej areas.

**Remains / next test:** Same shot before and after príchode new guard to areas; LOS rohy and selector 0 test separate.


## 21. Bossovia and transform

AND0EE for class 0x11 changes OBJECT class on 0x14, height offset on 35, GUARD state on 8, save state on 2, timer on 1 and HP on 255. Class 0x16 vedie to separate complete branches with 51AA=1. Radio v E1M9 uses AE56: selected guard nad wall class F prepnú to state 0x14 with timerom 112; pod 96 starts movement, subsequently sa restores original sequence.

**Status:** Confirmed / Inferred. **Confidence:** Medium–High for arrays; Medium for complete names/visual transform. **Range:** 1.10; AND0EE has identical normalize tvar in all four.

**Evidence:** 3:AND0EE, AE56, B010, 7B56 case 0x14.

**implement consequence:** Transform restores bojový status through specifically arrays, nie create ľubovoľného new actor. Preserve save sequence and temporary timer.

**Remains / next test:** Pair each branch with exact IMG class/variant assetom and original video; close Cannon and all ending context.


## 22. weapon kadencia

Gate AA90 zeros cooldown during allow pokusu, still before call 8B06. Subsequent branch can failure on ammo, full poole or jam state. Neúspešný pokus therefore can consume prepare cooldown. Prepnutie weapons is separate automatic 4C3AND: 2 decrements 4C3C, on nule switches selector and prejde to 1; 1 increase timer after limit 01F2 and prejde to 0. This automatic moves HUD/frame path AND2CE.

**Status:** Confirmed. **Confidence:** Medium–High; calls and state write are explicit. **Range:** 1.10; prahy [2,1,3,1] raw confirmed in all four v precede audite.

**Evidence:** 3:9806 → AA90 → 8B06; 3:AAE6, AND2CE; 4C3AND/4C3C.

**implement consequence:** Separate cooldown pokusu, accepted shot and animation weapons. During podržanej hrane nezavádzať automatic repeated for all weapons.

**Remains / next test:** Trace during 0 ammo, 8 occupied projectile, weapon jam and change weapons during hold Ctrl; measure actual intervaly.


## 23. Damage and hitscan

Hitscan 8B06 iterate through all guard with current-generation stampom and allow state; successful LOS vedie on 80F8. V this loop after element successful damage is not break. Viac candidates therefore can dostať damage v jednom accepted hitscan shot, if splnia filtre. Damage further reads projection OBJECT+0x18; score come from z separate tables 9F10.

**Status:** Confirmed / Inferred. **Confidence:** High for absenciu break v this loop; Medium for reach viacnásobný hit. **Range:** 1.10; older analog extracted.

**Evidence:** 3:8B06, 80F8, 9FA2; GUARD+2 stamp; 3:CC7C writer.

**implement consequence:** During reconstruction automatic do not replace this loop algoritmom nearest single target. Preserve class and difficulty branches.

**Remains / next test:** Two visible guard v stredovej areas: log stamp, LOS and count call 80F8 v jednej frame. Visual dojem hit itself is not enough.


## 24. Projectiles

Confirmed local lifetime: state 1 animuje let, movement through 9D30 and condition project; state 2 only dohrá impact frames and up to after reach count frames free slot on 0. Arrays +0x16…+0x19 are deadline embedded OBJECT, nie its projection height. Load copies all eight slotov and fix their map pointer; v check taili however rebasing deadline loops handle VEC and world OBJECT table.

**Status:** Confirmed / Inferred. **Confidence:** High for layout and lifecycle; Medium for consequence nerebasovaného projectile deadline. **Range:** 1.10.

**Evidence:** 3:9E20, 9D30, 9B64; raw load 5ACB–5B81; 8×42 B.

**implement consequence:** Neuvoľniť slot already during impact; distinguish flying/impact and separate deadline. During fix loadera does not denote nepozorovanú change for original behavior.

**Remains / next test:** Save let also impact, move system time and load; track slot+0x16 and visible frame. Meaning slot+0x0D remains open.


## 25. Projection cache

CC7C writes OBJECT+0x18 up to after visible condition and add sprite slotu. GUARD stamp writes still užšia branch: flag 8 and prekrytie stredového X with toleranciou four pixel. 6348 moreover selects objects from sort X or Y list according to užšieho range. Render before inputom therefore does not mean restore cache each actor. Itself OBJECT+0x18 receive projection result after >>4 stored still before sprite-slot clampom; expression „clipped row“ was v older referencii too strong.

**Status:** Confirmed. **Confidence:** High for condition writery; specific stale value without runtime Unknown. **Range:** 1.10.

**Evidence:** 3:6348, CC7C; raw 3:CE5E and CE98–CE9D; 3:9B64; raw CCBB–CCC2 → CE5B–CE5E.

**implement consequence:** Retain difference between projection cache and aim stampom. Projectile collision does not have v verify branch same stamp filter as hitscan.

**Remains / next test:** Watchpoint OBJECT+0x18 during odvrátení kamery and projectile impacte; record last writer, generation and result damage.


## 26. Fire and hazardy

Fire test object class 7 v player current whole and flag 4BE5; itself this branch does not read difficulty. table 100/10/2 sa subtracts directly and death sets game state 3. Kontakt guard uses other helper, own difficulty multiplier and state 2. Same HP change tak does not have to mean same subsequent priebeh smrti.

**Status:** Confirmed. **Confidence:** High for table, podmienku and state write. **Range:** table all four; detail filtrov and state 1.10.

**Evidence:** 3:BE62, AND1EA, 8C0AND; DS:01FC; caller D974.

**implement consequence:** Model hazard and kontakt separate. On fire do not transfer difficulty scaling enemy kontaktu.

**Remains / next test:** Fire during troch difficulty, concurrency with kontaktom v jednom slow update and prechod to game state 2/3; verify priority v original.


## 27. Special walls

Class 7 animator 65AND6 hold idle frame 0 and after activation stop on last frame; writer 4:392C activation frame 1. Class 0x2D has other completion helper 4:3C0C: clear eligibility flag and map wall bytes. ONE_SHOT therefore is not general demolácia geometrie. current separate analysis SPECIAL1 and eight strategy-3 pokusov is preserved.

**Status:** Confirmed. **Confidence:** High for distinction vetiev; Medium for all map context. **Range:** 1.10; 65AND6 identical normalize C tvar v four exportoch.

**Evidence:** 3:65AND6; 4:392C/3C0C; 3:C0AND2; current deep referencia, ONE_SHOT sekcia.

**implement consequence:** Animation completion dispatchovať according to runtime class. Nezameniť stop on last frame with remove walls.

**Remains / next test:** For all four build verify entire string activation→frame→completion on same map coordinate, separately SPECIAL1 after LOAD.


## 28. Level triggery

BFD8 dispatchuje according to episodes, level index and wall class G/H. E1M9 switches weapon jam; E1M10 G launch BF20 and sets 51AND6/51AND8 also player movement inhibit 4BE8. Reset eventov 0EF6 and save/load 8-byte block represent two difference lifecycle cycle these flagov. Trigger cannot generally name as control distance door.

**Status:** Confirmed. **Confidence:** Medium–High for static branches; runtime events Unknown. **Range:** 1.10; shareware MAP difference 1.3/1.6/1.8 supported osobitne.

**Evidence:** 3:BFD8, BF20, 0EF6, 5466/574C; event block 51AND4–51AB.

**implement consequence:** address eventy trojicou episode/level/class and retain one-shot flags during LOAD. During novom level application specific reset.

**Remains / next test:** SAVE/LOAD before and after each G/H evente; for E2/E3 requires conclusion also exactly assign assety and mapy individual buildov.


## 29. IMG and SEQDEF

Animators 65AND6/CBD4 move during reach deadline jednu frame and naplánujú new term now+interval. During delay do not catch up all missed frames. Alternative sequence uses packed start/length and repeat RNG selection, until length is not zero. Count odberov is therefore dátovo depend. Same IMG.1 v shareware trojici nedokazuje same runtime selection each facing/state.

**Status:** Confirmed. **Confidence:** High for selected animators; complete IMG selector map still open. **Range:** algoritmický tvar four exportov; detail 1.10.

**Evidence:** 3:65AND6, CBD4, 6142; 8-byte runtime cache; previous IMG hash comparison.

**implement consequence:** Distinguish 90-byte source seqdef, 8-byte cache and 10-byte frame entries. Does not add dobiehanie animations without labels change behavior.

**Remains / next test:** Close all selector/bank combinations nad exact IMG file, especially overlap nízkych selectorov with address.


## 30. VEC geometria

4:3430 splits VEC to four orientation list and class their. Completion 4:3C0C clear flag bit 0 and wall bytes map, but v this routine nekompaktuje VEC table nor does not reduce its count. Render 4:3564 najprv test eligibility bit. Static model remove tak uses inactive record, nie automatic physical vymazanie.

**Status:** Confirmed / Inferred. **Confidence:** Medium–High for local invalidation; overall lifetime list Medium. **Range:** 1.10.

**Evidence:** 4:3430, 3564, 3C0C; VEC+5 bit 0; count 7E56.

**implement consequence:** Preserve stable pointer during zneaktívnení walls. Kompakcia during porte by require prepojenie all controllerov and list.

**Remains / next test:** Process all writerov VEC count and rebuild list during LOAD and door; verify final whole vertical/horizontálneho mazania.


## 31. Projection and clipping

E5D8 uses fixed spodný limit depth 0x4000 and clip screen X to -16383…16383. E798 project oba konce walls; during obrátenom screen order vymení X also related projection height. Output decide up to subsequent viewport prevent. C export E798 has varovania o remove block, therefore itself listing is not enough on bit exact model all equality and verify cases.

**Status:** Confirmed / Inferred. **Confidence:** Medium; explicit constant, but unclosed raw branches and round. **Range:** 1.10.

**Evidence:** 3:E5D8, E798; 4:3564; attached C also raw window.

**implement consequence:** Use fixné integer formats and transfer oba endpoint attribute during swap. Near-plane model nesmie be derived only z visible screenshotu.

**Remains / next test:** Reference input tesne pod/on/nad 0x4000, cardinal uhly, identical konce and signed division; then framebuffer comparison.


## 32. wall pixely

366AND reads text after column through frameBase+U*64 and inkrement z tabuliek; WinG target has pitch 320. Shade branch map each texel through 8094. V this loop is not test transparent colors. 6422 nakoniec returns U & (width-1); to is mask, nie general modulo for ľubovoľnú width.

**Status:** Confirmed. **Confidence:** Medium–High for jadro sampleru; pixel match Unknown. **Range:** 1.10.

**Evidence:** 3:366AND, 3E44, 6422; tables 247E/2480/2C7F/2E7E.

**implement consequence:** Preserve column layout and carry frakčného kroku. Neaplikovať sprite transparent key on walls; preserve original U mask.

**Remains / next test:** Compute and compare all sampler tables, top clipping and specifically columns original index framebufferu.


## 33. Sprity

CC7C obsadzuje 18-byte sloty okolo projection row; 6914 iterate through 100 slotov in vzostupnom order and after draw slot free. 3F80/374E skip texel 0x29 and use wall visibility comparison. Bypass bit 0x10 sa v this path reads z OBJECT+5 through pointer v sprite slote; designation VEC flag v older pixel table was inaccurate.

**Status:** Confirmed. **Confidence:** High for pointer base and masku; verify result without capture Medium. **Range:** 1.10.

**Evidence:** 3:CC7C, 6914, 3F80, 374E; slot+2 → OBJECT, OBJECT+5.

**implement consequence:** Preserve correct base flagov and order slotov. Do not insert automatic new sprite Z-buffer to model original game.

**Remains / next test:** Two up to three overlap sa sprity on same row, boundary 100 slotov, transparency and bypass bit v linear also VGA mode.


## 34. Palette and shade

C5E2 distinguishes normal status and blackout 51AB. Normal is shade 2, fill bytes 0x0C/0x11, if their nenahradí CLI verify; blackout force shade 6 and oba fill bytes 0. Already confirmed differences palette uploadu 1.8→1.10 remain valid. GAME.PAL has complete PCX palette; exact pair this palette with specific registered 1.10 package still missing.

**Status:** Confirmed / Unknown. **Confidence:** High for defaulty and blackout; runtime output Unknown. **Range:** detail 1.10; previous raw comparison palety 1.8/1.10.

**Evidence:** 3:C5E2, 29BE, 31AA, 3360; previous GAME_PAL_RGB_768.bin.

**implement consequence:** CLI verify and blackout have specific prioritu. load remap and event flag needs to posudzovať total.

**Remains / next test:** Original capture WinG/DisplayDib and RC_PALETTE; SAVE/LOAD v blackoute also during fade, check palety and 256-byte remapu.


## 35. HUD and automapa

AND3B6 is not clear draw function: sets upper limity HP, ammo and power-up zásob. During case 2 calls weapon automatic AND2CE. BB26 decrements jednu enabled zásobu during timer&15==0 and second during timer&7==0; during normal 8 Hz callerovi is nominal steps raz for 2 with and raz for 1 with. First step depends from phases timeru.

**Status:** Confirmed / Inferred. **Confidence:** High for writes and mask; derived time without runtime Medium. **Range:** 1.10.

**Evidence:** 3:AND3B6, AND2CE, BB26, D974; automapa stored as 4096 B.

**implement consequence:** During separate render move also state effects HUD to ekvivalentnej phases. Themselves vypnutie HUD nesmie nechtiac remove clamp or weapon update.

**Remains / next test:** Close each automap farbu and dirty flag; test timing power-upov with rôznou initial paritou and during DEMO mode.


## 36. SFX and MIDI

SFX E3B0 uses one track wave header. If UnprepareHeader returns 0x21, requirement with lower prioritou than current sa zahodí; same or higher calls reset and continues. Condition is strict '<', so same priorita can override previous sound. From versions 1.8 moreover remains confirmed save and restore successful load MIDI/wave volumes.

**Status:** Confirmed. **Confidence:** High for 1.10 raw priority; same condition check v four C exportoch. **Range:** 1.3, 1.6, 1.8, 1.10 for select priority branch.

**Evidence:** 3:E3B0 raw E3E8–E400; analog E01C/E2AND4/E302; DD80.

**implement consequence:** SFX priority model with equal as possible interrupt. Neodvodzovať field z count events; MIDI hold separate.

**Remains / next test:** Play same/below/above priority during active bufferu; failure zariadenie and return z menu verify on original Win16 audio environment.


## 37. USER.SAV

Loader 574C during read door recordov preserves current three far pointer and restores their after load store bytes. OBJECT and projectile map pointer recalculate from coordinates. VEC and world OBJECT deadline recalculate vzorcom: if save<save, set 0; otherwise save+(now-save). On conclusion application B128 verify. Same sentinel 0xD6E7 therefore still is not evidence ľubovoľnej cross-version compatibility.

**Status:** Confirmed / Unknown. **Confidence:** High for raw tail rebasing; complete cross-version round-trip Unknown. **Range:** detail 1.10; other save/load bodies and sentinel attached.

**Evidence:** 3:574C, raw 5ACB–5B94; 3:5466; 64×22 B door; B128.

**implement consequence:** Neobnovovať stored segment selektory slepou copy. Retain doors naviazané on just load entity and use exact time base.

**Remains / next test:** Round-trip during movement door, pushu, flying/impact projectile and animations; separate skúšať prenos between 1.3/1.6/1.8/1.10.


## 38. CONFIG and BSF

Raw read CONFIG in all four EXE require file long exactly 20 bytes; 1.10 loads block 4BD4–4BE7. BSF troch shareware package is rozdelený on 54-byte header and three related XOR blocks. First block 530 B and last 985 B are after decode identical; changes sa environment manual and distributor. All three registered bytes are 0 and XOR check headers passed.

**Status:** Confirmed. **Confidence:** High; raw parser and independent decode actual data. **Range:** CONFIG 1.3/1.6/1.8/1.10; BSF 1.3/1.6/1.8.

**Evidence:** config_read.asm.txt; 3:534E, C772; 4:32E4; bsf_blocks.csv and bsf_manual_changes.diff.txt.

**implement consequence:** CONFIG is binary 20-byte block; BSF is text kontajner. Differences distribútora/manuálu do not mean new AI whether hidden classes.

**Remains / next test:** Add exact semantic increase CONFIG bit and original BSF patriaci k 1.10. Bytes after NUL v field distributora nenormalizovať without reason.


## 39. DEMO

Closed doteraz unknown jednotka timestampu: is to 32-bit number render generation. Raw writer also replay comparator use same array in all four EXE. Provided DEMO.1 have 203 events, header 10/5/20, first timestamp 19 and last 1157; neobsahujú key Escape. Dispatcher loads najviac one due record on jedno call and v verify branch explicit netestuje EOF return read.

**Status:** Confirmed / Unknown. **Confidence:** High for timestamp and data; complete EOF/time behu Unknown. **Range:** code all four; file data shareware 1.3/1.6/1.8.

**Evidence:** 3:90CE raw 915F–9163, 91FA–9203, 9241; verification40.json; demo_events.csv; DAA0.

**implement consequence:** Timestampy neprepočítavať directly on ms. Header does not determine full real FPS; special UI mode 8 vie increase generation also v replay branch without normal render.

**Remains / next test:** Log last ten recordov, returns read and game state during konci file; last timestamp automatic not consider for length entire playback.


## 40. Postup, score and final

Corrected table score on base raw jump table: class 8/26 gives 25; 12/29/30 gives 250; class 21 gives -1000; 17/25 gives 0. All 25 values class 8–32 is verify in all four EXE. 80F8 add signed16 result k 32-bit score. Final class 0x16 v AND0EE sets 51AA=1 and game state 0; to samo does not close entire ending play and content episode.

**Status:** Confirmed / Unknown. **Confidence:** High for 100 raw score check; complete final Unknown. **Range:** score 1.3/1.6/1.8/1.10; final branch detailne 1.10.

**Evidence:** score_table_raw.csv; 3:9F10 jump table 9F2E; 3:80F8 raw 81AND3–81AC; AND0EE.

**implement consequence:** Use signed increment; penalizáciu -1000 do not insert k class 12/29/30. Retain separate score and damage dispatchery.

**Remains / next test:** Process callback final, result image and ENDING.FLI with exact registered package; check prenos inventory/score through all episode prechody.


## Corrected table score

Following values sa match v raw jump tables all four EXE. Class is desiatkové runtime OBJECT+6, nie map ID nor change enemy. For classes mimo switch range is v this routine initialize result 0.

| Runtime class | Signed score |
|---|---:|
| 21 | -1000 |
| 17, 25 | 0 |
| 8, 26 | 25 |
| 10, 32 | 50 |
| 9 | 75 |
| 11, 15, 16, 23, 27, 28 | 100 |
| 13, 18, 19 | 150 |
| 14, 20, 24, 31 | 200 |
| 12, 29, 30 | 250 |
| 22 | 1000 |


## Exact cross-version kotvy new raw confirm

| Rola | 1.3 | 1.6 | 1.8 | 1.10 |
|---|---|---|---|
| Parser argumentov | 3:10D8 | 3:10CC | 3:10CC | 3:1118 |
| CONFIG read | 3:51FC | 3:520AND | 3:520AND | 3:52AE |
| Contact damage | 3:9FC8 | 3:AND13C | 3:AND13C | 3:AND1EA |
| Score | 3:9CEE | 3:9E62 | 3:9E62 | 3:9F10 |
| DEMO record/replay | 3:8EAC | 3:9020 | 3:9020 | 3:90CE |


## BSF: verify differences

| Package | Distributor | Block 0 | Manual | Block 2 | Registered |
|---|---|---:|---:|---:|---:|
| 1.3 | The RoadHouse BBS | 530 | 13327 | 985 | 0 |
| 1.6 | Author-Direct | 530 | 13878 | 985 | 0 |
| 1.8 | Internet | 530 | 13868 | 985 | 0 |


Decode diff 1.3→1.6 contains change distribution/order pokynov and pribudnuté francúzske and talianske sekcie; 1.6→1.8 modify japonskú distribution sekciu. Is to description historical obsahu file, nie current kontakty whether ceny. Hash each decode block is v `bsf_blocks.csv`.

## What result still nedokazuje

Neexistuje tu original runtime trace nor pixel/audio reference capture. Unclosed remain all historical build, entire class verify and AI state grafy, exact EOF DEMO, all final assety, cross-version save round-trip and pixel exact projection. Also during corrected score or timestampu therefore does not claim, that entire corresponding subsystem is complete.

Highest value has following series original behov: (1) same DEMO with logom generation and RNG; (2) save/load during door and projectile; (3) viac hitscan candidates and stale OBJECT+18 during projectile hit; (4) joystickové boundary and focus; (5) index framebuffer and audio priority. Each test must record hash EXE, hash assetov, map, input and output.

## evidence package and reprodukcia

`Nitemare3D_Win16_40_oblasti_evidence_2026-09-24.zip` contains this report, machine register, C/raw window, extracted score and switch tables, DEMO events, BSF diff, verification result and skripty. Original commercial EXE and entire assety package nekopíruje; on repeated byte check sa použijú original input according to `verification40.json`.

Skripty were run nad provided file. Result `PASS` denotes static byte/data check. Linear objdump can data jump table display as apparent instructions; score verify therefore reads table wordy directly and verifies actual targets.

## External identify Windows

Game conclusions come from z local primary artefaktov. On distinguish name virtual key and messages were verify oficiálne identify: [Microsoft — Virtual-Key Codes](https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes), [Microsoft — WM_CLOSE](https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-close). These page explain API constant; do not prove behavior game nor successful beh in Windows 3.11.

## Overall confidence

High for hash identitu, new raw score table, contact multiplier, timestamp writer/comparator, CONFIG length and BSF data comparison. Medium for broader semantic model založené on track C and select raw vetiev. Runtime conclusions remain Unknown, until sa does not execute specific distinguish test.