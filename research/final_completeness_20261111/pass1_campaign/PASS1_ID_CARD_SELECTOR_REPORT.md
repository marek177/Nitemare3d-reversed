# PASS1: ID card selector a jeho texty

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Funkcia **083D:1F6A**, obraz **[A33A,A378)**, má lokálnu dvojpoložkovú tabuľku FAR pointerov. Kopíruje DWORD DS:0D46 do SS:[BP-8] a DWORD DS:0D5A do SS:[BP-4]. Obe počiatočné polia majú segment 2771h so skutočnou EXEPACK relokáciou a texty `Red ID card` / `Yellow ID card`.

Argument WORD SS:[BP+6] sa vynásobí 4 cez SHL SI,2. DWORD zo SS:[BP+SI-8] sa odovzdá helperu 11EE:278C spolu s formátom **`You need a %s`** na DS:1508 a adresou lokálneho bufferu BP-48h. Následne sa SS pointer bufferu odovzdá 0D29:0720. Index sa lokálne neohraničuje, preto platné lokálne sloty 0/1 nepredstavujú dôkaz platnosti všetkých prirodzených caller vstupov. Kompletný formátovací a render kontrakt je otvorený.

| Objekt | Obrazový rozsah, end-exclusive |
|---|---|
| Red text | 2844A..28456 |
| Red FAR pointer | 28456..2845A |
| Yellow text | 2845A..28469 |
| Yellow FAR pointer | 2846A..2846E |
| Formát | 28C18..28C26 |

Samostatný bajt 28469h sa týmto dôkazom neoznačuje padding. Textový selector potvrdzuje mená ID kariet a formátovanie správy, nie kompletné pravidlá získania karty, otvárania dverí či prirodzené zobrazenie.

## Reprodukcia a metriky

`audit_pass1_id_card_selector.py IMAGE DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE, overuje SHA, pointery, relokácie, presné texty, formát a rozhodujúce selector bajty. Nezávisle dekóduje celé ohraničené telo. `promote_pass1_fields.py` použije vstup `pass1_crt_program_pointer/noncode_intervals.csv`. Výstupy sú v `pass1_id_card_selector/`.

49 B typovaných objektov zahŕňa 4 segmentové bajty už PARTIAL. Nových **45 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 49 867 B, CLASSIFIED ONLY 7 384 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 49 822 / 7 429 / 44 / 0 B. Netypované relokačné PARTIAL bajty klesli zo 48 na **44 B**; ide o inú množinu než 44 UNKNOWN bajtov. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: log indexov na A34F, výsledných FAR textov, formátovacieho bufferu a caller DS. Ďalší krok: prirodzené indexové guards a zostávajúce selector polia; PARTIAL sa nemení na DEEP VERIFIED iba z dôvodu presného textu.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 164 polí/29 zdrojov; ID card selector | 44 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | two-entry FAR selector and format | writeri/lifetime | pointer watchpointy |
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

