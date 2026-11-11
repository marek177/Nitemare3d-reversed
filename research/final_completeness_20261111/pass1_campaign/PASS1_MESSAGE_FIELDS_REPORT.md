# PASS1: dvanásť odkazovaných správ

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Nový dôkaz pokrýva **12 FAR16 pointerov a 12 NUL-terminated textov, spolu 887 B**. Každý má konkrétnu inštrukciu `PUSH DWORD PTR DS:[offset]` bezprostredne nasledovanú FAR volaním **0D29:0750**. Caller okná sú byte-pinned a nezávisle dekódované. Status PARTIAL.

Pointery majú offset do počiatočného default DS a segment 2771h so skutočnou EXEPACK relokáciou. Texty majú overený skutočný NUL, ASCII obsah vrátane prípadných LF/CR a presné SHA. Úplné texty, hranice, pointery, push a call bajty sú v `pass1_message_fields/message_references.csv`; typy v `data_fields.csv`.

Message helper na D9E8 odovzdáva pôvodný FAR argument do 0D29:052E. Ten na D7D0..D7D6 používa argument ako FAR text pre CRT helper s argumentom 0Ah a pri výsledku pokračuje ďalšou textovou vetvou. Úplný renderer/čakací kontrakt sa neuzatvára. V tomto reporte sa nedokazuje zobrazenie každej správy v prirodzenej hre ani platnosť DS na všetkých vstupných cestách.

Príklad jedného objektu: pointer v obraze 28572..28576 je odovzdaný na A55A..A55F; počiatočne smeruje na 2853E, text s LF o búrke a zhasnutých svetlách. Ostatné konkrétne texty sa evidujú adresne v CSV, nie iba cez zhodu slov. Susedné pointery volané inými helpermi sa touto dávkou nepromujú.

## Reprodukcia a pokrytie

`audit_pass1_message_fields.py IMAGE INVENTORY DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje SHA, pôvodné bajty a CS:IP, priame absolútne DS memory operandy, párové FAR volania, segmentové relokácie, mapovanie pointerov a textové terminátory. `promote_pass1_fields.py IMAGE PRIOR_MAP DATA_FIELDS OUT` aktualizuje mapu zo vstupu `pass1_crt_hook_slots/noncode_intervals.csv`.

Z 887 B bolo 24 segmentových bajtov už PARTIAL. Prírastok **863 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 49 597 B, CLASSIFIED ONLY 7 654 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predchádzajúca mapa: 48 734 / 8 517 / 44 / 0 B. Nový prirodzený runtime ani replay sa nevykonal.

Centrálny katalóg začleňuje typy a kontroluje ich zhodu s aktuálnou mapou. DOSBox-X plán: logovať prirodzený DS, pointery a renderované texty na uvedených call sites a sledovať writerov týchto polí. Ďalší krok: zostávajúce textové selector polia, CRT pointery a CLASSIFIED ONLY dáta; sémantické percentá sa z počtu správ neodvodzujú.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 147 polí/26 zdrojov; 887 B messages | 60 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 12 FAR text fields and direct call pairs | writeri/lifetime | pointer watchpointy |
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

