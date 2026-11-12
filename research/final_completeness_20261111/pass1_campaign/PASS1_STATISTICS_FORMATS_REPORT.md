# PASS1: štatistické formáty a riadiaca funkcia

Dávka staticky typuje **439 B** ako osem konkrétne spotrebovaných NUL formátov a rekonštruuje jednu lokálnu funkciu. Úroveň PARTIAL: formátovač ani prirodzené štatistiky a ukončenie programu sa nevykonávajú. Nové replay prípady 0.

## Vstupy a metóda

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. `audit_pass1_statistics_formats.py IMAGE INVENTORY DECODER OUT` overí identity, každý pôvodný inštrukčný štart, presné hranice textov, NUL, konverznú gramatiku a **priamu dvojicu PUSH format offset / FAR CALL 11EE:07E0** pre všetkých osem polí. Iné číselné immediates, ktoré náhodou smerujú dovnútra textov, sa nepoužívajú ako sémantické dôkazy.

Kanonické DS=2771h je podmienka mapovania near formátov. Skript overuje každú príslušnú WORD immediate voči image adrese. Presné texty s LF a NUL, range SHA, call IP, typy konverzií a variadic payload bytes sú v `format_catalog.csv` a `data_fields.csv`.

## Presný katalóg

Všetky intervaly polootvorené; všetky obsahujú vlastný koncový NUL.

| Formátová oblasť | Image interval | PUSH / CALL v CS 0476 | Typy payloadu v poradí |
|---|---|---|---|
| Vectors/Objects/Guards | [27FE3,28012) | 022F / 0232 | 6× unsigned WORD |
| Frame rate | [28012,28037) | 0246 / 0249 | 4× unsigned WORD |
| Near heap | [28037,28067) | 025D / 0260 | 3× unsigned WORD |
| Far heap | [28067,2809A) | 0274 / 0277 | 3× unsigned WORD |
| Extended memory | [2809A,280C8) | 0292 / 0295 | 3× unsigned WORD |
| Tile slots | [280C8,2810E) | 02B4 / 02B7 | WORD, DWORD, DWORD, WORD, WORD |
| Object slots | [2810E,28154) | 02D6 / 02D9 | signed WORD, DWORD, DWORD, WORD, WORD |
| Sound slots | [28154,2819A) | 02F8 / 02FB | WORD, DWORD, DWORD, WORD, WORD |

`%lu` sú explicitne DWORD a `%u/%d` WORD v tomto 16-bitovom caller kontexte. Frame formát má štyri `%u`; caller dodá dva WORD a jeden DWORD, ktorý sa spotrebuje ako dva samostatné WORD. Nejde o jeden `%lu`. Popisy formátov sú statické štítky programu; samy nepotvrdzujú správnosť vypočítaných runtime hodnôt alebo maximálnu kapacitu všetkých herných štruktúr.

## Funkcia, CFG a argumenty

**0476:01D0, image [04930,04A73)**, 323 B / 100 inštrukcií, úplný lokálny CFG. Prolog PUSH BP/MOV BP,SP; dva WORD argumenty BP+6/BP+8, prvý sa testuje cez low BYTE. FAR RETF; stack sa po formátovacích volaniach opakovane obnovuje MOV SP,BP. Žiadna jump table ani lokálna slučka. Callee telá sa nepovažujú za uzavreté týmto CFG auditom.

```text
call 0156:0254(3)
if low8(arg1) == 0:
    voliteľná cesta cez 083D:29CA(1), 0277:17DC(15),
    page flip, 0156:0254(2), 0D29:04FA
call local 0192
if low8(arg1) != 0:
    vypíš vectors, frame rate, near heap, far heap
    if BYTE[3CCE] != 0: vypíš extended memory
    vypíš tile slots, object slots, sound slots
else:
    call 0D29:162C
call CRT 11EE:01EB(arg2)
return FAR  // ak sa tento callee vráti
```

Presné predpodmienky voliteľnej cesty sú zachované v ASM CSV: query DX:AX musí byť nula a nasledujúci AL nenulový. Širší význam registrácie alebo príslušnej obrazovky sa z toho neuzatvára. CRT 01EB je termination-like dependency; v tejto dávke sa nevykonáva a návrat v lokálnom CFG nie je dôkaz, že sa prirodzený exit vracia.

Konkrétne argumenty formátov zo zásobníka:

- Vectors: WORD[626E], 1000; Objects: WORD[6270], 350; Guards: WORD[6276], 100.
- Frame: WORD[455A], WORD[4556], low WORD[455C], high WORD[455C].
- Near: WORD[3CB0]−WORD[3CB2] modulo WORD, total[3CB0], remaining[3CB2]; far analogicky 3CB4/3CB6, extended 3CB8/3CBA.
- Tile: výsledok 0768:0004, DWORD[E006], DWORD[E00A], WORD[E010], WORD[E00E].
- Object: výsledok 0768:0008, DWORD[E012], DWORD[E016], WORD[E01C], WORD[E01A].
- Sound: výsledok 0768:000C, DWORD[E01E], DWORD[E022], WORD[E028], WORD[E026].

Ide o presné operandové zdroje a poradie, nie prirodzené hodnoty. Tieto runtime/BSS polia sa nepromujú na file-backed NON-CODE len preto, že sú pomenované formátom. Počítanie reload/thrash nebolo vykonané. Celý formatter 07E0 ani jeho výstupné zariadenie sa touto dávkou neoverujú.

## Artefakty a meranie

`statistics_exit_dispatch.csv` obsahuje 100 inštrukcií s bajtmi a adresami; `calls.csv` explicitné lokálne/FAR call sites; `format_catalog.csv` konverznú mapu; `data_fields.csv` presné osem polí; `summary.json` rozsah a obmedzenia. Skript je reprodukovateľný bez spustenia hry alebo termination callee.

Presne **439 B CLASSIFIED ONLY → PARTIAL**. Mapa: **55689 B PARTIAL, 1562 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 767 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `d5c16296ca9fc11545e742481946de3ac1cb47b3f86c27cc495d7dba29a1c987`. Integrita mapy sama nepreukazuje sémantickú úplnosť.

Katalóg: 90 funkčných rozsahov, 3235 inštrukcií / 8125 B, 56575 B typovaných dát celého obrazu; 55687 B historických NON-CODE dát a 2 netypované PARTIAL relokačné bajty. Controlled replay zostáva 614175 plus osobitne 65548 smerových prefixových prípadov. Pôvodné runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. 439 typovaných bajtov alebo 100 inštrukcií nepredstavuje percento sémantickej úplnosti celej oblasti.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | 8 variadic formátov | formatter behavior | 07E0 closure |
| Dátové typy a konštanty | 95 % | N/A | 439 B / 8 NUL polí | zvyšné intervaly | ďalší veľký blok |
| Tabuľky a ukazovatele | 93 % | N/A | konkrétne near format adresy | DS caller invariant | startup trace |
| Funkcie / ASM / CFG | 90 % | N/A | 323 B / 100 inštrukcií | callee účinky | 0192 a 07E0 |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | frame DWORD rozdelený na dva `%u` | význam metriky | 455C writeri |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | predcesta page flip staticky | prirodzený scenár | caller trace |
| GUARD / bossovia | 93 % | N/A | 6276 zobrazené voči 100 | runtime počet | count writer |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | slots metriky odlíšené | počítanie reload/thrash | 0768 gettery |
| SAVE / LOAD | 92 % | N/A | štatistické texty oddelené | persistencia metrík | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | stats parity | Win format match |

## Runtime testy na vykonanie

V izolovanom DOS behu zachytiť skutočný caller 01D0 a flag argumenty, výstup 07E0, DS a formátové raw argumenty. Overiť metriky proti ich writerom, zvlášť dva WORD z DWORD 455C a slot countery. Ukončenie 01EB sledovať ako osobitný terminálny tok. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
