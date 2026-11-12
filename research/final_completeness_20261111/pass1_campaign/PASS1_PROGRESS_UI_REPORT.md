# PASS1: UI zdroje, texty a ukazovateľ priebehu

Dávka typuje celý zostávajúci interval [29376,293AD), 55 B, a rekonštruuje dve FAR funkcie. Úroveň PARTIAL: selector a progress telo sú kontrolovane vykonané, ďalší konzumenti len staticky doložení; query a kreslenie sú nahradené hookmi. Prirodzený loader a zobrazený výsledok zostávajú otvorené.

## Vstupy a hranice

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript kontroluje identity, presné dáta a inštrukčné bajty, nezávisle dekóduje CFG. Kanonické DS=2771h je explicitná podmienka modelu.

| Pole | Image interval, koniec exclusive | Typ / obsah | Dôkaz CS 0D29 |
|---|---|---|---|
| DS:1C66 | [29376,2937C) | 3 WORD: 5,7,8 | 0008 indexed WORD, predtým index×2 |
| DS:1C6C | [2937C,2937F) | 3 mutable BYTE initial 0 | 0179/0181 test a zápis indexed flag; tri nominálne resource skupiny |
| DS:1C6F | [2937F,2938B) | NUL ASCII `Press a key` | 0480 FAR text argument pre 0116 |
| DS:1C7B | [2938B,29397) | druhý samostatný NUL text | 04D0, iný caller scenár |
| DS:1C87 | [29397,293A3) | NUL filename `dstopen.img` | 079A/079D odovzdanie 0277:1600 |
| DS:1C93 | [293A3,293A8) | 5 BYTE: 0,0,40,80,100 | 08C7,08E2,0905 interpolácia |
| DS:1C98 | [293A8,293AA) | mutable WORD initial 0 | aktuálna dĺžka 0922/093C |
| DS:1C9A | [293AA,293AC) | mutable WORD initial 0 | redraw cache 0925/0952 |
| DS:1C9C | [293AC,293AD) | mutable BYTE initial 1 | testy 095D/0968 a nulovanie 0975 |

Žiadny bajt v tomto intervale sa neoznačuje ako padding. Trojprvkové selector/flag extenty sú nominálne podľa troch resource skupín a susedných polí; telá lokálne nekontrolujú ich index. Prirodzené globálne bounds a všetci alias writeri zostávajú otvorení.

| Funkcia | Image interval | CFG |
|---|---|---:|
| 0D29:0000 resource selector | [0D290,0D29E) | 14 B / 7 inštrukcií |
| 0D29:08AA progress | [0DB3A,0DBE9) | 175 B / 69 inštrukcií |

Spolu 189 B / 76 inštrukcií. Obe vracajú FAR, caller odstraňuje argumenty. Selector prijíma WORD index a vracia WORD [1C66+2×index] bez guardu. Progress prijíma WORD stage, signed WORD current a signed WORD total. BP/SI/DI/DS/SP sú v progress replayoch overené; pracovné registre a flags sa nepovažujú za zachované.

## Algoritmus progress

```text
points = BYTE[0,0,40,80,100]
if stage == 0:
    query(00010006h)
    draw_raw_WORDs(110,160,102,20,query_AX,1)
    return  // current/previous cache nemení
start = zero_extend(points[stage])
finish = zero_extend(points[stage+1])
WORD[3C90] = start + 111
n = signed_max(total,2)
v = trunc_toward_zero(((finish-start) * signed16(current)) / (n-1))
WORD[1C98] = low16(v)
if WORD[1C98] != WORD[1C9A]:
    query(0001000Eh)
    draw_raw_WORDs(WORD[3C90],161,WORD[1C98],18,query_AX,1)
WORD[1C9A] = WORD[1C98]
return
```

Päť endpoint BYTE podporuje špeciálny stage 0 a nominálne etapy 1..3: 0→40, 40→80, 80→100. Telo však neobmedzuje stage; mimo nominálnej domény môže čítať susedné dáta. Progress násobí signed current, delí signed 32-bitovým IDIV a ukladá len low WORD. Nulové/záporné total sa upraví na 2, current sa neclampuje. Záporný alebo priveľký current môže vytvoriť WORD mimo bežnej kresliacej dĺžky. To sú syntetické aritmetické výsledky, nie potvrdené prirodzené grafické chyby.

Query sa volá s DWORD, ale caller odstráni iba spodný WORD pred skladaním draw argumentov; zostávajúci horný WORD 1 sa stane šiestym raw argumentom. Replay kontroluje všetkých šesť WORD v poradí na FAR vstupe, nie len AX alebo počet kreslení. Konkrétne renderer parametre sa bez vykonania jeho tela nepreinterpretujú nad tento raw layout.

## Ostatní konzumenti

0170..0181 číta low BYTE skupiny, uloží ho do 368E, testuje príslušný loaded flag a pri nule ho nastaví pred resource volaním. Násobenie skupiny 1200 zodpovedá staršiemu doloženému trojbloku grafických dát. Celý loader/retry a možná zmena flagov na chybe nie sú replayované.

Dva texty `Press a key` majú rôzne konzumenty; oba sa odovzdávajú s DS segmentom ako FAR text. Filename má konkrétny loader call, ale asset `dstopen.img` sa v tejto dávke neotvára ani neidentifikuje jeho obraz. Initial flag 1C9C sa používa pri 095A: pri nule sa volá 080E, pri nenule sa nastaví epizóda 626A na 0, potom sa flag vždy nuluje. Celá táto funkcia sa tu nevykonáva.

## Reprodukcia a meranie

`audit_replay_pass1_progress_ui.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára dve ASM CSV, `static_contexts.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Pôvodné selector/progress telá sa nenahrádzajú. Mockované sú iba 0277:0188 query (AX=42h) a 0156:08D4 kreslenie (záznam raw argumentov).

**1302 prípadov, 0 odchýlok**: 6 nominal selector volaní a 1296 progress volaní (2 load bázy × stages0..3 × 9 signed current × 9 signed total × redraw/cache-hit scenár). Hodnoty current −32768,−1,0,1,2,49,99,100,32767; total −32768,−1,0,1,2,3,50,100,32767. Overujú sa query argumenty, draw argumenty, cache presné WORD a návratové registre/stack. Nie je to exhaustívna všetkých vstupov/stavov doména. SHA cases `8d5e55334410b0d956a52d8bd4e208112b7818d9a1b10ddf4954bcccdfccbf35`.

Presne **55 B CLASSIFIED ONLY → PARTIAL**. Mapa: **55244 B PARTIAL, 2007 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 758 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `0c9e2ae4b1c66d4f66fb050a78c4a9d0e16613370c589e75948f074330abffa0`. Partition integrita sama nedokazuje sémantickú úplnosť.

Katalóg: 86 funkčných rozsahov, 3046 inštrukcií / 7622 B, 56130 B typovaných dát celého obrazu; 55242 B historických NON-CODE dát a 2 netypované PARTIAL relokačné bajty. Controlled replay 613855 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé percentá orientačné. Replay počty nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | filename konkrétne spotrebovaný | formát assetu | otvorenie asset dát |
| Dátové typy a konštanty | 95 % | N/A | 55 B / 9 polí | globálne bounds/writeri | caller domény |
| Tabuľky a ukazovatele | 93 % | N/A | 3 WORD a 5 endpoint BYTE | neplatné indexy | stage producer |
| Funkcie / ASM / CFG | 90 % | N/A | 189 B / 76 inštrukcií | širší loader | 016A closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | bez nového dôkazu | časovanie | loop trace |
| DEMO a vstupy | 96 % | N/A | dva konkrétne key prompty | prirodzené scenáre | prompt caller trace |
| Renderer / VGA | 94 % | N/A | raw draw ABI a cache | skutočné kreslenie | 0156:08D4 |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | progress aritmetika 40/40/20 | asset identity | resource query |
| SAVE / LOAD | 92 % | N/A | initial epizódový flag oddelený | reset pri LOAD | writer ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | progress parity | Win UI match |

## Runtime testy na vykonanie

Zachytiť prirodzené stage/current/total pri načítaní a overiť nominálnu doménu. Porovnať raw draw argumenty s výsledným obrazom a redraw cache medzi etapami. Overiť loaded flag pri chybe resource čítania a význam startup 1C9C. DOSBox-X vykonanie a Win16 behaviorálna parity zostávajú otvorené.
