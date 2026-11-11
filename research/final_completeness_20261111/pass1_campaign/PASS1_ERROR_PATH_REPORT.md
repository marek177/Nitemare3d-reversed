# PASS1: error helper a CRT exit

## Nový výsledok

`0FBA:000C` (obraz FBAC..FBD5) nie je iba neznámy error callback. Po úvodnom volaní `0476:0192` odovzdá formát a adresu argumentov do `11EE:285A`, vytlačí dodatočný reťazec cez `11EE:07E0` a volá `11EE:01EB` s WORD argumentom 1. Zakódované LEAVE/RETF za týmto volaním existujú; ich existencia nedokazuje prirodzený návrat.

CRT vstup `11EE:01EB` na obraze 120CB nastaví CX=0 a skočí do spoločnej vetvy 120EC. Tá uloží CX na zásobník a vykoná cleanup. Pri bežnom zachovaní zásobníka a návratov helperov sa pri 12142 obnoví AX=0, AH=0 nepreskočí ukončenie a 12147 načíta argument 1. Inštrukcie `MOV AH,4Ch; INT 21h` na 1214A/1214C žiadajú DOS o ukončenie procesu s AL=1. Tým sa odlišuje CRT ukončenie od vlastnej hernej logiky.

**Podmienky:** cleanup obsahuje FAR volania cez tabuľku `[DI]`, NEAR callback `[253A]` pri magic WORD D6D6h a FAR callback `[2542]` pri nenulovom `[2544]`. Ich úplný inventár a integrita zásobníka nie sú uzavreté. Preto výsledok nie je bezpodmienečný globálny non-return dôkaz ani DEEP VERIFIED kapacita. Pri normálnom DOS ukončení sa zápisy za capacity error neuskutočnia; runtime zásahy a poškodený stav zostávajú mimo tohto dôkazu.

## Dátové objekty a referencie

| Obrazový interval, koniec exkluzívny | Bajty | Obsah | Priamy dôkaz |
|---|---:|---|---|
| 28DBD..28DD2 | 21 | `MAXOBJ exceeded (%d)` + NUL | B842 push 350; B845 push DS:16AD; B848 error helper |
| 28DD2..28DE9 | 23 | `MAXGUARD exceeded (%d)` + NUL | B8E9 push 100; B8EB push DS:16C2; B8EE error helper |
| 2974A..2974D | 3 | bodka, LF, NUL | FBC2 push DS:203A; FBC5 output helper |

Mapovanie používa predpoklad default DS=2771h potvrdený pri štarte, nie nový dôkaz DS na každej caller ceste. Formátovací wrapper 1473A..14777 odovzdá tieto argumenty ďalej; celý formátovací engine sa v tejto dávke neoznačuje za uzavretý. Presné texty majú byte assertions a SHA rozsahov.

## Pokrytie a reprodukcia

Vstupná mapa `pass1_records28/noncode_intervals.csv` mala PARTIAL 11 784 B, CLASSIFIED ONLY 9 649 B, UNKNOWN 35 862 B. Nová mapa `pass1_error_path/noncode_intervals.csv` a JSON má **PARTIAL 11 831 B, CLASSIFIED ONLY 9 602 B, UNKNOWN 35 862 B, DEEP VERIFIED 0 B**. Súčet je 57 295 B; 47 B sa presunulo z CLASSIFIED ONLY do PARTIAL. Nejde o nové sémantické percento projektu.

Reprodukcia: `audit_pass1_error_path.py IMAGE PRIOR_MAP DECODER_DIR OUT`. Skript kontroluje SHA obrazu aj predchádzajúcich intervalov, rozhodujúce kódové bajty, všetky tri texty, nezávisle dekóduje päť ohraničených ASM okien a zachováva presný menovateľ. Neoznačuje ich automaticky ako celé uzavreté funkcie v centrálnom katalógu. Originálny runtime ani instruction replay sa v tejto dávke nespustili.

Ďalší krok: rekonštruovať obsah cleanup tabuľky DS:254E..2552, callback guard DS:2534/253A a registre/DS po úvodnom game cleanup helperi 0476:0192. DOSBox-X: breakpoint B848/B8EE, sledovanie DS a zásobníka cez FBAC, log všetkých cleanup cieľov a zachytenie AH=4Ch, AL=1 na 1214C. Error cestu testovať v izolovanej kópii stavu, aby nebolo potrebné poškodzovať pôvodné herné dáta.

## Aktualizácia 13 oblastí

Nové sémantické percento je pri každej oblasti N/A: úplný inventár kontraktov a vetiev ako menovateľ neexistuje. Metodika budúceho percenta: uzavreté jednotky / úplný inventár jednotiek danej oblasti; runtime parity osobitne. Historické čísla sú orientačné odhady, nie nameraná baseline. Nasledujúca tabuľka vykazuje iba nové dôkazy tejto dávky; bez nového dôkazu znamená bez zmeny predchádzajúcich zistení.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | MAXOBJ/MAXGUARD diagnostika | mapový vstup a limity | sledovať scan a tvorbu rekordov |
| Dátové typy a konštanty | 95 % | N/A | 47 B textov PARTIAL | prirodzený DS | caller DS cez game cleanup |
| Tabuľky a ukazovatele | 93 % | N/A | cleanup nepriame ciele identifikované ako otvorené | writeri callbackov | DS:254E..2552 a 253A |
| Funkcie / ASM / CFG | 90 % | N/A | error → CRT exit → DOS 4Ch podmienečná cesta | cleanup návraty | uzavrieť callback kontrakty |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa DEMO |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer a DAC stopa |
| GUARD / bossovia | 93 % | N/A | diagnostický limit 100 | lifecycle a AI prechody | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | slot lifecycle | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | obnova pointerov | sledovať tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | callback DS kontrakty |
