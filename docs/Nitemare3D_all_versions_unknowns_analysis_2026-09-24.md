# Nitemare 3D — analýza otvorených oblastí naprieč DOS a Win16

**Dátum:** 24. 9. 2026  
**Rozsah:** dostupné DOS a Win16/Windows 3.x binárky, ich dekompilácie, mapy, assety a aktuálne audity.  
**Záver v jednej vete:** Podklady umožňujú presne určiť, čo je známe a čo ešte chýba pre osem potvrdených herných buildov, ale nepodporujú tvrdenie, že sú analyzované všetky historické vydania alebo celý runtime.

## 1. Ako čítať tento dokument

- **Potvrdené** znamená, že konkrétne bajty, reťazce, dátové záznamy alebo riadený izolovaný test podporujú tvrdenie.
- **Silné statické dôkazy** znamenajú, že kód ukazuje konkrétnu vetvu alebo dátový tok, ale chýba jeden článok reťazca alebo prirodzený beh hry.
- **Odvodené** znamená, že záver vyplýva z adresovej aritmetiky alebo porovnania, nie z pomenovania v pôvodnom zdrojovom kóde.
- **Neznáme** znamená, že dostupné podklady nerozhodujú otázku. Neznáme sa nepovažuje za chybu hry ani sa nedopĺňa odhadnutou hodnotou.

Čísla funkcií, zhodné dekompilované telá, ručný statický audit a runtime potvrdenie sú samostatné metriky.

## 2. Potvrdené verzie a vstupné hranice

### DOS

| Build v binárke | Veľkosť rozbaleného obrazu | SHA-256 obrazu | Stav identifikácie |
|---|---:|---|---|
| V1.0 | 154 448 B | `113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a` | Potvrdený build |
| V1.7 | 170 848 B | `df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff` | Potvrdený build |
| V1.9 | 171 296 B | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` | Potvrdený build |
| V2.0 | 171 360 B | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` | Potvrdený build |
| „V1.8“ | — | — | V dodaných súboroch sa nepotvrdil samostatný V1.8; súbory s označením E18 obsahujú V1.9 alebo sú jeho kópie |

Nadväzujúca surová analýza dokončila rozbalenie `N3D(5).EXE`: celý výsledný obraz sa zhoduje s V1.9. Aj `N3D-E-18.EXE` a `N3D-E-19.EXE` sú hashovo totožné a obsahujú označenie V1.9. V dodaných súboroch teda nie je samostatný DOS V1.8; predchádzajúca výhrada o neúplnom rozbalení už neplatí.

Názov `N3D-E-18.EXE.c` sám osebe nedokazuje, že export pochádza z V1.8. Jeho väzbu treba určiť podľa hashu vstupného EXE a obsahu exportu. V doterajšom materiáli nie je potvrdené samostatné DOS V1.8 EXE.

### Win16 / Windows 3.x

| Build v EXE | Veľkosť EXE | SHA-256 EXE | Počet exportovaných blokov `FUN_*` |
|---|---:|---|---:|
| V1.3 | 229 136 B | `926c0001944b9822cdae10b35c92c2d6cd3772bc774c4c88fb17df7465d1f156` | 959 |
| V1.6 | 230 128 B | `5851849bacd8b03e93444d8a8f34d51c23fecddc73d6b8df7f016885c3b9d418` | 965 |
| V1.8 | 230 224 B | `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22` | 965 |
| V1.10 | 230 400 B | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` | 967 |

Dvanásť ďalších nahratých súborov `nite3w*.exe` sú byte-identické kópie V1.10. Nejde o dvanásť odlišných verzií. V tejto sade nie je binárne potvrdený V1.2 ani úplný register historických/registrovaných Windows vydaní. V1.10 nemá v tomto prechode doložený kompletný zodpovedajúci dátový balík.

### Čo sa z toho dá tvrdiť

**Potvrdené:** štyri odlišné DOS obrazy a štyri odlišné Win16 EXE boli hashovo identifikované.  
**Neznáme:** či existujú ďalšie vydania alebo registrované buildy s odlišným kódom; chýbajú ich overiteľné EXE a párové assety.  
**Dôsledok:** „všetky verzie“ v tomto dokumente znamená všetky overené dostupné buildy, nie každé historické vydanie Nitemare 3D.

Verejný katalóg shareware navyše uvádza DOS V1.0, V1.7, V1.9 a V2.0 a Win16 V1.3, V1.6 a V1.8; pre DOS V1.9 vypisuje aj samostatné balíky Walnut Creek a author-direct. Katalóg je dôkaz distribučných záznamov, nie úplný zoznam registrovaných vydaní ani dôkaz odlišných kódov. Manifest nižšie preto rozlišuje hashovo potvrdené EXE buildy od distribučných archívov; úplné hashe všetkých komerčných a shareware archívov ešte nie sú uzavreté. Zdroje: [prehľad verzií Nitemare-3D](https://www.classicdosgames.com/game/Nitemare-3D.html) a [zoznam súborov](https://www.classicdosgames.com/files.html).

## 3. Pokrytie analýzy — čo znamenajú aktuálne počty

Najnovší zosúladený stav je z priebežnej správy verzie 19, CSV registra verzie 19 a zošita verzie 21. CSV má 1 486 riadkov funkcií: 519 DOS N3D V2.0 a 967 Win16 NITE3W V1.10.

| Metrika | Aktuálny údaj | Výklad |
|---|---:|---|
| Presné alebo silné zhody | 1 358 / 1 486 (91,4%) | 1 039 presných a 319 fuzzy-normalized párov |
| Slabé alebo nevyriešené zhody | 128 | 19 je v ručnom audite; 109 stále čaká |
| Úplné ručné 12-bodové statické audity | 455 / 1 486 (30,62%) | 436 v skupine presných/silných zhôd + 19 slabých/nezavretých párov |
| Úplné audity v skupine presných/silných zhôd | 436 / 1 358 (32,11%) | Zostáva 922 |
| Ručné audity DOS / Win16 | 0 / 455 | DOS: 0/519; Win16: 455/967 |
| Zostáva z celého inventára | 1 031 | 922 presných/silných + 109 slabých/neuzavretých |
| Runtime potvrdenia celého pôvodného programu | 0 | Izolované DOS inštrukčné scenáre sa evidujú osobitne; nejde o celý beh hry |

Staršie reporty uvádzali 277/1 358 a 285/1 486; neskorší snapshot v15/v17 už mal 415 auditov. V aktuálnom CSV v19 sa riadky zosúlaďujú bez zvyšku: 436 hotových v cieľovej skupine + 19 ručne preskúmaných slabých položiek = 455 celkovo; 922 + 109 = 1 031 čakajúcich.

**Rozsah 455 auditov je dôležitý:** všetkých 455 patrí do Win16 NITE3W V1.10; 328 funkcií je v segmente 1000 a 127 v segmente 1008. V registri 12-bodových auditov zostáva bez dokončeného riadku 320 funkcií v segmente 1010 a 98 v segmente 1018. Nový 40-oblastný Win16 audit však cielene preskúmal vybrané funkcie herných segmentov; ide o inú metriku než individuálne 12-bodové riadky. Ani jedna metrika sama osebe neznamená pokrytie všetkých štyroch Win16 buildov.

Všetky číselné stavy v tomto reportovaní sa ďalej viažu na konkrétny register a verziu súboru. Zhodná dekompilácia je kandidát na rovnakú funkciu, nie sama osebe dôkaz rovnakého správania. „Hotový audit“ znamená 12 preskúmaných statických oblastí; runtime/ASM potvrdenie sa počíta osobitne.

## 4. Čo už bolo zistené a čo to znamená pre rozdiely verzií

### DOS

- Rozbalené obrazy V1.0, V1.7, V1.9 a V2.0 boli porovnané s EXEPACK/DIET distribúciami. Štrukturálny prechod evidoval 37 nepriamych miest na build; neskorší audit klasifikoval šesť ako XMS volania, takže 31 zostáva neklasifikovaných. Miesto nie je automaticky samostatná funkcia; môže ísť o callback, IRQ, tabuľkový skok alebo hranicu.
- Hráčsky save blok má 92 bajtov vo V1.0/V1.7/V1.9 a 94 bajtov vo V2.0. Vo V2.0 sa posúvajú HP a obtiažnosť a pribúda signed-word časovač na offsete +0x26. Parser nesmie používať jednu pevnú štruktúru pre všetky štyri buildy.
- Selektor GUARD animácie sa líši: pri state 6 / strategy 2 V1.0 volí banku +0x24, kým V1.7/V1.9/V2.0 volia +0x04. Ostatné skúmané kombinácie majú ďalšie pravidlá; tento rozdiel sa nesmie zovšeobecniť na všetky stavy.
- Výpočty prichádzajúceho poškodenia a odmocniny boli skúšané na pôvodných izolovaných rutinách. Tieto testy podporujú presnú aritmetiku, nie prirodzený priebeh súboja, úplnú tabuľku enemy HP ani všetky hranice zásahu.
- V1.9 → V2.0 mení uložený hráčsky blok a časovanie indikátora zásahu. Vplyv na celý sled damage, RNG, ochrany a kreslenia ešte vyžaduje kontrolovaný beh.
- Neskorší raw audit potvrdil 23 strojových intervalov (3 858 bajtov) a opravil štyri hranice v starom Ghidra registri: `00A2`, `020C`, `04BE` a `0C5F` nie sú samostatné funkcie v predtým uvedenom význame. Potvrdil tiež 64×64 sken párových a špeciálnych stien, 28-bajtové object záznamy a pohybové rutiny; 31 z pôvodných 37 nepriamych miest na build zostáva neklasifikovaných.
- Ďalší DOS rozbor izolovane vykonal 501 scenárov nad pôvodnými inštrukčnými úsekmi s nahradeným file I/O, XMS/INT 2Fh alebo debug službami. Uzavrel načítanie GAME.PAL a farebné tabuľky, šesť XMS wrapperov a signed hranicu 32 768–65 535 KiB, 16-bajtový CONFIG.SAV blok a ďalšie CLI polia. Nejde o spustenie celého DOS programu.

### Win16

- V1.3/V1.6/V1.8/V1.10 majú dva oddelené časové rytmy. Nominálny pomalý update je 8 Hz; kalibrácia vychádza z merania kreslenia a nevytvára päť AI krokov za jeden render frame. Časovače GUARD, hazardov a kadencie sa preto nesmú odvodzovať z FPS.
- V1.6 → V1.8 pridáva cestu na obnovenie úspešne načítaných hlasitostí pri cleanup. V1.8 → V1.10 mení inicializáciu a zápis palety; helper V1.10 odovzdáva do WinG upravený `RGBQUAD[index]` a mení podmienku `RC_PALETTE`.
- Shareware assety `IMG.1`, `DEMO.1`, `SND.DAT`, `UIF.DAT` a `GAME.PAL` sú v dodaných balíkoch 1.3/1.6/1.8 bajtovo totožné. `MAP.1` V1.3 = V1.6; V1.8 mení dve bunky v E1M5. Objekt `0xD8` sa presúva medzi súradnicami (26,34) a (26,35), od nuly. `NITE3D.BSF` sa medzi týmito balíkmi líši a jeho sémantické rozdiely sú otvorené.
- V1.6 má voliteľnú úvodnú obrazovú cestu. V1.10 data pack nie je v tomto audite úplne spárovaný, takže rovnakosť jeho máp a assetov sa nesmie predpokladať.
- Zistenie „rovnaká funkcia“ medzi verziami nepokrýva automaticky inú inicializáciu, resource pack, callback cieľ, MFC tabuľku alebo runtime zariadenie.
- Nadväzujúci 40-oblastný audit raw Win16 potvrdil timestamp DEMO ako render-generation index, opravil score tabuľku, kontaktný damage multiplier, F2/F3/F4 mapovanie, viacero GUARD/dvere a save/load detailov a presné joystick dead-zone pravidlá. Otvorené zostávajú plná AI/state mapa, prirodzený runtime, koniec DEMO a framebuffer/audio zhoda.

## 5. Mapa otvorených oblastí

### P0 — potrebné pre správnu rekonštrukciu jadra

| Oblasť | DOS V1.0 / V1.7 / V1.9 / V2.0 | Win16 V1.3 / V1.6 / V1.8 / V1.10 | Rozlišujúci dôkaz |
|---|---|---|---|
| Skutočné funkčné hranice a dispatch | Raw audit opravil štyri zlé DOS hranice a klasifikoval 6/37 miest ako XMS; 31 zostáva neklasifikovaných na build. | Kandidáti bez priamych XREFov môžu byť far-pointer/vtable/message-map ciele alebo nesprávne hranice. | Pre DOS: raw bytes/relokácie všetkých zvyšných cieľov; pre Win16: tabuľka, caller ABI a návratový tok každého callbacku. |
| GUARD AI | Win16 dispatchery majú vo všetkých štyroch dostupných buildoch rovnakých 20 explicitných vetiev v rozsahu 0x00–0x15; vynechané sú iba 0x0A a 0x0B. Stav 0x0A zapisuje dokončenie smrti, 0x0B smrteľný kontakt guardu s hráčom. Stav 0x13 má staticky potvrdených osem pohybových pokusov a odpočítavanie aj pri blokovaní. Úplná matica stav × stratégia × trieda × timer × animácia × zvuk, LOS/sluch, alarm a bossovia zostávajú otvorené. | Zhodná množina `case` vo všetkých štyroch C exportoch; raw V1.10 potvrdzuje čítanie stavu a skokovú tabuľku. Runtime snímka/zvuk, prirodzená dosiahnuteľnosť a význam ostatných handlerov chýbajú. | V runtime overiť posledný frame/zvuk pri stavoch 0x0A/0x0B/0x13; potom doplniť writer→handler prechody a podmienky ostatných stavov. |
| Kolízie a damage | Polomer/rohy hráča, wall sliding, dvere obsadené aktérom, simultánne damage a úplné HP writery. | Chýbajú rohy/diagonály, zmena pohybu v jednom frame, projektilové okraje a všetky damage zdroje. | Identický stav a build; sledovať X/Y, collision result, HP pred/po a event order. |
| Zbrane a projektily | Rýchlosť, kadencia, zásahové hranice a úplné triedové škálovanie. | Neuzavreté `OBJECT/projectile +0x0D`, DDA jednotky, ukončenia poolu, prvý výstrel a ammo/pool súbeh. | Sledovať spawn → update → collision → wall hit → damage → free; opakovať pre každú zbraň. |
| USER.SAV / LOAD | Význam každého poľa 92/94 B bloku, ďalšie bloky, rebasing a LOAD počas letu/animácie. | Všetky polia a nepriame/raw prístupy; runtime diff a LOAD počas aktívnych eventov. | Uložiť pred a po jednej zmene stavu; porovnať bajty, obnoviť hru a sledovať prvé čítania polí. |
| Čas, RNG a DEMO | Sled odberov, seed resetov, IRQ/polling, DEMO record packing a deterministický replay. | Timer API latencie/wrap/focus/pause, seed a poradie RNG, DEMO štart/EOF/reálna rýchlosť. | Pevný vstupný záznam a log ticku, RNG, vstupov, stavu a času pre každý presný hash. |
| Renderer | VGA geometria/pixel path nie je preukázaná ako ekvivalentná Win16. | Near-plane, fixed-point zaokrúhlenie, clipping/tie, wall/sprite shade a bitovo presné pixely. | Originálny framebuffer + paleta pri zhodnej mape, pozícii, uhle, dverách a render generácii. |

### P1 — potrebné pre hernú úplnosť a verziovú kompatibilitu

| Oblasť | Čo zostáva neznáme naprieč buildmi | Ďalší test alebo statická kontrola |
|---|---|---|
| USE, dvere a tajné panely | DOS v2.0 pairing/state/USE a vybrané Win16 writery sú známe; všetky class podmienky, zamietnutie, blokovanie, cleanup a LOAD v animácii ostávajú otvorené. | Pre každý handler zostaviť tabuľku vstupných flags → zmena stavu/mapy → zvuk → koniec animácie. |
| SAFE, TRUNK, rádio a pickupy | Win16 frame 0/1/obsah, rádio E1M9 guard a odmietnutý pickup, ktorý zostáva na mape, sú doložené; cancel, limity a prenos levelmi nie. | Prepojiť mapovú triedu s handlerom, stringom, inventory writerom a uloženým fieldom. |
| WARP, výťahy a triggery | Poradie susedov N/E/S/W a cardinal uhol sú známe; obsadený cieľ, spätné prechody, one-shot, zrušenie a save/load eventu ostávajú otvorené. | Porovnať mapy a všetkých writerov event flagov; v behu zaznamenať pozíciu cieľa a event flagy. |
| Push objekty a špeciálne steny | Win16 blokovaný push zachová counter; DOS builders/pohyb sú raw preskúmané. Class-specific pohyb, `ONE_SHOT`, `SPECIAL1` a completion callbacks naprieč buildmi ostávajú otvorené. | Writer → controller → map cell/occupancy → completion callback → collision, zvlášť pre každý build. |
| IMG/SEQDEF a facing | Vybraný Win16 animátor posúva jednu snímku a RNG retry závisí od packed alternatív; úplný bank/facing/loop map a väzba na všetky epizódy/buildy chýba. | Sledovať sequence selector, frame pointer, interval a caller pre každú triedu. |
| Audio/MIDI a multimédiá | Win16 rovnaká SFX priorita môže prebiť aktívny zvuk a niektoré cleanup cesty obnovujú hlasitosť; celý DOS/Win driver a error/failure graf zostáva otvorený. | Callsite → resource ID → driver path; log úspech/chyba a cleanup. |
| Paleta, HUD a automapa | DOS GAME.PAL loader a odlišné nearest-color metriky sú izolovane overené; Win16 blackout/shade/HUD writery sú čiastočne doložené. Fade, všetci writery, farby a framebuffer output čakajú. | Zaznamenať paletu a framebuffer pred/po; nájsť každého writer-a príslušných polí. |
| Vstupné zariadenia | Win16 VK F2/F3/F4, joystick dead-zone ±5 v hre a ±8 v menu sú známe. Edge/repeat, súbehy, focus/pauza, myš a DOS device fallback ostávajú otvorené. | Rovnaký vstup v každom builde; log surový vstup aj akciu po spracovaní. |
| CLI, konfigurácia a BSF | DOS prepínače `-a/-w/-d/-f/-c/-e/-l`, CONFIG 16 B a Win16 CONFIG 20 B/tri BSF bloky sú čiastočne dekódované. DOS `-b`, CONFIG `+02`, zvyšné bity, invalid input a párovanie všetkých balíkov ostávajú otvorené. | Overiť každý prepínač na raw caller/write; porovnať BSF dekódované záznamy s vykonaným handlerom. |
| Epizódy a kompletnosť assetov | Dodané MAP.1–3 obsahujú 31 blokov a MAP.2 má jednu chýbajúcu definíciu wall 0x37; E2/E3 párovanie, nepoužité triedy a registered vydania nie sú uzavreté. | Hash manifest EXE + MAP/IMG/UIF/SND/DEMO/BSF; bez páru sa správanie neprenáša. |

### P2 — dokončenie dôkazovej a kompatibilitnej vrstvy

1. Roztriediť všetkých 128 weak/unresolved cross-version párov a oddeliť skutočné zmeny od chybných hraníc či exportov.
2. Prejsť každý class overlay a každý bajt GUARD/OBJECT: čitateľ → zapisovateľ → writer trigger → následný consumer.
3. Uzavrieť vtable, callback a message-map graf Win16; priamy počet XREFov nie je úplný graf.
4. Zostaviť build/hash manifest pre každý dostupný EXE aj dátový archív, s výslovným označením chýbajúcich párov.
5. Uchovávať rozdielne správanie pod profilom konkrétneho buildu, nie v jednej spoločnej „priemernej“ logike.

Položky v tejto mape sú **zostávajúce otázky**, nie tvrdenie, že sa k nim od pôvodného snapshotu neurobila žiadna práca. Cielené raw a 40-oblastné audity nižšie už uzavreli niektoré lokálne otázky, ale neuzatvárajú celé subsystémy.

## 6. Rozlišujúce testy pre chýbajúce runtime dôkazy

Tieto testy sa týkajú prirodzeného behu hry; **nie sú vykonané ako celý DOS/Win16 runtime**. DOS má navyše 501 vykonaných izolovaných scenárov nad pôvodnými inštrukciami s nahradenými systémovými službami; tie nenahrádzajú nižšie uvedené end-to-end testy.

1. **DOS V2.0 indikátor zásahu:** watchpoint na `DGROUP:417A`, breakpointy na úplnom obraze `6A93h` a `A236h`; uložiť HP a nasledujúce aktualizácie. Adresy sa pred použitím musia prepočítať podľa reálneho load segmentu.
2. **DOS GUARD banky:** dosiahnuť rovnaký state 6 / strategy 2 vo V1.0 a V1.7/V1.9/V2.0; zaznamenať vybraný bank offset a reálne zobrazené snímky.
3. **Win16 projekčná cache:** pri V1.10 sledovať writer `3:CC7C` k `OBJECT+0x18` a projectile/damage cestu `3:9B64 / 3:80F8 / 3:9FA2`; porovnať viditeľný objekt, objekt za okrajom a otočenie tesne pred zásahom.
4. **Save/load v aktívnom stave:** uložiť a obnoviť projektil, pohybujúce sa dvere, GUARD animáciu a trigger zvlášť. Zaznamenať rozdiel bajtov aj prvé čítanie po LOAD.
5. **Renderer:** pri identickom stave zachytiť surový framebuffer, 256-farebnú paletu, polohu, smer, stav dverí, render generation a relevantné VEC/span tabuľky.
6. **Časovanie Win16:** sledovať slow/frame čítače a ms clock počas bežného behu, preťaženia, focus loss, pauzy a DEMO. Skontrolovať, či po oneskorení vzniká catch-up séria.
7. **Input a zvuk:** rovnaké kombinácie kláves, myši, joysticku a súbežných SFX; zachytiť surový vstup, výslednú akciu a driver volanie.
8. **Win16 GUARD stav 0x0B:** V1.10 pri smrteľnom kontakte guardu s hráčom zachytiť `GUARD+0x0B`, HP, globálny herný stav, ďalšie volania `3:7B56` a poslednú vykreslenú snímku; test rieši už iba prirodzený výsledok.
9. **Win16 stav 0x13:** vyvolať stratégiu 3 proti obsadenej bunke; zaznamenávať timer, X/Y, obsadenosť bunky, stav a zvuk pri hodnotách timeru 8…0, aby sa statická vetva spojila s prirodzenou mapovou situáciou.
10. **Win16 GUARD stav 0x0A:** nechať guarda dokončiť smrť; zaznamenať prechod 9→0x0A, triedu guardu, časovač, flag animácie, následné volania `3:7B56`, bajt mapovej bunky, posledný frame a zvuk. Opakovať pre triedy 0x11 a 0x16, ktoré majú samostatné dokončovacie vetvy.

Gameplay video môže potvrdiť viditeľnú udalosť a jej poradie, ale samo nepreukáže interný field, adresu, RNG odber ani dôvod konkrétneho výsledku.

## 7. Stav pôvodného pracovného poradia

| Krok | Stav | Čo je dokončené a čo zostáva |
|---|---|---|
| Zamknúť identitu vstupov | Dokončené pre dostupné EXE; čiastočné pre archívy | Hashovo je potvrdených osem odlišných EXE buildov. Úplne rozbalený kandidát označený „V1.8“ sa zhoduje s V1.9; dodaný samostatný DOS V1.8 chýba. Všetky historické shareware/retail archívy a párové assety nie sú hashovo spárované. |
| Opraviť register auditov | Dokončené podľa najnovšieho stavu | CSV v19 a priebežná správa v19 uvádzajú 455 úplných auditov; zošit v21. Rozpad 436 presných/silných + 19 slabých = 455; čaká 922 + 109 = 1 031. |
| Doplniť statický DOS deficit | Čiastočne dokončené | DOS stále má 0/519 individuálnych 12-bodových auditov, no raw batch teraz overuje 23 intervalov, opravuje 4 hranice, porovnáva dostupné buildy a pridáva 501 izolovaných inštrukčných scenárov. Zostáva väčšina funkcií, 31 neklasifikovaných nepriamych miest na build a chýbajúci samostatný V1.8. |
| Dokončiť Win16 statické chvosty | Čiastočne dokončené | Individuálny register má 455/967 auditov. Samostatný 40-oblastný audit pokrýva vybrané funkcie herných segmentov, no 922 presných/silných a 109 slabých riadkov čaká; zostáva plný callback/vtable graf aj ostatné historické buildy. |
| Vykonať rozlišujúce runtime testy | Čiastočne pripravené, celý beh nevykonaný | V tomto prostredí nie sú DOSBox-X, DOSBox, Wine, QEMU ani Bochs. Všetkých desať end-to-end testov zo sekcie 6 čaká. DOS má 501 izolovaných testov pôvodných inštrukcií s náhradou systémových služieb; nebol spustený celý DOS ani Win16 EXE. |

## 8. Čo vyžaduje ďalší podklad

### Staticky možno pokračovať z dostupných exportov

- K dispozícii sú DOS EXE obrazy a raw disassembly batch, C export V2.0, izolované testovacie skripty a mapy/asset dôkazy; Win16 sú k dispozícii štyri C exporty, štyri EXE identity a 40-oblastný raw/C audit s dôkazovým balíkom.
- Najnovší Win16 priechod priniesol statické závery o DEMO, score, kontakte/damage, inpute, GUARD/dverách, save/load, projekcii a animáciách. DOS priechod doplnil GAME.PAL, farby, XMS, CONFIG.SAV a CLI.
- Zostáva 1 031 individuálnych 12-bodových riadkov a viaceré celé subsystémy. Cielené tematické audity nedopĺňajú automaticky všetkých 12 polí každého riadku.

### Dynamické testy v tomto prostredí zablokované

Príkazové vyhľadanie nástrojov nenašlo DOSBox-X, DOSBox, Wine, QEMU ani Bochs. Nebol preto spustený celý pôvodný EXE a nevznikol prirodzený gameplay/watchpoint/framebuffer trace; počet end-to-end potvrdení je nula. DOS izolované testy vykonali vybrané pôvodné inštrukcie v Unicorn, pričom sa nahradili file I/O, XMS/INT 2Fh alebo debug volania. Tieto testy sa nesčítavajú ako plný runtime a nenahrádzajú testy sekcie 6.

### Historické alebo úplné distribučné súbory

Na uzavretie tvrdenia „všetky historické vydania“ treba binárne overiť aj úplné komerčné/registrované balíky a distribučné varianty uvedené externými katalógmi. Názov, dátum ani obal nedokazujú odlišný EXE; samostatný DOS V1.8 sa v dodaných súboroch nepotvrdil. Win16 V1.10 dátový balík a plné E2/E3 sady nie sú spárované pre všetky buildy.

## 9. Nové statické zistenia z tohto pokračovania

Táto verzia zlučuje podklady, ktoré vznikli po predchádzajúcom snapshot-e: DOS deep audit a balík 501 izolovaných scenárov, Win16 40-oblastný audit a MAP.EXE audit. Opravy nižšie nahrádzajú staršie vety, ak sú s nimi v rozpore. Izolované inštrukcie ani cielené tematické audity sa nepočítajú ako kompletný beh hry alebo ako plné pokrytie všetkých funkcií.

### DOS N3D V2.0 — párové steny, USE a pohyb

Preverený export N3D-DOS-UNFULL-v20.exe.c má SHA-256 5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54, zhodný s hashom v najnovšom auditnom tracker-i. Nasledujúce body kombinujú dekompiláciu s novým raw disassembly batchom; samostatne sú označené izolované testy a tie nie sú celým runtime:

- FUN_1000_0052 prechádza záznamy so stride 0x0E, porovnáva dve WORD hodnoty na offsetoch +8 a +0x0A a pri zhode vracia pointer na záznam; pri nenájdení ide do chybovej cesty. To podporuje identitu lookupu špeciálnej steny, nie kompletný formát všetkých jeho polí.
- FUN_1000_0212 prechádza 64×64 mapovú mriežku od adresy 0x373E v krokoch po 2 bajtoch, vyhľadáva párové wall objekty označené bitom 0x08 a vytvára najviac 0x40 záznamov po 0x12 bajtov. Susedné objekty páru dostávajú uložený smer/typ páru a bit 0x20 v object flags. Presný význam všetkých polí záznamu ostáva otvorený.
- FUN_1000_0598 prepína stav páru v poli index +4. Pri stavoch 0 alebo 2 nastaví 3; pri 1 alebo 3 môže podľa orientácie vstupu nastaviť 2; stav 4 odmietne. Potom hľadá zodpovedajúce susedné dvere a propaguje stav. Pri prechode na 3 nastaví bit 0 v flags oboch wall objektov; volá tiež audio/event helpery.
- FUN_1000_0A40 odpočítava timer párových záznamov so stavom 0. Keď dôjde na nulu, kontroluje occupancy bunky a polohu hráča; pri voľnej bunke nastaví stav 3 a aktualizuje flags oboch objektov, inak nastaví krátky retry timer 4.
- FUN_1000_0704 je USE dispatcher: vyberie bunku pred hráčom podľa smeru a map pointera, potom vetví podľa wall/object flagov, triedy a inventory bitmasks. Z exportu možno potvrdiť dispatcher a gating, nie ešte úplnú tabuľku každého handlera a jeho vstupných/koncových stavov.
- FUN_1000_4D20 mapuje znamienka pohybových delta X/Y na osem smerových indexov 0–7; nulový vektor smer nemení. FUN_1000_5092 testuje obe strany každého pohybového vektora cez FUN_1000_4EC4, v prípade blokovania nulí príslušnú os a potom zapisuje novú pozíciu a occupancy mriežky. Pri stave 6 a blokovaní na oboch osiach používa RNG na výber jednej osi, ktorú obráti.
- FUN_1000_58DE znižuje timer na +6; pri jeho vypršaní zapíše 0 na +0x0A a stav 2 na +0x0B. Pri zostatku 8 vyšle audio/event volanie; pri hodnote pod 8 skúša posun o signed delty +0x13/+0x14 a aktualizuje occupancy bunky, ak je cieľ voľný alebo ide o tú istú bunku. Táto rutina sama v zobrazenom tele nerobí damage.

**Opravená hranica z raw bajtov:** starý C export označil `FUN_1000_00A2` ako trojbajtové prázdne telo, `FUN_1000_04BE` ako samostatnú funkciu a podobne posunul ďalšie vstupy. Raw disassembly teraz ukazuje, že `0x0052–0x00A4` je lookup špeciálnej steny; `0x00A4–0x00FE` vyhľadáva index objektu v záznamoch stride `0x06` a porovnáva objektové súradnice `+0x12/+0x14`. Štyri staré štítky `00A2`, `020C`, `04BE` a `0C5F` sú hranicové artefakty/epilógy/vnútorné ciele, nie samostatné rutiny v uvedenom starom význame. Tým sa uzatvára otázka raw hranice pre tieto miesta; všetky nepriame call/jump ciele a DOS funkcie tým uzavreté nie sú. Overený v2.0 batch pokrýva 23 intervalov/3 858 bajtov a porovnáva vybrané vzory naprieč dodanými DOS obrazmi.

### DOS V1.0/V1.7/V1.9/V2.0 — paleta, XMS, CONFIG a CLI

Neskorší DOS report vykonal 501 izolovaných scenárov na pôvodných inštrukčných úsekoch. File open/seek/read/close, INT 2Fh/XMS ovládač a debug výpis boli podľa testu nahradené; zachované boli pôvodné jadrové inštrukcie. Závermi sú:

- Všetky štyri dodané GAME.PAL sú 1 924 B a hashovo totožné. Hra číta posledných 768 B od offsetu 1 156, každú zložku posunie `>>2` a vykoná 769 zápisov do VGA DAC. Nepoužitý prefix 1 156 B tým nie je vysvetlený.
- Logické UI farby sa mapujú na paletu podľa štvorcovej euklidovskej vzdialenosti; shade tabuľka používa súčet absolútnych rozdielov. To sú dve odlišné metriky. Logická farba 12 z indikátora zásahu mapuje v dodanej základnej palete na index 161, RGB `(63,21,15)` v 6-bitových zložkách.
- Šesť nepriamych call sites je XMS ABI (query, allocate, free, move, lock, unlock); z 37 pôvodných nepriamych miest na build zostáva 31 neklasifikovaných. Pri XMS bloku od 32 768 do 65 535 KiB sa hodnota AX vyhodnotí ako záporná v signed vetve a táto inicializačná cesta XMS vypne; to nie je dôkaz pádu celého programu.
- XMS cache presúva celé KiB, zaokrúhľuje dĺžku nahor; helpery a záznam move sú popísané v sprievodnom DOS reporte. Vlastníctvo každého bufferu, eviction a disk fallback zostávajú otvorené.
- CONFIG.SAV je oddelený 16-bajtový blok. Je známych viacero vstupných polí a ich defaultov; význam `+02`, úplné účinky cheat polí a všetky hraničné vstupy zostávajú otvorené. Ďalšie CLI polia zahŕňajú doslovný path prefix `-a`, viewport `-w`, shade `-d`, floor/ceiling `-f/-c`, episode `-e` a level `-l`; účel `-b` ostáva nepotvrdený.

Z týchto 501 scenárov 52 sa týka palety, 96 XMS wrapperov, 192 prenosov, 53 config/path/viewport prípadov a 108 koncov inicializácie XMS. Žiadny test nespustil celý originálny DOS proces.

### Win16 — nové zistenia zo 40 oblastí

Win16 audit pokryl 40 tematických oblastí a vytiahol 424 verzionovaných funkčných okien; jeho verifikačný skript potvrdil okrem iného 100 raw score hodnôt, 12 raw kontrol damage/DEMO/CONFIG a tri DEMO súbory. Toto je cielený audit, nie potvrdenie všetkých funkcií alebo celých runtime subsystémov. Najdôležitejšie doplnenia:

- DEMO timestamp je 32-bitový render-generation index vo všetkých štyroch EXE. Dodaný DEMO.1 má 203 udalostí; posledný timestamp 1 157 sám neurčuje koniec prehrávania ani dĺžku v milisekundách.
- Raw score jump tables boli opravené pre 25 tried vo všetkých štyroch EXE: triedy 12/29/30 dávajú 250 bodov, penalizácia −1 000 patrí triede 21. Score a damage vetvy zostávajú odlišné.
- Guard→hráč kontaktné poškodenie sa pri difficulty 2 násobí dvoma a pri 0 delí dvoma. Toto sa týka kontaktnej cesty; oheň má inú vetvu bez rovnakého difficulty scaling.
- Vstupné bajty 0x71/0x72/0x73 sú F2/F3/F4; Alt+F4 posiela WM_CLOSE. Gameplay joystick má dead-zone −5…+5, menu používa ±8.
- Cielený audit doplnil zapisovače dverí, GUARD+0x0D ako podkladový bajt objektu mapovej bunky, AI stav 9 → stav dverí 4, opakovanie pohybu po blokovaní, podmienky safe/trunk/radio a smer výstupov teleportu/výťahu. Nadväzujúci cross-version priechod uzavrel množinu stavových vetiev dispatchera vo všetkých štyroch Win16 exportoch, smrteľnú vetvu stavu 0x0B a stav 0x13 s ôsmimi pokusmi a pokračujúcim odpočítavaním pri blokovaní.
- Save/load v1.10 rebazuje VEC/world OBJECT deadline, obnovuje aktuálne door pointers a prepočítava map pointers; projectile deadline ostáva špecifická otvorená otázka.
- Hitscan vetva v kontrolovanom tele nemá break po prvom úspešnom damage; cooldown môže byť spotrebovaný aj pri neúspešnom výstrele. Projectile impact slot zostáva obsadený do konca impact animácie.
- Render audit opravil predchádzajúci opis projekčnej cache: `OBJECT+0x18` dostáva projektovanú hodnotu po `>>4` v podmienenej projekčnej ceste ešte pred sprite-row/slot clampom. GUARD aim stamp má užšiu podmienku (flag 8 a prekrytie stredového X do 4 px). Ani to nepreukazuje refresh cache každého aktéra v každom frame.

### MAP.EXE — samostatný DOS map editor

Audit konkrétneho dodaného `MAP.EXE` a dát pokryl 40 oblastí, 62 aplikačných kandidátov, 136 názvov tried, 1 116 definícií a všetkých 31 fyzických blokov dodaných `MAP.1–3`. Všetky tri preskúmané cesty „uložiť“ volajú prázdnu funkciu `RET/NOP`; obsluha editácie myšou je prakticky prázdna. Príkaz C môže zmeniť mapu v pamäti a potvrdenie S zruší dirty flag bez zápisu. V `MAP.2`, bloku s interným indexom 3, bunka `(x=61,y=54)` obsahuje wall ID `0x37`, trieda hlavičky 0 a definícia vo `WALLS.2` chýba. Ide o samostatný editor a jeho dodané dáta, nie o herný runtime. Ďalších 210 nájdených štítkov nebolo podrobených rovnako hlbokému auditu; program nebol spustený.

### Win16 — staticky uzavretý depth cache a damage scalar

Porovnanie C exportov V1.3, V1.6, V1.8 a V1.10 odhalilo stabilné prepojenie projekčného cache poľa OBJECT+0x18 s výpočtom damage. Adresy funkcií a globálov sa presúvajú; numerická logika damage helpera je po normalizácii adries a názvov symbolov rovnaká vo všetkých štyroch exportoch.

| Build | Renderer zapisujúci OBJECT+0x18 | Damage helper | Projekčný referenčný global | Volanie RNG |
|---|---|---|---|---|
| V1.3 | FUN_1010_CA5A | FUN_1010_9D80 | DAT_1048_532C | FUN_1018_2FA0 |
| V1.6 | FUN_1010_CBCE | FUN_1010_9EF4 | DAT_1048_53DE | FUN_1018_3210 |
| V1.8 | FUN_1010_CBCE | FUN_1010_9EF4 | DAT_1048_53EE | FUN_1018_32DA |
| V1.10 | FUN_1010_CC7C | FUN_1010_9FA2 | DAT_1048_53EE | FUN_1018_32D2 |

V podmienenej projekčnej ceste sa vypočíta relatívna hĺbka a jej hodnota po `>>4` sa uloží do OBJECT+0x18 ešte pred sprite-row/slot clampom. Staršie tvrdenie, že zápis prichádza až po úspešnom zaradení do viditeľnej sprite tabuľky, bolo príliš silné a týmto sa opravuje. Samostatný GUARD aim stamp zapisuje ešte užšia vetva s flagom 8 a stredovým X v tolerancii ±4 px. Damage helper číta OBJECT+0x18 a počíta:

1. base = (OBJECT+0x18 − build-specific projection reference) × 8 + RNG mod 25.
2. OBJECT class byte +6 vyberá posun. Prvý selector je globálna hodnota; jeho názov/sémantika sa zatiaľ neuzatvára ako „obtiažnosť“.

| Class ID | Úprava pred druhým selectorom |
|---|---|
| 0x0C, 0x1D | posun doprava o 3 |
| 0x0D | selector 1: doprava o 1; inak doprava o 3 |
| 0x0E, 0x11, 0x14 | selector 2: doprava o 1; inak doprava o 3 |
| 0x0F, 0x10 | selector 1: doprava o 8; inak doprava o 1 |
| 0x12, 0x13 | posun doprava o 2 |
| 0x15 | vykoná dodatočný side effect a nastaví výsledok na 0 |
| 0x16 | pri samostatnom globále rovnom 3 nastaví výsledok na 3; inak 0 |
| 0x17 | selector 1: doprava o 8; inak doprava o 2 |
| 0x18 | selector 1: doprava o 8; selector 2: doprava o 4; inak doprava o 3 |
| 0x19 | výsledok 0 |
| 0x1A | selector 1: doprava o 1; inak 0 |
| 0x1B, 0x1C | posun doprava o 1 |
| 0x1E | selector 1: výsledok 0; inak doprava o 3 |
| 0x1F | selector 1: výsledok 0; inak doprava o 2 |
| Ostatné | bez class-specific zmeny |

3. Druhý global selector výsledok pri hodnote 2 delí dvoma, pri 0 násobí dvoma a výsledok nad 255 obmedzí na 255.

V1.10 má statickú call chain FUN_1010_9D30 → FUN_1010_9B64 → FUN_1010_80F8 → FUN_1010_9FA2. Tým sa potvrdzuje, že +0x18 sa číta v hit/damage ceste, nie iba pri kreslení. Po novšej raw kontrole neplatí predchádzajúca silná podmienka „len po zaradení do viditeľnej tabuľky“; stále však ide o podmienenú cestu a damage helper pole číta bez lokálneho refreshu. Či je hodnota aktuálna pri zásahu mimo viditeľnosti alebo po otočení kamery, vyžaduje runtime test 3.

## 10. Stav každej oblasti z pôvodného zoznamu

| Pôvodná oblasť | Stav po tomto pokračovaní |
|---|---|
| P0 — hranice funkcií a dispatch | DOS raw audit opravil štyri hranice a klasifikoval šesť XMS miest; 31 z 37 nepriamych miest na build zostáva neklasifikovaných. Win16 vtable/message-map a skryté far-call ABI zostávajú otvorené. |
| P0 — GUARD AI | Doplnili sa DOS v2.0 smerovanie/pohyb, Win16 writer stav 0x0A, stav dverí 4, wake cache, stav 0x0B smrteľná vetva a stav 0x13 odpočítavanie pri blokovaní; úplný stav × stratégia × trieda × timer × percepcia graf a prirodzená dosiahnuteľnosť chýbajú. |
| P0 — kolízie a damage | Win16 depth/damage formula, guard→hráč difficulty multiplier, hitscan slučka a fire/contact rozdiely sú staticky preskúmané; cache freshness, všetky zdroje a hranice zásahu aj DOS parity ostávajú otvorené. |
| P0 — zbrane a projektily | Doplnený je DOS pohybový timer; Win16 cooldown môže uplynúť aj pri neúspešnom výstrele a impact slot drží do konca animácie. Celý spawn → collision → damage → free chain naprieč buildmi chýba. |
| P0 — USER.SAV/LOAD | Win16 loader rebazuje VEC/world OBJECT deadlines, obnovuje door pointers a prepočítava map pointers; DOS bloky 92/94 B sú odlišné. Kompletný field map, ďalšie bloky a runtime load počas eventu ostávajú otvorené. |
| P0 — čas, RNG, DEMO | Win16 8 Hz/no-catch-up model, LCG callsite katalóg a DEMO generation timestamp sú staticky doložené. Úplné poradie RNG, focus/pause/hardvérové časovanie a DEMO EOF/replay runtime ostávajú otvorené. |
| P0 — renderer | Win16 OBJECT+0x18 sa zapisuje podmienenou projekčnou cestou pred sprite-row/slot clampom; aim stamp má užší filter. Pixelová zhoda a cache freshness ostávajú runtime otázkou. DOS paleta/shade algoritmy sú izolovane otestované, nie framebufferovo porovnané. |
| P1 — USE, dvere a tajné panely | DOS raw state transitions, linked records, auto-close a USE gating sú doplnené; Win16 dverové writery sú nájdené. Všetky class handlery, zamietnutia, cleanup a ostatné builds ostávajú otvorené. |
| P1 — SAFE, TRUNK, rádio a pickupy | Win16 frame 0/1/obsah, rádio vetva E1M9 a neúspešný pickup retention sú staticky potvrdené; všetky triedy, limity a cancel/save prípady nie. |
| P1 — WARP, výťahy a triggery | Win16 susedné výstupy N/E/S/W a cardinal uhol sú doložené; occupancy, spätné prechody, one-shot a save/load udalosti naprieč buildmi ostávajú otvorené. |
| P1 — push objekty a špeciálne steny | DOS paired/four-way wall builders a pohyb sú raw preskúmané; Win16 blokovaný push zachová counter a completion vetvy sa líšia. Všetky triedy a callbacks naprieč buildmi chýbajú. |
| P1 — IMG/SEQDEF a facing | Win16 animátor posúva jednu snímku po deadline a RNG retry závisí od packed alternatív; úplný selector map a všetky epizódy/buildy ostávajú otvorené. |
| P1 — audio/MIDI a multimédiá | Známe sú niektoré Win16 cleanup/priority vetvy a DOS zvukové ID pri dverách; úplný DOS driver/Win MIDI, IRQ ownership a error/failure graf zostáva otvorený. |
| P1 — paleta, HUD a automapa | DOS GAME.PAL loader a dve odlišné color-distance metriky sú izolovane uzavreté; Win16 blackout/shade/HUD writery sú čiastočne doložené. Full palette writers a prirodzený framebuffer/HUD test chýba. |
| P1 — vstupné zariadenia | Win16 VK F2/F3/F4, joystick dead-zone a rozdiel menu/gameplay sú staticky doložené; edge/repeat, focus/pause a device fallback runtime testy čakajú. |
| P1 — CLI, konfigurácia a BSF | Doplnené sú DOS prepínače `-a/-w/-d/-f/-c/-e/-l`, CONFIG 16 B a Win16 CONFIG 20 B/BSF diff; DOS `-b`, zvyšné config bity a chybné vstupy ostávajú otvorené. |
| P1 — epizódy a úplnosť assetov | MAP.1–3 majú 31 fyzických blokov; jedna chýbajúca definícia wall 0x37 v MAP.2 je identifikovaná. E2/E3/build pairing a V1.10 data pack ostávajú otvorené. |
| P2 — 128 slabých párov | 19 individuálne auditovaných; 109 ostáva otvorených. Audit slabého páru automaticky nepotvrdzuje totožnosť medzi verziami. |
| P2 — class overlays a všetky GUARD/OBJECT polia | Niektoré jednotlivé polia/reader-writer väzby boli potvrdené, no úplné reader → writer → trigger → consumer reťazce chýbajú. |
| P2 — vtable, callback a message-map graf | 455 Win16 individuálnych auditov a 40 tematických oblastí zúžili graf; úplné callbacky, skryté ABI aj všetky 1 010/1 018 riadky zostávajú. |
| P2 — hash manifest | Osem odlišných herných EXE je hashovo doložených; DOS „V1.8“ kandidát je potvrdený ako V1.9. Historické/retail distribúcie a všetky asset páry nie sú úplne spárované. |
| P2 — build-specific behavior profile | Potvrdené rozdiely a zhody sú uvedené pri DOS/Win16 tabuľkách a doplnkových auditoch; úplný profil každého subsystému/build páru zostáva otvorený. |
| Desať runtime testov zo sekcie 6 | 0/10 end-to-end testov vykonaných; 501 DOS izolovaných scenárov nie je celý runtime. V tomto prostredí chýba emulátor/debugger. |

**Čo sa týmto krokom naozaj uzavrelo:** aktuálny row-level počet 455 auditov; identita kandidáta DOS V1.8 ako V1.9; štyri konkrétne DOS hranice funkcií; vybrané DOS steny, XMS, farby, CONFIG a CLI; desiatky Win16/MAP.EXE otázok v cielených tematických auditoch; Win16 GUARD dispatcher case set vo všetkých štyroch exportoch, stavy 0x0A a 0x0B bez AI case a stav 0x13 s odpočítavaním/kolíziou naprieč V1.3/V1.6/V1.8/V1.10. **Čo zostáva:** 1 031 individuálnych 12-bodových auditov, mnohé celé subsystémy, všetkých desať end-to-end runtime testov, kompletné historické buildy a nepárované assety.

## 11. Istota a použité podklady

**Vysoká istota:** identita hashovo overených vstupov, uvedené raw bajty, veľkosti blokov, dátové rozdiely a konkrétne izolované rutinné testy.  
**Stredná istota:** sémantické názvy a herné dôsledky bez prirodzeného runtime calltrace.  
**Otvorené:** úplná historická pokrytosť, všetky runtime stavy, celá DOS/Win16 ekvivalencia a pixelová/audio identita.

Použité aktuálne podklady: `Nitemare3D_Win16_all_available_versions_audit_2026-09-24.md`, `Nitemare3D_MSDOS_all_available_versions_audit_2026-09-24.md`, `DOS_v1_8_candidate_identification_2026-09-24.md`, `Nitemare3D_DOS_dalsia_analyza_neznamych_2026-09-24.md`, `DOS_static_deep_audit_2026-09-24.md`, `Nitemare3D_Win16_40_oblasti_hlbkovy_audit_2026-09-24.md`, `MAP_EXE_analyza_40_oblasti.md`, `Nitemare3D_all_functions_12_point_audit_2026-09-24.xlsx`, `Nitemare3D_1486_function_12_point_status_2026-09-24.csv`, `Nitemare3D_all_functions_manual_12_point_audit_progress_2026-09-24.md`, `Nitemare3D_MSDOS_unknowns_matrix_2026-09-24.csv`, `Nitemare3D_Reverse_Engineering_Master_Reference_2026-09-23.md`, `Nitemare3D_deep_unknowns_2026-09-23.md` a `Nite3W_function_checklist_unknowns_audit_2026-09-23.md`.

Použité aktuálne podklady navyše: N3D-DOS-UNFULL-v20.exe.c (SHA-256 5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54), NITE3W13.EXE.c, NITE3W16.EXE.c, NITE3W18.EXE.c a nite3w110.exe.c (SHA-256 71ca365f8c6a61fa9cadad8631e9fcd6ce134e36c714878889c75b7399280168); `Nitemare3D_DOS_nove_dokazy_a_testy_2026-09-24.zip`, `Nitemare3D_Win16_40_oblasti_evidence_2026-09-24.zip` a `MAP_EXE_dokazy_a_skripty.zip`; priebežný audit v19, CSV v19, workbook v21 a DOS matica v1.

Žiadny z uvedených súhrnov sa nepoužíva ako náhrada za chýbajúci binárny alebo runtime dôkaz.

## 12. Nové uzavretie: Win16 GUARD stav 0x0B

**Potvrdené:** V1.3, V1.6, V1.8 a V1.10 zapisujú bajt GUARD `+0x0B = 0x0B` z jedinej nájdenej setter funkcie. Setter sa volá iba z obsluhy poškodenia guardom hráča v smrteľnej vetve: vypočítané poškodenie dosiahne aktuálne hráčove HP, HP sa nastaví na nulu, globálny herný stav na 2 a uloží sa index guardu. V1.10 raw caller `3:8C0A` túto postupnosť potvrdzuje na `8C41–8C79`, vrátane vzdialeného volania na `3:80EA`. Všetky štyri dekompilované dispatchery nemajú `case 0x0B`; kód preto nepodporuje predpoklad, že ide o ďalší bežný AI režim.

| Build | Zapisovač stavu | Volajúca funkcia pri smrti hráča | Dispatcher stavu |
|---|---|---|---|
| Win16 V1.3 | `3:7ED2` | `3:89F2` | `3:793E` |
| Win16 V1.6 | `3:8046` | `3:8B66` | `3:7AB2` |
| Win16 V1.8 | `3:8046` | `3:8B66` | `3:7AB2` |
| Win16 V1.10 | `3:80EA` | `3:8C0A` | `3:7B56` |

**Odvodené, stredná istota:** `0x0B` je koncový stav guardu pri prechode do smrti hráča, nie neznámy AI handler. Bez prirodzeného behu sa neuzatvára, či sa guard ešte vykreslí, ktorý frame zostane na obrazovke ani či existuje iný externý konzument stavu.

**Čo táto oprava neuzatvára:** ostatnú stav×stratégia×trieda tabuľku, runtime dosiahnuteľnosť, animáciu smrti hráča ani DOS ekvivalent. Ďalší rozlišujúci test je zaznamenať stav guardu, globálny herný stav, ďalšie volania dispatchera a poslednú snímku pri smrteľnom kontakte vo Win16 V1.10.

## 13. Nové uzavretie: Win16 GUARD stav 0x13 pri blokovanom pohybe

**Potvrdené staticky:** stratégia 3 zo stavu 7 môže založiť stav `0x13`; nastaví časovač `RNG % 80 + 8` a smerové delty. Update ho dekrementuje ako prvý krok. Pri novom timere 8 prehrá zvukovú udalosť. Pri novom timere 7…0 sa skúša posun. Ak mapová bunka alebo zdieľaná podmienka obsadenosti blokuje cieľ, kód odíde bez zmeny X/Y, ukazovateľa na aktuálnu bunku ani jej bajtu obsadenosti; časovač napriek tomu pokračuje. Po ôsmich blokovaných pokusoch (pôvodné hodnoty 8 až 1) nasledujúci dispatcher tick s pôvodnou hodnotou 0 nastaví `+0x0A=0`, `+0x0B=2`.

| Build | Zapisovač časovača/stavu | Update pohybu | Dôkaz |
|---|---|---|---|
| Win16 V1.3 | `3:77EE` | `3:782C` | C export `NITE3W13.EXE.c:24189–24250, 24459` |
| Win16 V1.6 | `3:7962` | `3:79A0` | C export `NITE3W16.EXE.c:24295–24356, 24563` |
| Win16 V1.8 | `3:7962` | `3:79A0` | C export `NITE3W18.EXE.c:24299–24360, 24567` |
| Win16 V1.10 | `3:7A06` | `3:7A44` | C export `nite3w110.exe.c:24308–24365, 24579–24581`; raw `3:7A50–7B4B` v evidence ZIP |

**Čo zostáva otvorené:** runtime potvrdiť, že konkrétna mapa/pozícia aktivuje práve tento state, aký event zvuku sa v prostredí počuje a aký frame sa zobrazí počas/po ôsmich neúspešných pokusoch. Statická vetva už neurčuje tento prirodzený vizuálny/audio výsledok.