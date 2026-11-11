# PASS1: UI pole bezprostredne za bajtovou mriežkou

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Pole **1C08:1000**, obraz **[1D080,1D0EC)**, má päť počiatočných nenulových 18-bajtových položiek a nulový 18-bajtový sentinel `[1D0DA,1D0EC)`, spolu 108 B. Status PARTIAL.

Na 96B4..96BA caller explicitne vloží FAR pointer **1C08:1000** a volá `0D29:1946`. Už overený spotrebiteľ EBD6..EC38 používa nulový BYTE +0, krok 12h, DWORD textový pointer +0Eh a WORD súradnice +0Ah/+0Ch. Každá nenulová položka má segmentový WORD +10h = 2771h so skutočnou EXEPACK relokáciou. Tým sa odlišuje statické UI pole od predchádzajúcej pracovnej mriežky, ktorej explicitné nulovanie končí presne na offsete 1000h pri DF=0.

Počiatočné BYTE identifikátory sú 1Bh,1Ch,1Dh,1Eh,06h. Caller pred menu iteruje po týchto záznamoch a mení BYTE +5 podľa globálneho herného stavu. Preto ich nemožno považovať za nemenné konštanty. Význam identifikátorov, kompletná sémantika flagov, prirodzené mutácie a plný caller kontrakt zostávajú otvorené.

## Reprodukcia a meranie

`audit_pass1_grid_ui.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje identitu, presný FAR argument a volanie, päť segmentových relokácií textových pointerov, sentinel, spotrebiteľský krok a intervalové SHA. Výstupy `pass1_grid_ui/` obsahujú šesť slotov, ohraničené ASM a CSV/JSON mapu.

Z 108 B bolo 10 B segmentových relokácií už PARTIAL. Pribudlo **98 B z UNKNOWN**. Aktuálne **PARTIAL 47 965 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 108 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 47 867 / 9 222 / 206 / 0 B. Nový prirodzený runtime ani replay sa nevykonal.

## Zostávajúce UNKNOWN

Všetky zostávajúce bajty sú počiatočne nulové, ale to samo nedokazuje padding ani nevyužitie:

| Obrazový interval, end-exclusive | Dĺžka |
|---|---:|
| 1BDA2..1BDB0 | 14 |
| 1C070..1C080 | 16 |
| 1D0EC..1D0F0 | 4 |
| 20B88..20B90 | 8 |
| 256CE..2570F | 65 |
| 2770F..27710 | 1 |

Pôvodných 17 B pri 11EE7h má samostatný starší status CLASSIFIED ONLY; netreba ich zamieňať s týmito 108 B UNKNOWN. Zníženie UNKNOWN nevytvára dôkaz DEEP VERIFIED pre zvyšných 57 187 B: PARTIAL polia a CLASSIFIED ONLY dáta naďalej vyžadujú uzavretie sémantiky, writerov, segmentov a lifetime.

DOSBox-X plán: logovať prechody hranice mriežky/UI poľa, modifikácie +5 a sentinel, watchpoint na všetkých šiestich UNKNOWN intervaloch. Ďalší krok: dôkaz zarovnania alebo reálneho použitia zvyšných núl a konsolidácia nezávislých katalógov; nulový obsah sa nepromuje automaticky.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 108 B grid-adjacent UI records; net +98 | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 5 FAR text fields and sentinel | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | explicit 1C08:1000 UI call | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
