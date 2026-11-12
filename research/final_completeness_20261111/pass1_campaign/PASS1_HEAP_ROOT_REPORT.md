# DOS 2.0: nepriame CRT heap polia, hlavička bloku a 64 KiB kódovanie

## Nové polia a spresnenie predchádzajúceho WORD view

| DS | Obrazový interval, koniec exclusive | Doložený typ a rola |
|---|---|---|
| 233E | [29A4E,29A52) | FAR pointer na posledný heap blok, počiatočne NULL |
| 2342 | [29A52,29A54) | WORD, počiatočne 3, kopíruje sa do nového heap headera +2 |
| 20F6 | [29806,29808) | WORD horný segmentový watermark, počiatočne 0 |
| 20F8 | [29808,2980A) | WORD dolný segmentový limit, počiatočne 0 |

Štyri polia zahŕňajú **10 B**, ale iba **8 B** prechádza z CLASSIFIED ONLY do PARTIAL: DS:2340 už bol 2 B PARTIAL WORD view. Nové FAR pole ho zahŕňa ako high/segment WORD, nepočíta ho druhýkrát. Predchádzajúci názov heap walk comparison WORD opisuje jeho priame použitie; nové nepriame zápisy dokazujú rodičovský FAR pointer. Presné počiatočné bajty a SHA sú v `data_fields.csv`.

Na ES:DI s DI=2336h sa teraz dá zostaviť 16 B control layout: +0 prvý blok FAR, +4 current/cache blok FAR, +8 posledný blok FAR, +0Ch header tag WORD a +0Eh predtým doložený WORD 2000h. Názvy first/current/last vyplývajú z konkrétnych link operácií. Širší význam tagu a control WORDu, všetci writeri a prirodzené inicializačné poradie zostávajú otvorené.

Z pôvodného 27 B bloku pred hookmi sú tak zostávajúce CLASSIFIED ONLY už iba **[29A3B,29A3D), 2 B**, a **[29A3F,29A40), 1 B**. Z ich núl sa nevyvodzuje padding. Predošlé reporty so siedmimi bajtmi zvyšku sú historické snímky pred týmto spresnením.

## Tri celé NEAR helpery

| Vstup | Obrazový interval, koniec exclusive | Inštrukčné B / počet |
|---|---|---:|
| 11EE:20FE, inicializácia bloku | [13FDE,14012) | 52 / 31 |
| 11EE:2132, pripojenie do rootu | [14012,14048) | 54 / 18 |
| 11EE:22E2, OS heap helper | [141C2,14206) | 67 / 29 |

Spolu **173 B / 78 inštrukcií**, byte-exact overených a nezávisle dekódovaných. Posledný helper má 68 B obalový rozsah a jeden nedosiahnutý bajt, ktorý sa nepridáva ako kód ani automaticky ako padding. Všetky tri končia NEAR RET; nejde o funkcie so samostatným BP rámcom.

## Zaokrúhlenie a systémová hranica

Pre callerom povolený request CX=0..FFE8h vypočíta helper:

```text
size_word = WORD(request + 27h) & FFF0h
paragraphs = size_word == 0 ? 1000h : size_word >> 4
repeat:
    AH = 48h
    INT 21h
    if CF == 1: return failure
    if returned_segment <= WORD DS:20F8: repeat
if returned_segment > WORD DS:20F6:
    DS:20F6 = returned_segment
DS = returned_segment; BX = 0
WORD DS:[2] = WORD ES:[DI+0Ch]
initialize_block(size_word)
append_block_to_root()
CF = 0
return
```

Skutočný kód výpočet paragraphs vykonáva cez NEG/NEG/CMC/RCR a tri SHR. Nulový size WORD teda neznamená nulovú alokáciu: reprezentuje **65 536 B, 4 096 paragrafov**. V tomto caller intervale vzniká pri requestoch FFD9h..FFE8h. Request=0 na úrovni tohto helpera vedie k 32 B bloku; nie je to tvrdenie o kompletnom malloc(0) API.

Úspešný helper necháva DS na novom segmente, BX=0, ES na control segmente a DI na control offsete. Caller musí tento kontext spracovať; nemožno ho nahradiť hypotézou, že DS zostáva DGROUP. AX/CX/DX/SI sú pracovné registre, úspešný AX sa tu neoznačuje za hotový návratový pointer mallocu. Pri modelovanej chybe sa overuje CF=1, seedovaný AX error, nezmenený root a pôvodný DS.

## Hlavička a pripojenie bloku

Nová hlavička v DS:0000 po inicializácii obsahuje:

| Offset | Šírka | Obsah |
|---:|---:|---|
| +00h | WORD | segment vlastného bloku |
| +02h | WORD | tag z rootu +0Ch |
| +04h | WORD | size WORD, 0 pre 64 KiB |
| +06h/+08h | WORD/WORD | dva interné offsety 0014h |
| +0Ah | WORD | WORD(size−2), teda FFFEh pri 64 KiB |
| +0Ch | FAR | link na nasledujúci blok, počiatočne NULL |
| +10h | FAR | link na predchádzajúci blok, počiatočne NULL |
| +14h | WORD | WORD(size−23), počiatočný interný node marker |
| size−2 | WORD | terminátor FFFEh |

Presný význam všetkých flag bitov interného node markeru sa neuzatvára iba podľa jeho hodnoty. Inicializátor explicitne vykoná CLD, obnoví uložené ES/DI a vráti sa; DF sa neobnovuje na pôvodnú hodnotu.

Prvý blok vyplní first/current/last FAR pointery rootu. Pri ďalšom bloku sa do starého tailu +0Ch uloží nový FAR pointer a do nového bloku +10h starý tail. Root first zostáva nezmenený, current/last sa prepnú na nový blok. Práve párové ES:DI+8/+0Ah zápisy a LES z ES:DI+8 dokazujú, že DS:233E/2340 je spoločný FAR pointer.

## Controlled replay a reprodukcia

`audit_replay_pass1_heap_root.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` vykonáva pôvodné tri helpery. Len **INT 21h/AH=48h** je modelovaný: vracia seedovaný segment/CF a zachová ostatné registre. Pamäť je v emulátore vopred mapovaná, žiadna reálna DOS alokácia neprebehne. ES=DS=referenčný DGROUP a DI=2336h sú vstupné predpoklady zodpovedajúce sledovanej caller ceste, nie prirodzená runtime stopa.

Finálna matica pri load bázach 0 a 1000h:

- všetkých 65 513 povolených requestov 0..FFE8h s novým rootom a tagom 3;
- vybrané requesty s tagmi 0/FFFFh na overenie WORD kopírovania;
- dva skutočne prepojené bloky, modelovaná systémová chyba a opakovanie po príliš nízkom segmente;
- zvýšenie horného watermarku aj jeho ponechanie pri vyššej pôvodnej hodnote.

Spolu **131 060 prípadov, 0 odchýlok**. Overujú sa požadované paragrafy, hlavička, terminátor, node marker, first/current/last linky, oba smerové FAR linky, watermark, CF/DS/ES/DI/SP podľa konkrétnej vetvy. Finálny SHA-256 `cases.csv`: `343e830d25bcc2b95d4b68b1087b5e12609eb81ae13f25474f0bf21e507cba79`. Predošlé menšie behy sa nezapočítavajú znova.

Artefakty `pass1_heap_root/`: tri ASM CSV, `data_fields.csv`, `cases.csv`, `summary.json`, aktuálna CSV/JSON mapa, promotion summary a nezávislá partition kontrola. Skutočný DOS ABI, dostupná pamäť, fragmentácia a úplné malloc/free algoritmy zostávajú otvorené. Žiadny počet modelovaných requestov z toho nerobí prirodzený runtime test.

## Pokrytie

Čistý prírastok je **8 B PARTIAL**. Aktuálna mapa: **55 014 B PARTIAL, 2 237 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, presne 57 295 B. Nezávisle overených 694 intervalov, SHA a presné členstvo, bez dier/prekryvov. Nižšie klasifikovaný zvyšok je v `remaining_after_heap_root/`: **94 intervalov / 2 281 B**.

Centrálny katalóg: **66 rozsahov, 2 316 inštrukcií / 5 674 B kódu**, 55 900 B typovaných dát celého obrazu a 55 012 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva iná, samostatne neuzavretá relokácia. Controlled replay súčet je 407 501 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. Výsledky zostávajú PARTIAL; GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | heap control a header layout | interné flagy | chunk metódy |
| Dátové typy a konštanty | 95 % | N/A | 10 B polí, 8 B čistý prírastok | 3 B fokus zvyšku | ich writeri |
| Tabuľky a ukazovatele | 93 % | N/A | first/current/last FAR linky | prirodzený lifetime | reálne alokácie |
| Funkcie / ASM / CFG | 90 % | N/A | 173 B / 78 inštrukcií | úplný malloc/free | 2168/21E4 |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené seedy | reset caller |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie udalostí | tick stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | call ordering | DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | prirodzené vstupy | effect producer |
| Sprity / HUD / paleta | 92 % | N/A | resource heap oddelený od assetov | reálny allocation flow | resource loader stopa |
| SAVE / LOAD | 92 % | N/A | heap pointer hierarchia | obnova/reset po LOAD | serializačné invarianty |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | heap ABI parity | Win allocator |

## Runtime testy na vykonanie

Zachytiť pôvodné INT 21h/48h bez modelu, registre pred/po volaní a root/hlavičku pri prvom aj druhom bloku. Overiť 64 KiB kódovanie pri prirodzene dostupnej požiadavke, segmentové limity a úspešný návrat celého mallocu. Následne sledovať free/coalescing a lifetime resource bufferov. DOSBox-X vykonanie zatiaľ chýba.
