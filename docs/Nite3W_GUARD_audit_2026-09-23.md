# GUARD v Nite3W: state machine, animations, sounds and DOS comparison

**Range:** Win16 `nite3w(10).exe` 1.10 as main version; check comparison Win16 1.8 and DOS E-20.

**Conclusion:** Win16 1.10 has teraz completely map branches main dispatcheru, plan stratégií, rules selection animačnej sequences and numeric selection sound. DOS E-20 shared kľúčové auxiliary algoritmy and its visible blocks state are very near Win16. Is not however poctivé mark entire GUARD audit for absolútne „100 %“: dynamic tables sequence were not subtract z behu game and complete DOS skokový dispatcher nor its audio switches are not restore with same confidence as Win16. Numbers sound selection are confirmed; names and počuteľná identita all vzoriek nie.

| Status evidence | Range |
|---|---|
| **Confirmed v Win16 1.10** | Each branch `0x00–0x15` dispatchera including neobslúžených `0x0A/0x0B`; boundary condition timer; strategy `0–4`; directional index and offset sekvenčných row; three class audio switche and condition WAVEOUT. |
| **Confirmed match helperov Win16/DOS** | Setter tokenu, LOS/near, planner, wall/direction, special strategy `3`, movement and zásahová table. |
| **Derived** | Names `Guard` during sound class correspond byte switch `OBJECT+6 = n+7`; this map is konzistentné with object katalógom, but nebolo subtract z živého record. Označenia events „prebudenie/attack/death“ vychádzajú z miesta calls helpera. |
| **Unclosed** | Živé values slov v load row class; complete DOS dispatcher and DOS audio switche; počuteľné names all WAV vzoriek. |

## Základné records

Win16 1.10 iterate 100 records GUARD after `0x1A` byte. `FUN_1010_80aa` calls `FUN_1010_7b56`; add object sa dohľadá through index on `GUARD+0x08`, multiplies sa `0x1C` and pripočíta k object table on `0x6D66`.

| Array | Role confirmed v code |
|---|---|
| `GUARD+0x00..01` | Zabalený token sequences: low byte is initial index frames, upper byte count frames. |
| `GUARD+0x06` | Timer v update simulácie, nie milisekundy. |
| `GUARD+0x08` | Index add object. |
| `GUARD+0x0A` | Strategy. |
| `GUARD+0x0B` | Current state. |
| `GUARD+0x0C` | Following or stored status. |
| `GUARD+0x0E` | compare identify v special cykle E/F. |
| `GUARD+0x0F` | Mode direction during výpočte otočenia. |
| `GUARD+0x11` | Direction GUARD, 8 values. |
| `GUARD+0x12` | Stored directional index; hit sem writes `8`, čím changes branch selection reakcie. |
| `GUARD+0x13/+0x14` | Zložky movement X/Y as podpísané bytes. |
| `GUARD+0x16` | Mode rozhodnutia between near and result LOS. |
| `GUARD+0x17` | Stored result visible. |
| `GUARD+0x18` | Flag near. |
| `OBJECT+0x04` | Index load row animačnej classes. |
| `OBJECT+0x06` | Class usage sound switch. |
| `OBJECT+0x03` | current frame object. |

`FUN_1010_762c` sets token sequences, frame object, timer `upper_bajt(token)-1`, current and following status. Timing state therefore odpočítava game update.

## Prechody stavov Win16 1.10

Main dispatcher is `FUN_1010_7b56` (`nite3w110.exe.c:24376–24639`). Below are branches, which itself executes; auxiliary functions can pritom meniť add object or additional guard.

| Status | Activity and prechod |
|---:|---|
| `0` | increase `OBJECT+3`; after reach konca range frames ho returns on start. Decrements timer. If new timer is `<1`, sets current state on `+0x0C`. |
| `1` | Decrements timer; to state `2` prejde, if its value **before znížením** was `0`. |
| `2` | Selects sound through `b862`, loads sequence z riadka classes `+0x34` and sets animation `0 → 3`. |
| `3` | Vyhodnotí `7594`. Neúspech: directly status `5`. Success: sequence `+0x36`, animation `0 → 4`. |
| `4` | Vyhodnotí `7594`; during success selects sound through `b5e4` and calls attack on player `8c0a`. If global game state is not `2`, always naplánuje sequence `+0x38`, animation `0 → 5`. |
| `5` | Calls plan strategy `76fc`; ten sets movement status `6`. |
| `6` | Selects directional sequence, executes movement `71dc`, decrements timer. If new timer is `0`, prejde to `3`. |
| `7` | Restores directional sequence. If is active global block flag `4be7`, ostane v state. Otherwise executes LOS `7494`. Without LOS ostane v state `7`; with stratégiou `3` prejde to `13`, otherwise to `2`. |
| `8` | Executes nástenné right `7920`, movement and update animations. Additional check sa robia only if `+0x0C==2`; then during vypnutom `4be7` and successful LOS sets status `2`. |
| `9` | Calls interakčný helper `a0ee`; during global flag `4c26==1` selects sound `b6a0`. If flags add object allow interakciu, writes `4,0` to bytes `+0x0C/+0x0D` v prepojenom record. |
| `0x0A` | V hlavnom switchi does not have vetvu. |
| `0x0B` | Does not have vetvu. `FUN_1010_80ea` ho sets as status vyradenia. |
| `0x0C`, `0x0D` | Vynúti update directional sequences through `6ee0`; samo does not change status. |
| `0x0E` | Update sequence. If is zapnutý flag `51a5`, sets timer on nulu and status `0x0F`. |
| `0x0F` | Update sequence. If `51a5` is not zapnutý, returns sa to `0x0E`. Otherwise decrements timer. When its original value was `0`, during match `GUARD+0x0E==4c1c` selects sound, sets `0x10`, vynúti sequence, sets timer z upper byte tokenu and sets current state `0`, following `0x10`. |
| `0x10` | Update sequence and decrements timer. When original value timer was `0`, during success `7594` calls attack `8c0a`, sets timer `8`, status `0x0F` and vynúti sequence. |
| `0x11` | Update sequence and movement, decrements timer. When new timer is `0`, selects new direction, zeros zložky movement and strategy, sets status `7` and vynúti animation. |
| `0x12` | Moves frame to konca sequences, decrements `OBJECT+0x1A` after 5 with clip on nulu and decrements positive timer. When timer also `OBJECT+0x1A` reach nulu, sets current state on `+0x0C`. |
| `0x13` | Executes special timer and movement through `7a44`. During input with timer `0` clear strategy and sets status `2`. After znížení timer on `8` finds wall class 7 through `4:3876` and aktivuje its frame 0→1 through `4:392C`; during novej value `<8` test movement. |
| `0x14` | If is timer already `<1`, calls global handler `ae56(1)`. Otherwise ho decrements; during novej value `<0x60` executes movement. |
| `0x15` | Moves reakčnú frame after poslednú. Then restores current state z `+0x0C`. |

Difference v okamihoch odpočítania is podstatný: state `0`, `6`, `11`, `12`, `14`, `15` check zníženú value according to above listed condition; state `1`, `0x0F` and `0x10` test store value **before** znížením.

## Strategy

Plan `FUN_1010_76fc` (`:24134–24257`) has these branches:

| Strategy | Exact behavior |
|---:|---|
| `0` | Computes relatívne cells player, selects directional zložky `0`, `+8` or `-8` through random branch, flag LOS and orientation. Without near and without LOS sets timer `0x18`; during LOS selects `rand()%8+8`, during difficulty level `2` ho divide dvoma, during difficulty level `0` multiplies dvoma; during near ho sets on `8`. Then sets status `6` and update direction, sequence i movement. |
| `1` | Only during HP `<0x7F` searches through `1394` najbližší valid target. If ho finds, sets movement k target and timer `0x10`; subsequently status `6`. Without valid target continues generickou branch. |
| `2` | Sets timer `rand()%8+8` (8–15), then status `6`; itself directional animátor for this strategy selects other sekvenčnú skupinu than normal chôdza. |
| `3` | Status `7` ho presmeruje to `7a06`: timer `rand()%0x50+8` (8–87), status `0x13` and zložky movement according to current direction. `7a44` odpočítava timer; during value after znížení `8` aktivuje ONE_SHOT wall frame 0→1 through `4:3876 → 4:392C`; during value `<8` test movement; during input with `0` clear strategy and prejde to `2`. movement branch sa can execute during new value `7…0` (najviac 8 update). |
| `4` | V `80f8` potláča normal neletálnu reakciu on hit. |

movement table for eight directional is `X={0,8,8,0,0,-8,-8,0}`, `Y={-8,0,0,8,8,0,0,-8}`. Numbers are fixed steps coordinates during each pokuse, nie dlaždice for one tik.

## Selection animation

Line classes sa reads through `row = *(word *)(0x4748 + 8 * OBJECT[+4])`. Word sequences is zabalený token; setter ho stores to GUARD and its low byte to `OBJECT+3`.

| Kontext | Source slova v riadku classes |
|---|---|
| Status `2` / prebudenie | `row+0x34` |
| Status `3` / finding | `row+0x36` |
| Status `4` / attack | `row+0x38` |
| Movement, status `6`, strategy iná than `2` | `row+0x24+2*facingIndex` |
| Status `6`, strategy `2` | `row+0x04+2*facingIndex` |
| Directional helper `6ee0` v state `7`, `8`, `0x10`, `0x11` | `row+0x14+2*facingIndex` |
| Directional helper v others state | `row+0x04+2*facingIndex` |
| Zásahová reakcia | `row+0x3A+2*variant` |
| Smrteľná reakcia | `row+0x4A+2*variant` |

Directional index is `(4 - (mode==0) + GUARD[+0x11] - vectorFacing) & 7`; `vectorFacing` count `d454`, result sa save to `GUARD+0x12`. If sa direction nezmenil and call is not vynútené, `6ee0` sequence does not change. During state `6` is osobitná branch listed v table above.

**Correction predošlého súhrnu:** priamy Win16 1.10 code `6ee0` selects `row+0x14` v state `7`, `8`, `0x10`, `0x11`; nie in all state `8–0x0F`. Raw 16 bit disassembly on `1010:6EE0` confirms condition. Other state directional helpera idú on `row+0x04`.

Table `0x4748` and its 90 byte lines sa skladajú during load class. Numeric words z each row therefore cannot spoľahlivo add only z tela dispatcheru; requires sa runtime dump tables or complete restore load define. Katalóg IMG určuje sloty and frames, but itself nepriraďuje all row items `+0x34/+0x36/+0x38` k name action.

## Selection zvukov Win16

`b862` sa calls v state `2`; `b5e4` v state `4` and during special cykle `0x0F`; `b6a0` v state `9` during flag `4c26==1` and during smrteľnom hit. Switches read class z `OBJECT+0x06`. Numeric selector sa posiela to `e3b0`; `e3b0` play only during zapnutom sound and nonzero record v table on `0x49F8+6*selector`. Numbers below are hexadecimálne interné selectory.

Designation class according to katalógov `Guard` track map `selectorClass = Guard + 7`; to is odvodenie z object registra and numeric range, nie subtract živý object record.

| `OBJECT+6` | Class z registra | Status `2` | Attack `b5e4` | Death / špeciál `b6a0` |
|---:|---|---:|---:|---:|
| `08` | GUARD1 Bat | `22` | — | `23` |
| `09` | GUARD2 Frankenstein | `38–3A` | `41` | `08` |
| `0A` | GUARD3 Mummy | `38–3A` | `41` | `07` |
| `0B` | GUARD4 Skeleton | `3B` | `4E` | `24` |
| `0C` | GUARD5 Mrs H. | `14` | `20` | `04` |
| `0D` | GUARD6 Zelda | `15` | `20` | `13` |
| `0E` | GUARD7 Vampira | `10` | `20` | `0E` |
| `0F` | GUARD8 Baddie #1 | `36–37` | `17–19` | `0B–0D` |
| `10` | GUARD9 Baddie #2 | `36–37` | `17–19` | `0B–0D` |
| `11` | GUARD10 Dracula | `06` | — | — |
| `12` | GUARD11 Cemetery Gargoyle | `3F` | `3E` | `07` |
| `13` | GUARD12 Garden Gargoyle | `3C` | `1F` | `07` |
| `14` | GUARD13 (without classes v katalógu) | — | — | `23` |
| `15` | GUARD14 Penelope | — | — | — |
| `16` | GUARD15 Dr. Hamerstein | `12` | `17–19` | — |
| `17` | GUARD16 Tall slim robot | `48` | `1F` | `46` |
| `18` | GUARD17 Trashcan robot | `47` | `20` | `46` |
| `19` | GUARD18 Cannon | — | `1D` | — |
| `1A` | GUARD19 Ghost | `49` | `4E` | `4A` |
| `1B` | GUARD20 Goldie | `0D` | `4B–4E` | `02` |
| `1C` | GUARD21 Greenie | `0D` | `4B–4E` | `02` |
| `1D` | GUARD22 Demon | `38` | `4B–4E` | `09` |
| `1E` | GUARD23 Alien #1 | `3D` | `4B–4E` | `46` |
| `1F` | GUARD24 Alien #2 | `3D` | `4B–4E` | `46` |

range are selection through RNG: `17–19 = rand()%3+0x17`, `36–37 = rand()%2+0x36`, `38–3A = rand()%3+0x38`, `4B–4E = rand()%4+0x4B`. Pomlčka mean, that daný switch does not have branch for class and ponecháva selector `0`.

For orientation: selector `0x22` is desiatkový index `34`; v exporte SND is named `Sound 034.wav`. Selector `0x41` is index `65`. During vzorkách pod `0x22` does not have check WAV export related named, therefore tu remain only numbers. `6dfa` sets pan doľava, stredu or doprava according to vzájomného direction object and player.

## Comparison DOS E-20 and Win16

| Area | Win16 1.10 / 1.8 | DOS E-20 | Conclusion |
|---|---|---|---|
| Record GUARD | 26 bytes, count to 100; dispatcher `1010:7B56`; 1.8 dispatcher `1010:7AB2` | 26 bytes, count `0x6276`; updater calls `FUN_1000_59F0` z `FUN_1000_5F26` | Layout and main helper interface sa match. |
| set sequences | `762c` save zabalený token, timer, current/next state | `54d8` robí same arrays | Confirmed logical match. |
| Selection smerovej animations | `6ee0`, table `0x4748`; smery `0xD6/0xDE` | `4d9a`, table `0x3D22`; smery `0xAC2/0xACA` | Same tvar algoritmu, other addresses and tables. |
| Plan | `76fc` | `55a8` | Same branches: prah HP `0x7F`, random wait `8–15`, general direction, LOS/near and status `6`. |
| Wall / direction | `7920` | `57bc` | Same rules for classes stien AND/B and otočenie. |
| Strategy `3` | `7a06`, `7a44` | `58a0`, `58de` | Same range timer `8–87`, tables movement and prechod to `2`. |
| LOS / near | `7494`, `7594` | `5342`, `5442` | Matching helperov is priame. |
| Damage | `80f8`, `b94e`, `b9b2` | poškodzovací klaster v `5f74` | Matches selection class row `+0x3A/+0x4A`, HP and return status `0x15`. |
| Entire dispatcher | C export 1.10 is čitateľný; 1.8 has same layout state | `FUN_59F0` and adjacent exportované functions contain prekrývajúce sa boundary and incorrect control-flow | DOS pseudo-C is not safe jediný evidence for each branch; complete skokový graf still is not closed. |
| Audio switches | All three class switche `b862/b5e4/b6a0` are rozlúštené on selectory | Neidentifikovaný DOS far helper / audio selector v exporte | Sound parita between build so far nepotvrdená. |

DOS code E-20 on offset okolo `1000:5A94–5F1C` uses same class items `+0x34/+0x36/+0x38`, setter `54d8`, planner `55a8`, movement helpery and state `0x0E–0x15`. Match supports priamy disassembly also zodpovedajúce helpery. Nevyhlasujem however complete reconstruction DOS skokovej tables: v MZ exporte sa its boundary miešajú with next block, therefore is correctly ponechať vysokú confidence for auxiliary algoritmy and lower for complete zosúladenie each DOS branches.

## What still missing k doslovnému „100 %“

1. Dumpnúť during behu Nite3W 1.10 lines class v `0x4748` and thereby nahradiť derived relationship `Guard+7` živými value; vypísať each word sequences on `+0x04/+0x14/+0x24/+0x34/+0x36/+0x38/+0x3A/+0x4A`.
2. compare these tokeny with 512 slotmi `IMG(10).1`, aby small each class status exact IMG index and čitateľný name frames.
3. Izolovať DOS E-20 dispatcher z original MZ code or runtime trace and restore class audio switche; then compare selectory with Win16.
4. If needs to počuteľné names, nie only numerické selektory, create list vzoriek from actual SND.DAT and identify their according to audia. Numeric selection v code is already confirmed.

## Primary evidence and range build

| Input | SHA-256 / locator |
|---|---|
| Win16 `nite3w(10).exe` | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |
| Win16 1.10 export `nite3w110.exe.c` | `71ca365f8c6a61fa9cadad8631e9fcd6ce134e36c714878889c75b7399280168`; dispatcher `24376–24639`, sequences `23701–23745`, LOS/near `23964–24070`, strategy `24134–24363`, hit `24641–24788`, sound `27723–28040`, WAVEOUT `30845+` |
| Win16 1.8 export `NITE3W18.EXE.c` | `0917624ccdc53a98a6ea04760689d989692bf2d86b818d86fd2a26c889f8cc94`; check dispatcheru `1010:7AB2`, directional function `6E3C` |
| DOS E-20 `N3D-E-20.EXE` | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` |
| DOS C export `N3D-DOS-UNFULL-v20.exe.c` | `5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54`; helpers `4D9A`, `5092`, `5342`, `5442`, `54D8`, `55A8`, `57BC`, `58A0`, `58DE`; dispatcher export `59F0`, guard loop `5F26`, damage klaster `5F74` |
| object katalóg | `OBJECTS(10).1–3`; `Nitemare3D_Objects_Enemies.pk3`, especially `docs/object_enemy_catalog.csv` and `docs/rotate_frame_map.csv` |
| Audio export | `snd.zip`; names WAV are numeric, napr. `Sound 034.wav` |

All tvrdenia o prechodoch and selectore Win16 above are static analysis specific 1.10 exportu/byte. Was not execute runtime trace Nite3W nor compare play DOS sound.


## Doplnenie 24. 9. 2026: identify strategy 3

**Confirmed/High, Win16 1.10:** `B02C` assign strategy 3 class 12/13, which provided OBJECTS/MAP identify as wall chrliče. `7A44` on novom timeri 8 finds ONE_SHOT wall class 7 v cell chrliča, selects plochu according to facing and through `4:392C` changes frame 0→1. NE relocation record 16 segment 3 confirms segment 4 oboch call. To spresňuje older designation „map/event helper“.

movement pokusov is eight, during value 7…0; maximum is 64 world units. During initial timeri **8** sa wall trigger skips, because najprv dôjde k dekrementu on 7. Code confirms this hraničnú branch; visual consequence v hre was not v this audite pozorovaný. Same time tok is v exporte Win16 1.8 `7962/79A0/3934`.

V provided MAP is 19 takýchto chrličov v E1M6 and 46 v E1M8; all 65 has v same cell wall class 7. Podrobnosti, directional table, save/animation related, evidence model 640 cases and exact additional test are v `Nite3W_ONE_SHOT_SPECIAL1_analysis_2026-09-24.md`. Runtime confirmation nor pokrytie entire automatu sa thereby automaticky nezvyšuje.