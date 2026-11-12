# PASS1: CRT spawn texty, parameterový záznam a callback

Dávka staticky typuje 83 B v 17 poliach. Ide o PARTIAL, nie DEEP VERIFIED: proces sa nespúšťa, DOS parsovanie ani alokátor sa nevykonávajú. Texty sú doložené konkrétnymi konzumentmi a ukazovatele konkrétnymi operandmi, nie len čitateľnosťou alebo nulami.

## Vstupy a metóda

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. `audit_pass1_crt_spawn_data.py IMAGE INVENTORY DECODER OUT` overuje identity, presné pôvodné bajty polí a 169 inštrukcií vybraných kontextov pomocou nezávislého 16-bitového dekódera.

`data_fields.csv` má presné polootvorené intervaly, dĺžky, range SHA a evidence CS:IP. `instruction_contexts.csv` má pôvodné inštrukčné bajty a dekódovanie. Kontexty nie sú celé uzavreté funkcie a nepridávajú sa k centrálnemu bounded počtu funkcií alebo kódu. Kanonické mapovanie DS=2771h je pri interpretácii dát podmienkou; startup všetkých prirodzených callerov sa tu neoveruje.

## Katalóg polí

| DS offset | Image interval, koniec exclusive | Typ / presný obsah | Konkrétny dôkaz |
|---|---|---|---|
| 24BC | [29BCC,29BD0) | NUL ASCII `/c ` | 33CD tvorba adresy, odovzdanie 2366 v 33D2 |
| 24C0 | [29BD0,29BD2) | mutable WORD, initial 0 | WORD zero-test 3261 |
| 24C2 | [29BD2,29BD4) | mutable WORD hlava exec záznamu | zápis AX 34C9, BX=24C2 pred INT21 v 3559 |
| 24C4 | [29BD4,29BD8) | mutable FAR pointer, initial 0:0 | offset AX 34CF a segment DS 34D2 |
| 24C8 | [29BD8,29BDC) | mutable FAR pointer, initial 0000:24D0 | segment DS 34D6, target DI=24D0 v 34E5 |
| 24CC | [29BDC,29BE0) | mutable FAR pointer, initial 0000:24E0 | segment DS 34DA, target DI=24E0 v 34F0 |
| 24F0 | [29C00,29C08) | NUL ASCII `COMSPEC` | 35BF/35C3 → environment lookup 248A |
| 24F8 | [29C08,29C0D) | NUL ASCII `.bat` | pointer table + 36BB/3744 |
| 24FD | [29C0D,29C12) | NUL ASCII `.exe` | pointer table + 3744 |
| 2502 | [29C12,29C17) | NUL ASCII `.com` | pointer table + 3744 |
| 2508 | [29C18,29C1E) | 3 NEAR WORD pointery 24F8,24FD,2502 | index 2→0 a zdvojenie v 372E..3744 |
| 250E | [29C1E,29C23) | NUL ASCII `PATH` | 37F7/37FB → lookup 248A |
| 2513 | [29C23,29C25) | BYTE 5Ch, NUL | 384E/3853 → string helper 2326 |
| 2516 | [29C26,29C2E) | NUL ASCII `COMSPEC` | 38EC/38F0 → lookup 248A |
| 251E | [29C2E,29C31) | NUL ASCII `/c` | 3918 vloží near pointer do SS argv-like záznamu |
| 2521 | [29C31,29C3D) | NUL ASCII `command.com` | 3966..3970 fallback volanie 378C |
| 252E | [29C3E,29C42) | mutable FAR callback, initial 0:0 | OR oboch WORD a FAR CALL [252E] v 3CEE..3D03 |

Počiatočné segmentové polovice troch FAR polí sú nuly, ale pred použitím sa explicitne prepíšu DS. Near cieľ 24D0/24E0 je skutočný uložený offset; nejde o odvodenie pointera z ľubovoľnej malej konštanty. Záznam [24C2,24D0) má presne WORD+tri FAR polia, teda 14 B. Jeho úloha pri exec sa opiera o BX a INT21 AH4B v tom istom kontexte; kompletný DOS ABI a výsledky procesu sa neuzatvárajú.

## Tabuľka prípon a fallback

V 372E sa SS lokálny index nastaví na 2, pri opakovaní sa zníži a pri signed <0 sa končí. 3742 index zdvojnásobí, 3744 načíta WORD [2508+2×index]. Preto doložená nominálna tabuľka obsahuje presne tri položky a táto lokálna cesta ich skúša v poradí `.com`, `.exe`, `.bat`. Inde 36BB používa prvú položku priamo. Úplné rozhodovanie pred týmto cyklom, správanie pri existujúcich príponách a prirodzený process launch zostávajú otvorené.

Dva `COMSPEC` texty majú odlišné konzumenty a zachovávajú sa ako dve samostatné polia. Pri system-like ceste sa `/c` vkladá do lokálneho pointerového zoznamu spolu s argumentom; pri fallback sa nastaví názov `command.com` a volá 378C. Nepredstiera sa tým uzavretie argument escaping, quote pravidiel alebo všetkých error vetiev.

Alokačný callback [252E] je v inom CRT kontexte: po neúspešných interných operáciách sa OR-testujú obe polovice pointera, volá sa s WORD požiadavkou a nenulový AX spôsobí opakovanie. Označenie retry vychádza z tohto lokálneho riadenia. Handler telo a úplný alokátor nie sú vykonané ani uzavreté.

## Čo zámerne zostáva otvorené

[29BE0,29C00) obsahuje dve susedné výstupné oblasti adresované DI=24D0/24E0 pri INT21 AX2901. Samotný odstup 16 B nie je dôkaz maximálneho rozsahu OS zápisu; preto sa ich 32 B v tejto dávke nepromuje. Nulové BYTE na 29C17,29C25,29C3D sa neoznačujú za padding bez referenčného dôkazu. WORD DS:2532 sa tu tiež netypuje. Žiadny externý program, shell alebo DOS OS call nebol spustený.

## Meranie

Presne **83 B CLASSIFIED ONLY → PARTIAL**. Mapa: **55189 B PARTIAL, 2062 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 750 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `86ccb1232246fabef0cf4208aa4695fa35c4f574c5dccfb6f3b48d5940dc77fa`. Partition integrita nie je dôkaz sémantickej úplnosti.

Katalóg má 84 funkčných rozsahov, 2970 inštrukcií / 7433 B, 56075 B typovaných dát celého obrazu; 55187 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Nové replay prípady 0; súčet zostáva 612553 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé percentá orientačné. 169 lokálnych dekódovaní nie je úplný function/CFG audit.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | exec záznamová forma | OS zápisové hranice | FCB výstupy |
| Dátové typy a konštanty | 95 % | N/A | 83 B / 17 polí | 32 B výstupov a nulové susedstvá | parser hranice |
| Tabuľky a ukazovatele | 93 % | N/A | 3 near prípony, 3 FAR parametre, retry callback | callback telo | writer ledger |
| Funkcie / ASM / CFG | 90 % | N/A | 169 inštrukcií lokálne overených | úplný spawn CFG | 35A6/378C |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | CRT spawn oddelený | prirodzené callery | caller graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | CRT procesové dáta oddelené | herné použitie | call ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | runtime parity | Win CRT dáta |

## Runtime testy na vykonanie

V izolovanom diagnostickom prostredí zachytiť záznam pred exec, skutočné INT21 AX2901 write rozsahy a startup DS. Najprv preukázať prirodzeného callera; prítomnosť linked CRT kódu neznamená, že hra spúšťa shell. Alokačný retry sledovať osobitne od spawn vetiev. Testy neprenášať na hostiteľský shell. DOSBox-X vykonanie zostáva otvorené.
