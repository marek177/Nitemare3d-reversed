# PASS1: saturovaná tangentová magnitúda so sínusovým znamienkom

Obraz SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tabuľka **DS:1954..1A0A**, obraz **[29064,2911A)**, obsahuje 91 signed WORDov, spolu **182 B**. T[0]=0, T[45]=1024, T[89]=T[90]=32767. Pre 0..88 sa od `1024*tan(angle)` líši najviac približne 0,9934. To podporuje interpretáciu kvantovanej saturovanej tangentovej štvrťvlny; presný generujúci zdrojový vzorec nie je dokázaný. Indexy 89/90 sú presne doložená plateau hodnota, nie matematický tangent singularity.

## Zakódované kvadranty

Helper **0C7D:087A**, obraz **[D04A,D096)**, má 76 B / 38 inštrukcií. FAR WORD argument je v SS:[BP+6], signed výsledok AX, caller odstráni argument. Obnovuje SI/BP, DS nemení; všetky FLAGS a ostatné registre nezachováva. Pre platnú doménu 0..359:

```text
signed_tangent_magnitude(a):
    if a < 90: return T[a]
    if a < 180: return T[180-a]
    if a < 270: return -T[a-180]
    return -T[360-a]
```

**Druhý kvadrant je nezáporný**, hoci obvyklý tangent by tam bol záporný. Preto sa helper neoznačuje za štandardný tan pre celý kruh. Napríklad 45/135 dávajú oba +1024; 225/315 oba -1024. Na 90 je +32767, na 270 -32767. Prirodzené callery môžu používať iba časť domény; tá zatiaľ nie je uzavretá. Kód nevykonáva všeobecnú normalizáciu modulo 360 a používa signed porovnania; záporné a veľké vstupy môžu indexovať mimo tabuľky.

## Reprodukcia a replay

`audit_replay_pass1_tangent.py IMAGE DECODER_DIR UNICORN_DIR OUT` kontroluje SHA, tabuľkové hodnoty a adresové konštanty, nezávisle dekóduje celý helper a vypíše všetkých 91 položiek. **720 seeded replay prípadov prešlo bez zlyhania**: 360 uhlov pri dvoch load segmentoch. Model používa pôvodné WORDy a presný kvadrantový vzorec. Kontroluje AX, SP/BP/SI/DS a nemennosť tabuľky po dávke. Nejde o prirodzený runtime ani všeobecnú matematickú tan implementáciu.

`promote_pass1_fields.py` používa vstup `pass1_trig/noncode_intervals.csv`. Všetkých **182 B** prešlo z CLASSIFIED ONLY do PARTIAL. Aktuálne **PARTIAL 54 164 B, CLASSIFIED ONLY 3 087 B, UNKNOWN 44 B, DEEP VERIFIED 0 B**, spolu 57 295 B. Predošlá mapa: 53 982 / 3 269 / 44 / 0 B.

Prijatý replay súčet kampane je **4 817**, prirodzené runtime testy stále 0. Celý helper je samostatne začlenený do funkčného katalógu. DOSBox-X plán: prirodzené caller uhly, následné znamienkové operácie a kvadrantové hranice. Ďalší krok: caller inventár a susedný inverzný uhlový helper bez predpokladu štandardnej atan/tan sémantiky.


## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 356 polí/42 zdrojov; 182 B saturated table | 2 relokačné B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | nonstandard tangent signs; 720 replay cases | writeri/lifetime | pointer watchpointy |
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

