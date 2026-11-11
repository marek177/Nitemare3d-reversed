# PASS1: konštantné open a jediné %s argumenty

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. **24 samostatných NUL ASCII objektov, 242 B**, má konkrétne argumentové spotreby. Status PARTIAL.

Použité vzory sú úzke a oddelené:

- Konštantný NEAR filename PUSH bezprostredne pred presným FAR CALL 11EE:1C72. Názov musí celý ležať vo file-backed DS. Runtime filename buffery pri DS:62xx sa vynechávajú.
- Súvislá trojica `PUSH konštantný string`, `PUSH formát`, presný FAR CALL 0FBA:000C. Formát musí mať práve jedno percento a konverziu `%s`, bez ďalších konverzií. Tým sa neinterpretuje číselný `%d` argument ako string pointer.

Skript overuje pôvodné bajty, CS:IP, fyzickú susednosť, dĺžku/platnosť nezávislého dekódovania, presné FAR call bytes a skutočný NUL/ASCII obsah. Nevyužíva iba náhodnú zhodu konštanty s tlačiteľnou oblasťou.

Objekty zahŕňajú samostatné kópie `snd.dat`, `uif.dat`, `game.pal`, `debug.txt`, `nite3d.bsf` a identifikátory `Read_image()`, `Read_img_sequence()`, `Read_images()`, `Text_read()` použité v diagnostike nedostatku pamäte. Úplné adresy, texty, roly, formáty a call sites sú v `pass1_io_argument_strings/argument_references.csv`, presné hranice/SHA v `data_fields.csv`.

Tieto názvy potvrdzujú počiatočné argumentové objekty, nie existenciu či obsah konkrétnych asset súborov alebo úspešný prirodzený I/O. Zdedený DS a kompletné printf/vararg kontrakty zostávajú otvorené. Pri iných konverziách alebo nepriamom zostavení argumentu sa tento vzor automaticky nepoužíva.

## Reprodukcia a metriky

`audit_pass1_io_argument_strings.py IMAGE INVENTORY DECODER_DIR OUT` vytvára source-pinned polia a 24 xrefs. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_error_formats/noncode_intervals.csv`. Centrálna dátová únia overuje a odpočítava prekryvy.

Z 242 B bolo **72 B už PARTIAL**. Nových **170 B** pochádza z CLASSIFIED ONLY. Aktuálne **PARTIAL 53 618 B, CLASSIFIED ONLY 3 633 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 53 448 / 3 803 / 44 / 0 B. Netypované relokačné PARTIAL bajty zostávajú 2 B. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: názvy pri skutočnom open a error print, DS, uložené handles a dynamické filename buffery. Ďalší krok: zostávajúce formátové/zdrojové reťazce a statické tabuľky; neznámy buffer sa nepovažuje za file-backed dáta podľa konštantného offseta.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 353 polí/40 zdrojov; I/O argument strings | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | constant open arguments and single %s triples | writeri/lifetime | pointer watchpointy |
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

