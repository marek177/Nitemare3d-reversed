# PASS1: cache epizódy a file handle grafického súboru

Dávka typuje 4 B historického NON-CODE a rekonštruuje celé riadiace telo 0277:0002. Úroveň PARTIAL: open/close/seek/read/error sú v replays nahradené hookmi. Pôvodné file I/O, asset payload a terminálne error správanie zostávajú otvorené.

## Hranice a ABI

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí identity, pôvodné inštrukčné bajty a nezávisle rekonštruuje CFG.

| Položka | Image interval, koniec exclusive | Typ / dôkaz |
|---|---|---|
| Funkcia 0277:0002..008A | [02772,027FA) | 136 B / 43 inštrukcií |
| DS:017C | [2788C,2788E) | mutable WORD initial 0, cached handle; test, zápis AX a handle argumenty |
| DS:017E | [2788E,27890) | mutable WORD initial 0, cached episode; CMP/MOV s DS:626A |

DS=2771h sa v modeli nastavuje explicitne. Funkcia prijíma FAR destination na SS:BP+6, DWORD file offset na BP+0A, WORD count na BP+0E. FAR RETF, argumenty odstraňuje caller. BP/DS/SP sa overujú; pracovné registre a AX výsledok po prípadnom error callee nemajú deklarovanú všeobecnú garanciu. Medzi callee volaniami sa SP obnovuje na BP.

## Algoritmus

```text
if WORD[017E] != WORD[626A] and WORD[017C] != 0:
    close_11EE_1BB6(WORD[017C])
    WORD[017C] = 0
WORD[017E] = WORD[626A]
if WORD[017C] == 0:
    WORD[017C] = open_11EE_1C72(near_628C,8000h)
    if WORD[017C] == FFFFh:
        error_0FBA_000C(near_0180,near_628C)
seek_11EE_1BD6(WORD[017C],offset_DWORD,0)
result = read_0FBA_009E(WORD[017C],destination_FAR,count_WORD)
if result != count_WORD:
    error_0FBA_000C(near_0196,near_628C)
return FAR
```

Near filename buffer 628C je z predchádzajúcej epizódovej prípravy `img.N`; v tejto dávke sa jeho tvorba nevykonáva. Hook používa explicitný `img.1` seed, pričom argumentový near offset sa musí zhodovať aj v syntetických testoch inej epizódy. Nejde o dôkaz file name koherencie všetkých prirodzených callerov.

Cache používa 0 ako neprítomný handle. Ak open v modeli vráti 0, toto volanie ho ešte odovzdá seek/read, ale ďalšie volanie bude znovu otvárať. FFFFh naopak zostáva uložený nenulový stav. Pri vracajúcom error hooku sa po neúspešnom open pokračuje seek/read s FFFFh; prirodzené error callee môže proces ukončiť, preto sa táto syntetická kontinuita nepovažuje za dosiahnutú hernú cestu.

Close výsledok a seek DX:AX sa v tomto tele nekontrolujú. Read sa posudzuje iba WORD rovnosťou s požiadavkou. Predchádzajúci audit DOS read wrappera doložil FFFFh ako chybový sentinel; pri count=FFFFh sa rovnaká návratová hodnota v tejto vrstve od úspešného počtu nerozlíši. Prirodzená doména count a dosiahnuteľnosť takej požiadavky nie sú uzavreté. Krátke čítanie, ktoré sa počtom nerovná požiadavke, vedie do error callu.

## Reprodukcia a výsledky

`audit_replay_pass1_image_handle_cache.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára ASM CSV, data fields, cases a summary. Pri load 0/1000h aplikuje reálne EXEPACK relokácie. Päť callee tiel je nahradených RETF/hookmi. Kontrolujú sa presné open WORD argumenty, close handle, seek handle/DWORD offset/origin, read handle/FAR pointer/count a oba error format/name argumenty. Žiadny súbor sa neotvára a žiadne payload bajty sa nepovažujú za načítané.

**5184 prípadov, 0 odchýlok** = 2 load bázy × 4 old/current epizódové dvojice × 3 staré handles × 3 open výsledky × 4 counts × 3 read výsledkové scenáre × 3 DWORD offsets × 2 seek výsledky. Counts 0/1/16/FFFF; handles 0/7/FFFF; offsets 0/7FFFFFFF/FFFFFFFF. Seek vracia 0 alebo FFFFFFFF; close hook vracia 5, ktoré caller ignoruje. Read výsledky sú equal, request−1 modulo, FFFF. Overuje sa presný call trace, oba cache WORD a návratový DS/BP/SP. Nejde o exhaustívny súčin všetkých stavov ani pôvodný DOS I/O test. SHA cases `a438aa1a4214152ab0a2c46bebdfbcc52e2c98b1b68dea1f0d5474eb92399cc9`.

## Meranie

4 B CLASSIFIED ONLY → PARTIAL. Mapa: **56801 B PARTIAL, 450 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 842 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `00d32d18511650b5f18aeb6ab11a5b9bcec710adcc5c44ff28b777ef731bd70b`. Integrita mapy sama nepreukazuje sémantickú úplnosť.

Katalóg: 94 funkčných rozsahov, 3356 inštrukcií / 8449 B, 57687 B typovaných dát celého obrazu; 56799 B historických NON-CODE dát a 2 PARTIAL netypované relokačné bajty. Controlled replay 710527 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Replay počty nepreukazujú úplné asset I/O.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | presné offset/count argumenty | img payload | loader calleri |
| Dátové typy a konštanty | 95 % | N/A | 4 B / 2 WORD | ostatné cache writeri | reset ledger |
| Tabuľky a ukazovatele | 93 % | N/A | handle odlíšený od epizódy | prirodzená handle doména | open ABI |
| Funkcie / ASM / CFG | 90 % | N/A | 136 B / 43 inštrukcií | pôvodné callees | seek/open closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | bez nového dôkazu | timing | loop trace |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | cached image file read vrstva | pixel spracovanie | asset parser |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | konkrétna image read vrstva | asset identity | caller/chunk ledger |
| SAVE / LOAD | 92 % | N/A | asset handle cache oddelená | reset pri epizóde/LOAD | natural trace |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | I/O parity | Win cache match |

## Runtime testy na vykonanie

Pri prirodzenom načítaní image zaznamenať 017C/017E, filename, request count, offset a DOS výsledky. Overiť prechod epizód a opakované čítanie tej istej epizódy, skutočný seek error a terminálne správanie error callee. Zistiť, či caller môže požadovať FFFFh. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
