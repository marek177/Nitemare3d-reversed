# NITE3W: GUARD AI and percepcia — subsequent audit

**Date:** 24. 9. 2026  
**Skontrolovaný commit:** `9e002c10d0449885af883177d36c3037f2179e82`  
**Range:** check existing reconstruction, rozporov v dokumentácii and odvodených hraničných cases.

## 1. Result and hranice

current C++ model state `0x13` executes eight pokusov o movement. Zahŕňa also call, v ktorom sa timer decrements z 1 on 0. Requirement on vymazanie strategy and prechod to state 2 returns up to following call. During initial timer 8 nevráti žiadnu requirement on movement sound. These own are verify run nezmeneného auxiliary z current repository [WITH1].

**Is not thereby confirmed, that original NITE3W executes eight krokov.** Older analysis opisuje seven krokov [WITH2]. Original EXE nor complete assembler functions `FUN_1010_7A44` sa v this behu nepodarilo load. Cannot rozhodnúť between dvoma tvrdeniami only according to dátumu their write. GitHub dokumentácia and C++ implement are not two independent evidence original behavior.

usage označenia:

- **MODEL-TEST:** performed test existing C++ auxiliary.
- **DOCUMENT-DERIVED:** odvodenie z exactly listed older auditu; nie new check EXE.
- **OPEN:** missing evidence on rozhodnutie o original.

Count run original EXE v this audite: **0**. Count new game runtime records: **0**. CSV v package are synthetic track modelu, nie zaznamenaná game.

## 2. Identita test code and performed test

Header `src/game/GuardSystem.hpp` has 8 895 bytes and Git blob SHA-1:

`0792595c4c55523d7df91ad15d7834cf729ecdc0`

Local copy has exactly same hash. Test function sa therefore nemenila during prepise obsahu z konektora. Identitu possible znovu skontrolovať helper `verify_source.py`.

| Skupina | Exact range | Result |
|---|---|---|
| Initialize timer | All 65 536 input type uint16 | PASS |
| One step existing auxiliary | 65 536 values timer × 2 values povolenia movement = 131 072 | PASS |
| Entire sequences existing auxiliary | 80 initial timer × 256 binary masiek povolenia eight pokusov = 20 480 | PASS |
| Comparison dvoch interpretácií nuly | 80 initial timer | Difference nastane during input with timer 1 |
| New model aktivačnej condition according to dokumentu | 256 stratégií × 256 state × 2 results compare selektora × 2 state cache = 262 144 | PASS |
| Additional scenario new modelu aktivácie | 16 including selektora 0, reset, restore modelovej cache and neskorej oprávnenosti | PASS |

V each complete behu prešlo 2 134 136 active check. Three konfigurácie: GCC; GCC with `NDEBUG`; Clang with AddressSanitizer and UndefinedBehaviorSanitizer. Without messages errors v these behoch. `results/summary.json` and records prekladačov are part of package.

**These counts are not počtom preskúmaných game scén, functions EXE nor percentom completion AI.** Test aktivácie verifies new model right opísaných v dokumente [WITH3], nie original routine `7664`. Input `targetCellAllowsMove` nenahrádza analysis kolíznej functions: is only provided logical result.

## 3. Exact priebeh stavu 0x13 v current modeli

`0x13` is 19 v desiatkovej sústave. Nezamieňať with stratégiou 3, poľom `GUARD+0x13` nor class object `0x13`.

| Timer before call | Timer after call | Output modelu |
|---:|---:|---|
| 10 and viac | T−1 | Wait without pokusu o movement and without sound requirement |
| 9 | 8 | Jedna requirement on movement sound; without pokusu o movement |
| 8 up to 1 | T−1 | Pokus o movement; commit only during povolení target |
| 0 | 0 | Requirement on vymazanie strategy and prechod to stavu 2 |

### F01 — last pokus is 1 → 0

**MODEL-TEST.** Eight pokusov corresponds to input value timer 8, 7, 6, 5, 4, 3, 2, 1. During element T v range 8–87 sa terminate requirement returns on call T+1. Helper only returns requirement; its call must execute actual write state and strategy.

### F02 — initial 8 skips sound

**MODEL-TEST.** Initialize can return 8. First call vtedy decrements timer on 7 and začne movement. Status after znížení nikdy nenadobudne 8, so sound branch sa nespustí. Initial values 9–87 return jednu sound requirement.

To does not mean, that enemy is completely tichý: test helper nepokrýva other audio calls. Netvrdíme probable 1/80, because rozdelenie and source original RNG tu were not verify.

### F03 — block nepredlžuje movement window

**MODEL-TEST.** All 256 combination povolených and block pokusov preserves eight pokusov and same number terminate calls. Block changes only `commitMovement`. During complete block is eight pokusov, nula commitov; timer sa nezastaví and helper neskúša provided náhradné steps.

This still does not close collisions original game, obchádzanie prekážok nor movement iných stratégií.

## 4. What exactly rozhodne rozpor seven verzus eight

Existing model checks nulu before znížením. As distinguish hypotézu sme zostavili alternatívu, which terminate process after znížení on nulu, before movement. Alternatíva is not vyhlásená for reconstruction original.

| Input timer = 1 | current model | Konkurenčná sedemkroková hypotéza |
|---|---|---|
| Zníženie | On 0 | On 0 |
| Pokus o movement | Yes | Nie |
| Terminate requirement | Up to additional call | V this call |

**Najmenší rozhodujúci evidence z original:** telo `FUN_1010_7A44` during input with `GUARD+0x06 = 1`, order compare with nulou, zníženia timer and calls movement branches. verify also writes `state` and `strategy` and subsequent call.

During block poslednom pokuse can mať oba modely same result coordinate. Therefore itself final position is not enough; needs to capture also pokus, timer and okamih prechodu state. `results/competing_model_divergence.csv` ukazuje difference for all 80 initialize.

## 5. Directional komponenty and arrays GUARD

Audit [WITH2] states specific 16 bytes directional tabuliek and their usage for `GUARD+0x13/+0x14`. Their interpretáciu sme skontrolovali as data z dokumentu, nie z new binary input.

| Facing | ΔX | ΔY |
|---:|---:|---:|
| 0 | 0 | −8 |
| 1 | +8 | 0 |
| 2 | +8 | 0 |
| 3 | 0 | +8 |
| 4 | 0 | +8 |
| 5 | −8 | 0 |
| 6 | −8 | 0 |
| 7 | 0 | −8 |

### F04 — eight orientation does not mean eight movement directional

**DOCUMENT-DERIVED.** V this branch is four osové vector. `F8` needs to interpretovať as −8, nie +248. During eight úspešných krokoch by sum posunu was 64 interných jednotiek; during siedmich 56. Are to výpočty for predpokladu success all krokov, nie measure game distance.

### F05 — v source named remains nesúlad

V existing header [WITH1] is `+0E` still `definitionId`, hoci [WITH3] opisuje stored last DOOR selektor. `+13` is všeobecne named `transitionParam` and `+14` is still v `unknown14_15`, hoci [WITH2] im v stratégii 3 assign X/Y komponenty.

Safe working name for +0E v opísaných branch is `lastDoorSelector`. movement komponenty have mať prístup kvalifikovaný stratégiou/state. Itself evidence jednej branches neoprávňuje tvrdiť, that bytes do not have other usage v iných class whether state. This package does not change ABI nor nepremenováva verejné členy v repository.

## 6. Percepcia: separate priamy výhľad from skupinovej aktivácie

[WITH3] opisuje separate aktivačnú branch after successful player výstrele. Is not general evidence, that všetka AI ignoruje distance or walls.

### F06 — activation is depend also from histórie

**DOCUMENT-DERIVED, test v novom modeli dokumentovaných right.** Selektor sa during prejdení ne-D cells nemaže. Player also guard si uchovávajú last zaznamenaný selektor door type. Is not to jedinečný identify door, coordinate or izby.

Two state with same visible position can reagovať different, if sa differs previous selektor or 64-byte aktivačná cache. Reconstruction only z position and orientations therefore is not postačujúca for this branch.

### F07 — first shot can spotrebovať aktiváciu naprázdno

Dokumentovaný poriadok is: skontrolovať cache → set marker → prehľadať guard. Also prehľadanie with nulou oprávnených guard therefore marker spotrebuje. Neskoršie splnenie condition neprinúti next shot same skupinu znovu prehľadať. This is logical consequence opísaného poradia, nie new pozorovanie during game.

Oprávnenosť v this branch is: strategy 0, status 7 or 8 and match guard selektora with player. Result is status 1 and timer 0–7. Selektor 0 nevykoná aktiváciu; argument −1 clear cache. Zachovanie/restore cache during save/load is supported v [WITH3], no test package nevyvoláva original save loader.

### F08 — argument cache and player selektor sa do not have potichu zlúčiť

According to [WITH3] argument určuje index cache, until compare guard uses global player selektor. Normálna strelecká path their provided identical. Model intentionally preserves two values and test also their different. Takýto synthetic input is not evidence, that different values nastávajú v normálnej hre.

Model adds check range 0–63 on ochranu test procesu. Takáto ochrana **is not tvrdená as property original**.

## 7. State track cannot zovšeobecniť on each enemy

### F09 — aktivačná branch and strategy 3 are not one univerzálny string

Skupinová activation [WITH3] changes guard with stratégiou 0. Movement to `0x13` z [WITH2] is viazaný on strategy 3 after success percepčnej condition v state 7. Cannot without evidence connect these two branches for seba and mark result for priebeh each enemy.

### F10 — repeated hit odhaľuje neúplnú špecifikáciu návratu

[WITH2] opisuje save original state to `nextstate` during normal nesmrteľnom hit, with výnimkami. Doslovná príliš všeobecná implement by during next hit during state `0x15` mohla prepísať return value on `0x15` and then sa return sama to seba.

Test contains minimálny protipríklad k tomuto zovšeobecneniu. **Is not dokázanú error original game nor o dokázanú error current execute engine.** V test header complete zásahový handler is not implement. On uzavretie needs to preveriť input filtre and exact branches `FUN_1010_80F8`, behavior during original state `0x15`, výnimku state 0 and class selection sequences `FUN_1010_B9B2`.

### F11 — Cannon and boss require global status sveta

[WITH4] viaže Cannon, class `0x19`, state `0x0E–0x10` also on global bránu `0x51A5`, ovládanú panel command `0x20/0x21`. Local record GUARD therefore is not complete input rozhodnutia o útoku.

Same dokument viaže flag `0x51AA` on event classes `0x16` v state 9 and sound requirement `0x12`. Z tohto itself is not dovolené urobiť general name type „boss zomrel“. These links were prevzaté from older auditu and v this kroku sa nanovo nerozoberali v EXE.

## 8. What remains open

| Question | Exact missing evidence |
|---|---|
| Seven or eight krokov v original | Original inštrukčná branch during timer 1; order dekrementu and test nuly |
| Vynechanie sound during T=8 v original | Initialize + všetci sound call okolo input to 0x13 |
| Priama percepcia, rohy, zorné array | Complete condition percepčnej routines, kolízny/visible priechod and input global |
| Completion movement | actual test target cells, obsadenie, writes coordinates and map; nie only bool input modelu |
| Repeated hit during 0x15 | Complete original damage receiver including filtrov and return state |
| Animation and SND.DAT | Živé or completely derived sekvenčné tables, index and všetci call sound |
| Entire životný cyklus enemy | Track jednej identify inštancie with local poľami, global flag and RNG |
| DOS match | Separate evidence z DOS; Win16 dokumentácia nor C++ test ju nepotvrdzujú |

Record for verify by small preserve number inštancie, class, status, strategy, nextstate, timer, coordinate before/pokus/after, result movement, zvolenú animation, sound requirement, player/guard selektor, cache and relevantné globally brány. Is not enough video without these values on jednoznačné uzavretie each internal prechodu.

### F12 — pokrytie switch is not pochopenie AI

V header is 22 numeric items and 20 different target adries. Dvojice `0x0A/0x0B` and `0x0C/0x0D` shared addresses. Is inventory, nie 22 uzavretých semantic nor complete graf stratégií.

**Predošlý working estimate 75–85 % this auditom nezvyšujeme.** Pribudli performed test modelu, exact diskriminátor rozporu and specifically implement riziká. Nepribudol new priamy evidence o original EXE nor runtime parite. Súčasné podklady neobsahujú complete menovateľ all AI required, z whose by sa dalo poctivo compute new overall percento.

## 9. Source and reprodukovateľnosť

WITH1 — exact test header:  
`https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/game/GuardSystem.hpp`

WITH2 — original sedemkrokový opis and reakcia after hit:  
`https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_guard_reaction_2026-09-23.md`

WITH3 — selektory and jednorazová aktivačná cache:  
`https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_guard_wake_cache_2026-09-23.md`

WITH4 — globally flags ovplyvňujúce AI:  
`https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_user_sav_story_flags_2026-09-23.md`

WITH5 — existing test v repository, skontrolovaný as kontext, nie running this package:  
`https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/tests/guard_facts_test.cpp`

New performed test: `test/guard_model_audit.cpp`. Measure results: `results/summary.json`, `results/test_output_*.txt`. Entire aplikácia sa nekompilovala nor nespúšťala. Repository on GitHube was not upravený.