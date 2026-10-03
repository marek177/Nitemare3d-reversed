# NITE3W renderer – ďalšia analýza, 25. septembra 2026

## Výsledok

Toto kolo rozšírilo prácu o **dve reprodukované chyby v modernom C++ framebufferi**
a **spustiteľný, obmedzený model zdokumentovaných animácií stien**. Neopakuje
predchádzajúci test indexu 512 ani porovnanie 16.16 vzorkovania s delením.

Pôvodný NITE3W.EXE sa v tomto kole znovu nedisassembloval ani nespustil.
Prístupný lokálny ZIP obsahoval zdrojové kódy a testy, nie EXE. Hľadanie podkladov
v pripojenom Drive nevrátilo zhodu a externý binárny balík sa nepodarilo stiahnuť.
Model animácií preto vychádza z existujúceho projektového auditu, nie z nového
nezávislého prečítania inštrukcií. Dostupnosť súborov v inom vlákne nie je ich
sprístupnením tomuto procesu.

**Rozlíšenie dôkazov:** chyby `Framebuffer.cpp` sú priamo reprodukované na
presnej kópii zdroja z GitHubu. Závery o animáciách sú dôsledky opisu v [S4],
overované na novom modeli. Účinky `FUN_1018_3C0C`, presný test času a
8-bitové krajné prípady zostávajú otvorené v pôvodnej EXE.

Na GitHub neboli zapísané žiadne zmeny. Lokálny patch mení iba
`src/renderer/Framebuffer.cpp`; model nie je pripojený do herného runtime.
Zachovaný odhad statického poznania rendereru **80–85 % sa neprepočítava**.

## 1. Potvrdené pretečenie v `fillRect()`

[S1] používa slučky cez celú požadovanú šírku a výšku a volá:

```cpp
setPixel(x + xx, y + yy, colorIndex);
```

Kontrola hraníc je až v `setPixel()`. Sčítanie argumentov však nastáva skôr.
Pri 32-bitovom `int` sa pre `x=INT_MAX`, `w=2` vyhodnotí `INT_MAX+1`;
rovnaký problém vznikne na osi Y. Toto nie je bezpečné orezanie súradníc.

### Reprodukcia

Na framebufferi 8×6 boli oddelene spustené:

```cpp
fb.fillRect(INT_MAX, 0, 2, 1, 7);
fb.fillRect(0, INT_MAX, 1, 2, 7);
```

GCC 14.2 aj Clang 17, oba s UBSan a `-fno-sanitize-recover=all`, ukončili obe
skúšky s návratovým kódom 1 a správou o znamienkovom pretečení
`2147483647 + 1`. Logy: `logs/{gcc,clang}_original_overflow-{x,y}.txt`.
UBSan je podľa primárnej dokumentácie [S5] určený okrem iného aj na tento typ chyby.

**Rozsah tvrdenia:** je to dokázaná chyba C++ metódy na syntetickom krajnom
vstupe. Nie je tým dokázané, že normálna herná mapa takýto vstup vytvorí, ani
že rovnakú chybu obsahuje pôvodná Win16 hra.

### Oprava

Patch najprv odmietne nekladné rozmery obdĺžnika. Potom vypočíta pravý a dolný
okraj v `int64_t`, oreže obdĺžnik na skutočný framebuffer a iteruje len cez
prienik. Sčítanie sa rozširuje **pred** operáciou, nie po nej.

Tým sa odstráni aj zbytočné prechádzanie všetkých pixelov obrovského obdĺžnika
mimo obrazu. Počet zapisovaných pixelov je obmedzený veľkosťou prieniku;
nekoná sa test času založený na odhade rýchlosti CPU.

## 2. Potvrdené nesprávne poradie validácie v konštruktore

[S1] alokuje `indices_` v inicializačnom zozname:

```cpp
indices_(static_cast<std::size_t>(width) * height)
```

Kontrola `width <= 0 || height <= 0` nasleduje až v tele konštruktora.
Vstup `Framebuffer(-1, 1)` preto v oboch testovaných toolchainoch vyhodil
`std::length_error` z vektora ešte pred zamýšľanou validáciou rozmerov.
Nevznikol vektor správne zamietnutý plánovanou správou
`Framebuffer dimensions must be positive`.

Patch používa `checkedPixelCount()` už v inicializačnom zozname. Najprv
skontroluje kladné rozmery, potom možnosť pretečenia násobku v `size_t`, a až
potom odovzdá veľkosť vektoru. Pri extrémne veľkom kladnom rozmere sa stále
môže legitímne objaviť výnimka vektora alebo nedostatok pamäte; patch nesľubuje
ľubovoľne veľké alokácie.

Otestovaných bolo 8 nulových/záporných kombinácií vrátane INT_MIN. Všetky
opravené behy vrátili zamýšľanú validačnú výnimku bez pokusu o pixelovú alokáciu.

## 3. Časovanie animácií: jeden krok na splatné volanie

[S4] uvádza, že `FUN_1010_65A6` pri splatnosti zvýši snímku a uloží
`gameClock + interval` do termínu ďalšej zmeny. Z tohto opisu vyplýva, že
jediné splatné volanie **automaticky nedobieha všetky zmeškané snímky**.

Modelový príklad bez pretečenia hodín:

| Údaj | Hodnota |
|---|---:|
| Stará snímka | 0 |
| Počet snímok | 10 |
| Starý termín | 100 |
| Aktuálny čas | 137 |
| Interval | 10 |
| Snímka po jednom splatnom volaní podľa [S4] | 1 |
| Nový termín | 147 |

Alternatívny algoritmus `while (now >= deadline) { ++frame; deadline += 10; }`
by spracoval termíny 100, 110, 120, 130 a skončil na snímke 4 s termínom 140.
Nie je to ekvivalentný prepis dokumentovaného postupu.

**Obmedzenie:** jeden krok je tu na jedno volanie pomocníka. Nie je tým
stanovený počet jeho volaní na jednu hernú snímku, jednu stenu ani jeden span.
Pri nulovom intervale a opakovane dodanom `due=true` postúpi model opäť aj
pri rovnakom čase. Či originál považuje presnú rovnosť termínu za splatnosť,
je otvorené: model preto úmyselne prijíma `bool due` od volajúceho.

32-bitový súčet času a intervalu je v modeli explicitný. Test pretečenia
`0xFFFFFFFA + 10 = 4` overuje len tento súčet, nie pôvodný komparátor hodín.
Na úplnú rekonštrukciu treba presné inštrukcie porovnania, znamienkovosť a
správanie pri obtečení čítača.

## 4. Trieda 0x07: nulová snímka je stabilný stav

Podľa [S4] sa najprv zvýši snímka a následná hodnota 1 sa vráti na 0.
Preto vstupná snímka 0 vedie späť na 0. Samotné ďalšie splatné volania ju
nevyvedú z nulového stavu.

Pre štyri snímky a bežnú platnú doménu:

| Vstupná snímka | Bežná cyklická trieda | Trieda 0x07 |
|---:|---:|---:|
| 0 | 1 | 0 |
| 1 | 2 | 2 |
| 2 | 3 | 3 |
| 3 | 0 | 3 |

Nula sa správa ako osobitný pokojový stav a posledná snímka ako stav
zastavenia. **To je opis prechodov, nie nové potvrdenie názvu herného objektu.**
Nepriraďujem automaticky triede dvere, ovládací panel, teleport alebo knižnicu.

Model otestoval 300 po sebe idúcich splatných krokov z nuly pre každý počet
snímok 1…255: spolu **76 500 krokov** bez opustenia nuly.

Praktický dôsledok pre ďalšie RE: pokiaľ sa táto trieda vo viditeľnej hre
aktivuje z nuly, niečo mimo tohto samotného prechodu musí zmeniť stav — napríklad
zapísať nenulovú snímku alebo zmeniť triedu. Presný aktivačný zápis do `VEC+03`
ani jeho volajúci ešte neboli v tomto kole dohľadané. Označenie „externý spúšťač“
je pracovný cieľ hľadania, nie identifikovaná funkcia.

## 5. Sekvenčný záznam: prvá snímka a dĺžka úseku

Opis [S4] používa low+high ako hranicu a pri novom výbere načíta low do
aktuálnej snímky. V tejto konkrétnej vetve to podporuje význam:

```text
low  = prvá snímka úseku
high = počet snímok v úseku; 0 vyradí položku z nového výberu
hraničná hodnota = low + high
```

Názvy `startFrame` a `length` sú **významové odvodenie z opísaných operácií**,
nie pôvodné symboly alebo novo prečítané mená položiek IMG. Označenie low iba
ako „počet snímok“ by nezodpovedalo jeho použitiu pri nastavení novej snímky.

Príklad syntetických dát: položka 0 má `{2,3}`, položka 6 má `{8,2}`.
Model začne v snímke 2 položky 0 a dá postupnosť:

```text
2 -> 3 -> 4 -> nové rozhodnutie -> 8
```

Pri novom rozhodnutí bola dodaná náhodná postupnosť s maskovanými kandidátmi
1, 3, 6. Prvé dve položky sú zakázané, tretia povolená, preto model spotreboval
tri hodnoty generátora. Volanie, ktoré iba prejde 2→3 alebo 3→4, nespotrebovalo
žiadnu hodnotu generátora.

To je dôležité pri presnom prehrávaní náhodného priebehu: aj odmietnutý kandidát
spotrebuje hodnotu, pokiaľ má slučka správanie opísané v [S4]. Či má pôvodný
generátor spoločný stav s inými systémami a aké je jeho rozdelenie, zostáva otvorené.

Model prešiel **255 neprázdnych masiek povolených položiek × 64 dvojíc kandidátov
= 16 320 skúšok**. V 4 544 dvojiciach boli oba kandidáty zakázané: model vrátil
`needMoreRandom`. Nie je to tvrdenie, že originál po dvoch pokusoch skončí.
Je to ukončenie konečnej dodanej testovacej postupnosti.

Pre tabuľku s ôsmimi nulovými high bajtmi neexistuje prijateľný kandidát.
Validátor modelu to rozpozná bez nekonečnej slučky. **Nie je preukázané, že
niektoré originálne WALLS/IMG dáta takú tabuľku používajú alebo že sa jej vetva
v origináli vôbec vykoná.** `noEnabledSequence` je diagnostika modelu, nie
rekonštruovaná návratová hodnota pôvodnej funkcie.

## 6. Trieda 0x2D: požiadavka na koncový efekt nie je zaručene jednorazová

[S4] uvádza volanie `FUN_1018_3C0C` pri dosiahnutí hranice a následné držanie
poslednej snímky. Pri nezmenenom renderClass a deskriptore sa teda táto
požiadavka môže opakovať v ďalších splatných volaniach.

Model s count=4, interval=10 a počiatočnou snímkou 0:

| Splatné volanie | Snímka po kroku | Požiadavka na efekt |
|---:|---:|---|
| 1 | 1 | Nie |
| 2 | 2 | Nie |
| 3 | 3 | Nie |
| 4 | 3 | Áno |
| 5 | 3 | Áno |
| 6 | 3 | Áno |

Model emitoval tri požiadavky v šiestich volaniach. **Nevykonal tri pôvodné
volania 3C0C.** Vedľajšie účinky pôvodnej funkcie môžu zmeniť mapu, triedu,
stav VEC či ďalšie podmienky, takže tvrdiť bez nich neobmedzené opakovanie v
skutočnej hre by bolo nesprávne.

Praktický dôsledok: do portu nemožno svojvoľne pridať `alreadyFinished` a tým
potlačiť ďalšie volania. Najprv treba dohľadať celý kontrakt `3C0C`.
Naopak, model nesmie túto funkciu nahradiť vymysleným „otvor dvere“.

## 7. Rozsah testov a výsledky

| Sada | Rozsah v jednom behu | Výsledok |
|---|---:|---|
| Opravené fillRect | 14 400 obdĺžnikov | PASS |
| Porovnanie pixelov s nezávislým 64-bitovým membership predikátom | 691 200 pixelov | PASS |
| Neplatné rozmery konštruktora | 8 kombinácií | PASS |
| Zachovanie paletovej konverzie AARRGGBB | 256 položiek | PASS |
| Základné modelové prechody 4 tried, count 1…255 | 130 560 prechodov | PASS |
| Stabilita nulovej snímky triedy 0x07 | 76 500 krokov | PASS |
| Sekvenčný výber nad neprázdnymi maskami | 16 320 postupností | PASS |

Základné modelové prechody testujú osobitne nesplatné aj splatné volanie.
Počet 130 560 označuje konfigurácie count/frame/class, nie počet inštrukcií EXE.

Obe sady prešli cez **GCC 14.2.0 aj Clang 17.0.0** v konfigurácii Release
(`-O2 -DNDEBUG`) aj s ASan/UBSan (`-O1 -g`, bez pokračovania po chybe).
Vždy boli zapnuté `_GLIBCXX_ASSERTIONS`; vlastné CHECK sú aktívne aj v Release.
V týchto zostaveniach neboli vypísané kompilátorové varovania. Samostatný CMake
Release beh: **2/2 CTest testy prešli**. Všetky skúšky prebehli na Linux x86-64,
nie v pôvodnom Win16 prostredí ani na používateľovom Windows 11.

Výsledky modelu potvrdzujú zhodu s jeho explicitnými pravidlami a invariantmi.
**Nenahrádzajú nezávislé diferenciálne porovnanie s pôvodnou EXE.** Opakovania
cez kompilátory sa nesčítavajú ako nové unikátne vstupy.

Logy sú v `logs/`, strojovo čitateľný prehľad v `logs/matrix.json`, vybraté
priebehy v `logs/animation_traces.txt`. Očakávané zlyhania pôvodného zdroja sú
zachované oddelene; neboli zatajené v úspešnej testovacej sade.

## 8. Súbory a použitie

- `framebuffer_safety.patch`: lokálna oprava iba Framebuffer.cpp.
- `patched/renderer/Framebuffer.cpp`: opravený súbor.
- `original/`: presné tri potrebné zdroje z pripojeného GitHubu.
- `include/WallAnimationEvidenceModel.hpp`: model, nie náhrada runtime hry.
- `analysis/DOCUMENTED_ANIMATION_RULES.md`: zdrojové pravidlá a výslovné hranice modelu.
- `tests/`: regresné testy a oddelený reproduktor pôvodných chýb.
- `run_audit.py`: overenie zdrojových hashov a behy GCC/Clang.

Zostavenie testov bez SDL, herných dát a siete:

```sh
cmake -S . -B build/local -DCMAKE_BUILD_TYPE=Release
cmake --build build/local --config Release
ctest --test-dir build/local -C Release --output-on-failure
```

Rozšírená matica vrátane reprodukcie pôvodných chýb:

```sh
python run_audit.py
```

Patch v koreňovom adresári Nitemare3d-reversed:

```sh
git apply --check framebuffer_safety.patch
git apply framebuffer_safety.patch
```

Aplikovateľnosť na zachytený zdroj, aplikácia aj byte-to-byte porovnanie
výsledku boli otestované. Patch nepridáva automaticky nové testy do CMake
pôvodného herného repozitára. Verejné mutable `indices()` API naďalej umožňuje
volajúcemu porušiť rozmerový invariant zmenou veľkosti vektora; táto ďalšia
zmena API nie je predmetom minimálnej opravy.

## Zdroje

[S1] `src/renderer/Framebuffer.cpp`, blob
`4f03fa7c0a9755058fe04ab3d5c4d30be451020c`.

[S2] `src/renderer/Framebuffer.hpp`, blob
`f8f4b7091d6e646acff61e0194445653181a7bce`.

[S3] `src/formats/Pcx8.hpp`, blob
`f2d0e9374907edd58cedc0397b59e7e395811482`.

[S1–S3] repozitár `marek177/Nitemare3d-reversed`, zachytený stav stromu
`9d485e82a84ef1241eff7165c390c82eaff47970`. Lokálne Git blob hashe sa zhodujú
s výsledkami konektora. Presné adresy a SHA-256 sú v `source_manifest.json`.

[S4] `analysis/nite3w_renderer_2026-09-23.md`, blob
`253c1f84166386761f3669aa419371315bcee4d9`, sekcia `FUN_1010_65A6`.
Cieľ uvedený v audite: NITE3W.EXE v1.10,
SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
Tento hash označuje cieľ staršieho auditu, nie novo získaný EXE v tomto balíku.

[S5] Primárna dokumentácia LLVM/Clang: UndefinedBehaviorSanitizer,
`https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html`, overená 25. 9. 2026.