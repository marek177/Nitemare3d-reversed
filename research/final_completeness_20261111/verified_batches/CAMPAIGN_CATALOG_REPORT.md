# Nitemare 3D — nezávislé dekódovanie a spoločný katalóg

11. 11. 2026. Táto dávka zlepšuje reprodukovateľnosť a konsoliduje existujúce lokálne dôkazy. **Nemení pôvodné klasifikácie PASS320 a nepotvrdzuje úplnosť kampane.**

## Merateľný výsledok

Obraz má 171 360 B a SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

| Metrika aktuálnej kampane | Výsledok |
|---|---:|
| Funkčné rozsahy v katalógu | 20 |
| Inštrukcie overené nezávislým dekóderom | 785 |
| Bajty týchto inštrukcií | 1 796 |
| Únia lokálne identifikovaných dátových polí | 808 B |
| Iné bajty, v tejto kampani neposúdené | 168 756 B |
| Intervaly úplnej pracovnej partition | 74 |
| Nové DEEP VERIFIED | 0 B |
| Runtime testy | 0 |
| Riadené instruction replay prípady, nie originálny runtime | 23 |

1 796 + 808 + 168 756 = 171 360. Prekrývajúce sa dátové polia sú počítané ako únia; nedochádza k ich dvojitému započítaniu. PARTIAL kód a dáta znamenajú lokálne dôkazy, nie uzavreté kontrakty. UNKNOWN v pracovnej partition neprepisuje historický status týchto bajtov z iných auditov. Aktualizované po zlúčení XMS dát a4 B saved vector pointera; predchádzajúca snímka read312E mala 1 273 B kódu a 258 B dát. Z 280 B XMS dávky bolo 8 B už zahrnutých, prírastok je 272 B.

**2 604 lokálne posúdených bajtov sa nesmie deliť počtom 57 295**: ich prienik s originálnymi NON-CODE intervalmi nie je známy. Nové sémantické percento celého projektu sa nevypočítava.

## Nezávislá kontrola

Skript `independent_decode_and_catalog.py` používa iced-x86 1.21.0 v 16-bitovom režime. Pri každej inštrukcii kontroluje:

1. Presnú zhodu zakódovaných bajtov so SHA-pinned obrazom.
2. Rovnosť `image_offset = CS*16 + IP` v príslušnom nerelokovanom priestore.
3. Platnosť dekódovania a zhodu dĺžky so starším inventárom.
4. Jedinečné vlastníctvo inštrukčných bajtov a neprítomnosť konfliktu s lokálnymi dátovými intervalmi.

Výsledok PASS sa týka týchto kontrol. Nie je automatickým potvrdením každej staršej mnemoniky, interpretácie všetkých operandov, globálnej dosiahnuteľnosti ani úplnosti CFG. Výstup `independent_instructions.csv` zachováva nový dekódovaný text vedľa historického textu; cieľ priamych vetiev je dostupný na ďalšie porovnanie. SHA natívneho dekódera je zaznamenaný v summary.json.

Štyri medzery v prevzatých inventároch ostávajú UNKNOWN, hoci obsahujú 90h. Žiadna nebola potichu doplnená do počtu inštrukcií. Mapa bola vytvorená nad kompletným obrazom a obsahuje aj neposúdené rozsahy.

## Artefakty

- `campaign_catalog/byte_intervals.csv` a `.json`: úplná aktuálna partition, presné hranice end-exclusive, dĺžky, SHA-256 rozsahu, lokálny status a dôkazový vlastník.
- `campaign_catalog/functions.csv`: dvadsať lokálnych funkčných rozsahov, počty, výsledok nezávislej kontroly hraníc a otvorené členstvo PASS320.
- `campaign_catalog/independent_instructions.csv`: 785 dekódovaných inštrukcií, bajty, segmentový kontext a priame ciele.
- `campaign_catalog/summary.json`: reprodukované súčty a identita dekódera.
- Dátové typy, vlastníci, xrefs a vedľajšie účinky sú v `worx_helper/data_intervals.csv`, `worx_dataflow/data_intervals.csv` a príslušných troch WORX reportoch. Pracovná partition nenahrádza ich bohatšie kontrakty.

Reprodukcia v existujúcom pracovnom prostredí:

```text
python independent_decode_and_catalog.py PATH_TO_ICED_X86_INSTALLATION OUTPUTS_DIRECTORY
```

Dekóder sa nainštaloval iba do pracovného priečinka. Globálny Python ani pôvodné herné súbory neboli menené. Prvý pokus starým pipom vyžadoval nedostupný Rust build; úspešný pokus použil wheel `iced_x86-1.21.0-cp38-abi3-win_amd64.whl` cez lokálny pip 25.0.1.

## Aktualizácia 13 oblastí

Historické odhady nie sú baseline meraného pokrytia. Nové percento je **N/A pri všetkých oblastiach**, pretože chýbajú úplné inventáre menovateľov a pôvodná NON-CODE mapa. Metodika po ich získaní: sémanticky uzavreté jednotky / úplný inventár príslušných polí, položiek, funkčných kontraktov alebo vetiev. Runtime výsledky sa vykazujú osobitne.

| Oblasť | Historický odhad | Nové potvrdenie | Neznáme / blokátor | Najbližší krok |
|---|---:|---|---|---|
| Mapy a formáty | 99 % | read312E umožňuje short read s CF=0, PARTIAL | skutočné vstupy a spracovanie nedoplneného headera | párová stopa čítania a spotreby polí |
| Dátové typy a konštanty | 95 % | centrálna únia 808 B PARTIAL po deduplikácii XMS a vector polí | členstvo NON-CODE a životnosť | úplné alias xrefs |
| Tabuľky a ukazovatele | 93 % | XMS move descriptor 16 B; counter=63 aritmeticky zasiahne handle/callback; 28/28 normalizovaných DOS dispatcher párov | selector bounds, neskoršie zápisy a externé ABI | sledovať prvé použitie skutočne inštalovaného vektora63 a counter |
| Funkcie / ASM / CFG | 90 % | DOS: 690 nezávisle dekódovaných inštrukcií a 12 replay prípadov; Win16: 27 kandidátov, 1 154 inštrukčných začiatkov PARTIAL | DOS ABI, inicializácia, lifetimes a prirodzená dosiahnuteľnosť | DOSBox-X read/seek/error stopy |
| RNG | 97 % | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | PIT helper a8 callerov PARTIAL; 35 aritmetických low8 nulových vstupov,5 caller replay prípadov | platné resource menovatele a tick ordering | watchpoint AH43/base20000 a spotrebiteľ3675/367C |
| DEMO a vstupy | 96 % | bez nového dôkazu | determinizmus | párové prehratie |
| Renderer / VGA | 94 % | bez nového dôkazu | clipping/VGA stav | framebuffer a DAC |
| GUARD / bossovia | 93 % | bez nového dôkazu | stavové prechody | dispatcher a dosiahnuteľnosť |
| Zbrane / projektily | 92 % | bez nového dôkazu | slot lifecycle | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | bez nového dôkazu | cache po LOAD | serializačný kontrakt |
| Windows Win16 | 92 % | 6082 fixup miest; CFG z NE vstupov: 27 kandidátov, 2 713 dekódovaných B vrátane 3 konfliktných B, PARTIAL | 13 nepriamych control sites; pri troch callbackoch selector guard; 60 231 historických začiatkov prešlo byte/decode kontrolou; 9 priamych čítaní slotu, 0 priamych writerov v inventári; návrat KERNEL:#1, runtime selektory | producenti DS:20D0 pointera a DS ABI callbacku; kontrakt importu na 2:3C7A |

## Zostávajúca hlavná brána

Originálna mapa PASS320 s 1 488 rozsahmi a pôvodným hash manifestom stále chýba. Existujúca mapa vedľajšej kampane výslovne uvádza, že PASS320 neimportovala. Nie je prípustné premenovať náš nový katalóg na PASS320 ani spätne priradiť 57 295 bajtov podľa agregovaného súčtu.

Konkrétne runtime testy ostávajú v WORX reportoch: DF a pamäť názvov, krátke read kontajnerového headera, bypass DX sentinel vetvy seek a producenti callbacku. V tejto dávke sa žiadny runtime test nespustil. PE32 port sa nevykonáva.

## Doplnenie obnovy PASS320

Priamo overený zdrojový balík na L:/_chrome má štyri zhodné manifest položky, ale žiadny CSV ledger. Generátor kopíruje bez zmeny PASS319 deep_byte_ranges319.csv. Podrobnosti a merateľné hranice ZIP hľadania sú v PASS320_ARCHIVE_RECOVERY_REPORT.md; nasledujúci cieľ obnovy je tento konkrétny predchodca. Žiadne percento ani bajtový status sa nemení.

## Dávka DOS XMS layout

DOS_XMS_LAYOUT_REPORT.md pridáva identifikáciu XMS ABI podľa primárnej špecifikácie, deväť lokálnych polí (280 B vrátane prekryvov s predchádzajúcimi dávkami), 71 CS operand xrefs a skorý metadata alias pri count=63. Po následnom zlúčení centrálna partition obsahuje530 B dát; prírastok je272 B po odpočítaní8 B prekryvu. Lokálna slučka netestuje AX po XMS move a bez úpravy odovzdá nepárny short read, ak nastane. Runtime dosiahnuteľnosť a celkový limit counter ostávajú otvorené. Nové percentá N/A, DEEP VERIFIED0 B.

## Dávka callerov service49

Skript probe_dos_service49_callers.py znovu overil35 648 prevzatých inštrukčných začiatkov. Nenašiel priamy encoded CALL na service49 ani dispatcher; v celom obraze nie je CD63. Jediný immediate AH49 kandidát volá INT21, preto nie je callerom INT63. Tabuľkový slot AH49 ostáva doložený. Nepriame, generované a externé volania nie sú vylúčené; nejde o dôkaz nedosiahnuteľnosti ani limitu counter. Percentá ostávajú N/A; ďalší krok: producenti FAR pointerov na dispatcher a runtime stopa vstupu.

## Dávka inštalácie INT63

DOS_VECTOR63_REPORT.md a audit_dos_vector63.py overili tri fragmenty (43 inštrukcií /81 B), uloženie starého vektora, inštaláciu15BF:30E6 a dve obnovy cez INT21. Nové4 B saved pointera sú zahrnuté v dátovej únii534 B. Fragmenty zatiaľ nezvyšujú počet uzavretých funkcií ani centrálny code count. Neznáme: vykonanie inicializácie, prví callerovia, nepriamy/external vstup a poradie restore. Nové percentá N/A, ďalší krok: runtime IVT/caller stopa.

## Dávka audio lifecycle

DOS_AUDIO_LIFECYCLE_REPORT.md pridáva3 kandidátne funkcie (306 B), priame game caller hrany inicializácie a ukončenia,35 port helper callerov a8 B pointerových dát. Centrálna partition má1 579 B kódu a542 B dát. Otvorené: callback AX clobbers, helpery a runtime IF/DF; portová slučka nie je volaním INT63 servisov. Ďalší krok: producenti CS:3896 a helper466A. Nové percentá N/A.

## Dávka callback/PIT

DOS_CALLBACK_PIT_REPORT.md pridáva13 B setter a53 B divisor helper,6 B dát a6 riadených CPU replay prípadov. Doložený slotAH46, IF=1 po setteri, gate==1 bypass a divide error pri gate!=1/AX0. Nie je to DOSBox-X ani dôkaz prirodzenej chyby. Scheduler riadok bez sémantického percenta: nový časovačový helper PARTIAL, tick ordering zostáva otvorený; ďalší krok je8 callerov divisor a gate writeri.

## Dávka divisor callerov

DOS_PIT_CALLER_REPORT.md pridáva provenienciu8 callerov,3 fixné gate referencie, úplnú WORD aritmetiku dvoch numerátorov a5 originálnych caller+callee replay prípadov. Bajtové súčty sa nemenia. Zostáva prirodzená dosiahnuteľnosť a input validation; ďalší krok je producent CS:34B9 na190AB. Nové percentá N/A, DEEP VERIFIED0 B.

## Dávka timer základne

DOS_TIMER_BASE_REPORT.md overil initialWORD20000,6 B setter v sloteAH43 a7 fixných referencií. Dva pridané dátové bajty a6 B kódu sú zlúčené do partition. Hodnota20000 dáva lokálne nenulový PIT vstup59;35 matematických kandidátov nie je automaticky35 resource chýb. Zostávajú prirodzení setter callerovia a timer handler. Nové percentá N/A, DEEP VERIFIED0 B.

## Dávka sample IRQ

DOS_SAMPLE_IRQ_REPORT.md pridáva145 B handler a2 B accumulator. Šesť mutable operandov /12 B je samostatná overlay vrstva v kóde, nepočíta sa znovu ako DATA. Tri replay pokusy zlyhali na sémantickej zhode a majú accepted0;23 predchádzajúcich replay prípadov sa nemení. Blokátor tejto runtime vetvy: izolovať Unicorn/harness nesúlad pri samomodifikácii. Ďalší krok: single-instruction ADC/fetch kontrola a lookup table bounds. Nové percentá N/A.

## Dávka sample lookup a SMC diagnózy

DOS_SAMPLE_LOOKUP_SMC_REPORT.md pridáva256 B lookup tabuľku s úplnou input/output mapou, hranicami odvodenými z BYTE indexu a range SHA. Centrálna dátová únia808 B. Pri SMC continuous trace je opakovaný ADC hook s rozdielnym CF; count1 beh sa zastaví na64-krokovom limite. Oba experimenty terminal, accepted0.23 predchádzajúcich prijatých replay prípadov sa nemení. Blokátor: presná príčina SMC nesúladu; ďalší krok minimalizovaný ADC experiment a nezávislý CPU model. Nové percentá N/A, DEEP VERIFIED0 B.

## Dávka izolácie emulačného nesúladu

UNICORN_SMC_DIAGNOSTIC_REPORT.md reprodukuje problém syntetickým ADD/ADC: memory_add2/12 odchýlok iba pri zmene budúceho operanda; explicit_flags0/12 a flags_barrier0/12.36 syntetických diagnostických prípadov sa nepočíta do23 game instruction replay. Pôvodný handler ostáva runtime neoverený, ďalší krok druhý CPU model/DOSBox-X. Byte counts a nové percentá bez zmeny, DEEP VERIFIED0 B.
