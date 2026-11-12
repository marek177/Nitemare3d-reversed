# PASS1: tabuľka posunov susednej bunky

Nové dôkazy typujú 8 B historického NON-CODE ako signed BYTE pole používané štyrmi adresnými prefixmi. Výsledok je PARTIAL: prirodzená doména indexu, celé funkcie a bezpečnosť cieľovej pamäte nie sú uzavreté. Táto dávka nepridáva DEEP VERIFIED ani pôvodné runtime testy.

## Vstupy, dáta a hranice

Kanonický DOS 2.0 image má SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár inštrukcií SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Obe identity skript pripína a pre každý dekódovaný prefix kontroluje pôvodné inštrukčné bajty.

Pole DS:0822 pri kanonickom DS=2771h leží presne v **[27F32,27F3A)**. Bajty `C0 01 01 40 40 FF FF C0` majú signed hodnoty **−64, 1, 1, 64, 64, −1, −1, −64**. Hranicu ôsmich prvkov podporuje osem smerových slotov a už nezávisle rekonštruovaný producent DS:4158. Bezprostredný deviaty bajt DS:082A je samostatný mutable first-init príznak, pôvodne 1, potvrdený predchádzajúcou dávkou. Nejde o deviaty doložený prvok tabuľky.

| Index | Signed BYTE | Pripočítaný BYTE offset |
|---:|---:|---:|
| 0 | −64 | −128 |
| 1 | 1 | 2 |
| 2 | 1 | 2 |
| 3 | 64 | 128 |
| 4 | 64 | 128 |
| 5 | −1 | −2 |
| 6 | −1 | −2 |
| 7 | −64 | −128 |

V kontexte už doloženej 64×64 WORD mapy ide o posun o jednu bunku alebo jeden riadok, násobený dvomi bajtmi na bunku. Identita konkrétneho prirodzeného FAR base s hlavným mapovým bufferom však v tejto dávke nie je dokázaná pre všetky callery; preto sa samotný base nepretypováva. Duplicitné hodnoty zodpovedajú párom susedných smerových slotov, nejde o plnú dvojzložkovú tabuľku diagonálnych pohybov.

## Štyri adresné prefixy

| CS:IP rozsah (koniec exclusive) | Image rozsah | Inštrukcie / B | Base / výsledok |
|---|---|---:|---|
| 0000:070A..0723 | [0070A,00723) | 8 / 25 | DS:417C/417E → DX:AX a SS lokálne WORD |
| 0000:097F..098C | [0097F,0098C) | 5 / 13 | ES:DI → ES:AX |
| 083D:0D20..0D35 | [090F0,09105) | 7 / 21 | DS:417C/417E → ES:BX |
| 083D:2074..2087 | [0A444,0A457) | 6 / 19 | DS:417C/417E → DX:AX |

Spolu 78 B / 26 inštrukcií. Sú to vnútorné prefixy, nie štyri uzavreté funkcie. Nekopírujú sa do centrálneho počtu úplne ohraničených funkčných rozsahov. V týchto prefixoch nie je volanie ani vetvenie; replay končí presne pred ďalšou inštrukciou a nečíta výslednú cieľovú bunku.

```text
index = WORD DS:[4158]
value = signed8(BYTE DS:[(0822 + index) & FFFF])
offset = (base.offset + 2 * value) & FFFF
segment = base.segment
```

Všetky štyri sekvencie používajú CBW, teda znamienkové rozšírenie načítaného bajtu. Výsledné sčítanie je 16-bitové a segment nemení; prípadný carry neprenesie do segmentu. Napríklad base.offset=FFFF a value=1 poskytne offset=0001 s rovnakým segmentom. To je presný adresný výpočet, nie dôkaz platnosti výsledného ukazovateľa.

Žiadny zo štyroch prefixov nemá lokálny bounds check. Starší exhaustívny replay producenta DS:4158 ukázal, že jeho obmedzená jednorazová normalizácia nevytvára 0..7 pre všetky signed vstupy; táto dávka ho nevykonáva znovu a neuzatvára prirodzené vstupy. Index 8 v aktuálnom obraze číta DS:082A=1; po defaults rutine môže čítať 0. Z toho nemožno vyhlásiť prirodzený herný bug bez preukázania dosiahnuteľnosti indexu 8.

## Reprodukcia a pokrytie

`audit_replay_pass1_neighbor_offsets.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára `instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Používa pôvodné inštrukcie bez náhrad závislostí a aplikuje reálne EXEPACK relokácie pri load segmentoch 0/1000h.

**448 prípadov, 0 odchýlok** = 4 prefixy × 14 indexov × 4 base offsety × 2 load bázy. Indexy sú 0..8, 007F, 0080, 00FF, FFFE, FFFF; base offsety 0000,0001,7FFF,FFFF. Out-of-domain prípady sa explicitne označujú a očakávanie vychádza z načítaného okolitého bajtu, nie z predstieranej položky ôsmich prvkov. Overuje sa offset, zachovanie segmentu a DS/SP. ES alebo lokálne premenné sú pracovné výsledky podľa konkrétneho prefixu. Prirodzené callery, cieľové dereferencie, stack prology a epilogy týchto funkcií nie sú vykonané.

Presne 8 B prešlo CLASSIFIED ONLY → PARTIAL. Nová mapa: **55052 B PARTIAL, 2199 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 707 intervalov, ich SHA a presné členstvo bez dier či prekryvov; neoveruje sémantiku nezávislým runtime spôsobom. SHA mapy `a932501e33cc722001325e50133309486b6e779effdc4fb9dec682c1d7cb6de5`.

Centrálny bounded katalóg zostáva 73 funkčných rozsahov, 2565 inštrukcií / 6309 B; prefixových 78 B sa do týchto počtov nepripočítava. Typované dáta celého obrazu 55938 B, z historického NON-CODE 55050 B; 2 PARTIAL relokačné bajty zostávajú bez uzavretého typu. Controlled replay súčet 409575 zahŕňa aj túto explicitne obmedzenú dávku; osobitne zostáva 65548 prípadov smerového normalizačného prefixu. Prirodzené runtime testy 0. Posledná GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Nové sémantické % vyžaduje počet uzavretých jednotiek / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Predošlé hodnoty sú historické orientačné odhady. Bajtová integrita mapy ani 448 replay prípadov tento menovateľ nenahrádzajú.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | signed posun buniek ×2 | base identita v calleroch | vystopovať 417C |
| Dátové typy a konštanty | 95 % | N/A | 8 B signed pole | všetci writeri/indexy | aliases ledger |
| Tabuľky a ukazovatele | 93 % | N/A | štyri CBW konzumenty | bounds nie sú lokálne | prirodzený index |
| Funkcie / ASM / CFG | 90 % | N/A | 78 B / 26 prefixových inštrukcií | celé funkcie | uzavrieť 0704 CFG |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené call ordering | DEMO stopa |
| Scheduler | 96 % | N/A | bez nového časového dôkazu | režimový writer | 3CCF graph |
| DEMO a vstupy | 96 % | N/A | indexová závislosť od smeru | udržiavaná doména | zachytiť otočenia |
| Renderer / VGA | 94 % | N/A | bez nového render dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | susedná bunka pre interakciu | význam celých callerov | 083D:0D1A |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | persistencia stavu | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | tabuľka a konzumenti | Win cross-match |

## Runtime testy na vykonanie

Sledovať DS:4158 pred štyrmi konzumentmi a overiť 0..7 pri pohybe, otočení a DEMO. Zaznamenať prirodzené FAR base, výslednú bunku a mapové hranice; osobitne otočenia pri okraji mapy. Overiť, či niektorá prirodzená cesta po producentovi upravuje index alebo DS:0822..0829. Index 8 a záporné indexy skúšať iba ako oddelené diagnostické vstupy a nezamieňať ich s dosiahnutým stavom pôvodnej hry. DOSBox-X testy zatiaľ neboli vykonané.
