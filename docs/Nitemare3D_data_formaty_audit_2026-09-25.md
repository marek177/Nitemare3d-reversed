# Nitemare3D — Dáta, mapy a formáty: ďalší audit

Dátum: **25. 9. 2026**
Repozitár: **marek177/Nitemare3d-reversed**
Kontrolovaný commit: **9d485e82a84ef1241eff7165c390c82eaff47970**

## Výsledok

V tomto kroku boli lokálne reprodukované a opravené **dve triedy implementačných problémov**: nesprávne prijatie súradníc mimo mapy a nedostatočné oddelenie adresára DAT od neprázdneho obsahu. Päť regresných scenárov na pôvodnom kóde zlyhalo; po oprave prešlo všetkých 16 testovacích skupín. Opravená bola tiež zastaraná časť dokumentácie IMG a spresnený opis všeobecného čítača DAT.

Nejde o nový rozbor pôvodnej EXE ani o dôkaz chyby pôvodnej hry. Analyzované boli dostupné C++ čítače, existujúce odborné zápisy a syntetické súbory. Originálne MAP/IMG/SND/UIF ani NITE3W.EXE neboli v tomto kroku lokálne dostupné a neboli spustené.

**Spoločný údaj 75–80 % zostáva historickým pracovným odhadom.** Tento audit nevytvára nový spoločný menovateľ pre poznanie všetkých formátov. Úspešnosť testov sa nesmie zamieňať za percento reverznej analýzy.

## 1. MAP: súradnice treba kontrolovať pred výpočtom indexu

Pôvodný `LevelMap::at(x,y)` kontroluje iba výsledný lineárny index:

```cpp
return cells.at(y * Width + x);
```

To nestačí na kontrolu dvoch súradníc. Pre `at(64,0)` vznikne index 64, ktorý leží v poli 4096 buniek, ale zodpovedá bunke `(0,1)`. Hodnota mimo mapy preto nevyvolá očakávanú výnimku. Ďalší prípad vzniká pri pretečení neznamienkového `size_t`: riadok `SIZE_MAX / 64 + 1` sa pri násobení 64 zmení na nulu. Toto neznamienkové pretečenie je definované správanie; samotná kontrola nedefinovaného správania ho nemusí odhaliť.

Oprava odmieta `x >= 64` alebo `y >= 64` pred akýmkoľvek násobením. Správanie všetkých 4096 platných súradníc je zachované. Ide o zmluvu bezpečného moderného C++ rozhrania, nie o tvrdenie, že pôvodný Win16 kód pri neplatnej súradnici vyhadzuje C++ výnimku.

### Čo sa na MAP skutočne overilo

Na syntetických archívoch s 1, 10 a 11 mapami test overil počet úrovní, zachovanie všetkých 514 bajtov hlavičky, poradie bajtov stena/objekt a výpočet každej bunky každej načítanej úrovne. Samostatne sa overilo odmietanie krátkej hlavičky, neúplného mapového bloku a nesúladu počtu úrovní s veľkosťou súboru.

Zachovanie 514 bajtov **neznamená** nový dôkaz významu každého bajtu hlavičky. Testuje uchovanie dát a indexovanie. Nepriraďuje nové názvy triedam ani neporovnáva originálne revízie MAP. Zachované je aj doterajšie prijatie archívu s nulovým počtom máp; nie je tým potvrdené, že taký archív prijíma pôvodná hra.

## 2. DAT: obsah sa nesmie začať interpretovať ako adresár

Pôvodný `DatArchive::load()` kontroluje, či každý odkaz leží v súbore, ale neoddeľuje prečítanú hlavičku od neprázdneho obsahu. Na poškodených syntetických vstupoch preto prijal tri neplatné varianty.

| Variant | Syntetický dôkaz | Pôvodný výsledok |
|---|---|---|
| Obsah ako ďalší záznam adresára | Súbor 18 B: prvý descriptor `length=6, offset=6`; bajty obsahu od offsetu 6 zároveň vyzerajú ako `length=6, offset=12`. | Prijal dva záznamy; hlavička končila na 12, hoci obsah začínal na 6. |
| Hlavička ako vlastný obsah | Súbor 12 B, prvý descriptor `length=12, offset=0`. | Prijal celý súbor vrátane descriptora ako payload. |
| Neskorší spätný odkaz do hlavičky | Súbor 30 B, descriptory `(1,24)` a `(24,6)`. | Prijal neprázdny payload prekrývajúci druhý descriptor. |

### Oprava

Čítač sleduje najnižší offset **neprázdneho** obsahu. Pred prečítaním ďalšieho descriptora musí celých 6 bajtov stále ležať pred touto hranicou. Po prečítaní nového nenulového záznamu sa overí, či ním určený obsah nezasahuje do už prečítanej hlavičky.

Nulová dĺžka neoznačuje neprázdny obsah. Preto zostávajú zachované prázdne sloty aj nulový EOF sentinel. Testy tiež overujú zachovanie duplicitných offsetov, výplne medzi hlavičkou a obsahom a nezoradených, neprekrývajúcich sa offsetov. Pôvodná diagnostická metóda `firstPayloadOffset()` sa nemení, ani pri umelom prázdnom zázname s nenulovým offsetom.

Toto je sprísnenie moderného čítača podľa jeho dokumentovaného oddelenia hlavičky a obsahu. Kompatibilita s každým originálnym DAT variantom nebola bez originálnych súborov znovu overená.

### Čo zostáva otvorené

Čítač stále končí pri prvom descriptore s `offset + length == file_size`. Tento krok nevytvára samostatné čítače pevných tabuliek pre SND a UIF, neoveruje všetky indexy zdrojov a nesľubuje zachovanie slotov za týmto ukončovacím descriptorom. Význam zvukových a používateľských zdrojov sa nemení.

## 3. IMG: zastaraný súhrn sa nesmie vydávať za aktuálny formát

`docs/FORMAT_NOTES.md` ešte uvádzal rezervovaný dword na začiatku a jednu zmiešanú tabuľku od offsetu 4. Podrobnejší audit z 23. 9. už opisuje dve obrazové tabuľky:

| Oblasť | Offsety vrátane posledného bajtu | Rozsah |
|---|---|---|
| Obrazové offsety stien | `0x0000–0x03FF` | 256 × 4 B |
| Obrazové offsety objektov | `0x0400–0x07FF` | 256 × 4 B |
| Dolná sekvenčná banka | `0x0008–0x5A07` | 256 × 90 B |
| Horná sekvenčná banka | `0x5A08–0xB407` | 256 × 90 B |

Test vykonal 512 výpočtov offsetov a 512 kontrol klasifikácie prekrytia. Výsledok: dolné selektory **0–22**, teda 23 záznamov, majú neprázdny prienik s obrazovými tabuľkami. Súčet týchto prienikov je **2040 bajtov**. Selektor 22 začína na `0x07C4` a prekrýva posledných 60 bajtov adresárov; selektor 23 začína na `0x081E`, už za nimi.

Tento výsledok overuje aritmetiku existujúceho modelu. **Nevysvetľuje príčinu prekrytia**, nepreukazuje správnu interpretáciu intervalov a počtov snímok na originálnych dátach a nerozhoduje medzi zámerným zdieľaním bajtov a nesúladom EXE/dát.

Dôležitá zostávajúca hranica: `ImgArchive.cpp` stále číta `firstDataOffset` z offsetu 4, teda zo slotu 1 stenového adresára, a hodnotu na offsete 0 nazýva `reservedDword`. Lokálna úprava dokumentácie tento implementačný predpoklad nezamieňa s univerzálnou špecifikáciou. IMG parser nebol v tomto kroku zmenený ani spúšťaný; testovaná bola hlavička s výpočtami rozloženia.

## 4. Vykonané testy

Východiskové kópie ôsmich súborov sa overili podľa Git blob SHA-1. Konkrétne hodnoty sú v `source_manifest.json` sprievodného balíka. Nešlo iba o ručne podobné prepisy: obsah použitý na zostavenie zodpovedá bajtovo pripnutým verziám.

| Zostava | Skupiny | Zlyhania |
|---|---:|---:|
| Pôvodný kód, GCC 14.2, Debug | 16 | **5** |
| Oprava, GCC 14.2, Debug | 16 | **0** |
| Oprava, GCC 14.2, Release `-O2 -DNDEBUG` | 16 | **0** |
| Oprava, GCC 14.2, UBSan | 16 | **0** |
| Oprava, Clang 17, Debug | 16 | **0** |
| Oprava, Clang 17, Release `-O2 -DNDEBUG` | 16 | **0** |
| Oprava, Clang 17, UBSan | 16 | **0** |

Každá úspešná zostava vykonala **109 110 kontrolných podmienok v 16 pomenovaných skupinách**. Nie je to 109 110 nezávislých herných testov. Rovnaká sada bola opakovaná na dvoch kompilátoroch a v troch režimoch; počty sa nesčítavajú do percenta poznania. Kontroly sú aktívne aj pri `NDEBUG`.

Samostatný CMake projekt v balíku sa nakonfiguroval a zostavil v Release; CTest spustil jeho jeden testovací program úspešne. Ide o zostavu troch formátových `.cpp` súborov a jednej testovacej jednotky, nie o celú hru. MSVC, Windows x86/x64, SDL integrácia, pôvodná hra, staršie projektové testy a proprietárne dáta sa v tomto kroku netestovali.

## 5. Obsah opravy a reprodukcia

Patch mení `src/formats/MapArchive.hpp`, `src/formats/DatArchive.cpp`, `docs/FORMAT_NOTES.md` a pridáva `tests/data_format_boundaries_test.cpp` a tento audit do `docs/DATA_FORMAT_AUDIT_2026-09-25.md`. Nemení existujúci hlavný CMake súbor, ostatné subsystémy ani originálne aktíva.

Patch bol lokálne overený príkazmi `git diff --check` a `git apply --check` proti pripnutej základni. Na GitHub sa v tomto kroku nič nezapisovalo.

Samostatný balík:

```sh
cmake -S standalone -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

Rovnaké príkazy sú určené aj pre prostredie s dostupným C++20 nástrojovým reťazcom na Windows; vykonané však boli iba v lokálnom linuxovom prostredí. Pythonový `run_matrix.py` vyžaduje GCC aj Clang a opakuje šesť lokálnych konfigurácií.

Po aplikovaní patchu do repozitára sa dá test zostaviť priamo bez registrácie v hlavnom CMake:

```sh
c++ -std=c++20 -O2 -DNDEBUG -Isrc tests/data_format_boundaries_test.cpp src/formats/MapArchive.cpp src/formats/DatArchive.cpp src/formats/BinaryIO.cpp -o data_format_test
./data_format_test
```

Patch je pripravený na commit uvedený v hlavičke. Pri novších zmenách treba najprv použiť `git apply --check`, nie prepisovať súbory naslepo. Balík obsahuje lokálne logy a `results.json`; tie nie sú súčasťou patchu do repozitára.

## 6. Zdroje a hranice dôkazu

Všetky online zdroje nižšie sú pripnuté ku kontrolovanému commitu; dokumentované tvrdenia o pôvodnej EXE sa tu používajú ako predchádzajúce poznatky, nie ako nový nezávislý disassembly audit.

- [MapArchive.hpp — pôvodný accessor](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/MapArchive.hpp)
- [MapArchive.cpp — archívový čítač](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/MapArchive.cpp)
- [DatArchive.cpp — pôvodný generický čítač](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/DatArchive.cpp)
- [BinaryIO.cpp — kontroly rozsahov a little-endian čítanie](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/BinaryIO.cpp)
- [ImgSequenceLayout.hpp — testované vzorce](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/ImgSequenceLayout.hpp)
- [IMG audit z 23. 9. 2026](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/analysis/nite3w_img_seqdef_2026-09-23.md)
- [ImgArchive.cpp — zostávajúci predpoklad prvého offsetu](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/ImgArchive.cpp)
- [FORMAT_NOTES.md — pôvodný zastaraný opis](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/docs/FORMAT_NOTES.md)
- [PLAYER_COLLISION_RE.md — odlíšenie mapových ID, interných typov a vlastností](https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/docs/PLAYER_COLLISION_RE.md)

## Nasledujúca obsahová úloha

Pre zvýšenie poznania formátov, nie iba spoľahlivosti čítačov, ostáva prioritou zosúladiť konkrétnu dvojicu NITE3W/IMG a sledovať výber dolných sekvenčných záznamov až po načítané snímky. Čisté výpočty offsetov už samy nevyriešia, prečo sa na vzorke prekrývajú rozdielne interpretované dáta.