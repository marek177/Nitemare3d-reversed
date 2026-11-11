# PASS320 — pôvodná mapa obnovená a bajtovo overená

11. 11. 2026. Nový používateľom dodaný archív odstránil blokátor chýbajúcej intervalovej mapy. **Obnova identity mapy nie je dokončením jej sémantickej reanalýzy.**

## Identita a reprodukovateľnosť

Vstup `L:\_chrome\N3D_PASS300-322_VSETKY_ZIP.zip`,1701068 B, SHA-256 `d54e2b05a9e5fb6c5091f804a2af14404df6c86c03b9057739f45ce199e9b27d`. Obsahuje24 ZIP príloh vrátane dvoch odlišne pomenovaných PASS305. `import_pass300_322_ledgers.py` ich číta bez vykonania priložených generátorov alebo pokynov v dokumentoch.

Pre každý priložený CSV ledger overil všetky súvislé intervaly proti reálnemu kanonickému obrazu171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`: začiatok0, end-inclusive→end-exclusive prevod, dĺžku, intervalový SHA, bez medzier/prekryvov a presný koniec obrazu. Výsledky všetkých24 príloh sú v `pass320_recovered/archive_validations.json`, pôvodné CSV bajty v `source_ledgers/`. Nejde o dôkaz správnosti historických komentárov alebo dátových typov.

Pôvodný `deep_byte_ranges320.csv` má273055 B,1488 intervalov, SHA-256 **`8bf6afc62977ff68f6b7030288db48adb12cbba2d0157a14195f1708307830d2`**. Ledgery PASS319,320,321,322 sú navzájom bajtovo totožné. To teraz priamo potvrdzuje predtým iba zdrojovo doložené kopírovanie predchodcu; nepotvrdzuje každý historický analytický záver.

## Skutočný menovateľ PASS1

| Pôvodný status, zachovaný doslovne | Bajty |
|---|---:|
| PARTIAL | 72014 |
| ALIGNMENT | 84 |
| NOP | 597 |
| EMBEDDED_TABLE | 752 |
| NON-CODE PROVISIONAL | **57295** |
| EXTERNAL CLASSIFIED | 40618 |

Súčet171360 B, historický DEEP VERIFIED0 B. Počet1488 sa týka **všetkých** intervalov, nie1488 NON-CODE intervalov. NON-CODE PROVISIONAL sú presne tieto dva:

| Pôvodný riadok, index od0 | Image end-exclusive | Bajty | Pôvodný owner / proof |
|---:|---|---:|---|
| 1484 | **11EE7h..11EF8h** | 17 | Padding / historical padding |
| 1487 | **1BDA2h..29D60h** | 57278 | DGROUP / historical data/table/state classification |

Prvý interval obsahuje17 nulových bajtov. To samo osebe nepotvrdzuje padding; môže ísť o iný nula-inicializovaný stav, kým sa nevylúčia referencie a životnosť. Druhý obsahuje48215 nulových a9063 nenulových bajtov. Historické označenie DGROUP **nepreukazuje konkrétny runtime DS base** ani jednotný dátový typ celého rozsahu. Segmentový kontext treba rekonštruovať zo startup/relokácií, nie odvodiť iba z owner názvu.

## Prienik doterajšej kampane

Presný intervalový join s aktuálnou centrálnou mapou ukázal:

- z2557 lokálne dekódovaných kódových bajtov: **0 B** v pôvodnom NON-CODE;
- z848 lokálne posúdených dátových bajtov: **0 B** v pôvodnom NON-CODE;
- celých57295 B pôvodného NON-CODE zostáva v tejto kampani bez novej sémantickej analýzy.

Doterajší WORX/audio audit zostáva použiteľný pre externé rutiny, neznáme funkcie a lokálnu parity, ale **nepredstavuje pokrok v menovateli57295 B**. Nový28 B IRQ handler takisto neleží v týchto dvoch intervaloch. Predchádzajúce reporty s chýbajúcou mapou sú historické snímky; toto je aktuálna korekcia ich blokátora a neznámeho prieniku.

`campaign_catalog` teraz explicitne rozlišuje `NON_CODE_BASELINE` a `OUTSIDE_NON_CODE_BASELINE`. Po rozdelení na obnovených hraniciach má96 intervalov, rovnaké bajtové súčty. Funkčný katalóg uvádza `NO_INSTRUCTION_BYTES_IN_NONCODE` pri všetkých32 doterajších rozsahoch. Import hraníc neprepisuje pôvodnú ani novú sémantickú klasifikáciu.

## Výstupy

- `pass320_recovered/noncode_baseline.csv` a `.json`: presné dva intervaly, source ledger hash a pôvodné tvrdenia; nový reanalysis status UNKNOWN.
- `campaign_intersections.csv` a `.json`: reprodukovateľný join k aktuálnej centrálnej mape.
- `archive_validations.json`: identity24 ZIP/CSV a výsledky intervalových kontrol.
- `summary.json`: súčty, identita zdrojov, totožnosť319–322 a explicitne neukončená reanalýza.

Reprodukcia: `python import_pass300_322_ledgers.py SUPPLIED_ZIP CANONICAL_IMAGE CAMPAIGN_CSV OUT_DIR`; potom `independent_decode_and_catalog.py` načíta overené NON-CODE hranice a aktualizuje membership. Žiadny priložený build_pass skript nebol spustený.

## Najbližší konkrétny postup

PASS1 má teraz presný menovateľ a už nie je blokovaný dostupnosťou mapy. Začať17 B intervalom a rekonštrukciou startup DS/ES/SS; následne rozdeliť57278 B podľa preukázaných segmentových hraníc, inicializovaných polí, tabuliek, reťazcov, bufferov a referencií. Čisto nulový obsah nesmie dostať DEEP VERIFIED ani automatický typ padding/BSS.

Aktuálna nová reanalýza tohto menovateľa: DEEP VERIFIED0 B, PARTIAL0 B, CLASSIFIED ONLY0 B, UNKNOWN57295 B. To je stav tejto kampane, nie spätné vyhlásenie, že všetky predchádzajúce znalosti projektu sú nulové. Percentá13 sémantických oblastí zostávajú N/A bez ich vlastných úplných inventárov. Replay DSP handlera je rozpracovaný ďalší krok mimo priority; nevykonával sa počas importu.
