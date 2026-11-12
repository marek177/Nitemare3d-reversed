# Krížové porovnanie VGA page-flip rutín

Nový dôkaz potvrdzuje lokálnu bajtovú a CFG zhodu dvoch celých rutín v ôsmich DOS označeniach 1.0/1.1/1.2/1.5/1.7/1.8/1.9/2.0. Ide o sedem unikátnych rozbalených obrazov. Žiadny runtime test ani nová klasifikácia NON-CODE bajtov sa nepridáva. Win16 vlastný present algoritmus zostáva otvorený.

## Metóda a vstupy

`compare_vga_page_versions.py IMAGE OLD_ROOT DECODER TRIG_VERSIONS_CSV WIN_EXE OUT` používa kanonický obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Verziové SHA sa overujú proti skoršiemu dôkazu `trig_cross_version/versions.csv`, ktorého SHA-256 je `e38ee99642f8b435f9398b0d9a96812668607e58d187a1c3101ff2becb8da7e9`. Presné SHA všetkých obrazov zostávajú v `functions.csv`.

Referencie sú DOS 2.0 immediate [015EE,01607), 25 B / 12 inštrukcií, a synchronized [01608,01637), 47 B / 23 inštrukcií. Dekóder dovolí normalizovať **iba tri dekódované WORD DS displacements na 012C/012E v každej rutine**. Ostatné bajty sa musia zhodovať presne vrátane portových konštánt, branch offsetov, CLI/STI, inštrukčných prefixov a RETF. Všetky tri rozdiely musia mať rovnakú deltu. Kandidát musí byť v každom obraze unikátny a vzdialenosť začiatkov oboch rutín presne 26 B.

Každý nájdený kandidát sa nezávisle dekóduje a porovnáva sa relatívny IP, dĺžka a flow-control trieda každej inštrukcie. Tým sa preverí presná lokálna CFG/body ekvivalencia; caller kontext a prirodzená reachability sa z toho neodvodzujú.

## Výsledky DOS

Adresy sú hex image offsets, všetky intervaly polootvorené.

| DOS označenie | Immediate začiatok | Synchronized začiatok | DS displacement delta | Segmentové WORD dáta image začiatok |
|---|---|---|---:|---:|
| 1.0 | 015E0 | 015FA | −2 | 2372A |
| 1.1 | 015E0 | 015FA | −2 | 23A7A |
| 1.2 | 015E0 | 015FA | −2 | 23ADA |
| 1.5 | 015EE | 01608 | 0 | 275CC |
| 1.7 | 015EE | 01608 | 0 | 2766C |
| 1.8 | 015EE | 01608 | 0 | 277FC |
| 1.9 | 015EE | 01608 | 0 | 277FC |
| 2.0 | 015EE | 01608 | 0 | 2783C |

Všetky zodpovedajúce štyri dátové bajty sú presne `00 A0 00 A4`, teda WORD A000h/A400h. Staršie 1.0–1.2 používajú DS:012A/012C; od 1.5 DS:012C/012E. Dátová image báza sa pre každú verziu preberá zo skoršieho jednoznačného trig table/code odvodenia. Táto dávka nepredstiera nezávislé startup DS overenie každej verzie. Všetky vypočítané dátové adresy sú skontrolované proti skutočným bajtom príslušného obrazu.

**16 normalizovaných celých funkčných zhôd, z toho 10 raw-exact**. Staršie tri verzie majú spolu 18 WORD editov (3 verzie × 2 funkcie × 3 operands). Nijaký iný bajt sa nemaskuje. Zhodné sú výmena segmentových WORD, spracovanie high BYTE segmentu, WORD OUT na 03D4h s indexom 0Ch, v synchronized aj status polling na 03DAh, CLI a nepodmienené STI. To dokazuje rovnaké lokálne inštrukčné správanie pri rovnakom vstupnom stave a I/O odpovediach. Nepotvrdzuje totožný VGA init režim, frame pacing, caller IF ani výsledný obraz medzi verziami.

## Win16 1.10

EXE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Skript parsuje NE hlavičku a skenuje všetky štyri file-backed code segmenty v ich deklarovaných hraniciach. V žiadnom sa nenachádza ani jedna z dvoch inštrukčných šablón s povolenými tromi DS displacement zmenami.

Toto je **negatívny výsledok iba pre presnú šablónu**. Nie je to dôkaz absencie page flipu alebo funkčne rovnocenného vykresľovania vo Win16. Iné prology, API backendy, registre, inštrukčné usporiadanie alebo algoritmy tento matcher nerozpoznáva. Zatiaľ sa nepriraďuje žiadny Win present counterpart ani behaviorálna parity.

## Artefakty a aktuálna mapa

`vga_pages_cross_version/functions.csv` má 16 výsledkov s image a range SHA. `operand_edits.csv` má všetkých 18 skutočných zmien. `instructions.csv` zachováva nezávislé relatívne dekódovanie každej verzie. `win_code_segments.csv` eviduje skenované NE code rozsahy. `summary.json` zaznamenáva vstupné SHA a negatívny Win template výsledok. Žiadne unikátne replay prípady sa touto dávkou nepripočítavajú.

NON-CODE mapa sa nemení: **55075 B PARTIAL, 2176 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Posledná nezávislá kontrola platí pre identickú mapu so SHA-256 `b0ed4ef42aa5fbd5986580e10bb7d7b49d73c3d6cc3bf9b72f0290d08c3c02ab`, 715 intervalov bez dier/prekryvov. Centrálny katalóg zostáva 78 funkčných rozsahov, 2761 inštrukcií / 6903 B, 55961 B typovaných dát celého obrazu; historických NON-CODE dát 55073 B a 2 netypované PARTIAL relokačné bajty. Controlled replay 531425 plus osobitne 65548 smerových prefixových prípadov; pôvodné runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 novú dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; predošlé percentá sú orientačné. 16 funkčných zhôd sa nevydáva za úplné pokrytie oblasti.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | A000/A400 v 8 DOS označeniach | startup DS kontext | inicializačné rutiny |
| Tabuľky a ukazovatele | 93 % | N/A | staršie displacementy −2 | alias writeri | page ledger |
| Funkcie / ASM / CFG | 90 % | N/A | 16 lokálnych body/CFG zhôd | caller invarianty | flip caller graph |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO stopa |
| Scheduler | 96 % | N/A | CLI/STI telo zhodné v DOS | caller IF | runtime IF trace |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Renderer / VGA | 94 % | N/A | 2 algoritmy zhodné v 8 DOS | VGA init / viditeľný efekt | mode setup match |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | page počiatočné dáta zhodné | framebuffer layout | režim init |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | 4 code segmenty bez tej istej šablóny | vlastný present algoritmus | Win display API callers |

## Runtime testy na vykonanie

Pre reprezentatívne DOS 1.0 a 2.0 zaznamenať VGA init, stránkové segmenty, IF pri flip vstupe a CRTC portové udalosti; porovnať viditeľný frame a pacing. Vo Win16 najprv staticky vystopovať display/present API, potom porovnať výsledné správanie. Žiadna PE32 portácia sa nevykonáva.
