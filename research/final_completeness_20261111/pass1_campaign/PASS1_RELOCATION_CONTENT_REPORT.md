# PASS1 — relokované WORDy a počiatočný obsah celých57295 B

11. 11. 2026. Nová úplná PASS1 mapa má252 intervalov. **PARTIAL** v tejto dávke znamená overený loader WORD kontrakt; neznamená uzavretý FAR pointer, funkčný objekt ani vylúčený kódový operand. DEEP VERIFIED0 B, runtime testy0.

## Relokačná evidencia

Zo1670 konkrétnych EXEPACK relokácií leží130 WORD miest v pôvodnom NON-CODE. Všetkých130 má overené pôvodné slovo, presné2 B hranice a range SHA oproti autentickému obrazu. Neexistuje prekryv týchto130 WORD polí.65 leží pred default DS bázou27710h a65 za ňou.

Každé miesto má doloženú transformáciu `(initial_WORD + load_segment) & FFFFh`. Preto dostáva typ `loader_relocated_WORD` a stavPARTIAL. Jeho úloha zostáva `data_or_code_operand_UNRESOLVED`. Samotný fakt relokácie nevylučuje dosiaľ nerozpoznaný kódový immediate v historicky NON-CODE oblasti.

V `relocated_words.csv` sa zachováva predchádzajúce WORD a kandidátsky FAR cieľ, ale **FAR interpretácia je pri všetkýchNOT_PROVEN**. Ak je predchádzajúce WORD takisto relokované, nie je prípustné automaticky skladať dva relokované segmentové WORDy na obyčajný offset:segment pointer. Zoznam obsahuje aj takéto susedné relokácie.

Najčastejšia počiatočná segmentová hodnota je2771h:105 zo130 polí. Zvyšné hodnoty smerujú do iných image segmentových báz, ale ani to bez spotrebiteľa neidentifikuje callback, segmentový register či tabuľkový pointer.

## Obsahový census bez zamieňania za typy

Oba pôvodné NON-CODE intervaly boli prečítané celé a rozdelené na1761 maximal zero/nonzero behov:

| Meranie | Bajty |
|---|---:|
| počiatočné nuly | 48232 |
| počiatočné nenulové bajty | 9063 |
| spolu | 57295 |

Najdlhšie nulové behy sú21FBEh..27718h (22362 B),1D0DAh..219A0h (18630 B),1BDA2h..1D080h (4830 B). Prvý dokonca prechádza cez default DS hranicu. Tieto behy preto nepredstavujú automaticky objekty, padding, BSS alebo nepoužívanú pamäť. Do plného typového uzavretia zostávajú referencie a životnosť.

`initial_content_runs.csv` zachováva všetkých1761 behov s hashmi. Obsahová vrstva máCLASSIFIED ONLY vlastnosť bytovej hodnoty, ale **nenahrádza** stavovú partition sémantickej/loader reanalýzy.

## ASCII vzory a relokačné hranice

Sken našiel327 maximal printable-ASCII+NUL vzorov,5539 B vrátane terminátorov. Všetky ležia v default-DS file prefixe, žiadny pred27710h. Dvadsať raw vzorov prekrýva relokované WORDy.

Príklad pri28410h má počiatočné ASCII `q'Red key`. Úvodné `q'` sú bajty71h27h, teda relokované segmentové WORD2771h. Nemajú sa automaticky považovať za textový prefix. Druhý sken používa známe relokačné WORDy ako **neprintable hranice**, nie ako umelo vložené NUL terminátory. Každý prijatý terminátor musí byť pôvodná skutočná nula mimo relokačného WORDu.

Výsledok tejto ohraničenej verzie je325 kandidátov /5493 B. Názvy sa nesmú zameniť za325 potvrdených runtime reťazcov; chýbajú konzumenti, pointerové vstupy, kódová stránka a životnosť. Oba inventáre zostávajú zachované ako `ascii_nul_patterns.csv` a `ascii_after_relocation_boundaries.csv`. Ich bajty sa nepripočítavajú znovu do loader WORD alebo structural status súčtov.

## Aktuálna PASS1 partition

| Stav | Predchádzajúca štrukturálna dávka | Aktuálny stav |
|---|---:|---:|
| DEEP VERIFIED | 0 B | 0 B |
| PARTIAL | 0 B | **260 B** |
| CLASSIFIED ONLY | 9825 B | 9695 B |
| UNKNOWN | 47470 B | 47340 B |
| spolu | 57295 B | 57295 B |

Metodika:260 jedinečných loader WORD bajtov nahradí130 predtýmUNKNOWN a130CLASSIFIED ONLY bajtov. Ostatné statusy sa nemenia. Nijaké percento13 sémantických oblastí sa z toho neodvodzuje. Generovanie textového vzoru ani prečítanie nulového rozsahu nie je uzavretie jeho skutočného dátového typu.

`noncode_intervals.csv` a `.json` tvoria úplnú252-intervalovú partition pôvodných dvoch NON-CODE rozsahov s end-exclusive hranicami, hashmi, pôvodným baseline ID a konkrétnym relocation field ID. Súčet a neprítomnosť dvojitého započítania sú skriptovo overené. Centrálny lokálny code/data katalóg s848 B dát zostáva osobitný; tieto260 B sa ešte nasilu neoznačilo za obyčajné DATA, keďže kódový operand nie je globálne vylúčený.

## Reprodukcia a nasledujúci krok

`python audit_pass1_relocation_content.py IMAGE RELOCATIONS_CSV NONCODE_BASELINE_CSV STRUCTURAL_MAP_CSV OUT_DIR` kontroluje SHA obrazu, pôvodných rozsahov a1670-entry relocation zdroja. Výstupy sú v `pass1_relocation_content/`; summary obsahuje hashe všetkých vstupov.

Nasleduje spotrebiteľská validácia konkrétneho FAR/string kandidáta bez relokovaného predchádzajúceho WORDu a inventár spojených tabuliek pred defaultDS. Nulové oblasti treba následne viazať na FAR segmentové vstupy a konkrétne dĺžky bufferov; veľkosť nulového behu sa nesmie prebrať ako ich veľkosť.
