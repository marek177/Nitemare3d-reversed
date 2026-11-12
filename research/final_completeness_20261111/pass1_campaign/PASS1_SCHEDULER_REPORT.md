# PASS1: riadiace telo schedulera a tri DWORD stavy

Dávka typuje 12 B historického NON-CODE a rekonštruuje celé riadiace telo 0BDE:03C8. Úroveň PARTIAL: všetkých 15 závislostí je v replayoch mockovaných. Skutočné časovanie, aktualizácie sveta, VGA a prirodzené DEMO správanie zostávajú otvorené.

## Hranice a typy

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript pripína identity, porovnáva pôvodné bajty a nezávisle rekonštruuje CFG.

Funkcia **[0C1A8,0C2B6)** má **270 B / 92 inštrukcií**, ENTER 8, bez explicitných argumentov, FAR RETF. BP a lokálny stack sa obnovia. DS/BP/SP sa v modeli overujú, pracovné registre a príznaky sa nepovažujú za všeobecne zachované. Lokálne podmienené skoky tvoria rozhodovanie; v tele nie je jump table ani slučka dobiehajúca termíny.

| Pole pri DS=2771h | Image interval | Typ / initial | Dôkaz |
|---|---|---|---|
| DS:1734 | [28E44,28E48) | mutable DWORD / 0, posledný sample | DWORD zápis 04A2 a odčítanie 04AA; zápis DX:AX po fallback sample |
| DS:1738 | [28E48,28E4C) | mutable DWORD / 0, next bucket8 | unsigned high/low porovnanie s výsledkom 00D4; DWORD zápis counter+1 |
| DS:173C | [28E4C,28E50) | mutable DWORD / 0, next configured bucket | unsigned high/low porovnanie s výsledkom 0114; DWORD zápis counter+1 |

Sú to skaláre, nie segment:offset ukazovatele. Priame DWORD operandy a dvojice unsigned porovnaní stanovujú presné šírky. Predchádzajúci BYTE DS:1733 zostáva touto dávkou netypovaný. Všetci alias writeri ani startup/reset invarianty sa neuzatvárajú.

## Rekonštruovaný algoritmus

```text
T0 = cached_clock_0094()
R0 = sample_clock_0018()
C8 = bucket_00D4(T0); DWORD[3672] = C8
if DWORD[1738] <= C8:                       // unsigned DWORD
    if WORD[3CD6] == 0: tick_action_0370(C8)
    DWORD[1738] = (DWORD[3672] + 1) & FFFFFFFF

CF = bucket_0114(T0); DWORD[3676] = CF
if DWORD[173C] <= CF:
    if WORD[3CD6] != 0 and (BYTE[4540] & 1):
        tick_action_0370(DWORD[3672])
    call 0BDE:02F8
    call 0BDE:0156
    call 083D:1CE8
    call 083D:1E66
    call 0000:0AEA
    call 07ED:0360
    T1 = cached_clock_0094()
    elapsed = (T1 - T0) & FFFFFFFF
    if elapsed < 65: call 0156:00A8           // synchronized page flip
    else: call 0156:008E                    // immediate page flip
    call 06B0:05D6
    DWORD[173C] = (DWORD[3676] + 1) & FFFFFFFF
    DWORD[1734] = R0

if ((R0 - DWORD[1734]) & FFFFFFFF) > 500:
    call 0BDE:0004(1)
    call 0BDE:0004(0)
    DWORD[1734] = sample_clock_0018()
return
```

Názvy tick_action a update skupín sú pracovné; ich kompletná gameplay interpretácia nie je súčasťou tejto dávky. Vetva 3CD6 je presne nula/nenula, nie všeobecné pomenovanie konkrétneho DEMO režimu. Parita sa testuje pred volaním 0156 a z najnižšieho BYTE 4540.

Obe deadline podmienky sú unsigned a zahŕňajú rovnosť. Po vykonaní nastavujú next na práve uložené počítadlo+1 s modulo pretečením. Neexistuje lokálna slučka, ktorá by dobiehala všetky preskočené termíny. Callee však môžu meniť globálne 3672/3676; pseudokód preto pri finálnych zápisoch zachováva skutočné opätovné načítanie globálu.

Voľba page flipu testuje high WORD rozdielu a low WORD <0041h, čo je presne unsigned DWORD elapsed<65. Pokles T1 pod T0 sa vyhodnotí modulo, nie signed záporným časom. Watchdog podobne používa unsigned DWORD rozdiel >500. Po dokončení update vetvy sa 1734 prepíše na R0, takže za predpokladu nemeniacich callee je následný rozdiel nula.

## Reprodukcia a obmedzenia

`audit_replay_pass1_scheduler.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára `game_scheduler.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Presné adresy všetkých 15 mockovaných cieľov sú v summary. Clock a bucket hooky poskytujú seedované DX:AX, ďalšie hooky zaznamenávajú volania bez globálnych vedľajších účinkov. Kontrolujú sa DWORD argumenty oboch bucketov a tick_action, poll WORD argumenty v poradí 1,0 a celý trace.

**5760 prípadov, 0 odchýlok** = 2 load bázy × 5 counter hodnôt × 3 relatívne deadline8 stavy × 3 deadline-config stavy × 2 hodnoty 3CD6 × 2 parity × 4 frame rozdiely × 4 watchdog rozdiely. Counter je 0/1/FFFF/10000/FFFFFFFF. Deadline hodnoty sú counter−1/counter/counter+1 modulo. Frame rozdiely 0/64/65/FFFFFFFF, watchdog 0/500/501/FFFFFFFF. Oba bucket hooky v tejto matici vracajú rovnaký counter; nezávislé nerovnaké hodnoty oboch counterov a mutácie globálov v callees zostávajú netestované. Overuje sa päť výsledných DWORD, trace, poll args a DS/BP/SP. SHA cases `d2c26302ec46ab4576aa17814b21107906001ebd7b6be49fca2f1e8eb2da7d84`.

Presne 12 B CLASSIFIED ONLY → PARTIAL. Mapa: **55096 B PARTIAL, 2155 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 725 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `e2f2c306704505dcbf9dbf5a483b2e5b9a01ba45b18b016ebfd36cbb57ebe59b`. Partition integrita nie je dôkaz celej sémantiky.

Katalóg: 81 funkčných rozsahov, 2910 inštrukcií / 7309 B, 55982 B typovaných dát celého obrazu; 55094 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay 546513 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé hodnoty sú orientačné. Testové počty nie sú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 12 B / 3 DWORD | alias writeri | reset ledger |
| Tabuľky a ukazovatele | 93 % | N/A | deadline/sample skaláre | susedný 1733 | presné referencie |
| Funkcie / ASM / CFG | 90 % | N/A | 270 B / 92 inštrukcií | callee účinky | 02F8/0370 |
| RNG | 97 % | N/A | bez nového RNG dôkazu | ordering | trace call poradia |
| Scheduler | 96 % | N/A | deadline, 65/500 hranice a update poradie | prirodzené timing | natívne prepojenie |
| DEMO a vstupy | 96 % | N/A | 3CD6/parita riadia tick_action | význam režimu | 3CD6 writeri |
| Renderer / VGA | 94 % | N/A | sync/immediate voľba podľa elapsed | viditeľný frame | runtime CRTC trace |
| GUARD / bossovia | 93 % | N/A | update call poradie | AI callee semantika | callee closure |
| Zbrane / projektily | 92 % | N/A | input po page flip | reálne účinky | action trace |
| Sprity / HUD / paleta | 92 % | N/A | update call poradie | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable scheduler stav oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | scheduler parity | Win timer match |

## Runtime testy na vykonanie

Zachytiť oba clock výsledky, countery/deadlines a 3CD6/4540 pri bežnom behu, pauze, DEMO a pomalom frame. Korelovať elapsed s voleným flipom a skutočným VGA výstupom. Overiť callee zápisy do 3672/3676/1734 a prirodzené vykonanie watchdog vetvy. Pri LOAD/NEW GAME kontrolovať reset všetkých troch DWORD. DOSBox-X vykonanie a Win16 časová parity zostávajú otvorené.
