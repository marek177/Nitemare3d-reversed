# DOS 2.0: názvy epizód, mapové hlavičky a presah hudobného indexu

## Funkcia

FAR vstup 0277:0336 má presné hranice `[02AA6,02B3A)`, **148 B / 53 inštrukcií**, končí RETF. CFG od vstupu overil celé telo proti pôvodným bajtom; priame vetvy majú ciele na jeho inštrukčných hraniciach. Výstupy externých volaní a ich návrat zostávajú závislosťami.

WORD argument na SS:[BP+6] sa uloží do DS:626A a používa sa bez kontroly rozsahu ako číslo epizódy. Tri volania CRT 11EE:278C dostanú formát `%s%d`, prefix a ten istý WORD. Cieľové near offsety sú DS:627C, 628C a 629C, po 10h bajtoch. Tento stride sám neuzatvára kapacitu všetkých runtime objektov; pri konvenčnom 16-bit `%d` však najdlhšie výsledky vrátane NUL majú 11 B pre `map.`/`img.` a 12 B pre `demo.`. Skutočný CRT formátovací kontrakt zostáva otvorený.

```text
episode = WORD argument
DS:626A = episode
format(DS:627C, "%s%d", "map.", episode)
format(DS:628C, "%s%d", "img.", episode)
format(DS:629C, "%s%d", "demo.", episode)
handle = call 11EE:1C72(DS:627C, 8000h)
if handle == FFFFh: call error(open-format, DS:627C)
count = call 11EE:1E14(handle, DS:D30C, 0202h)
if count != 0202h: call error(read-format, DS:627C)
call 11EE:1BB6(handle)
return
```

Názov súboru, požadovaný počet 514 B a následné porovnanie sú staticky doložené. Význam CRT flags, úplné filesystem chyby, návratová hodnota wrappera a natural DS sú otvorené. Ak error callee vráti riadenie, samotné telo nezastaví pokračovanie po chybnej hodnote handle či krátkom čítaní. SI/DI/BP sa v tele ukladajú a obnovujú; plný callee register/segment ABI sa nedokazuje.

## Presné NON-CODE polia

| DS offset | Obrazový interval, koniec exclusive | Obsah vrátane NUL |
|---|---|---|
| 028C | [2799C,279A1) | `map.\0` |
| 0291 | [279A1,279A6) | `%s%d\0` |
| 0296 | [279A6,279AB) | `img.\0` |
| 029B | [279AB,279B0) | `%s%d\0` |
| 02A0 | [279B0,279B6) | `demo.\0` |
| 02A6 | [279B6,279BB) | `%s%d\0` |

Spolu **31 B / 6 polí**, každý interval má SHA a konkrétny spotrebiteľ v `filename_bindings.csv`. DS:626A a cieľové buffery sú mimo file-backed obrazu a nepridávajú NON-CODE bajty. Chybové texty už boli evidované; nezapočítavajú sa znova.

## Reálne MAP súbory a nový rozpor

Používateľov adresár `L:\nite3d\nite3\dos` obsahuje všetky tri MAP/IMG/DEMO sady. Táto dávka analyzuje prvý WORD, hlavičku a celkovú dĺžku troch MAP súborov; ich SHA a SHA prvých 514 B sú v `map_assets.csv`.

| Súbor | B | Prvý WORD, desiatkovo | Overená rovnosť |
|---|---:|---:|---|
| MAP.1 | 90 626 | 11 | 514 + 11×8192 |
| MAP.2 | 82 434 | 10 | 514 + 10×8192 |
| MAP.3 | 82 434 | 10 | 514 + 10×8192 |

To dokladá zhodu dĺžok s počtom 8 KiB záznamov za hlavičkou, nie úplný obsahový parser všetkých levelov. Párovanie súborov s EXE vychádza z ich spoločného používateľovho adresára, nie zo zachyteného runtime otvorenia.

Hudobný selector z predchádzajúcej dávky používa `DS:15BE + 10*episode + level`. Pri odvodených nominálnych level indexoch 0..count−1 vzniká **31 kombinácií**, nie iba 30. Pre epizódu 1 / level 10 je výsledná obrazová adresa **28CE2h**, hodnota **13**: ide o prvý bajt nasledujúceho nominálneho riadka. Predošlé označenie matice 3×10 preto zostáva iba nominálnym rozdelením bajtov, nie úplnou doménou hry. Hlásenie o tomto obmedzení bolo doplnené priamo do `PASS1_MUSIC_SELECTOR_REPORT.md`.

`music_index_crosscheck.csv` obsahuje všetkých 31 výpočtov podľa reálnych count WORDov. Ide o statický crosscheck, nie 31 nových runtime/replay prípadov. Neuzatvára prirodzenú dosiahnuteľnosť levelu 10, pôvod čísla epizódy ani všetky LOAD/doménové guardy. Neoznačuje tento presah automaticky za chybu hry: číta platný existujúci bajt a jeho zámer môže byť zdieľané ID.

## Reprodukcia a pokrytie

`audit_pass1_episode_files.py IMAGE INVENTORY DECODER_DIR GAME_DIR OUT` reprodukuje pôvodné inštrukcie/CFG, šesť literalov, tri väzby formátovania a crosscheck MAP súborov. Výstupy v `pass1_episode_files/`: `instructions.csv`, `cfg_edges.csv`, `data_fields.csv`, `filename_bindings.csv`, `map_assets.csv`, `music_index_crosscheck.csv`, `summary.json`.

31 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálna mapa: **54 746 B PARTIAL, 2 505 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nezávislá kontrola 660 intervalov potvrdila SHA, presné členstvo 57 295 B a nulové diery/prekryvy.

Centrálny katalóg: **45 funkčných rozsahov, 1 614 inštrukcií / 3 822 B kódu**, 55 592 B typovaných dát celého obrazu a 54 744 B typovaných historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia. Controlled replay súčty sa nemenia: 7 687 plus samostatne 65 548 prefixových prípadov. Prirodzené runtime testy 0. Nové výsledky zatiaľ nie sú na GitHub.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta pre každú oblasť: uzavreté jednotky / úplný inventár jednotiek. Úplné menovatele chýbajú; nové percentá sú N/A a predošlé orientačné. Výsledky zostávajú PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | count 11/10/10 a presné dĺžky | obsah hlavičiek/levelov | doména level indexu |
| Dátové typy a konštanty | 95 % | N/A | 31 B / 6 textov | CRT kontrakt | formátovač ABI |
| Tabuľky a ukazovatele | 93 % | N/A | hudobný level-10 presah | zámer zdieľania ID | calleri selectoru |
| Funkcie / ASM / CFG | 90 % | N/A | 148 B / 53 inštrukcií | externé chyby a bounds | caller argumenty |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | audio ordering | stop/play stopa |
| DEMO a vstupy | 96 % | N/A | názov demo.N z epizódy | DEMO parser | otvorenie DEMO |
| Renderer / VGA | 94 % | N/A | názov img.N z epizódy | IMG parser | header loader |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | episode globál a header destination | stav po LOAD | serializačné polia |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | map/resource parity | Win hlavičky |

## Runtime testy na vykonanie

Zachytiť argument 0277:0336, tri výsledné názvy, skutočný otvorený MAP a 514 B čítania. V epizóde 1 preveriť dosiahnutie levelu 10 a jeho hudobné ID, bez predpokladu, že ide o chybu. Porovnať prirodzené prechody, LOAD a DEMO a sledovať DS:626A/626C. Chybné epizódy či záporné levely testovať iba ako označené syntetické experimenty. DOSBox-X vykonanie zatiaľ chýba.
