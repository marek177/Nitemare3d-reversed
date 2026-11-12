# DOS 2.0: interné vzory skenera a 256-bitová znaková množina

## Presné NON-CODE polia

| Pole | DS | Obrazový interval, koniec exclusive | Bajty |
|---|---|---|---|
| Whitespace vzor | 22C2 | [299D2,299D8) | `20 09 2D 0D 5D 00` |
| Prázdny vzor | 22C8 | [299D8,299DA) | `5D 00` |

Spolu **8 B**. Každé pole je NUL-ukončený interný scanset vzor so zatváracím `]`; whitespace vzor obsahuje medzeru a rozsah TAB..CR. Žiadne susedné nulové WORDy sa k nim nepridávajú. Presné hranice a SHA sú v `data_fields.csv`.

Vetva 11EE:0EDC uloží do SS:[BP-18Ch] pointer 22C2h; vetva 0ED3 uloží 22C8h. Spoločný kód cez pôvodnú CRT rutinu 11EE:2FB0 vymaže 32 B lokálneho buffera SS:[BP-20h]. Skener následne buduje bitovú množinu s indexom `character >> 3` a maskou `1 << (character & 7)`. Pre konkrétne vzory vzniknú:

- Whitespace bitmapa: členovia **09h, 0Ah, 0Bh, 0Ch, 0Dh a 20h**.
- Prázdny vzor: žiadny člen; všetkých 32 B je nula.

Po inicializačnom DEC má samostatný BYTE SS:[BP-1A8h] hodnotu FFh pri seedovanej počiatočnej nule. Preto sa samotná bitmapa nesmie bez analýzy ďalšej vetvy označiť za množinu povolených znakov: môže slúžiť ako vylučovacia množina. Plné správanie `%s`, `%c`, explicitných scansetov, inverzie a konzumácie vstupu zostáva otvorené.

## Parserový fragment

Konkrétny whitespace vzor vykoná vetvu rozsahu medzi 09h a 0Dh, vrátane oboch koncov. Cursor skončí na zatváracom `]`, DS:22C6. Prázdny vzor skončí bez pridania znaku na DS:22C8. V tejto dávke je DI seedované na 73h, takže osobitné spracovanie úvodného `]` pre režim 7Bh sa nevykonáva. Nevyhlasuje sa preto úplný kontrakt všeobecnej scanset gramatiky ani všetkých BYTE rozsahov.

`scanner_context.csv` obsahuje 104 byte-exact a nezávisle dekódovaných začiatkov z okna 0ED3..1007. Ide o kontextový výrez väčšej funkcie, nie samostatnú uzavretú funkciu; celých 104 sa nepridáva do centrálneho počtu funkčných tiel. Stop je na 11EE:1007 pred nasledujúcou vstupnou slučkou a volaniami input helperov.

## Pôvodná nulovacia rutina

FAR 11EE:2FB0 má presný rozsah **[14E90,14EBD), 45 B / 23 inštrukcií**, končí RETF. Prijíma near destination na SS:[BP+6], fill WORD na [BP+8] (používa low BYTE) a WORD count na [BP+0Ah]. ES nastaví na DS. Pri nepárnom destination a nenulovom count zapíše prvý BYTE, potom používa REP STOSW a prípadný posledný BYTE cez REP STOSB. DF sa v tele nenastavuje; forward správanie vyžaduje DF=0.

V lokálnom tele sa obnovujú BP a DI, AX vracia pôvodný destination offset; DX používa na uloženie vstupného DI, ES sa mení na DS. Úplný callee ABI a všetky možné counts/adresy nie sú touto dávkou exhaustívne testované. Menovka zodpovedá pamäťovému fill helperu, nie dôkazu pôvodu z konkrétnej knižničnej distribúcie.

Pre lokálny near buffer odvodený z BP je dôležité DS/SS: riadený model tejto dávky výslovne používa **DS=SS**. To nepreukazuje prirodzený runtime kontext všetkých callerov.

## Reprodukcia a overenie

`audit_replay_pass1_crt_scan_templates.py IMAGE INVENTORY DECODER_DIR EMULATOR_DIR OUT` pripína SHA obrazu, kontroluje oba vzory, kontextové inštrukcie a celú fill rutinu. Vykoná oba pôvodné výbery vzorov a pôvodnú tvorbu bitmapy pri load bázach 0 a 1000h s reálnymi EXEPACK relokáciami, DF=0 a DS=SS: **4 riadené prípady, 0 odchýlok**. Žiadny callee nie je nahradený mockom.

Overuje všetkých 32 výsledných BYTE, guard BYTE pred/za bufferom, konečný cursor, inverzný BYTE a lokálne SP. Fill rutina je tu vykonaná iba s count 32 a nulovou hodnotou; žiadne ďalšie counts sa nepočítajú za otestované. Výstupy v `pass1_crt_scan_templates/`: `scanner_context.csv`, `memset_instructions.csv`, `data_fields.csv`, `cases.csv`, `summary.json`, nová mapa a nezávislá partition kontrola.

## Pokrytie

8 B prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálna mapa: **54 851 B PARTIAL, 2 400 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezávisle bolo overených 666 intervalov, ich SHA a presné členstvo, bez dier či prekryvov.

Centrálny katalóg po pridaní celého fill helpera: **52 funkčných rozsahov, 1 740 inštrukcií / 4 122 B kódu**, 55 697 B typovaných dát celého obrazu. V historickom NON-CODE je typovaných 54 849 B; rozdiel 2 B voči PARTIAL zostáva neuzavretá relokácia. Prijaté controlled replay prípady: 12 069 plus osobitne 65 548 normalizačných prefixových prípadov. Prirodzené runtime testy zostávajú 0.

Výsledky sú PARTIAL; celý skener ani všeobecná bezpečnosť fill rutiny sa neoznačujú za DEEP VERIFIED. Najnovší overený GitHub commit 52924ebf849dd79d15af9d7c164b8304f50cae87 túto novú dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického percenta: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá sú N/A a predošlé hodnoty sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 8 B / 2 scanset vzory | okolité stavové dáta | priame spotreby |
| Tabuľky a ukazovatele | 93 % | N/A | presná 256-bit bitmapa | inverzia pri konzumácii | vstupná slučka |
| Funkcie / ASM / CFG | 90 % | N/A | fill helper a parserový fragment | celý scanner a DF kontext | od 1007 |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | prirodzené poradie | tick stopy |
| DEMO a vstupy | 96 % | N/A | CRT vstupná množina oddelená | reálne vstupné callery | scanner call sites |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | parity | serializačné stopy |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | scanner parity | Win vzory a parser |

## Runtime testy na vykonanie

Zachytiť prirodzené volanie skenera s DS/SS a DF, konkrétny formát, vzor, bitmapu a inverzný príznak. Nasledujúcu vstupnú slučku sledovať pre medzeru, TAB..CR a bežný znak, vrátane šírky a konca vstupu. Oddelene overovať všeobecné scansety; vykonanie dvoch interných vzorov nezastupuje celý parser. DOSBox-X vykonanie zatiaľ chýba.
