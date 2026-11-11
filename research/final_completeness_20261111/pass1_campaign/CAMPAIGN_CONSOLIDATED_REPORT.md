# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](DOS_IO_WRAPPERS_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) je citatelny, ale dostupna Linux distribucia pre prilozeny ELF nebola zistena. Prirodzene runtime testy zostavaju 0.

## Aktualne meranie PASS1

Mapa `pass1_episode_files/noncode_intervals.csv/json`: **54746 B PARTIAL, 2505 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 660 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `0e44930f5c325bf502bc9acc74d17397f92d895b2f9962eff75e4037da488907`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 48 |
| Nezavisle dekodovane instrukcie | 1691 |
| Instrukcne bajty | 4028 |
| Unia typovanych dat celeho obrazu | 55592 B |
| Ostatne katalogom neposudene bajty | 111740 B |
| Intervaly celeho obrazu | 385 |
| Typovane data v povodnom NON-CODE | 54744 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 7909 |
| Oddelene prefixove replay pripady | 65548 |
| Prirodzene runtime testy | 0 |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 404 poli z 49 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_episode_files DOS_IO_WRAPPERS_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Nove lokalne davky po publikovanom commite a43690cac60dea52020b557c733c239504ba9bf1 zatial nie su synchronizovane na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár jednotiek oblasti. Menovatele nie sú uzavreté, nové percentá sú N/A a predošlé hodnoty sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | wrapper vracia krátky počet bez retry | prirodzené čítanie | DOS capture |
| Dátové typy a konštanty | 95 % | N/A | handle/FAR buffer/count stack ABI | pointer bounds | caller domény |
| Tabuľky a ukazovatele | 93 % | N/A | DS:DX prenos a obnova DS | runtime segmenty | DOS stopa |
| Funkcie / ASM / CFG | 90 % | N/A | 50 B / 26 inštrukcií, 160 prípadov | interrupt kontrakt | skutočné chyby |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | I/O časovanie | prirodzené udalosti |
| DEMO a vstupy | 96 % | N/A | spoločný I/O wrapper kontrakt | DEMO parser | read caller ledger |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | spotrebitelia flagov |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | read/write error AX strata, CF zachovanie | reakcie callerov | každý krátky prenos/error |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | Win I/O ABI | Win import wrappery |

