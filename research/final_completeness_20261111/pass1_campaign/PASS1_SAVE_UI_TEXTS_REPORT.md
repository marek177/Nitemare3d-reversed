# PASS1: SAVE/LOAD texty a herné správy

Nové statické dôkazy typujú **434 B v 26 NUL poliach**. Úroveň PARTIAL. Presné literal operandy a vybrané konzumenty sú overené; pôvodné SAVE/LOAD I/O, formát save súboru, UI ani sprintf sa nevykonávajú a nevyhlasujú za uzavreté.

## Vstupy a reprodukcia

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. `audit_pass1_save_ui_texts.py IMAGE INVENTORY DECODER OUT` overí oba vstupy, všetky hranice, NUL a presné near offset immediates v CS 0D29. Vybraných 281 inštrukcií konzumentov sa porovná s obrazom a nezávisle dekóduje. Kanonický DS=2771h je podmienka mapovania; prirodzené DS/SS invarianty celých funkcií sa neuzatvárajú.

`text_catalog.csv` zachováva všetkých 26 presných textov, escape/newline obsah, adresy a role. `data_fields.csv` má polootvorené intervaly, dĺžky a range SHA. `literal_references.csv` má presný PUSH/MOV operand a `contexts.csv` nadväzujúce použitie. Náhodné konštanty 2000h alebo iné číselné immediates z nesúvisiacich funkcií sa nepoužívajú ako dôkaz textových referencií.

## Adresy a konkrétni konzumenti

| Image interval (koniec exclusive) | Obsah / role | Referencia v CS 0D29 |
|---|---|---|
| [29597,2959F), [2959F,295A6) | `use the`, `need a` | 1E56/1E5C výber AX, push do sprintf argumentov |
| [295A6,295B0) | `You %s %s` | 1E60 → CRT 278C v 1E67 |
| [295B0,29612) | multiline cheat notice | 2199 s DS segmentom → local 0720 |
| [29612,2961B) | `user.sav` | 224C → 0277:0D3E |
| [2961B,29636) | prázdny slot, presne 27 B | 2265 → REP MOVSD + MOVSW + MOVSB |
| [29636,2963F), [2963F,29648) | dve `user.sav` | 232A → 0277:1176, 2393 → 0277:0D3E |
| [29648,29663) | druhý 27 B prázdny slot | 23AC → rovnaká dĺžka kopírovania |
| [29663,2966C), [2966C,29675) | dve `user.sav` | 2401 a 243A, susedné file helper argumenty |
| [29675,2967A) | `SAVE` | 244D → sprintf 278C |
| [2967A,296A7) | save confirmation s dvoma `%s` | 2450 → sprintf 2458, výsledok SS buffer → prompt |
| [296A7,296B0), [296B0,296B9) | dve `user.sav` | 2476 → 0277:0E1C, 24A6 → 0277:0D3E |
| [296B9,296BE) | `LOAD` | 24B9 → sprintf |
| [296BE,296EB) | samostatná load confirmation | 24BC → sprintf 24C4, SS buffer → prompt |
| [296EB,296F4), [296F4,296FD), [296FD,29706) | tri `user.sav` | 24DD/25C1/25F3 → file helper calls |
| [29706,2970B), [2970B,29710) | `map.`, `%s%d` | 2629/262C → sprintf 2633 |
| [29710,29715), [29715,2971A) | druhé `map.`, `%s%d` | 269F/26A2 → sprintf 26A9 |
| [2971A,2973C) | weapon jam message | 2741 DS FAR text → local 0750 |
| [2973C,29749) | `Really quit?` | 2899 DS FAR text → 0720; návrat AL porovnaný s 59h |

Rovnaké texty sa nezlučujú: majú odlišné adresy a konkrétne konzumenty. Desať výskytov `user.sav` sú desať dátových polí, nie dôkaz desiatich rôznych formátov save súboru. Hlavičky a payload save súborov táto dávka neanalyzuje.

## Presné kopírovanie a formátovanie

Obe šablóny prázdneho slotu obsahujú 10 úvodných medzier, `** Empty slot **` a NUL, spolu 27 B. Skript kontroluje ECX=6, REP MOVSD (24 B), MOVSW (2 B) a MOVSB (1 B) na konkrétnych adresách. DS sa kopíruje do ES; pointer cieľa sa načíta z lokálnej premennej. Je to dôkaz presného statického rozsahu kopírovania za predpokladu DF=0, nie vykonanie UI ani dôkaz dostatočnej cieľovej kapacity.

Text `You %s %s` berie jeden argument z výberu `use the`/`need a` a druhý zo SI; nasledujúce odovzdanie výsledku je cez SS lokálny buffer. Save/load confirmation má dve near-string konverzie, akčný label a dynamický popis slotu. Po prompt call sa AL porovná s Escape 1Bh pred file helper cestou. Presný obsah dynamického popisu, kapacita všetkých SS bufferov a nebezpečné dlhé vstupy nie sú uzavreté týmto dátovým auditom.

Mapové mená sa tvoria z near prefixu `map.` a `%s%d`; prirodzený argument domény a súborové otvorenie zostávajú na ďalšom audite. Pri quit prompt sa porovnáva hodnota 59h (`Y`); úplná normalizácia vstupu v prompt rutine sa tu nevykonáva. Prítomnosť jam textu nie je sama dôkaz príčiny zaseknutia zbrane.

Samostatný nulový BYTE **[29749,2974A)** zostáva CLASSIFIED ONLY. NUL po poslednom reťazci nie je automatický dôkaz paddingu/alignment. Toto pole sa do 434 B nezapočítava.

## Meranie

434 B CLASSIFIED ONLY → PARTIAL. Mapa: **56123 B PARTIAL, 1128 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 793 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `6ff03b14ed471110fca085f5af721163a80a87cac65b3edb9a86ca2a9c4c2d94`. Integrita mapy sama nie je dôkaz sémantickej úplnosti.

Katalóg zostáva 90 funkčných rozsahov, 3235 inštrukcií / 8125 B. Vybrané kontexty sa nezapočítavajú ako nové celé funkcie. Typované dáta celého obrazu 57009 B; historického NON-CODE 56121 B a 2 netypované PARTIAL relokačné bajty. Controlled replay bez zmeny 614175 plus osobitne 65548 smerových prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé hodnoty orientačné. Počet textových bajtov nenahrádza uzavretie SAVE/LOAD alebo UI algoritmov.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | dve map name šablóny | file I/O a doména | name caller |
| Dátové typy a konštanty | 95 % | N/A | 434 B / 26 NUL polí | nulový susedný BYTE | referencia 29749 |
| Tabuľky a ukazovatele | 93 % | N/A | near/FAR text odlíšený | dynamické slot pointery | record producer |
| Funkcie / ASM / CFG | 90 % | N/A | 281 kontextových inštrukcií | celé funkcie | 0277 file helper CFG |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | bez nového dôkazu | timing | loop trace |
| DEMO a vstupy | 96 % | N/A | Escape/Y testy callerov | prompt normalizácia | 0720 |
| Renderer / VGA | 94 % | N/A | textové call argumenty | renderer body | 0750 |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | jam message konkrétne volaný | príčina jamu | 2740 calleri |
| Sprity / HUD / paleta | 92 % | N/A | dve presné 27 B šablóny | cieľové kapacity | slot record layout |
| SAVE / LOAD | 92 % | N/A | filename, confirm a Escape gate | serializácia/payload | file helper closure |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | UI/SAVE parity | Win text/caller match |

## Runtime testy na vykonanie

Zachytiť slot popisy a presné SS sprintf buffer hranice pri SAVE/LOAD; overiť abort Escape pred I/O. Pri prázdnom slote skontrolovať cieľových 27 B a DF. Map name a quit/jam správy korelovať s prirodzenými callermi. Pôvodné DOSBox-X I/O a Win16 behaviorálna parity zostávajú otvorené.

