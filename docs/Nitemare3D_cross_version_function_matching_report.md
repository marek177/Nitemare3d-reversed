# Nitemare 3D – krížové párovanie funkcií medzi verziami

Dátum: 2026-09-22

## Cieľ

Použiť staršie DOS a Windows zostavenia na identifikáciu rovnakých rutín, opravu nesprávnych hraníc funkcií v Ghidre a doplnenie zlyhaných dekompilácií. Adresy sa medzi verziami menia, preto sa funkcie nepárovali iba podľa `segment:offset`, ale podľa normalizovaného tvaru dekompilovaného kódu.

## Zahrnuté dekompiláty

| Vetva | Verzia/súbor | Extrahované telá funkcií |
|---|---|---:|
| DOS | `N3D-E-10.EXE.c` | 493 |
| DOS | `N3D-E-17.EXE.c` | 514 |
| DOS | `N3D-E-18.EXE.c` | 526 |
| DOS | `N3D-E-20.EXE.c` | 519 |
| Windows | `NITE3W13.EXE.c` | 959 |
| Windows | `NITE3W16.EXE.c` | 965 |
| Windows | `NITE3W18.EXE.c` | 965 |
| Windows | `nite3w110.exe.c` | 967 |

DOS 1.9 je dostupný ako EXE/Ghidra projekt, ale v súčasnom súbore vstupov chýba samostatný C export. Dá sa zaradiť v ďalšom kole cez raw-binary/opcode porovnanie.

## Metóda

1. Brace-balanced extrakcia každého tela `FUN_segment_offset`.
2. Vylúčenie samostatných volaní, ktoré by sa mohli chybne považovať za definíciu.
3. Normalizovanie lokálnych premenných, parametrov, presunutých globálov, labelov, cieľov volaní a veľkých adries.
4. SHA-256 presne normalizovaného tela pre jednoznačné zhody.
5. Tokenové trigramy a Jaccard podobnosť pre funkcie s vloženým alebo odstráneným kódom.
6. Porovnanie poslednej dostupnej vetvy proti všetkým starším verziám rovnakej platformy.

`exact-normalized` znamená identický riadiaci a aritmetický tvar po odstránení relokácií/názvov. `fuzzy-normalized >= 0.72` je silný kandidát, ktorý treba potvrdiť disassembly. Slabšia zhoda sa nepovažuje za dôkaz identity.

## Výsledky

| Cieľová vetva | Funkcií | Presná zhoda | Silná fuzzy zhoda | Slabá/bez zhody |
|---|---:|---:|---:|---:|
| DOS 2.0 | 519 | 355 | 74 | 90 |
| Nite3W 1.10 | 967 | 684 | 245 | 38 |
| **Spolu** | **1 486** | **1 039** | **319** | **128** |

### Pokrytie

- DOS: 429/519, teda **82,7 %**, má presnú alebo silnú viacverziovú zhodu.
- Windows: 929/967, teda **96,1 %**, má presnú alebo silnú viacverziovú zhodu.
- Celkovo: 1 358/1 486, teda **91,4 %**, možno podoprieť staršou verziou.

## Zistenia pre poškodené funkcie

### `FUN_1000_0AEA`

Ghidra ju nedokázala dekompilovať v DOS 1.7, 1.8 ani 2.0. To ukazuje stabilný problém analýzy rovnakého 16-bitového konštruktu, nie jednorazovo poškodený EXE. Najlepšou cestou je porovnať raw bajty s DOS 1.0 a manuálne určiť far/near hranice a vstupný stav segmentových registrov.

### `FUN_1000_4A86`

Dekompilácia zlyháva v DOS 1.8 a 2.0. Staršie vetvy 1.0/1.7 sú preto prioritným zdrojom ekvivalentu. Ak sa adresa presunula, treba hľadať podľa callerov, konštánt a normalizovaných susedných funkcií, nie podľa offsetu `4A86`.

### `FUN_2000_9364`

V DOS 2.0 je to extrémny zlúčený blok s približne 6417 riadkami. Najlepší fuzzy kandidát v DOS 1.7 je `FUN_2000_9194` s približne 6527 riadkami, ale podobnosť iba 0,2397 nestačí na potvrdenie jednej funkcie. Veľkosť v oboch verziách dokazuje, že Ghidra opakovane pohltila rozsiahlu runtime oblasť. Blok treba rozdeliť podľa:

- všetkých cieľov `CALL` smerujúcich dovnútra rozsahu,
- `RET/RETF/IRET` a následných platných prologov,
- switch/jump tabuliek omylom označených ako kód,
- exportov a relocation entries v MZ obraze,
- správne rozpoznaných hraníc v IDA projektoch 1.0/1.7/1.8/2.0.

## Čo možno opraviť automaticky

1. Preniesť identitu a navrhovaný názov na 1 039 presných zhôd.
2. Vytvoriť kandidátov pre 319 silných fuzzy zhôd a potvrdiť ich cez callgraph.
3. Pri rozdielnych hraniciach porovnať počet riadkov/tokov a označiť split/merge kandidátov.
4. Nájsť funkciu, ktorá v jednej verzii existuje samostatne, ale v druhej leží uprostred veľkého zlúčeného bloku.
5. Porovnať caller/callee okolie, reťazce, konštanty a štruktúrne stride hodnoty.

## Čo vyžaduje manuálnu kontrolu

- 90 DOS a 38 Windows funkcií bez silnej zhody;
- funkcie nové iba v poslednej verzii;
- krátke thunky s málo rozlišujúcimi inštrukciami;
- funkcie používajúce inline assembly, port I/O alebo neštandardné segmentové registre;
- všetky obrovské zlúčené bloky a adresy, kde Ghidra hlási `Unable to decompile`.

## Odporúčané poradie opravy

1. DOS `FUN_1000_0AEA` a `FUN_1000_4A86` cez staršie verzie a raw disassembly.
2. Rozdelenie `FUN_2000_9364` pomocou vnútorných call targetov.
3. Prenos 1 039 presných identít do master function mapy.
4. Callgraph potvrdenie 319 fuzzy zhôd.
5. Zaradenie DOS 1.9 a raw EXE porovnania, aby sa vyplnila medzera medzi 1.8 a 2.0.

## Súbory výsledkov

- `function_counts.csv` – počet funkcií v každom dekompiláte.
- `cross_version_matches.csv` – najlepší starší kandidát pre každú funkciu DOS 2.0 a Nite3W 1.10.
- `summary.csv` – súhrn presných, fuzzy a nevyriešených zhôd.
- `match_functions.py` – reprodukovateľný normalizačný a párovací nástroj.

## Záver

Viacverziová analýza je účinná: **91,4 % analyzovateľných funkcií posledných DOS/Windows vetiev má oporu v staršej verzii**. Sama osebe neopraví chybnú disassembly, ale výrazne zužuje miesto a správny tvar každej rutiny. Najväčší zostávajúci problém nie je neexistencia porovnávacieho materiálu, ale manuálne rozdelenie niekoľkých opakovane zle rozpoznaných 16-bitových oblastí.