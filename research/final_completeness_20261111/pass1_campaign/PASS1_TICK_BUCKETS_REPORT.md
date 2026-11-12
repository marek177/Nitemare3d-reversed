# PASS1: časové pásma a počítadlá schedulera

Táto dávka pridáva 16 B typovaných dát a dve rekonštruované DOS 2.0 funkcie. Úroveň PARTIAL: pôvodné telá boli kontrolovane vykonané, ale prirodzená sekvencia schedulera, všetci alias writeri a runtime parity zostávajú otvorené.

## Presné adresy a dôkazy

Kanonický image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; historický inštrukčný inventár SHA-256 `a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a`. Reprodukčný skript pripína tieto vstupy, porovnáva bajty každého štartu a rekonštruuje oba CFG nezávislým 16-bitovým dekóderom.

| Funkcia | Image interval, koniec exclusive | Kód |
|---|---|---:|
| 0BDE:00D4 | [0BEB4,0BEF3) | 63 B / 17 inštrukcií |
| 0BDE:0114 | [0BEF4,0BF35) | 65 B / 17 inštrukcií |

Medzi funkciami je 1 B mimo ich CFG, neoznačený ako vykonaná inštrukcia. Obe funkcie majú ENTER 4, DWORD argument na SS:BP+6, výsledok DX:AX a FAR RETF bez odstránenia argumentu. BP/DS/SP sú v modeli overené; EAX/ECX/EDX a príznaky sú pracovné. Nevolajú externé funkcie, nepoužívajú ES ani nepriame skoky. CFG každej funkcie má jediný podmienený skok, ktorý preskočí aktualizáciu stavu pri nezmenenom pásme.

| Pole pri DS=2771h | Image interval | Typ / pôvodná hodnota | Konzument |
|---|---|---|---|
| DS:16F6 | [28E06,28E0A) | mutable DWORD / 0 | INC DWORD a návrat DX:AX v 00D4 |
| DS:16FA | [28E0A,28E0E) | mutable DWORD / 0 | porovnanie a zápis posledného pásma v 00D4 |
| DS:16FE | [28E0E,28E12) | mutable DWORD / 0 | INC DWORD a návrat DX:AX v 0114 |
| DS:1702 | [28E12,28E16) | mutable DWORD / 0 | porovnanie a zápis posledného pásma v 0114 |

Sú to štyri 32-bitové skaláre, nie segment:offset ukazovatele. Presné hranice vychádzajú z DWORD operandov; pôvodná nulová výplň sama o sebe nie je klasifikačný dôkaz. DS:3CC2 je signed WORD vstup konfigurovateľného výpočtu; predchádzajúca defaults rutina ho nastavuje na 25, ale všetky prirodzené hodnoty nie sú touto dávkou uzavreté.

## Algoritmus

```text
bucket_8(time_DWORD):
    q = ((time_DWORD << 3) & FFFFFFFF) / 1000  // unsigned division
    if q != DWORD[16FA]:
        DWORD[16FA] = q
        DWORD[16F6] = (DWORD[16F6] + 1) & FFFFFFFF
    return DWORD[16F6]

bucket_configured(time_DWORD):
    rate32 = sign_extend_16_to_32(WORD[3CC2])
    product = low32(unsigned_MUL(rate32, time_DWORD))
    q = product / 1000  // unsigned division, EDX explicitly cleared
    if q != DWORD[1702]:
        DWORD[1702] = q
        DWORD[16FE] = (DWORD[16FE] + 1) & FFFFFFFF
    return DWORD[16FE]
```

Počítadlo sa zvýši presne raz za pozorovanú zmenu pásma, bez ohľadu na veľkosť skoku. Pri sekvencii vstupov 0,125,125,1000 v bucket_8 sú pásma 0,1,1,8 a počítadlá z nuly 0,1,1,2. Funkcia nedobieha sedem preskočených pásiem. Zníženie pásma tiež spôsobí increment; pri pretečení počítadla sa výsledok modulo 2^32 vráti na nulu. Pri rate=0 sa pásmo ustáli na 0, čo ešte môže raz zvýšiť počítadlo, ak predchádzajúce pásmo bolo nenulové.

Konfigurovaná vetva používa MOVSX pred unsigned MUL, potom zahodí horných 32 bitov produktu a vynuluje EDX pred DIV. Nie je ekvivalentná neobmedzenému matematickému `time * rate / 1000`. Napríklad rate=−1 a time=1 vytvoria q=4294967. Táto syntetická hodnota je dôkazom aritmetiky, nie dôkazom prirodzeného záporného nastavenia hry.

## Volania a širší scheduler

Dodaná inštrukčná inventúra obsahuje dve priame volania: 0BDE:03E5 → 00D4 a 0BDE:041F → 0114. Obe používajú PUSH CS + NEAR CALL na FAR-return funkciu a caller odstraňuje DWORD argument. Predchádzajúci caller úsek uloží výstup cached clock 0094 do SS:BP−4/−2 a práve tento DWORD odovzdá obom funkciám. Medzi tým samostatne zavolá sample 0018 a uloží iný čas do BP−8/−6.

Výsledky ukladajú do DS:3672/3676 a porovnávajú s DWORD limitmi DS:1738/173C. To staticky spája funkcie so schedulerom; úplný loop, prirodzené tempo, význam oboch task skupín a vplyv obnovovania cached clock sa tým neuzatvárajú. Žiadny výsledok tejto dávky nie je vydávaný za úplnú gameplay alebo DEMO parity.

## Reprodukcia a meranie

`audit_replay_pass1_tick_buckets.py IMAGE INVENTORY DECODER EMULATOR OUT` vytvára dve ASM CSV, `direct_callers.csv`, `data_fields.csv`, `cases.csv`, `summary.json`. Pôvodné funkcie sa vykonávajú bez mockov pri load bázach 0/1000h s aplikovanými EXEPACK relokáciami. Argumenty, stav a rate sú explicitne seedované.

**90324 volaní, 0 odchýlok** = 2 load bázy × 9 kombinácií entry/rate × 5018 vstupov v štyroch sekvenciách. Zahrnutá je súvislá sekvencia 0..5000, skoky a poklesy času, veľké DWORD hodnoty, pretečenie počítadla z FFFFFFFE a nezmenený nenulový stav. Konfigurované rates −32768,−1,0,1,8,25,1000,32767. Nejde o exhaustívny kartézsky súčin všetkých DWORD vstupov, DWORD stavov a WORD rates.

Presne 16 B prešlo CLASSIFIED ONLY → PARTIAL. Mapa teraz obsahuje **55068 B PARTIAL, 2183 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57295 B. Nezávislá partition kontrola potvrdila 710 intervalov, ich SHA a presné členstvo bez dier/prekryvov; sémantickú úplnosť tým nepreukazuje. SHA mapy `97f48eac36bd115f151348b749da2e683b220393919641bf27242c7f33877af8`.

Centrálny katalóg: 75 funkčných rozsahov, 2599 inštrukcií / 6437 B, 55954 B typovaných dát celého obrazu, 55066 B typovaných historických NON-CODE dát; zostávajú 2 PARTIAL netypované relokačné bajty. Controlled replay súčet 499899 plus osobitne 65548 normalizačných prefixových prípadov. Prirodzené runtime testy 0. GitHub snímka 52924ebf849dd79d15af9d7c164b8304f50cae87 túto dávku ešte neobsahuje.

## Aktualizácia 13 oblastí

Metodika nového sémantického %: počet dôkazmi uzavretých jednotiek / úplný inventár oblasti. Menovatele chýbajú; nové percentá preto N/A. Predošlé čísla sú historické orientačné odhady. Počty prípadov ani partition integrita nenahrádzajú túto metodiku.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | úplný inventár | zostávajúce intervaly |
| Dátové typy a konštanty | 95 % | N/A | 16 B / 4 DWORD polia | alias writeri | state write ledger |
| Tabuľky a ukazovatele | 93 % | N/A | časové skaláre oddelené | susedné limity | DS:1738/173C |
| Funkcie / ASM / CFG | 90 % | N/A | 128 B / 34 inštrukcií | širší caller loop | rekonštruovať scheduler |
| RNG | 97 % | N/A | bez nového dôkazu | prirodzené poradie | DEMO stopa |
| Scheduler | 96 % | N/A | increment raz za zmenu pásma | task skupiny / tempo | caller 03CC.. |
| DEMO a vstupy | 96 % | N/A | cached čas ako argument | prirodzené ordering | runtime clock trace |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | render stopa |
| GUARD / bossovia | 93 % | N/A | bez nového AI dôkazu | lifecycle | health updater |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | effect producer | damage caller |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | asset identity | descriptor producer |
| SAVE / LOAD | 92 % | N/A | mutable tick state oddelený | persistencia | SAVE ledger |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | tick parity | Win scheduler match |

## Runtime testy na vykonanie

Zaznamenať prirodzené argumenty oboch funkcií, DS:3CC2 a posledné pásma/počítadlá pri bežnom behu, pauze, pomalom frame a DEMO. Rozlíšiť preskočené pásma od počtu vykonaných taskov. Overiť reset stavu pri NEW GAME/LOAD a správanie pri zmene rate. Následne overiť DOS/Win16 rozdiely v scheduler timing. DOSBox-X vykonanie zostáva otvorené.
