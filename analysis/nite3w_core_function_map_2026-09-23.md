# Nitemare 3D — hlbšie mapovanie funkcií herného jadra

**Dátum:** 23. 9. 2026  
**Rozsah:** DOS N3D v2.0 a Win16 NITE3W 1.10; doplnkové porovnanie Win16 1.8  
**Stav:** subsystémy sú zmapované; úplný call graph a hranice niektorých veľkých funkcií ešte nie sú uzavreté.

## Hlavný záver

Už máme funkčnú mapu jadra od vstupov a simulácie až po vykresľovanie, dáta a uloženie stavu. Najviac detailu máme pri stenách/dverách/USE, pohybe a kolíziách hráča, vstupoch, guard AI a častiach rendereru. Názvy funkcií uvedené nižšie sú analytické názvy podľa pozorovaného kódu, nie pôvodné symboly vývojárov.

Nie je poctivé tvrdiť, že každá funkcia je sémanticky rozlúštená. Ghidra našla 519 funkčných definícií v DOS exporte a 967 vo Win16 exporte. Všetkých 1 486 definícií je zaradených do auditu, ale za prvými 200 funkciami každej vetvy ide prevažne o klasifikáciu podľa volaní, konštánt, dátových štruktúr a reťazcov. V DOS 2.0 zostáva viacero veľkých zlúčených blokov.

## Verzie a istota

- DOS adresy v tomto dokumente patria k DOS exportu N3D v2.0.
- Win16 adresy patria k NITE3W 1.10, ak nie je výslovne uvedená iná verzia. Win16 1.8 sa používa ako doplnkový dôkaz pri guard AI a boji.
- Čísla segmentov a offsety medzi DOS a Win16 sa nesmú párovať iba podľa rovnakej adresy. Párovanie musí potvrdiť telo funkcie, volajúci, dátové stride hodnoty alebo správanie.
- **Potvrdené** znamená, že operácia je viditeľná priamo v tele alebo v kontrolách EXE.
- **Čiastočne potvrdené** znamená, že účel subsystému je zrejmý, no presná hranica, prototyp alebo niektoré vetvy čakajú na assembler/XREF kontrolu.
- **Kandidát** znamená, že automatická analýza našla pravdepodobný subsystém, ale telo nesmieme považovať za hotový opis funkcie.

Viacverziové párovanie podporuje 429/519 DOS funkcií (82,7 %) a 929/967 Win16 funkcií (96,1 %) presnou alebo silnou fuzzy zhodou. Toto je podpora identity funkcií naprieč verziami, nie percento úplného porozumenia ich správania.

## Funkčný tok jadra

Toto je mapa závislostí, nie definitívny časový sled každého volania:

1. **Štart a zariadenia:** inicializácia runtime, grafiky, časovača a vstupov.
2. **Načítanie levelu:** hlavička/mapa, triedy stien a objektov, grafické záznamy, dvere/panely/push objekty a actor/guard runtime.
3. **Frame update:** vstupy sa prekladajú na akcie; hráč sa pohybuje cez kolízne testy; objekty, steny, stráže, projektily a časovače menia stav.
4. **Zobrazenie:** kamera transformuje viditeľné steny a objekty; renderer zostaví spany/stĺpce; HUD a zbraň sa vykreslia navrch.
5. **Uloženie a prechody:** uloženie/obnovenie runtime tabuliek, level/episode trigger a ukončovacie vetvy.

Presné poradie krokov v hlavnom cykle zatiaľ zakrýva zlúčená rutina DOS 1000:70D6.

## DOS v2.0 — mapa jadrových funkcií

| Oblasť | Funkcie a adresy | Zistená úloha | Istota |
|---|---|---|---|
| Vstupy a časovanie | 1000:430A, 4346, 4484, 453E, 45CE, 466C, 46C4, 471A, 4760, 4778, 47D8, 482E, 48EA, 48F2, 4930 | Vymazanie vstupného stavu; čítanie klávesnice, myši a joysticku; preklad na herné akcie; voľba aktívneho režimu; čakanie na frame a synchronizácia časovačov. | Väčšinou čiastočne potvrdené |
| Wall/object lookup a property tabuľky | 1000:0052, 00A2, 00A4, 0F74, 0FBE, 0FF4, 103E, 1092, 10E6, 1126, 1187, 11C0, 11D2, 1236 | Vyhľadanie runtime objektu/steny, mapovanie tried a zostavenie 256-prvkových príznakových tabuliek. Funkcie 00A2, 1187, 11D2 a 1236 majú podozrivé hranice alebo vyzerajú ako pokračovania. | Vysoká pri lookup/property úlohe; hranice niektorých tiel otvorené |
| Dvere, špeciálne steny a USE | 1000:0212, 03FE, 0598, 0704, 0A40, 0C5F | Zostavenie tabuliek párových stien (limit 64) a triedy špeciálnych stien (limit 32); USE dispatcher; propagácia stavu a zvuku; automatické zatváranie a pohyb stien. Párová stena sa v zistenom pohybovom kroku posúva o 2 jednotky. | Vysoká |
| Objekty a teleport | 1000:0DF8, 0E50, 12C4, 13F4 | Aktivácia objektu na dlaždici, pohyb mapového objektu, hľadanie voľnej susednej dlaždice a výber teleport cieľa/smeru. | Vysoká pri hlavnom správaní |
| Projektily a zásah steny | 1000:57BC, 58DE/58EA, 59B8, 6378, 6488 | Vytvorenie a pohyb projektilu, výpočet kroku, dispatch zásahu steny/objektu a dokončenie dopadu s poškodením alebo animáciou. 58DE/58EA vyzerajú ako alternatívne vstupy alebo poškodené hranice. | Čiastočne potvrdené |
| Guard AI a pohyb | 1000:4AD4, 4BE0, 4C49, 4C76, 4CB4, 4D20, 4D9A, 4DD0, 4DFA, 4E3C, 4E88, 4EC4, 5092, 5342, 5442, 5486, 5510, 55A8, 59F0, 5A8A–5B8E, 5F26 | Stavový automat, výber stratégie, pohybový vektor, kolízie, zápis pozície/stavu, line-of-sight a náhodný cieľ, damage/pain/death a spawn útoku. | Jednotlivé helpery stredná až vysoká; veľké dispatchery nízka pre chybný merge |
| Zbrane a boj hráča | 1000:5F74, 6180, 6258, 62D0, 6302, 88BC | Veľký cluster cadence/munície/hit/damage, update boja, pohyb pri útoku, výber a animácia zbrane a aktualizácia hráčových počítadiel. | Čiastočne potvrdené; 5F74 je pravdepodobne zlúčené telo |
| Kamera a objekty na obrazovke | 1000:6636, 676E, 6824, 688C, 6914, 696C | Príprava view transformu, projekcia a clipping bodu/objektu, vytvorenie zoznamu viditeľných objektov a zoradené kreslenie sprite objektov. | Stredná |
| HUD a foreground | 1000:6A70, 6C8C, 6CD0, 6D04, 6E88, 6EBE, 709A, 70B8 | Kreslenie zbrane/HUD, status textu, načítanie UI assetov, uvoľnenie UI bufferov a zostavenie panelu. | Stredná |
| Renderer a video | 1000:1560, 1590, 1608, 168A, 16B0, 16F5, 176A, 1921, 19B6, 19BA, 19C6, 1A2E, 1AE1, 1B10, 1B71, 1D3E, 1DEC, 1E34, 1EA6, 1EDC, 1F24, 1F9A, 1FC6, 76A4, 7914, 79D0, 7A4E, 7E04–7EC4 | Projekčné tabuľky, VGA DAC/paleta, retrace, planárne blitovanie, masked columns, render buffer a jeho rozmery/stride. | Helpery sú prevažne potvrdené; celá kresliaca slučka nie |
| Načítanie dát, levelu a grafiky | 1000:2772, 27FA, 28F8/28FE, 2A16, 2AA6, 2B3A, 2BA4, 2BCC, 2C16, 2CF4, 7A82, 7B58, 7C00, 7D04 | Kontrolované file I/O, resource directory, dekompresia/bloky, načítanie wall/object/level/UI grafiky. | Stredná; hranice dekodéra 28F8/28FE treba opraviť |
| Save/load a config | 1000:3A00, 3A96, 3ED6, 3F1E, 40DC, 4162, 4206, 4256, 4272/4278 | Čítanie/zápis runtime tabuliek a typovaných blokov, hlavičky a cleanup. 4272/4278 môžu byť prekrývajúce sa vstupy. | Stredná |
| Pohyb hráča a kolízie | 1000:7F96, 8142, 8230 | Test kolízie pre navrhovaný pohyb, osové sklzové riešenie po blokovaní a commit pohybu. | Stredná; presné rozmery/radius a flags treba oddeliť |
| Level init a hlavný update | 1000:70D6, 84FE, 8590, 86DC, 87D8, 89A2 | Zlúčené bloky hlavného cyklu, level init, guard runtime, wall renderer a projectile/damage. Nie sú bezpečné na priamy prepis do zdrojového kódu podľa pseudokódu Ghidry. | Nízka pre hranice; subsystem je zrejmý |

### Dôležité dátové štruktúry v Win16 v1.10

Priame hraničné kontroly a násobky stride hodnôt potvrdzujú tieto runtime kapacity:

| Štruktúra | Kapacita | Veľkosť záznamu |
|---|---:|---:|
| Dvere | 64 | 22 B |
| Panely | 32 | 22 B |
| Push objekty | 12 | 6 B |
| Objekty | 350 | 28 B |
| Guards | 100 | 26 B |
| Renderované segmenty | 50 | 20 B |
| Vektory | 1000 | 28 B |
| Orientačné zoznamy vektorov | 333 na smer, 4 smery | — |

Objektový záznam 28 B a guard záznam 26 B majú čiastočne pomenované polia; blok USER.SAV +0xC403 je vyriešený ako 8 × 42-bajtové projektilové záznamy; podrobnosti sú v nite3w_projectile_pool_2026-09-23.md. Render segment 20 B je samostatný prechodný zoznam, nie object record.

## Win16 v1.10 — samostatná renderer pipeline

Win16 renderer je štrukturálne zrekonštruovaný výrazne hlbšie než jeho finálna pixelová slučka. Funkcie pochádzajú z NITE3W 1.10 exportu:

1. 1018:4046 prechádza 64×64 mapu v štyroch svetových smeroch.
2. 1018:3E82 a 1018:3D54 tvoria stenové vektory po 28 B; 1018:4006 spája kompatibilné susedné hrany.
3. 1018:3430 rozdeľuje vektory podľa orientácie 0–3 a triedi ich; limit je 333 v každej skupine.
4. 1010:E798 transformuje body do kamery, oreže near plane a perspektívne projektuje konce vektora.
5. 1018:3564 zapisuje viditeľného vlastníka do 320-prvkového stĺpcového buffera na 0x53FE a pri prekrytí rozhoduje, ktorá stena je vpredu.
6. 1018:3940 prechádza kandidátov viditeľnosti; 1010:6266 spojí súvislé stĺpce rovnakého vektora do spanov, maximálne 50.
7. 1010:6152 pripraví 16.16 interpoláciu vertikálnej projekcie pre span.

Toto nie je klasický Wolfenstein 3D raycaster, ktorý pre každý pixelový stĺpec nezávisle nájde jednu stenu. Je to vector/span renderer so stĺpcovým testom viditeľnosti. Zostáva presne odhaliť prevod projekčnej hodnoty na horný/dolný okraj steny, výber textúry/V kroku, transparentné prípady a poslednú slučku zapisujúcu texely do framebufferu.

## Win16 — guard AI a boj, dôkaz z verzie 1.8

Tento prehľad je potvrdený v NITE3W 1.8 a treba ho ešte priamo spárovať s telami v 1.10:

- Guard record má krok 26 B. Offset +0x06 je timer, +0x08 index world/object recordu, +0x0A strategy, +0x0B aktuálny state, +0x0C ďalší state, +0x10 health/strength a +0x12 pain cooldown.
- Dispatcher spracúva stavy 0x00–0x15. Potvrdené skupiny zahŕňajú idle/timed animation, wait, chase/move, attack decision/attack, strategy reacquire, transform/spawn, pain/recovery a scripted displacement. Číselné vetvy sú pevnejšie potvrdené než ich slovné názvy.
- Combat routines 1010:9E62, 9EF4 a A13C riešia skóre, damage do guarda/weapon resistance a damage hráča. Difficulty 0/1/2 mení damage oboma smermi: hráč dáva na easy 2×, medium 1×, hard 0,5×; damage od nepriateľov sa škáluje opačne. Presná class × weapon tabuľka ešte potrebuje doplniť názvy zbraní a všetky kombinácie.

## Čo zatiaľ nie je uzavreté

1. **Hlavný cyklus:** 1000:70D6 má približne 3 249 riadkov dekompilátu a pravdepodobne obsahuje viac logických funkcií. Potrebné sú vnútorné CALL ciele, RET/RETF hranice a porovnanie s DOS 1.7/1.8.
2. **Načítanie levelu:** 1000:84FE má približne 3 755 riadkov; treba oddeliť parser/header, stavbu wall/object tabuliek a spawnovanie guardov.
3. **Guard runtime:** 1000:8590 a prekryv 4AD4/4BE0/4C49 treba rozdeliť a zosúladiť s potvrdeným state dispatcherom Win16 1.8.
4. **Wall render:** 1000:86DC má približne 2 605 riadkov; zostáva spojiť vytvorenie vektora, projekciu, occlusion, span a texel write s jedným presným call graphom.
5. **Combat:** 1000:87D8, 5F74, 9CF2 a 9EB4 majú split/merge varovania; treba rekonštruovať weapon cadence → projectile/hit → damage → pain/death → SFX.
6. **Ďalšie DOS bloky:** 2000:9364, 2000:2C16 a 2000:0592 sú tisíce riadkov a pravdepodobne obsahujú viacero rutín alebo omylom zahrnuté dáta.
7. **Win16 XREF:** audit našiel 6 082 NE relokačných miest, z toho 4 904 interných segmentových fixupov. To nie je počet úplných IDA XREF-ov: lokálne near call/jump a niektoré dátové odkazy relokáciu nepotrebujú. Na úplný callsite → caller → callee register treba export z IDA databázy.
8. **Verziové párovanie:** 90 DOS a 38 Windows funkcií nemá presnú alebo silnú staršiu zhodu; nové funkcie, krátke thunky a zmenené hranice vyžadujú ručné potvrdenie.

## Poradie ďalšej analýzy

1. Rozdeliť 1000:70D6 na samostatné fázy a vytvoriť call graph hlavného cyklu.
2. Rozdeliť 1000:84FE a pomenovať každú fázu level-load/spawn.
3. Prejsť 1000:8590 a guard skupiny 4AD4/4BE0/4C49 v assembleri; porovnať s Win16 1.8/1.10.
4. Doplniť wall-render graf od mapového vektora po texel write, vrátane edge cases pre dvere a transparentné steny.
5. Uzavrieť damage/weapons/SFX a zmapovať 2000-segmentové zlúčené oblasti.
6. Vygenerovať IDA xref CSV pre NITE3W a doplniť pri každej rutine callsite, caller, callee a dátové globály.

## Podklady

- Nitemare3D_first_200_unknown_functions_audit.md — ručne posúdené funkcie 1–200 v DOS a Win16.
- Nitemare3D_all_1486_unnamed_functions_audit.md — všetky dostupné funkčné definície a subsystem klasifikácia.
- Nitemare3D_cross_version_function_matching_report.md — párovanie DOS 1.0/1.7/1.8/2.0 a Win16 1.3/1.6/1.8/1.10.
- Nitemare3D_additional_damaged_functions.md — neúspešná dekompilácia a split/merge kandidáti.
- Nitemare3D_vector_span_renderer_reconstruction.md — podrobná Win16 v1.10 renderer pipeline.
- Nitemare3D_nite3w_xref_audit_2026-09-22.zip — NE relocation-site audit NITE3W; nie úplný IDA XREF export.
- Nite3W_Win311_38_weak_functions.md — klasifikácia slabých cross-version zhôd a MFC rutín.

