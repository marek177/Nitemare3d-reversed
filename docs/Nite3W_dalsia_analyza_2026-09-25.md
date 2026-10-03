# Nite3W — pokračovanie analysis: inventory, projectiles, GUARD save and MFC model

**Date:** 25. september 2026  
**Reference repository:** `marek177/Nitemare3d-reversed`  
**Exact commit:** `45777ac20d0bf5bb57b0452d1a8281eddd87ee03`  
**Nadväzuje on:** `Nite3W_nove_finding_a_test_2026-09-24.zip`.

## Result and hranice

V this prechode were skompilované and performed reprodukčné test desiatich exactly verify source file and their depend. verify Git blob SHA-1 also SHA-256 is v `sources_manifest.json`. Nine file was novo load as entire text; Guard.hpp was prevzatý z previous package and its identita opätovne verify on current commite. next text podkladom was new MFC/memory report repository.

**Specifically results:** two type nedefinovaného behavior C++ v four auxiliary function; local correction oboch; evidence missing registration test and neúčinnosti vybraného Release test; kvantifikované own geometrie projectile; rozšírená check zachovania unknown bytes GUARD; identify medzery between MFC životným cyklom and novými modelmi systémových object.

**Is not to new priamy analysis bytes NITE3W.EXE.** V this behu was not získaná original binary nor complete ASM/Ghidra export. Pokus stiahnuť verejný Win16 shareware archív neposkytol usage bytes. Original game, Win16 environment, framebuffer and actual Windows handles sa nespúšťali. Entire port nor all 20 its original test programov were not zostavené. None file on GitHube sa nemenil.

## Označenia

- `CODE_CONFIRMED`: property specific C++/CMake source and reprodukovaného test.
- `MODEL_DERIVED`: derived consequence existing modelu, nie new meranie original.
- `REGRESSION_CONFIRMED`: rozšírené verify already zapísaných right.
- `INTEGRATION_GAP`: missing záruka or nerozlíšená semantic during budúcom prepojení.
- `OPEN_ORIGINAL`: odpoveď still requires original instructions, data or beh.

## P01 — Inventory executes posun o invalid count bitov

**Status: CODE_CONFIRMED. Corrected locally.**

`hasInventoryBit()` and `grantInventoryBit()` accept index as `uint8_t`, but execute `1u << bit` without check index. V verify environment has unsigned int 32 bitov. During index 32 UBSan zastavil obidve functions with message:

```text
runtime error: shift exponent 32 is too large for 32-bit type 'unsigned int'
```

Inventory has pritom only eight bitov. Values 8–31 v this 32-bitovom environment create after zúžení zero mask, but values 32–255 already cannot takto safely evaluate. Semantic invalid is for this inventory each index >= 8.

**Correction:** before posunom reject index >= 8; read returns false and write ponechá mask nezmenenú. Is explicitnú field moderného interface, nie o tvrdenie o historical process invalid class.

verify was all **65 536 dvojíc mask × index**, therefore 256 masiek and 256 possible bit index. On common define range 0–31 sa original and upravený code match v 8 192 dvojiciach. For valid index 0–7 is preserved behavior, including nedotknutých others bitov.

Related open question: `warpKeyBitForClass()` without valid can for class 0x18 return 255. Existuje `isWarpKeyClass()`, so is requirement on order call, nie o evidence, that existing game caller takú invalid class prepustí. V this prechode sa entire množina callerov netrasovala.

Evidence: `sources/src/game/InventoryRuntime.hpp`, `tests/ub_probe.cpp`, `results/ub_original.json`, `results/ub_patched.json`, `results/arithmetic_extended_patched.json`.

## P02 — Difference coordinates can pretiecť still before test hit

**Status: CODE_CONFIRMED for deklarované int32_t interface. Corrected locally.**

`projectileHitsGuard()` and `projectileNeedsProjection()` subtract two int32_t input v int32_t type. Reprodukčné input:

```text
projectileHitsGuard(INT32_MAX, 0, -1, 0)
projectileNeedsProjection(INT32_MIN, 0, 1, 0)
```

UBSan preukázal nedefinované signed pretečenie v oboch case. Is not vhodný spôsob modelovania zámerného 16-bitového pretečenia original — is to nedefinovaná operation v modernom C++.

**Correction:** rozšíriť first operand on int64_t BEFORE subtract. Znamienka and prahy zostali same, API nor size records sa nemenili. Maximálny difference dvoch int32_t values has absolútnu value 4 294 967 295, what int64_t safely reprezentuje.

Important boundary: coordinate v deklarovanom `ObjectRuntimeRecord` are int16_t. Difference ľubovoľných dvoch takých values is v range -65 535 up to 65 535 and original 32-bitovú auxiliary function nepretečie. Finding therefore **is not evidence pádu normal original map**. Uzatvára safe širšieho moderného API during nekontrolovaných input.

Test skontrolovali **16 777 216 dvojíc jednorozmerných coordinates 0–4095**, for each os and obidve functions. To predstavuje 67 108 864 compare with reference intervalmi. Is not to enumerácia all štvoríc X/Y player and projectile. Original also corrected code passed same check. Moreover corrected version prešla **83 521 štvoricami** from 17 hraničných values int32_t without messages UBSan.

Evidence: `sources/src/game/ProjectileRuntime.hpp`, `tests/arithmetic_regression.cpp`, `results/arithmetic_common_original.json`, `results/arithmetic_common_patched.json`, `results/arithmetic_extended_patched.json`.

## P03 — Hit GUARD is štvorcová condition, nie kruh with field 9

**Status: MODEL_DERIVED / REGRESSION_CONFIRMED. Nie new objav prahu 9.**

Z existing condition for obidve osi plynie:

```text
-9 <= dx <= 9 AND -9 <= dy <= 9
```

Is **361 celočíselných relatívnych position**. Kruh `dx² + dy² <= 81` has only **253** position. Nahradenie condition kruhovou distance by change result for **108** position.

Example: relatívna field `(9, 9)` spĺňa model hit, hoci kruh with field 9 ju neobsahuje. This is geometria auxiliary test, nie evidence, that each taký projectile v celej hre zasiahne: map collision, selection target and additional brány remain mimo this izolovanej functions.

Evidence: results `square_hit_positions=361`, `circle9_positions=253` v aritmetickom teste.

## P04 — Zóna without projekcie is also štvorcová and neukončuje let

**Status: MODEL_DERIVED / REGRESSION_CONFIRMED.**

Condition projekcie is OR between osami. During `|dx| <= 20` and at the same time `|dy| <= 20` model projekciu nepožaduje. Takých celočíselných position is **1 681**, nie 1 257 position kruhu with field 20.

For example `(20,20)` is without requirement on projekciu; `(21,0)` already projekciu requires. Is not right smrti projectile, free slotu nor o záruku konečnej visible on image.

`firstFreeProjectileSlot()` was moreover verify on all **6 561 combination eight slotov v troch evidovaných state** and on next **2 048 sondách all byte state v each position**. Free is výhradne status 0. Dopadová animation v state 2 slot still neuvoľňuje. Other nonzero values skener also považuje for obsadené; to nepotvrdzuje, that is legálne state original game.

Evidence: `tests/arithmetic_regression.cpp`, JSON arrays `legal_slot_combinations`, `slot_byte_probes`, `square_projection_skip_positions`, `circle20_positions`.

## P05 — New NativeHandleWrapper is data obal, nie complete message lifetime

**Status: CODE_CONFIRMED for copies and move; INTEGRATION_GAP during actual systémových object.**

Reprodukcia:

```cpp
NativeHandleWrapper<int> a{77, HandleOwnership::Owned};
auto b = a;
auto c = std::move(a);
```

All three objects then have handle 77 also designation Owned. Implicitný move prenesie primitívne arrays, but source nevynuluje. Further `attach(88, Owned)` jednoducho nahradí store value without return predchádzajúcej or vyvolania free functions.

Súčasný type is triviálne zničiteľný and itself none systémový object neuvoľňuje. **Test therefore nepreukázal double-free nor únik actual HWND.** Preukázal, that name Owned is v this version only designation v data and nepresadzuje výhradné ownership. Before add automatického free needs to explicitne rozhodnúť o copy, move, prevzatí and opätovnom attach.

This property is not automaticky incorrect for čisto pozorovací value model. Is not however dostatočná on tvrdenie, that životný cyklus MFC already was complete rekonštruovaný.

Evidence: `sources/src/platform/NativeHandleWrapper.hpp`, `tests/ownership_observations.cpp`, `results/ownership_observations.json`.

## P06 — Zero z-order sentinel sa nesmie zamieňať with obyčajným invalid handle

**Status: CODE_CONFIRMED / INTEGRATION_GAP.**

Existing MFC report states four z-order pseudo-values 0, 1, -1, -2. Code `NativeHandleWrapper::valid()` however for sentinel 0 returns false, because testuje only `handle != 0`. Other three returns as nonzero true.

After `clearBorrowed()` on `Sentinel{-1}` ostane combination `(0, Sentinel)`, which is on úrovni these dvoch fields same as reprezentácia Top sentinelu. Moreover `HandleRegistry::fromHandle(0, factory)` creates temporary object with zero handle; itself registry zero input neodmieta.

To is not evidence incorrect poradia okien in finálnom porte. `ZOrderTarget` enum already v repository existuje and can these operations safely oddeľovať. Conclusion is, that `valid()` mean „has nonzero handle“, nie automaticky „is valid z-order argument“. During integrácii needs to these two meaning preserve oddelene.

Evidence: `results/ownership_observations.json`; text podklad `analysis/nite3w_win16_mfc_memory_2026-09-25.md` on pripnutom commite. Original CWnd instructions sa v this prechode znovu nedekódovali.

## P07 — HandleRegistry nezabezpečuje vynulovanie handle before deštruktorom

**Status: CODE_CONFIRMED for order call; INTEGRATION_GAP for zvolený type wrappera.**

MFC report opisuje vymazanie handle v temporary obaloch before call their virtuálneho deštruktora. Moderný register so far uses `temporary_.clear()` or `temporary_.erase(handle)`. Does not have cleanup hook nor own vnorený ochranný count mechanizmus.

V diagnostic type, whose deštruktor eviduje „uzavretie“ each nonzero handle, sa during `clearTemporary()` zvýšil count record uzavretia raz. During nahradení temporary object persistent sa record uzavretia objavil already during `attachPermanent()`, hoci persistent object still uchovával same value; during subsequent zániku registra pribudol second record.

**Nešlo o call DestroyWindow nor o actual zdvojené close OS object.** Diagnostic deštruktor only ukazuje, that register itself nezaručuje behavior „clear handle, then znič wrapper“. WITH borrowed-safe deštruktorom can be súčasné usage v poriadku; with deštruktorom očakávajúcim previous disconnect nie.

Correction entire MFC lifecycle sa therefore nenavrhuje as slepé add deštruktora k NativeHandleWrapper. Najprv needs to define compatibility zmluvu register ↔ wrapper ↔ free function ↔ z-order pseudo-values. Code these dvoch modelov sa v this package nemenil.

## P08 — Dvadsať test programov is not dvadsať registrovaných CTest test

**Status: CODE_CONFIRMED. Partial local correction for two verify tests.**

Pripnutý koreňový CMakeLists define **20 targets končiacich `_test`**, but contains **0 call `add_test()` and 0 call `enable_test()`**. V this file sa nor nenačítava modul CTest. Own test programy tak are not registrované for normal spúšťanie through CTest. To does not mean, that their cannot run manually.

V izolovanom CMake experimente with dvoma exact original handle test sa after itself create and zostavení programov objavilo `0` registrovaných test and return code `ctest` was napriek tomu 0. After registration sa našli and execute 2 test.

**Range experimentu:** library n3d_core was v test project nahradená INTERFACE target with path ku header. Entire koreňový project and its other depend sa nekonfigurovali nor nezostavovali. Exact registračný block proposed v patchi sa v this izolovanom project execute.

Patch `handle_test_ctest.patch` registruje only `n3d_handle_registry_test` and `n3d_native_handle_wrapper_test`. increase **18** existing test targets this patchom registrovaných is not; netvrdí sa, that was closed entire test system.

## P09 — Release removes also test operation schovanú v assert

**Status: CODE_CONFIRMED including negatívnej check.**

Oba load handle test have after 11 check `assert`. V natívnom obale is also:

```cpp
assert(owned.detach() == 77);
```

During define NDEBUG zmizne check also themselves call detach. Preprocesorový output confirmed 1 actual výskyt calls v Debug and 0 v Release. During count were ignorované strings including diagnostic text assertu.

Aby sa preverila účinnosť test, v ODDENEJ test copy was intentionally change function valid() tak, aby always return false. This mutácia is not part of opravných patchov.

| Konfigurácia izolovaného test | Result |
|---|---|
| Nemodifikovaný code, Release, ponechané assertions | Oba test passed. |
| Intentionally incorrect valid(), Debug | Native test error capture. |
| Intentionally incorrect valid(), Release/NDEBUG | Oba test passed — error ostala nepovšimnutá. |
| Intentionally incorrect valid(), Release with -UNDEBUG | Native test error capture. |

Patch for two handle test okrem registration ruší NDEBUG on these target. Linux/GCC branch was execute. MSVC branch `/UNDEBUG` is listed for zodpovedajúcu konfiguráciu, but v this Linux behu was not zostavená. Long is vhodnejšie, aby test check were not viazané on vypínateľný assert and aby vedľajšie effects were not schované to výrazu check. New C++ sondy v this package use explicit check independent from NDEBUG.

Evidence: `tests/check_ctest_and_ndebug.py`, `results/ctest_ndebug_summary.json`, `results/mutant_*_ctest.log`, `results/native_preprocessed_*.log`.

## P10 — GUARD save preserves unknown bytes and safely reject short input

**Status: REGRESSION_CONFIRMED. New pokrytie testami, nie new meaning fields.**

For `readGuardSaveBlock()`, `writeGuardSaveBlock()` and timer helpery was verify:

| Check | Range |
|---|---:|
| value vzory nad všetkými 2 600 byte GUARD block | 256 vzorov; 665 600 byte round-trip check |
| Timer write on +06/+07 | All 65 536 values |
| Kratšie input than end GUARD block | 48 739 dĺžok for read also for write |
| Bytes mimo block and nepomenované bytes record | Preserved v test round-tripoch |

Writes reject for príliš short slot nemenili test buffer. Exactly minimálna dostatočná length was prijatá. Everything sa execute nad synthetic memory buffermi, nie nad capture USER.SAV original game.

Result increase dôveru v copy and endian write timeru, **nie poznanie semantic all 26 bytes GUARD**. Neoveruje rebasing far pointer, restore animation nor obojstrannú compatibility original versions save file.

## Opravy and reprodukcia

1. `patches/inventory_projectile_bounds.patch`: two check index inventory and rozšírené subtract v obidvoch projectile function. Prahy, game constant, record size and kľúčové classes sa nemenia.
2. `patches/handle_test_ctest.patch`: registration and zachovanie assertions only v dvoch separate verify handle test.

Oba patche passed `git apply --check` also actual aplikovaním v novom temporary local repository z verify podkladov. Arithmetic test sa then skompilovali z takto corrected stromu. Nešlo o push, commit nor pull request on GitHube.

Reprodukcia:

```sh
python run_audit.py
```

Requires Python 3.10+, Git, CMake 3.24+ and GCC/Clang with UBSan. call set `CXX`. Output contains also očakávané neúspechy: four sondy original missing UBSan and two capture zámerné mutácie. These neúspechy are evidence, that sonda error odhalila, nie neočakávaným failure celej reprodukcie. result environment is zapísané v `results/verified_test_summary.json`.

Archív neobsahuje original hru, fonty, Windows libraries nor komerčné assety. Neobsahuje run Linux test binaries and build cache; tie sa create locally during reprodukcii.

## What remains open

Primary analysis MFC vtable/message map and all actual cleanup vetiev; complete check callerov inventory and projectile; meaning projectile +0D and others unknown fields; plný AI/animation/sound graf; restore far pointer after save/load; comparison framebufferu and dynamic timing original.

These items sa v registri **neoznačujú as closed** only therefore, that above passed test vybraných modelov. Overall percento completion EXE sa this prechodom neprepočítava.

## Zdroje and verzionovanie

Each local source v `sources/` has original Git blob identify v `sources_manifest.json`. Kanonický base their URL is:

```text
https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/
```

MFC text podklad on same commite:

```text
analysis/nite3w_win16_mfc_memory_2026-09-25.md
Git blob: 8e8622f6a2d01af2998c7160993453798588dba0
```

Oficiálne technické podklady konzultované during interpretácii test:

```text
https://cmake.org/cmake/help/latest/command/enable_testing.html
https://cmake.org/cmake/help/latest/command/add_test.html
https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html
https://eel.is/c++draft/cassert.syn
```