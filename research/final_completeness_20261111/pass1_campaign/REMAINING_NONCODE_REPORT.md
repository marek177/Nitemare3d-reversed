# PASS1: presný inventár zvyšných CLASSIFIED ONLY / UNKNOWN intervalov

## Rozsah a výsledok

Aktuálna mapa `pass1_rng/noncode_intervals.csv` má SHA-256 `d56c8e140699962935cac685cbfe4dfa153509d7351626ea5dfa8fd25c0bace8`. Z nej bolo bez zmeny statusov vyčlenených **92 intervalov / 2 309 B**: 86 intervalov / 2 265 B CLASSIFIED ONLY a 6 intervalov / 44 B UNKNOWN. Presné hranice, dĺžky, statusy, SHA, pozorovania bajtov, referenčné počty a ďalšie kroky sú v `remaining_noncode/interval_ledger.csv/json`.

Toto je inventár nižšie klasifikovaného zvyšku, **nie všetkej zostávajúcej práce kampane**. Ďalších 54 986 B PARTIAL ešte nemá automaticky uzavreté všetky typové, writer, caller a runtime kontrakty. Navyše 2 B PARTIAL bez uzavretej typovej roly zostávajú samostatne evidované v centrálnom `untyped_partial_relocation_check.json`. DEEP VERIFIED je stále 0.

## Metodika a referenčné kategórie

`audit_remaining_noncode.py IMAGE MAP_CSV INVENTORY DECODER_DIR OUT` overí kanonický SHA obrazu a intervalové SHA vstupnej mapy. Znovu byte-exact overí a nezávisle dekóduje všetkých **35 648** začiatkov dodaného DOS inventára. Z explicitných operandov vytvára kandidátske väzby do zvyšných intervalov:

| Kategória | Počet | Presný význam |
|---|---:|---|
| DS_DIRECT_CONDITIONAL | 283 | priamy DS operand vrátane jeho šírky, mapovaný pod podmienkou default DS bázy 27710h |
| INDEXED_BASE_CANDIDATE | 835 | konštantná základňa indexovaného operandu; skutočná adresa závisí od registrov |
| IMMEDIATE_DS_CANDIDATE | 201 | WORD konštanta v MOV/PUSH, ktorá by pri interpretácii ako DS offset zasiahla interval |
| ADDRESS_FORMATION_CANDIDATE | 28 | LEA, nie dereferencia |
| DIRECT_CONTROL_TARGET | 0 | priamy near/FAR branch/call target v dodanom inventári |

Spolu **1 347 kandidátskych vzťahov**, nie 1 347 potvrdených sémantických spotrebiteľov. Jedna inštrukcia môže zasiahnuť viac intervalov alebo vytvoriť viac druhov kandidáta. DS kontext každého callera nie je uzavretý. Indexed základňa ani numerická konštanta sama nedokazuje dátovú referenciu; ich skutočná adresa môže byť inde alebo hodnota vôbec nemusí byť pointer.

Šírky priamych operandov sa čítajú z nezávislého dekódera, preto sa zachytia aj prístupy začínajúce pred intervalom a presahujúce doň. Dynamické ES/SS mapovanie, REP/implicitné pamäťové cesty, aliasované pointery a kód mimo dodaného inventára nie sú týmto zoznamom uzavreté. Názov starého inventára ani existencia začiatku inštrukcie nie sú dôkaz prirodzenej dosiahnuteľnosti.

## Presných 44 UNKNOWN bajtov

Všetky nižšie uvedené konce sú exclusive. Obsah je nulový, ale padding či zarovnanie z toho nevyplýva.

| Interval | B | Priame DS / immediate kandidáty |
|---|---:|---|
| [1BDA2,1BDB0) | 14 | 0 / 0 |
| [1C070,1C080) | 16 | 0 / 0 |
| [1D0EC,1D0F0) | 4 | 0 / 0 |
| [20B88,20B90) | 8 | 0 / 0 |
| [2770E,2770F) | 1 | 0 / 0 |
| [2770F,27710) | 1 | 0 / 0 |

Posledné dve susedné položky tvoria jeden 2 B súvislý zvyšok, ale zostávajú dvoma intervalmi aktuálnej partition. Skorší slovný zoznam piatich súvislých neznámych oblastí sa preto nesmie zameniť za počet riadkov mapy. Potrebné sú dôkazy o segmentových hraniciach, loaderi a nepriamych writeroch. Nulové kandidátske počty nie sú dôkaz nepoužívania.

## Konkrétne ďalšie analytické priority

| Interval | B | Podmienené priame DS väzby | Najbližší krok |
|---|---:|---:|---|
| [29A3B,29A56) | 27 | 26 | rozložiť CRT stav pri 11EE:2073..20EB a ostatných spotrebiteľoch; oddeliť WORD/FAR polia |
| [27F2D,27F3C) | 15 | 23 | sledovať priame čítania/zápisy pred debug stream WORDom, rozlíšiť flagy a limity |
| [27839,27848) | 15 | 21 | uzavrieť konkrétne typy a writerov z operandov v kandidátskom CSV |
| [29BB2,29BC8) | 22 | 19 | rozdeliť TZ texty, pointery a konštanty pred už doloženým RNG stavom |
| [28E00,28E16) | 22 | 18 | sledovať globály, nerozšíriť automaticky nulové dáta na padding |
| [28EDD,28EE0) | 3 | 18 | preveriť šírky operandov presahujúce do týchto troch bajtov pred music pointerom |
| [29BCC,29C44) | 120 | 12 | rozlíšiť command/environment texty a CRT stav podľa skutočných consumerov |

Referenčný počet je priorizačný signál, nie sémantické percento ani dôkaz konkrétnej štruktúry. V kandidátskom CSV sú pri každej väzbe CS:IP, pôvodné bajty, dekódovaná inštrukcia, kandidátska adresa, šírka a cieľový interval.

33 intervalov nemá v tejto obmedzenej sade žiadny kandidát. Spolu 171 B zvyšného inventára je v kompletne nulových intervaloch. Ani jedna z týchto skupín sa automaticky nepreklasifikuje. ASCII/NUL príznak v ledgeri je iba pozorovanie obsahu; nevytvára bez consumer dôkazu nový string typ.

## Reprodukcia a pokrytie

Artefakty: `audit_remaining_noncode.py`, `remaining_noncode/summary.json`, `interval_ledger.csv/json`, `reference_candidates.csv`. Skript nemení zdrojovú mapu. Status changes=0, nové replay prípady=0, prirodzené runtime testy=0 a nové DEEP VERIFIED=0.

Celkový PASS1 stav zostáva **54 986 B PARTIAL, 2 265 B CLASSIFIED ONLY, 44 B UNKNOWN**, presne 57 295 B. Centrálny katalóg zostáva 62 rozsahov / 2 167 inštrukcií / 5 348 B kódu a 55 872 B typovaných dát celého obrazu. Výsledok nie je vyhlásením dokončenia žiadnej fázy. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 tento nový inventár ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú; nové percentá sú N/A a predošlé orientačné. Kandidátske skeny nič nepovyšujú na PARTIAL/DEEP VERIFIED.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | presný zvyšný intervalový inventár | dynamické writeri | loader/segment stopy |
| Dátové typy a konštanty | 95 % | N/A | 92 riadkov s obsahovými pozorovaniami | konkrétne typy zvyšku | CRT 27 B blok |
| Tabuľky a ukazovatele | 93 % | N/A | explicitné kandidátske adresy/šírky | aliasy a indexy | kontext jednotlivých väzieb |
| Funkcie / ASM / CFG | 90 % | N/A | 35 648 začiatkov znovu overených | neuvedený/indirect kód | alternatívne vstupy |
| RNG | 97 % | N/A | bez nového algoritmického dôkazu | prirodzené seedy | reset caller |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie udalostí | tick stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | seed/call ordering | DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | prirodzené vstupy | effect producer |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | real asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | nepriamy stavový zápis | serializačné rozsahy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | DOS/Win dátová parity | Win ekvivalenty polí |

## Runtime testy na vykonanie

Pre šesť UNKNOWN intervalov nastaviť load-base korigované watchpointy na čítanie/zápis a zaznamenať celý rozsah pamäťovej operácie. Negatívna stopa jedného scenára nedokazuje padding. Pri prioritných CRT blokoch zachytiť DS a konkrétne pointer/word hodnoty pri priamych consumeroch; kandidátske immediate/indexed väzby uzavrieť až podľa skutočných registrov alebo silnejšej statickej analýzy. DOSBox-X vykonanie zatiaľ chýba.
