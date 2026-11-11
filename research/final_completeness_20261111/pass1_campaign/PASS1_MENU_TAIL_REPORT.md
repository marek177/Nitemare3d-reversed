# PASS1: posledné štyri počiatočné UI polia segmentu 20B9h

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Rozsah **[21E0E,21FD0)** má 450 B, 21 nenulových 18-bajtových záznamov a štyri nulové 18-bajtové sentinely. Status PARTIAL.

| FAR báza | Obrazový začiatok | Počiatočné položky | Sentinel, end-exclusive | Nový xref |
|---|---|---:|---|---|
| 20B9:127E | 21E0E | 6 | 21E7A..21E8C | F343 nastaví AX=127E, CX=20B9 a DS=CX |
| 20B9:12FC | 21E8C | 10 | 21F40..21F52 | EE1B..EE22 FAR argument do 0D29:1946 |
| 20B9:13C2 | 21F52 | 3 | 21F88..21F9A | EEC9..EED0 FAR argument do 0D29:1946 |
| 20B9:140A | 21F9A | 2 | 21FBE..21FD0 | F07D..F084 FAR argument do 0D29:1946 |

Prvé pole používa osobitná vetva s explicitnou bázou; celý jej spotrebiteľský kontrakt sa nepreberá automaticky z ostatných troch. Typová interpretácia je PARTIAL podľa počiatočného kroku, 6 FAR pointer polí a explicitnej bázy. Ostatné tri majú priamy dôkaz rovnakého generického UI spotrebiteľa ako predchádzajúca dávka: BYTE +0 sentinel, krok 12h, DWORD +0Eh a súradnicové WORDy +0Ah/+0Ch. Všetkých 21 počiatočných segmentových WORDov +10h má hodnotu 2771h a skutočnú EXEPACK relokáciu. Počiatočné nulové sentinely sú byte-pinned; ich runtime nemennosť sa netvrdí.

Predchádzajúca analýza ukázala, že caller 12FCh vie zapisovať nulový prvý BYTE dynamicky podľa počtu položiek. Preto počiatočných desať záznamov predstavuje file-backed layout, nie dokázaný počet položiek pri každom zobrazení. Význam všetkých polí, textov, callbackov a runtime hraníc je otvorený. Callbacková oblasť pred 21E0Eh sa touto dávkou nepreznačuje.

## Reprodukcia a meranie

`audit_pass1_menu_tail.py IMAGE PRIOR_MAP DECODER_DIR OUT` vyžaduje `relocations.csv` vedľa IMAGE. Kontroluje SHA, explicitné bázy/caller konštanty, spotrebiteľský krok, všetkých 21 relokovaných FAR polí, štyri nulové sentinely a intervalové SHA. Dekóduje päť ohraničených okien. Výstupy `pass1_menu_tail/` obsahujú 25 slotov, ASM a CSV/JSON mapy.

Zo 450 B bolo 42 B segmentových relokácií už PARTIAL. Nových **408 B** pochádza z UNKNOWN. Aktuálne **PARTIAL 47 383 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 690 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 46 975 / 9 222 / 1 098 / 0 B. Nový runtime ani replay sa nevykonal.

DOSBox-X plán: sledovať dynamické ukončenie poľa 12FCh, DS vetvy 127Eh, textové pointery a mutácie sentinelov vo všetkých štyroch poliach. Ďalší krok: zvyšných 690 UNKNOWN bajtov vrátane callbackového regiónu; neznáme medzery sa neoznačujú padding iba podľa nulových bajtov.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | no new resource format evidence | formát a bounds | DS:3F64 producent |
| Dátové typy a konštanty | 95 % | N/A | 450 B UI records PARTIAL; net +408 | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 21 FAR fields; 4 initial sentinels | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | three direct callers and one explicit base | prirodzená dosiahnuteľnosť | UI pointer trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI text pointer and coordinate reads | renderer contract | 0D29:0096 |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
