# PASS1: nominálny priestor 350 × 28 bajtov

Obraz: SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Adresy obrazu sú nerelokované, konce intervalov exkluzívne. Nové zistenie je statické, status PARTIAL.

## Rozsah a dôkaz

Pole `21FD:0006..264E`, obraz `[21FD6,2461E)`, má nominálne 350 záznamov po 28 B, spolu 9 800 B. Celý rozsah má po rozbalení nulové bajty. Nulové dáta samotné neboli dôvodom určenia hraníc.

Konštruktor od `0AEA:0958` (obraz B7F8) vynuluje SI. B81D vypočíta `SI*1Ch`, B820 pridá 6. Pred zápisom B83B porovná offset s 264Eh; B840 pri menšom offsete preskočí chybové volanie. `(264Eh-6)/1Ch = 350` presne. B97D inkrementuje offset o 1Ch a B981 počet SI. B99F uloží SI do DS:6270. Báza producenta je ES z DS:2566 (B856); inicializačný WORD v obraze 29C76 je 21FDh a má skutočnú EXEPACK relokáciu. Susedný globál DS:2568 má rovnakú počiatočnú hodnotu, ale jeho neskoršie aliasovanie zostáva otvorené.

Volanie chyby `0FBA:000C` na B848 má zakódované pokračovanie B84D. Netriviálny non-return kontrakt zatiaľ nebol dokázaný. Preto nominálna kapacita nie je dôkazom, že žiadna runtime cesta nezapíše mimo poľa. Medzera za 264Eh až po ďalšiu známu tabuľku 3076h sa touto dávkou neklasifikuje.

Počítadlo DS:6270 pri predpoklade default DS 2771h zodpovedá obrazu 2D980h. Leží mimo súborového obrazu aj pôvodného NON-CODE menovateľa, v oblasti CRT nulovania. Nepočíta sa ako ďalší potvrdený bajt PASS1. Prirodzený DS konštruktora a všetci writeri globálov zostávajú otvorení.

## Pozorované zápisy polí

| Offset záznamu | Šírka | Pozorovaný zápis |
|---|---:|---|
| +0 | 1 | vstupný bajt mapového skenu |
| +1 | 1 | rozdiel vstupného bajtu a výsledku helpera |
| +2,+3 | 1 každý | nula |
| +5 | 1 | lookup bajt z DS tabuľky |
| +6 | 1 | ďalší lookup bajt z DS tabuľky |
| +7 | 1 | podmienečný index DS:6276 |
| +8 | 4 | nula |
| +0C,+0E | 2 každý | offset DI-1 a relokovaný segment 21FDh |
| +10,+12 | 2 každý | súradnice skenu s krokom 40h |
| +1A | 1 | nula |

Nezapísané polia, neskoršie zmeny, význam helperov a sémantika typov objektov nie sú uzavreté.

```text
count = 0
for each cell in the bounded map scan:
    if flags[cell] & 1:
        offset = 6 + count * 28
        if offset >= 0x264e: error_helper(...)  # return contract unresolved
        initialize_observed_fields(segment_global_2566:offset)
        call_helpers(...)
        count += 1
DS[0x6270] = count
```

## Meranie a reprodukcia

Predchádzajúca mapa: PARTIAL 1 984 B, CLASSIFIED ONLY 9 649 B, UNKNOWN 45 662 B. Nová mapa: **PARTIAL 11 784 B, CLASSIFIED ONLY 9 649 B, UNKNOWN 35 862 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Prírastok 9 800 B bol celý UNKNOWN. Ide o rozdelenie presného bajtového menovateľa, nie o percento sémantickej úplnosti.

`audit_pass1_records28.py IMAGE RELOCS PRIOR_MAP DECODER_DIR OUT` overuje identitu obrazu, rozhodujúce bajty, relokácie, rozsah, nuly, SHA predchádzajúcich intervalov a zachovanie súčtu. Dekóduje súvislé okno B7F8..B9A3 bez tvrdenia o uzavretí celej funkcie. Výstupy `pass1_records28/` obsahujú CSV/JSON intervaly, 350 slotov, dátový rozsah, ASM a súhrn. Centrálny code/data katalóg zatiaľ ostáva samostatnou staršou snímkou; tieto čísla sa s ním nesčítavajú.

DOSBox-X plán: sledovať DS/ES pri B856, zápisy DS:2566 a DS:6270, prvý a posledný platný slot, chybovú cestu pri počte 350 a prípadný návrat helpera. Porovnať pole pred/po LOAD a pri prechode úrovne. Runtime testy tejto dávky: 0. Ďalší krok: uzavrieť helper chyby a všetky zápisy do segmentového globálu pred tvrdením o bezpečnej kapacite.
