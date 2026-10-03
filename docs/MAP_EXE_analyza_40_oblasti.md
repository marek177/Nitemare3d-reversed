# Nitemare3D MAP.EXE — analysis 40 areas

Date: 24. 9. 2026. Analysis specific provided DOS programu and its data.

**Main finding: this MAP.EXE contains prázdnu function save and prakticky prázdnu obsluhu editovania mouse.** Interface ponúka save, but all three preskúmané path save call only `RET`. Program pritom dokáže meniť map v pamäti command C and subsequently zrušiť flag neuložených zmien without write map.

Next specific finding is nedefinovaná wall `0x37` v štvrtom block `MAP.2`, on coordinate **x=61, y=54**, count from nuly. Its class v header is 0 and v provided `WALLS.2` missing its define.

Audit zahŕňa 62 candidate aplikačných functions, 136 name class, 1 116 define and all 31 map block v provided `MAP.1–3`. Findings are založené on original byte, disassemblovaní and independent parsovaní data. **Original program was not running v DOS-e. increase 210 find functional štítkov nebolo podrobených same hĺbkovému auditu.** Result therefore is not tvrdením, that all unknown own programu were define vyriešené.

## Identita and read evidence

| File | Size | SHA-256 |
|---|---:|---|
| MAP.EXE | 49 906 B | `e88bf6bc1a2612737fdbfcb171f68b99154c48f362c9346d89f024d8f0f47f8a` |
| MAP.EXE.gzf | 294 747 B | `7fe4b4185b6ab6ef71dc5a9ee5530d7b4800296f60c28f90e66d37101ab5db92` |

Ghidra databáza contains identical SHA-256 also MD5 programu. Was verify CRC and rozbalenie its dátového toku. Databáza was not importovaná to run Ghidra; its štítky sa použili as pomôcka during divide code. Provided `MAP.EXE.c` belongs inému, podstatne väčšiemu programu and nepoužilo sa as dekompilácia tohto `MAP.EXE`.

All addresses functions below are **relatívne k load DOS image**, spravidla `0000:xxxx`. For this skupinu applies `offset v file = 0x400 + xxxx`. Ghidra their denotes as `1000:xxxx`. actual segment during behu depends from miesta load DOS-om. Data segment is relatívne `0ABD`, its start v file is `0xAFD0`; grafická library uses relatívny segment `055F`.

- **P — confirmed:** directly čitateľné v byte or verify on provided data; high confidence.
- **O — derived:** interpretation toku code or purpose; listed obmedzenia remain podstatné.
- **N — unclosed:** available podklady nedávajú konečnú odpoveď.

Addresses odkazujú on files `evidence/functions/XXXX.asm.txt` v evidence package. Are v nich bytes instructions also their výklad. Three recognize vložené tables skokov are marked as data, aby sa nemýlili with instruction.

## Prehľad exactly 40 areas

| # | Area | Result | Status and main evidence |
|---:|---|---|---|
| 1 | Format programu | DOS MZ, 1 024 B header, 132 relocation; input `0000:2DF4`. | P; MZ header, CRT input |
| 2 | Match Ghidra podkladu | GZF contains obe exact identity EXE; 272 unikátnych štítkov `FUN_…`. | P; CRC, hashe, register štítkov |
| 3 | Version and origin | Copyright 1994 David P. Gray; exact number vydania undetermined. `MAPEDIT.EXE.c` is other program. | P/N; strings and address range |
| 4 | Spustenie | Argumenty → grafika → fonty → read mapy → initialization define and main loop → termination. | P; `2B38`, `2A10` |
| 5 | Command line | Branches `-e`, `-w`, `-o`, pozičné number block; interné number from nuly. | P; `2B38`, `2B2C` |
| 6 | Selection episodes | `-e` pripája provided string for `map.`, `walls.`, `objects.`; neprevádza ho on number. | P; `2BC2–2C20` |
| 7 | Numeric classes | `-w 1..72` and `-o 1..62` vypisujú class through terminate function; nula has other behavior. | P; `242A`, `2496`, `0026` |
| 8 | Names class | 73 name stien and 63 object including NULL; compare without distinguish size písmen. | P; DS `00B2`, `0144`, `52EC` |
| 9 | Header MAP | 2 B count blokov, 256 B tried stien, 256 B tried object. | P; `1042`, `2502`, comparison data |
| 10 | Cells mapy | 64 × 64 buniek; dvojica bytes wall/object; 8 192 B on block. | P; `1042`, `0BB4`, `1824` |
| 11 | Range read | Block starts on `514 + 8192 × index`; missing explicit reject negative index. | P; `1042` |
| 12 | New/vynulovaná map | Each cell dostane wall=1 and object=0; nejde only o rám okolo map. | P; `0EC4` |
| 13 | save | Target `1108` is only `C3 90` — RET and NOP. | P; physical offset `0x1508` |
| 14 | Flag zmien | C sets dirty; confirmed WITH ho zruší also without write. Save during odchode/change block also calls prázdnu function. | P; `21F0` |
| 15 | Format WALLS/OBJECTS | ID, štvorznakový symbol, name assetu, class, opis; parser requires four assign. | P; `2502`, DS `0DA4` |
| 16 | Record define | 92 B: two opisy after 41 B and two codes after 5 B, total for same ID walls and object. | P; `2502`, `0BB4` |
| 17 | Status rozhrania | Index bloku, type/start selection, filtre and flags; exact purpose state+6 remains open. | P/N; `2502`, `21D6` |
| 18 | Podlahové ID | Interval first and posledného record classes FLOOR according to poradia v file. | P; `2502`, `0BB4` |
| 19 | Match provided data | All 1 116 name class recognize; all 1 536 class bytes v header match. | P; independent parser |
| 20 | Missing define | MAP.2, block 4, cell (61,54): wall `37h`, object `17h`; wall does not have define. | P; physical offset map `0x7D7C` |
| 21 | Grafický mode | Main interface žiada mode `12h`; image náhľad žiada `13h`. | P; `00F0`, `175A` |
| 22 | Fonty and text | Registration `*.FON`, format set fontu, separate draw znakov and text. | P; `0178`, `0196`, `0206`, `0246` |
| 23 | Map symbol | Four znaky are programom for draw symbol; is not univerzálne game bit flags. | P; `0662`, `05EC` |
| 24 | Šestnásť tvarov | Third znak selects branch `0..9,a..f`; all sa nachádzajú v provided define. | P; `0662`, štatistika define |
| 25 | Direction šípky | During type `f` rozhoduje second hexadecimálny znak; fourth direction does not determine. | P; `0694–069F`, `08B9`, table `0AA3` |
| 26 | Layer and filtre | Najskôr wall, then object; F switches podlahy and O object filter. | P; `0BB4`, `21F0` |
| 27 | Key | C/F/O/Q/WITH/T, Escape and part navigačných rozšírených kódov. T calls empty hook. | P; `21F0` |
| 28 | Mouse | INT 33h reset, field, two tlačidlá, move, display and hide. Shift zamyká os. | P; `298E`, `2D10–2DDA` |
| 29 | Areas screens | Six obdĺžnikových zón; map has range pixel 6..453 v oboch osiach. | P; `0F64` |
| 30 | Editovanie kliknutím | call handler reads state+4 to local premennej and ends; cells does not change. | P; `21D6`, call `2AE1` |
| 31 | Informácie pod kurzorom | Prevod `(pixel−6)/7`; before read cells missing ohraničenie on 0..63. | P/O; `2A10`, `1824` |
| 32 | Selection palette | Existuje line also stránka 25 items; graf priamych call z main k nim nevedie. | P/O; `0D68`, `0E1C` |
| 33 | Selection image assetu | define → PCC/PCX or SEQ → výrez; this string does not have find priame napojenie z main. | P/O; `175A`, `153A` |
| 34 | PCX decode | 128 B header, manufacturer `0Ah`, jedna rovina, RLE; obmedzené check input. | P; `110A` |
| 35 | SEQ | Seven load fields; posledné four numeric values sa use as coordinate výrezu. | P/N; `1388` |
| 36 | VGA palette and image | Posledných 768 B GAME.PAL, prevod on 6-bit komponenty, porty 3C8/3C9; image to AND000. | P; `16B4`, `1678`, `1298` |
| 37 | Flood fill | Rekurzia to four susedov, náhradné wall ID, flag prerušenia and check remain zásobníka. | P/O; `1964`, `4BC2` |
| 38 | Auxiliary counters | Count object class `06h..3Dh`; search nepoužitého podlahového ID. | P; `1BBA`, `1C5A` |
| 39 | Doors and úseky stien | Orientačná table door and count directional úsekov; nevytvára hotovú geometriu. | P/O; `1CF8`, `1D82` |
| 40 | GDA and boundary complete | getenv(GDA) has zahodený result; odomknutie editora sa nepotvrdilo. Runtime, other build and 210 next štítkov remain mimo uzavretej parts auditu. | P/N; `2B1C`, `4F04`, register functions |

## save and editovanie: rozhodujúce evidence

| Miesto | Bytes or tok | Consequence |
|---|---|---|
| `0000:1108`, file `0x1508` | `C3 90` | Function sa okamžite returns; neotvára nor nezapisuje file. |
| `0000:22B2` | `CALL 1108` | Path save during odchode. |
| `0000:22EE` | `CALL 1108` | Path explicitného WITH; subsequently v `22F4` sets dirty on 0. |
| `0000:23AE` | `CALL 1108` | Path save during change map block. |
| `0000:21CC`, file `0x25CC` | `56 57 33 F6 33 FF 5F 5E C3 90` | Push, temporary zero registrov, their restore, return. None persistent work. |
| `0000:21D6`, file `0x25D6` | read `[state+4]` to `[BP−2]`, epilóg | None úprava map nor call náhľadu. |

**Interpretation with strednou confidence:** is variant určený especially on prezeranie map, with ponechanými time editora and remove or nedokončenými input function. Reason, autorov zámer and spôsob vzniku tohto variant are not preukázané. Prítomnosť slova „Save“ sama o sebe is not evidence functional save.

Graf only priamych near call reach z `2B38` 45 from 62 aplikačných candidates. Nedosiahne:

`007C, 00C8, 05BC, 0D68, 0E1C, 110A, 1298, 1388, 153A, 1678, 16B4, 175A, 1964, 1BBA, 1C5A, 1CF8, 1D82`.

This is result specific grafu, nie evidence impossible each indirect calls whether externého hit. Najsilnejším evidence obmedzenej editácie remain themselves empty bodies functions.

## Binary format MAP and verify blocks

All viacbajtové entire numbers v this špecifikácii are little-endian.

| Offset | Length | Meaning |
|---:|---:|---|
| `0x000` | 2 B | Count store map block |
| `0x002` | 256 B | `wall_class[wall_id]` |
| `0x102` | 256 B | `object_class[object_id]` |
| `0x202 + 0x2000 × i` | 8 192 B | Block with interným index i |

V block applies `cell_offset = 128*y + 2*x`, where `0 ≤ x,y < 64`. On this offset is wall ID, on nasledujúcom object ID. identify cells and identify its classes are difference values. For example `wall_id=0x37` does not mean automaticky `wall_class=0x37`.

| File | Count block v header | actual also očakávaná size | Range FLOOR ID |
|---|---:|---:|---|
| MAP.1 | 11 | 90 626 B | `BAh..DFh` |
| MAP.2 | 10 | 82 434 B | `C0h..E5h` |
| MAP.3 | 10 | 82 434 B | `C0h..E5h` |

Count 31 denotes **physical blocks these file**. Audit does not determine, koľko z nich specific game version sprístupňuje as hrateľné level.

read `1042` requires exact 514 B headers and 8 192 B vybraného block. When block is not v upper range, initializes náhradnú map. Negative index explicitne neodmieta; their praktický result depends also from behavior seek/read and error branches. During initial run parser `2502` znovu creates class tables z define. Neskorší prechod between block znovu loads header z MAP. For provided data are oba source identical.

### Specific unknown cell

| Property | Value |
|---|---|
| File and block | MAP.2, block 4, interný index 3 |
| coordinate from nuly | x=61, y=54 |
| coordinate from units | x=62, y=55 |
| Offset wall byte v file | 32 124 = `0x7D7C` |
| Dvojica bytes | wall `37h`, object `17h` |
| Class walls v header | 0, NULL |
| define in WALLS.2 | missing |

Initialization define gives nenájdeným item text `Unknown %04X` and code `F010`. For this wall therefore remains text **`Unknown 0037`** and predvolený map symbol; subsequent vykreslenie object can symbol walls prekryť. Is odvodenie z code, nie o nasnímaný result behu.

WALLS.1 also WALLS.3 item 0037 have, but with different assetmi and class. Their define cannot preniesť to episodes 2 without next evidence. Is not closed, whether is zámerný empty priestor, old record, missing define or combination file different pôvodu. V others check cell sa additional nedefinované wall/object ID nenašlo.

## Status and define v pamäti

Main map buffer is `DS:1332..3331`, nasleduje status on `DS:3332`. For state záhlavím is 256 define after 92 B; celok ends before `DS:8F40`, where sa uses auxiliary registerový block for mouse.

| Offset from stavu | Type | Meaning and confidence |
|---:|---|---|
| `+00` | u16 | current index bloku; P |
| `+02` | u16 | Choice list stien/object use in selection palette; P |
| `+04` | u16 | Start stránky selection list; P |
| `+06` | u16 | Initialize on 0; complete zamýšľaný purpose unclosed |
| `+08` | u16 | ID for filter object, original 0; P |
| `+0A` | u8 | Display podlahového intervalu, original 0; P |
| `+0B` | u8 | All objects, original 1; during nule sa displays only ID z +08; P |
| `+0C` | u8 | Requirement terminate; P |
| `+0D` | u8 | Neuložené change; P |
| `+0E` | 256 × 92 B | Table define according to ID; P |

| Offset v 92 B define | Length | Content |
|---:|---:|---|
| `+00` | 41 B | Opis walls, najviac 40 znakov and NUL |
| `+29` | 41 B | Opis object |
| `+52` | 5 B | Symbol walls, four znaky and NUL |
| `+57` | 5 B | Symbol object |

Input format parsera is doslova `%4x %4s %*s %s %[^\n]`. Assetové meno sa v this parseri skips. Náhľadová function ho neskôr reads separate. Parser reads lines to 132 B bufferu, short lines to eight znakov ignoruje, requires four assign and checks length symbol/opisu. Before index tables however is not explicitná check ID < 256. V provided 1 116 record is each identify v range, opisy sa zmestia and v individual file sa ID neopakujú.

## Štvorznakové symbol

Označme code as `ABCD`. AND and B sa prevádzajú z hexadecimálnych znakov; invalid znak gives nulu. C sa compares as znak: `0..9` and **small** `a..f`. D sa uses on tlačený znak during C=0. String `0000` sa skips entire.

| C | Kresliaca operation z code | Count v provided define |
|---|---|---:|
| 0 | Znak D farbou AND; if B≠0, pripraví sa pozadie | 299 |
| 1 | Dlaždica 7 × 7 farbou AND | 42 |
| 2 | Dlaždica with vzorom z DS:0044 | 22 |
| 3 | Dlaždica and stred 3 × 3 farbou B | 176 |
| 4 | Vzorovaná dlaždica and stred farbou B | 31 |
| 5 | Bodový vzor 7 × 7 with farbami AND/B | 47 |
| 6 | Vodorovný pruh | 42 |
| 7 | Zvislý pruh | 42 |
| 8 | Upper part farbou AND and lower farbou B | 55 |
| 9 | Small obdĺžnik with coordinate +3..+4, grafická operation 2 | 42 |
| and | Vyplnený obdĺžnik x+2..4, y+1..5 | 27 |
| b | Vyplnený štvorec x+2..4, y+2..4 | 84 |
| c | Vyplnený štvorec x+1..5, y+1..5 | 87 |
| d | Two diagonály, tvar X | 10 |
| e | Obdĺžnik 7 × 7, grafická operation 2 | 39 |
| f | Šípka farbou AND, direction according to B | 71 |

coordinate and numbers grafických operations are directly z argumentov call. Pixel result individual mode grafickej libraries was not compare with frame DOS behu.

For šípku applies B: **0 sever, 1 severovýchod, 2 východ, 3 juhovýchod, 4 juh, 5 juhozápad, 6 západ, 7 severozápad**, v coordinate screens. Values 8..15 do not have draw branch. Is not confirmation same number uhlov v game engine. For example `a2f0` selects farbu AND and šípku vpravo; posledná nula does not determine direction.

## Ovládanie and okraje interface

| Input | Behavior subtract z code |
|---|---|
| C | Confirmation Y/N, then all cells wall=1/object=0, dirty=1 |
| F | Switches display intervalu podláh |
| O | Switches all objects / only object ID from state+8 |
| WITH | Confirmation, empty auxiliary call, empty save, dirty=0 |
| Q or Escape | During change question on save, then termination |
| T | Empty hook `21CC` |
| Home, rozšírený code 47h | Interný index 0 |
| Hore or Page Up, 48h/49h | Zvýšenie index; local upper boundary missing |
| End, 4Fh | Last block according to count, case 0 |
| Dole or Page Down, 50h/51h | Zníženie index, if is väčší than 0 |
| Shift during movement mouse | Zámok jednej osi and set field kurzora |

Normal písmenové commands sa normalizujú on large písmená. Dialog accept only znaky z povolenej množiny; Escape is not všeobecnou possible zrušenia dialog Y/N.

Command line has different okrajové cases: numeric `-w`/`-o` vypisujú result through `0026`, which terminate program with code 1. Argument `0` prepadne to search name „0“, hoci nápoveda naznačuje range from nuly. Negative nonzero values prejdú znamienkovým compare with upper boundary; lower check before index tables missing. Naopak valid name, for example `-w WALL`, returns class, but main function return value nepoužije and continues v štarte. For switch sa loads next argument without miestnej check its prítomnosti. String for `-e` sa copies to small zásobníkových bufferov without visible length limitu. Are to static identify slabé miesta; pády nor other následky sa netestovali.

Function `0F64` distinguishes okrem map also five right panel. Their exact zamýšľané action sa nedajú restore only from itself obdĺžnikov, because obsluha kliknutia is prázdna.

| Area | x including boundaries | y including boundaries |
|---:|---|---|
| 1, mapa | 6..453 | 6..453 |
| 2 | 464..637 | 2..350 |
| 3 | 464..506 | 355..378 |
| 4 | 509..546 | 355..378 |
| 5 | 549..576 | 355..378 |
| 6 | 579..637 | 355..378 |

V main loop calculation areas nechráni all subsequent read pod kurzorom. Modelový example pixelu (638,470) can cell (90,66) and offset 8 628, mimo 8 192 B map. Static therefore existuje path k read mimo map bufferu. Is not verify, what text, grafickú error or other prejav to spôsobí during specific behu.

## Classes: what sa confirm and what z name nevyplýva

Complete exact map all 136 name is v `evidence/class_names.csv`, including addresses pointer and string v EXE. Selected skupiny:

| Druh | Class ID hex | Names |
|---|---|---|
| Walls | 0D..14 | WARP_1..WARP_8 |
| Walls | 15..18 / 19..1C | WARP_WITH1..4 / WARP_L1..4 |
| Walls | 1D..24 / 25..2C | WARP_E1..8 / WARP_C1..8 |
| Walls | 2D / 2E / 2F / 30 | WALL_EX / WALL_EX1 / WALL_EX2 / JAMB |
| Walls | 31..40 | DOORV/H and párové variant L, L2, L3, I, R, U, C |
| Walls | 41..48 | TURN, RETREAT, FLEE, FLOOR, SAFESPOT, ACTIONSPOT, TRIGGER1, TRIGGER2 |
| Objects | 01..07 | HERO, START, SECRET, IMPACT, MISSILE, VAPID, CAUSTIC |
| Objects | 08..25 | GUARD1..GUARD30 |
| Objects | 26..2E | SAFE, TRUNK, PUSH, ACTION, PERMEABLE, DUMB, DUMB4, DUMB8, ELEVATED |
| Objects | 2F..3E | KEY, IDCARD, GOLD, MONEY, FOOD, AID, LIFE, WEAPON, RADAR, BATTERY, AMMO, CRYSTALB, MAGICEYE, PENTAGRAM, SCROLL, UIFOBJ |

Is prekladové and klasifikačné tables MAP.EXE. Name classes v nich itself nepotvrdzuje its complete game mechaniku, využitie in all versions nor existenciu corresponding predmetu v specific úrovni. Especially GUARD1..30 does not mean 30 separate implement type AI v this editore.

## Image and auxiliary branches without find priameho napojenia

**PCX/PCC/SEQ.** Function `175A` searches ID v define and preberá meno assetu. `153A` during mene with bodkou test file `.seq` according to parts before element bodkou; during mene without bodky test `.PCC`, then `.PCX`. `1388` search sekciu označenú `image_id`, parsuje format `%s%d,%d,%d,%d,%d,%d` and požaduje seven assign. First two numbers do not have v preskúmanom copy image využitie; posledné four tvoria výrez. Exact meaning first dvoch čísel remains unclosed. load PCX sa repeated uses, pokiaľ sa nezmení its meno.

**Obmedzenia PCX.** `110A` checks identify výrobcu 0Ah and jednu rovinu, but v preskúmanom tele nekontroluje all needed own headers, including bits-per-pixel and bytes-per-line. Rozmery odvodzuje z min/max coordinates. Compress tok interpretuje as byte pixely with PCX RLE. Internal loop repeated neobmedzuje length on count remain pixel. Negative, damage or nepodporované input therefore cannot považovať for safely reject. Is static findings; damage files sa to original programu nepúšťali.

**VGA.** `1298` prenáša including oboch krajov zadaný výrez to segment AND000 with krokom screens 320 B; source step is width decode image. `16B4` vezme posledných 768 B `GAME.PAL`, each value prevedie helper `(v >> 2) & 63` and `1678` their writes to DAC. This routine nerozlišuje „čistý 768 B file“ from väčšieho file with palette on konci. Itself name GAME.PAL does not determine its complete format.

**Flood fill.** `1964` changes wall bytes and rekurzívne navštevuje four susedov. Uses original ID z `DS:1330`, new ID z `DS:956E` and flag prerušenia `DS:94D4`. Checks coordinate and small remain zásobník. call initialization this operations sa v restore directly grafe did not find, therefore is not confirmed zamýšľaný command nor korektnosť celej lifetime these global values.

**Counters.** `1BBA` count cells with class object from 06h after 3Dh including; mark result jednoducho as „count enemies“ by was incorrectly. `1C5A` test podlahové ID počínajúc element+1 and returns relatívny result. During vyčerpaní range can be result for its koncom; error and empty range are not closed runtime test.

**Directional úseky.** `1CF8` distinguishes 16 class door 31h..40h on striedajúce sa V/H dvojice: V vyhovuje direction 2/3, H direction 0/1. `1D82` iterate through map after row or column according to direction, compares current and adjacent cell and count začiatky úsekov. Uses classes 01h..30h, change ID, doors, object class SECRET=3 and osobitné branches for WALL_EX1/2=2Eh/2Fh. Condition okolo these class are confirmed; game meaning „zničiteľná wall“ sa itself editorovým count define nepreukazuje. Function returns count, nevypĺňa list geometrií. Interim status úseku sa v pozorovanom code nenuluje on start each row; boundary dôsledky require diferenciálny test.

## Open questions and specifically additional verify

| Question | What we already know | Next rozhodujúci test |
|---|---|---|
| Why is editor neúplný? | Three bodies are empty or without persistent work. | compare other autentický MAP.EXE according to hashov, nie according to name. |
| Which vydanie to is? | Copyright 1994 and exact hash. | Dobový package with čitateľným pôvodom and dátumom vydania. |
| Save nejaká hide path? | Three key path save through RET. | V izolovanom DOS behu track input to `1108` and DOS writes; hash copies MAP before/after. |
| Can be zapojiť náhľad or selection? | Priamy graf z main k nim nevedie. | Track possible indirect calls and key/mouse; breakpointy `175A`, `0E1C`. |
| On what was state+6? | Initialization on nulu. | Comparison plnej versions editora or dynamic writes on `DS:3338`. |
| What are first two numbers SEQ? | Parser their loads, výrez their does not use. | Identical original SEQ and code their next konzumentov. |
| What exactly vykreslí each symbol? | Restore branches and argumenty grafických primitív. | Frame mriežky all 16 tvarov z original DOS behu. |
| Why v MAP.2 missing wall 0037? | Jedna cell, class 0, missing text record. | compare additional autentické páry MAP.2/WALLS.2 and game loader danej versions. |
| As sa prejaví kurzor mimo map? | Neobmedzený index can prekročiť buffer. | Breakpoint `1824`, movement to right and spodného panel, log effect adries. |
| Aké are boundary image dekodérov? | Static missing viaceré check. | Small check PCX vzorky with paddingom and hraničným RLE v izolovanom emulátore. |
| Is counter úsekov ekvivalentné game? | Získaná orientation and rozhodovacie condition editora. | Comparison result with specific DOS/Win16 game binary on same map. |
| What robia remain knižničné functions? | next 210 štítkov is evidovaných; selected CRT auxiliary preskúmané. | Separate audit knižničného code, call DOS/BIOS and grafických backendov. |
| Funguje this tool in Windows 3.11? | Preskúmaný file is DOS program. | Test specific DOS relácie pod specific konfiguráciou Windows; this audit ho nevykonal. |

Findings sa neprenášajú automaticky on NITE3W.EXE, other MAP.EXE, plný MAP.EXE nor on all vydania Windows. These programy needs to compare according to exact binary identít and separate tokov code.

## Reprodukcia and content evidence package

`audit_map_exe.py` execute **20 úspešných static check**. Checks identitu EXE, MZ, CRC and match GZF, register functions, priamy graf, define, map rozmery, class tables, missing cell, exact empty functions, calls save and directional table šípok. Number 20 denotes check skriptu, nie 20 run original game. coordinate example kurzora is výpočtový model.

Package contains:

- `audit_map_exe.py`: reprodukovateľný audit for this hash, Python 3 and GNU objdump.
- `evidence/function_catalog.csv`: all 62 aplikačných candidates with rolou, address and state v directly grafe.
- `evidence/functions/`: 62 výpisov original bytes and instructions; three vložené skokové tables are vyznačené as data.
- `evidence/support/`: input CRT and selected verify knižničné auxiliary.
- `evidence/class_names.csv`: all 136 exact name tried and their umiestnenie.
- `evidence/definition_records.csv`: 1 116 define with original file and riadkom.
- `evidence/map_blocks.csv`: 31 block with offset, hashmi and nedefinovanými ID.
- `evidence/undefined_cells.json`: exact unknown cell.
- `evidence/asset_crosscheck.json`, `validation.json`, `input_manifest.json`: results kontrol and identity vstupov.
- `evidence/direct_app_calls.json`, `direct_reachability.json`, `ghidra_function_symbols.json`: hranice and podklady grafu.
- `evidence/data_strings.csv`, `glyph_selectors.json`: data strings and pokrytie symbolov.

Original EXE, GZF, image nor entire game data sa to output package znovu nepribaľujú. On repeated auditu vlož original MAP.EXE and MAP.EXE.gzf to `inputs/`, nine dátových file to `assets/` and run `python3 audit_map_exe.py`. Skript original input only reads. Exact očakávané identity are v manifeste.