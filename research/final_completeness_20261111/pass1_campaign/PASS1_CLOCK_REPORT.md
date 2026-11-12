# PASS1: herné hodiny, uložený čas a prvotné nastavenia

Táto dávka pridáva dôkazmi podložené typovanie 9 B a rekonštrukciu troch DOS 2.0 funkcií. Výsledky sú PARTIAL. Neuzatvára prirodzený scheduler, CRT časový subsystém ani časovanie hardvéru. Win16 parity tejto dávky zatiaľ chýba.

## Vstupy a presné hranice

Kanonický rozbalený obraz: 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Inventár inštrukcií: SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript kontroluje pôvodné bajty každého rekonštruovaného štartu a nezávisle dekóduje CFG pomocou iced-x86 1.21.0.

Adresy sú kanonické image offsets; hranice sú polootvorené. DS mapovanie 2771h sa v replays nastavuje explicitne; samo osebe nedokazuje DS všetkých prirodzených callerov.

| Pole | Image interval | Typ a dôkaz |
|---|---|---|
| DS:081E | [27F2E,27F32) | DWORD, pôvodne 0; časový výsledok DX:AX zapísaný 0BDE:009F/00A2; DWORD porovnanie 0201:0417/041B s termínom objektu +8 |
| DS:082A | [27F3A,27F3B) | BYTE, pôvodne 1; 0476:0000 test a 002C nulovanie podmieňujú prvotné nastavenia |
| DS:16F2 | [28E02,28E06) | DWORD, pôvodne 0; BIOS tick origin čítaný a aktualizovaný v 0BDE:0018 |

DS:081E nie je FAR pointer: operácie s ním sú celočíselné porovnávanie a sčítanie termínu, zdrojom je časová rutina. Rozdelenie zápisu do dvoch WORD nepredstavuje dôkaz ukazovateľa. Pole DS:0822 a susedné neanalyzované bajty táto dávka netypuje. Časová nula sa používa ako sentinel a zároveň môže byť platným tickom; všetci writeri mimo explicitného inventára zostávajú otvorení.

| Funkcia | Image interval | CFG kód |
|---|---|---:|
| 0BDE:0018 sample | [0BDF8,0BE74) | 123 B / 37 inštrukcií |
| 0BDE:0094 cached | [0BE74,0BE8E) | 26 B / 9 inštrukcií |
| 0476:0000 defaults | [04760,047BE) | 94 B / 24 inštrukcií |

Spolu 243 B / 70 inštrukcií. Bajt na 0BDE:0093 je RETF; v rozsahu sample zostáva jeden nedosiahnutý bajt medzi vetvami mimo rekonštruovaného CFG. ASM CSV zachovávajú presné inštrukčné bajty. Vnútorné vetvy zostávajú v uvedených hraniciach. Sample volá FAR 11EE:2AEA; cached používa PUSH CS + NEAR CALL 0018 na FAR-return funkciu. Stack sa tým správa ako FAR volanie.

## Algoritmus a kontext

```text
sample():
    if BYTE[3CC7] == 0 and BYTE[3CCF] != 0:
        ES = 0040h
        ticks = WORD[ES:006C] | (WORD[ES:006E] << 16)
        if DWORD[16F2] == 0: DWORD[16F2] = ticks
        return low32((ticks - DWORD[16F2]) * 55)  // DX:AX
    FAR_CALL 11EE:2AEA(near_address_of_SS_local_14_bytes)
    return low32(DWORD[local+0] * 1000 + WORD[local+4])

cached():
    if BYTE[3CCF] == 0: DWORD[081E] = sample()
    return DWORD[081E]  // DX:AX
```

BIOS vetva je pri priamom sample dostupná pri nenulovom 3CCF; cez cached pri tom istom stave sa sample vôbec nevolá. Pravidelné osviežovanie uloženého času v tomto režime preto musí mať iného writera, prípadne ide o stav vyžadujúci ďalší kontext. Táto dávka taký writer neuzatvára. Názvy príznakov ako konkrétny audio backend sa z hodnoty samotnej nevyvodzujú.

Odčítanie a násobenie sú modulo 2^32. Inštrukcie čítajú BIOS DWORD ako dva WORD bez vlastnej ochrany proti prerušeniu; prirodzená atomicita a CPU interrupt kontext nie sú preukázané. Denný BIOS reset nie je v tomto tele špeciálne ošetrený. Faktor 55 je presný integer z ASM, nie dôkaz presnej frekvencie fyzických hodín.

Fallback má 14 B SS lokál, odovzdáva near adresu a spotrebuje prvých 6 B. CRT dependency sa prirodzene nevykonáva: replay hook zapíše sekundy 3 a zlomkovú WORD hodnotu 999 na SS lokál, výsledok je 3999. DS/SS predpoklady pôvodnej CRT rutiny, jej štruktúra nad prvými 6 B a jednotky v reálnom DOS prostredí zostávajú otvorené. ES je pracovný register; v BIOS vetve sa nastaví na 0040h a neobnovuje sa.

0476:0000 pri nenulovom DS:082A nastaví DWORD 3CCA=00070220h, BYTE 3CC6/3CC7/3CCE/3CCF=1, WORD 3CBC/3CBE/3CC0=FFFFh, vynuluje 082A/3CC8/3CD0/3CD6/3CDC a nastaví WORD 3CC2=25. Pri nulovom 082A tieto polia nemení. V oboch vetvách nastaví BYTE 3CD1=1, 3CD2=0, DWORD 3CD8=0 a WORD 3CC4=FFFFh. Toto je presný efekt tela, nie uzavretá interpretácia všetkých konfiguračných polí.

## Reprodukcia a výsledky

`audit_replay_pass1_clock.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` vytvorí tri ASM CSV, presné `data_fields.csv`, `direct_references.csv`, `cases.csv` a `summary.json`. Pri load bázach 0/1000h aplikuje reálne EXEPACK relokácie.

512 prípadov overuje všetkých 256 BYTE hodnôt first-init príznaku pri oboch load bázach. Ďalších 864 prípadov pokrýva priamy sample aj cached, 3CCF z {0,1,2,255}, 3CC7 z {0,1,2}, šesť BIOS tickov vrátane 0/FFFF/10000/FFFFFFFF a tri origin hodnoty. Overuje presný DX:AX, zmeny uloženého času a origin, počty mockovaných CRT volaní a návratové DS/BP/SP. Celkom **1376 prípadov, 0 odchýlok**. BIOS pamäť je seedovaná; CRT časový callee je jediná nahradená závislosť. Hodnoty nenulových príznakov sa v týchto telách nenormalizujú.

Skript `promote_pass1_fields.py` pridal presne 9 B z CLASSIFIED ONLY do PARTIAL. `verify_pass1_partition.py` overil 707 intervalov, ich SHA, presné členstvo pôvodných 57295 B, nulové prekryvy a chýbajúce bajty. Mapa má SHA-256 `795c20ffaefc873cf001d9c50f72a912b2af6448bc82991d08d94cc17c4fac24`.

Aktuálne: **55044 B PARTIAL, 2207 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Katalóg má 73 funkčných rozsahov, 2565 inštrukcií / 6309 B, 55930 B typovaných dát celého obrazu a 55042 B typovaných historických NON-CODE dát; zostávajú 2 PARTIAL netypované relokačné bajty. Controlled replay súčet 409127 plus samostatných 65548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: počet dôkazmi uzavretých jednotiek / úplný inventár oblasti. Úplné menovatele chýbajú, preto nové percentá N/A; predošlé čísla sú orientačné. Počet replay prípadov ani integrita mapy nenahrádzajú sémantické pokrytie.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | kompletný inventár | zostávajúce typy |
| Dátové typy a konštanty | 95 % | N/A | 9 B / 3 mutable polia | susedné 0822 dáta | index doména |
| Tabuľky a ukazovatele | 93 % | N/A | 081E je časový DWORD | alias writeri | úplný write ledger |
| Funkcie / ASM / CFG | 90 % | N/A | 243 B / 70 inštrukcií | CRT 2AEA | rekonštrukcia callee |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené call ordering | DEMO stopa |
| Scheduler | 96 % | N/A | sample/cache režimy a modulo | režimový writer času | 3CCF write/call graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | timestamp ordering | zachytiť DEMO |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | 0201 deadline používa DWORD čas | AI prirodzené intervaly | deadline producer |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | health updater |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable čas oddelený | persistencia času | SAVE call ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | clock parity | Win clock caller |

## Runtime testy na vykonanie

1. Zaznamenať DS/SS a hodnoty 3CC7/3CCF pri inicializácii, hlavnej slučke a DEMO; sledovať všetky zápisy DWORD 081E a volania sample/cached.
2. Overiť 11EE:2AEA, reálnu lokálnu štruktúru a jednotky jej prvých 6 B; porovnať DX:AX s emulovaným časom pri bežných podmienkach.
3. Pri BIOS režime kontrolovať origin=0, prechod cez tick WORD carry a denný reset. Overiť interrupt kontext pri dvojitom WORD čítaní.
4. Overiť poradie inicializácie 0476:0000 a jeho opakované volanie po zmenách nastavení. Modelované výsledky nie sú prirodzené runtime potvrdenie.
