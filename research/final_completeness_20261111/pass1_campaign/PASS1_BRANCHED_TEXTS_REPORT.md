# PASS1: textové pointery cez spoločné call vetvy

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Štyri FAR pointery a NUL texty tvoria **168 B**, status PARTIAL. Presné texty a adresy sú v `pass1_branched_texts/text_references.csv`, typy/SHA v `data_fields.csv`.

| DS slot | PUSH site | Nadväzujúca cesta |
|---|---|---|
| 0E88 | A74A | JMP A757 → FAR 0D29:0720 |
| 0F52 | A87D | JMP A8CC → FAR 0D29:0720 |
| 114A | 933F | JMP 9369 → FAR 0D29:0720 |
| 10EE | 92FE | priamo 9303 → FAR 0D29:06BC |

Prvé tri texty informujú o oprave napájania, prasknutom zrkadle a nesprávnej kombinácii. Štvrtý je počiatočný text otázky na kombináciu vrátane koncových znakov pred skutočným NUL; úplný obsah sa zachováva v CSV, neodrezáva sa podľa interpunkcie či vizuálneho dojmu. Všetky pointer segmenty majú počiatočnú hodnotu 2771h a skutočnú EXEPACK relokáciu.

Pre prvé tri je doložené, že pointer ostáva na zásobníku pri krátkom JMP a spoločný FAR CALL ho použije ako argument. Samotná neprítomnosť susedného CALL za PUSH teda neznamená nevyužitý text. Vetva 10EE vkladá aj lokálny NEAR buffer a argument 6. Helper 0D29:06BC v prefixe D94C..D964 odovzdáva pôvodný FAR text helperu 0D29:052E a následne vynuluje prvý BYTE výstupného bufferu. Kompletná vstupná slučka a význam limitu 6 ešte nie sú uzavreté.

Nie je potvrdená prirodzená dosiahnuteľnosť každej správy, platnosť DS všetkých callerov ani nemennosť pointerov. Layout/text nie je dôkaz úplnej puzzle logiky. Okná spoločných vetiev sú ASM anotácie, nie nové celé funkcie v centrálnom počte.

## Reprodukcia a metriky

`audit_pass1_branched_texts.py IMAGE DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje SHA, pointer/text hranice, relokácie, PUSH, presné JMP a spoločné CALL bajty; nezávisle dekóduje sedem okien. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_ctype/noncode_intervals.csv`. Výstupy sú v `pass1_branched_texts/`.

Z 168 B bolo 8 segmentových bajtov už PARTIAL. Nových **160 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 50 517 B, CLASSIFIED ONLY 6 734 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 50 357 / 6 894 / 44 / 0 B. Netypované relokačné PARTIAL bajty klesli z 20 na **12 B**. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: stopy spoločných CALL vetiev, textové pointery a buffer otázky na kombináciu, jeho skutočný limit a ukončenie. Ďalší krok: otvorené štyri selector položky, demo pointer a CRT hook bez spotrebiteľa; neuzavretý symbol sa nevyhlási za nepoužitý podľa absencie priameho xref.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 198 polí/34 zdrojov; branched text pointers | 12 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 3 shared call branches and 1 input prompt | writeri/lifetime | pointer watchpointy |
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

