# PASS1: file-backed názvy súborov a I/O diagnostika

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. **15 samostatných NUL ASCII objektov, 204 B**, má konkrétne NEAR DS argumenty v game I/O cestách. Zhodné texty na rôznych adresách sa vedú ako samostatné objekty. Status PARTIAL.

| Skupina | DS offsety | Spotreba |
|---|---|---|
| Zvukový resource loader | 01AE,01B6,01BE,01D4,01DC | `snd.dat`, error filename argumenty a opening/reading formáty |
| UI adresár 32×6 | 0679,0681,0689,069F,06A7 | `uif.dat`, error filename argumenty a opening/reading formáty |
| UI resource čítanie | 06F2,06FA,0702,0718,0720 | ďalšie samostatné `uif.dat` a diagnostické objekty |

Otváracie cesty 2807/280A, 3EE9/3EEC a 40E5/40E8 vložia príslušný NEAR offset a volajú CRT **11EE:1C72**. Ten na 13B7B načíta DX zo SS:[BP+6], na 13B82 nastaví AH=3Dh a na 13B84 vykoná INT 21h. DS ostáva zdedený; konkrétny prirodzený DS a otvorenie fyzického súboru sa v tejto dávke nemerali.

Error cesty vkladajú NEAR pointer filename a formátu do už analyzovaného 0FBA:000C. Formáty sú `Error opening file %s` a `Error reading file %s`. Presné adresy, texty, NUL hranice a PUSH sites sú v `pass1_io_strings/text_references.csv`; SHA a typy v `data_fields.csv`.

Tým sa dá konkrétne prepojiť skôr doložený loader 1D0F:0000 s cestou `snd.dat` a 192-bajtový adresár/ďalšie UI resource čítanie s `uif.dat`. Nepotvrdzuje sa tým úplný formát súborov ani úspešný prirodzený read. Uvedené názvy sú počiatočné statické argumenty, nie náhrada za hash reálnych assetov.

## Reprodukcia a pokrytie

`audit_pass1_io_strings.py IMAGE DECODER_DIR OUT` overuje SHA, 15 konkrétnych PUSH opcode/offset párov, skutočné NUL terminátory a ASCII obsah, priame open call sites a DOS open primitív. Nezávisle dekóduje pointer argumenty a primitívny úsek. `promote_pass1_fields.py` používa predchádzajúcu mapu `pass1_calendar/noncode_intervals.csv`. Výstupy sú v `pass1_io_strings/`.

Všetkých **204 B** prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **PARTIAL 50 873 B, CLASSIFIED ONLY 6 378 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 50 669 / 6 582 / 44 / 0 B. Netypované relokačné PARTIAL bajty zostávajú 2 B. Nový prirodzený runtime ani replay sa nevykonal.

DOSBox-X plán: reálne DS:DX názvy, open CF/AX a file handles, read/seek výsledky a error cesty. Ďalší krok: ďalšie reťazce v začiatku DS, rozlíšenie CRT vs game data a presné asset identity pri prirodzenom I/O.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 224 polí/37 zdrojov; 15 I/O strings | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | NEAR filename arguments and DOS open path | writeri/lifetime | pointer watchpointy |
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

