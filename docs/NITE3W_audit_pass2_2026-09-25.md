# NITE3W — second pass slabšie pokrytých areas

**Date:** 25. 9. 2026. **Target evidencie:** NITE3W Win16 1.10.
**Prečítaný status rekonštrukčného repository:** `9d485e82a84ef1241eff7165c390c82eaff47970`.

## 1. Range and boundary evidence

This prechod execute new audit specific C++ code, reprodukčné test loadera,
comparison dvoch damage tabuliek and test hraničného behavior existing modelu
GUARD. Is not to new disassembláž original NITE3W. Locally were available three
output previous prechodu, nie EXE, SND.DAT nor Ghidra C/ASM export.

Verejný shareware `nite3w18.zip` was search v katalógu RGB Classic Games,
but its stiahnutie failure. Version 1.8 was not v this prechode rozbalená,
hashovaná nor analyzovaná. Historical zmienky o Library exportoch were separate
from actually available input. Reference hash 1.10 remains only target for budúce
spárovanie: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

Four complete files z repository are v `reference/src/formats/`. Each exact copy
was verify Git blob SHA-1 and SHA-256; values and commit are v
`evidence/reference_sources.json`. `reference/excerpts/guard_state13.hpp` is
explicitly only výrez structures and helpera z Guard.hpp, nie entire original file.

## 2. New finding SND-01: end vzorky is not end address

Source `src/formats/DatArchive.cpp`, blob
`394d7dbefee01c705620e86f3ca21ce38bab86e4`, uses in všeobecnom `load()` condition:

```cpp
if (static_cast<std::size_t>(offset) + length == bytes.size()) {
    foundTerminalEntry = true;
    break;
}
```

At the same time project audit SND opisuje fixed directory 160 × 6 = 960 bytes,
poslednú logical SFX item 110, zero EOF record 111 and rezervované items
112..159. CSV for item 110 states `offset=838206`, `length=5712`; sum is
843918. This is citovaná evidencia z CSV, nie new load original SND.

Reprodukčný file has same index usporiadanie, but only umelé štvorbajtové
payloady. Neobsahuje original music nor sounds. Nezmenená implement load()
sa on ňom zastaví after item 110:

| Pointer | Original loader on synthetic input | New explicitná SND path |
|---|---:|---:|
| Preserved physical sloty | 111 | 160 |
| `headerBytesUsed()` | 666 | 960 |
| Record 111 load | nie | yes |
| Rezervované sloty 112..159 valid | nie | yes |

Is not evidence, that normal sounds 34..110 always missing or znejú zle. Is
predčasné termination inventory and valid. If skorší index references on last
payload, same condition terminate scan still skôr. Test with aliasom v slote 34
reprodukuje only 35 zachovaných items.

## 3. New finding SND-02: scan vie process to data

`firstPayload` sa count, but does not determine upper boundary loops. That is obmedzená
only size entire file. Synthetic example without EOF sentinel v first
160 record vloží podobu sentinel to data on offset 960. Original loader ju
považuje for next descriptor:

```text
entries = 161
headerBytesUsed = 966
firstPayloadOffset = 960
```

Therefore load „index“ bytes presahujú start data. This is reprodukovaný
problem parsera during umelom input, nie message memory exploitácie original game.
New path reads exactly 160 records and takýto file reject for missing zero
EOF descriptor v address.

Test further reprodukujú, that original path nevšimne damage descriptor 159,
when sa zastavila during 110, and prijme nonzero payload direction dovnútra address.

## 4. Pripravená local correction

`snd_win16_fixed_directory.patch` adds:

```cpp
auto snd = n3d::DatArchive::loadSndWin16(path);
```

New verejný input loads and skontroluje all 160 descriptorov, preserves
empty also aliasované index, checks boundary without pretečenia subtract and
reject nonzero payload in vnútri 960-byte address. Requires at least one
zero descriptor odkazujúci exactly on EOF. Neodvodzuje PCM parametre nor
nevyhlasuje each file with takýmto layoutom for original game asset.

**General `load()` was intentionally ponechaný without change.** UIF and other DAT kontajnery
sa must not without evidence previesť on fixed SND layout. Patch so far neprepája all
callerov project on novú method; spotrebiteľ, which loads SND, must explicitne
use `loadSndWin16()`. This is not change zapísaná to GitHub nor hotová correction
all UI/editorových ciest.

Items 1..15 sa v test verify helper umelého tagu `MThd`; are not to plné
MIDI skladby. Test therefore verifies zachovanie indexov and podpisu, nie MIDI decoder
nor assign skladieb k levelom. Posun event → physical SND slot `+32` remains
neoverenou historical hypotézou and patch ho does not use.

## 5. New finding OBJ-01: two damage tables sa rozchádzajú

compare podklady:

- AND: `docs/COMBAT_DAMAGE_RE.md`, blob `f35f2b91885e6a5bccb00ca1327871884ea4cacc`.
- B: `analysis/nite3w_projectile_pool_2026-09-23.md`, blob
  `1a1329ea6b6ce4325181c51c0f3a593b419e0dc5`.

During 19 class with štyrmi numerickými weapon branch sa compare 76 buniek.
**17 buniek nesúhlasí; is 7 class:** `0E, 0F, 10, 11, 14, 1B, 1C`.

| Classes | Nesúlad |
|---|---|
| 0E / 11 / 14 | Weapon 1: AND states /2, B /8. |
| 0F / 10 | AND gives zbrani 1 /2 and ostatným /256; B zbrani 1 /256 and ostatným /2. |
| 1B / 1C | AND gives všetkým /2; B allow /2 only zbrani 1 and otherwise nulu. |

For positive modelový raw damage 120 returns difference interpretation classes 0F,
weapons 1 values 60 or 0 before difficulty. This example nerozhoduje, what robí
original; ukazuje, that nejde only o rozdielne names tej istej operations.

Osobitne is sporná class16 condition: AND states gate `DS:7E52 == 3`, B
`episode == 3 || DS:51A6 != 0`. This condition is not zahrnutá to count 17
numerických buniek. Complete differences are v `evidence/damage_report_conflicts.json`.

**None damage matica was not zvolená for right and combat code was not prepísaný.**
Needs to original branch 9FA2 with podmienkami before jump table and exact mapovanie
read global. Kľúčové is also nezameniť 9FA2 (damage relative to GUARD) with AND1EA
(kontaktové damage relative to player).

## 6. New finding AUD-01: hraničný timer changes movement also sound modelu

current `GuardSystem.hpp`, blob `0792595c4c55523d7df91ad15d7834cf729ecdc0`,
contains `stepGuardState13`. V its exact izolovanom výreze sa test
80 initial timerov 8..87, each with free also block target: 160 behov.

Source model:

- sound požaduje, when **new** timer is 8;
- movement allow during novom timere 7..0, therefore eight pokusov;
- prechod to state 2 returns up to during next call with input timerom 0;
- z initial values 8 sa sound branch vôbec nevykoná;
- block target nezastavuje countdown.

Older `analysis/nite3w_guard_reaction_2026-09-23.md`, blob
`b47ae77d54724f34a09b88c69060026c389b1a05`, opisuje seven movement updateov.
During uvádzanom kroku 8 by to was 56 jednotiek, until model umožní 64. Exact
order test nuly v original `FUN_1010_7A44` is therefore distinguish bodom.

**Model has preukázateľne eight pokusov; tvrdenie o original hre sa thereby
nerozhodlo.** Nesmie sa svojvoľne opraviť on seven only according to older text.
None taká change sa v this package nevykonala.

## 7. Eight added meaning aliasov

This are new items registra, nie eight new binary objavov. All have
`repo_report_supported`; nor jedna does not have `new_binary_verification=true`.

| Symbol Win16 1.10 | Analytický alias | Note |
|---|---|---|
| FUN_1010_7AND06 | BeginStrategy3TimedCardinalMove | set timeru and kroku strategy 3. |
| FUN_1010_7AND44 | AdvanceStrategy3TimedCardinalMove | Movement/sound/timer; nula is open. |
| FUN_1010_188AND | UpdateDoorStateWithScriptGate | Gate 51AB; nie univerzálne zmrazenie sveta. |
| FUN_1010_1E00 | StepDoorMovement | Separate scheduler branch movement door. |
| FUN_1010_9B64 | Test | Cell collisions, guard/wall/script. |
| FUN_1010_9D30 | AdvanceProjectileSubsteps | Podkroky with kolíznymi test. |
| FUN_1010_9FA2 | ComputeGuardDamageFromProjection | Purpose is opísaný; damage matica is sporná. |
| FUN_1010_AND1EA | ComputeObjectContactDamage | Separate from damage relative to GUARD. |

Overall register has 36 items: original 28 and new 8. Nine historical
candidates BSF/MIDI/audio sa nepreklasifikovalo on verify. Number 36 is not
count completion 12-bodových auditov. Ghidra selector 1010 denotes NE segment 3,
nie lineárnu address v ľubovoľnej IDA databáze. DB premenovania were not aplikované.

## 8. Status piatich track areas after this kole

| Area | What actually pribudlo | What sa thereby does not close |
|---|---|---|
| BSF | Zachovanie lower evidence level 7 historical aliasov. | New bodies C772/60AA/C696 were not získané. |
| MIDI | Corrected test predpoklad complete load SND address. | Selection skladby menu/level/DEMO remains without new original caller evidence. |
| Skripty | Separate aliasy 188AND/1E00 and AND1EA; new evidenčné boundary. | Order initialization 51AND4/51AND5 remains open. |
| OBJECT | Finding závažný rozpor damage reportov; added kolízne aliasy. | None new original writery +14/+16 nor define damage matica. |
| Audio events | Reprodukcie SND parsera, new loader and timer/sound okraj modelu. | New complete event → SND table nor original playback trace nevznikli. |

## 9. Test, writes, percentá

- C++20 kompilácia with `-O2 -Wall -Wextra -Wpedantic -Werror`: úspešná.
- SND: **13/13 test skupín**; only synthetic input.
- GUARD source helper: **160/160 check trajektórií**; nie original game.
- Damage reporty: **76 numerických buniek compare, 17 difference**.
- Four plné reference files: identical Git blob SHA-1.
- `git apply --check` on pripnutých reference file: úspešný.
- New binary verify original functions: **0**.
- Run/trace original game: **0**.
- GitHub writes and IDA/Ghidra premenovania: **0**.
- New overall or subsystémové percentá: **nevyčíslené**.

Plné output are v `evidence/all_cpp_test_results.txt` and
`evidence/damage_report_comparison_results.txt`. Spustenie without game data:

```sh
python tests/run_tests.py
python analysis/compare_damage_reports.py
```

## Source references

These references slúžia on identify podkladov; none original game binaries
sa v package nenachádzajú.

- https://github.com/marek177/Nitemare3d-reversed/tree/9d485e82a84ef1241eff7165c390c82eaff47970
- `src/formats/DatArchive.cpp`, `.hpp`, `BinaryIO.cpp`, `.hpp`: hashe v priloženom manifeste.
- `src/game/GuardSystem.hpp`: blob `0792595c4c55523d7df91ad15d7834cf729ecdc0`.
- `analysis/snd_index_audit.csv`: blob `8650c7f55cdeda96bda75901a393a88798813b67`.
- `docs/RE_AUDIT_CHEATS_AUDIO.md`: blob `9fbd71d07caf47f881fc25c3e8a4ae02580fda5f`.
- `analysis/nite3w_user_sav_story_flags_2026-09-23.md`: blob `cf14797841707cbfac65b7d47ad85d11375a2188`.
- `marek177/Nite3d-win3.11/docs/win16/audit-2026-09-24.md`: blob `0f95e2f81e95beb5b6d6aa82b0d32375ef284c05`.
- Two damage tables and reaction report are identify during corresponding finding.