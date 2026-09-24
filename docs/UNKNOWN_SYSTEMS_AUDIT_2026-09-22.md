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
`FUN_1010_6422`, and animation path `FUN_1010_65A6`. RNG arithmetic, DEMO seed
resets and DOS clock sources are now mapped below. Trace full RNG call order and
cross-platform timing; the two 8 B DEMO layouts differ.

The 2026-09-23 IMG/seqdef pass confirms the two 256-entry image directories and both 90-byte selector-bank formulas across DOS 2.0 and Win16 1.8/1.10. The low bank overlaps the directory region for selectors 0..22 in the supplied IMG sample. Address arithmetic is now modeled; meaning and exact EXE-to-asset pairing remain open. See [the detailed IMG audit](../analysis/nite3w_img_seqdef_2026-09-23.md).

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
| 2 | **DOS scheduler – poradie a DEMO vetvenie potvrdené.** `C1A8` oddeľuje vetvy 8/1000 a 25/1000 jednotiek zdrojového času. V bežnej hre volá `C150` pomalšia vetva; pri `3CD6 != 0` ho hlavná vetva volá pri nepárnom `4540`, pred inkrementom v `BF36`. | Úplná sémantika všetkých callee, zhodnosť Win16 poradia a živý trace. Vynechaný bucket zvyšuje logický čítač iba raz; scheduler spätne nedobieha všetky zmeškané kroky. |
| 3 | **DOS RTC handler a jednotky času potvrdené.** Skutočný vektor je `0BCC:0002`, teda image offset `BCC2`; ISR zvyšuje dword `DS:081E`, číta RTC C a posiela EOI obom PIC. Pri 1024 Hz RTC predstavujú vetvy 25/1000 a 8/1000 nominálne 25,6 a 8,192 Hz. `BDF8` poskytuje samostatný polling čas. | Zmerať skutočný beh, stratené IRQ, pauzu/LOAD a Win16 paritu. Samostatne preveriť wrap a čítanie čítača počas prerušenia. Hodnoty 40 a 65 sú jednotky `BE74`; 500 používa polling čas `BDF8`. |
| 4 | **RNG – algoritmus, násobenie, seed a DEMO reset potvrdené.** LCG `state × 214013 + 2531011 mod 2^32`, návrat `(state >> 16) & 0x7FFF`. DOS a Win16 používajú byte-identický 50 B násobiteľský helper. Obe DEMO štartovacie cesty nastavia seed 1. `3634/3636` sú countdown/fáza paletového záblesku. | Celkové poradie odberov, význam `3630/3632`, prípadné nepriame resety mimo DEMO a úplná save/load kontinuita RNG. Modulo bias je vypočítaný; runtime porovnanie zostáva otvorené. |
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
| 22 | **Level scripts – čiastočne, s konkrétnou mapou XREF.** TRIGGER1/2 (`0x47/0x48`) sú trasované cez epizódu, index levelu a zapisované flagy. Osem bajtov `USER.SAV+0xC553` má samostatný rozpis v `analysis/nite3w_user_sav_story_flags_2026-09-23.md`. | Zostávajú pôvodné texty udalostí, význam niektorých latch-ov, dosah skriptov po LOAD a úplný graf MAP zápisov/SFX pre všetky vetvy. |
| 23 | **Postup/finále/skóre – čiastočné.** Je 31 finálnych máp; class score a hlavné episode/level exit cesty sú čiastočne doložené. | Úplný E3M10 event sled po FLI/menu, restarty a score výnimky; vplyv difficulty na score a všetky koncové príbehové podmienky. Potrebný raw trigger/caller graf a beh. |
| 24 | **VEC/geometria – renderer kostra potvrdená.** 1000×28 B VEC, štyri zoradené skupiny po 333; 64×64 map scan, susedné hrany sa spájajú a vlastník steny sa ukladá do stĺpcového bufferu. | Všetky VEC flags, životnosť a invalidácia zoznamov po wall mutation/load; vysvetliť presný vzťah VEC[1000] ↔ VECLIST[4×333] v oboch buildoch. |
| 25 | **Projekcia/clipping – hlavný tok doložený.** Win16 oreže near-plane okolo `0x4000`, projektuje vektorové konce a rozhoduje viditeľnosť po stĺpcoch. | Všetky orientačné dvojice pri prekrytí, equality/tie prípady, near-plane okraje a fixed-point rounding. Porovnať raw frame capture z pevne zadanej pozície. |
| 26 | **Texture/transparency – otvorená pixelová hranica.** Projekcia/span má zmapovaný 20 B record a 16.16 vertikálnu interpoláciu; shade/remap tabuľka má potvrdenú funkciu. | Finálna texture U/V adresa, texel writer, masked/transparency steny, čiastočne otvorené dvere a tieňové výnimky. Dokončiť od span emittera až po framebuffer zápis. |
| 27 | **Sprites/order – čiastočné.** Je 350×28 B OBJECT pool, projekčný visible-object prechod a wall-owner buffer pre occlusion. | Presné triedenie, rovnaká hĺbka, clipping, wall/sprite order, priority a limit pre preplnený onscreen list. Potrebný call graph sort → span/sprite write. |
| 28 | **Palette/video – remap aj DOS paletový záblesk zmapované.** `A0CC` prepína DAC index 0xEB a index z `D2F7` medzi nulami a 0xFF komponentmi. `3634` je countdown a `3636` fáza; návrat do tmavej fázy volá zvuk 0x42. | Grafické assety používajúce oba indexy, Win16 ekvivalent, všetky ostatné remap/transparent cesty a pixelová parita. |
| 29 | **HUD/automap – dáta čiastočne potvrdené.** Save obsahuje 4096 B automap plochu; existujú HUD a portrait draw routiny. | Význam všetkých raster hodnôt/farieb, dirty flags, portrait HP prahy, značky a spotreba máp metrov. Sledovať každého writeru automap buffera a HUD update. |
| 30 | **Menu/texty/config – čiastočné.** Q/R a Alt+Enter klávesy, difficulty/UI a remote door/cannon menu majú priamo doložené vetvy. | Ukladanie konfigurácie, všetky dialog/message vetvy, command-line parser, MFC/runtime texty a okrajové textové clipping. Nevyvodzovať `-debug` iba z `debug.txt`. |
| 31 | **MAP/IMG/UIF/loadery – jadro MAP potvrdené.** MAP header/cell layout a file I/O/resource loader vetvy sú známe; seqdef loader načíta pevné 90 B bloky. | Runtime mutácie MAP, zvyšné IMG metadata a frame linky, UIF sloty 0–2, prázdne sloty 17–31 a presné asset aliasy. Overiť loader → renderer/dispatcher XREF. |
| 32 | **Zvuk/hudba – kontajner a ďalšia väzba udalosti potvrdené.** SND.DAT má 160 slotov, 88 nenulových položiek. DOS paletový záblesk končí volaním `9270 → C686(0x42,0,2)`: zvukový index 66 a priorita 2. | Kompletná event→slot tabuľka, sample/codec/rate, MIDI slučky, mix/prekrývanie a DOS/Win16 porovnanie. |
| 33 | **ENDING.FLI – otvorené okraje.** Hlavička uvádza 488 frame; fyzická kontrola našla 489 blokov a najmenej šesť prázdnych koncových blokov. | Zistiť, ktoré bloky sú padding/EOF, čo prehrávač považuje za koniec a či všetky 489 záznamy majú valídny frame header. |
| 34 | **Mapy/assety – obsah zmeraný, runtime nie.** 31 finálnych mapových blokov; E1M3 a E1M11 zdieľajú wall plane, no líšia sa v 17 object cells; E2M4 má známu anomáliu. | Všetky class/asset použitia naprieč epizódami a buildmi, nepoužitý content a aktérske hraničné počty; pre DEMO.2/3 preveriť všetkých 31 máp. |
| 35 | **USER.SAV – physical layout confirmed; C553 and D5A3 behavior partly mapped.** C553 event/AI bytes have direct callers; D5A3 is a one-shot guard wake cache keyed by nonzero class-D wall selector. | 94-byte player/global block, timer/pointer rebasing, design reason for DOOR-ID grouping, and selector bounds across all WALLS builds. |
| 36 | 911 alebo 910 | 0–7 |
| 37 | **Debug/CMD/cheats – čiastočné.** `debug.txt` aj `Invalid command line` sú v oboch skúmaných binárkach; Win16 logger a `-r` DEMO recording sú doložené. | Cross-reference fyzických stringov, všetky command-line callers, logger activator, rozdiel od CRT/MFC parsera a dosiahnuteľnosť cheat/debug gate. |
| 38 | **Platformová vrstva – základ identifikovaný.** DOS je MZ; Win16 NITE3W je NE; Win16 používa systémové tick API a WinG/DisplayDIB, DOS BIOS/VGA časovanie a výstup. | Message loop, callbacky, focus/device recovery, cleanup, import API celý a DOS XMS/disk cache. Potrebné sú exact-hash build exports a caller graph. |
| 39 | **Register funkcií – úplnosť inventára nie je sémantická úplnosť.** Známe je 519 DOS + 967 Win16 = 1 486 definícií; všetky sú klasifikované, no starší ručný detail pokrýval 200 z každej vetvy a ďalšie rutiny sa rozoberali cielene. | Uzavrieť skutočné hranice veľkých merged blokov, near/far/nepriame xrefy, callbacky a dead-code kandidátov; aktualizovať každý entry na CONFIRMED/PARTIAL/CANDIDATE pre presný build. |
| 40 | **Verzie/validácia – čiastočné.** Function pairing podporuje 429/519 DOS a 929/967 Win16 matchov; nové audity oddeľujú presne hashované buildy a neprenášajú závery automaticky. | Behaviorálna parita DOS/Win16/shareware/full, rozpory segmentových hraníc, obraz/zvuk/trace a identita buildov. Pre každú mechaniku treba rovnaký vstup, mapu, tick a porovnateľný výsledný stav. |

### Čo sa po zosúladení už nemá opakovať ako úplne neznáme

1. `USER.SAV +0xC403` nie je anonymný 336-bajtový blok: je to osem 42 B projectile záznamov.
2. Fire damage `100/10/2` HP na simulačný update je potvrdený; neznáme ostáva DPS pri konkrétnom kalibrovanom intervale a ostatné hazardy.
3. Win16 explodujúca stena má completion cleanup mapového blokovania; iba DOS call target a presná stopa ostávajú otvorené.
4. DEMO formáty DOS a Win16, ich rozdielne rozloženie event/mask, Win16 hlavičkové pohybové parametre, hlavné input bity a state 1–5 sú rozpoznané; mapovanie levelu DEMO.2/3 a wall-clock dĺžka ešte nie.
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

## Doplnenie P0: inventár volaní DOS RNG

V analyzovanom DOS C exporte som spočítal **26 textových callsite záznamov v 18 caller funkciách**. Ich pozorované konzumné tvary sú:

| Caller funkcia | Pozorované použitie výsledku |
|---|---|
| `241E`, `B22C` | `& 7`, potom výber cez tabuľkový index. |
| `5092`, `9EB4` | `& 1`; vyberie sa znamienko/odrazová os. |
| `5510`, `5516` | `% 8` do poľa `+6`; následne sa nastavuje stav `+0x0B`. |
| `55A8`, `58A0` | Delay/state hodnota `% 8 + 8`, `% 0x50 + 8` a ďalšia maskovaná voľba. |
| `5F74`, `70D6`, `84FE`, `954A`, `980C`, `9CF2` | Dve hodnoty `% 0x3E` a `% 0x24` ukladajú sa do `0x3632/0x3630`; význam týchto globálov ostáva otvorený. |
| `8590` | `% 0x19` sa pripočíta do výrazu `(field_delta * 8) + random`. |
| `9FB4`, `A018` | `% 7` používa výsledok v opakovanej výberovej vetve; presný intended range treba potvrdiť na inštrukciách. |
| `A0CC` | `% 0xF0 + 0xA0` nastaví countdown `0x3634` pri konci svetlej fázy paletového záblesku; fáza je `0x3636`, zvukový slot `0x42`. |

Počet je prevzatý z textového exportu; veľké merged bloky môžu skresliť počet logických callsite a ich hernú rolu. Algoritmus helpera, DEMO reset a význam `0x3634/0x3636` sú teraz potvrdené nižšie. Otvorené zostávajú najmä chronologické poradie odberov, `0x3630/0x3632` a resety mimo DEMO.


---

## 2026-09-23 addendum: USER.SAV event/AI flags

The eight bytes at USER.SAV+0xC553 are now traced individually to their Win16 1.10 readers and writers; the same block and call-site shape appears in Win16 1.8. DAT_1048_51A4 is a selector-keyed door-state bitfield; 51A5 gates GUARD states 0x0E–0x10; 51A6 is a shared 0/1/2 trigger stage and also affects class 0x16 contact damage; 51A7/51A8 latch episode-1 index-9 trigger branches; 51A9 marks the episode-2 index-9 timed collision script; 51AA marks class-0x16 GUARD state-9 handling; 51AB selects shade mode 6 and suppresses normal door updates during a scripted presentation mode. The event matrix and evidence limits are in [analysis/nite3w_user_sav_story_flags_2026-09-23.md](../analysis/nite3w_user_sav_story_flags_2026-09-23.md).

Trigger index values are zero-based. The exact original narrative text and story names remain unresolved; the operational behavior is confirmed from the call sites.

## 2026-09-23 addendum: USER.SAV guard wake cache

The 64-byte block at USER.SAV+0xD5A3 mirrors runtime bytes 0xA65E..0xA69D. The attack path invokes the cache after a successful hitscan or projectile fire. It derives a selector from the player's most recently recorded class-D (DOOR-family) wall tile. The selector is wall ID minus the first class-D ID; in the supplied WALLS data, class D starts at 0x70 and the supported DOOR selectors are sparse values 0..62.

Selector zero is a no-op. For a first nonzero selector, the cache marks that selector before scanning guards. It changes guards with strategy 0, matching guard selector at +0x0E, and state 7 or 8: a 0..7 simulation-step delay is stored at +0x06, then state becomes 1. This handler has no distance or LOS test; the adjacent attack-sound call is a separate operation. Cache writes are saved; level initialization clears them, and the save-load path restores the saved bytes afterward.

The same mechanism appears in Win16 1.8 under FUN_1010_75C0/FUN_1010_8A62 and in Win16 1.10 under FUN_1010_7664/FUN_1010_8B06. Its behavioral purpose and room/door grouping remain partially inferred. See [the detailed cache analysis](../analysis/nite3w_guard_wake_cache_2026-09-23.md).


---

## 2026-09-23: DOS EXEPACK mapping

The DOS MZ is packed with an EXEPACK-style stream. Its EXEPACK header contains signature `RB`, original entry `11EE:0018`, original `SS:SP=3574:0800`, and an expanded length of `0x29D60` bytes. The packed stream uses backward `B0` fill and `B2` literal commands and an internal relocation table with 1,670 entries. Consequently, MZ `e_crlc=0` does not mean the unpacked program has no relocations, and raw file offsets cannot be used as addresses for the expanded code. The header and unpack algorithm are documented by [unEXEPACK](https://github.com/w4kfu/unEXEPACK); a technical overview is available from [Pushbx](https://pushbx.org/ecm/doc/insref.htm#EXEPACK).


## Pokračovanie P0: opravená RTC adresa, časové jednotky a DOS/Win16 DEMO

### Presné vstupy a overenie

| Podklad | SHA-256 |
|---|---|
| DOS `N3D-UNFU(1).exe` | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` |
| Rozbalený DOS image | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |
| Obnovený MZ | `45f0035a4480313856b41befc6e3a8a9a2ecaa109c72400c7de9ba07981b25d8` |
| DOS Ghidra C export | `5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54` |
| Win16 `nite3w(10).exe` | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |

Dôkaz tvorí priama 16-bitová disassembláž a čítanie MZ/NE relocácií. Adresy DOS bez segmentu v tejto sekcii znamenajú offset v rozbalenom image; sú zhodné s offsetovou časťou používaných označení `FUN_1000_...`. DOS segmenty v uložených far pointeroch sú relatívne k load segmentu. Pri Win16 sa používa číslo NE segmentu a offset. Originál hry sa v tomto prechode nespúšťal.

### 1. Oprava adresy RTC handlera a úplné telo ISR

Predchádzajúca verzia omylom interpretovala segment volanej CRT funkcie ako segment handlera. Správna postupnosť na `BD74–BD7C` je:

```asm
push 0x0BCC      ; segment handlera, MZ relocation na BD75
push 0x0002      ; offset handlera
push 0x0070      ; číslo interruptu
call 11EE:39F4   ; set-vector helper, image 158D4
```

Helper `158D4` načíta `DS:DX` cez `LDS DX,[BP+8]` a volá DOS `INT 21h/AH=25h`. Preto je handler **`0BCC:0002` → image `BCC2`**. Hodnota `11EE:0BCC` v staršom audite bola nesprávna.

| ISR offset | Priama operácia |
|---|---|
| `BCC2–BCCE` | uloží 32-bitové všeobecné registre, DS/ES; nastaví DS na relokovaný `2771`; CLD |
| `BCCF` | `INC DWORD PTR DS:[081E]` |
| `BCD4–BCD8` | vyberie RTC register C na porte 70h a prečíta ho z 71h |
| `BCDA–BCDE` | pošle EOI `0x20` na port A0h aj 20h |
| `BCE0–BCE6` | obnoví registre a vykoná IRET |

MZ tabuľka potvrdzuje relocácie segmentu handlera na `BD75`, jeho DS operandu na `BCCA` a segmentu CRT callu na `BD7F`. Funkcia `BD34` pri zapnutí uloží pôvodný vektor, zmení rate-select na 6, povolí periodic bit v RTC B, prečíta RTC C a odmaskuje IRQ8. Pri vypnutí obnoví vektor a maskuje IRQ8; neobnovuje pôvodný rate-select registra A. Zapnutie/vypnutie v tomto tele nenuluje `081E`.

### 2. Dve časové základne a presné vetvenie scheduleru

`BE74` vracia `DS:081E`. Ak `3CCF == 0`, pred návratom ho obnoví z `BDF8`; pri aktívnom RTC vracia ISR čítač. Každý RTC interrupt zvýši hodnotu o 1, bez prepočtu na milisekundy.

`BDF8` má samostatné cesty:

- `3CC7 == 0 && 3CCF != 0`: odčíta BIOS tick `0040:006C`, odpočíta uloženú bázu `16F2` a výsledok násobí 55.
- Inak volá `11EE:2AEA` (image `149CA`). Helper načíta DOS dátum/čas; do `struct+4` uloží **DOS stotiny sekundy × 10**, teda milisekundovú zložku. Caller skladá `32-bitové sekundy × 1000 + word na +4`. Presný názov runtime funkcie je kandidát `ftime`; význam spotrebovaných polí je doložený inštrukciami.

Oprava jednotiek: pri štandardnej 32,768 kHz báze RTC znamená rate-select 6 frekvenciu 1024 Hz; mapovanie uvádza aj [tabuľka registrov MC146818](https://sources.debian.org/src/gxemul/0.7.0%2Bdfsg-1/src/include/thirdparty/mc146818reg.h/#L354). Kód zachováva horný nibble registra A, takže tento záver predpokladá štandardné nastavenie bázy. Časy odvodené z `BE74` sú potom nasledovné:

| Výraz/prah | Jednotky kódu | Ideálny fyzický ekvivalent s RTC |
|---|---:|---:|
| `floor(25*t/1000)` | 40 interruptov medzi bucketmi | 39,0625 ms; 25,6 bucketov/s |
| `floor(8*t/1000)` | 125 interruptov medzi bucketmi | 122,0703125 ms; 8,192 bucketov/s |
| test `< 0x41` | menej ako 65 interruptov | menej ako 63,4765625 ms |
| watchdog `>500` | používa **BDF8**, samostatný polling čas | približne 500 ms podľa vybranej polling cesty |

Hodnoty **25 Hz/40 ms a 8 Hz** platia pri milisekundovom vstupe. Pri RTC sa časová základňa líši o 2,4 %. Uvedené RTC frekvencie sú odvodené limity pri pravidelnom obsluhovaní prerušení a dostatočne častom pollingu, nie namerané FPS.

`BEB4` a `BEF4` pri zmene vypočítaného bucketu zvýšia svoj logický čítač **iba o 1**. Ak medzi dvoma volaniami preskočí viac bucketov, nedobiehajú ich počet. Násobenie v `BEF4` zachováva iba dolných 32 bitov pred delením; wrap správanie preto treba zachovať pri portovaní.

`C1A8` vykonáva:

1. Snímka `BE74` pre logické vetvy a samostatná snímka `BDF8` pre watchdog.
2. Bežná hra (`3CD6 == 0`): pri pomalom termíne zavolá `C150`.
3. DEMO režim (`3CD6 != 0`): v hlavnej vetve zavolá `C150`, iba ak je `4540` nepárny **pred** volaním `BF36`.
4. Hlavná vetva: `C0D8 → BF36 → A0B8 → A236 → 0AEA → 8230 → 1608/15EE podľa 65 jednotiek → 70D6`.
5. `BF36` zvyšuje 32-bitový `4540` o 1. DEMO preto volá `C150` každý druhý hlavný priechod; ideálne pri RTC 12,8-krát/s, kým bežný režim používa pomalú vetvu 8,192-krát/s.
6. Watchdog pri rozdiele >500 zavolá `BDE4(1)`, potom `BDE4(0)`, a aktualizuje bázu `1734`; jeho argumenty sú potvrdené raw kódom.

Zostáva runtime meranie, sémantika všetkých callee, presná matica režimov, pauza/LOAD a porovnanie s Win16. `BE74` číta low/high word osobitne; atomicitu pri príchode IRQ a hraničné pretečenia ešte treba overiť.

### 3. RNG: potvrdené násobenie, opravené Win16 adresy a DEMO reset

```text
state[n+1] = (state[n] * 214013 + 2531011) mod 2^32
result[n]  = (state[n+1] >> 16) & 0x7FFF
```

DOS RNG `FD40 → 11EE:31F8` má telo na `150D8`, stav `DS:24B8/24BA`. Setter `11EE:31E6` je na `150C6`; wrapper `FD46` mu odovzdáva 1. Win16 RNG je `NE seg2:6EC8`, setter `seg2:6EB0`, stav `DS:0A90/0A92`. Obe inicializované hodnoty sú 1.

**Násobenie už je uzavreté:** DOS `11EE:3AD8` mapuje na `159B8`. Jeho 50 bajtov sa presne zhoduje s Win16 `seg2:7118`. Helper počíta dolných 32 bitov súčinu pomocou dolného 16×16 súčinu a dvoch krížových súčinov. Návrat je DX:AX; `RETF 8` odstráni dva 32-bitové argumenty. Nezávislý aritmetický model zodpovedá plnému 32-bitovému násobeniu pri 1 005 hraničných a deterministicky vybraných pároch.

Hodnota **`6DA3` v raw Win16 calle nie je runtime selector**. Je to ďalší článok NE relocation reťazca. Relocation record #3 (index od 0) segmentu 2 je type 2/internal, zdroj `6EE0`, cieľ NE segment 2; tým priamo určuje volanie `seg2:7118`. Rovnaký princíp platí pre ostatné nerealokované Win16 far cally. Formát bol overený proti zdrojovej implementácii [Wine NE loadera](https://github.com/wine-mirror/wine/blob/master/dlls/krnl386.exe16/ne_segment.c).

| Platforma | Potvrdená resetovacia cesta |
|---|---|
| DOS | `F98C` pripraví režim 1 alebo 3, vykoná prípravu a `F972`, na `F9AC` zavolá `FD46`, potom na `F9B1` vynuluje `4540` a vstúpi do `E964`. DEMO štart tak vždy začína RNG seed-om 1 a nulovým counterom. |
| Win16 | `seg3:DAA0` pri DEMO stave 1 alebo 3 vstúpi na `DAB4`; na `DAFC` volá `seg4:32D8 → seg2:6EB0` s argumentom 1; na `DB01` vynuluje `53DC`, potom spustí DEMO dispatcher. Cieľ seg4 je potvrdený relocation recordom #16 segmentu 3. |

Zhoda algoritmu, násobiteľského helpera, počiatočného stavu a resetu pri DEMO štarte je staticky potvrdená. Zhoda hry po jednotlivých udalostiach stále vyžaduje rovnaké poradie odberov, mapu, vstupy a časové vetvy. Resety pri bežnej novej hre, LOAD a prechode levelu ešte nemožno z tejto cesty všeobecne odvodiť.

Inventár C exportu obsahuje 26 textových referencií v 18 caller blokoch; merged bloky môžu obsahovať duplicity. Konzumenti používajú `&1`, `&7`, `%8`, `%80+8`, `%62`, `%36`, `%25`, `%7`, `%240+160`. Modulo bias pri rovnomernom celom 15-bitovom priestore:

| Modul | Počet vstupov na zvyšok | Častejšie zvyšky |
|---:|---|---|
| 2 / 8 | presne 16384 / 4096 | žiadne |
| 80 | 410 alebo 409 | 0–47 |
| 62 | 529 alebo 528 | 0–31 |
| 36 | 911 alebo 910 | 0–7 |
| 25 | 1311 alebo 1310 | 0–17 |
| 7 | 4682 alebo 4681 | 0 |
| 240 | 137 alebo 136 | 0–127 |

Tabuľka platí pre celý priestor 32768 možných návratov, ktoré sú rovnomerne pokryté počas úplného cyklu LCG. Krátka herná stopa má vlastné rozdelenie. Návrat je nezáporný, takže signed/unsigned modulo samotného výsledku RNG vychádza rovnako. Prvý výstup pre seed 1 je 41.

### 4. DEMO: rovnaká veľkosť, rozdielne rozloženie recordu

Oba loadery čítajú tri 16-bitové hlavičkové hodnoty a potom 8-bajtové recordy. Význam prvých štyroch bajtov sa však líši:

| Pole | DOS `6D04–6E87` | Win16 `seg3:90CE–9266` |
|---|---|---|
| Event code | word `+0` → buffer `34BE`; pri zázname SI z BIOS key vetvy | byte `+0` → `375E`, zdroj `0108` |
| Vstupná maska | word `+2` → `34C0`, runtime `3F50` | word `+1` → `375F`, runtime `3756` |
| Byte `+3` | horný bajt DOS masky | táto Win16 vetva ho nezapisuje ani nekonzumuje |
| Timestamp | dword `+4` → `34C2`, zdroj `4540` | dword `+4` → `3762`, zdroj `53DC` |
| Hlavičkové premenné | `455C`, `455E`, `4560` | `53F6`, `53F8`, `53FA` |

Dôkaz DOS writeru: `6E57` zapisuje word SI na `34BE`, `6E5E` masku na `34C0`, `6E65` timestamp na `34C2`. Reader na `6DEF/6DF3` číta tie isté wordy. Win16 writer na `9153–9163` používa byte event a posunutý word masky.

Príklad dodaného posledného recordu DEMO.1: prvé bajty `25 08 00 00`. Win16 z nich číta event `0x25` a masku `0x0008`; DOS by čítal key word `0x0825` a masku `0`. Priamy prenos súboru by zmenil ovládanie. V dodaných troch DEMO súboroch má Win16 interpretácia 140/194/194 nenulových masiek; DOS interpretácia iba 6/5/21. To podporuje ich Win16 rozloženie, ale neurčuje pôvodnú mapu.

DOS timestamp je doložene **počet priechodov BF36**, ktorý priamo inkrementuje `4540`; nejde o RTC counter. Počet sekúnd prehrávania závisí od skutočnej kadencie hlavnej vetvy. Počas prehrávania DOS testuje živú klávesnicu na `6E0A`; ak je kláves dostupný, vracia `0x1B` na ukončovaciu cestu.

### 5. EOF: potvrdená lokálna logika a zostávajúci koniec prehrávania

V DOS sa po načítaní ďalších 8 B na `6E02` návrat AX nekontroluje. Vo Win16 sa rovnako nekontroluje read na `seg3:921A`. Ani jedna z týchto vetiev explicitne neprepína na stop stav podľa počtu načítaných bajtov. DOS read helper `13CF4` používa DOS `INT 21h/AH=3Fh`; vetvy read sú odlíšené od game dispatcheru.

V dodaných súboroch posledný event je `0x25`, `0x26`, resp. `0x00`; žiadny z nich nie je Escape. Potvrdené sú preto ignorovanie read-resultu a absencia explicitného EOF prechodu v týchto dispatcher vetvách. Ak EOF ponechá buffer nezmenený a hra zostane v playback stave, predchádzajúci record je znovu dostupný. Úplný koniec sa musí sledovať cez vonkajší herný stav, udalosti mapy a vstup; samotný posledný timestamp nepreukazuje celkovú dĺžku DEMO.

### 6. Doteraz anonymný RNG konzument: DOS paletový záblesk

`A0CC` používa `3634` ako countdown a `3636` ako fázu. V bežnej hre ho volá `C150`; v DEMO má preto vyššie opísanú odlišnú kadenciu. Kód sa preskočí v epizóde 2 a v epizóde 3, ak `level_index + 1 < 10`.

- Inicializácia s nenulovým argumentom: countdown 80, fáza 0, čierne RGB pre DAC index `0xEB` a index uložený v `D2F7`.
- Update odpočíta 1 a rozhoduje podľa **pôvodnej** hodnoty. Udalosť nastane, keď bola pôvodná hodnota 0; interval preto zodpovedá uloženému countdownu **+1** volaniam.
- Začiatok záblesku: fáza 1, countdown 3, obe paletové položky dostanú komponenty `0xFF`.
- Po ďalších **4 update volaniach**: fáza 0, nové oneskorenie `rand()%240 + 160`, obe položky späť na 0; zavolá sa `9270 → C686(0x42,0,2)`.
- `C686` je SND prehrávacia cesta: index 66, priorita 2. Zvuk je teda volaný pri konci svetlej fázy. Náhodné číslo sa spotrebuje tiež pri tomto prechode.

`16B0` zapisuje priamo VGA DAC porty `3C8/3C9`, čo potvrdzuje paletový charakter efektu. Konkrétne okno/obloha/asset viazaný na tieto indexy a zvukový obsah položky 66 ešte vyžadujú obrazové a zvukové porovnanie. Pracovný názov „blesk/hrom“ je z týchto operácií odôvodnený, ale mapovanie na konkrétny asset zostáva čiastočné.

### Ďalšie najdôležitejšie otvorené dôkazy

1. Zmapovať úplný order RNG odberov vrátane paletového efektu, AI a menu; preveriť `3630/3632`.
2. Zmerať oba clock režimy a hranice 40/65/500; overiť reakciu na pauzu, LOAD, wrap a vynechané IRQ/buckety.
3. Dokončiť externé DEMO exit stavy a mapy DEMO.2/3; pre porovnanie platforiem prevádzať event a masku podľa správneho layoutu.
4. Párovať callee `C150/BF36` s Win16 update cestou a obrazom/zvukom pôvodnej hry.


---

## 2026-09-23 consolidated update from all audits

This update folds the latest DOS v2.0, Win16 1.10/1.8, save-layout, projectile, fire, renderer, and function-inventory findings into the repository register. It keeps behavioral inference and static executable evidence distinct; unresolved timing and full cross-platform runtime equivalence remain open.

### USER.SAV and projectile pool

The 336-byte block at USER.SAV+0xC403 is an eight-slot array of 42-byte player-fired projectile records. Each record has 14 bytes of Bresenham movement state followed by the 28-byte OBJECT at +0x0E. State +0x0C is 0=free, 1=flying, 2=impact. Pool exhaustion skips the shot without consuming ammunition. Weapon selectors 0, 1, and 3 use this pool; selector 2 is hitscan. The ±20 X/Y condition controls projection/culling and is not a lifetime or slot-release test. Guard collision uses an inclusive ±9 test on each axis. Sequence offsets are wand 2/3 and plasma 0/1. Projectile speed in physical time, exact movement interpretation for every byte, and the DOS runtime counterpart remain open.

USER.SAV+0xC3E3 is 32 panel activation bytes copied from panel record +0x14. The following save blocks are now named: push records at C55B–C5A2; automap storage C5A3–D5A2; 64-byte DOOR-family guard wake cache D5A3–D5E2; 256-byte color remap D5E3–D6E2; fill selectors D6E3/E4; and shade level D6E5. Automap byte-level semantics remain partial.

### Story/event flags and wake behavior

The eight bytes saved at C553 correspond to runtime 0x51A4–0x51AB. Evidence distinguishes the selector-keyed SECRET panel bit channel and red-ID-card requirement (mask bit 0; object 0x09), Cannon AI gate at 0x51A5, shared event stage and class-0x16 damage branch at 0x51A6, trigger latches at 0x51A7/8, episode-2 timed collision latch at 0x51A9, class-0x16 state-9 handling at 0x51AA, and shade mode 6 / early return in door-state updates at 0x51AB. Some bytes are written without a direct functional reader in the examined call graph, so they are not assigned narrative names.

After a successful shot, the guard wake handler derives a selector from the most recently recorded class-D wall. Selector 0 is a no-op; supported supplied-map selectors are sparse. It wakes strategy-0 guards with the matching selector in states 7 or 8, assigns rand()%8 delay, then changes state to 1. The handler has no distance or line-of-sight test. This behavior is cross-checked in Win16 1.8 and 1.10; its intended design purpose is still partly inferred.

### Object fields, hazards, and renderer

OBJECT+0x18 is written by FUN_1010_CC7C as a camera-projection/depth-scale cache, not world Y. OBJECT+0x1A is the vertical offset used by the projectile record interpretation. Fire object IDs 0x3B/0x3C/0x3D are large/medium/small and apply 100/10/2 HP per simulation update. Small and medium fire are passable; large fire is impassable and lethal in the audited gameplay evidence. Damage per second is still unknown until the simulation interval is measured.

The 9/23 renderer assembly pass resolves occupied-column wall ownership, texture-U corrections, 16.16 sampling/interpolation, and wall-animation update control flow. Scene-level integration and captured-image comparison remain incomplete.

### Function inventory and evidence boundaries

The paired inventory contains 1,486 function definitions (519 DOS, 967 Win16). Identity support exists for 429 DOS and 929 Win16 entries, or 1,358/1,486 (91.4%); this is function matching support, not percent of the game understood. Manual detailed review currently covers only the first 200 functions per platform. The NE relocation pass classified 6,082 sites: 4,904 internal; 610 assigned (104 described, 462 call-target, 44 data); 20 ambiguous; 5,452 without an owner. The recovered call graph contains 283 partial call edges.

The E3M6 completion save records level 6, 18 enemies remaining, two panels missing, bonus 0, and score 25,675. This confirms the observed fire passability in that tested save. Use the detailed reports [core function map](../analysis/nite3w_core_function_map_2026-09-23.md), [projectile pool map](../analysis/nite3w_projectile_pool_2026-09-23.md), and [story/event flag map](../analysis/nite3w_user_sav_story_flags_2026-09-23.md) for addresses, offsets, and evidence tables.


## 2026-09-25 Win16 MFC / memory synchronization

The current repository now contains the relocation-aware Win16 MFC reconstruction and its modern compatibility layer. Canonical entry point: `docs/WIN16_MFC_RE_SUMMARY.md`. Static artifacts cover `CRuntimeClass16`, 31 runtime classes, CWnd layout/vtable/lifecycle anchors, HWND/HDC/HGDIOBJ/HMENU HandleMaps, evidence levels and explicit coverage states. Runtime validation remains separately tracked and requires the Win3.1 debugger checklist/capture template. The modern C++20 layer now includes `HandleRegistry`, `NativeHandleWrapper`, `WindowWrapper`, `WindowRegistry`, nested/RAII temporary scopes and the recovered z-order mapping. Historical 16:16 pointers, NE fixups and raw MFC object layouts are evidence only and are not reproduced as the x64 ABI.
