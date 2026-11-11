# PASS1: 60 odkazovaných UI reťazcov

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Nová dávka identifikuje **60 samostatných NUL-terminated ASCII objektov, 693 B**, všetky s konkrétnym počiatočným FAR poľom UI záznamu. Status PARTIAL. Zhodný text na rôznych adresách je samostatný objekt; bajtový súčet je únia presných hraníc vrátane terminátorov.

Príklady: `New game`, `Save game...`, `Restart at last save`, tri epizódy, tri obtiažnosti, Mouse/Joystick/Music/Sound FX, cheat nastavenia, Floor 1..10 a remote doors/cannons. Konkrétne adresy, úplné texty a SHA sú v `pass1_ui_strings/data_fields.csv`. Jednotlivé xrefs s adresou pointera a relokačného WORDu sú v `text_references.csv`.

## Dôkaz a rozsah tvrdenia

Vstupom je päť predtým analyzovaných skupín UI záznamov: `pass1_menu_records`, `pass1_menu_records_more`, `pass1_menu_tail`, `pass1_ui_callbacks`, `pass1_grid_ui`. Každé pole +0Eh sa číta ako DWORD, má segment 2771h na +10h so skutočnou EXEPACK relokáciou a offset do default DS file-backed dát. Výsledný rozsah končí skutočným nulovým bajtom; všetky predchádzajúce bajty sú ASCII 20h..7Eh. Táto dávka nevyhľadáva len voľné ASCII vzory bez referencie.

Generický UI spotrebiteľ číta textový DWORD +0Eh a odovzdáva ho render helperu, čo je doložené staršími ASM dávkami. Osobitná vetva poľa 127Eh má explicitnú bázu a rovnaký počiatočný layout; jej celý render kontrakt zostáva otvorený. Pointery sa môžu počas hry meniť. Počiatočný FAR reťazec a jeho hranice neznamenajú uzavretú prirodzenú dosiahnuteľnosť každej položky ani renderer parity. Dynamické SS texty z dvoch iných polí sa sem nezahŕňajú.

## Reprodukcia a meranie

`audit_pass1_ui_strings.py IMAGE PRIOR_MAP OUTPUTS_ROOT OUT` používa `relocations.csv` vedľa IMAGE a zdrojové slot CSV. Kontroluje SHA obrazu a každého predošlého intervalu, relokačné WORDy, FAR mapovanie, terminátory, hranice, ASCII obsah, neprítomnosť prekryvov textových objektov a presný menovateľ. Zdrojové CSV SHA sa uchovávajú pri xrefs. Výstupy `pass1_ui_strings/` obsahujú textové polia, referencie a CSV/JSON mapu.

Všetkých **693 B** prešlo z CLASSIFIED ONLY do PARTIAL. Predošlá mapa: PARTIAL 48 029 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 44 B. Aktuálna: **PARTIAL 48 722 B, CLASSIFIED ONLY 8 529 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Nový runtime ani replay sa nevykonal.

Centrálny katalóg bol rozšírený o texty a overený proti aktuálnej mape; sémantické uzavretie sa z počtu reťazcov nepočíta. DOSBox-X plán: sledovať prirodzené pointery pri menu a remote-control položkách, mutácie polí a skutočné renderované texty. Ďalší krok: zostávajúce CLASSIFIED ONLY reťazce a tabuľky s vykonateľnými xrefs, plus 120 relokačných bajtov bez dátovej roly.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 105 polí/23 zdrojov; 693 B textov | 120 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 60 textov s FAR xrefs | writeri/lifetime | pointer watchpointy |
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

