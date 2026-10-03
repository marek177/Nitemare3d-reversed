# NITE3W: GUARD AI and percepcia — pokračovanie 2

**Date:** 25. 9. 2026  
**Reference commit:** `9e002c10d0449885af883177d36c3037f2179e82`  
**Nadväzuje on:** use package `Nite3W_GUARD_AI_test_audit_2026-09-24.zip`.

## Result and range

This prechod prináša seven next finding o verify and modelovaní GUARD:
missing separate odbery RNG v predchádzajúcom test modeli,
depend timer from poradia odberov, exact obmedzenosť reconstruction RNG
z aktivačných timer, consequence for reprodukovateľnosť, exact modulo counts
and numeric nesúlad during pripájaní sound requirement on SND.DAT.

**Is not new analysis bytes original EXE.** Locally vstupy obsahovali
previous report and test ZIP, nie NITE3W.EXE. New read GitHubu
confirm reference commit; prehľadané connect source neposkytli missing
complete bodies 7AND44/80F8/B9B2. Webové search distribúcie neposkytlo v this
behu binary input; priame stiahnutie failure. Correct historical hash remains
`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`, but this
file tu was not open nor execute.

Kategórie evidence:

- **SOURCE-INSPECTED:** directly skontrolovaný available source text test/modelu.
- **DOCUMENT-DERIVED:** right prevzaté z listed project auditu.
- **MATHEMATICALLY-DERIVED:** consequence explicitného algoritmu; evidence is listed.
- **MODEL-TEST:** execute test provided reconstruction/modelu, nie original game.
- **OPEN-EXE:** requires missing inštrukčný or original runtime evidence.

Count new original game behov: **0**. Count new original
frame/tick trace records: **0**. CSV and JSON príklady v package are synthetic.

## F13 — previous model neoveroval random between guard

**SOURCE-INSPECTED.** V predchádzajúcom `DocumentedWakeModel::apply(...)`
was `randomValue` one skalárny argument. Vnútri loops sa for each
oprávneného guard použilo `randomValue % 8`. Counter `rngCalls` sa
increase, but nevyvolávalo next odber.

To postačovalo on test right tables oprávnenosti one guard.
**Nepostačovalo to on test sequences odberov or difference random
oneskorení during skupine.** Is not dokázanú error EXE, but o medzeru
previous testovacieho pokrytia. Old tests remain usage
v original obmedzenom range and were znovu run without úpravy.

New `WakeModel.apply` executes separate `next_u15()` for each oprávneného
guard and zaznamená slot, poradové number odberu, RNG before/after and result
timer. One odber v each oprávnenej iterate is modelová interpretation
record [WITH2]; its original call site sa this nanovo neoveril.

## F14 — activation is citlivá on order prechádzania enemies

**DOCUMENT-DERIVED + MODEL-TEST.** Model uses algoritmus opísaný v [WITH1]:

```text
state_next = (state * 214013 + 2531011) modulo 2^32
r = (state_next >> 16) & 0x7FFF
wake_delay = r % 8
```

From synthetic initial seedu 1 dostaneme first values
`41, 18467, 6334, 26500`, therefore oneskorenia `1, 3, 6, 4`.

| Order oprávnených inštancií | Timer AND | Timer B | Timer C |
|---|---:|---:|---:|
| AND, B, C | 1 | 3 | 6 |
| C, B, AND | 6 | 3 | 1 |

Table is synthetic consequence sekvenčnej spotreby, nie pozorovaný priebeh
v specific map. Exact order original GUARD loops including case
preusporiadania/remove records remains separate evidence.

implement compatibility mode nesmie považovať prechod z index
array on neusporiadaný kontajner for automaticky behaviorálne neutrálny,
if each oprávnená inštancia odoberá z one shared RNG.

## F15 — one other odber posunie results celej nasledujúcej skupiny

**MODEL-TEST.** Z same synthetic seedu 1:

| Scenario | Aktivačné timer AND, B, C |
|---|---|
| Without previous iného odberu | 1, 3, 6 |
| One provided odber before aktiváciou | 3, 6, 4 |

To is evidence citlivosti reconstruction on order spotreby, nie evidence, that
specific render/bojová function v original just vtedy odoberá random.
User original RNG can be also other subsystém; all call
sme v this prechode nezrekonštruovali.

New test distinguish zero selector, reset, repeated already označenú skupinu,
first prehľadanie without oprávnených guard and oprávnené/neoprávnené records.
V modelovanej routine first four cases nevykonajú odber. Oprávnení guard
spotrebujú after jednom; neoprávnený guard between nimi odbery neposunie.
This tvrdenie is locally for modelovanú routine, nie for entire shot/frame.

## F16 — z aktivačných timer sa cannot determine entire RNG status

**MATHEMATICALLY-DERIVED; experimentálne verify on modelových input.**

result aktivačný timer is:

```text
((state_next >> 16) & 0x7FFF) % 8
= (state_next >> 16) & 7
```

Reads therefore only bits 16 up to 18 state after update. Lower 19 bitov
update depends only from lower 19 bitov predošlého state:

```text
(state * A + C) modulo 2^19
= ((state modulo 2^19) * A + C) modulo 2^19
```

Two initial values, which sa differ o multiply `2^19`, therefore create
**same nekonečný track `rand()%8`**, pokiaľ have same count odberov.
To is not obmedzenie size test, but informačný limit daného output.

For each identify lower 19-bit seed existuje
`2^(32−19) = 8192` different 32-bit stavov with this same sledom.
Nekonečný record only these timer their nerozlíši.

### Specific synthetic protipríklad

| Initial RNG status | First `r` | Aktivačný timer `r%8` | Timer strategy 3 `r%80+8` | Random člen `r%25` |
|---|---:|---:|---:|---:|
| `0x00000001` | 41 | 1 | 49 | 16 |
| `0x00080001` | 8209 | 1 | 57 | 9 |

Oba seedy have identical track aktivačných timer, nielen first timer.
Do not have however identical results others listed transformácií. Column
`r%25` is only random člen, **nie overall damage**. Príklady nepredstavujú
spojenie aktivácie and strategy 3 to univerzálneho životného cyklu guard.

### Exhaustívna reconstruction lower 19 bitov

Add tool enumeruje all 524288 possible lower 19-bit
initial state. For synthetic track `1,3,6,4,1,4,6` are counts candidates:

```text
pred pozorovaním: 524288
po 1. hodnote:     65536
po 2. hodnote:      8191
po 3. hodnote:      1056
po 4. hodnote:       150
po 5. hodnote:        20
po 6. hodnote:         4
po 7. hodnote:         1   (dolných 19 bitov = 1)
```

Nor this jediný lower candidate neodstraňuje 8192 possible 32-bit
rozšírení. **Seven is not univerzálny count needed pozorovaní.** Is
result for this one specific track. Tool predpokladá after sebe idúce
odbery without hide medzikrokov; otherwise result cannot use on identify
original behu.

### Still exact: najvyšší bit is not visible nor v celom `rand()`

Multiply 214013 is nepárny. Two seedy different exactly o `2^31` sa after each
kroku still differ o `2^31` modulo `2^32`. Output mask bit 31, so their
entire 15-bit return values `rand()` are always same. This sa relationship
only on pozorovanie listed generátora, nie on possible other priame read
its memory state.

## F17 — match activation is not evidence match next priebehu

**MATHEMATICALLY-DERIVED + MODEL-TEST.** Z F16 follows, that themselves identical
aktivačné oneskorenia nemôžu confirm correct status RNG for movement or boj.
Z F14/F15 follows, that is not enough nor same seed without same poradia odberov.

On reprodukciu track needs to preserve status generátora also order its
spotreby, locally GUARD arrays, globally brány and status jednorazovej cache.
Modelový test ukazuje identical pokračovanie after skopírovaní entire modelového
checkpointu and difference after restore guard/cache with posunutým RNG.
**This test does not use original USER.SAV writer nor loader.**

[WITH1] umiestňuje 32-bit status Win16 1.10 on **DS offset `0x0A90..0x0A93`**
(two words `0A90/0A92`), generátor on NE `2:6EC8` and setter on `2:6EB0`.
To is podklad prevzatý z auditu, nie novo finding address. NE number segment
nor DS offset are not automaticky živý selector or address procesu.
Map addresses must zodpovedať hashu/build profilu. Original save/load
kontinuita RNG remains v [WITH1] open; z missing named array v
našom opise nevyvodzujeme, that original RNG neukladá.

## F18 — initialize 8–87 is not equal modulo nad 15-bitovým range

**MATHEMATICALLY-DERIVED + MODEL-TEST.** Listed RNG returns `0..32767`.
Predošlá skúška all uint16 input was valid skúška interface
auxiliary, nie rozdelenia original RNG.

```text
32768 = 80 × 409 + 48
```

For all possible numeric return values after jednom:

| Transformácia | Exact count input for jednu value |
|---|---:|
| Timer 8–55 z `r%80+8` | 410 |
| Timer 56–87 z `r%80+8` | 409 |
| Oneskorenia 0–7 z `r%8` | 4096 |

On minimum 8 pripadá 410 from 32768 values. To spresňuje previous
okrajový case modelu, v ktorom T=8 skips sound requirement.
**Is not odmeranú probable tichého enemy v hre.** Selected
condition odbery nemusia mať equal rozdelenie and other audio calls
remain mimo tohto auxiliary. Themselves behavior T=8 v original sa tu
nanovo neoverilo.

## F19 — numeric sound requirement sa nesmie automaticky stotožniť with index archívu

**DOCUMENT-DERIVED.** Audit [WITH3] states requirement `0x12` v events classes
`0x16`, status 9. SND inventory [WITH4] however contains:

```text
index 18: Reserved/empty, length=0, offset=0
```

`0x12` is desiatkovo 18. **Priame assign this requirement k play
vzorke SND.DAT[18] therefore does not have oporu v danom inventory.** Themselves finding
nedokazuje existenciu specific konverznej tables: can missing preklad in
call helperi, can ísť o zero effect or does not have to be exact older opis
argumentu/call-site. These possible needs to distinguish on original toku call.

Therefore needs to v registri distinguish minimálne:

```text
argument udalosti / typ zvuku
    -> triedový alebo iný výber (ak existuje)
    -> skutočný archívny index
    -> offset a dĺžka vzorky
    -> požiadavka prehrávaču / prípadné potlačenie
```

Nor named type GUARD_HUMAN_DIE v CSV sa do not have without next povýšiť on
priame EXE evidence: sprievodný audio audit [WITH5] their denotes for sekundárne
semantic assign. This prechod žiadnu unknown vzorku nepremenoval.

## Performed tests and identita

Nezmenená `Guard.hpp` has 8895 bytes and Git blob SHA-1
`0792595c4c55523d7df91ad15d7834cf729ecdc0`; local match was prepočítaná.

| Check | Range | Result |
|---|---|---|
| New Python test | 16 test method | PASS |
| 32-bit RNG vs independent 16-bit limb arithmetic | 262144 seedov: all lower words × 4 upper words | PASS; nie entire 32-bit priestor |
| Preobrazy modulo 80 and 8 | 32768 return values for each transformáciu | PASS |
| Same low19 and all high13 rozšírenia | 8192 seedov × 12 odberov during low19=1 | PASS |
| Reconstruction low19 from synthetic príkladu | All 524288 low19 candidates | One low19 candidate, 8192 full32 possible |
| Skupinová activation | 6144 cases: 256 masiek × 4 seedy × 2 poradia × 3 state cache | PASS |
| Permutácie troch oprávnených guard | 6 order | PASS |
| Old C++ audit — GCC with NDEBUG | 2134136 active check | PASS |
| Old C++ audit — Clang ASan/UBSan | 2134136 active check | PASS without sanitizer messages |

Counts sa nesčítavajú to count game scenarios. Part check sa prekrýva.
Is test modelov, arithmetic and nezmeneného auxiliary, nie celej aplikácie.
None result nepredstavuje DOS/Win16 behaviorálnu paritu.

## What sa this neuzavrelo

**original seven or eight movement krokov:** model eight znova passed,
but original requires branch `FUN_1010_7A44` during timer 1.

**Repeated hit during `0x15`:** missing complete original `FUN_1010_80F8`
including filtrov and selector `FUN_1010_B9B2`. Minulý protipríklad is still
varovanie before nedostatočnou špecifikáciou, nie confirmed error game.

**Priama percepcia:** skupinová activation and RNG analysis neuzatvárajú exact
LOS priechod, zorné array, rohy, doors nor special strategy/class branches.
Numeric zhrnutia 135 stupňov/8 buniek from older súhrnov sa tu nepoužívajú
as náhrada for complete branch and map geometriu.

**Percento poznania EXE:** this prechod nepriniesol new performed or
nanovo rozobraté original instructions. Predošlý working estimate therefore
nezvyšujeme. Prírastok is specific: rozšírené test, seven finding and exact
math limit toho, what possible confirm only timer.

## Zdroje

[WITH1] `docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md`, especially doplnok RNG:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md

[WITH2] `analysis/nite3w_guard_wake_cache_2026-09-23.md`:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_guard_wake_cache_2026-09-23.md

[WITH3] `analysis/nite3w_user_sav_story_flags_2026-09-23.md`:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_user_sav_story_flags_2026-09-23.md

[WITH4] `analysis/snd_index_audit.csv`:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/snd_index_audit.csv

[WITH5] `docs/RE_AUDIT_CHEATS_AUDIO.md`:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/docs/RE_AUDIT_CHEATS_AUDIO.md

[WITH6] Original sedemkrokový opis and reakcie:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_guard_reaction_2026-09-23.md

[WITH7] Nezmenený model Guard.hpp:
https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/game/GuardSystem.hpp

Original audit/test ZIP z konverzácie: use provided local input.
New results: `results/python_tests.txt`, `results/seed_recovery_example.json`,
`results/synthetic_examples.json`, `results/baseline_gcc/test_log.txt`,
`results/baseline_clang/test_log.txt`. Repository was not change.