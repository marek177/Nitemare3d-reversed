# PASS1: stavové bajty vstupov menu

Táto dávka typuje 4 B historického NON-CODE a kontrolovane vykonáva dva vnútorné úseky menu. Výsledok je PARTIAL: vstupné ovládače, prirodzené domény a celý menu loop nie sú uzavreté. Prefixy sa nezapočítavajú ako nové celé funkcie.

## Vstupy a presné hranice

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Reprodukčný skript kontroluje tieto identity a pôvodné bajty každého štartu. Dekóduje dosiahnuteľné vetvy oboch obmedzených úsekov, nie lineárne medzery.

| Pole pri DS=2771h | Image interval | Skutočný typ / initial |
|---|---|---|
| DS:0B58 | [28268,28269) | mutable BYTE, história prvého aux vstupu / 0 |
| DS:0B59 | [28269,2826A) | mutable BYTE, druhý aux latch / 1 |
| DS:0B5A | [2826A,2826B) | mutable BYTE, história prvého mouse bitu / 0 |
| DS:0B5B | [2826B,2826C) | mutable BYTE, druhý mouse latch / 1 |

Typovanie stojí na presných BYTE čítaniach/zápisoch v uvedených úsekoch. Susedné 0B5C..0B5E sa touto dávkou nemenia. Názvy aux/mouse sú pracovné označenia podľa caller kontextu; prirodzené zariadenie ani celý driver ABI sa tu nevykonáva.

| Prefix, koniec exclusive | Image interval | CFG inštrukcie / B |
|---|---|---:|
| 06B0:042A..046D | [06F2A,06F6D) | 20 / 66 |
| 06B0:04B1..04F1 | [06FB1,06FF1) | 19 / 64 |

Spolu 130 B / 39 inštrukcií; prvý span má 67 B, jeden bajt mimo jeho CFG sa nepočíta. Prefixy nevolajú iné funkcie a replay končí pred uvedeným koncom, nie návratom z menu funkcie. SS:BP a lokálne vstupy sú explicitne seedované. DS/BP/SP sa nemenia; AX/flags sú pracovné.

## Rekonštruovaný algoritmus

Pre prvý prefix je `primary = BYTE[SS:BP−6] & 1`, `secondary = BYTE[SS:BP−6] & 2`. Pre druhý prefix je primary celé WORD[SS:BP−12h] a secondary celé WORD[SS:BP−10h]. Oba menia iba nízky BYTE key na SS:BP−4:

```text
if primary == 0 and previous_primary != 0: key = 0Dh
if secondary != 0 and previous_secondary == 0: key = 1Bh
previous_primary = low8(primary)
previous_secondary = 1 if secondary != 0 or key == 0Dh else 0
```

0Dh zodpovedá Enter, 1Bh Escape. Prvý event vzniká pri uvoľnení; druhý pri novom stlačení a môže prepísať práve vytvorený Enter. Druhý latch navyše môže zostať 1 kvôli key=Enter aj bez aktívneho secondary. Preto nejde iba o nezávislé kópie stavu tlačidiel.

Pri aux prefixe sa primary testuje ako WORD, ale ukladá sa len low BYTE. Syntetická hodnota 0100h je teda v tomto kroku aktívna, no uložená história je 0. Prirodzená návratová doména upstream ovládača sa musí overiť pred hodnotením tohto javu ako herného problému. Oba prefixy zapisujú iba nízky BYTE key; seedovaný horný BYTE ABh zostal v každom prípade nezmenený.

## Reprodukcia a pokrytie

`audit_replay_pass1_menu_latches.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára `instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Pôvodné prefixy sa vykonávajú bez mockov pri load bázach 0/1000h s reálnymi EXEPACK relokáciami. Nevykonávajú sa predchádzajúce driver calls, filtre pohybu ani opakovací menu loop.

**2160 prípadov, 0 odchýlok**: mouse 2×5 vstupných WORD×3×3 staré BYTE stavy×4 key hodnoty = 360; aux 2×5×5 vstupných WORD×3×3 staré stavy×4 key = 1800. Histórie sú 0/1/255, key 0/13/27/65; aux vstupy 0/1/255/256/FFFF. Kontrolujú sa oba nové BYTE stavy, presný WORD key a DS/BP/SP. Nie je to exhaustívna všetkých vstupov/state doména. SHA cases `660ccb314679303fe71c18b43c137cd978a9a0630692acbe45c0c67756054dd7`.

Počiatočný lineárny decode narazil na bajt mimo inventára a bol nahradený CFG dekódovaním. Predpoklad všetkých nulových počiatočných hodnôt bol odmietnutý kontrolou reálnych bajtov; konečné fields majú presne 0/1/0/1 a ich range SHA. Finálne počty pochádzajú z úspešného behu po týchto opravách.

Presne 4 B CLASSIFIED ONLY → PARTIAL. Aktuálna mapa: **55081 B PARTIAL, 2170 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 720 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `adee960e59347e83d0de01e77f4a5adf79d13d35e7e40870aca5bd1743c7e15f`. Integrita mapy nie je nezávislý dôkaz celej sémantiky.

Centrálny bounded katalóg zostáva 80 funkčných rozsahov, 2818 inštrukcií / 7039 B; tieto vnútorné prefixy sa tam ako celé funkcie nepridávajú. Typované dáta celého obrazu 55967 B, historického NON-CODE 55079 B a 2 netypované PARTIAL relokačné bajty. Controlled replay súčet 538193 plus osobitne 65548 smerových prefixových prípadov. Pôvodné runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Počty replayov ani intervalov nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 4 BYTE histórie/latches | alias writeri | reset ledger |
| Tabuľky a ukazovatele | 93 % | N/A | presné oddelenie polí | susedné 0B5C..5E | gameplay história |
| Funkcie / ASM / CFG | 90 % | N/A | 130 B / 39 prefixových inštrukcií | celý menu CFG | upstream driver |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO trace |
| Scheduler | 96 % | N/A | bez nového dôkazu | runtime timing | loop trace |
| DEMO a vstupy | 96 % | N/A | release Enter / press Escape | prirodzená input doména | driver výsledky |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | gameplay latch | 0B5D/0B5E |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | consumer dispatch |
| SAVE / LOAD | 92 % | N/A | menu mutable stav oddelený | reset pri LOAD | write ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | input parity | Win event adapter |

## Runtime testy na vykonanie

Zachytiť driver output WORD/BYTE pri stlačení, držaní a uvoľnení oboch vstupov, vrátane súbehu. Sledovať reset histórií pri otvorení menu a prechode medzi menu a hrou. Overiť prirodzenú aux WORD doménu a inicializáciu celého key WORD mimo týchto prefixov. DOSBox-X a Win16 behaviorálne porovnanie zostáva otvorené.
