# PASS1: class7 tabuľka, stavový text a počítadlo

Dávka typuje **157 B v 10 poliach**. Statické dôkazy zahŕňajú konzumentov textov a reálne sekundárne class tabuľky MAP. Kontrolovane sa vykonáva iba šesťinštrukčný counter prefix. Úroveň PARTIAL; celé UI, class7 správanie a prirodzené call poradie nie sú uzavreté.

## Vstupy a presné dáta

Image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Skript overí identity, presné bajty polí a vybrané pôvodné inštrukcie nezávislým dekóderom. Kanonické DS=2771h je podmienka dátového mapovania.

| Pole | Image interval, koniec exclusive | Typ / dôkaz v CS 083D |
|---|---|---|
| DS:1516 | [28C26,28C29) | 3 BYTE: 100,10,2; indexed read 212F po odčítaní cached class7 base |
| DS:151A | [28C2A,28C2C) | mutable WORD initial FFFF; epizódový key CMP/MOV 20FD/2103 |
| DS:151C | [28C2C,28C2E) | mutable WORD initial 0; INC, CWD, signed IDIV20 v 2520..252D |
| DS:151E | [28C2E,28C33) | NUL text `none`, presné 5 B kopírovanie |
| DS:1523 | [28C33,28C38) | druhý NUL text `none`, 5 B |
| DS:1528 | [28C38,28C3D) | tretí NUL text `none`, 5 B |
| DS:152D | [28C3D,28C3F) | NUL text `R`, vybraný v 2786 |
| DS:152F | [28C3F,28C41) | NUL text `S`, vybraný v 278C |
| DS:1531 | [28C41,28C46) | NUL text `V2.0`, sprintf argument 2790 |
| DS:1536 | [28C46,28CC4) | 126 B NUL status format, 2793 → CRT sprintf 278C |

Samostatný nulový BYTE **[28C29,28C2A)** sa nepromuje. Nie je dokázaný ako štvrtý prvok tabuľky ani padding. DS:1516 sa číta cez dynamický index bez lokálneho guardu; tri nominálne prvky podporujú reálne MAP dáta, nie všeobecnú bounds garanciu pre iné mapy.

## Reálne MAP a cache

V MAP.1/2/3 sú sekundárne triedy presne v súborovom [258,514). Vo všetkých troch sú class7 ID **59,60,61**, preto relatívne indexy sú 0,1,2. `assets.csv` uchováva SHA celých súborov a týchto tabuliek. Skript ich porovnáva s reálnymi bajtmi; nečíta iba starší report.

V 20FA..2111 sa epizóda 626A porovnáva s key 151A. Pri zmene sa key aktualizuje a volá sekundárny class search 00F7:004E s DWORD 7; AL sa uloží do BSS BYTE 3637. Neskôr sa tento base odčíta od aktuálneho mapového ID a výsledok indexuje 1516. Výsledný BYTE sa porovná s 4189 a ovplyvní nasledujúcu hernú vetvu. Celý search ani ďalšie efekty tu nie sú vykonané; význam hodnôt 100/10/2 ako konkrétneho herného pravidla zostáva otvorený.

## Stavový text

Tri samostatné `none` texty sa kopírujú MOVSD+MOVSB, presne 5 B vrátane NUL, na začiatok cieľového recordu a na +0Ah/+13h. Celá record semantika nie je doložená len týmto initializerom; preto sa nenazývajú automaticky keys/cards/panels bez ďalšieho producer auditu.

Status format obsahuje titul/verziu, epizódu/level, polohu, cheat režimy, zostávajúcich guardov/panely a nenájdené keys/cards. Konkrétne R/S sa volí podľa nulového/nenulového DX:AX query 083D:29CA(1). Texty sú odovzdané do near sprintf a výsledok SS bufferu do 0D29:0720. Nevydáva sa to za overenie dynamických údajov, kapacity bufferu alebo úplnej sprintf sémantiky. Presný 126 B text a jeho range SHA sú zachované v image a `data_fields.csv`.

## Exhaustívny lokálny counter replay

Prefix **083D:2520..252F, image [0A8F0,0A8FF)** má 15 B / 6 inštrukcií. Replay končí pred JNE v 252F; predchádzajúci sound call a nasledujúce efekty sa nevykonávajú.

```text
WORD[151C] = (WORD[151C] + 1) & FFFF
AX = WORD[151C]
DX:AX = sign_extend(AX)
AX,DX = signed_divide(DX:AX,20)  // quotient,remainder
ZF = (DX == 0)                  // OR DX,DX
```

Testuje sa znamienkovo interpretovaný nový WORD, nie neobmedzený unsigned counter. Väčšina nulových zvyškov je vzdialená 20 inkrementov, ale cez signed wrap sú hodnoty +32760 a −32760 vzdialené **16** inkrementov. Táto lokálna aritmetika bola overená; nie je to dôkaz prirodzenej frekvencie volania, trvania v sekundách ani toho, že hra tak dlho beží bez resetu countera.

`audit_replay_pass1_status_data.py IMAGE INVENTORY DECODER EMULATOR MAP_DIR OUT` vytvára data fields, static contexts, asset ledger, prefix ASM, cases a summary. **65548 prípadov, 0 odchýlok** = všetkých 65536 starých WORD pri load 0 + 12 boundary prípadov pri load 1000h. Kontroluje sa nový WORD, signed quotient, signed remainder a ZF. Prefix nemá segmentové relokačné operandy ani callee; DS je explicitne nastavené. Neexistuje mock a žiadne pôvodné runtime I/O sa nevykoná. SHA cases `237f2007155887eb9cad6f74d0e7c50f0a4c53c3e32d300e4abdfb4d87db4229`.

## Meranie

Presne 157 B CLASSIFIED ONLY → PARTIAL. Mapa: **56280 B PARTIAL, 971 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá kontrola overila 803 intervalov, SHA a presné členstvo bez dier/prekryvov. SHA mapy `29fa9ad5aea2b71e17ad52eea6118f7739ab89a29da8690c0384dcabab2ac8f9`. Integrita mapy nie je dôkaz úplnej sémantiky.

Katalóg zostáva 90 funkčných rozsahov, 3235 inštrukcií / 8125 B; nový prefix sa nepočíta ako celá funkcia. Typované dáta celého obrazu 57166 B, historického NON-CODE 56278 B a 2 netypované PARTIAL relokačné bajty. Controlled replay 679723 zahŕňa túto novú cadence dávku; osobitne zostáva 65548 starších smerových normalizačných prípadov. Zhodné počty dvoch odlišných dávok neznamenajú duplicitné testy. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového %: uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, nové percentá N/A, predošlé orientačné. Exhaustívny WORD prefix nie je exhaustívny audit celého UI alebo hry.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | secondary class7 ID59..61 v 3 MAP | custom domény | class search bounds |
| Dátové typy a konštanty | 95 % | N/A | 157 B / 10 polí | nulový susedný BYTE | 28C29 referencie |
| Tabuľky a ukazovatele | 93 % | N/A | 3 BYTE a epizódový key | alias writeri | cache reset ledger |
| Funkcie / ASM / CFG | 90 % | N/A | 15 B prefix a vybrané kontexty | celé funkcie | 2512 closure |
| RNG | 97 % | N/A | bez nového dôkazu | ordering | DEMO trace |
| Scheduler | 96 % | N/A | signed IDIV20 wrap efekt | prirodzená cadence | counter call trace |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | driver ABI | input closure |
| Renderer / VGA | 94 % | N/A | status format spotrebovaný | skutočný text | sprintf/display |
| GUARD / bossovia | 93 % | N/A | status labels odlíšené | údaje producentov | status record |
| Zbrane / projektily | 92 % | N/A | class7 hodnota porovnaná s4189 | herný význam | 20F3 vetva |
| Sprity / HUD / paleta | 92 % | N/A | tri presné 5 B initial texty | record identity | initializer closure |
| SAVE / LOAD | 92 % | N/A | epizódový cache stav oddelený | reset | LOAD writer ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | status/cadence parity | Win match |

## Runtime testy na vykonanie

Zachytiť prirodzený counter a reset pri NEW GAME/LOAD, overiť reálne následné efekty pri nulovom zvyšku. Class7 mapové ID korelovať s hodnotami 100/10/2 a writerom 4189. Status text porovnať s produkovaným recordom a hranicami SS bufferu. DOSBox-X vykonanie a Win16 parity zostávajú otvorené.
