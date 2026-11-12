# PASS1: nulovaná FAR alokácia a retry callback

Dávka typuje 4 B a rekonštruuje celé telo CRT 11EE:2A16. Úroveň PARTIAL: DOS alokácia je modelovaná, retry callback je hook. Pôvodný správca pamäte, veľké úspešné alokácie a prirodzené callery zostávajú otvorené.

## Presné hranice a ABI

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript kontroluje identity, každý pôvodný štart a nezávislý CFG.

- Funkcia **11EE:2A16..2AEA, image [148F6,149CA)**: 212 B / 97 inštrukcií.
- Callback **DS:246A, image [29B7A,29B7E)**: mutable FAR16 pointer, pôvodne 0000:0000. OR oboch WORD testuje null, FAR CALL [246A] dokazuje pointerový typ.

Funkcia má DWORD count na SS:BP+6 a WORD size na BP+0A. Vracia FAR pointer DX:AX, pričom malé úspešné prípady vrátia segment:0000. BP/SI/DI/DS/SP sa v modeli zachovávajú. ES, pracovné registre a flags nie sú všeobecne zachované; úspešná zero-fill cesta vykoná CLD. Chybová cesta pred nulovaním nemusí vstupný DF meniť.

## Riadenie a algoritmus

Telo násobí DWORD count × WORD size, ale zachováva iba low32 produktu. Nulový produkt smeruje do failure vetvy. Ďalšie WORD/DWORD hranice a pravidlá pre size, vrátane power-of-two testu `(size-1)&size`, sú presne zachované v ASM CSV. V rozsahu testovaných úspechov product<65536 platí jednoduchá odstavcová veľkosť `ceil(product/16)` a offset0. Pre veľké prípady sa uplatňuje dodatočný SI alignment výpočet; táto dávka mu nepripisuje všeobecnú overenú high-level calloc špecifikáciu.

```text
retry:
    vykonaj pôvodné multiply/bounds/alignment výpočty
    ak neplatný vstup: goto failure
    INT21 AH48, BX = odstavce
    ak CF=1: goto failure
    ak returned_segment <= WORD[20F8]: opakuj INT21 AH48
    end_segment = returned_segment + paragraphs - 1
    ak end_segment > WORD[20F6]: WORD[20F6] = end_segment
    nuluj všetky alokované odstavce
    return DX:AX = segment:alignment_offset
failure:
    AX=DX=0
    if DWORD[246A] != 0:
        AX = FAR_CALL [246A](size_WORD,count_low_WORD,count_high_WORD)
        DX = sign_extend(AX)
        if AX != 0: goto retry
    return DX:AX
```

Retry test je nula/nenula; FFFFh sa považuje za pokyn zopakovať, nie automaticky za signed neúspech. Callback môže v skutočnom tele meniť podmienky; mock iba vracia zadanú sekvenciu. Vetva segment<=20F8 opakuje OS alokáciu bez lokálneho free callu v tomto tele; jej prirodzená dosiahnuteľnosť, zásoba pamäte a celkový lifecycle sa neuzatvárajú.

Zero-fill používa ES, DI=0, AX=0 a REP STOSW, po blokoch najviac 1000h odstavcov. Nuluje aj padding posledného odstavca, nie iba presný product byte count. V malých testoch sa kontroluje celý odstavcový rozsah a dva nasledujúce nezmenené guard bajty.

## Reprodukcia a výsledky

`audit_replay_pass1_halloc.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára ASM CSV, data fields, cases a summary. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Pôvodné telo sa nemení. INT21/AH48 hook buď vráti CF=1/AX=8, alebo modelovaný segment6000h. Callback RETF/hook overí tri WORD argumenty presne v poradí na stacku. Žiadna hostiteľská ani pôvodná DOS pamäť sa nealokuje.

**552 prípadov, 0 odchýlok**:

- 504 failure/retry prípadov: 2 load bázy × 9 DWORD counts × 7 WORD sizes × 4 callback policies (null,0,1→0,FFFF→0). Niektoré neplatné vstupy zlyhajú pred OS callom, iné po modelovanom CF=1; oba sú evidované.
- 48 malých úspešných prípadov: 2 bázy × 6 counts × 4 sizes; overený počet odstavcov, DX:AX, high-watermark, celý vynulovaný rozsah a guard bajty.

Count failure matica obsahuje 0/1/15/16/4096/FFFF/10000/10001/FFFFFFFF, size 0/1/2/3/16/256/FFFF. Úspešné counts 1/2/15/16/17/255 a sizes1/2/3/16 zostávajú pod 65536 B. Veľké success a segment wrap nie sú testované. SHA cases `cd515f35fa5f40f552e5bb9f825303352b4eb643d3035cc75669714d5e4cfdce`.

## Susedný kalendárny kandidát

[29B7E,29B98) má presných 13 WORD `−1,30,59,90,120,151,181,212,243,273,304,334,365`, teda priestupný kumulatívny vzor. Táto formula už bola známa v staršej dávke a **nepromuje sa znovu ani teraz**. Indexed operand DS:2486 v 11EE:2DD0 smeruje na posledný WORD tejto oblasti, ale pri nominálnom month1..12 vstupuje do nasledujúcej common-year tabuľky. Samotný nesprávny/okrajový index0 nie je dôkaz bežného používania celej priestupnej tabuľky. Jej funkčná rola zostáva CLASSIFIED ONLY. Samostatný susedný nulový BYTE sa tiež neoznačuje za padding.

## Meranie

4 B CLASSIFIED ONLY → PARTIAL. Mapa: **56869 B PARTIAL, 382 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 848 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `0e86809d2d5ec5c4c480c68d9c7a48ac6a98e665623868fae67bcd746176d5f9`. Partition integrita nie je dôkaz úplnej sémantiky.

Katalóg: 98 bounded funkčných rozsahov, 3502 inštrukcií / 8773 B, 57755 B typovaných dát celého obrazu; 56867 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay 777039 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Malé úspešné modely nepreukazujú celé DOS heap ABI.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | kalendárny kandidát zostáva otvorený | konzument celej tabuľky | pointer derivácie |
| Dátové typy a konštanty | 95 % | N/A | 4 B FAR callback | writeri | callback init |
| Tabuľky a ukazovatele | 93 % | N/A | presné tri WORD callback args | telo retry | call/write ledger |
| Funkcie / ASM / CFG | 90 % | N/A | 212 B / 97 inštrukcií | veľké success alignment | rozšíriť doménu |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | runtime allocator oddelený | prirodzené callery | caller graph |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | žiadny nový render dôkaz | asset heap vzťah | asset caller |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | nulovanie alokácie oddelené | asset identity | resource allocation |
| SAVE / LOAD | 92 % | N/A | CRT heap stav oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | allocator parity | Win CRT helper |

## Runtime testy na vykonanie

Sledovať prirodzené counts/sizes, retry callback a DOS AH48 výsledky, osobitne hranice 64 KiB/128 KiB a veľké size. Overiť returned alignment pointer a nulovanie, segment<=20F8 a high-watermark. Kalendárny kandidát sledovať oddelene, bez záveru z numerickej zhody. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
