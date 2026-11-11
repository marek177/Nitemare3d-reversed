# Win110: relokačne doložené volania trigonometrických helperov

## Výsledok a hranice dôkazu

V reálnom Win1.10 EXE je doložených šesť priamych FAR volaní štyroch už porovnaných helperov. Každá hrana má overené bajty inštrukcie, hranicu v nezávisle predekódovanom inventári a NE relokáciu selector WORDu. Ide o statický výsledok PARTIAL. Prirodzená dosiahnuteľnosť, runtime DS a úplnosť nepriamych volaní zostávajú otvorené. Nové DEEP VERIFIED bajty: 0; prirodzené runtime testy: 0.

Adresy nižšie sú NE segment:offset, hexadecimálne; číslo segmentu nie je runtime selector.

| Volanie | Cieľ | Helper | Relokovaný WORD |
|---|---|---|---|
| 3:E56B | 3:ECAC | sin | 3:E56E |
| 3:E57A | 3:ECF8 | cos | 3:E57D |
| 3:EE85 | 3:ED44 | tangentová magnitúda | 3:EE88 |
| 3:EEDF | 3:ED44 | tangentová magnitúda | 3:EEE2 |
| 3:EF2F | 3:ED44 | tangentová magnitúda | 3:EF32 |
| 3:6DC4 | 3:ED90 | angle lookup | 3:6DC7 |

Relokácie majú source type 2, šírku 2 a interný cieľ segment 3. Pôvodné WORDy v selector poliach FAR CALL obsahujú články fixup reťazca. Nesmú sa interpretovať ako načítané runtime selectory. V overenom inventári sa nenašiel priamy NEAR CALL na tieto štyri vstupy; tento výsledok nevylučuje ďalšie hranice ani nepriame volania.

## Dátové väzby callerov

Na 3:E567 sa pushuje WORD DS:4BEA pre sin. Caller po návrate odstráni 2 bajty argumentu a uloží AX na DS:4C46 (3:E573). Na 3:E576 pushuje rovnaký WORD pre cos; po odstránení argumentu uloží AX na DS:4C48 (3:E582). Toto dokazuje spoločný zdroj argumentu a dve výsledkové lokácie pri platnom DS, nie ich prirodzenú hodnotu či platný rozsah uhla.

Tri tangentové call sites odovzdávajú po jednom WORDe: DS:4BEA, potom výsledok 16-bitového odčítania 005Ah od DS:4BEA a výsledok odčítania 010Eh. Každý caller odstráni 2 bajty a následne vykoná CWD nad AX. Bez uzavretia predchádzajúcich vetiev sa tým nedokazuje, že argument vždy leží v podporovanom intervale helpera.

Wrapper na 3:6DBC vykoná ENTER 4,0; na 3:6DC0 pushne DWORD SS:[BP+6], teda dvojicu WORD argumentov pre angle lookup. Po FAR CALL odstráni 4 bajty, uloží AX do SS:[BP-2] a odčíta DS:4BEA. Rozsah oboch vstupov a význam následného rozdielu zostávajú otvorené.

## Reprodukcia

Skript `audit_win110_trig_callers.py EXE ASM FIXUPS_DIR DECODER_DIR OUT` používa Win EXE `L:\nite3d\nite3\windows\nite3w - 110.exe`, historický `reachable.asm` a predchádzajúci inventár `win110_fixups`. Vyžaduje byte-exact EXE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Nezávisle overil bajty a dekódovanie všetkých 60 231 evidovaných začiatkov; názov historického ASM nie je dôkaz dosiahnuteľnosti.

Strojové výstupy: `win110_trig_callers/summary.json`, `far_callers.csv`, `caller_instruction_context.csv`. Summary pripína aj SHA-256 ASM a oboch vstupných fixup CSV. Kontextové riadky sú okná inventára, nie samostatne uzavreté CFG.

PASS1 mapa sa nemení: 54 164 B PARTIAL, 3 087 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED, spolu 57 295 B. DOS katalóg zostáva 40 rozsahov, 1 372 inštrukcií / 3 133 B kódu a 55 010 B typovaných dát celého obrazu. Predchádzajúce seeded replay prípady zostávajú 6 091; táto dávka nepridáva replay. Nové lokálne výsledky zatiaľ nie sú publikované na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta pre každú oblasť: počet dôkazmi uzavretých jednotiek delený úplným inventárom jednotiek oblasti. Menovatele kontraktov, vetiev a polí zatiaľ nie sú uzavreté, preto je nové percento N/A. Historické percentá nižšie sú iba orientačné. Žiadna oblasť sa touto dávkou neoznačuje za DEEP VERIFIED.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Najbližší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené súbory a stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | DS:4BEA vstup a DS:4C46/4C48 výsledky callerov | identita DS a vstupný rozsah | sledovať definície DS |
| Tabuľky a ukazovatele | 93 % | N/A | šesť selector fixup väzieb | runtime selectory, nepriame hrany | loader fixup stopa |
| Funkcie / ASM / CFG | 90 % | N/A | šesť priamych FAR hrán | dosiahnuteľnosť a caller CFG | uzavrieť vstupné vetvy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie tickov | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | konkrétne Win trig dátové väzby | účel výsledkov a clipping | výsledkoví spotrebitelia |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI a lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie a sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | LOAD parity | porovnať načítaný stav |
| Windows Win16 | 92 % | N/A | šesť NE relokačne doložených volaní | DS, selectory, nepriame volania | caller DS a argument guardy |

## Runtime testy

DOSBox-X: zachytiť zodpovedajúce DOS trig callery, ich DS, argumenty a výstupné WORDy pri prirodzenej hre; porovnať s predchádzajúcimi seeded modelmi. DOSBox-X sám nepotvrdí tento Win16 selector kontext. Pre Win16 treba kompatibilné Windows prostredie s debuggerom: zastaviť na šiestich FAR call sites, zaznamenať opravený selector, DS, zásobník a AX pred/po návrate; overiť aj hraničné vstupy a výsledkových spotrebiteľov. Tieto testy sú plánované, nevykonané.
