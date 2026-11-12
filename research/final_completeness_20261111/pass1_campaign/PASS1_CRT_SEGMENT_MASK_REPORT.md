# PASS1: CRT segment PSP kontextu a maskový helper

Dávka typuje 4 B a rekonštruuje 17-bajtovú NEAR rutinu. Úroveň PARTIAL. Maskové telo sa vykonáva pôvodné; segmentové startup konzumenty sa overujú staticky. Pôvodný DOS startup, PSP vytvorenie ani memory resize sa nevykonávajú.

## Presné adresy a dôkazy

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí obe identity, pôvodné bajty a nezávislé dekódovanie. Mapovanie dát predpokladá DS=2771h.

| Položka | Image interval, koniec exclusive | Typ / dôkaz |
|---|---|---|
| DS:211A | [2982A,2982C) | WORD initial 0; zdroj NOT/AND transformácie v 11EE:1E03 |
| DS:211E | [2982E,29830) | segmentový WORD initial 0; MOV ES/MOV DS a PSP-like konzumenti |
| Funkcia 11EE:1E03..1E14 | [13CE3,13CF4) | 17 B / 8 inštrukcií, NEAR RET |

Susedný WORD DS:211C sa nepretypuje bez konzumenta. Pole 211A sa nenazýva DOS errno len podľa susedstva s 2118; jeho konkrétny doložený účel v tejto dávke je maska. Všetci writeri a úplná významová doména ostávajú otvorené.

## Segmentové pole

11EE:0141/016A načítajú DS:211E do ES a čítajú ES:002C pre environment segment. 034F načíta toto pole do DS, nastaví SI=0081h a následne číta command-tail-like bajty. Ďalšie konzumenty sú v startup 0320/04A0 a memory-resize kontexte 229E, kde sa segment používa pri výpočte a v ES pred INT21/AH4A.

Tieto nezávislé segmentové operandy a offsetové kontexty podporujú PSP-context rolu, nie všeobecný integer či FAR pointer. Presný pôvod hodnoty pri startup, všetky verzie DOS a prirodzené DS/SS prechody sa touto statickou dávkou neuzatvárajú. Nevykonáva sa žiadny INT21 z uvedených kontextov. `instruction_contexts.csv` zachováva konkrétne bajty a operandové adresy.

## Maskový algoritmus a ABI

```text
input: CX = incoming WORD mask
AX = (~WORD DS:[211A]) & CX
CX = 0
if (AL & 80h) == 0: CL |= 1
return NEAR
```

AX je plná 16-bitová transformovaná hodnota; CX je potom presne 0 alebo 1 podľa bitu 80h výsledku. Horné bity vstupného CX sa môžu objaviť v AX, ale neovplyvnia tento jedno-bitový test. Vrutine nie je zásobníkový argument ani FAR return. Používa pracovné AX/CX/flags; DS ostáva zachované a finálny SP je vstupný SP+2. Konkrétny vyšší význam bitu 80h pri open/file flags zostáva na caller/writer closure.

## Reprodukcia a výsledky

`audit_replay_pass1_crt_segment_mask.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára ASM CSV, data fields, statické kontexty, cases a summary. Pôvodný helper neobsahuje callee, segmentové relokačné operands ani I/O; DS a CX sa seedujú pri load segmentoch 0/1000h. Žiadne telo sa nemockuje a žiadne OS volanie sa nevykonáva.

**65640 prípadov, 0 odchýlok**: všetkých 65536 WORD hodnôt DS:211A pri CX=0080h na load 0; 48 dodatočných kombinácií ôsmich hraničných mask hodnôt a šiestich iných CX; 56 kombinácií na load 1000h. Duplicitných osem CX=80h boundary dvojíc sa pri load0 odfiltruje. Kontroluje sa AX, CX, DS a SP. Nie je to exhaustívny súčin všetkých 2^32 mask/input dvojíc. SHA cases `e68ff0a400265c6eef9ee3f18406aba056906eda940d6d4fc2186325b7362b18`.

## Meranie

4 B CLASSIFIED ONLY → PARTIAL. Mapa: **56805 B PARTIAL, 446 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 844 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `29c830b05a5a476d3239bc176716e315f7030c4384714459f093a5a13d49e14c`. Integrita mapy sama nepreukazuje sémantickú úplnosť.

Katalóg: 95 funkčných rozsahov, 3364 inštrukcií / 8466 B, 57691 B typovaných dát celého obrazu; 56803 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay 776167 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Exhaustívna jedna os vstupu nie je úplný audit CRT ani startup.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | PSP-like offsetové kontexty | prirodzený DOS block | startup trace |
| Dátové typy a konštanty | 95 % | N/A | 4 B / 2 WORD | susedný 211C | reader/writer audit |
| Tabuľky a ukazovatele | 93 % | N/A | segment odlíšený od pointera | inicializácia211E | startup writer |
| Funkcie / ASM / CFG | 90 % | N/A | 17 B / 8 inštrukcií | caller význam bitu | 1E03 call graph |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | runtime/OS stav oddelený | prirodzené callery | trace |
| DEMO a vstupy | 96 % | N/A | command-tail konzument staticky | celý argv parser | startup closure |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | CRT maskový stav oddelený | fileflag význam | wrapper closure |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | CRT parity | Win helper match |

## Runtime testy na vykonanie

Zachytiť pôvodný zápis 211E a porovnať environment/command-tail konzumenty so skutočným DOS segmentom. Vystopovať writerov 211A, vstupný CX a caller interpretáciu CX po návrate. Memory resize sledovať oddelene bez predpokladu, že rovnaké segmentové pole znamená uzavreté OS ABI. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
