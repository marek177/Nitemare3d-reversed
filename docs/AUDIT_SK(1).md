# NITE3W – audit hlavných systémov, 25. 9. 2026

## Result and exact range

This prechod is **new audit dostupnej C++ reconstruction, its hraničných stavov and matches with already uloženou dokumentáciou reverznej analysis**. Is not to new disassembly originálnej EXE. Original binárka was not v this pracovnom environment sprístupnená; v dvoch prečítaných repozitároch sa pracovalo with rekonštrukciou and auditnými správami. Original NITE3W nor SDL aplikácia sa nespúšťali.

Analyzované source frames:

- `marek177/Nitemare3d-reversed`, commit `9d485e82a84ef1241eff7165c390c82eaff47970`.
- `marek177/Nite3d-win3.11`, commit `791394730187ae0ded48e423fd11aa0d68f70f10`.

**All nine lokálnych zdrojových file is byte verify proti Git blob SHA-1 vrátenému GitHubom.** Súpis contains also size and SHA-256: `source_manifest.json`. `original/` denotes original status these C++ file on uvedených commitoch, NIE original source kódy game.

Five preskúmaných areas: player movement, posúvanie object, prepojenie GUARD/boja, load define and prístup k mape, timing/kalibrácia. Is not complete uzavretie all functions these systémov.

## Súhrnný register zistení

| ID | Area | Finding | Druh evidence | Status lokálnej opravy |
|---|---|---|---|---|
| AND01 | GUARD/boj | Two define `kFreshGuardStrength` v jednom mennom priestore znemožňujú shared preklad dvoch headers. | Preklad exact file, GCC also Clang, obe poradia include. | Corrected locally spoločnou hlavičkou. |
| AND02 | Movement | Checks sa target, nie prejdená dráha; requirement can preskočiť wall. | Reproduced on syntetickej mape. | Algoritmus so far nezmenený. |
| AND03 | Movement | During wall sa netestuje zdokumentovaný player box with polovičným rozmerom 27/64 dlaždice. | Reprodukovaný prienik obálky + comparison with auditom kolízií. | Algoritmus so far nezmenený. |
| AND04 | Movement | Zamietnutý diagonálny pokus nevyužije voľnú os; separate movement after Y prejde. | Dvojica reprodukčných pokusov on same mape. | Algoritmus so far nezmenený. |
| AND05 | PUSH | Two posúvania prijmú same target and neskôr prepíšu its map object byte. | Record all eight aktualizácií. | Neopravené; potrebný kontrakt obsadenosti. |
| AND06 | PUSH | Target obsadený after začatí posúvania sa during prechode to cells znovu neoveruje. | Reproduced vložením object through verejný prístup k mape. | Neopravené; potrebný kontrakt obsadenosti. |
| AND07 | define | Neoverí sa entire hexadecimálny token nor range before zúžením on 16 bitov. | Vstupy `10000`, `-1`, `0005xyz`; reálne load parserom. | Corrected locally. |
| AND08 | define | Duplicitné ID ostanú v table; `find()` returns first record and next zatieni. | Two different records with ID 5. | Local validačná politika duplicity odmieta. |
| AND09 | Mapa | `LevelMap::at(64,0)` returns bunku `(0,1)`; check plochého indexu nenahrádza kontrolu coordinates. | Test addresses/obsahu cells, also pretečenie during extrémnom Y. | Corrected locally. |
| AND10 | Numeric vstupy | `beginPush(..., INT_MIN, 0)` vyvolá nedefinované behavior during `abs()`. | UBSan v GCC also Clang. | Corrected locally without `abs()`. |
| AND11 | Numeric vstupy | `tryMovePlayer(NaN, ...)` prevedie nereprezentovateľnú value on `int`. | UBSan/float-cast-verify v GCC also Clang. | Corrected locally kontrolou konečnosti and boundaries before konverziou. |
| AND12 | Kalibrácia | Model during priemere 2001 ms and vyššom returns `frame_rate=0`. | Vyhodnotenie all 65 536 prijatých values priemeru. | Question for originál; without zmeny vzorca. |

AND02–AND04 konkretizujú **already známy provizórny charakter movement implement**; are not prezentované as objav new original algoritmu. AND05–AND06 dokazujú nekonzistenciu during specific postupnosti call verejného API. Dosiahnuteľnosť tohto súbehu v kompletnej hernej slučke was not verify. AND07–AND11 are errors/medzery moderného code during chybných vstupoch, nie evidence chybných original game data.

## 1. Player movement: what missing between známym pravidlom and kódom

### Function and tok data

`src/game/LevelState.cpp:164`, `LevelState::tryMovePlayer(dx,dy,allowAutoPush)`:

1. Spočíta novú position `nx=x+dx`, `ny=y+dy`.
2. Z nej odvodí jednu cieľovú bunku pomocou `floor()`.
3. call začne tlačenie object v this bunke.
4. Testuje priechodnosť cieľovej cells and kruhovú distance from posúvateľných object.
5. During success stores obidve coordinate; during neúspechu neuloží nor jednu.

Zdokumentované original routines `3:8604` and `3:84F4` sa správajú podstatne otherwise: audit states jednotkové steps, separate skúšanie osí and vedúcu hranu player boxu with polovičným rozmerom 27 jednotiek during 64 units on dlaždicu. `3:8A20` subsequently aktualizuje bunku and during zmene cells vyvoláva event `0x16`.

This prechod znovu necertifikuje assembler these adries; uses stored `docs/PLAYER_COLLISION_RE.md` as reference kontrakt.

### Reprodukcia AND02: preskočenie walls

Syntetická mapa has player v `(1.5,1.5)` and pevnú wall v bunke `(2,1)`. Call `tryMovePlayer(2.0,0.0,false)` returns `true` and stores `(3.5,1.5)`. Testovaná was only prázdna koncová cell. None cell uprostred dráhy sa nenavštívila.

Evidence applies for API and this input; nehovorí, that current ovládač game taký large step bežne passes.

### Reprodukcia AND03: neexistujúca kolízna obálka during wall

During same štarte and wall prejde `tryMovePlayer(0.3,0.0,false)`. Stred sa dostane on X=1.8. Pravá hrana zdokumentovaného boxu by pritom was `1.8 + 27/64 = 2.221875`, therefore already v wall začínajúcej on X=2.

Kruh with value 0.30 v `positionBlockedByPushable()` is not náhradou this obálky: this function sa uses for posúvateľné objects, nie on testovanie player boxu proti wall.

### Reprodukcia AND04: missing posun after voľnej osi

Pokus `(dx,dy)=(0.6,0.25)` smeruje to walls and ponechá Y=1.5. Následný separate pokus `(0,0.25)` prejde on Y=1.75. Function therefore sama nevykonáva separate tests osí nor alternatívny posun after voľnej osi.

### Consequence for completion

Správny integračný target is not only change konštantu `radius`. Needs to vložiť zdokumentované jednotkové krokovanie, test vedúcich hrán, numeric stavy door, touch vedľajšie effects and následný commit cells. Order callbackov, possible zmeny walls/object during testu and boundary rohové cases needs to viesť as separate kontrakty. Priložená bezpečnostná correction this algoritmus nenahrádza.

## 2. Posúvanie object: strata konzistencie mapy

### Functions

`beginPush()` verify momentálne empty target and sets speed and eight remain aktualizácií. V dátovej štruktúre is not rezervácia cieľovej cells. `tickPushables()` aktualizuje coordinate and after prechode to novej cells directly executes `newCell.object = oldCell.object`, without new verify obsadenosti target.

### Reprodukcia AND05

Object with ID 5 starts v `(2,2)`, object with ID 6 v `(4,2)`. Calls posunu doprava and doľava obe prijmú target `(3,2)`.

| Update | X object 5 v units | X object 6 v units | object byte v `(3,2)` |
|---:|---:|---:|---:|
| 1 | 168 | 280 | 0 |
| 2 | 176 | 272 | 0 |
| 3 | 184 | 264 | 0 |
| 4 | 192 | 256 | 5 |
| 5 | 200 | 248 | 6 |
| 6 | 208 | 240 | 6 |
| 7 | 216 | 232 | 6 |
| 8 | 224 | 224 | 6 |

Konečný status: v zozname are two objects on same coordinate, but jedna cell uchováva only ID 6. Is not to viacvláknová race condition; stačí listed order sekvenčných call. Difference okamihu prekročenia boundary during kladnom and zápornom smere is visible already v 4. and 5. aktualizácii.

### Reprodukcia AND06

After prijatí one posunu sa target through `LevelState::at()` obsadí object 7. Štvrtá update ho prepíše object 5. This modeluje hit next subsystému to obsadenosti mapy; is not tvrdenie, that sa to odohralo v original hre.

### Proposed kontrakt, nie neoverená correction

Needs to rozhodnúť, kto vlastní source and target during movement, when sa rezervácia uvoľní and as sa reprezentuje prípadný podkladový predmet. Up to this kontrakt určí opravu. Jednoduché doplnenie `if (newCell.object != 0) return;` by mohlo zanechať coordinate, mapu and count remain aktualizácií v next nekonzistentnom stave. Therefore this part is not v minimálnom patchi.

## 3. GUARD and boj: integračná error and timer stavu 0x13

### AND01: opakovaná define

`GuardSystem.hpp:13` and `CombatSystem.hpp:75` define:

```cpp
inline constexpr std::uint8_t kFreshGuardStrength = 0xFF;
```

Obe deklarácie are v `nitemare3d::game`. During spoločnom zahrnutí oboch file vzniká error `redefinition`. Test zlyhal v GCC 14.2 also Clang 17 and v oboch poradiach zahrnutia. To, that obe values are same and deklarácie use `inline`, konflikt v jednej prekladovej jednotke neodstráni.

Local correction creates `GuardConstants.hpp` and oba original files zahŕňajú jedinú spoločnú define. Name, type, value and rozloženie `GuardRuntimeRecord` remain preserved. Correction is doložená for this dvojicu headers; is not tvrdenie, that was zostavený entire projekt or that neexistujú other konflikty.

### verify boundary behavior existing modelu

For `stepGuardState13()` was verify all 65 536 vstupných values timer, during blokovanom also priechodnom cieli. separate prebehli entire cykly for počiatočné časovače 8–87.

| Timer on vstupe | Timer on výstupe | Result modelu |
|---:|---:|---|
| 9 | 8 | Requirement on movement sound, without pokusu o movement. |
| 8 | 7 | First movement pokus. |
| 1 | 0 | Last movement pokus, still without príznaku ukončenia. |
| 0 | 0 | Termination strategy and requirement prechodu to stavu 2. |

Each entire cyklus z intervalu 8–87 contains exactly eight pokusov o movement. Blokovanie zastaví commit coordinates, nie countdown. Cyklus začínajúci directly on 8 neprejde branch požiadavky on sound. Ukončovací flag sa objaví during next call after dosiahnutí nuly.

This is check existing pomocného modelu and its okrajov. Nepotvrdzuje celú AI, audio system nor zhodu with priebehom original EXE.

## 4. define and prístup k mape

### AND07–AND08: parser

Original C++ parser uses `std::stoul(idHex, nullptr, 16)` and subsequently zúži result on `uint16_t`. Nezisťuje, koľko znakov sa actually prečítalo, nor whether sa value before zúžením zmestila to cieľového typu.

| Token | Pozorované load ID |
|---|---:|
| `10000` | 0 |
| `-1` | 65535 |
| `0005xyz` | 5 |
| `+1` | 1 |

During dvoch define ID 5 zostanú oba lines stored, but `find(5)` returns first. Is slabú validáciu and tiché aliasovanie/zatienenie. Prijatie samotného znamienka plus is question vstupnej politiky; priložená striktná politika neprijíma znamienka. Neoznačujeme ju for novo zistené pravidlo formátu original EXE.

Local correction preverí entire token through `from_chars`, range 0–65535 and jedinečnosť ID. Preserves podporu obyčajných hexadecimálnych tokenov also prefixu `0x`/`0X`; nepridáva nepodložené obmedzenie celej tables on 255.

### AND09: mapa

`LevelMap::at(x,y)` original verifies only `cells.at(y*64+x)`. Therefore X=64, Y=0 prejde as plochý index 64 and returns bunku X=0, Y=1. During extrémnom Y sa moreover can násobenie typu `size_t` obaliť to platného indexu.

Local correction odmietne `x>=64 || y>=64` still before násobením. Otestované were obe error branches and addresses all 4096 platných buniek. read formátu MAP archívu nor meaning all bytes its headers this test does not close.

### AND10–AND11: nedefinované behavior

`beginPush()` odmieta neplatné smery up to pomocou súčtu absolútnych values. For `INT_MIN` already themselves získanie absolútnej values does not have reprezentovateľný result v type `int`. UBSan ohlásil chybu v riadku 118. Correction compares input directly with štyrmi prípustnými smermi.

`tryMovePlayer()` original konvertuje result `floor(NaN)` on `int`. UBSan with kontrolou `float-cast-overflow` ohlásil chybu v riadku 167. Correction before konverziou verify konečnosť result coordinates and príslušnosť to range mapy.

Is umelo vyvolané error vstupy verejného API. None tvrdenie o bežnom výskyte during hraní or zneužiteľnosti sa z nich nevyvodzuje.

## 5. Timing and kalibrácia

### Confirmed behavior modelu

Pomocná function pomalého count increments logický read raz during zmene časového bucketu. Jednorazový prechod 0→1000 ms therefore can 1 step, so far what vzorkovanie after 125 ms can eight krokov. To corresponds to uloženému auditu `3:D70A`, which explicitly opisuje absenciu dobiehania vynechaných krokov.

Test at the same time verify 32-bit obalenie: during čase 536 870 911 ms is pomalý bucket 4 294 967, during 536 870 912 ms klesne on 0. For frame rate 25 was verify analogický prechod 171 798 691→171 798 692 ms. Zmena compare `!=` on obyčajné `>` by tak was not ekvivalentnou náhradou. Themselves tests however nepreverili each possible status kompletného plánovača.

### AND12: nulová frame rate v prijatom range

Kalibračný model accepts all raw priemery from 0 to 65535 ms. Efektívny priemer D is at least 40 ms and frame rate computes as:

```text
floor((1000 + floor(D/2)) / D)
```

For priemer 2000 ms is result 1, for 2001 ms is result 0. Vyhodnotenie entire prijatého intervalu confirm, that nulová value vzniká for each priemer 2001–65535 ms.

When sa nulová frekvencia odovzdá existujúcemu `frame_time_bucket()`, its násobenie produkuje nulu for each time. During inicializovanom nulovom predchádzajúcom buckete sa frame read further nezvyšuje. Is to priamy consequence zobrazených pomocných functions; actual reakcia celej historickej game during takejto kalibrácii remains open.

**Nepridáva sa svojvoľné `max(1, frame_rate)`.** Taká zmena by mohla be rozumnou modernou politikou, but was not by thereby dokázaná verná reconstruction original. On uzavretie needs to verify extrémnu kalibračnú branch, šírky medzivýpočtov and následné usage nulového tempa v original code.

## Pracovné semantic names original routines

These names are derived z already dostupných address auditov. Is not new objavené vstupy nor o tvrdenie, that were v this prechode znovu disassemblované. Väzbu `FUN_1010_xxxx` on NE segment 3 states audit versions Win16.

| Address / existing exportný name | Navrhované pracovné meno | Exact range |
|---|---|---|
| `3:84F4` / `FUN_1010_84f4` | `TestPlayerLeadingEdgeAndTouches` | Priechodnosť dvoch buniek vedúcej hrany and príslušné touch branches. |
| `3:8604` / `FUN_1010_8604` | `StepPlayerMotionWithAxisCollision` | Jednotkové krokovanie and separate kolízne tests osí. |
| `3:8A20` / `FUN_1010_8a20` | `CommitPlayerTileAndEntryEvent` | Svetové/dlaždicové coordinate, MAP pointer and event zmeny cells. |
| `3:1A22` / `FUN_1010_1a22` | `DispatchUseOnAdjacentCell` | Selection susednej kardinálnej cells and rozdelenie vetiev USE. |
| `3:21B6` / `FUN_1010_21b6` | `TryBeginOctantPush` | Počiatočná branch posunu according to smerových tabuliek; nie entire update object. |
| `3:D70A` / `FUN_1010_d70a` | `SampleNominal8HzCounter` | Zmena bucketu → one logický pomalý step. |
| `3:D74A` / `FUN_1010_d74a` | `SampleCalibratedFrameCounter` | Zmena kalibrovaného frame bucketu → one step. |
| `3:D7D0` / `FUN_1010_d7d0` | `CalibrateFromFiveRenderPresentCalls` | Kalibrácia z piatich meraných render/present call. |

Size písmen v name `FUN_*` needs to prispôsobiť konkrétnemu exportu. Priložený package does not change databázu IDA/Ghidra nor nevytvára falošné functional vstupy z vnútorných branch labelov.

## Validácia actually vykonaná

usage kompilátory: GCC 14.2.0 and Clang 17.0.0 on Linuxe. Kontrolované konfigurácie: Debug (`-O0`), Release (`-O2 -DNDEBUG`), UBSan (`-fsanitize=undefined,float-cast-overflow -fno-sanitize-recover=all`). Kontroly v diagnostickom programe remain aktívne also with `NDEBUG`.

| Check | Count | Result |
|---|---:|---|
| Hashová match original C++ zdrojov | 9 file | All súhlasia with Git blob hashmi. |
| Spoločné headers before opravou | 4 preklady | Očakávaná error redefinície, obe poradia v oboch kompilátoroch. |
| Spoločné headers after lokálnej oprave | 4 preklady | Success. |
| Diagnostika original reconstruction | 6 behov | Reprodukcie zistení and modelové kontroly according to očakávania. |
| Diagnostika locally opravenej frames | 6 behov | Corrected input errors odmietnuté; ponechané kolízne/PUSH reprodukcie still platia. |
| Separate error vstupy before opravou | 4 behy | UBSan reprodukoval 2 druhy nedefinovaného behavior v oboch kompilátoroch. |
| Separate error vstupy after oprave | 4 behy | Bezpečné odmietnutie, návratový code 0. |

Main diagnostický beh before opravami vykonal 995 411 kontrol; after lokálnych opravách 995 403. Difference is spôsobený different branch testu očakávaného odmietnutia. **These numbers are not counts functions, dokončených auditov nor meranie pokrytia EXE.** Návratový code 0 diagnostiky mean, that sa reprodukoval očakávaný status including označených chýb; does not mean, that are collisions or posúvanie already correctly.

`validation_results.json` and `logs/` zaznamenávajú 42 invokácií validačnej matice including prekladov and výpisov versions. Doplnkovo passed separate CMake/CTest projekt v Release: 4/4 tests. Patch was aplikovaný v dočasnom Git repozitári and result files sa byte zhodovali with otestovanou lokálnou snímkou. Complete game repository, all its older tests, Windows/MSVC, original game data, entire SDL aplikácia and original Win16 EXE were not testované.

## Files and reprodukcia

`original/` contains exact verify frames deviatich C++ file; `patched/` their locally corrected varianty. `tests/main_systems_probe.cpp` creates own malé text define and mapy. Komerčné game assety nor originálna EXE are not part of package.

Spustenie on stroji with Python 3 and C++20 kompilátorom GCC or Clang:

```sh
python run_audit.py
```

call separate CMake projekt v package zostavuje only these sondy, nie celú hru. Windows zostavenie package nebolo performed.

Patche are separate:

- `01_shared_guard_constant.patch`: jediná define spoločnej konštanty.
- `02_data_validation.patch`: complete validácia ID, duplicít and map coordinates. Is explicitnú modernú validačnú politiku.
- `03_numeric_input_validation.patch`: odmietnutie neplatného smeru and nereprezentovateľných coordinates without nedefinovaného behavior.
- `all_minimal_safety_fixes.patch`: súhrn troch above uvedených zmien.

Patche nezasahujú to časovacích vzorcov, gameplay krokovania nor to algoritmu mapovej obsadenosti during posúvaní. **On GitHub was not urobený none write.**

## What to mean for percentá

Historický working interval **70–85 %** sa this auditom neprepočítava. Nepribudlo new meranie pokrytia celej EXE nor original runtime record. Pribudli reprodukovateľné kontra-príklady, specifically locally bezpečnostné opravy, verify kontraktov pomocných modelov and new exactly formulovaná open question kalibrácie.

Najvyššiu value next hernej integrácie has náhrada provizórneho `tryMovePlayer()` zdokumentovaným jednotkovým movement total with uceleným kontraktom obsadenosti movement object. This work must preserve order kolíznych/touch events, nie only visually podobný movement.

## Primárne projektové podklady

Source cesty and Git hashe are v `source_manifest.json`. On comparison with historickými address were prečítané:

- `marek177/Nitemare3d-reversed@9d485e8`, `docs/PLAYER_COLLISION_RE.md`, blob `cd56924e8540bcb5c9348dddc78ea96d4d8f184f`.
- Same commit, `docs/USE_INTERACTION_RE.md`, blob `5c03321b2cf24641e9aeb8dca50f5f2e5abe5692`.
- `marek177/Nite3d-win3.11@7913947`, `docs/win16/audit-2026-09-24.md`, blob `0f95e2f81e95beb5b6d6aa82b0d32375ef284c05`, usage parts 1–2.3 o identite buildov, count and kalibrácii.

Označenia original statického evidence v these správach are prevzatá proveniencia, nie automaticky new evidence z tohto prechodu.