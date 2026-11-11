# PASS1: päť FAR textov čítaných po WORDoch

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Päť pointerov a päť textových objektov má spolu **232 B**, status PARTIAL. Nová klasifikácia sa neopiera iba o relokovaný segment či tlačiteľné bajty.

| DS pointer slot | Obraz pointera | Začiatok konkrétnej spotreby |
|---|---|---|
| 0F28 | 28638 | A76C |
| 0D72 | 28482 | A79E |
| 0D8C | 2849C | A7D6 |
| 0DA4 | 284B4 | A80E |
| 0DBE | 284CE | A846 |

Každé okno obsahuje `MOV BX,[offset]`, `MOV CX,[offset+2]`, `MOV DI,BX`, prípravu lokálneho bufferu a `MOV ES,CX`. Nasleduje REPNE SCASB cez ES:DI. Prvá vetva explicitne vynuluje AX pred skenom; ďalšie sú v rovnakom nadväzujúcom úseku, kde nulovosť AL a korektný DF závisia od predchádzajúceho toku. Kompletný CFG tejto rutiny sa touto dávkou neuzatvára.

Počiatočné segmentové WORDy pointerov sú 2771h a majú skutočné EXEPACK relokácie. Offsety smerujú do file-backed DS; presné texty, NUL hranice, LF a SHA sú v `pass1_split_strings/text_references.csv` a `data_fields.csv`. Následný kód vymieňa DS/ES a používa MOVSW/MOVSB pri kopírovaní alebo pripájaní do lokálneho bufferu. Nepotvrdzuje sa tým globálna kapacita bufferu ani bezpečnosť skenovania pri poškodených pointeroch alebo DF=1.

## Reprodukcia a meranie

`audit_pass1_split_strings.py IMAGE DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje SHA, oba WORD memory operandy, segmentovú spotrebu, skenovací opcode, relokácie, textové terminátory a nezávisle dekóduje päť okien. `promote_pass1_fields.py IMAGE PRIOR_MAP DATA_FIELDS OUT` používa vstup `pass1_message_fields/noncode_intervals.csv`.

Z 232 B bolo 10 segmentových bajtov už PARTIAL. Nových **222 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 49 819 B, CLASSIFIED ONLY 7 432 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 49 597 / 7 654 / 44 / 0 B. Nový prirodzený runtime ani replay sa nevykonal.

Centrálny katalóg začleňuje desať polí a overuje ich proti aktuálnej mape. Relokačné PARTIAL bajty bez konkrétnej dátovej roly klesli zo 60 na **50 B**. DOSBox-X plán: skutočný DS/ES/DI/AL/DF na každom skene, dĺžky a výsledný stack buffer pri všetkých vetvách. Ďalší krok: otvorené selectory textových polí a CRT pointery, nie opakovanie už doložených bajtov.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 157 polí/27 zdrojov; 232 B split strings | 50 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 5 split FAR fields and ES:DI scans | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

