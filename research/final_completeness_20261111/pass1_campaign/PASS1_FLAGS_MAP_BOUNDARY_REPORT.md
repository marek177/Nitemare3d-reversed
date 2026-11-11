# PASS1: 64 flagov a oprava hranice dvojbajtovej mapy

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Táto dávka opravuje starší nominálny rozsah v PASS1_MAP_GRID_REPORT.md; starý rozsah nie je aktuálnou hranicou mapového objektu.

## Nový dôkaz a oprava

Na 36C7..36D3 SAVE cesta explicitne vloží dĺžku **2000h**, segment **21FDh**, offset **373Eh** a volá DOS write wrapper 0FBA:00B8. Mapový serializovaný rozsah je teda **21FD:373E..573E**, obraz **[2570E,2770E)**, 8 192 B.

Starší scan B815 začína na 373Fh a číta BYTE s krokom 2 v cykloch 64×64. To je druhý BYTE buniek mapy so začiatkom 373Eh. Dôkaz scanu neoprávňoval rozšíriť celý nominálny dvojbajtový slot až za posledný čítaný BYTE. Pôvodne publikovaný lokálny nominálny rozsah `[2570F,2770F)` bol preto posunutý o jeden bajt. Nová mapa pridáva prvý doložený bajt 2570Eh do PARTIAL a vracia posledný nedoložený bajt **2770Eh do UNKNOWN**. Adresa 2770Fh zostáva UNKNOWN. Presný význam oboch mapových BYTE sa ešte neuzatvára.

## Tabuľka 64 BYTE flagov

Na 382F..383A SAVE cesta odovzdá dĺžku 40h a FAR pointer **21FD:36FE** do rovnakého write wrappera. Rozsah je **[256CE,2570E)**, 64 B. Nezávisle na 5524..5534 kód vynuluje EAX, nastaví ECX=10h a DI=36FEh a vykoná REP STOSD cez segmentový globál DS:255E, počiatočne relokovaný 21FDh. Pri DF=0 to vyčistí presne 16*4 B. Na 5541 sa číta BYTE ES:[BX+36FE], pri nule sa na 5549 nastaví na 1.

To potvrdzuje tabuľku bajtových flagov a nominálny serializovaný rozsah, nie platnosť každého runtime BX. Nulovací úsek nemá CLD; prirodzený DF a globálna nemennosť segmentového globálu zostávajú otvorené. SAVE wrapper používa AH=40h podľa už analyzovaného primitívu; úspešný prirodzený zápis súboru sa v tejto dávke nemeral.

## Reprodukcia a presná bilancia

`audit_pass1_flags_map_boundary.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje SHA, skutočné relokácie segmentov serializačných argumentov, kódové bajty dĺžok a offsetov, flagové nulovanie, počiatočné nuly a intervalové SHA. Explicitne vykonáva aj downgrade jedného predtým PARTIAL bajtu. Výstupy sú v `pass1_flags_map_boundary/`.

Predošlá mapa: PARTIAL 47 965 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 108 B. Pribudne 65 B PARTIAL (64 flagov + prvý bajt mapy), **1 B sa vráti do UNKNOWN**. Nová mapa: **PARTIAL 48 029 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Net prírastok je 64 B, nie 65 B. História starých dávok sa zachováva, aktuálna mapa ich hranice nahrádza. Nový runtime ani replay sa nevykonal.

Zvyšných 44 B: `[1BDA2,1BDB0)` 14 B, `[1C070,1C080)` 16 B, `[1D0EC,1D0F0)` 4 B, `[20B88,20B90)` 8 B, `[2770E,27710)` 2 B. Nulový obsah nie je dôkaz paddingu. PARTIAL ani CLASSIFIED ONLY nie sú DEEP VERIFIED úplnosť.

DOSBox-X plán: sledovať rozsahy SAVE/LOAD, oba BYTE mapových buniek, flagové BX a vstupný DF; sledovať dva bajty za mapou samostatne. Ďalší krok: audit zostávajúcich núl a konsolidácia aktuálnych hraníc do centrálnych katalógov.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 64 B flags plus corrected 8192 B map boundary | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | explicit SAVE lengths and relocated pointers | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | flag reads/writes and DF-dependent clear | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | map and flags serialization bounds | LOAD parity | natural SAVE/LOAD trace |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
