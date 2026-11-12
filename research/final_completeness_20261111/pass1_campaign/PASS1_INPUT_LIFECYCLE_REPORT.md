# PASS1: životný cyklus vstupov a história klávesu

Dávka typuje 4 B historického NON-CODE a rekonštruuje dve celé riadiace FAR funkcie. Úroveň PARTIAL: telá get/set vector a aux init/close sú mockované. Žiadny skutočný interrupt vector, ISR, ovládač alebo hostiteľské zariadenie sa nemení.

## Presné hranice

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overuje identity, pôvodné bajty a nezávisle dekóduje CFG. Kanonické DS=2771h je explicitná podmienka modelu.

| Pole | Image interval, koniec exclusive | Typ / dôkaz |
|---|---|---|
| DS:0B3E | [2824E,2824F) | mutable BYTE initial 0; active flag pre vector9 lifecycle |
| DS:0B3F | [2824F,28250) | mutable BYTE initial 0; aux initialized flag |
| DS:0B40 | [28250,28252) | mutable WORD initial 0; porovnanie so SI v 0348 a zápis SI v 037A |

Posledný WORD je v tejto dávke doložený staticky cez `key_history_context.csv`: po upstream 11EE:39B0(10h) sa porovná so SI, pri zmene sa pripraví runtime record a história aktualizuje. Celá funkcia, vstupná normalizácia a DEMO/file zápis sa nevykonávajú. Názov last-key je pracovná interpretácia kontextu, nie uzavreté celé vstupné ABI.

| Funkcia | Image interval | CFG |
|---|---|---:|
| 06B0:0134 IRQ9 lifecycle | [06C34,06C8C) | 86 B / 32 inštrukcií |
| 06B0:018C aux lifecycle | [06C8C,06CD0) | 66 B / 27 inštrukcií |

Obe majú WORD mode na SS:BP+6, FAR RETF, obnovia BP a lokálny stack. Každý span má 2 B mimo rekonštruovaného CFG, ktoré sa nepočítajú ako vykonané. Spolu 152 B / 59 inštrukcií. Pracovné AX/DX/flags nemajú všeobecnú zachovávaciu garanciu; DS/BP/SP sa kontrolujú.

## Algoritmus

```text
irq9(mode):
    if mode == 0 and BYTE[0B3E] == 0:
        DWORD[3F52] = get_vector(9)             // DX:AX
        set_vector(9, FAR(current_code_segment:0000))
        BYTE[0B3E] = 1
    else if mode == 1 and BYTE[0B3E] != 0:
        set_vector(9, DWORD[3F52])
        BYTE[0B3E] = 0
    return

aux(mode):
    if mode == 0:
        if BYTE[0B3F] == 0:
            result = call 0831:000E()
            BYTE[414C] = 0 if unsigned16(result) < 1 else 1
        BYTE[0B3F] = 1
    else if mode == 1:
        if BYTE[0B3F] != 0: call 0831:0028()
        BYTE[414C] = 0
        BYTE[0B3F] = 0
    return
```

IRQ9 mode 0 pri nenulovom starom flagu vracia bez normalizácie; napríklad 255 zostane 255. Aux mode 0 naopak vždy zapíše 1, aj keď call init preskočí. Probe FFFFh je v CMP unsigned nenulový výsledok, teda vytvorí dostupnosť 1; nevykladá sa automaticky ako signed zlyhanie. Pri probe=0 je initialized flag aj tak 1 a ďalší mode0 init neopakuje.

IRQ get/set wrappers sú 11EE:39E2/39F4. Model kontroluje vector argument 9 a presný FAR pointer, vrátane segmentovej EXEPACK relokácie pri druhej load báze. Pôvodný cieľ je 06B0:0000; tela ISR a wrapperov sa touto skúškou neuzatvárajú. DWORD[3F52] je BSS uložený pôvodný handler a nepridáva sa ako nový file-backed NON-CODE údaj.

## Reprodukcia a overenie

`audit_replay_pass1_input_lifecycle.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára dve ASM CSV, data fields, key history kontext, cases a summary. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Mockované sú iba get-vector, set-vector, aux init a aux close. Query vracia seedovaný FAR pointer, setter zaznamenáva raw argumenty; nič sa neinštaluje do skutočnej IVT.

**8192 prípadov, 0 odchýlok** = 2 load bázy × 256 starých BYTE hodnôt × 4 modes (0,1,2,FFFF) × (1 IRQ scenár + 3 aux probe výsledky 0/1/FFFF). Kontroluje sa presný trace, saved pointer, active flag, dostupnosť a DS/BP/SP. Neplatné modes nemenia stav. Seedované nenulové flags dokazujú konkrétne testy nula/nenula, nie prirodzenú dosiahnuteľnosť všetkých týchto stavov. SHA cases `d1c6ed86d265d4cdcb37c438edbd2eda3572eecae1efe90994ee1e8dab8c3f28`.

## Meranie

4 B CLASSIFIED ONLY → PARTIAL. Mapa: **56797 B PARTIAL, 454 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 840 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `b13c87d99a9dc9f68d0be9dd7521cdb20bceedadc63fd8ee7af4e1abb330a8d6`. Partition integrita sama nepreukazuje sémantickú úplnosť.

Katalóg: 93 funkčných rozsahov, 3313 inštrukcií / 8313 B, 57683 B typovaných dát celého obrazu; 56795 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay 705343 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Počty flags/replayov nie sú percentá úplnej vstupnej parity.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 4 B / 3 polia | alias writeri | lifecycle reset ledger |
| Tabuľky a ukazovatele | 93 % | N/A | vector9 FAR pointer argumenty | pôvodný ISR | 06B0:0000 |
| Funkcie / ASM / CFG | 90 % | N/A | 152 B / 59 inštrukcií | get/set/aux telá | driver closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | interrupt lifecycle oddelený | IF/IRQ časovanie | ISR trace |
| DEMO a vstupy | 96 % | N/A | dve lifecycle vetvy a last-key WORD | celý record zápis | key/DEMO loop |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | init režimu | VGA setup |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | input transform | action producer |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable input state oddelený | reset | LOAD writer ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | event lifecycle parity | Win input adapter |

## Runtime testy na vykonanie

Sledovať pôvodné get/set vector9 a uložený handler pri štarte/ukončení aj opakovanej inicializácii. Overiť aux init návratovú doménu, flag414C a zatváranie; následne analyzovať ISR a IF/IRQ kontext. Last-key WORD korelovať s prirodzeným klávesom a DEMO recordom. Pôvodné DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
