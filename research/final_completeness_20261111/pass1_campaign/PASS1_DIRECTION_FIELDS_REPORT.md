# DOS 2.0: indexované smerové dáta a príznaky

## Doložené polia

Desať BYTE operandov dokladá desať susedných nominálne osembajtových polí. Každé pole má presné obrazové hranice a SHA, jeden byte-exact overený primárny spotrebiteľ a overené okno susedných inštrukcií. Osemprvkové rozmery sú nominálne podľa susedných základní a obsahu; úplné writer/consumer inventáre a platnosť indexov zostávajú otvorené. Stav je PARTIAL.

Adresy a hodnoty sú hexadecimálne, pokiaľ tabuľka neuvádza inak. Konce intervalov sú exclusive.

| DS základňa | Obrazový interval | Primárne čítanie | Osem hodnôt, desiatkovo |
|---|---|---|---|
| 00CA | [277DA,277E2) | 0000:0E2C | 0, 8, 8, 0, 0, -8, -8, 0 |
| 00D2 | [277E2,277EA) | 0000:0E3B | -8, 0, 0, 8, 8, 0, 0, -8 |
| 0AC2 | [281D2,281DA) | 04C7:0238 | 0, 1, 1, 1, 0, -1, -1, -1 |
| 0ACA | [281DA,281E2) | 04C7:0246 | -1, -1, 0, 1, 1, 1, 0, -1 |
| 0AD4 | [281E4,281EC) | 04C7:0C57 | 0, 8, 8, 0, 0, -8, -8, 0 |
| 0ADC | [281EC,281F4) | 04C7:0C63 | -8, 0, 0, 8, 8, 0, 0, -8 |
| 20A6 | [297B6,297BE) | 0FD9:04A1 | 0, 1, 1, 1, 1, 1, 1, 0 |
| 20AE | [297BE,297C6) | 0FD9:04A8 | 1, 1, 1, 0, 0, 1, 1, 1 |
| 20B6 | [297C6,297CE) | 0FD9:04AF | 1, 0, 0, 1, 1, 1, 1, 1 |
| 20BE | [297CE,297D6) | 0FD9:04B6 | 1, 1, 1, 1, 1, 0, 0, 1 |

Záporné hodnoty v prvých šiestich riadkoch sú interpretácia dvojkového doplnku BYTE (F8h = -8, FFh = -1); samotné čítania MOV AL nepreukazujú signed aritmetický kontrakt všetkých následných spotrebiteľov. CSV preto uchováva unsigned aj signed interpretáciu. Kľúčový rozdiel: dvojica 0AD4/0ADC je presná 16 B kópia dvojice 00CA/00D2, ale **nie je** jednoduchým vynásobením celej dvojice 0AC2/0ACA ôsmimi. Nemožno ich zameniť za univerzálnu rovnakú smerovú tabuľku.

## Konkrétne dátové toky

Na 0000:0E28 a 0E37 sa index číta ako WORD z DS:4158; dva výsledné BYTE sa zapisujú cez FAR ukazovateľ do ES:[BX+2] a ES:[BX+3], potom sa do ES:[BX+4] uloží 8. Presný životný cyklus cieľového objektu a platný interval DS:4158 sa týmto oknom neuzatvárajú.

Na 04C7:0232 a 0242 sa index číta z BYTE ES:[SI+11h], BH sa pred prvým čítaním nuluje. Výsledky 0AC2/0ACA sa posunú `SHL AL,CL` a uložia do ES:[SI+13h]/[SI+14h]. Hodnota CL vzniká z lokálneho BYTE; v zachytenom kontexte sa vetví aj podľa ES:[SI+0Ah]. Celý vstupný kontrakt a všetky možné CL sa nepovažujú za uzavreté. Posun sa vykonáva v 8-bit AL, preto sa nesmie automaticky nahradiť neobmedzeným signed násobením.

Na 04C7:0C51 a 0C5F sa rovnaký BYTE smeru ES:[SI+11h] používa pre dvojicu 0AD4/0ADC, výsledky sa ukladajú do ES:[SI+13h]/[SI+14h] bez tohto posunu.

Na 0FD9:049D sa BX nastaví z DS:4158. Štyri BYTE čítania 20A6/20AE/20B6/20BE sa ukladajú na SS:[BP-2], [BP-9], [BP-0Ah], [BP-0Bh]. Obsah 0/1 podporuje označenie príznakov; úplný význam každej renderovacej vetvy a orientácia na svetové strany zostávajú neuzavreté. V týchto vstupných čítaniach sa nenachádza maskovanie BX na 0..7. Dokázaná neexistencia lokálneho maskovania nie je dôkaz neplatných prirodzených indexov.

## Reprodukcia a metriky

`audit_pass1_direction_fields.py IMAGE INVENTORY DECODER_DIR OUT` overí SHA kanonického obrazu, každý primárny DS operand, jeho bajty a dĺžku, okolité inštrukcie a presnú duplikáciu dvoch 16 B blokov. `pass1_direction_fields/data_fields.csv`, `consumers.csv`, `consumer_context.csv`, `summary.json` uchovávajú hranice, hodnoty a dôkazy. Kontextové okná nie sú samostatne uzavreté funkcie a nepridávajú sa k centrálnemu počtu funkcií.

Promócia z mapy `pass1_dsp_status` pridala **80 B z CLASSIFIED ONLY do PARTIAL**. Nové súčty: **54 638 B PARTIAL, 2 613 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nezávislá kontrola overila všetkých 646 intervalov, ich SHA a presné členstvo 57 295 B, bez dier a prekryvov.

Centrálny katalóg má naďalej 42 funkčných rozsahov / 1 450 inštrukcií / 3 354 B kódu, teraz 55 484 B typovaných dát celého obrazu a 54 636 B typovaných historických NON-CODE dát. Rozdiel 2 B oproti PARTIAL zostáva neuzavretý relokačný WORD. Žiadny nový seeded replay ani prirodzený runtime test; súčty zostávajú 6 091 a 0. Nové lokálne výsledky zatiaľ nie sú publikované na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta pre každú oblasť: uzavreté jednotky / úplný inventár jednotiek oblasti. Menovatele chýbajú, preto sú nové percentá N/A; predošlé hodnoty sú orientačné. Nové polia zostávajú PARTIAL, nie DEEP VERIFIED.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 80 B / 10 polí | indexové hranice | writeri DS:4158 |
| Tabuľky a ukazovatele | 93 % | N/A | presná kópia dvoch tabuliek | úplné referencie | odvodené adresy |
| Funkcie / ASM / CFG | 90 % | N/A | desať primárnych čítaní | celé caller CFG | vstupné guardy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | štyri indexované 0/1 polia | význam každej vetvy | spotrebitelia lokálnych flagov |
| GUARD / bossovia | 93 % | N/A | smerové BYTE do polí +13h/+14h | lifecycle a smerové domény | writer ES:[SI+11h] |
| Zbrane / projektily | 92 % | N/A | dva BYTE kroky do FAR objektu | typ objektu | consumer +2/+3 |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | LOAD parity | porovnať stav |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | DS callerov | caller guardy |

## Runtime testy na vykonanie

Zaznamenať prirodzené hodnoty DS:4158 a ES:[SI+11h] na desiatich čítaniach, overiť DS/ES/SS, nasledujúce zápisy a všetky navštívené indexy. Indexy 0..7 možno porovnať s tabuľkami, ale ich syntetické prechádzanie nie je dôkaz úplnej hernej dosiahnuteľnosti ani indexovej bezpečnosti. Pre renderer sledovať následné vetvy podľa štyroch lokálnych BYTE, pre objekty skutočný signed/unsigned spôsob použitia +2/+3 a +13h/+14h. DOSBox-X testy zatiaľ nevykonané.
