# Nite3W: new static and modelový analytický prechod

**Date:** 24. september 2026  
**Range:** available reconstruction Win16 Nite3W, render, timing, GUARD, damage, IMG and integrácia headers.  
**Podklady:** 10 file load through connect GitHub. Each local copy has identical Git blob SHA-1 with result load. Complete evidencia is v `sources_manifest.json`.

## Result

Reprodukcia preukázala konflikt dvoch headers, medzeru in valid IMG odkazov and several important arithmetic boundaries rekonštruovaných algoritmov. Pripravená and locally verify is correction konfliktu headers. Rozšírené test pokrývajú selected auxiliary functions, nie celú hru.

**Original EXE nor complete ASM/Ghidra export were not v this behu k dispozícii.** Pokus získať verejný shareware archív neposkytol stiahnuteľné bytes. Was not run original game, Win16 emulácia, measure original memory, capture original framebufferu nor posluch original sound. Older text „files are v library“ is not evidence, that their this specific beh tool actually získal.

Results therefore are not novým priamym byte auditom all functions EXE. Are not nor novým percentom complete Nite3W. Findings o arithmetic are confirmed for preverené modely; their prenos on original depends from correct existing reverzného prepisu.

## Druhy evidence

| Designation | Meaning |
|---|---|
| `CODE_CONFIRMED` | Property current source file, reprodukovaná kompiláciou or its execute. |
| `MODEL_DERIVED` | Math consequence exact prevereného modelu, nie new measure original. |
| `REGRESSION_CONFIRMED` | Rozšírené verify already opísaného behavior vybranej functions. |
| `DOC_CONFLICT` | Rozpor between existing podkladmi; without primary výpisu cannot automaticky povýšiť jednu version. |
| `OPEN_ORIGINAL` | Question remains open for specific original build or its beh. |

---

## N01 — GUARD and Combat sa nedajú zahrnúť to jednej prekladovej units

**Status: `CODE_CONFIRMED`. New reprodukovaný integračný problem.**

`src/game/Guard.hpp:13` and `src/game/CombatSystem.hpp:75` define v same namespace `nitemare3d::game` same constant:

```cpp
inline constexpr std::uint8_t kFreshGuardStrength = 0xFF;
```

separate sa obe headers skompilovali. After their vložení to one `.cpp` vznikla error redefinície v oboch poradiach. `#pragma once` chráni repeated vloženie jednej headers, nie two independent define v dvoch different header.

| Kompilačná sonda | Before opravou | After local oprave |
|---|---:|---:|
| Only CombatSystem | Success | Success |
| Only GuardSystem | Success | Success |
| CombatSystem then Guard | Redefinícia | Success |
| Guard then CombatSystem | Redefinícia | Success |

Correction v `guard_shared_constant.patch` presúva constant to common `src/game/Guard.hpp`. Value 255, name, type and namespace remain same. Obe original headers load common define. Patch passed also `git apply --check`, actual aplikovaním v temporary local repository and subsequent kompiláciou. GUARD and HP test before opravou and after nej return same results.

**boundary conclusion:** nebolo performed zostavenie entire project. Preukázaný is specific konflikt during common zahrnutí these headers; netvrdíme, that each existing separate target CMake already teraz failure. GitHub was not change.

Evidence: [WITH1], [WITH2], `results/original_combat_guard.log`, `results/original_guard_combat.log`, `results/patch_apply_verification.json`.

## N02 — IMG loader prijme reference, which sa cannot assign k frame

**Status: `CODE_CONFIRMED`. New reprodukovaný valid nedostatok reconstruction.**

`ImgArchive::load()` checks, whether nonzero reference z address lies between element image dátami and koncom file. After rozdelení file on frames however nekontroluje, whether each taký reference belongs between actual začiatky frames evidované v `exactOffsetToFrame_`.

Synthetic check file has jednu frame 1 × 1. Header frames starts on `0x800`, jediný pixel is on `0x80A`, end file is `0x80B`. Nonzero item address set on `0x80A` prejde range check. Subsequent `frameAtExactOffset(0x80A)` returns empty result.

| Check | Result |
|---|---|
| Reference on start frames `0x800` | load and recognize. |
| Reference on pixel `0x80A` | load, but nerozpoznaný as start frames. |
| Reference on EOF `0x80B` | Rejected. |

Odporúčaná diagnostic after parsovaní is process obidva address and vypísať nonzero references without exact target, including banky, index and offset. Taká diagnostic sa v test actually executes and odhalí exactly one incorrect reference. Plošné change loadera on tvrdé reject by small predchádzať verify all original IMG variant; v this prechode sa taká change nerobila.

**boundary conclusion:** is not preukázaný pád original game nor evidence, that provided original data taký reference contain. Is to konzistenčná medzera between range valid and subsequent exact search v reconstruction.

Evidence: [WITH4]–[WITH8], `tests/img_directory_probe.cpp`, `results/img_directory_probe.json`, three files `results/fixtures/synthetic_*.img`.

## N03 — exact math prepočet nedáva same vzorkovanie walls

**Status: `MODEL_DERIVED`, execute modelu confirmed. New kvantifikovaný regresný example.**

Preverené jadro selects text coordinate prírastkom 16.16:

```text
step = floor((64 × 65536) / n)
texel(y) = floor((y × step) / 65536)
```

To všeobecne is not to isté as priamy racionálny prepočet:

```text
texel_ideal(y) = floor((64 × y) / n)
```

During height column **n = 6**, initial coordinate nula and without clip vznikne:

| Line y | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---:|---:|---:|---:|---:|---:|
| Preverený fixed step 16.16 | 0 | 10 | 21 | **31** | 42 | 53 |
| Priamy racionálny prepočet | 0 | 10 | 21 | **32** | 42 | 53 |

Reason: `step = 699050`. After troch krokoch is value `2097150`, tesne pod `32 × 65536 = 2097152`. Strata zlomku during create kroku is therefore pozorovateľná during subsequent selection texelu.

Test passed all **511 výšok 1–511** and all their lines, total **130 816 selection**. Two methods sa differ v **1 264 selection**, layout between **274 výšok**. Difference is v this test range always one texel direction nadol. Entire list different selection is v `results/sampler_counterexamples.json`.

original function `drawWinGIndexedColumn()` test compare also with independent zapísaným algoritmom celočíselnej parts, zlomku and prenosu. usage test text has different value each texelu, so difference coordinate nezanikne match farbou.

**Consequence for reconstruction:** original kvantovanie neslobodno nahradiť „exact“ výpočtom without označenia change behavior. Count 1 264 nevyjadruje count different pixel v capture image game. Original framebuffer sa tu neporovnával and v actual text can mať adjacent texely same farbu.

Evidence: [WITH3], [R1], `tests/renderer_edges.cpp`, `results/renderer_edges.json`.

## N04 — Celočíselný final bod and akumulátor úseku can nesúhlasiť o jednotku Q4

**Status: `MODEL_DERIVED`. New hraničný example.**

For `initializeSpanInterpolation()` was usage input:

```text
x1 = 0, x2 = 3
Y1_Q4 = 1600, Y2_Q4 = 1601
centerY_Q4 = 1600
span.xStart = 0, span.xEnd = 3
```

Model stores final `yAtEnd = 1601`, but step 16.16 is only `21845`. After troch prírastkoch has akumulátor value `65535`, nie `65536`. Its celočíselná part posunu is still nula, hoci separate compute final posun is jedna jednotka Q4.

Is consequence dvoch separate zaokrúhlení, nie automaticky o error jadra. During prepájaní render sa nesmie predpokladať, that stored final bod and repeated akumulácia are always zameniteľné. Test nevyhodnocuje, whether complete vykresľovacia loop daného build final column zahŕňa; compares exactly listed values modelu.

Add were also check reject nereprezentovateľného result `(-32768 × 65536) / -1` and prijatia reprezentovateľnej values `(-32768 × 65536) / 1`.

Evidence: [WITH3], `results/renderer_edges.json`.

## N05 — Rozhodovanie o own column is not univerzálny class komparátor

**Status: `MODEL_DERIVED`. New protipríklad for neobmedzené input.**

For two synthetic osovo orientované úsečky:

```text
A: orientation = 0; (0,10) → (10,10)
B: orientation = 2; (5,0) → (5,20)
```

applies naraz:

```text
ownerConflictReplaces(A, B) == true
ownerConflictReplaces(B, A) == true
```

Therefore function cannot use as všeobecné comparison for `std::sort` nad ľubovoľnými VEC record. Požadované usporiadanie class algoritmu takú obojstrannosť nepripúšťa. Existing code however nor netvrdí, that is general komparátor: modeluje rozhodovanie o already obsadenom column v specific order process.

**boundary conclusion:** synthetic úsečky sa pretínajú. This test nedokazuje, that taká dvojica vznikne z original map and their extrakcie boundaries. Is to reason preserve predpoklady and order original algoritmu, nie evidence errors its normal game output.

Evidence: [WITH3], [R1], `results/render_edges.json`. Jazykový podklad: [L1].

## N06 — Multiply time input preteká skôr than itself 32-bit time

**Status: `MODEL_DERIVED`, verify on rekonštruovaných function.**

Model najprv ponechá spodných 32 bitov multiply and up to then divide 1000. Order operations is important.

| Calculation | Input time_ms | result bucket |
|---|---:|---:|
| `low32(time_ms × 8) / 1000` | 536 870 911 | 4 294 967 |
| Ten certain | **536 870 912** | **0** |
| `low32(time_ms × 25) / 1000` | 171 798 691 | 4 294 967 |
| Ten certain | **171 798 692** | **0** |

First boundary corresponds to numeric value 6 dní, 5 hodín, 7 minút and 50,912 sekundy; second 1 dňu, 23 hodinám, 43 minútam and 18,692 sekundy. **Are to values input time, nie automaticky length from run game.** During multiply 25 is first pretečenie súčinu, nie tvrdenie o exact periódickosti každých toľko milisekúnd.

Pokles bucketu does not mean v preverenom auxiliary reset logical count: compares sa nerovnosť, so counter sa increments raz. Modelový test verify also this case. Cannot z neho vyvodiť pád game, reset celej simulácie nor problem all callerov.

Test was entire range **65 536 bit reprezentácií sadzby** proti 15 hraničným time value: **983 040 cases**. Referencia uses independent signed 64-bit súčin and normalizovaný increase modulo 2^32; does not change sa pritom define 16-bit extension znamienka.

Evidence: [WITH9], [WITH10], [R2], `results/timing_edges.json`.

## N07 — Check kalibračného range nezaručuje positive frame tempo

**Status: `CODE_CONFIRMED` for model; `OPEN_ORIGINAL` for reach v original hre.**

Kalibračná function reject priemer nad 65 535 ms, but accepts also priemery, during ktorých vzorec already returns nulu:

```text
frame_rate = floor((1000 + floor(D/2)) / D)
```

| Priemerné D | Result |
|---:|---:|
| 1 999 ms | 1 |
| 2 000 ms | 1 |
| **2 001 ms** | **0** |

First taký input measure piatich render/present call is **10 005 ms**. Preverený model this input prijme. If sa zero sadzba vloží to separate frame helpera and its predošlý bucket is also nula, logical counter already change input time neposúvajú.

Enumerované were all celočíselné input `elapsed_ms = 0..327679`, total **327 680** values. Z nich **317 675** vedie k prijatej zero sadzbe. To is count umelých input functions, nie probable events v hre. Preverené was also first reject during `elapsed_ms = 327680`.

**Consequence:** reconstruction potrebuje this status at least diagnostic distinguish. Without primary rozboru all kalibračných vetiev cannot tvrdiť, that original v takej situácii zamrzne. same cannot potichu zaviesť clamp on 1 and mark ho for verné original behavior. This prechod nemenil time model.

Evidence: [WITH9], [WITH10], `results/timing_edges.json`.

## N08 — GUARD 0x13: rozšírené verify all modelových prekážkových priebehov

**Status: `REGRESSION_CONFIRMED`. Is not new objav already zdokumentovaného skip sound during timeri 8.**

Preverená is function `stepGuardState13()`, nie entire state machine enemy. Test contain:

- **131 072 jednorazových prechodov:** all 65 536 values 16-bitového timer × priechodnosť yes/nie.
- **20 480 complete priebehov:** 80 initial timerov 8–87 × all 256 combination priechodnosti eight movement pokusov.
- Complete priebehy total vykonali **993 280 call** pomocnej functions.

In all these modelových priebehoch nastane eight movement pokusov. Zablokovaný pokus sa nedobieha moreover. Count commitov sa equal count povolených pokusov. Initial timer 8 nevygeneruje requirement on movement sound; higher timer ju vygeneruje raz. Output from state nastane v separate nasledujúcom call with zero timerom, therefore after `initialTimer + 1` call this functions.

**boundary conclusion:** array `playMovementSound` is requirement modelu, nie odmeraný počuteľný sound. Test neoveruje actual writes map, selection direction, distance movement, animation, original count milisekúnd nor other state GUARD.

Evidence: [WITH1], `tests/guard_edges.cpp`, `results/guard_edges.json`.

## N09 — Rozpor v evidencii kolízneho boxu

**Status: `DOC_CONFLICT`. Is not new prečítanie EXE.**

`docs/PLAYER_COLLISION_RE.md` denotes value 27 world units v movement routine for directly finding and vysvetľuje ju as field rozmer osovo orientovaného boxu, nie kruhový field. Novší prehľad open areas still states field/rohy/sliding as unclosed without jasného distinguish základného tvaru and complete all interakcií.

Correct evidencia has oddeľovať:

1. older specifically message o boxe with field rozmerom 27;
2. verify instructions and all vetiev on current zvolenom hashi EXE;
3. behavior during rohoch, dynamic door and obsadených cell.

Condition geometrický model poskytuje jednoduchý check example: v ideálnej chodbe wide 64 jednotiek, with fixed hranami and without next prekážok, condition `x-27 >= 0` and `x+27 < 64` allow celočíselné field stredu 27–36, therefore ten field. Is not to new nameraná kolízna trajektória original nor evidence poradia test its helperov.

Evidence: [R2], [R3], `results/collision_box_conditional_model.json`.

## N10 — Clip tables: independent check poradia celočíselných operations

**Status: `MODEL_DERIVED` and `REGRESSION_CONFIRMED`.**

For nezáporné AND and positive n applies:

```text
floor(floor(A/n)/2) = floor(A/(2n))
```

table model was compare with druhým, 64-bitovým write. Preverených is **262 143 dvojíc h,n**: h = 0–511 and moreover h = 65535, always n = 1–511. V rámci unsigned 16-bitového interface have all h ≥ 511 same zero branch `divide`, so large h are moreover pokryté jednoduchým rozborom condition.

V this modeli is najväčší čitateľ `511 × 64 × 65536 = 2143289344`, therefore pod boundary 2^31. Is not tu needed predpokladať negative value before divide and right posunom. Is to evidence arithmetic konzistencie prevereného C++ modelu; original znamienkovosť input and všetci calleri sa this novým behom nedekódovali.

Evidence: [WITH3], [R1], `results/renderer_edges.json`.

## N11 — Mask text predpokladá vhodnú width

**Status: `MODEL_DERIVED`.**

Input `width` v `selectTextureU()` sa uses as mask `width-1`, nie as univerzálne modulo. For width 64 was preverených all **65 536 reprezentácií input alongWall** v priamej mask branch; result súhlasí with bitovým obalom to 0–63.

During width 3 however for example input 1 can `1 & 2 = 0`, nie `1 % 3 = 1`. Is preukázanú property interface, nie finding nesprávnej original text. V preverenom wall jadre is normálna width 64. During next integrácii needs to preserve this predpoklad or explicitne odlíšiť rozšírený mode iných text.

Evidence: [WITH3], `results/renderer_edges.json`.

## N12 — Subtract HP: rozšírené boundary test

**Status: `REGRESSION_CONFIRMED`.**

`subtractGuardStrength()` was preverené for all HP 0–255 and damage -1–256: **66 048 combination**, plus `INT_MIN` and `INT_MAX`. Results correspond reject nekladného damage and saturácii HP on nulu during smrteľnom damage. V test case UBSan neohlásil nedefinované behavior.

**boundary conclusion:** this function nevypočítava original damage z projection cache, classes, weapons or RNG. Therefore sa this test does not close bojový system nor matica imunitných and bossovských výnimiek.

Evidence: [WITH2], `results/combat_edges.json`.

---

## What sa this prechodom neuzavrelo

| Area | actual status after this prechode |
|---|---|
| MFC RuntimeClass deskriptory, vtable, message map | Without new surových bytes and relocation. boundary, layout and targets are not nanovo confirmed. |
| Ownership and free memory v original | Complete allocate-own graf sa nevytvoril. |
| GUARD as celok | Test is helper 0x13 and define; ostatný graf remains open. |
| Collisions, doors, teleporty, USE | recognize dokumentačný rozpor; new priame comparison original helperov nevykonané. |
| IMG/SEQDEF spodná banka | Preserved known prekrývanie 23 selektorov; reach and correctly matching with assetmi nevyriešené. |
| Complete render | New reference príklady arithmetic, but without portovania and compare celej scény. |
| USER.SAV, hidden eventy, bossovia, audio links | Without new uzavretia semantic; cannot im z tohto prechodu pripočítať percentá. |
| Vernosť Windows/DOS versions | Modely nepredstavujú evidence parity between build. |

## Reprodukcia

V koreňovom priečinku package:

```sh
python run_audit.py
```

Needed is Python 3.10+ and available C++20 kompilátor `g++`. verify zostava v this prechode: **GCC 14.2.0, C++20**, with `-Wall -Wextra -Wpedantic` and `-fsanitize=undefined -fno-sanitize-recover=all`. Skript supports switch `--no-sanitize` for environment without tohto sanitizéra; provided results however vznikli with zapnutým UBSan.

Skript checks hash all 10 file, runs negatívne also pozitívne kompilačné sondy, zostaví and executes five test programov and verify local candidate opravu. Original snapshoty does not change. Nepripája sa ku GitHubu and nespúšťa original hru. Results stores to `results/summary.json` and separate protokolov.

V `results/summary.json` is `unexpected_failures: 0`. To does not mean, that were not find problem: obe očakávané redefinície and prijatie nekonzistentného IMG odkazu are explicit reproduced finding, on which are sondy zostavené.

Local patch possible before usage v inom checkout-e skontrolovať helper `git apply --check`. Is určený on three named files reconstruction, nie on úpravu original EXE.

## Source references

Git blob SHA and SHA-256 each local copies are v `sources_manifest.json`; these hashe určujú exact content also v case budúcej change branches main.

- [WITH1] `marek177/Nitemare3d-reversed`, `src/game/GuardSystem.hpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/game/GuardSystem.hpp
- [WITH2] Same repository, `src/game/CombatSystem.hpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/game/CombatSystem.hpp
- [WITH3] Same repository, `src/renderer/Win16WallRasterCore.hpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/renderer/Win16WallRasterCore.hpp
- [WITH4] Same repository, `src/formats/ImgArchive.cpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/formats/ImgArchive.cpp
- [WITH5] Same repository, `src/formats/ImgArchive.hpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/formats/ImgArchive.hpp
- [WITH6] Same repository, `src/formats/ImgSequenceLayout.hpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/formats/ImgSequenceLayout.hpp
- [WITH7] Same repository, `src/formats/BinaryIO.cpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/formats/BinaryIO.cpp
- [WITH8] Same repository, `src/formats/BinaryIO.hpp`: https://github.com/marek177/Nitemare3d-reversed/blob/main/src/formats/BinaryIO.hpp
- [WITH9] `marek177/Nite3d-win3.11`, `src/win16_timing_model.cpp`: https://github.com/marek177/Nite3d-win3.11/blob/main/src/win16_timing_model.cpp
- [WITH10] Same repository, `include/nitemare3d/win16_timing_model.hpp`: https://github.com/marek177/Nite3d-win3.11/blob/main/include/nitemare3d/win16_timing_model.hpp
- [R1] Existing renderer audit: https://github.com/marek177/Nitemare3d-reversed/blob/main/analysis/nite3w_renderer_2026-09-23.md
- [R2] Existing audit Win16 versions: https://github.com/marek177/Nite3d-win3.11/blob/main/docs/win16/audit-2026-09-24.md
- [R3] Existing analysis player collision: https://github.com/marek177/Nitemare3d-reversed/blob/main/docs/PLAYER_COLLISION_RE.md
- [L1] Working proposal C++, requirement on triediace comparison: https://eel.is/c++draft/alg.sorting.general

**Konečný range result:** new specific integračná correction, reprodukovateľná IMG diagnostic, arithmetic protipríklady and rozšírené regresné test. Nie complete analysis všetkého unknown v original Nite3W.