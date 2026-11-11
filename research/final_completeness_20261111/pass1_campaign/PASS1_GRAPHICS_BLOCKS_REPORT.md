# PASS1: tri nominálne grafické bloky

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Počiatočná oblasť **[20B90,219A0)** má 3 600 nulových bajtov. Dôkaz podporuje tri nominálne bloky po 1 200 B vo FAR segmente 20B9h, status PARTIAL. Nuly neurčovali veľkosť.

## Počet a hranice

`083D:0008` má v historickom byte-pinned inventári tri priame FAR volania `0D29:016A`, pred nimi konštantné `PUSH 2` na 83EF, `PUSH 1` na 841A a `PUSH 0` na 84F2. Loader používa dolný BYTE argumentu, vynuluje BH a počíta index*4B0h. Na D41D vloží relokovaný segment 20B9h a výsledný offset ako cieľ resource loadera 0277:196C. Segmentové WORDy D41E, D446 a D468 majú skutočné EXEPACK relokácie.

| Index | Offset segmentu | Obraz, end-exclusive |
|---:|---|---|
| 0 | 0000..04B0 | 20B90..21040 |
| 1 | 04B0..0960 | 21040..214F0 |
| 2 | 0960..0E10 | 214F0..219A0 |

Tri volania dokazujú používané nominálne sloty, nie úplnosť všetkých možných nepriamych callerov. Loader nekontroluje index proti 3 a resource loader nekontroluje dĺžku proti 1 200. Preto nejde o globálny bounds ani bezpečnostný dôkaz. Medzera 219A0..219B0 a bajty pred 20B90 zostávajú bez novej klasifikácie.

## Parser a pointery

Pred prvým čítaním sa testuje BYTE DS:[1C6C+index]; pri nenulovom sa rutina vráti. Pri nulovom ho nastaví na 1 ešte pred resource I/O. Po read uloží FAR pointer bázy do DS tabuľky `3690h + index*512`. Potom SI=1, DI=2, pre SI=1..127:

1. Uloží FAR pointer aktuálnej položky na `3690h + index*512 + SI*4`.
2. Načíta BYTE položky +0 a BYTE +1 (druhý cez segmentový globál DS:256A, počiatočne 20B9h).
3. Spočíta `payload_size = byte0 * ((byte1+7) >> 3)`.
4. Pre každý payload bajt volá `0FBA:00D2` s FAR pointerom na položka+2+i.
5. Zvýši DI o payload_size+2, SI o 1.

Algoritmus podporuje interpretáciu dvojbajtovej rozmerovej hlavičky a bitovo balených riadkov; konkrétnu orientáciu bitmapy, identitu fontu a význam transformácie 00D2 táto dávka neuzatvára. Vzor zodpovedá bitovej mape s výškou byte0 a šírkou byte1, ale označenie osí zostáva hypotézou do kontroly renderer spotrebiteľa. Preto sa typ eviduje ako nominálny grafický blok, nie úplne identifikovaný fontový formát.

Parser nemá lokálnu kontrolu DI+payload proti 1200. Pri poškodených hlavičkách môže čítať a transformovať mimo nominálneho slotu; prirodzené resource dáta zatiaľ neboli overené. Neprítomnosť ďalších priamych volaní v historickom inventári nie je dôkaz absencie nepriamych volaní.

## Reprodukcia a pokrytie

`audit_pass1_graphics_blocks.py IMAGE PRIOR_MAP DECODER_DIR OUT` používa `relocations.csv` vedľa IMAGE. Kontroluje identitu obrazu, konštantné argumenty, relokácie, násobenie, rozmerový výpočet, limit parser cyklu, počiatočné nuly a intervalové SHA. Nezávisle dekóduje celý ohraničený loader aj tri caller okná. Výstupy sú v `pass1_graphics_blocks/`.

Pribudlo **3 600 B PARTIAL z UNKNOWN**. Aktuálne **PARTIAL 39 195 B, CLASSIFIED ONLY 9 222 B, UNKNOWN 8 878 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predchádzajúca mapa mala PARTIAL 35 595 B, UNKNOWN 12 478 B. Nové runtime/replay prípady: 0. Sémantická úplnosť sa neodvodzuje z nominálnych veľkostí.

DOSBox-X plán: zachytiť reálne resource dĺžky indexov 0..2, výsledné DI po 127 položkách, zápisy transformátora, DS:256A a všetky volania s inými indexmi. Ďalší statický krok: transformátor 0FBA:00D2 a renderer čítajúci DS:3690 pointer tabuľku; runtime index bounds zostávajú otvorené.


## Aktualizácia 13 oblastí

Nové sémantické percento všade N/A: chýba úplný inventár kontraktov/polí/vetiev. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické čísla sú orientačné.

| Oblasť | Predošlý odhad | Nové % | Nový dôkaz | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | 3 nominal graphics blocks and 127 entries | formát a bounds | resource lengths |
| Dátové typy a konštanty | 95 % | N/A | 3 600 B blocks PARTIAL | ostatní writeri | write xrefs |
| Tabuľky a ukazovatele | 93 % | N/A | 3 relocated block bases | resource index | caller bounds |
| Funkcie / ASM / CFG | 90 % | N/A | constant index callers and parser | prirodzená dosiahnuteľnosť | DI and payload trace |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping/VGA stav | framebuffer/DAC |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | helper 04C7:1692 |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | dimension-prefixed bitmap hypothesis | orientation and transform | renderer xrefs |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | pointer restore | tabuľky po LOAD |
| Windows Win16 | 92 % | N/A | bez nového dôkazu | runtime selektory | DS callbacku |
