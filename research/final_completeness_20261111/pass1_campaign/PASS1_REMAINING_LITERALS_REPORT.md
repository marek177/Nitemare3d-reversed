# PASS1: zvyšné priamo spotrebované textové skupiny

Dávka typuje **254 B v 37 poliach: 36 NUL reťazcov a jeden mutable BYTE**. Ide o PARTIAL statické dôkazy. Tlač, shell command, súborové načítanie, formatter ani UI sa nevykonávajú; žiadny externý program alebo tlačiareň sa nepoužili.

## Vstupy a metóda

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. `audit_pass1_remaining_literals.py IMAGE INVENTORY DECODER OUT` overuje identity, presné NUL hranice, príslušné PUSH/MOV immediate každého textu a 464 vybraných pôvodných kontextových inštrukcií nezávislým dekóderom. Mapovanie near offsetov používa kanonické DS=2771h; prirodzené DS/SS všetkých callerov zostávajú otvorené.

`text_catalog.csv` obsahuje presný text, adresy a referenciu všetkých 36 reťazcov. `data_fields.csv` ich presné intervaly, dĺžky a SHA. `instruction_contexts.csv` zachováva konkrétne nadväzujúce použitie; nie sú to celé funkcie ani kompletné CFG.

## Skupiny a presné hranice

| Skupina | Image rozsah, koniec exclusive | Polia / dôkaz |
|---|---|---|
| Order UI | [294F1,2953D) | 3 NUL texty, 76 B: multiline poďakovanie, `order.txt`, `copy %s prn` |
| Slot/číselné formáty | [293E5,29417) | 9 NUL polí, 50 B: štyri `%d`, `%lu`, dve `_`, prázdny slot, `%i` |
| Resource mená | [28D73,28DA2) | 5 NUL polí, 47 B: `n3d.exe`, `map.1`, tri samostatné `nite3d.bsf` |
| Config/startup texty | [281AF,281D1) | 10 NUL polí, 34 B: `windir`, `%s` a osem numerických formátov |
| HUD texty | [28B2D,28B4D) | 7 NUL polí, 32 B: `%d : %d`, `%lu`, `%d%%`, tri `%d`, `%d,%d` |
| HUD initial flag | [28B2C,28B2D) | mutable BYTE initial 1; test 083D:05D8 a nulovanie 05E1 |
| Ending filename/mode | [28CFB,28D09) | 2 NUL polia, 14 B: `ending.fli`, `rb` |

Samostatné nulové BYTE [281D1,281D2) a [28B4D,28B4E) sa nepromujú na padding. Označenie resource mena ani suffix automaticky neuzatvára vnútorný formát assetu.

## Konkrétne konzumenty

Order cesta v 0D29:1518..154F odovzdáva DS FAR poďakovanie do lokálnej 052E, potom skladá SS buffer cez CRT sprintf 278C z formátu `copy %s prn` a argumentu `order.txt`. Výsledok odovzdá CRT 38E6. Predchádzajúca CRT analýza ukazuje system-like spracovanie COMSPEC; táto dávka potvrdzuje len statické prepojenie volaní, nie prirodzenú aktiváciu alebo úspešnú tlač.

Slot formáty sa používajú v konkrétnych sprintf/parse konzumentoch 0D29:0A95,0AC8,0AFC,0B2E,0B64,0C20,0C52,1188. Dve underscore polia zostávajú samostatné. Prázdny slot text na 293F9 sa v 0F76 načíta do DI; nasleduje ES=DS, prechod DS na segment porovnávaného record textu, SCASB a CMPSB. Je to porovnávací konzument, nie ďalšia automaticky predpokladaná kópia 27 B. Celé triedenie/slot UI zostáva otvorené.

083D:2A56/2A6E odovzdávajú `n3d.exe` a `map.1` lokálnej 28EE. Tá používa `rb` na file open CRT 06E6. Tri výskyty `nite3d.bsf` z 2AA3/2AB1/2ABF sa spájajú do spoločného volania 0277:1B02 s odlišnými dynamickými pointermi/WORD argumentmi. Tieto tri polia sa nezlučujú a nereinterpretujú ako jeden spoločný pointer bez dôkazu.

`ending.fli` má osobitné volanie 0430:0382 v 083D:28DB; pripísanie kompletnej FLI sémantiky by vyžadovalo audit tohto callee a assetu. `rb` je konkrétny open-mode literal pre inú lokálnu resource cestu. Oba majú nezávislé referencie.

`windir` sa v 0476:0342 odovzdá pôvodnému getenv 248A. Nenulový AX vedie k nulovaniu 3CCF a nastaveniu WORD 3CC2=18 v tomto caller kontexte. Samotná prítomnosť environment key nedokazuje konkrétny OS alebo skutočnú hostiteľskú konfiguráciu. Config numerické formáty a HUD formáty majú presné call kontexty v CSV; názvy metrikám sa bez writer auditu nepridávajú. V `%d%%` druhé `%%` znamená literal percent, nie ďalší numerický argument.

## Meranie

254 B CLASSIFIED ONLY → PARTIAL. Mapa: **56727 B PARTIAL, 524 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 837 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `95b47b5ebb18915b2615e70e0175574b6b8949dbf15dcf03584283d3fae27a21`. Partition integrita nie je dôkaz sémantickej úplnosti.

Bounded katalóg zostáva 90 funkčných rozsahov, 3235 inštrukcií / 8125 B; lokálne kontexty sa nepridávajú ako celé funkcie. Typované dáta celého obrazu 57613 B; historického NON-CODE 56725 B a 2 PARTIAL netypované relokačné bajty. Controlled replay zostáva 679723 plus osobitne 65548 smerových prefixových prípadov; nové prípady 0. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Počet textov ani ich bajty nenahrádzajú úplný audit konzumentov.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | konkrétne file-name konzumenty | asset vnútorné formáty | 1B02/0382 |
| Dátové typy a konštanty | 95 % | N/A | 254 B / 37 polí | zvyšných 524 CLASSIFIED | interval audit |
| Tabuľky a ukazovatele | 93 % | N/A | near text a FAR text odlíšené | runtime pointer invarianty | caller trace |
| Funkcie / ASM / CFG | 90 % | N/A | 464 vybraných inštrukcií | celé funkcie | file helper closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | windir vetva mení rate3CC2 | prirodzené prostredie | startup trace |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | HUD flag test/clear | celé redraw správanie | 05D2 closure |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | 7 konkrétnych HUD formátov | význam metrík | writer ledger |
| SAVE / LOAD | 92 % | N/A | slot text porovnávaný, nie kopírovaný | record layout | slot comparator |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | config/UI parity | Win literal match |

## Runtime testy na vykonanie

Zachytiť názvy/modes a pointer argumenty file helperov pri prirodzených resource cestách. Order tlačový command najprv sledovať bez vykonania shellu v izolovanom diagnostickom prostredí. Overiť `windir` rozhodovanie a rate zmenu pri pôvodnom DOS environment. Slot comparator, HUD flag a ich writerov sledovať oddelene. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
