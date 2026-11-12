# CRT: near-heap next-fit scan, split a coalescing

Stav PARTIAL. 11EE:2168..21E4, image [14048,140C4), span124 B, **63 inštrukcií / 123 B**. Jeden span byte nie je dosiahnutý týmto CFG. Pôvodné bajty a začiatky sú nezávisle dekódované a porovnané s kanonickým image aj inventárom. Exporty near_heap_next_fit_scan.csv a cfg_edges.csv. Žiadne nové typované NON-CODE bajty ani DEEP VERIFIED.

## Register ABI a blokový model

NEAR vstup, BX=near root v DS, CX=request WORD. Rutina hneď vykoná INC CX a AND CL,FEh: zaokrúhlená veľkosť je **((request+1) mod65536) & FFFEh**, nie request+2. CLD zmení DF na0 a ponechá ho tak. BX a SP obnoví, BP nemení. SI/DI/DX/AX sú pracovné; pri úspechu DX=DS, AX=pointer za hlavičkou, CF=0. Pri zlyhaní AX=root+6 hodnota, root+8 sa nastaví na root+6 a CF=1; DX pri chybe nie je výsledkový kontrakt.

Root+6 je dolný blokový offset, +8 kurzor, +0A sentinel offset. WORD hlavička obsahuje párnu payload dĺžku a najnižší bit voľnosti. Nasledujúca hlavička je current_header+2+payload. Sentinel je FFFEh. Pre túto maticu sú všetky hlavičky párne a reťaze platné. Neexistuje lokálna univerzálna validácia pointerov, cyklov alebo poškodených veľkostí.

## Vyhľadávanie a mutácie

Najprv skenuje od kurzora k tail sentinel. Pri neúspechu na platnej párnej hranici sa môže vrátiť na root+6, ak kurzor nie je už na začiatku, a pokračovať s hranicou cursor-1. Hranica sa kontroluje vo vetve obsadených hlavičiek; opis ako pevný obmedzený array scan by bol nepresný. Voľné bloky sa môžu počas hľadania meniť aj pri konečnom neúspechu.

```text
pre aktuálnu voľnú hlavičku:
    payload = tag - 1
    ak payload >= wanted:
        header = wanted            // bit0 clear, allocated
        result = header_address + 2
        ak payload != wanted:
            next_header = result + wanted
            next_header.word = payload - wanted - 1 // zostávajúci free tag
        root.cursor = result + wanted
        return result,DS,CF=0
    ak nasledujúci blok je voľný:
        header = payload + next_tag + 2
        znovu posúď spojenú voľnú hlavičku
    inak pokračuj cez obsadenú hlavičku
```

Spájanie prepíše iba prvú voľnú hlavičku; staré vnútorné hlavičky ostávajú ako bytes vo väčšom payload. Sken nemusí zachovať pôvodný layout pri zlyhaní. Exact fit nevytvorí zvyškovú hlavičku. Split umiestni root cursor na začiatok novej zvyškovej hlavičky. Request0 aj priamy requestFFFFh zaokrúhlia na0; tento vnútorný helper preto môže vracať pointer zodpovedajúci nulovej payload alokácii. Vyšší malloc caller má vlastný guard veľkosti (FFFFh do normálnej cesty neprepúšťa), takže nejde o dôkaz prirodzeného FFFFh požiadavku alebo chyby hry.

## Nezávislý model a kontrolovaná emulácia

19 680 prípadov na dvoch load bázach. Pre každé n=1,2,3 sa používajú všetky kombinácie payload0/2/8, všetky allocated/free tag kombinácie, každý blokový kurzor vrátane sentinel pozície a request0,1,2,3,7,8,15,16,FFF0h,FFFFh. Model používa logické hlavičky a explicitné graph scan pravidlá, nie vykonávanie skopírovaného ASM. Pôvodná rutina beží bez callee modelov a bez OS volaní.

Porovnáva sa celý 256-bajtový buffer vrátane zachovaných payloadov a starých hlavičiek, dva guard BYTE, celý 12 B root, AX/CF, DX pri úspechu, SP/BP/BX/CX a DF. 3 778 prípadov spájalo bloky a 11 820 vstúpilo do druhého scan priechodu. Nulové odchýlky. Maticu nemožno vydávať za dôkaz ľubovoľne dlhej reťaze, poškodených alebo nepárnych hraníc, segmentového wrapu, concurrent zmeny, celého malloc alebo prirodzeného runtime.

Reprodukcia: audit_replay_near_heap_scan.py IMAGE INVENTORY DECODER EMULATOR OUT. Canonical image SHA e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297, iced-x861.21.0/Unicorn2.1.4. cases.csv obsahuje sizes/free/cursor/request, počet priechodov a spojení a výsledok. Pôvodný grow/resize zostáva osobitne dokladovaný v NEAR_HEAP_GROW_REPORT.md a PASS1_NEAR_HEAP_FLAGS_REPORT.md; integrácia celého malloc ešte zostáva otvorená.

## Meranie

PASS1 ostáva **57 102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**. Nové funkčné pokrytie nie je sémantické percento CRT alebo celej hry. Natural DOSBox-X runtime0. Táto nová lokálna dávka ešte nie je v publikovanej analytickej snímke ba27379dd28c9a689d15233b0fd7017867f50114.

SHA cases `8193b25ef066925637b5960670acab4ba0ba631a89adc5573b53150fffb24b2e`.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Historické odhady sa nemenia podľa test count alebo integrity mapy.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|bez nového dôkazu|loader hranice|map closure|
| Dátové typy a konštanty |95 %|N/A|bez novej promócie|149 B iba klasifikované|susedné alias polia|
| Tabuľky a ukazovatele |93 %|N/A|blokové tagy, split a spájanie|ľubovoľné reťaze|malloc sekvencie|
| Funkcie / ASM / CFG |90 %|N/A|123 B / 63 inštrukcií|celý malloc|3CCF integrácia|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|CRT memory oddelená|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|iný heap model|Win kontrakt|

## Runtime testy na vykonanie

V DOSBox-X sledovať prirodzené malloc požiadavky, kurzor a viacblokový layout pred/po skene2168. Zaznamenať spájanie aj pri zlyhaní a nadväzujúci grow/retry. Overiť, či prázdny alebo nulový request vôbec vzniká z prirodzených callerov. Nezamieňať seedovaný model s runtime potvrdením celej knižnice. PE32 sa nevytvára.
