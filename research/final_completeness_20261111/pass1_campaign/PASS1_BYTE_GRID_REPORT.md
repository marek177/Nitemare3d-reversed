# PASS1: samostatná 4 096-bajtová pracovná mriežka

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Počiatočná nominálna oblasť **1C08:0000..1000**, obraz **[1C080,1D080)**, má 4 096 nulových bajtov. Typ: pracovné BYTE pole s riadkovým krokom 64, nominálne 64×64. Nejde o dvojbajtové bunky v segmente 21FDh z predchádzajúcej dávky.

## Rozsah a DS kontext

Na 9894..98A4 kód vynuluje AX, načíta ES z DS:2564, nastaví CX=1000h a DI=0, posunie CX doprava o 1 a vykoná REP STOSW. Globál DS:2564 v obraze 29C74 má hodnotu 1C08h a skutočnú EXEPACK relokáciu. Pri nezmenenom globále a DF=0 sa vykoná 2 048 WORD zápisov, presne 4 096 B od offsetu 0. CF po SHR je 0; REP STOSW ho nemení, takže JAE preskočí zvyškové STOSB. Rozsah sa teda neodvodzuje zo susednej sentinelovej tabuľky pri offsete 1000h.

**DF je vstupná podmienka:** tento úsek nemá CLD. Pri DF=1 sa WORD zápisy posúvajú späť a nevyčistia nominálny súvislý rozsah. Prirodzený DF všetkých prístupových ciest sa v tejto dávke neuzatvára. Rovnako sa netvrdí nemennosť globálu DS:2564.

Zápis jednej bunky na 987F..9891 načíta ES z rovnakého globálu a počíta BX = lokálne Y*64 + lokálne X. Na 988C uloží AL do BYTE ES:[BX]. V rozsahu 9B7A..9BE5 ďalší kód explicitne nastaví segment 1C08h a píše horizontálne s krokom SI+1 alebo vertikálne s krokom SI+40h. Vstupy lokálnych súradníc nemajú v týchto ohraničených oknách dokázaný platný rozsah; nominálna geometria nie je globálna ochrana pred prekročením poľa.

```text
clear_grid:                       # requires DF=0 and expected segment global
    ES = DS[0x2564]
    AX = 0; DI = 0; CX = 0x1000 / 2
    REP STOSW

put_cell(x, y, value):
    BYTE[segment_global_2564 : ((y*64+x) & 0xffff)] = value
```

Konkrétny herný význam hodnôt, producent mapového obsahu, runtime súradnice a SAVE/LOAD lifecycle sú otvorené. Súvislosť s mapovými/editačnými operáciami podporuje geometria zápisov; presnú sémantiku každej hodnoty neoznačujem za potvrdenú.

## Pokrytie a reprodukcia

`audit_pass1_byte_grid.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Overuje SHA obrazu, relokáciu globálu, bajty nulovania a adresových výpočtov, počiatočné nuly, intervalové SHA a presný menovateľ. Dekóduje tri ohraničené okná, bez tvrdenia o uzavretí celej funkcie 083D:143C. CSV/JSON výstupy sú v `pass1_byte_grid/`.

Nových **4 096 B PARTIAL** bolo UNKNOWN. Aktuálne **PARTIAL 43 291 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 4 782 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 39 195 / 9 222 / 8 878 / 0 B. Originálne runtime testy ani nový replay sa v tejto dávke nevykonali. Prijatý replay súčet predchádzajúcich dávok zostáva 2 603.

DOSBox-X plán: zachytiť DF a DS:2564 na vstupe nulovania, sledovať prvý/posledný zápis a všetky coordinate bounds pri prirodzených operáciách. Ďalší krok: zostávajúce UNKNOWN intervaly a sentinelové záznamy od 1C08:1000; ich koniec sa nebude určovať iba nulovým behom.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | BYTE grid, stride 64 | formát a bounds | grid producer |
| Dátové typy a konštanty | 95 % | N/A | 4 096 B grid PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | relocated grid global | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | REP STOSW and coordinate writes | DF and coordinate bounds | DF and write trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
