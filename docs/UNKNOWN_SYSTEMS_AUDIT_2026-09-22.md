# Unknown systems audit — 2026-09-22

This report consolidates unresolved and newly prioritised targets from the
cross-session Nitemare 3-D analyses. It is an audit plan, not a claim that
every hypothesis is present in the original game. Evidence labels are
intentional: `VERIFIED_EXE`, `VERIFIED_DATA`, `VERIFIED_SAVE_LAYOUT`,
`BEHAVIOURAL`, `INFERRED`, `PARTIAL`, and `TODO`.

The machine-readable counterpart is `src/re/UnknownSystemsAudit.hpp`, covered
by `n3d_unknown_systems_audit_test`.

## Highest-value end-to-end chain

```text
GUARD AI -> attack sequence/frame event -> projectile or weapon
 -> collision -> damage/difficulty -> strength <= 0
 -> death/sound -> score, drop, morph or removal
```

This chain can resolve AI timing, projectile representation, damage/immunity,
SND mapping, score assignment, Dracula-to-Bat behaviour and hidden spawn paths.

## Current evidence anchors

| Area | Confirmed/high-confidence anchor | Remaining question |
|---|---|---|
| GUARD | base `0x93AE`, stride 26 B, capacity 100; states `00..15`; pain `15h`; score switch `08..20` | exact state names, movement/LOS/attack timing, GUARD26–30 |
| Combat | strength `+10`; health `0x4C1D`; ammo `0x4C1F/0x4C20/0x4C44`; difficulty `0x4C14` | visible enemy/projectile binding, RNG/resistance, fire probability |
| Runtime | OBJECT count `0x7E58`; GUARD count `0x7E5E`; OBJECT 28 B | runtime spawn/despawn and projectile record type |
| Walls | property tables `0x7E94/0x7F94`; dispatcher target `SEG3:2334–247A` | handler table and common trigger/script mechanism |
| Renderer | VEC 28 B/1000; lists 333; owner `0x53FE`; occlusion `0x58FE`; spans 50×20 B; sprites 100×18 B | conflict math, flags `04/08/10`, texture-U and animation |
| MAP | 514 B header plus 64×64×2 payload; 31 supplied levels including E1M11 | header fields and technical level ceiling |
| Saves | USER.SAV slot `0xD6E7`; unknown block `0xC403`, 336 B; word `0xD6E5` mirrors `0x7E60` | semantic ownership and event diffs |
| Resources | SND directory 160×6 B; MIDI IDs 1–15; SFX 34–110; FLI deltas | event-to-SND map, UIF reserved slots, playback fidelity |
| NE/BSF | Win16 NE has 10 segments; BSF has six known xrefs | relocation classification and BSF algorithm |

## New discovery targets

### GUARD decision tree and sequence events

Audit every read/write of GUARD `+06`, `+0A`, `+0B`, `+0C`, `+0E`, `+10`, then
join it to sequence-definition and SND calls. A sequence may encode frame
duration, attack event, sound, movement and next-sequence transitions. Do not
assign HP, speed, alert radius or immunity per visible name until class binding
is recovered.

Classify GUARD26–30 by creation and use. Candidates include dancer, projectile,
helper, scripted replacement or unused classes; existence alone proves none of
these interpretations.

### Spawn, collision and projectile classification

Partition count/record writes into level load, wall trigger, drop, projectile,
replacement and removal. Build a matrix for `PLAYER×WALL`, `PLAYER×OBJECT`,
`PLAYER×GUARD`, `PROJECTILE×WALL`, `PROJECTILE×GUARD`, `GUARD×WALL` and
`GUARD×GUARD`. Record exact `TEST/AND/OR/CMP` masks before naming flags.

### Death, score and morph

The recovered score switch gives Dracula class `0` and Demon class `250`.
That is direct score-dispatch evidence, not proof that Dracula-to-Bat is absent.
Trace `strength <= 0` through death sequence, sound, score, counter, object
replacement, item drop and final removal.

### Wall dispatcher and E2M4 `0x37`

Create `wall class -> handler -> condition -> map write -> sound ->
animation/resource -> object/guard write` for `WARP_L*`, `WARP_*`, `WARP_E*`,
`WARP_S2`, `CONTROL`, `SPECIAL1`, `ONE_SHOT`, `REVWALL` and `DOOR*`.
E2M4 cell `(61,54)` with wall `0x37` is a candidate anomaly, not proof of a
deleted class. Compare MAP, WALLS.2 and EXE handler domains first.

### Renderer, timing and hidden content

Keep the established projected-boundary-vector model. Audit VEC `+01/+02/+03/
+04/+08`, flags `04/08/10`, owner conflict `FUN_1018_3564`, texture-U
`FUN_1010_6422`, and animation path `FUN_1010_65A6`. Locate RNG/seed and main
logical tick; DEMO records are 8 B but determinism still requires evidence.

Use four hidden-content sets: `DEFINED`, `PLACED`, `REFERENCED`, `EXECUTED`.
Report `DEFINED−PLACED`, `REFERENCED−PLACED`, `DEFINED∩PLACED−EXECUTED`, and
`EXE handlers−known classes` across IMG, OBJECTS, WALLS, SND, UIF, MAP and EXE.

## Prioritised next passes

1. GUARD state/sequence/SND XREF join and GUARD26–30 classification.
2. Wall dispatcher plus E2M4 `0x37` validation.
3. Attack-to-damage-to-death-to-score/morph trace.
4. RNG/main tick and DEMO determinism.
5. MAP header differential and USER.SAV 336-byte event diff.
6. BSF consumer/version diff and NE relocation classification.
7. Mathematical hidden-content scan and UIF/SND/FLI edge cases.

Do not publish one overall percentage. Keep format knowledge, executable
control-flow recovery and behavioural equivalence as separate progress axes.


---

## 2026-09-23: review of the full 40-area unknowns table

This appendix reconciles the open-area register against the targeted DOS v2.0 and Win16 1.10 audits. It records what is evidenced, what remains open, and the proof needed to close each area. It does not claim that all areas are resolved. The source register is in Slovak to match the project owner's working language.

## Druhý analytický prechod: výsledok ku všetkým 40 položkám

Tento prechod zosúlaďuje register s novšími priamymi auditmi Win16 1.10 a DOS v2.0. Hodnotenie sa vzťahuje na presne doložené časti; položka zostáva čiastočná, ak je otvorená čo len jedna dôležitá vetva. „Uzavretý výrez“ neznamená uzavretie celého subsystému. Bez živého porovnávacieho behu sa runtime časovanie a obrazová zhoda označujú ako otvorené.

| # | Výsledok analýzy a doložené fakty | Čo je naozaj otvorené a aký dôkaz to uzavrie |
|---:|---|---|
| 1 | **Štart – čiastočné.** Win16 má spoločnú stavbu `map.N`, `img.N`, `demo.N`; `-r` zapína záznam DEMO. Obe skúmané platformy obsahujú `Invalid command line`, ale samotný text neurčuje parser hry. | Zostaviť WinMain/DOS štartovaciu vetvu, zoradiť init grafiky, času, vstupu a súborov; nájsť všetky exit a chyby open/load. Rozlíšiť herné argumenty od runtime/MFC textov. |
| 2 | **Hlavný cyklus – scheduler DOS zmapovaný, presná sémantika stále P0.** `FUN_1000_e964` opakuje `c1a8` v hernom stave. `c1a8` má samostatné 8 Hz a predvolené 25 Hz vetvy; update call order je `c0d8 → bf36 → A0B8 → A236 → 0AEA → 8230 → lag hook → 70D6`. Win16 `0x46B6` prepína herné vetvy a DEMO dispatcher sa volá v stave 8. | Pomenovať a rozhraniť jednotlivé callee, najmä zlúčený blok `1000:70D6`, oddeliť input/player/AI/combat/world/render a spárovať s Win16. Overiť správanie pri 65 ms lag hranici a 500 ms rebase. |
| 3 | **Časovanie – významná časť potvrdená.** Win16 kalibruje päť update priechodov. DOS nastavuje `0x3CC2=25`; `FUN_1000_bef4` z toho počíta 25 krokov/s (40 ms), `FUN_1000_beb4` vedie samostatný 8 Hz čítač a `FUN_1000_bf7a` meria desať update priechodov. `FUN_1000_c1a8` ukazuje poradie scheduleru a 500 ms rebase. DOS nastavuje aj RTC vektor `INT 70h` s handlerom `11EE:0x0BCC`; alternatívna cesta používa BIOS tick `0x46C/0x46E`. | Zistiť presný význam každého scheduler callu, RTC handlera a `0x3CC7/0x3CCF` režimov; overiť wrap, pauzu/LOAD, lag vetvy a runtime čas pri presnom builde. DEMO `0x53DC` ostáva osobitný čítač. |
| 4 | **RNG – helper lokalizovaný, algoritmus otvorený P0.** DOS volania smerujú cez `1000:0xFD40`, ktorého stub skáče na `11EE:0x31F8`. Calleri používajú bit `&1` aj modulo `0x19`; to potvrdzuje náhodný výber, nie seed ani vzorec generátora. | Dekódovať cieľový segment/overlay a jeho zápisy stavu; nájsť seed/reset a všetky callery; zmerať bias `&1`/`%n` a porovnať DOS s Win16 a DEMO replay. Kontaktové damage a guard wait rozsahy ostávajú doložené samostatnými callsite auditmi. |
| 5 | **Pamäť a cache – otvorené.** Pevné kapacity polí sú potvrdené; USER.SAV obsahuje VEC/OBJECT/GUARD/door, panel, projectile, push, automap a remap bloky. | Chýba alokačno-vlastnícky graf, životnosť far pointerov po level change/LOAD a presná DOS XMS/disk-cache vetva. Treba sledovať alloc/free a všetky pointer rebasing writery. |
| 6 | **Level load – čiastočné.** MAP má 514-bajtovú hlavičku, dve 256-bajtové class mapy a 64×64 bunky po 2 B; finálne dáta obsahujú 31 levelov. Win16 staví názvy MAP/IMG/DEMO z rovnakého selektora. | Presné poradie parser → steny/vektory → objekty/guardy → dvere/panely/pushes → spawn; reset persistentných polí; DOS hranice `1000:84FE` a porovnanie level-init buildov. |
| 7 | **Vstupy – Win16 klávesnica prevažne zmapovaná.** Šípky menia `0x3756`; ľavý/pravý Shift nastavujú `0x40/0x20`, Ctrl `0x80`, Alt používa `0x3757`; Q prepína hudbu, R efekty, Alt+Enter režim okna. DOS číta aj klávesnicu, myš a joystick. | Neuzavreté sú Win16 myš/joystick, DOS scancode mapovanie, dead-zone, strata fokusu a kombinované udalosti. Raw caller test pre stavový bit `0x8000` a tri systémové klávesové callery. |
| 8 | **Pohyb/kolízia hráča – čiastočne potvrdené.** Svetové súradnice sa prevádzajú na dlaždice posunom o 6; hráčsky commit zapisuje X/Y a pri zmene bunky posiela event `0x16`. Známe sú tri helpery pred commitom. | Presný polomer/rohy, axis slide pri každej stene, diagonály, moving blockers a poradie helperov pri obsadených dverách. Rozobrať tri pre-commit helpery a otestovať hraničné súradnice v origináli. |
| 9 | **HP, smrť a obnova – čiastočné.** Guard damage podľa vzdialenosti/class, difficulty a damage writer/ death vetvy sú analyzované; existujú priame vetvy hráčskeho kontaktového damage. | Kompletná matica hráčskych HP writerov, invulnerability/stagger, smrť, respawn/restart a limity heal/pickup. Porovnať všetky zásahy v rovnakom ticku, najmä hazard + guard/projektil. |
| 10 | **Inventár – čiastočné.** Objektové triedy pokrývajú kľúče, karty, jedlo, zbrane a muníciu; sú známe viaceré ammo pooly a ich spotreba pri streľbe. | Limity, duplicitný pickup, spotrebovanie ID karty/kľúča, čo sa prenáša cez level/episode a čo sa mení pri difficulty/restart. Sledovať každý writer inventára aj save/load. |
| 11 | **USE – vysoké pokrytie, nie uzavreté.** Centrálna USE vetva, karty, secret panely, remote dvere `0x1E/0x1F`, väčšina warpov a bežných dverí sú doložené. | Zostávajú SAFE/TRUNK/radio/special station handlers, trezorové kombinácie a kombinácie class × map variant. Zostaviť callsite → class → runtime record → MAP write pre každú triedu. |
| 12 | **Teleporter/výťah – hlavné cesty potvrdené.** WARP rodiny a elevator/level-up triedy sú v dátach a v dispatcheroch; voľná susedná dlaždica sa používa v teleport výbere. | Cieľová bunka pri obsadenom priestore, konečný smer, zrušenie výberu, spotreba podmienok a rezervované `0x25–0x2C`. Porovnať výslednú pozíciu/smer na každom mapovom variante. |
| 13 | **GUARD AI – kostra potvrdená.** 26 B záznam; stavy `0x00–0x15`; LOS cez najviac 8 buniek, približne 135° v bežnom smerovom režime, proximity <65 world units; známe sú časti stratégií 1–3. | Writer → handler → timer → movement → animation → sound matica pre každý state/strategy/class; sluch, alarm šírenie a stavy `0x0A–0x0D` vrátane boss vetiev. Potvrdiť v 1.10, 1.8 a DOS. |
| 14 | **Bossovia/zvláštni aktéri – čiastočné.** Dracula-Bat je druhá fáza triedy `0x14`; Dancers sú spojené s class `0x21`/ACTIONSPOT. GUARD25 vyzerá genericky a nedokončene, nie ako potvrdený boss. | Cannon/gargoyle, Dancers script, GUARD25 grafika/seqdef/placement, Hammerstein/Penelope story flagy a všetky morph writers. Odlíšiť potvrdený runtime prechod od hypotézy o cut content. |
| 15 | **OBJECT/GUARD polia – layout potvrdený, úplná mapa nie.** Win16 OBJECT 28 B, GUARD 26 B; známe sú HP, state, strategy, facing a vybrané projection/movement polia. | Všetky read/write offsety podľa class a životnosti; rozpor `GUARD+0x12` pain timer vs cache invalidation držať otvorený do úplného XREF prechodu. Mapovať aj vložený OBJECT v projectile recorde. |
| 16 | **Zbrane/hitscan/damage – jadro doložené.** Weapon 2 je hitscan; 0/1/3 používajú projektily. Win16 cooldowny sú `[2,1,3,1]` simulačných krokov; ammo pooly a class/difficulty vetvy sú zmapované. | Presný distance→base damage, hitscan tolerancie a blokovanie, spread/range, všetky class × weapon × difficulty prípady, a callsite pre jednotlivé melee/attack prezentácie. Zosúladiť s nejednotnými staršími damage opismi. |
| 17 | **Projektily – veľká časť uzavretá.** Pool 8×42 B = USER.SAV 336 B; Bresenham podkroky, map/guard collision, impact animácia a save/load sú doložené. ±20 test je projekčný/cull krok, nie potvrdený lifetime. | Presná rýchlosť v sekundách, nepomenované bajty, mapový far pointer počas letu, všetky damage typy a DOS ekvivalent. Otestovať prečo sa vzdialený slot uvoľní a či ide o hard range alebo iba render cleanup. |
| 18 | **Hazardy – oheň uzavretý na damage za update.** Veľký/stredný/malý fire objekty dávajú 100/10/2 HP na simulačný update. | Zmerať DPS pri kalibrovanom intervale; preveriť ostatné contact hazards, súbeh damage, invulnerability a či closing door crush poškodzuje aktéra. Fire class mapping samotný už neviesť ako neznámy. |
| 19 | **Dvere/panely/pushes – dátové jadro potvrdené.** Kapacity 64/32/12; záznamy 22/22/6 B; panely môžu prepájať štyri strany, dvere sa posúvajú po krokoch. | Dosiahnuteľnosť každého stavu, stair-trap push výnimka, blokovanie pri zatváraní a class-specific eventy/tick jednotka. Riadené testy so strážcom/objektom v priechode. |
| 20 | **Špeciálne steny – Win16 explózia s cleanup potvrdená.** Wall class `0x2D` po animácii odstraňuje mapový blokovací bajt; ONE_SHOT/SPECIAL1 majú identifikované wall IDs. | DOS completion call target sa rozchádza s Ghidra hranicou; ONE_SHOT/SPECIAL1 trigger a finálne mapové/flag zmeny zostávajú otvorené. Vytiahnuť call trace a porovnať bunky pred/po v oboch buildoch. |
| 21 | **SEQDEF – všeobecný dispatcher čiastočne uzavretý.** Termín je na `object+0x08`, frame count v seqdef `+0`, interval `+2`, alternatívny pointer `+4`; loop a osem alternatívnych slotov sú opísané. | Získať konkrétne 90 B seqdef a 10 B frame záznamy pre všetky assety; pomenovať frame políčka, intervaly, event/SFX hooky a typovo odlíšiť GUARD vs wall/object seqdef. |
| 22 | **Level scripts – čiastočné.** TRIGGER1/2 sú wall class `0x47/0x48`; `DAT_51A4–51AB` sú globálne event/guard/shade flagy s viacerými potvrdenými callers. | Úplné condition → flag → MAP write → SFX → reset/save grafy; sémantika `0x51A7–0x51AA`, Safe/combo `0x51A4` a dĺžka story stavov. Overiť po LOAD/restart. |
| 23 | **Postup/finále/skóre – čiastočné.** Je 31 finálnych máp; class score a hlavné episode/level exit cesty sú čiastočne doložené. | Úplný E3M10 event sled po FLI/menu, restarty a score výnimky; vplyv difficulty na score a všetky koncové príbehové podmienky. Potrebný raw trigger/caller graf a beh. |
| 24 | **VEC/geometria – renderer kostra potvrdená.** 1000×28 B VEC, štyri zoradené skupiny po 333; 64×64 map scan, susedné hrany sa spájajú a vlastník steny sa ukladá do stĺpcového bufferu. | Všetky VEC flags, životnosť a invalidácia zoznamov po wall mutation/load; vysvetliť presný vzťah VEC[1000] ↔ VECLIST[4×333] v oboch buildoch. |
| 25 | **Projekcia/clipping – hlavný tok doložený.** Win16 oreže near-plane okolo `0x4000`, projektuje vektorové konce a rozhoduje viditeľnosť po stĺpcoch. | Všetky orientačné dvojice pri prekrytí, equality/tie prípady, near-plane okraje a fixed-point rounding. Porovnať raw frame capture z pevne zadanej pozície. |
| 26 | **Texture/transparency – otvorená pixelová hranica.** Projekcia/span má zmapovaný 20 B record a 16.16 vertikálnu interpoláciu; shade/remap tabuľka má potvrdenú funkciu. | Finálna texture U/V adresa, texel writer, masked/transparency steny, čiastočne otvorené dvere a tieňové výnimky. Dokončiť od span emittera až po framebuffer zápis. |
| 27 | **Sprites/order – čiastočné.** Je 350×28 B OBJECT pool, projekčný visible-object prechod a wall-owner buffer pre occlusion. | Presné triedenie, rovnaká hĺbka, clipping, wall/sprite order, priority a limit pre preplnený onscreen list. Potrebný call graph sort → span/sprite write. |
| 28 | **Palette/video – palette transform potvrdený.** 236 základných farieb sa remapuje podľa úrovní stmavenia; Win16 používa WinG/DisplayDIB a DOS VGA helpery. | Všetky používateľské cesty remap/transparent colors, rezervované farby a bitovo presná DOS/Win16 výstupná zhoda. Zmerať identický frame a porovnať 320×200 palette bytes. |
| 29 | **HUD/automap – dáta čiastočne potvrdené.** Save obsahuje 4096 B automap plochu; existujú HUD a portrait draw routiny. | Význam všetkých raster hodnôt/farieb, dirty flags, portrait HP prahy, značky a spotreba máp metrov. Sledovať každého writeru automap buffera a HUD update. |
| 30 | **Menu/texty/config – čiastočné.** Q/R a Alt+Enter klávesy, difficulty/UI a remote door/cannon menu majú priamo doložené vetvy. | Ukladanie konfigurácie, všetky dialog/message vetvy, command-line parser, MFC/runtime texty a okrajové textové clipping. Nevyvodzovať `-debug` iba z `debug.txt`. |
| 31 | **MAP/IMG/UIF/loadery – jadro MAP potvrdené.** MAP header/cell layout a file I/O/resource loader vetvy sú známe; seqdef loader načíta pevné 90 B bloky. | Runtime mutácie MAP, zvyšné IMG metadata a frame linky, UIF sloty 0–2, prázdne sloty 17–31 a presné asset aliasy. Overiť loader → renderer/dispatcher XREF. |
| 32 | **Zvuk/hudba – kontajner čiastočne zmapovaný.** SND.DAT má 160 slotov, 88 nenulových položiek; existujú Q/R toggle a event SFX volania. | Úplná event→slot tabuľka, sample/codec/rate a dôvod chybných exportov, priority/prekryv zvukov, MIDI loop a DOS/Win16 prehrávanie. |
| 33 | **ENDING.FLI – otvorené okraje.** Hlavička uvádza 488 frame; fyzická kontrola našla 489 blokov a najmenej šesť prázdnych koncových blokov. | Zistiť, ktoré bloky sú padding/EOF, čo prehrávač považuje za koniec a či všetky 489 záznamy majú valídny frame header. |
| 34 | **Mapy/assety – obsah zmeraný, runtime nie.** 31 finálnych mapových blokov; E1M3 a E1M11 zdieľajú wall plane, no líšia sa v 17 object cells; E2M4 má známu anomáliu. | Všetky class/asset použitia naprieč epizódami a buildmi, nepoužitý content a aktérske hraničné počty; pre DEMO.2/3 preveriť všetkých 31 máp. |
| 35 | **USER.SAV – layout z veľkej časti vyriešený.** Slot `0xD6E7`; 336 B blok je 8 projektilov, 4096 B automap, 256 B palette remap; 32 B secret panel a ostatné bloky majú reader/writer pomenovania. | 94 B hráčsky blok, osem globálnych flagov, 64 B guard wake cache indexy a rebasing všetkých timer/pointer polí. Porovnať save-load cez level change. |
| 36 | **DEMO – formát a stavový automat prevažne uzavreté.** 6 B hlavička, 8 B record; kód eventu + vstupná maska + nulový/nepoužívaný bajt + čas; hlavička `(10,5,20)` sú pohyb/turn/substep parametre; state 1–5 a timed playback sú potvrdené. | Začiatočná mapa/spawn, reprodukovateľný RNG, EOF/prerušenie, wall-clock dĺžka counteru, účel `+3`, level match DEMO.2/3 a DOS parita. |
| 37 | **Debug/CMD/cheats – čiastočné.** `debug.txt` aj `Invalid command line` sú v oboch skúmaných binárkach; Win16 logger a `-r` DEMO recording sú doložené. | Cross-reference fyzických stringov, všetky command-line callers, logger activator, rozdiel od CRT/MFC parsera a dosiahnuteľnosť cheat/debug gate. |
| 38 | **Platformová vrstva – základ identifikovaný.** DOS je MZ; Win16 NITE3W je NE; Win16 používa systémové tick API a WinG/DisplayDIB, DOS BIOS/VGA časovanie a výstup. | Message loop, callbacky, focus/device recovery, cleanup, import API celý a DOS XMS/disk cache. Potrebné sú exact-hash build exports a caller graph. |
| 39 | **Register funkcií – úplnosť inventára nie je sémantická úplnosť.** Známe je 519 DOS + 967 Win16 = 1 486 definícií; všetky sú klasifikované, no starší ručný detail pokrýval 200 z každej vetvy a ďalšie rutiny sa rozoberali cielene. | Uzavrieť skutočné hranice veľkých merged blokov, near/far/nepriame xrefy, callbacky a dead-code kandidátov; aktualizovať každý entry na CONFIRMED/PARTIAL/CANDIDATE pre presný build. |
| 40 | **Verzie/validácia – čiastočné.** Function pairing podporuje 429/519 DOS a 929/967 Win16 matchov; nové audity oddeľujú presne hashované buildy a neprenášajú závery automaticky. | Behaviorálna parita DOS/Win16/shareware/full, rozpory segmentových hraníc, obraz/zvuk/trace a identita buildov. Pre každú mechaniku treba rovnaký vstup, mapu, tick a porovnateľný výsledný stav. |

### Čo sa po zosúladení už nemá opakovať ako úplne neznáme

1. `USER.SAV +0xC403` nie je anonymný 336-bajtový blok: je to osem 42 B projectile záznamov.
2. Fire damage `100/10/2` HP na simulačný update je potvrdený; neznáme ostáva DPS pri konkrétnom kalibrovanom intervale a ostatné hazardy.
3. Win16 explodujúca stena má completion cleanup mapového blokovania; iba DOS call target a presná stopa ostávajú otvorené.
4. DEMO formát, hlavičkové pohybové parametre, hlavné input bity a state 1–5 sú rozpoznané; mapovanie levelu DEMO.2/3 a wall-clock dĺžka ešte nie.
5. Win16 klávesové udalosti a shade/remap funkcia sú doložené; nezamieňať to s úplným input-device alebo renderer uzavretím.
6. 1 358/1 486 párovaných funkcií je podobnosť identity; nie 91,4 % pochopenia hry. Súhrnné 50–60 % je len starší pracovný odhad, nie meraná metrika.

### Závislostné poradie ďalšej práce

1. **Funkčné hranice + hlavný cyklus + čas + RNG:** položky 39, 2, 3, 4, 1, 6. Bez toho nemožno presne pomenovať poradie ani zopakovať správanie.
2. **Polia a kolízny model:** položky 15, 8, 13, 19. Uzavrieť read/write maticu, potom hráča, guardov, dvere a push.
3. **Combat/hazards:** položky 16, 17, 18, 9, 14. Spojiť input → fire → collision → damage → pain/death → sound.
4. **Skripty a sekvencie:** položky 20, 21, 22, 23, 11, 12. Overiť animáciu/event → map mutation → level transition.
5. **Pixelová zhoda:** položky 24–29 a 28. Dokončiť span/texture/sprite/HUD/video od raw write po capture.
6. **Dáta a platformy:** položky 31–38, 5, 10. Uzavrieť load/save, assets, demo, debug a DOS/Win16 cross-tests.

Pri ďalšom prechode treba po každom uzavretom výreze uviesť build/hash, adresu rutiny, prečítané/zapísané polia a test. Ak chýba runtime dôkaz, ponechať presne označené PARTIAL/UNKNOWN namiesto percentuálneho odhadu.

**Podklady pre tento zosúladený register:** `Nitemare3D_deep_unknowns_2026-09-23.md`; `Nitemare3D_unknown_logic_audit_2026-09-23.md`; `Nitemare3D_12_areas_evidence_audit_2026-09-23.md`; `Nitemare3D_core_function_map_2026-09-23.md`; `Nitemare3D_projectile_pool_deep_map_2026-09-23.md`; `Nitemare3D_DEMO_playback_analysis_2026-09-23.md`; `Nitemare3D_unknowns_audit_2026-09-21.md` v29. Tento dodatok konsoliduje ich výsledky; každý riadok si zachováva platformový rozsah uvedený v zdroji.


---

## Pokračovanie P0: priamy DOS rozbor scheduleru, hodín a RNG brány

### Identita dôkazu

- DOS obraz `N3D-UNFU(1).exe`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Ghidra C export `N3D-DOS-UNFULL-v20.exe.c`, SHA-256 `5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54`.
- Nižšie uvedené adresy sú offsety DOS segmentu `1000`; volanie RTC handlera používa segment `11EE`. Export C má pri veľkých merged blokoch nepresné hranice, preto sú tvrdenia o poradí volaní silnejšie než domnienky o názve každej fázy.

### Priame časovacie fakty

1. `FUN_1000_4760` a `FUN_1000_4778` nastavujú `0x3CC2` na `25`. `FUN_1000_bef4(t)` vypočíta celočíselný bucket `floor(0x3CC2 * t / 1000)`; keď sa bucket zmení, zvýši čítač `0x16FE` a uloží posledný bucket do `0x1702`. Pri predvolenom nastavení to dáva **25 krokov za sekundu**, teda nominálne **40 ms na krok**.
2. `FUN_1000_beb4(t)` počíta odlišný bucket `floor(8 * t / 1000)`. Pri zmene zvýši čítač `0x16F6` a uloží poslednú hodnotu do `0x16FA`. Je to samostatná **8 Hz časová os**; jej presná produktová rola sa neurčuje iba podľa frekvencie.
3. `FUN_1000_bf7a` najprv vykoná desať volaní `FUN_1000_bf36` a spriemeruje nameraný čas. Ak prvý priemer nedosiahne `0x41` ms (65 ms), vykoná ďalších desať meraní s dodatočným volaním `0x19B6`. Potom porovná nameraný čas s `1000 / 0x3CC2` a odvodí parametre `0x4556–0x4560`. Funkcia teda meria DOS update výkon a zohľadňuje minimálny 40 ms interval.
4. `FUN_1000_bd34(0)` číta a upraví RTC register A cez porty `0x70/0x71` (dolný nibble nastaví na `6`), uloží starý vektor `INT 70h`, nainštaluje handler `11EE:0x0BCC`, povolí periodic interrupt bit `0x40` v RTC registri B a odmaskuje IRQ8 cez port `0xA1`. Vetva s parametrom `1` maskuje IRQ8, vypne bit `0x40` v RTC registri B a obnoví pôvodný vektor. `FUN_1000_bde4` volá túto správu podľa flagu `0x3CCF`. Presný časový význam počítadla v samotnom handleri `11EE:0x0BCC` ešte treba získať.
5. `FUN_1000_bdf8` má dve cesty. Pri `0x3CC7 == 0` a `0x3CCF != 0` číta BIOS Data Area na `0x46C/0x46E`, pracuje s bázou na `0x16F2` a používa násobok `0x37` (55 ms na BIOS tick). Inak volá helper `1000:0x49CA` a skladá výsledok ako `local_10[0] * 1000 + local_c`; význam návratových polí helpera zatiaľ nie je pomenovaný.
6. `FUN_1000_be74` pri `0x3CCF == 0` obnoví timestamp cez `bdf8` a uloží ho do `0x81E/0x820`; pri aktívnom flagu vráti už udržiavanú hodnotu. Samotné flagy `0x3CC7/0x3CCF` preto rozlišujú časové režimy, ale ich úplná init/fallback matica zostáva otvorená.

### Poradie scheduleru

`FUN_1000_e964` nastaví stav `0x3CD4=1` a opakuje `FUN_1000_c1a8`, kým stav neprejde na `3` alebo `0`. V `c1a8` sú dve hranice:

- Pri dosiahnutí bucketu z `beb4` sa volá `FUN_1000_c150` podľa režimu `0x3CD6` a posúva sa ďalší deadline `0x1738`.
- Pri dosiahnutí bucketu z `bef4` sa volá postupne `FUN_1000_c0d8`, `FUN_1000_bf36`, `0xA0B8`, `0xA236`, `0x0AEA`, `0x8230`, potom lag vetva `0x1608` alebo `0x15EE` a napokon `0x70D6`. Ďalší deadline sa uloží do `0x173C`, časová báza do `0x1734`.
- Ak rozdiel od `0x1734` prekročí 500 ms, scheduler zavolá `bde4` dvakrát, znovu odčíta `bdf8` a rebazuje časovú bázu.

Z kódu je potvrdený **call order**, nie plná sémantika každého callee. Najväčší ďalší výnos prinesie párovanie `0xA0B8/0xA236/0x0AEA/0x8230/0x70D6` s Win16 update cestou a runtime záznamom 40 ms tickov.

### RNG: nájdená brána, nie algoritmus

DOS volania na `1000:0xFD40` sú päťbajtový far-call stub: `lcall 11EE:0x31F8; retf`. Callery potvrdzujú náhodné použitie: `FUN_1000_5092` testuje návratový bit `&1` pri výbere odrazovej osi a `FUN_1000_8590` použije `FD40() % 0x19`, teda zvyšok 0–24. Ďalšie callery odovzdávajú argumenty helperu.

Zostáva otvorené, čo presne robí kód `11EE:0x31F8`, kde ukladá seed, kedy sa seed resetuje a či DOS a Win16 používajú rovnakú sekvenciu. Kým sa cieľový segment a jeho zápisy stavu neprejdú, helper sa neoznačuje za konkrétny CRT `rand()` algoritmus.

### Ďalší uzatvárací test

1. Rozlúštiť adresnú mapu a overlay/segment pre `11EE:0x0BCC` a `11EE:0x31F8`.
2. Vytvoriť read/write tabuľku pre `0x81E/0x820`, `0x16F2`, `0x16F6/0x16FA`, `0x16FE/0x1702`, `0x1734/0x1738/0x173C` a `0x3CC2/0x3CC7/0x3CCF`.
3. Zmerať DOS tick trace s rovnakým DEMO vstupom pri bežnom behu, pauze a LOAD; osobitne porovnať intervaly okolo 40 ms, 65 ms a 500 ms.
4. Zaznamenať výstupy `FD40` pre opakované seed/time podmienky a porovnať s Win16; až potom uzavrieť generátor, bias a reprodukovateľnosť replaya.
