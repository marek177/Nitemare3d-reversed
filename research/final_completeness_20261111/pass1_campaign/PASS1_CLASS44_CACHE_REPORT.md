# PASS1: epizódová cache a relatívne ID triedy 44h

Nová dávka typuje 2 B historického NON-CODE a rekonštruuje dve FAR funkcie. Replays používajú pôvodný vyhľadávač a reálne class tabuľky z MAP.1/2/3 bez nahradených callee tiel. Úroveň zostáva PARTIAL: prirodzené načítanie tabuliek, invalidácia cache a chybové vetvy nie sú úplne uzavreté.

## Presné hranice a dáta

Kanonický image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript pripína oba vstupy, porovnáva bajty každého štartu a nezávisle dekóduje CFG pomocou iced-x86.

**DS:012A, image [2783A,2783C)** je mutable WORD, pôvodne FFFFh. 00F7:017D ho porovná s WORD DS:626A a 0183 aktualizuje pri rozdiele. Je to cache key epizódy, nie VGA konštanta napriek tesnému susedstvu page segmentov. Jeho počiatočný sentinel nespôsobí aktualizáciu, ak by prvé epizódové WORD bolo tiež FFFF; prirodzená doména epizódy zostáva samostatný predpoklad.

Súvisiaci BYTE DS:2650 je cache prvého tile ID triedy 44h. Pri kanonickom DS leží na image offsete **29D60h**, presne za file-backed obrazom a historickou NON-CODE hranicou. Ide o BSS stav; táto dávka mu nevymýšľa pôvodný súborový bajt a nezapočítava ho do 57295 B. Vyhľadávanie číta 256 BYTE tabuľku DS:D30E, ktorú predchádzajúci loader plní z MAP headera; aktuálny replay ju explicitne seedu-je skutočnými bajtmi.

| Funkcia | Image interval, koniec exclusive | CFG |
|---|---|---:|
| 00F7:0004 primary-class search | [00F74,00FBD) | 73 B / 32 inštrukcií |
| 00F7:0176 class44 relative ID | [010E6,01125) | 63 B / 25 inštrukcií |

Obe majú FAR RETF a zachovávajú BP. Prvá prijíma WORD class na BP+6 a z druhého WORD na BP+8 používa iba nízky BYTE ako počiatočný index; druhá prijíma FAR pointer na tile BYTE na BP+6. AX je výsledok, BX/CX a pri relatívnej funkcii ES sú pracovné. DS/BP/SP sú v replayoch overené. Funkcie nepoužívajú skokovú tabuľku ani FAR indirect call.

## Algoritmus a otvorené vetvy

```text
search(class_WORD, start_WORD):
    start = low8(start_WORD)
    scan index start..255 for zero_extend(BYTE[D30E+index]) == class_WORD
    if found: return index
    scan index 0..255 for the same class
    if found: return index
    FAR_CALL 0FBA:000C(format_DS_00DA, class_WORD)
    return  // AX nie je explicitne nastavené na error sentinel

relative_id(tile_far):
    if WORD[012A] != WORD[626A]:
        WORD[012A] = WORD[626A]
        BYTE[2650] = low8(search(0044h, 0000h))
    tile = BYTE[tile_far]
    if BYTE[D30E+tile] != 0044h: return FFFFh
    return (zero_extend(tile) - zero_extend(BYTE[2650])) & FFFFh
```

Pri cache miss sa key zapisuje pred vyhľadávaním. Skutočný návratový osud po error callee, trieda mimo BYTE rozsahu a nenulové search start nie sú touto dávkou replayované. Statické telo ukazuje druhý úplný scan, ktorý môže opäť preskúmať už prezreté ID. V aktuálnych úspešných volaniach start=0 a trieda vždy existuje.

Pri cache hit sa BYTE[2650] ani class search neobnoví. Ak je cache seedovaná nesprávnou bázou 255, výsledky pre platné class44 tiles sú záporné modulo WORD hodnoty. Táto skúška potvrdzuje závislosť od cache invariantu; nedokazuje prirodzený bug ani dosiahnuteľnosť poškodeného stavu. Význam triedy 44h ako konkrétneho predmetu/spritu sa z číselnej zhody nevyvodzuje.

## Reálne MAP dáta

Použitých 256 primary-class BYTE je v každom súbore presne [2,258). Hlavička má 514 B; file I/O sa v tejto dávke nevykonáva. Úplné SHA sú v `assets.csv`/`summary.json`.

| Súbor | Veľkosť | Trieda 44h ID (decimal, inclusive) | Počet | Relatívne ID pri správnej cache |
|---|---:|---|---:|---|
| MAP.1 | 90626 B | 186..223 | 38 | 0..37 |
| MAP.2 | 82434 B | 192..229 | 38 | 0..37 |
| MAP.3 | 82434 B | 192..229 | 38 | 0..37 |

Všetky class44 ID sú v každom z týchto troch skutočných headerov súvislé. To nie je garancia pre neznáme/custom mapy. Ostatné tile ID vracajú FFFFh.

## Reprodukcia a výsledky

`audit_replay_pass1_class44_cache.py IMAGE INVENTORY DECODER EMULATOR MAP_DIR OUT` vytvorí dve ASM CSV, `data_fields.csv`, `assets.csv`, `cases.csv`, `summary.json`. Pri load bázach 0/1000h aplikuje reálne EXEPACK relokácie. Pozorovací code hook iba počíta vstupy do search a zastaví pri neočakávanej error vetve; nič nemení v registroch ani pamäti.

**4608 prípadov, 0 odchýlok** = 2 load bázy × 3 skutočné headery × všetkých 256 tile BYTE × 3 cache scenáre (miss, správny hit, seedovaná chybná báza). Overuje AX, key, cache base, počet search volaní, DS/BP/SP. Search sa vykonáva natívnymi pôvodnými inštrukciami v každom miss prípade. Modelované FAR tile pointery a BSS tabuľka nenahrádzajú prirodzený beh loadera. SHA cases `0530a8fc6e66082e93299da8aef3a2ada2afdaf79fd2c910d06f2a70e63f2f7d`.

2 B CLASSIFIED ONLY → PARTIAL. Aktuálna mapa: **55077 B PARTIAL, 2174 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 716 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `d8166a355b27c3197e01526ba3933fd640373fae627da61a81cd3c8fce733058`; kontrola integrity nie je dôkaz úplnej sémantiky.

Centrálny katalóg: 80 funkčných rozsahov, 2818 inštrukcií / 7039 B, 55963 B typovaných dát celého obrazu; 55075 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay súčet 536033 plus osobitne 65548 smerových normalizačných prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé hodnoty sú orientačné. Počty prípadov ani 716 overených intervalov nenahrádzajú sémantické percentá.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | class44 rozsahy troch MAP headerov | custom dáta | search error cases |
| Dátové typy a konštanty | 95 % | N/A | 2 B epizódový key | alias writeri | cache invalidácia |
| Tabuľky a ukazovatele | 93 % | N/A | primary-class search a BSS base | neplatný cache stav | startup BSS |
| Funkcie / ASM / CFG | 90 % | N/A | 136 B / 57 inštrukcií | search error callee | 0FBA:000C |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO trace |
| Scheduler | 96 % | N/A | bez nového dôkazu | runtime timing | scheduler loop |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Renderer / VGA | 94 % | N/A | cache odlíšená od page segmentov | class44 význam | relatívne ID calleri |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | class44 relatívne ID 0..37 | asset identity | consumer dispatch |
| SAVE / LOAD | 92 % | N/A | cache key závisí od epizódy | reset pri LOAD | call/write ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | class parity | Win class table |

## Runtime testy na vykonanie

Pri prechode epizód a LOAD sledovať DS:012A, DS:2650, DS:626A, class tabuľku a všetky vstupy relative_id. Overiť načítanie správneho headera pred cache miss a prípadné resetovanie key pri opakovanom načítaní tej istej epizódy. Zachytiť význam class44 výsledku u prirodzených callerov. Pôvodné DOSBox-X vykonanie zostáva otvorené.
