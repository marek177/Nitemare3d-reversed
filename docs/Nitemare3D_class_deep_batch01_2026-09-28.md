# Nitemare3D: triedy objektov 0x02, 0x03 a 0x08 — analytická várka 1

Dátum: 28. 9. 2026. Zdroj bajtov: Library `nitemare.zip`, súbory `MAP.1–3`, `OBJECTS.1–3`, DOS a Win16 EXE. Pomocné podklady: `Nitemare3D_function_quick_catalog_2026-09-28.csv`, `Nitemare3D_Reverse_Engineering_Master_Reference_2026-09-23.md`, `Nitemare3D_MSDOS_all_available_versions_audit_2026-09-24.md`. `OBJECTS` je editorová definícia názvov; názov nie je dôkazom celej runtime funkcie.

## Metóda

Header každého MAP obsahuje po dvojbajtovom počte máp 256-bajtovú tabuľku tried stien a 256-bajtovú tabuľku tried objektov. Druhý bajt každej bunky 64 × 64 je ID objektu. Každé nižšie uvedené ID sa mapovalo cez tabuľku príslušného MAP a vyhľadalo v textovom `OBJECTS` danej epizódy. Pri buildoch bez samostatného OBJECTS bol použitý epizódny referenčný súbor `N3D-Dos` alebo `N3D-Win`; tento editorový názov sa preto nedá tvrdiť ako verzovo jedinečný.

| Trieda objektu | Potvrdené ID a názov v OBJECTS | Výskyt v priložených MAP | Istota identity |
|---|---|---|---|
| 0x02 | 01–04: `START`, orientácie N/E/S/W | E1: 11 buniek v 11 mapách; E2: 10/10; E3: 10/10 | Vysoká pre mapovanie ID/názov |
| 0x03 | 62: `SECRET`, Secret panel | E1: 206 buniek; E2: 70; E3: 123 | Vysoká pre mapovanie ID/názov |
| 0x08 | 80–83: `GUARD1`, Bat N/E/S/W | E1: 64 buniek; E2: 15; E3: trieda 0x08 v dodanom MAP.3 neprítomná | Vysoká pre mapovanie ID/názov |

Počty platia pre epizódne MAP v `N3D-Dos` a `N3D-Win`; pri E1 sú tieto počty rovnaké v skontrolovaných verziových MAP. Sú to výskyty buniek vrátane E1M11, nie počty jedinečných objektov pri behu ani dôkaz aktivácie v každej obtiažnosti.

## 0x02 — START

**Potvrdené:** štvorica ID 01–04 má v OBJECTS názvy `Start position N/E/S/W`; vo všetkých 31 epizódnych mapách je presne jedna bunka z tejto triedy. Je to značka počiatočnej polohy/orientácie podľa editorovej definície. **Odvodené:** loader zrejme vyberá súradnice a smer hráča z tejto bunky. **Neznáme:** presný EXE dispatcher, reprezentácia smeru a správanie pri nulovej alebo viacnásobnej značke; zatiaľ neoznačovať konkrétnu funkciu za potvrdený START handler. Otestovať breakpoint na čítaní objektového bajtu MAP pri inicializácii E1M1, potom kontrolovať zápis hráčskych X/Y a smeru.

## 0x03 — SECRET

**Potvrdené pre skúmanú vetvu Win16 1.10:** ID 62 mapuje na triedu 03; inicializácia panelu spája najviac štyri susedné wall/door záznamy, alokuje panelový záznam z kapacity 32 a ukladá aktiváciu na byte +0x14. Aktivácia používa zvukový event 0x27. Relatívny index triedy vyberá bit v `DAT_1048_51A4`; cesta overuje credential bit v `DAT_1048_4C29` a následné menu odosiela príkazy 0x1E/0x1F do príslušných párových stien. Pozri master reference, sekcia 9.2. **Neznáme:** presné mená oboch príkazov podľa ich účinku, správanie všetkých panelov pri rôznych kartách, parity DOS a Win16 1.3/1.6/1.8. Počet 206 panelových značiek v epizóde neznamená súčasne 206 runtime panelov; limit 32 je na načítanú mapu.

## 0x08 — GUARD1 / Bat

**Potvrdené:** ID 80–83 sú orientačné varianty netopiera. DOS audit prichádzajúceho poškodenia uvádza pre OBJECT class 08 pred úpravou obtiažnosťou výraz `RNG & 7`; nezávislá izolovaná emulácia pôvodného kódu overovala class dispatch pri štyroch DOS buildoch. Zvyšok guard správania pre túto triedu treba odlíšiť od spoločnej guard state machine. V pracovnom katalógu DOS 1.8 a 2.0 sú rutiny `FUN_1000_5f26` (`SpawnOrResetGuard`) a `FUN_1000_4be0` (väčší guard state-machine cluster); ich pracovné názvy nepreukazujú samostatný Bat handler. **Neznáme:** konkrétne HP, rýchlosť, vizuálna sekvencia, per-class vetvy Win16, spôsob zmeny Dracula → Bat a DOS/Win16 parita damage vzorca.

## Verzový rozsah a ďalšia kontrola

Dodané EXE: DOS 1.0, 1.7, 1.9, 2.0 a Win16 1.3, 1.6, 1.8, 1.10. Dodané epizódne MAP.2/.3 sú iba v referenčných `N3D-Dos` a `N3D-Win`; preto ich názvy a výskyty nemožno bez ďalších balíkov priradiť osobitne každej verzii EXE. Súbor označený DOS 1.8 bol v predchádzajúcom audite identifikovaný ako kópia 1.9. Pri ďalšej várke treba pre každý class byte zaznamenať priame EXE porovnania, volajúce funkcie, čítané polia, testovací MAP prípad a verziový rozdiel.