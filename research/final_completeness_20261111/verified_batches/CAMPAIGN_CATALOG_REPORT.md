# Nitemare 3D — nezávislé dekódovanie a spoločný katalóg

11. 11. 2026. Táto dávka zlepšuje reprodukovateľnosť a konsoliduje existujúce lokálne dôkazy. **Nemení pôvodné klasifikácie PASS320 a nepotvrdzuje úplnosť kampane.**

## Merateľný výsledok

Obraz má 171 360 B a SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

| Metrika aktuálnej kampane | Výsledok |
|---|---:|
| Funkčné rozsahy v katalógu | 8 |
| Inštrukcie overené nezávislým dekóderom | 268 |
| Bajty týchto inštrukcií | 617 |
| Únia lokálne identifikovaných dátových polí | 42 B |
| Iné bajty, v tejto kampani neposúdené | 170 701 B |
| Intervaly úplnej pracovnej partition | 32 |
| Nové DEEP VERIFIED | 0 B |
| Runtime testy | 0 |

617 + 42 + 170 701 = 171 360. Prekrývajúce sa dátové polia sú počítané ako únia; nedochádza k ich dvojitému započítaniu. PARTIAL kód a dáta znamenajú lokálne dôkazy, nie uzavreté kontrakty. UNKNOWN v pracovnej partition neprepisuje historický status týchto bajtov z iných auditov.

**659 lokálne posúdených bajtov sa nesmie deliť počtom 57 295**: ich prienik s originálnymi NON-CODE intervalmi nie je známy. Nové sémantické percento celého projektu sa nevypočítava.

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
- `campaign_catalog/functions.csv`: osem lokálnych funkčných rozsahov, počty, výsledok nezávislej kontroly hraníc a otvorené členstvo PASS320.
- `campaign_catalog/independent_instructions.csv`: 268 dekódovaných inštrukcií, bajty, segmentový kontext a priame ciele.
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
| Mapy a formáty | 99 % | bez nového formátového dôkazu | všetky polia a varianty | kontajnerový header a súbory |
| Dátové typy a konštanty | 95 % | únia 42 B PARTIAL | členstvo NON-CODE a životnosť | kompletné xrefs |
| Tabuľky a ukazovatele | 93 % | spoločná evidencia intervalov | aliasy a externé ABI | relokačný pointer ledger |
| Funkcie / ASM / CFG | 90 % | 268 nezávisle dekódovaných inštrukcií | globálne vstupy a úplné CFG | porovnať branch operands a xrefs |
| RNG | 97 % | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | bez nového dôkazu | tick ordering | dispatcher CFG |
| DEMO a vstupy | 96 % | bez nového dôkazu | determinizmus | párové prehratie |
| Renderer / VGA | 94 % | bez nového dôkazu | clipping/VGA stav | framebuffer a DAC |
| GUARD / bossovia | 93 % | bez nového dôkazu | stavové prechody | dispatcher a dosiahnuteľnosť |
| Zbrane / projektily | 92 % | bez nového dôkazu | slot lifecycle | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | bez nového dôkazu | resource binding | draw xrefs |
| SAVE / LOAD | 92 % | bez nového dôkazu | cache po LOAD | serializačný kontrakt |
| Windows Win16 | 92 % | bez nového dôkazu | NE fixupy | identita a segmentová mapa |

## Zostávajúca hlavná brána

Originálna mapa PASS320 s 1 488 rozsahmi a pôvodným hash manifestom stále chýba. Existujúca mapa vedľajšej kampane výslovne uvádza, že PASS320 neimportovala. Nie je prípustné premenovať náš nový katalóg na PASS320 ani spätne priradiť 57 295 bajtov podľa agregovaného súčtu.

Konkrétne runtime testy ostávajú v WORX reportoch: DF a pamäť názvov, krátke read kontajnerového headera, bypass DX sentinel vetvy seek a producenti callbacku. V tejto dávke sa žiadny runtime test nespustil. PE32 port sa nevykonáva.
