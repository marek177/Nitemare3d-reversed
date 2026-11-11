# PASS1: šesť doložených CRT FAR hook slotov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Šesť samostatných DWORDov má konkrétnych nepriamych FAR CALL spotrebiteľov; status PARTIAL.

| DS slot | Obraz, end-exclusive | FAR CALL site |
|---|---|---|
| 2346 | 29A56..29A5A | 137A8 |
| 234A | 29A5A..29A5E | 133AD |
| 234E | 29A5E..29A62 | 137D4 |
| 2352 | 29A62..29A66 | 137C0 |
| 235A | 29A6A..29A6E | 1379E |
| 235E | 29A6E..29A72 | 1338F |

Všetky počiatočne obsahujú offset 02C0h a relokovaný segment 11EEh. Segmentové WORDy majú skutočné EXEPACK relokácie. Primitív v cieli 11EE:02C0, obraz 121A0, nastavuje AX=2 a skáče do startup/error vetvy; celý jeho ukončovací kontrakt sa touto dávkou neuzatvára. Počiatočný cieľ nie je dôkazom všetkých prirodzených runtime cieľov.

Susedný slot **DS:2356**, obraz 29A66..29A6A, vyzerá rovnako, ale nemá v použitom inventári doložený priamy consumer. Nepreberá sa automaticky do nového typu. Samotná zhodná hodnota a pravidelný krok nestačia. Caller DS a aliasovaní writeri všetkých slotov zostávajú otvorení; chýbajúci priamy writer v inventári nedokazuje nemennosť.

## Reprodukcia a metriky

`audit_pass1_crt_hook_slots.py IMAGE INVENTORY DECODER_DIR OUT` nezávisle dekóduje a byte-pinuje šesť nepriamych FAR volaní s absolútnym DS slotom bez indexu, kontroluje CS:IP a relokácie. Výstupy `pass1_crt_hook_slots/data_fields.csv`, `hook_consumers.csv`, `summary.json` zachovávajú presné xrefs a SHA vstupov.

`promote_pass1_fields.py IMAGE PRIOR_MAP DATA_FIELDS OUT` vytvára mapu zo vstupnej `pass1_ui_strings/noncode_intervals.csv` a overených polí. Z 24 B bolo 12 segmentových bajtov už PARTIAL; iba **12 offsetových bajtov** prešlo z CLASSIFIED ONLY. Aktuálne **PARTIAL 48 734 B, CLASSIFIED ONLY 8 517 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B.

Centrálny typový katalóg má 123 polí z 25 zdrojov, typovanú úniu 49 498 B a prienik NON-CODE 48 650 B. Relokačné PARTIAL bajty bez určenej dátovej roly klesli z 96 na **84 B**. Nový prirodzený runtime/replay sa nevykonal.

DOSBox-X plán: watchpointy na sloty, runtime FAR ciele, prirodzený DS a návraty z hookov. Ďalší krok: ostatné callbackové/štruktúrne pointery a nepoužitý-looking slot 2356, bez záveru o jeho nevyužití iba podľa inventára.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 123 polí/25 zdrojov; 24 B hook slots | 84 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 6 FAR hook slots and call sites | writeri/lifetime | pointer watchpointy |
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

