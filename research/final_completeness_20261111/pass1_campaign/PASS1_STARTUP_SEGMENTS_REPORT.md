# PASS1 — startup DS/SS a skutočné hranice súborových dát

11. 11. 2026. Prvá dávka priamo nad obnovenými57295 B PASS320 NON-CODE. **CLASSIFIED ONLY** znamená v tejto dávke nové štrukturálne fakty, nie uzavreté jednotlivé dátové typy. DEEP VERIFIED0 B, runtime testy0.

## Segmentový dôkaz

Na image11F05 je `MOV DI,2771h`. Jeho immediate WORD na11F06 patrí medzi1670 overených EXEPACK relocation miest; pôvodné slovo2771h sedí s kanonickými bajtmi aj relocation CSV. Preto pri relokačnom load segmenteL ide o hodnotuL+2771h, nie o absolútny fyzický segment2771h za všetkých okolností.

Na normálnej startup ceste sa na11F18 vykoná `MOV SS,DI`. Neskôr `PUSH SS/POP ES` na11F82..11F83 a po nulovaní `PUSH SS/POP DS` na11F91..11F92. V nerelokovaných image súradniciach je teda predvolená dátová báza **27710h**. Tento dôkaz nie je globálnym tvrdením, že každá funkcia vždy zachováva DS; externé volania a alternatívne/error vetvy zostávajú samostatným kontraktom.

Pred zmenou SS jeCLI, SP sa upraví oE02Eh a nasledujeSTI. Carry z tejto stack úpravy riadi error vetvu. Táto dávka nezatvára celý memory-allocation/stack kontrakt; pre dátové rozdelenie používa explicitne normálnu vetvu pokračujúcu k nulovaniu.

## CRT nulovanie je mimo pôvodného NON-CODE menovateľa

Kód nastaví ES=SS, CLD, DI=2650h, CX=E030h-DI, AX=0 a vykoná REP STOSB. Presný nulovaný interval:

```text
ES:2650h .. ES:E030h     end-exclusive
image-equivalent 29D60h .. 35740h
length B9E0h = 47584 B
```

Začiatok29D60h je **presne koniec171360 B kanonického súborového obrazu**. Tieto runtime nula-inicializované bajty preto nie sú súčasťou57 295 auditovaných file-backed NON-CODE bajtov. Nie je prípustné nimi odôvodniť označenie celého historického DGROUP intervalu akoBSS ani pripočítať ich do súborového menovateľa.

Použitá súradnica je po odčítaní spoločného load základu; pri runtime treba dosadiťL a overiť reálny adresný model. Nulovanie sa v tejto dávke nevykonávalo v DOSBox-X.

## Nová úplná štrukturálna partition PASS1

| Image end-exclusive | Bajty | Nový stav | Doložená vlastnosť |
|---|---:|---|---|
| 11EE7h..11EF8h | 17 | CLASSIFIED ONLY | všetky bajty0; pred CRT vstupom; padding stále nepotvrdený |
| 1BDA2h..27710h | 47470 | UNKNOWN | súborová oblasť pred doloženou default DS bázou; konkrétne objekty neznáme |
| 27710h..29D60h | 9808 | CLASSIFIED ONLY | súborom podložený default-DS prefix, offsety0000h..2650h |

Súčet57295 B. Historický ownerDGROUP bol príliš hrubý na automatické použitie ako segmentová báza. Tento názov sa zachováva ako pôvodná evidencia, nová mapa ho nenahrádza domnienkou, že všetkých57278 B používa rovnaký default DS offsetový priestor.

Ani CLASSIFIED ONLY rozsah ešte neznamená správne rozlíšenie reťazcov, WORD/DWORD polí, pointerov, paddingu, tabuliek či možných kódových fragmentov. **Sémanticky uzavreté typové bajty sú zatiaľ0.** Sedemnásť núl nemá dôkaz nepoužívania a nedostáva status padding ani DEEP VERIFIED.

## Reprodukovateľné artefakty

`audit_pass1_startup_segments.py IMAGE RELOCATIONS_CSV NONCODE_BASELINE_CSV ABSOLUTE_DECODER_DIRECTORY OUT_DIR`:

1. Overí identitu171360 B obrazu a oba pôvodné NON-CODE range SHA.
2. Kontroluje kritické startup bajty a konkrétnu relocation položku.
3. Nezávisle dekóduje startup okno11EF8h..11FC5h s presnými CS:IP adresami.
4. Vytvorí celú trojintervalovú PASS1 partition s range SHA, počtami núl a oddeleným sémantickým stavom.

`pass1_startup_segments/noncode_structural_map.csv` a `.json`, `startup_instructions.csv` a `summary.json` zachovávajú všetky hranice a hashe vstupov. Centrálny doterajší PARTIAL code/data katalóg sa touto štrukturálnou vrstvou nenafukuje; jeho prienik s NON-CODE zostáva0 B. Nové fakty sa vykazujú osobitne.

## Pokrytie a ďalší krok

Nová PASS1 štrukturálna evidencia: CLASSIFIED ONLY9825 B, UNKNOWN47470 B, PARTIAL0 B, DEEP VERIFIED0 B. Tento pomer nie je percentom sémantickej úplnosti. Štrukturálne známu polohu nemožno zameniť za uzavretý dátový objekt.

Nasleduje presný inventár initialized default-DS polí/reťazcov a validácia DS kontextu ich callerov. Pre47470 B prefix treba sledovať FAR segmentové pointery a relokácie; neprekladať jeho offsety voči defaultDS tak, ako keby boli nezáporné near premenné. Pre17 B interval preveriť všetky adresné referencie vrátane vypočítaných a susedné segmentové hranice. Percentá13 oblastí zostávajú N/A; blokátor ledgeru už neplatí.
