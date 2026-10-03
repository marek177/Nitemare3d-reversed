# Nitemare 3D — analýza otvorenej logiky

**Dátum:** 23. 9. 2026  
**Rozsah:** DOS v2.0 a Win16 NITE3W 1.10; doplnkový dôkaz z Win16 1.8  
**Podklady:** dekompiláty N3D-DOS-UNFULL-v20.exe.c, nite3w110.exe.c a existujúce funkčné mapy.

## Čo znamená dnešný stav analýzy

Ghidra rozpoznala 519 funkčných definícií v DOS exporte a 967 vo Win16 exporte. Všetkých 1 486 je zatriedených podľa pravdepodobného subsystému, ale len prvých 200 z každej vetvy bolo podrobne ručne rozobratých. Viacverziové párovanie podopiera 1 358/1 486 položiek, teda 91,4 %, identitou alebo silnou podobnosťou. To nie je percento úplného pochopenia ich správania.

Nižšie sú nové zistenia, ktoré sa dajú priamo odvodiť z tiel funkcií. Slovné názvy zostávajú pracovnými názvami, ak pri nich nie je uvedená priama operácia.

## 1. Klávesová logika Win16

Funkcia **FUN_1010_8cd2** je spoločný vstupný dispatcher pre klávesové správy. Jej volajúci sú obsluhy klávesových a systémových klávesových udalostí.

| Vstup | Priama operácia | Istota |
|---|---|---|
| Ľavý Shift, scan code 0x2A | nastaví bit 0x40 v DAT_1048_3756 | potvrdené |
| Pravý Shift, scan code 0x36 | nastaví bit 0x20 v DAT_1048_3756 | potvrdené |
| Ctrl | nastaví bit 0x80 v DAT_1048_3756 | potvrdené |
| Alt | nastaví bit 0x01 v DAT_1048_3757 | potvrdené |
| Escape | bit 0x01 v DAT_1048_3756 | potvrdené |
| Šípky | vľavo 0x08, hore 0x02, vpravo 0x10, dole 0x04 v DAT_1048_3756 | potvrdené |
| Space | bit 0x02 v DAT_1048_3757 | potvrdené |
| Q | prepne hudbu; zobrazí Music on/off, keď je hra aktívna | potvrdené |
| R | prepne zvukové efekty; zobrazí Sound on/off, keď je hra aktívna | potvrdené |
| Alt+Enter | prepína zobrazenie cez režimy 3/4 funkcie FUN_1010_2d9c; režim 3 vstupuje do fullscreen, režim 4 obnoví uloženú veľkosť okna | potvrdené |
| Alt+S | vymaže vstupný stav a odošle vlastnú správu oknu | odoslanie potvrdené, účel správy neznámy |

Druhý parameter vstupného dispatcheru obsahuje stavový bit 0x8000, ktorý kód používa pri nastavovaní a čistení bitov klávesov. Presný význam tohto bitu na úrovni pôvodnej Windows správy treba ešte potvrdiť kontrolou troch callerov v raw assembleri. Z mapy bitov ešte nevyplýva úplný význam každého bitu v hernej simulácii; to vyžaduje prejsť všetkých jeho čitateľov.

V tomto dispatcher-i sa nenašiel prepínač príkazového riadka ani debug príkaz. To nepreukazuje ich neexistenciu inde v programe. Význam Alt+S a presný postup prehľadania štartovacej vetvy zostávajú otvorené.

## 2. DAT_1048_7E60 riadi úroveň stmavenia

Predtým nejasný 16-bitový údaj **DAT_1048_7E60** sa používa ako úroveň úpravy farieb pri vykresľovaní.

Priama evidencia:

- **FUN_1010_29be** používa tabuľku úrovní 0, 4, 8, 12, 16, 20, 30, 40.
- Pre každú z 236 farieb znižuje R, G a B o štyrikrát zvolenú hodnotu, s dolným limitom nula.
- Pre každú upravenú farbu vyberie najbližšiu farbu zo základnej 236-farebnej palety podľa súčtu absolútnych rozdielov R+G+B. Výsledky zapisuje do remap tabuľky DAT_1048_8094 pre indexy 10–245.
- Efektívne stmavenie jednotlivých úrovní je 0, 16, 32, 48, 64, 80, 120 alebo 160 jednotiek na každý RGB kanál.
- **FUN_1010_c5e2** nastaví úroveň na DAT_1048_4698, ak je hodnota nezáporná; inak použije predvolenú úroveň 2. Pri príznaku DAT_1048_51AB nastaví úroveň 6.
- **FUN_1010_66b0** posúva túto úroveň ďalej do vykresľovania segmentov. Hodnota DAT_1048_7E60 sa zapisuje aj načítava v save/load rutinách.

**Záver s vysokou istotou:** DAT_1048_7E60 je farebná/ambientná úroveň stmavenia. Hodnota 2 je predvolený vzhľad, hodnota 6 je silne stmavený špeciálny stav.

**Čo ešte treba uzavrieť:** presný zdroj a platný rozsah DAT_1048_4698; kontrola, či načítaná uložená hodnota vždy patrí do rozsahu 0–7; všetky vykresľovacie vetvy, ktoré používajú alebo obchádzajú remap tabuľku. DAT_1048_51AB sa nastavuje a čistí v story/event vetvách, preto treba otestovať jej trvanie a presný herný prejav.

## 3. Presnejší model Win16 vector/span renderera

Tri predtým otvorené miesta teraz tvoria súvislý tok: projekcia steny → výber viditeľného vlastníka každého stĺpca → zlúčenie stĺpcov do segmentov.

### Projekcia a clipping — FUN_1010_e798

Funkcia číta koncové body vektorového záznamu na offsetoch +0x0C, +0x0E, +0x10 a +0x12; odčíta polohu hráča a použije smerové hodnoty DAT_1048_4C46 a DAT_1048_4C48. Hodnoty na +0x14..+0x1A sú výstupné projektované súradnice koncov vektora: X0, Y0, X1, Y1. Kód oreže blízku rovinu pri 0x4000, premietne konce cez projekčný faktor DAT_1048_3A72 a obmedzí vodorovný rozsah na DAT_1048_53E4..DAT_1048_53E6.

### Occlusion podľa viditeľnosti — FUN_1018_3564 a FUN_1018_3940

FUN_1018_3940 prechádza štyri samostatne zoradené zoznamy vektorov. Pre každý kandidátsky stĺpec používa FUN_1018_3564. Tá:

1. odmietne vektor bez eligibility bitu 0 na +0x05;
2. premietne a oreže jeho rozsah;
3. zapíše far pointer vektora do vlastníckeho bufferu od 0x53FE, štyri bajty na stĺpec;
4. pri už obsadenom stĺpci porovná orientáciu +0x07 a koncové súradnice kandidátskych vektorov a podľa smeru hrany nahradí vlastníka, ak nový vektor vyhráva test prekrytia;
5. vedie počet prázdnych stĺpcov v DAT_1048_53FC a skončí, keď sú všetky stĺpce priradené.

Toto vysvetľuje, prečo renderer nie je klasický Wolf3D renderer s jedným nezávislým lúčom na každý stĺpec. Vektory sa triedia podľa orientácie, premietajú sa a potom sa ich vlastníctvo rozhoduje pre každý obrazový stĺpec.

### Span record — FUN_1010_6266 a FUN_1010_6152

FUN_1010_6266 zlúči súvislé stĺpce s rovnakým vlastníkom. Má maximum 50 záznamov po 20 bajtov; počet je v DAT_1048_5E7E a začiatok poľa je 0x5E88.

| Offset v 20 B zázname | Význam podľa priamych čítaní/zápisov |
|---:|---|
| +0, +2 | far pointer na vektor, offset a segment |
| +4 | prvý X stĺpec spanu |
| +8 | posledný X stĺpec spanu |
| +6, +0x0A | interpolované Y hodnoty na koncoch spanu |
| +0x0C | 16.16 sklon dY/dX |
| +0x10 | počiatočná zlomková časť interpolácie |
| +0x12 | vertikálna základňa voči stredu projekcie |

FUN_1010_6152 vypočíta sklon a vertikálnu hodnotu na oboch X hraniciach. Tým je odstránená hlavná neznáma o účele 20-bajtového visible-span záznamu.

**Stále otvorené:** úplné pravidlá porovnávania všetkých dvojíc orientácií pri prekrytí; finálny texel-write cyklus; masked/transparent steny a čiastočne otvorené dvere; presné fixed-point zaokrúhľovanie a zhoda s originálnymi snímkami. Tieto body vyžadujú raw assembler alebo porovnanie render výstupov z rovnakých pozícií.

## Zvyšné neznáme podľa priority

### P0 — správanie potrebné na vernú hernú logiku

1. **GUARD AI:** presné mená a prechody stavov 0x02–0x14, všetky strategy hodnoty, sight/FOV/range, line-of-sight a reakcia na zvuk. Stavový switch je viditeľný, ale časť názvov a podmienok je stále pracovná.
2. **Čas a sekvencie:** časová jednotka v celej hre; seqdef intervaly, loop/ping-pong/one-shot pravidlá a synchronizácia s frame rate; dvere, wall animácie a actor animácie.
3. **Zbrane a projectile:** cadence, spread/range, rýchlosť a lifetime projektilu, presný hitbox a damage link. Časť class×weapon resistance a difficulty scaling je už numericky potvrdená.
4. **Hazardy:** damage a interval ohňa podľa veľkosti, kolízia pri zatváraní dverí a presné správanie projectile pri každom type steny.
5. **Špeciálne triedy:** triedy 03–06, ONE_SHOT, SPECIAL1 a object triedy 26–29; presné prepojenie class ID na každý mapový/grafický variant. Trigger1/2 sú oddelené epizódové skripty; remote dverové menu má samostatnú cestu cez class 03 a príkazy 0x1E/0x1F.
6. **Kolízie a pohyb:** plný význam radius/flags/sliding, blokovanie guardov v dverách, hraničné prípady teleportu a špeciálna stair-trap vetva push objektov.

### P1 — uložené stavy a presná zhoda

- USER.SAV bloky 336 B pri 0xC403, 32 B pri 0xC3E3, 8 B pri 0xC553, 4096 B pri 0xC5A3, 64 B pri 0xD5A3 a 256 B pri 0xD5E3; časovače, ktoré sa rebazujú pri load.
- Object 28 B a Guard 26 B záznamy: nepomenované polia a ich všetci čitatelia/zapisovači.
- VEC 28 B: zostávajúce flags a presná životnosť štyroch 333-prvkových zoznamov.
- Úvodná a finálna levelová udalosť E3M10: trigger → Penelope/Hammerstein → smrť bossa → FLI → score/menu.

### P2 — obsahové formáty a platformové rozdiely

- SND.DAT payload/codec/sample rate a prečo niektoré exporty neznejú správne.
- UIF.DAT sloty 0–2; presný rozsah a účel prázdnych slotov 17–31.
- ENDING.FLI: deklarovaných 488 snímok verzus 489 fyzických blokov a koncové prázdne bloky.
- DEMO.2/3: mapovanie záznamov na tlačidlá, level a tick.
- Joystick scaling/dead-zone a rozdiely VGA DOS voči WinG.
- Debug prepínače a command-line parser: zatiaľ neidentifikovaná startup vetva. Diagnostický logger do debug.txt existuje v neskorších Win16 buildoch, ale jeho existencia sama osebe nepotvrdzuje používateľský prepínač.

## Najbližšie konkrétne kroky

1. Sledovať všetky read/write XREF pre DAT_1048_4698 a DAT_1048_7E60; skúsiť uloženú hodnotu mimo 0–7 a overiť validáciu.
2. Pri GUARD state machine vytvoriť tabuľku writer → handler → timer → pohyb → zvuk pre každý číselný stav a porovnať DOS 2.0 s Win16 1.8/1.10.
3. Získať seqdef intervaly a globálnu časovú jednotku; tým sa uzavrie význam frame count, animácie stien aj časť AI.
4. Rozobrať 20-bajtový span emitter od FUN_1010_66b0 po texture bytes a porovnať s originálnym obrazom.
5. Rozdeliť DOS zlúčené oblasti 1000:70D6, 1000:84FE, 1000:8590, 1000:87D8 a 2000:9364 podľa raw CALL/RET/RETF cieľov a starších DOS verzií.
6. Párovať save/read/write offsety po bajtoch pre zostávajúce anonymné bloky.
7. Overiť DEMO, SND, UIF a FLI cez loader callsites; formát z disku sám nedokáže potvrdiť runtime význam.

## Istota a obmedzenia

- **Potvrdené:** konkrétne porovnanie, čítanie/zápis, limit, volanie alebo aritmetika v dekompiláte.
- **Vysoká interpretácia:** viacero nezávislých operácií podporuje názov subsystému, no test v pôvodnej hre chýba.
- **Otvorené:** vyžaduje raw assembler, call-site analýzu, runtime trace alebo porovnávací test.

Oprava dnešného auditu je merateľná: vstupné skratky sú pomenované, 16-bitový shade parameter má priamu funkciu a span záznam má zmapovanú dátovú úlohu. Celá logika hry ešte nie je uzavretá; zvyšné oblasti sú uvedené vyššie podľa toho, čo najviac bráni vernej reprodukcii.


## 4. Seqdef dispatcher a dokončenie explodujúcej steny (2026-09-23)

Ďalší prechod cez DOS v2.0 a Win16 NITE3W 1.10 potvrdil, že animačný dispatcher oboch buildov má rovnakú jadrovú štruktúru. Pri Win16 sa navyše našla priama dokončovacia cesta pre runtime triedu `0x2D`, ktorá uzatvára časť doterajšej neznámej logiky explodujúcej steny.

### Potvrdené správanie sekvenčného dispatcheru

`FUN_1000_241e` v DOS exporte a `FUN_1010_65a6` vo Win16 1.10:

1. Čítajú 32-bitový termín objektu na `object+0x08`. Ak globálny čas ešte termín nedosiahol, nemenia frame.
2. Pri dosiahnutí termínu zvýšia `object+0x03` o jeden.
3. Sekvenčný záznam má podľa priamych offsetov: frame count na `seqdef+0`, interval na `seqdef+2` a voliteľný pointer na tabuľku alternatív na `seqdef+4`.
4. Po spracovaní nastavujú nový termín na `global_time + seqdef.interval`. Vo Win16 sa carry z low word správne prenáša do high word.

Pre triedu `object+0x06 >= 0x30`:

- Ak `seqdef+4` je null, dispatcher po dosiahnutí frame count nastaví frame na nulu. Ide o opakovanú sekvenciu.
- Ak pointer nie je null, používa osem 16-bitových položiek. `object+0x02` vyberá položku; jej dolný bajt je počiatočný frame a horný bajt počet frame-ov v tejto vetve. Test hranice používa súčet oboch bajtov. Po dohraní vetvy generátor vyberá slot 0–7 a opakuje výber, kým nenájde položku s nenulovým horným bajtom; index slotu uloží do `object+0x02` a dolný bajt položky do `object+0x03`.
- Opakované platné položky v ôsmich slotoch môžu meniť zastúpenie vetvy. Či sa konkrétny RNG správa rovnomerne, ani skutočné obsahy tabuliek sme zatiaľ neoverili.

Špeciálne triedy majú osobitné pravidlá: `0x2F` sa v tejto rutine vracia na frame 0; `0x07` nepoužíva bežný loop; `0x2D` po dosiahnutí frame count prechádza dokončovacou rutinou. Ich herný význam sa nesmie odvodiť iba z týchto čísel.

### Explodujúca stena — Win16 1.10

Kolízna vetva projektilu vo `FUN_1010_9d30` volá `FUN_1010_9b64`. Pri stene s vlastnosťou bit `0x10` sa prehrá SFX `0x29`, vyhľadá sa runtime object príslušnej triedy a prechádza do triedy `0x2D`. Pri variante `.` nastaví `object+0x03=0`, zapíše class `0x2D` do `object+0x06`, vyberie sequence a založí ďalší termín. Variant `/` začína na frame 1.

Keď animačný dispatcher `FUN_1010_65a6` dosiahne frame count tejto triedy, volá `FUN_1018_3c0c`. Jej telo:

- používa `FUN_1018_3736` na prevod hraníc objektu z herných súradníc na bunky mapy (delenie 64),
- odstraňuje bit `0` z `object+0x05`,
- zapisuje nulu do prvého bajtu buniek pozdĺž vypočítanej vodorovnej alebo zvislej stopy; krok medzi bunkami je 2 bajty,
- následne nastavuje frame na posledný platný index, aby sa dispatcher nevrátil na začiatok animácie.

To je silný statický dôkaz, že vo Win16 1.10 sa po dohraní sekvencie odstraňuje stena/blokovanie na jej mape, nie iba jej kreslenie. Interpretácia „prvý bajt páru buniek = wall ID“ zodpovedá známemu rozloženiu MAP, ale konkrétnu stopu a úplnú podmienku ukončenia vnútorného hľadania treba ešte potvrdiť v raw assembleri alebo runtime trace: Ghidra C export tu vytvára podozrivé kontroly pointerov vo while slučke.

DOS v2.0 má analogickú vetvu `0x2D` v `FUN_1000_241e`, ale cieľ jej callu sa v raw EXE rozchádza s dekompilovanou hranicou. Preto zatiaľ prenášam záver o odstraňovaní mapovej steny iba na Win16 1.10; DOS potrebuje osobitné potvrdenie segmentového mapovania a zápisov.

### Dôkazy a otvorené okraje

| Tvrdenie | Zdroj | Istota |
|---|---|---|
| Dospelý termín spustí krok frame; nový termín je súčet globálneho času a seqdef intervalu | `NITE3W 1.10`: `FUN_1010_65a6`, export riadky 23127–23189; `DOS v2.0`: `FUN_1000_241e`, riadky 3022–3088 | potvrdené v oboch exportoch |
| Osem slotov alternatív kóduje počiatočný frame a dĺžku vetvy | Win16 riadky 23169–23183; DOS riadky 3063–3080 | potvrdená interpretácia bajtov kódu |
| Trieda `0x2D` spúšťa mapovú dokončovaciu cestu vo Win16 | `FUN_1010_65a6` + `FUN_1018_3c0c`, export riadky 23161–23164 a 35195–35243 | silná statická evidencia; presná stopa/loop partial |
| DOS trieda `0x2D` vykoná rovnaký cleanup | DOS raw call target sa nezhoduje s exportovanou hranicou `FUN_1000_04be` | otvorené |

Ďalší cielený test: vyťažiť reálne seqdef záznamy a intervaly pre `WALL_EX1/EX2`, potom zaznamenať wall-ID, object flags a bunky MAP pred/po poslednom frame. Tým sa overí počet odstránených buniek, dotknutý bajt bunky a rozdiel DOS/Win16.