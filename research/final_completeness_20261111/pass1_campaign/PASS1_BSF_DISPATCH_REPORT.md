# PASS1: BSF dispatcher a zostávajúce názvy zdroja

14 B CLASSIFIED ONLY → PARTIAL: [28D2C,28D2F) = rb + NUL, [28D2F,28D3A) = nite3d.bsf + NUL. Explicitné PUSH pointery DS:161C a 161F v 083D:29F2/29F5 vstupujú do CRT 11EE:06E6. Dôkaz neurčuje celý formát BSF ani význam skratky. Žiadny DEEP VERIFIED.

## Funkcia, CFG a segmenty

083D:29CA..2AD7, image [0AD9A,0AEA7), span 269 B. Overených 89 inštrukcií / 254 B. Dvanásť bajtov [0ADB0,0ADBC) tvorí šesť WORD skokových cieľov cez CS, ďalšie tri bajty span nie sú dosiahnuté týmto CFG a nepočítajú sa ako kód. Výstup noninstruction_bytes.csv uvádza každý nekódový bajt tohto rozsahu. Neurčuje automaticky padding.

FAR vstup, mode WORD v [SS:BP+6], ENTER 4, zachované BP/SI. DS je DGROUP, SS obsahuje lokály. Rutina pracuje s pracovným blokom DS:3638 a ďalšími DS pointermi mimo počiatočného file image. Mode sa porovnáva unsigned s 5; pri vyššej hodnote ide na spoločnú návratovú cestu. Skoková tabuľka obsahuje presne 29F2,2A7C,2A90,2A9A,2AA8,2AB6. Exporty: switch_table.csv, cfg_edges.csv, bsf_mode_dispatch.csv. Všetky dekódované bajty sú porovnané s kanonickým obrazom aj dodaným inventárom.

## Rekonštrukcia režimov

| Mode | Staticky potvrdené operácie | Návrat / otvorená otázka |
|---:|---|---|
|0|open nite3d.bsf v rb; read count 1 × size 54 do DS:3638; close; XOR helper 0FBA:01B2 na 54 B; ak AL!=0 error; helper 083D:28EE s BYTE3639 a podľa flagu363B aj BYTE363A|spoločný návrat z neinicializovaných lokálov; caller použitie otvorené|
|1|test BYTE363B|nenulový → DS:363B, inak FAR NULL|
|2|offset 363C a segment DS|FAR DS:363C|
|3|WORD366A, DWORD3660, text1671 → 0277:1B02|DX:AX z callee|
|4|WORD3668, DWORD365C, text167C → 0277:1B02|DX:AX z callee|
|5|WORD366C, DWORD3664, text1687 → 0277:1B02|DX:AX z callee|
|>5|bez inicializácie lokálov → spoločný návrat|hodnota nie je lokálne definovaná|

Lokály BP-4 (offset) a BP-2 (segment) inicializačná vetva mode0 explicitne nenapĺňa. To nie je samo osebe dôkaz prirodzenej chyby: návrat môže caller ignorovať. Mode1/2 a 3..5 majú vlastné definované návratové cesty. Error wrapper 0FBA:000C môže ukončiť proces; bez dôkazu jeho prirodzeného návratu sa nasledujúce inštrukcie nevydávajú za správanie po chybe. Výsledok read sa pred XOR lokálne nekontroluje. Pôvodná analýza XOR helpera zostáva samostatným dôkazom, v tejto dávke sa nevykonáva.

Prvé dve volania helpera 28EE posúvajú argument pomocou MOV AL z BYTE bez vynulovania AH. Význam celého WORD argumentu musí určiť callee; pseudokód nesmie predpokladať zero-extension. Mode3..5 používajú celé DWORD zo stavového bloku, ich dátový typ v tejto dávke nie je uzavretý.

## Reprodukcia a meranie

audit_pass1_bsf_dispatch.py IMAGE INVENTORY DECODER OUT; promote_pass1_fields.py s mapou pass1_near_heap_state; verify_pass1_partition.py. Kanonický image SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Táto dávka je statická: nové controlled replay prípady 0, prirodzené runtime testy 0. Callee ABI a celý formát zostávajú PARTIAL.

**57 067 B PARTIAL, 184 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 877 intervalov potvrdila presné členstvo a hash hodnoty bez dier a prekryvov. Integrita nie je sémantická úplnosť. Posledná publikovaná GitHub snímka ešte túto lokálnu dávku neobsahuje.

SHA mapy `420dbc5bd1c596b9d7594d9d4b130a8361c3e5cda5ea3f7a0f3e0d1919f9e71c`.

## Aktualizácia 13 oblastí

Nové percento = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; historické percentá sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|BSF 54 B read a XOR cesta|celý formát|preskúmať skutočný BSF|
| Dátové typy a konštanty |95 %|N/A|14 B / 2 reťazce|184 B iba klasifikované|zvyšné SS/alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|6 WORD CS jump table|typy 365C..366C|callee kontrakt|
| Funkcie / ASM / CFG |90 %|N/A|254 B / 89 inštrukcií|callee a caller efekty|mode calleri|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag 8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|resource vetvy oddelené|zdroj identity|0277:1B02 closure|
| SAVE / LOAD |92 %|N/A|read návrat lokálne nekontrolovaný|prirodzený I/O kontrakt|kratší read trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|BSF parita|nájsť ekvivalent|

## Runtime testy na vykonanie

V DOSBox-X zachytiť mode callerov a používanie návratu pri mode0, obsah 54 B pred a po XOR a skutočný read count. Odlišovať normálny a chybový beh; pri chýbajúcom alebo krátkom súbore sledovať handler až po terminálny výsledok. Overiť DS/SS kontext a WORD argumenty 28EE. Nové runtime testy neboli vykonané; PE32 sa nevytvára.
