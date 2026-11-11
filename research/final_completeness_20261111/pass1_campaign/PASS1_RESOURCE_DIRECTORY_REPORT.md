# PASS1: 32-položkový resource adresár

SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Nový rozsah **1BDB:0000..00C0**, obraz **[1BDB0,1BE70)**, obsahuje počiatočne 192 nulových bajtov. Typ je nominálny adresár 32 položiek po 6 B; status PARTIAL. V každej položke je WORD dĺžka a DWORD súborový offset, oba little endian.

## Dôkazy

Loader `0277:1766`, obraz 3ED6..3F4B, pri nenulovom BYTE DS:0678 najprv vynuluje tento flag, otvorí súbor a číta presne C0h bajtov do relokovaného FAR pointera 1BDB:0000. Návratový počet porovná s C0h; pri nezhode volá game error helper. Následne alebo pri už nulovom flagu počíta index*6 a vráti DX:AX = (load+1BDB):offset. Segmentové WORDy 3F0D a 3F46 sú skutočné EXEPACK relokácie. Index sa lokálne nekontroluje.

Spotrebiteľ `0277:196C`, obraz 40DC..4161, načíta pointer cez tento accessor, použije DWORD [record+2] pri seek s origin=0 a WORD [record] ako počet bajtov pre FAR DOS read. Porovná skutočný počet s WORD dĺžkou a súbor zatvorí. Konkrétny cieľový pointer je argument callera; veľkosť cieľovej alokácie táto rutina nekontroluje. Seek výsledok sa pred read explicitne netestuje.

```text
directory_entry(index):
    if initialize_flag:
        initialize_flag = 0
        read_exact_or_error(directory_file, 1bdb:0000, 192)
    return 1bdb:((index * 6) & 0xffff)

read_resource(index, destination):
    file = open_resource_file()
    entry = directory_entry(index)
    seek(file, entry.dword2, 0)
    actual = read(file, destination, entry.word0)
    if actual != entry.word0: error_helper(...)
    close(file)
```

Počet 32 vyplýva z pevného read 192 B a kroku 6, nie z medzery medzi segmentmi. Runtime obsah adresára, prirodzené indexy a non-return error helpera zostávajú otvorené. Nulovanie init flagu pred I/O môže byť významné pri zlyhaní; bežná error cesta žiada ukončenie, jej globálny kontrakt ešte nie je uzavretý.

## Reprodukcia a pokrytie

`audit_pass1_resource_directory.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa aj `relocations.csv` vedľa IMAGE. Overuje identitu, relokácie, rozhodujúce bajty, nulový počiatočný objekt, intervalové SHA a nezávislé dekódovanie loadera i spotrebiteľa. Výstupy sú v `pass1_resource_directory/`.

Pribudlo **192 B PARTIAL z UNKNOWN**. Aktuálna mapa: **PARTIAL 35 595 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 12 478 B, DEEP VERIFIED 0 B**. Súčet je 57 295 B. Predchádzajúca mapa mala PARTIAL 35 403 B a UNKNOWN 12 670 B.

Samostatný `verify_pass1_partition.py IMAGE MAP_CSV OUT_JSON` nezávisle overil presné členstvo všetkých bajtov v dvoch pôvodných NON-CODE intervaloch, bez dier a prekryvov, dĺžky a SHA každého výsledného intervalu. Táto kontrola dokazuje integritu partition, nie sémantickú správnosť všetkých klasifikácií.

DOSBox-X plán: zaznamenať skutočný adresárový súbor, prirodzené indexy 0..31 a prípadné odľahlé indexy, read count, seek CF a cieľové rozsahy. Ďalší statický krok: calleri accessorov a veľkosť blokov segmentu 20B9h. Originálny runtime ani nový replay sa v tejto dávke nespustil.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | 32 resource records: WORD size + DWORD offset | formát a bounds | directory callers |
| Dátové typy a konštanty | 95 % | N/A | 192 B directory PARTIAL | runtime entries | directory file |
| Tabuľky a ukazovatele | 93 % | N/A | relocated directory pointer | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | directory loader and consumer | prirodzená dosiahnuteľnosť | index and read trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
