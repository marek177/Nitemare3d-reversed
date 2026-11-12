# Doplnkové overenie inicializácie správcu zvuku

Predchádzajúca dávka rekonštruovala celý CFG 0C2B:00DC, ale kontrolovane vykonala len modes 1/2 a neplatné modes. Táto dávka dopĺňa **13122 prípadov mode 0**. Presná mapa NON-CODE ani statusy sa nemenia; nové dôkazy prehlbujú existujúcu klasifikáciu PARTIAL. Pôvodné WORX závislosti a prirodzený lifecycle zostávajú otvorené.

## Vstupy a rozsah

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inštrukčný inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Nezmenený funkčný rozsah [0C38C,0C51A), 394 B / 127 CFG inštrukcií. Aktívne stavy DS:17CD/17CE/17CF sú v [28EDD,28EE0); požiadavky M/S/X sú DS:414D/414E/414F. DS kontext sa v modeli nastavuje explicitne; prirodzené DS/SS a interrupt okolnosti nie sú potvrdené.

## Potvrdená vetva mode 0

```text
if BYTE[3CC6] == 0:
    M = S = X = 0
    return  // active A/D/B sa nemenia
call 0C2B:0006
A = 1
probe = signed16(call 0C2B:0020)
capability = low8(call 10BF:06AA)
call 10BF:05E2
WORD[367A] = call 10BF:0646
WORD[367C] = call 10BF:0678
B = 1
if capability == 0: M = 0
if probe <= 0: BYTE[3CC7] = 0
D = 1 if S != 0 and BYTE[3CC7] != 0 else 0
if D == 0: call 10BF:070E
if capability != 0: call 0C2B:0298(0)
if M != 0: call 0C2B:00AA
return
```

Poradie je významné: backend init/gettery prebehnú pri povolenej inicializácii nezávisle od vstupného M/S/X a capability. Capability nenulové vyvolá resource 0 aj pri M=0. Kladný probe s pôvodným 3CC7=0 tento flag neobnovuje; flag sa v tomto tele pri probe<=0 iba nuluje. D sa prepočíta na 0/1; A/B sa nastavia na 1. Naopak pri 3CC6=0 A/D/B zostávajú vrátane seedovaných nenulových hodnôt.

Toto je správanie vlastného managera pri kontrolovaných návratoch závislostí. Hooky init/resource/backend môžu v skutočnej hre vykonať ďalšie zápisy, ktoré táto skúška zámerne nemodeluje. Výsledok sa nepovažuje za uzavreté WORX ABI ani skutočnú dostupnosť zariadenia.

## Reprodukcia a kontrola

Rozšírený `audit_replay_pass1_audio_state.py IMAGE INVENTORY DECODER EMULATOR OUT` teraz pokrýva modes 0/1/2 aj neplatné modes. Naďalej kontroluje image/inventory SHA, rekonštruuje pôvodný CFG a aplikuje reálne EXEPACK relokácie pri load segmentoch 0/1000h. Doplnený capability hook je na 10BF:06AA, image 1129A; vracia 0/1/255. Probe vracia −1/0/1. Dvanásť závislostí je mockovaných; originálny manager sa vykonáva bez náhrady. Žiadne DOSBox-X ani pôvodné audio driver testy sa nevykonali.

Mode 0: **2 load bázy × 27 kombinácií M/S/X × 3 počiatočné A/D/B (000,111,FFFFFF) × 3 enable hodnoty × 3 hodnoty 3CC7 × 3 probe výsledky × 3 capability výsledky = 13122 prípadov**. Enable a 3CC7 sú 0/1/255. Presne sa kontrolujú výsledné M/S/X, A/D/B, 3CC7, zachovanie enable, oba getter outputs, poradie volaní, resource argument 0 a návrat DS/BP/SI/SP.

Spolu s pôvodnými 10212 prípadmi je aktuálny súbor **23334 prípadov, 0 odchýlok**. Súčet kampane sa zvyšuje iba o 13122 na **523233**, nie o celý opakovaný beh. Starý summary/cases sú zachované ako `summary_before_mode_zero.json` a `cases_before_mode_zero.csv`; aktuálny `cases.csv` SHA-256 `eb6950ca8d574dbbcedae40a51bd334e2d1eb0b48f55e938449ba15cbc036f75`. Bez nových inštrukčných bajtov či dátových bajtov; funkcia sa do katalógu započítava raz.

Mapa zostáva **55071 B PARTIAL, 2180 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57295 B, 712 intervalov. Jej SHA-256 `1cece8eb421492091d9dd86178d5a4dc8b45883e48968f2cc43a28297eb600a5`. Posledná partition kontrola platí pre identický súbor; táto dávka mapu nemení. Katalóg zostáva 76 funkčných rozsahov, 2726 inštrukcií / 6831 B, 55957 B typovaných dát celého obrazu; 55069 B typovaných historických NON-CODE a 2 PARTIAL netypované relokačné bajty. Osobitne sa vedie 65548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; staršie percentá sú orientačné. Replay počty nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | mode 0 writeri troch stavov | alias writeri | write ledger |
| Tabuľky a ukazovatele | 93 % | N/A | getter outputs v inicializácii | pôvodné getter ABI | WORX gettery |
| Funkcie / ASM / CFG | 90 % | N/A | mode 0 kontrolovane vykonaný | pôvodné init dependencies | 0C2B:0006 |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO stopa |
| Scheduler | 96 % | N/A | init príznak 3CC7 môže byť vynulovaný | timing / IRQ | WORX interrupt graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | prirodzené prepínače | settings trace |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | sound callee | 10BF:0EF1 |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | audio init reset oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | init parity | Win lifecycle match |

## Runtime testy na vykonanie

Pri pôvodnom štarte zachytiť enable 3CC6, 3CC7, probe/capability výsledky a skutočné vedľajšie zápisy všetkých dependency tiel. Overiť resource 0 pri vypnutej hudbe, dostupnosť DSP a opätovnú inicializáciu po zlyhaní detekcie. Sledovať DS/SS a prerušenia v audio driveroch; následne porovnať Win16 lifecycle. Výsledky seedovaných testov nezamieňať za prirodzené dosiahnuté stavy.
