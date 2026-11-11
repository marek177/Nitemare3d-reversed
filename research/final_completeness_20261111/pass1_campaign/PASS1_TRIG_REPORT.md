# PASS1: kvantované sínusové a kosínusové tabuľky

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Dve počiatočné signed WORD tabuľky po **91 položkách**, spolu **364 B**, sú doložené kvadrantovými helpermi:

| Tabuľka | DS offsety | Obraz, end-exclusive |
|---|---|---|
| S, sínus štvrťvlny | 17E8..189E | 28EF8..28FAE |
| C, kosínus štvrťvlny | 189E..1954 | 28FAE..29064 |

S[0]=0, S[90]=1024, C[0]=1024, C[90]=0. Každá položka a jej SHA rozsahu sú uchované. Reálne škálované sin/cos hodnoty sa od dát líšia najviac približne 0,9864 / 1,0; skript používa numerickú toleranciu 1,000001 iba na túto matematickú kontrolu. **Nedokazuje sa presný generujúci vzorec ani nahraditeľnosť tabuliek volaním floating-point sin/cos.** Algoritmické modely používajú pôvodné WORDy, nie vypočítané náhrady.

## Dva vykonateľné helpery

Sínus **0C7D:07E2**, obraz `[CFB2,CFFE)`, a kosínus **0C7D:082E**, obraz `[CFFE,D04A)`, majú spolu 152 B / 76 inštrukcií. FAR ABI: WORD angle v SS:[BP+6], výsledok signed AX, caller odstráni argument. SI/BP sa obnovujú, DS sa v tele nemení. Lokálne signed porovnania používajú hranice 90,180,270. Pre vstupy 0..359:

```text
sin_fixed(a):
    if a < 90: return S[a]
    if a < 180: return S[180-a]
    if a < 270: return -S[a-180]
    return -S[360-a]

cos_fixed(a):
    if a < 90: return C[a]
    if a < 180: return -C[180-a]
    if a < 270: return -C[a-180]
    return C[360-a]
```

Adresovanie v ASM používa aj posunuté konštanty a záporné indexové vyjadrenia, ale pre uvedenú vstupnú doménu smeruje do týchto tabuliek. Kód nevykonáva všeobecnú normalizáciu modulo 360 ani lokálnu validáciu záporných či príliš veľkých uhlov. Prirodzená doména callerov a použitie výsledkov v pohybe/rendereri zostávajú otvorené. Tabuľkové dáta sa neoznačujú za CRT len pre matematický názov funkcie.

## Reprodukcia a kontrola

`audit_replay_pass1_trig.py IMAGE DECODER_DIR UNICORN_DIR OUT` kontroluje SHA, bázy a rozhodujúce kvadrantové inštrukcie, nezávisle dekóduje celé dva rozsahy a vypíše 182 tabuľkových položiek. Vykonal **1 440 seeded replay prípadov, 0 zlyhaní**: 360 uhlov × dve funkcie × dva load segmenty. Kontroluje výsledok podľa pôvodných tabuliek, SP/BP/SI/DS a nemennosť tabuliek po dávke. Nejde o prirodzený beh hry, test všetkých FLAGS ani dôkaz všetkých možných pamäťových zápisov.

`promote_pass1_fields.py` používa vstup `pass1_io_argument_strings/noncode_intervals.csv`. Všetkých **364 B** prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **PARTIAL 53 982 B, CLASSIFIED ONLY 3 269 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 53 618 / 3 633 / 44 / 0 B.

Prijatý replay súčet kampane je **4 097**, prirodzené runtime testy zostávajú 0. Oba celé ohraničené rozsahy boli začlenené do centrálneho katalógu. DOSBox-X plán: prirodzené uhly, DS a výsledky pri kvadrantových hraniciach, následná aritmetika renderer/pohyb callerov. Ďalší krok: zvyšná susedná tabuľka a caller indexové kontrakty, bez odhadovania jej typu podľa podobnosti prvých hodnôt.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 355 polí/41 zdrojov; 364 B trig tables | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | 2 quadrant helpers; 1440 replay cases | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | 60 počiatočných UI textov | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

