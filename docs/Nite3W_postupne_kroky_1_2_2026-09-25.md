# Nite3W — postupné riešenie bodov 1 and 2, príprava bodu 3

Date: **25. september 2026**  
Repository: `marek177/Nitemare3d-reversed`  
Exact base: `fadb68316a19d9673d759998afffdea7035cfb31`

## Súhrn result

**Locally closed v range moderných auxiliary interface:** safe bit operations inventory, safe map classes kľúčového warpu and subtract projectile coordinates. Pribudli persistent regresné test independent from vypínateľného `assert`.

**Pripravené, but nie entire integračne verify:** registration all koreňových test targets through CTest. V current CMake is 22 existing test; patch adds three new, therefore zamýšľa registrovať 25. Actually zostavené and run were **three new test programy**, v four combination GCC/Clang and Debug/Release. Entire koreňový project, `n3d_core`, SDL viewer nor 22 older test programov sa v this kroku nezostavovali.

**Original NITE3W.EXE sa nespúšťal nor novo nedekódoval.** Is opravy and verify rekonštruovaného C++ code. Is not to evidence matches original game, new meaning unknown fields nor zvýšenia percenta static poznania EXE. GitHub sa nemenil.

## 1. Inventory and kľúčové warpy

### 1.1 Safe bit operations

`hasInventoryBit()` and `grantInventoryBit()` check `bit >= 8` before posunom. Invalid read returns `false`; invalid write mask does not change. Valid bits 0–7 have nezmenené behavior.

Z original headers sa error znovu reprodukovala through UBSan: during index 32 nastal posun presahujúci width type. New regresný test checks read, add bitu also idempotentnosť add on all **65 536 dvojiciach mask × index**.

### 1.2 New correction nadväznosti class → bit → inventory

Predošlý patch only ohraničoval itself posun. `warpKeyBitForClass()` still return difference `class - 0x19` also for classes mimo 0x19–0x1C. Some incorrectly classes tak create valid index obyčajného inventory bitu.

Following results are directly reproduced sondou nad original also corrected header. V column read sa uses mask `0xFF` and v column add initial mask nula:

| Class | Is kľúčový warp? | Original bit | Bit after oprave | Original read / add | After oprave |
|---|---|---:|---:|---|---|
| `0x19` | yes | 0 | 0 | true / `0x01` | nezmenené |
| `0x1C` | yes | 3 | 3 | true / `0x08` | nezmenené |
| `0x1D` | nie | 4 | `0xFF` | true / `0x10` | false / `0x00` |
| `0x20` | nie | 7 | `0xFF` | true / `0x80` | false / `0x00` |

Corrected function preserves return type `uint8_t`. For all 252 invalid class returns `kInvalidInventoryBit = 0xFF`, which obe safe inventory operations reject. For four valid classes remain index 0–3.

verify was all **65 536 combination mask × class**, including celej nadväznosti read and write. Moreover sa verify all 256 masiek during existing auxiliary function for ID cards and pentagramy.

**boundary conclusion:** is to obranná field moderného API for input mimo deklarovanej domény. Does not mean to, that original game allow warp with nesprávnym kľúčom. Všetci callers v celom original EXE nor v celom repository were not v this kroku preskúmaní. Search name functions through konektor nevydalo complete graf call; empty result sa neinterpretuje as neexistencia callerov.

Status: **CORRECTED AND REGRESNE verify V POMOCNOM API**.

## 2. projectile auxiliary functions

V `projectileHitsGuard()` and `projectileNeedsProjection()` is operand rozšírený on `int64_t` **before** subtract. Thereby sa removes signed pretečenie for entire deklarované interface with `int32_t` input.

Nezmenilo sa: štvorcová tolerancia hit ±9 on oboch osiach, requirement projekcie mimo štvorca ±20, geometria namiesto kruhovej distance, selection slotov, state values nor size records.

| Part new persistent test | Count cases v jednom run |
|---|---:|
| Štvorice coordinates from sady 21 hraničných values `int32_t` | 194 481 |
| Locally odchýlky −21 up to +21 for each coordinate 0–4095, obe osi | 352 256 |
| Dvojrozmerné relatívne field −24 up to +24 on troch posunutiach | 7 203 |
| All combinations 8 slotov v troch evidovaných state | 6 561 |
| Each byte value stavu v each slote | 2 048 |
| All byte selektory weapons | 256 |

For each coordinate štvoricu sa verifies hit and projection v oboch direction. This **is not** enumerácia all possible state celej map. Test nor this report nepripisujú original hre behavior on nekorektných 32-bit coordinate; `ObjectRuntimeRecord` v existing modeli has 16-bit world coordinates.

Original header opätovne vyvolala message UBSan on subtract prekračujúcom `int32_t`. Corrected version prešla všetkými listed case v four konfiguráciách.

Status: **CORRECTED AND REGRESNE verify V POMOCNOM API**.

## 3. Test system — pripravená registration, ohraničené performed verify

New `cmake/N3DTests.cmake` registruje existing run koreňové targets zodpovedajúce `n3d_*_test`. Main CMake zapína CTest, adds three new programy and calls registračnú function up to after deklarovaní targets. Two novšie window test declaration z current commitu remain preserved.

Each taký test dostáva zrušenie `NDEBUG`: GCC/Clang `-UNDEBUG`, MSVC branch `/UNDEBUG`. New inventory and projectile test moreover use explicit `N3D_TEST_CHECK`, which sa neodstraňujú through `NDEBUG`.

Third program `n3d_assertions_enabled_test` is zámerná check, that `assert` actually evaluate výraz. Its konečné rozhodnutie does not use `assert`, so vypnuté check oznámi as error.

For `n3d_pushable_test` sa passes explicitný `N3D_ORIGINAL_DATA_DIR`, predvolene `data/original`. This test dostáva designation `original-data`. Missing data sa this modulom **nepremieňajú on success nor automaticky nepreskakujú**. Other test use koreň project as working directory. Repeated registration nepridá duplicitné test.

### What was actually performed

Separate CMake project use three new actual test source and **ten certain registračný modul** as pripravený root patch. Nahradenie entire engine prázdnymi úspešnými test sa nepoužívalo. remain 22 targets sa v this separate project vôbec nevytváralo.

| Kompilátor | Zostavenie | Real registrované and performed | Result |
|---|---|---:|---|
| GCC | Debug + UBSan | 3 | 3 passed |
| GCC | Release + UBSan | 3 | 3 passed |
| Clang | Debug + UBSan | 3 | 3 passed |
| Clang | Release + UBSan | 3 | 3 passed |

Is **three difference test programy v four konfiguráciách**, nie o 12 different pokrytých subsystémov. Oba new functional test passed also during separate directly preklade with `-DNDEBUG`.

verify was idempotentná registration, zero registration during `BUILD_TEST=OFF` and return errors during `ctest --no-test=error`, when were not registrované none test. File `results/static_registration_inventory.json` contains list 22 existing and troch new name. This list is static evidencia, nie listing 25 execute test.

**Neoverené:** entire root CMake build, 22 original test programov, integrácia `n3d_core`, Windows/MSVC branch, actual data original. Original test executables remain v main CMake deklarované also during `BUILD_TEST=OFF`; patch nerefaktoruje their existing condition zostavovania.

Status: **REGISTRATION PRIPRAVENÁ; NEW TEST verify; COMPLETE INTEGRÁCIA OPEN**.

## 4. Negatívne check

Aby success neznamenal only neúčinný test, were v oddelených working copy performed these očakávané neúspechy:

| Check | Pozorovaný result |
|---|---|
| Original inventory header | UBSan capture invalid posun. |
| Original projectile header | UBSan capture signed pretečenie. |
| Remove new valid classes warpu | Regresný test failure on nesprávnom index. |
| Change boundary hit z `<= 9` on `< 9` | Regresný test failure. |
| Change projection OR between osami on AND | Regresný test failure. |
| Vypnutý `assert` v check programe | Program return error 1. |

Mutácie are not part of opravných patchov. Creates their only reprodukčný skript v working address.

## 5. Files and aplikovanie

- `patches/01_inventory_projectile_regressions.patch`: upravené auxiliary functions, shared check test and two persistent regresné test.
- `patches/02_ctest_registration.patch`: root CMake, registračný modul and check program for `assert`. Use after patchi 01.
- `patches/combined.patch`: oba steps v jednom patchi; **nepoužívať moreover after aplikovaní oboch čiastkových patchov**.
- `baseline/`: only four verify original files needed for this step, nie entire repository.
- `patched/`: their upravené versions and new test files; takisto nie entire repository.
- `sources_manifest.json`: Git blob SHA-1 and SHA-256 original podkladov.
- `results/`: current protokoly kompilácie, CTest, negatívnych check and verify aplikovateľnosti.

Oba patche were skontrolované through `git apply --check`, aplikované for sebou to local copies podkladov and all result change files sa byte match with test version. Základom is commit listed hore; additional change distance repository were not touto aplikáciou prepísané.

This new súhrnný patch nahrádza previous inventory/projectile patch and previous partial proposal CTest. Old separate patch common constant GUARD/Combat is not part of tohto kroku. Nekombinovať old and new opravy naslepo.

V zodpovedajúcej working copy repository:

```sh
git apply --check combined.patch
git apply combined.patch
```

On complete repository possible subsequently verify integráciu for example takto; these following commands are not tvrdením, that sa entire root build execute v this audite:

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF -DBUILD_TESTING=ON
cmake --build build --config Release
ctest --test-dir build -C Release --no-tests=error --output-on-failure
```

Offline reprodukcia exactly execute ohraničeného auditu:

```sh
python run_audit.py
```

Requires Python 3.10+, Git, CMake 3.24+ and GCC or Clang with UBSan. verify was linuxová path; during available oboch kompilátorov sa automaticky použijú oba. Files original game nor sieťový prístup are not needed.

## 6. Additional individual body

| Bod | Status after this kroku |
|---|---|
| P01 — safe inventory, including invalid class warpov | Locally corrected and test auxiliary API. |
| P02 — safe projectile subtract | Locally corrected and test auxiliary API. |
| P03/P04 — boundary hit/projekcie and sloty | Preserved, added to persistent regresie; nie new EXE objavy. |
| P08/P09 — CTest and účinnosť Release check | New registračný patch pripravený, three test performed; complete build/test suite open. |
| P05–P07 — ownership handle, sentinely, lifecycle | Requires next separate audit current code including novších WindowWrapper/WindowRegistry. Old conclusions sa automaticky neprenášajú on new implement. |
| P10 — GUARD save and meaning unknown fields | Previous round-trip sa nepreznačuje on znalosť fields; next semantic analysis remains separate role. |

## Primary podklady

Original files on pripnutom commite:

```text
https://github.com/marek177/Nitemare3d-reversed/blob/fadb68316a19d9673d759998afffdea7035cfb31/CMakeLists.txt
https://github.com/marek177/Nitemare3d-reversed/blob/fadb68316a19d9673d759998afffdea7035cfb31/src/game/InventoryRuntime.hpp
https://github.com/marek177/Nitemare3d-reversed/blob/fadb68316a19d9673d759998afffdea7035cfb31/src/game/ProjectileRuntime.hpp
https://github.com/marek177/Nitemare3d-reversed/blob/fadb68316a19d9673d759998afffdea7035cfb31/src/game/ObjectSystem.hpp
```

Mechanizmus CTest registration and behavior during zero počte test are opísané v oficiálnej dokumentácii:

```text
https://cmake.org/cmake/help/v3.24/command/add_test.html
https://cmake.org/cmake/help/v3.21/manual/ctest.1.html
```

Performed locally experimenty and exact commands: `results/verified_summary.json` and corresponding logy. Designation „corrected“ v this reporte always references on specific rekonštruovaný auxiliary code and listed range test, nie on entire original subsystém.