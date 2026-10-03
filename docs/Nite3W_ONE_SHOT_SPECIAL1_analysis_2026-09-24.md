# Nite3W: ONE_SHOT, chrliče and SPECIAL1

Static analysis z 24. 9. 2026. Main build: Win16 1.10; check comparison relevantnej branches with C exportom Win16 1.8. Skúmané data: provided `MAP(10).1`, `IMG.1`, slovníky WALLS/OBJECTS. Original game v this audite was not run.

## Result

Podarilo sa spojiť doteraz neúplne vysvetlenú strategy GUARD 3 with jednorazovou animation wall chrliča. At the same time sa uzavrel basic cyklus ONE_SHOT, exact time jednotka meniacej sa tabule and neaktívna SPECIAL1 branch v E1M9. Našiel sa hraničný case timer and strong podložený candidate on difference behavior tabule after LOAD.

| Status | Finding | Primary evidence | Confidence |
|---|---|---|---|
| Confirmed | GUARD classes `0x12/0x13` dostávajú strategy 3; status `0x13` finds ONE_SHOT wall v cell guard and according to direction selects its plochu. | `3:B02C`, `3:7A06`, `3:7A44`, `4:3876`; MAP class tables and OBJECTS | High: code, raw instructions also data |
| Confirmed | `4:392C` changes wall frame `0→1`. Nespúšťa sound. | `4:3932–3939`; relocation record 16 segment 3 | High: priame bytes EXE |
| Confirmed | ONE_SHOT drží frame 0, after run continues after last frame and tam zostane. | `3:65A6`, branch `3:6646–6665`; IMG ID `54/55` | High |
| Confirmed | Movement has 8 pokusov; during all úspešných krokoch is 64 world units. Initial timer 8 skips run wall animations. | `3:7A50–7AA1`, DS tables `00E8/00F0` | High for static tok; visible prejav nepozorovaný |
| Confirmed | E1M2 SPECIAL1 switches shared interval tabule z 0 on 150 ms. Table has six frames and then cyklus opakuje. | `3:C0A2`, `3:65A6`, `3:66B0`, `IMG.1` | High |
| Confirmed | Ten certain wall ID `0x56` v E1M9 does not have v skúmanom SPECIAL1 handleri obsluhu. | MAP E1M9 + `3:C0AA–C0BC` | High for this interakčnú path |
| Inferred | Animovanie tabule after LOAD can depend from toho, whether sa level znovu initialize. Interval is not part of skúmaného save layoutu. | `4:28FC–2945`, `4:09F2`, `3:4C8A`, `3:5466`, `3:574C` | Medium for visible behavior; individual operations static confirmed |

Addresses `3:xxxx` and `4:xxxx` are **numbers NE segment and offset**, nie runtime Windows selectory. Correspond exportným menám `FUN_1010_xxxx` and `FUN_1018_xxxx`. DS denotes logical data segment exportu `1048`, v file NE segment 10.

## 1. Identita and overenie podkladov

EXE has 230 400 bytes and SHA-256:

`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`

Its NE segment 3 starts v file on `0x15FC0`, segment 4 on `0x25260`, segment 10 on `0x2C040`. file offset kotvy is start corresponding segment + listed offset. Complete hashe all deviatich input contains `source_manifest.json` v evidence package.

On interpretáciu far call sa použili also NE relocations. For example raw call on `3:7A8F` contains offset `392C` and nereálny segment word `7A10`. Fixup on `3:7A92` belongs k internal segment relocation recordu 16, which určuje NE segment 4. actual static target is therefore **`4:392C`**. Obdobne `3:7A85 → 4:3876`. Is not audio helper nor o address `7A10:392C` for behu.

## 2. Chrlič: from map k stratégii and wall animation

| MAP object ID | Object class | Name v OBJECTS | Base directional variant |
|---|---|---|---|
| `B4–B7` | `12` | Cemetary wall Gargoyle N/E/WITH/W | `B4` |
| `B8–BB` | `13` | Garden wall Gargoyle N/E/WITH/W | `B8` |

`3:D1A2` creates object and GUARD. Raw sequence `3:D2BB–D2D6` subtracts first ID same classes from current ID and posiela this subtype as last argument initialization `847E`. C export this pass nevykresľuje completely. `844C` z neho sets facing `(subtype & 3)*2`; during subtype 0–3 are initial movement komponenty zero. `B02C` sets for classes 12/13 strategy 3 and initial status 7. Possible map rules RETREAT/FLEE/ACTIONSPOT can všeobecne strategy change; skúmané chrliče ležia on wall class 7.

V state 7 nasleduje check global flag `4BE7` and percepcia through `7494`. Up to during successful result and stratégii 3 sa calls `7A06`, which sets:

- `GUARD+06 = rand()%80 + 8`;
- `GUARD+0B = 0x13`;
- `GUARD+13/+14` from directional tabuliek DS `00E8/00F0`.

| Facing | Posun X/update | Posun Y/update | Vybraná orientation wall plochy `+7` |
|---:|---:|---:|---:|
| 0 | 0 | −8 | 0 |
| 1 | 8 | 0 | 2 |
| 2 | 8 | 0 | 2 |
| 3 | 0 | 8 | 1 |
| 4 | 0 | 8 | 1 |
| 5 | −8 | 0 | 3 |
| 6 | −8 | 0 | 3 |
| 7 | 0 | −8 | 0 |

Strategy 3 therefore synchronizuje output movement chrliča with change its wall image. Game named vychádza from slovníka assetov; interný tok is confirmed directly.

### Exact boundary timer

`7A44` najprv preserves old timer, then ho decrements. Rozhodovanie uses starú also novú value:

```text
old = timer
timer = timer - 1
if old == 0:
    strategy = 0
    state = 2
else if timer == 8:
    wall = find_wall_at_guard_cell(class=7, facing=guard.facing)
    if wall.frame == 0: wall.frame = 1
else if timer < 8:
    attempt_emergence_move(dx, dy)
```

Movement sa test during new value **7,6,5,4,3,2,1,0**. To is eight pokusov, maximálne **8 × 8 = 64 jednotiek**, therefore jedna map cell. During nasledujúcom update with starou value 0 sa branch skončí; timer vtedy already contains −1.

During initial timer **8** sa first update decrements equal on 7. Branch `timer==8` sa v this priechode nevykoná. During initial value 9–87 sa executes raz. Is to jedna z 80 possible values increase RNG, nie doložená frekvencia výskytu v odohratej hre. Same logic is v exporte Win16 1.8: `7962 → 79A0 → 387E → 3934`.

**Obmedzenia movement:** v this branch sa allow posun v original cell; during change cells sa requires zero object byte target and iná cell than player. After success sa prenesie object byte, changes cell pointer and X/Y. Timer sa decrements also during neúspechu, so 64 is maximum, nie zaručená distance. This special output does not use general wall-property collision test.

## 3. What exactly mean ONE_SHOT

`WALLS(9).1` denotes `54` as Cemetery – Disappearing gargoyle and `55` as Garden – Disappearing gargoyle. MAP their mapuje on wall class 7. Is not object class 7, which has other meaning.

| Wall ID | SEQDEF offset v IMG.1 | Interval | Frames | Rozmery each frames |
|---|---:|---:|---:|---|
| `54` | `2588` | 200 ms | 5 | 64 × 64 |
| `55` | `25E2` | 200 ms | 5 | 64 × 64 |
| `56` | `263C` | original 0; after E1M2 USE 150 ms | 6 | 128 × 64 |
| `12` | `0E54` | 0 | 1 | according to frame record; is not this morph sequence |

Updater `65A6` increments frame and then for class 7 executes osobitnú branch:

| Frame before expiráciou | Frame after expirácii |
|---:|---:|
| 0 | 0 |
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |
| 4 | 4 |

Helper `392C` umožňuje only prechod 0→1; already running or completion image nereštartuje. Updater classes 7 does not change wall ID, geometriu nor collision flag. „Disappearing“ sa therefore týka obsahu animovaného image; is not to evidence remove celej walls.

`66B0` calls updater z vykresľovania list wall segment and only during nonzero intervale (`3:68ED–68F8`). `65A6` after expirácii executes najviac one step and sets new deadline on `now+interval`, without dobiehania zmeškaných frames. During doby, when wall nevstupuje to this render branches, this call path its frame neposúva. Exact image prejav during odvrátení and opätovnom pohľade remains runtime test.

Time pochádza z `D6C6`, which stores GetTickCount or timeGetTime. Value 200 is therefore interval v milisekundách. Trigger 392C does not change deadline: from aktivácie after nasledujúcu frame does not have to uplynúť exactly celých 200 ms.

### Map verify

coordinate are `(x,y)` from nuly, level v table from units. Counts are cells provided MAP; nie count create wall plôch nor runtime events.

| Map | ONE_SHOT cells | Chrliče class 12/13 v same cell |
|---|---:|---:|
| E1M2 | 54 | 0 |
| E1M6 | 19 | 19 |
| E1M8 | 48 | 46 |

All **65 map chrličov class 12/13** z tohto MAP lies on ONE_SHOT wall. On E1M8 moreover existuje wall 55 without object and wall 54 with object SECRET 62. Itself prítomnosť ONE_SHOT dlaždice does not mean, that sa aktivuje through guard.

Specific test kotva: E1M6 `(52,15)`, wall `54`, object `B5` — východný chrlič. Prirodzený direction movement is to `(53,15)`, where has provided MAP object byte 0. Initial stred is `(3360,992)` world units. This are coordinate chrliča, nie odporúčaný spawn player.

## 4. SPECIAL1: table and poistková skrinka

`1A22` posiela interakciu with wall class 8 to `C0A2`. This handler obsluhuje only episode 1 and level indexes 1 and 6:

| Mapa and miesto | Confirmed operation |
|---|---|
| E1M2 `(32,50)`, `(33,50)`, wall `56` | Finds element class-8 entitu for cell; vezme its cache selector `+4`; sets `DS:51AE + 8*selector = 150`; calls SFX event `44`. |
| E1M7 `(27,26)`, wall `12` | Only during `51A6==1` sets `51A6=2`, `51AB=0`, restores color set and corresponding time status; displays jednu z dvoch message according to condition. |
| E1M9 `(46,42)`, `(46,43)`, wall `56` | This USE/SPECIAL1 path sa returns without aktivácie animations. |

Interval tabule is shared through sequence cache; `4C8A` shared cache according to image-stream offset. Individual wall entity have own frame/deadline. Cannot their therefore automaticky považovať for one shared play status.

SEQDEF tabule has `extended=0`, six frames and original interval 0. After set on 150 sa uses všeobecná branch animátora: `0→1→2→3→4→5→0…`. **Is opakujúcu sa animation after interakcii**, nie o class-7 play jedenkrát. Repeated USE opäť sets interval and calls sound; `C0A2` neprikazuje return on frame 0 nor new deadline. Nominálne six intervalov predstavuje 900 ms, no render and oneskorenia can cyklus predĺžiť.

## 5. SAVE/LOAD: confirmed layout and derived problem tabule

`5466` save 28 000 bytes wall records from runtime offset 6; v save slote sa this block starts on `0x2093`. Part of records are frame `+3` and deadline `+8`. ONE_SHOT therefore nepotrebuje new osobitný boolean „already run“: its status is stored in frame. `574C` after load upraví deadline-y according to new time.

Wall sequence cache on `51AC` and its intervaly `51AE+8*k` sa v skontrolovanom list save block neukladajú. Event block `51A4–51AB` ends before cache. `4C8A` napĺňa intervaly nanovo z IMG.

Raw LOAD dispatcher `4:28FC–2945` distinguishes existing same level/episode from potreby initialization through `09F2 → 51B4 → 4C8A`:

| Scenario | Static derived očakávanie for table |
|---|---|
| Aktivovať table, save and LOAD v tom istom already load level | Existing cache interval can zostať 150; restore frame further animuje. |
| Aktivovať, save, load save after novej initialize level | Interval sa naplní z IMG value 0; stored frame sa restores, but this animačná path sa nespustí up to to next USE. |
| Save before aktiváciou, then aktivovať, subsequently LOAD starého save v tom istom level | Cache interval 150 can prežiť LOAD also napriek restore older frame. |

This is **Inferred/Medium for result on image**, nie already odpozorovaná error original game. confirm sa condition loadera, writes cache and missing cache block v serializácii. Dynamic test has verify entire track including others obslúh game menu. ONE_SHOT has on difference from tabule nonzero interval 200 already v IMG, so sa this specific zero intervalový problem naň directly neprenáša.

## 6. implement dôsledky

- Preserve separate `guard.strategy`, `guard.state`, `guard.timer`, `wall.frame`, `wall.deadline` and shared sequence interval.
- For compatibility must class 7 držať frame 0, spúšťať sa through 392C and zastaviť on poslednom frame.
- Output chrliča has eight movement pokusov, nie seven. Block nezastaví timer.
- During faithful mode preserve zdokumentovanú branch initial timeru 8. Correction has be vedomá odchýlka, nie tiché prepísanie condition.
- Table sa after USE cyklí with intervalom 150 ms; E1M9 nepovažovať automaticky for aktivovateľnú only according to wall ID.
- Restore cache during LOAD proposed up to after runtime test listed troch scenarios. Exact compatibility and konzistentné „corrected“ behavior are two difference implement choice.

These rules are pripravené for implement ohraničenej mechaniky v1.10. Nenahrádzajú general collision system nor evidence pixel matches.

## 7. verify and remain questions

verify was hash EXE, NE layout and fixup strings, raw instructions kľúčových vetiev, physical size MAP, all relevantné map cells and four SEQDEF/frame streamy. Small derived model passed **640 combination** 80 initial timerov × 8 directional and skontroloval count pokusov, triggerov, result posun and termination. Is check dôsledkov code, nie o 640 behov Nite3W. Count runtime behov: **0**.

| Question | Distinguish test |
|---|---|
| Visible consequence timeru 8 | On chrličovi E1M6 `(52,15)` capture prirodzený input to state 13 with timerom 8; track guard `+06/+0B`, wall `+03` and call `4:392C`. compare with timerom 9. |
| Vplyv odvrátenia pohľadu | After triggeri track wall frame/deadline, otočiť sa mimo walls, then sa return. Rozhodujúci is input walls to render listu and call `3:68F8`. |
| LOAD tabule | E1M2 wall 56 on `(32,50)` or `(33,50)`; record `selector=wall[+4]`, `DS:51AE+8*selector`, frame and deadline v each z troch LOAD scenarios above. |
| E1M9 table | verify USE on wall 56 and return `C0A2` without write intervalu; track, whether existuje other runtime spúšťač. |
| Exact draw and sounds | Capture frames/sound v original Win16 build. ID sound events samo does not determine name nahrávky. |

Runtime selectory needs to v debugger-i zistiť z nahratých NE segment; fixed numbers 3/4 nor dekompilované 1010/1018 sa must not slepo vložiť as runtime CS.

Overall confidence: **High for opísané static branches Win16 1.10; Medium for complete LOAD prejav and visual synchronizáciu.** Win16 1.8 supports match strategy 3, but its EXE bytes and DOS parity sa v this added neoverovali. Percento hotovej celej game sa does not change.

## evidence package

`Nite3W_ONE_SHOT_SPECIAL1_evidence_2026-09-24.zip` contains this report, reprodukčný Python skript, hashe input, výrezy original instructions with disassembly, NE relocation map, očíslované výrezy C exportov, map inventory, SEQDEF/frame inventory and output modelu. Neobsahuje entire EXE nor entire game data.