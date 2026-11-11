# PASS1: typovanie dvanástich segmentových globálov

SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Dvanásť WORDov **DS:2556..256E**, obraz **[29C66,29C7E)**, má teraz konkrétny typ segmentového globálu. Všetky už boli PARTIAL podľa loader relokácie; byte status sa nemení.

| DS offset | Počiatočný segment | Priame MOV do ES/DS v inventári |
|---|---|---:|
| 2556 | 21FD | 6 |
| 2558 | 21FD | 4 |
| 255A | 21FD | 3 |
| 255C | 21FD | 1 |
| 255E | 21FD | 3 |
| 2560 | 1BE7 | 5 |
| 2562 | 21FD | 6 |
| 2564 | 1C08 | 7 |
| 2566 | 21FD | 2 |
| 2568 | 21FD | 3 |
| 256A | 20B9 | 11 |
| 256C | 21FD | 1 |

Spolu **52 spotrieb**. Každý WORD má skutočnú EXEPACK relokáciu; pri load segmente L je počiatočná hodnota `(initial+L)&FFFFh`. Nový dôkaz spočíva v priamych inštrukciách typu `MOV ES,WORD PTR DS:[offset]`, nie iba v blízkosti známej dátovej bázy. Segmentové globály sa nepovažujú automaticky za DWORD FAR pointery.

Reprodukčný skript byte-pinuje inštrukcie proti obrazu a nezávisle kontroluje ich dekódovanie, dĺžku, CS:IP mapovanie, register ES/DS a absolútny DS operand bez indexu či bázy. Caller DS je zdedený; zhodný literálny offset pri odlišnom DS by odkazoval inam. Inventár teda dokazuje konkrétne segmentové spotreby pod DS predpokladom, nie globálnu prirodzenú dosiahnuteľnosť alebo nemennosť. Nepriame, aliasované a mimoinventárové zápisy zostávajú otvorené.

## Artefakty a metrika

`audit_pass1_segment_globals.py IMAGE INVENTORY DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Výstupy `pass1_segment_globals/data_fields.csv`, `segment_consumers.csv`, `summary.json` uchovávajú 12 typov, 52 presných xrefs, SHA obrazu a inventára. Script sa úspešne vykonal.

Centrálny dátový katalóg zahŕňa ďalších **24 B**: typovaná únia v celom obraze **49 474 B**, prienik s NON-CODE **48 626 B**. PARTIAL bajty bez určenej dátovej roly klesli zo 120 na **96 B**, všetky stále ležia na relokačných sites. Katalóg má 117 polí z 24 zdrojov. Byte mapa zostáva **48 722 B PARTIAL, 8 529 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Runtime/replay prírastok je 0.

DOSBox-X plán: watchpointy na dvanásť globálov, prirodzený DS pri MOV spotrebách a zmeny po LOAD/inicializácii. Ďalší krok: zostávajúce relokované polia a callback pointery bez uzavretého typu. Výsledok nie je uzavretie všetkých segmentových kontraktov ani PASS1.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 117 polí/24 zdrojov; 24 B segmentov | 96 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 12 segment globals and 52 direct reads | writeri/lifetime | pointer watchpointy |
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

