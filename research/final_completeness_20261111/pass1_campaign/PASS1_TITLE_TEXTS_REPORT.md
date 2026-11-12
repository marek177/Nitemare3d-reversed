# DOS 2.0: titulné texty a podmienená registered/shareware vetva

## Funkcia a presné hranice

FAR vstup 083D:0008 má rozsah **[083D8,084FD), 293 B / 87 inštrukcií**, končí RETF. Každý byte a inštrukčná hranica sú overené voči kanonickému obrazu a historickému inventáru nezávislým dekóderom. Telo má jednu podmienenú voľbu medzi dvoma statickými textami; neobsahuje jump table. Príprava zdrojov, kreslenie a dotazy sa vykonávajú cez externé helpery, ktorých širší kontrakt táto dávka neuzatvára.

## Šesť presných NON-CODE reťazcov

| DS | Interval obrazu, koniec exclusive | B vrátane NUL | Text |
|---|---|---:|---|
| 139E | [28AAE,28ABA) | 12 | `Nitemare-3D` |
| 13AA | [28ABA,28ABF) | 5 | `V2.0` |
| 13AF | [28ABF,28ACE) | 15 | `Distributed by` |
| 13BE | [28ACE,28AE2) | 20 | `Registered software` |
| 13D2 | [28AE2,28AF4) | 18 | `Shareware version` |
| 13E4 | [28AF4,28B16) | 34 | `Copyright 1994-95, David P. Gray.` |

Spolu **104 B** v súvislom rozsahu `[28AAE,28B16)`. Každý má konkrétny FAR textový dátový tok do 0D29:0116 a SHA v `data_fields.csv`. Nasledujúce číselné tabuľky nie sú súčasťou textov. Žiadny reťazec sa nepredlžuje cez prvý NUL.

## Dátový tok, vetvenie a zásobník

Telo postupne odovzdáva textovej rutine 0D29:0116 tieto druhé súradnicové WORDy a pointery:

| Poradie v jednom behu | WORD | Text |
|---:|---:|---|
| 1 | 40 | Nitemare-3D |
| 2 | 60 | V2.0 |
| 3 | 100 | Distributed by |
| 4 | 115 | dynamický FAR pointer v DX:AX z dotazu 083D:29CA s argumentom 2 |
| 5 | 140 | Registered software, ak dotaz s argumentom 1 vráti DX:AX != 0; inak Shareware version |
| 6 | 160 | Copyright text |

Dotaz s argumentom 1 sa testuje `OR DX,AX`, teda je to nulový/nenulový výsledok celej dvojice, nie iba test AX. Samotná implementácia dotazu nie je touto dávkou uzavretá: nie je to dôkaz konkrétneho licenčného, aktivačného či registračného algoritmu. Dynamický text pri hodnote 2 sa podľa okolitého nápisu javí ako distribučný text; jeho skutočný obsah a lifetime sa tu nepotvrdzujú.

Pri každom texte sú na zásobníku pre 0116 WORDy `[FFFFh, druhý_WORD, text_offset, text_segment, AX_z_resource_helpera, 0001h]`. Prvý WORD je vždy FFFFh; konkrétny centrovací/renderovací význam tohto sentinelu vyžaduje kontrakt 0116. Posledný WORD 1 pochádza z hornej polovice skoršieho PUSH DWORD a zostáva na zásobníku po odstránení WORD argumentu resource helpera. Nemožno preto každé PUSH DWORD považovať za jeden argument tohto helpera.

Rutina volá 0277:0188 pre zdroje, 0156:0A3A pre prípravnú závislosť, 0D29:016A s hodnotami **2,1,0** a 083D:29CA s hodnotami **2,1**. Úplný význam zdrojových AX, bankových hodnôt a kreslenia sa nepredpokladá iba podľa ich čísel. Explicitne neprepína DS/ES/SS; callee register/segment ABI a prirodzený runtime DS zostávajú otvorené.

## Controlled replay a reprodukcia

`audit_replay_pass1_title_texts.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` overuje kanonický SHA, celé telo a šesť NUL hraníc. Vykoná dva výsledky predicate helpera (0 a 1) pri load bázach 0 a 1000h s EXEPACK relokáciami: **4 prípady, 0 odchýlok**. Každý vyprodukuje šesť pozorovaných textových call argumentov, spolu 24 záznamov.

Päť závislostí je v emulačnej kópii nahradených RETF. Resource helper vracia seedovaný AX; query 2 vracia seedovaný FAR text, query 1 seedovaný nulový/nenulový výsledok. Test overuje poradie textov a offsetov, DS segment, WORD sentinel, style WORD 1, poradie oboch dotazov, hodnoty 2/1/0 a SP po návrate. Nedokazuje prirodzený obsah dynamického textu, správanie dotazu ani výsledné pixely. Testy sú výslovne iba lokálny riadený model s uchovaným DS v mockoch.

Artefakty `pass1_title_texts/`: `instructions.csv`, `data_fields.csv`, `cases.csv`, `draw_arguments.csv`, `summary.json`; ďalej aktuálna CSV/JSON NON-CODE mapa, promotion summary a nezávislá partition kontrola.

## Pokrytie

104 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne: **54 955 B PARTIAL, 2 296 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávisle overených 672 intervalov, ich SHA a presné členstvo, bez dier a prekryvov. Triedenie a lokálny replay neoprávňujú označiť titulnú obrazovku alebo dynamický query obsah za DEEP VERIFIED.

Centrálny katalóg: **53 rozsahov, 1 827 inštrukcií / 4 415 B kódu**, 55 801 B typovaných dát celého obrazu a 54 953 B historických NON-CODE dát. Rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia. Controlled replay súčty: 12 073 plus samostatne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. Najnovšia overená GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto novú dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá sú N/A a predošlé sú orientačné. Nové výsledky zostávajú PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 104 B / 6 textov | susedné číselné dáta | ich indexovaní spotrebitelia |
| Tabuľky a ukazovatele | 93 % | N/A | statické a dynamický FAR pointer | dynamický lifetime | query 29CA |
| Funkcie / ASM / CFG | 90 % | N/A | 293 B / 87 inštrukcií | externé kontrakty | helpery a prirodzený caller |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | poradie udalostí | tick stopy |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | presné volacie argumenty titulných textov | pixelový význam sentinelov | 0116 kontrakt |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | poradie textov a podmienený nápis | reálne vykreslenie a farby | render stopa |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | parity | serializačné stopy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | titulná parity | Win texty a query |

## Runtime testy na vykonanie

Zachytiť prirodzený vstup 083D:0008, výsledky query 2/1, ich DS/ES kontext a skutočný obsah dynamického textu. Porovnať argumenty textovej rutiny a výsledné snímky oboch staticky zistených vetiev, ak sú prirodzene dostupné. Seedovaná zmena výsledku query nie je dôkaz licenčného správania hry. DOSBox-X vykonanie zatiaľ chýba.
