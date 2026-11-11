> SUPERSEDED BOUNDARY: PASS1_FLAGS_MAP_BOUNDARY_REPORT.md corrects the map extent to [2570E,2770E). This report is a historical scan-only snapshot.

# PASS1: počiatočné pole 64 × 64 buniek

SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Nominálna oblasť je **21FD:373F..573F**, obraz **[2570F,2770F)**, 8 192 B. Počiatočne je nulová. Ide o 4 096 buniek s krokom 2, v tejto ceste sa číta dolný BYTE. Význam druhého bajtu zostáva otvorený; plný WORD typ hodnoty sa netvrdí.

## Dôkaz z cyklov

Konštruktor od B7F8 (0AEA:0958) nastaví SI=0, lokálnu Y súradnicu na 0, DI=373Fh a lokálnu X súradnicu na 20h. Na B826 načíta ES z default DS:2568. Globál v obraze 29C78 má počiatočný segment 21FDh a skutočnú EXEPACK relokáciu. Na B82A číta BYTE ES:[DI]. Na B982 zvýši DI o 2, na B985 zvýši X o 40h a na B989 porovná X s 1020h. Presný dekódovaný cieľ v ASM výstupe je **0AEA:0986, obraz B826**. Rozsah X=20h..FE0h teda obsahuje presne 64 vstupov. Na B992 zvýši Y o 40h, porovná s 1000h a pri JL sa vráti na B818, kde sa X znovu nastaví na 20h. Y=0..FC0h má tiež 64 vstupov. DI sa pri začiatku ďalšieho riadka nenuluje.

Posledná čítaná bunka má offset `373Fh + 4095*2 = 573Dh`; jej nominálny dvojbajtový slot končí 573Fh. Adresový výpočet v týchto slučkách nepretečie cez 16 bitov. Súradnicové počítadlá sú odlišné od počtu objektov SI, ktorý rastie len pri vybraných bunkách.

```text
di = 0x373f
for y in range(0, 0x1000, 0x40):
    for x in range(0x20, 0x1020, 0x40):
        cell_low = BYTE[segment_global_2568:di]
        if flags[cell_low] & 1:
            construct_object_from_cell(...)
        di += 2
```

Objektový konštruktor má FAR helpery a error cestu, preto nemožno tvrdiť, že každý prirodzený beh prejde všetkých 4 096 buniek alebo zachová segmentový globál. Rozsah je počiatočný nominálny layout pod podmienkou nezmeneného globálu a riadneho návratu helperov. Dôkaz neuzatvára producenta mapových dát, druhý BYTE buniek ani SAVE/LOAD lifecycle. Samostatný posledný bajt pred DS bázou 27710h nie je automaticky padding.

## Neuzavretý kandidát 20B9h

Funkcia 0D29:016A počíta base segmentu 20B9h + zero-extended BYTE index * 4B0h a vytvára do nej FAR ukazovatele. Loader 0277:196C používa resource dĺžku pri DOS čítaní. Počet blokov a obmedzenie resource dĺžky na 1200 B však zatiaľ neboli dokázané. Táto oblasť ostáva UNKNOWN; krok 1200 sa nepoužil na odhad kapacity podľa susedných adries.

## Pokrytie a reprodukcia

`audit_pass1_map_grid.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa aj `relocations.csv` vedľa IMAGE. Kontroluje SHA obrazu, segmentový globál, bajty inicializácií a cyklov, počiatočné nuly, intervalové SHA a zachovanie menovateľa. Súvislé okno B7F8..B9A3 nezávisle dekóduje; neoznačuje ho za uzavretý kontrakt celej funkcie. Výstupy sú v `pass1_map_grid/`.

Predošlá mapa: PARTIAL 27 211 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 20 862 B. Aktuálna: **PARTIAL 35 403 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 12 670 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Všetkých 8 192 B pribudlo z UNKNOWN. Originálne runtime testy tejto dávky: 0, nové replay prípady: 0.

DOSBox-X plán: logovať DS:2568 a ES na B826, prvý a posledný DI, 64 návratov riadkov, helpery meniace mapu a rozdiely oboch bajtov buniek pred/po LOAD. Ďalší statický krok: producent mapy a indexové bounds pre segment 20B9h.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | 64x64 cell scan | formát a bounds | map producer |
| Dátové typy a konštanty | 95 % | N/A | 8 192 B grid PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | relocated grid segment global | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | nested loops and stride 2 | prirodzená dosiahnuteľnosť | grid runtime trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
