# NITE3W — first pass piatich slabšie pokrytých areas

Date: 25. 9. 2026. Target: Windows NITE3W 1.10.

## Range actually vykonanej work

Prečítané were current available audity and source files project
`marek177/Nitemare3d-reversed` and Win16 audit v `marek177/Nite3d-win3.11`.
File `src/game/ObjectSystem.hpp` usage during kompilácii was prepísaný z output
konektora and verify git-blob hashom: **9b113feb4fdb52ba800and7f45d0aa79af5cdd51cd**,
3 786 bytes. Is to exact copy prečítaného file, nie manually upravená náhrada.

Original EXE, complete Ghidra export and IDA databáza were not v this working environment
sprístupnené. This prechod therefore contains **krížovú analysis reportov and code,
kontextové named and locally test modelu**, nie novú disassembláž original.
References on instructions v podkladoch are prevzaté z tam listed older auditov.

Reference hash EXE according to project podkladov:
`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`, 230 400 B.
This EXE was not v this kole znovu hashovaný nor running.

## Selection areas and percentá

| Area | Older orientačný estimate usage on selection | Result tohto kola |
|---|---:|---|
| BSF | 30–40 % | Distinguish old repo TODO from historical, nesynchronizovanej map 7 functions. |
| Selection MIDI | 40 % | Oddelený loader/directory from so far nepriradeného selectoru music. |
| Level skripty | 45 % | 10 proposal name; identify nesúlady flagov and obmedzený range 51AB. |
| Runtime arrays OBJECT | 50–55 % | 6 proposal name; kontextový projectile verify and kompilované test. |
| assign sound | 60–65 % | 3 proposal z reportov + 1 historical; separate wake and audio, označená neistota index. |

Numbers are older odhady z rozhovoru, nie dnešné measure entire EXE. New percentá
sa nevyčíslili. Some older values are zjavne pozadu for neskoršími finding;
also current repo status reject miešať format, named and runtime match to
jediného percenta. BSF does not have be after novšom historical audite automaticky považovaný
for still same unknown only therefore, that sa nezmenil old súhrn.

## 1. BSF: najprv nezamieňať missing write for missing poznanie

Repo konsolidácia still vedie six odkazov on `nite3d.bsf` and their rodičovské functions
as open. Neskorší finding z previous rozhovoru opisuje BSF also as
kontajner nápovedy/registračných text and states dispatcher operations, loader,
XOR check and text helpery. This história is not v read repo reporte
primerane zapracovaná. Sama osebe nenahrádza missing bytes and export.

Working addresses z histórie: `3:C772`, `3:60AA`, `3:C696`, `4:32E4`, `4:15B4`,
`4:17D8`, `4:19A6`. V registri have **history_only**. Neprezentujú sa as new
objavy tohto kola nor as verify original symboly.

**Distinguish problem:** count odkazov on name file, count rodičovských functions
and count operations dispatchera are three rozdielne counts. Six operations 0..5 nedokazuje
six XREF. Historical audit moreover korigoval Win16 counts compared with older DOS
prehľadu. Without original výpisu sa these counts do not have automaticky zjednotiť.

On primary check remains: input `C772`, doména commands, read blocks,
integritný akumulátor, key/initial phase decode and reakcia on skrátený
or damage block. This package neimplementuje neoverený dekodér nor patch
obchádzajúci check.

## 2. MIDI: loader is not selector skladby

Z kontajnerového auditu are known hudobné items 1..15. To does not determine, which hrá
v menu, v specific level, during rádiu or DEMO. Length address also does not determine
count hudobných vetiev game.

Historical candidate `FUN_1010_4592` is v registri as
`LoadSoundArchiveDirectories`, nie as `SelectLevelMusic`. Its address and complete
meaning remain on verify v exporte. For exact selector menu/episode/level/DEMO
sa **nevytvorila vymyslená address**.

String on doplnenie is: event game → choice logickej skladby → index/descriptor
SND → loader/temporary file → playback/MCI. Existencia `MCI temp file` and
`Tune %d not found` v starom binary audite ukazuje where search loader/playback,
nie sama osebe to, where sa rozhoduje o skladbe.

Z repeated change music v DEMO cannot without selectoru distinguish round-robin,
inkrementovaný index nor RNG. V this kole nevznikla confirmed complete table
30 levelov → MIDI and nor new identify its functions.

## 3. Skripty: state flags and exact names without vymysleného príbehu

Report trasuje `BFD8` through episode, zero level index and wall class `0x47/0x48`.
Z toho follows kontextové names handlerov v registri. For example index 6 is M7,
index 8 is M9 and index 9 is M10. Number episode remains 1..3.

### New findings tohto krížového auditu

**WITH-01 — tvrdenie o 51AND7 without game readera is not konzistentné with thereby istým reportom.**
byte table hovorí, that mimo save/restore was not found reader, but dispatch
matrix explicitne states condition `51A7 == 0` during E1M10/TRIGGER2. Korektný record
is: existuje supported gate-reader v dispatcheri; next subsequent consumer/text
remains open. This is error/neaktuálnosť reportu, nie preukázaný bug game.

**WITH-02 — initialization 51AND4/51AND5 potrebuje order writerov.**
Úvod states after `0EF6` bytes `01 00 00 00 00 00 00 00`; line o `51A5` at the same time
states initialize on 1. Can to be different phases initialization. Without writerov
cannot rozhodnúť, which description is nesprávny, nor zaviesť predvolený status kanónov
according to one izolovaného row.

**WITH-03 — 51AND6 sa nesmie change on bool.**
Report has prechod 0 → 1 → 2 and its read also v contact-damage branch. Is not to
only „text already was display“. Preserve byte and dokumentovať state meaning.

**WITH-04 — 51AB is not evidence univerzálneho pozastavenia sveta.**
Doložená is change shade/fill and skorý return z helpera `188A`. Separate Win16
scheduler report states movement door through `1E00`; z kontroly v `188A` cannot without
entire call grafu vyvodiť, that is vypnutý each movement all door.
Therefore nenavrhujem symbol `FreezeAllDoors` nor `PauseEntireWorld`.

**WITH-05 — object-property 0x40 has at least specific konzumenta.**
`9B64 → C356` is opísané as kolízna script branch, obmedzená on E2M10. This
upresňuje usage bitu v this branch, nie univerzálny meaning bitu in all
table, triedach and versions.

None name type „finálne víťazstvo“ or „Hamerstein zomrel“ sa nepriraďuje
only according to near text pointer whether write 51AA.

## 4. OBJECT: separate meaning same bytes v projectile

Existing `ObjectSystem.hpp` has 28-byte record. projectile report opisuje
42-byte record with 14-byte prefixom and vloženým OBJECT. Their spojením dostávame:

| OBJECT offset | Entire projectile | Supported meaning v projectile branch |
|---|---|---|
| +03 | +11 | Index frames animations, nie univerzálny signed animY offset. |
| +04 | +12 | Flight/impact sequence index. |
| +05 | +13 | Render flags; v opísanej branch sa during náraze sets 0x10. |
| +08..+0B | +16..+19 | Absolútny 32-bit term animations; jednotka sa tu nenazýva ms. |
| +18 | +26 | Projection cache; nesmie sa read as worldY. |
| +1AND | +28 | Vertikálny sprite offset for letu 5..20; nie vek projectile. |

**O-01:** generický name `animY` does not have be automaticky usage as signed coordinate
v each triede. For example byte 200 is unsigned frame 200, but during explicitnom
signed-offset výklade -56. Test verifies difference výkladov; netvrdí, that provided
assety real use frame 200.

**O-02:** `runtime08` is not completely without známeho usage. For vložený projectile
OBJECT is opísaný deadline. Nesmie sa however globally premenovať on this meaning,
until sa neuzavrú other classes. Doplnok uses kontextový view namiesto change ABI.

**O-03:** spodný komentár original headers states, that writer projection array
remains unknown, hoci komentár toho istého array and projectile audit identify
`CC7C`. Patch removes this neaktuálnu note; nevyhlasuje for closed exact
units cache, stale-cache behavior nor all projection branches.

`src/ObjectSemanticViews.hpp` is only doplnkový read-only pohľad. Nezmenil sa
layout original structures, were not derived new offset odhadom and was not added
neoverený update game. Arrays `+14/+16`, obyčajné classes use `+08` and missing
branches remain open.

## 5. Sounds: separate event, wake and number items

Repo report states after úspešnej streľbe `8B06 → 7664` and subsequently `B594`.
`7664` pracuje with store 64-byte wake cache and vybranými GUARD record;
`B594` selects/play attack sound. This sa does not have premenovať on jedinú function
`PlaySoundAndWakeEveryone`.

**AND-01:** wake branch v danom reporte does not have test vzdialenosti nor LOS and is not
modelom šírenia sound. During reconstruction sa therefore does not have mechanicky condition
execute doloženej wake operations thereby, that sa podarilo play audio. To nevylučuje
other audio/AI branches inde v EXE.

**AND-02:** parameter `7664` and player selector are not v popise two zameniteľné veci.
Parameter kľúčuje cache; GUARD filter is opísaný as comparison with store
`DAT_4C1C`. Alias therefore nepredstiera všeobecnú function „prebuď miestnosť X“.
Argument 0 is no-op; -1 čistí cache.

**AND-03 — zásadná check index priestoru:** historical audio audit states
SFX directory from `0xC0`, descriptor 6 B and prevod `physicalSlot = event + 32`.
Math is `0xC0 / 6 = 32`. Neskoršie príklady 27→59 and 33→65 with thereby súhlasia.
This východiskový binary finding sa v this kole nedal znovu verify.

Therefore sa `E3B0(0x44, ...)` nesmie without verify automaticky name as
physical `SND[68]`: during uvedenom historickom modeli by to was `SND[100]`.
Nor opačná korekcia sa nesmie execute plošne, until sa nepotvrdí specific caller,
loader and bankový posun. SND kontajnerový audit uses absolútne sloty;
nie all old game reporty jasne uvádzajú, which numeric priestor citujú.

Existencia PCM data from slotu 34 sama nedokazuje posun +34: bank can obsahovať
empty úvodné items. Opravy event→SND tabuliek are v this package marked as
**check on completion**, nie as execute new binary verifikácia.

## Register functions

All names below are analytické proposal. Are not to restore original symbol
development. `Report – proposal` mean oporu v prečítanom repo reporte, nie new
manual audit entire tela functions. `Len história – verify` is lower evidence
level and nesmie sa automaticky aplikovať.

Ghidra synthetic selector `1010` is NE segment 3, `1018` is NE segment 4.
These addresses sa do not have copy as lineárne IDA addresses. Real address určuje
load layout specific databázy. None databázové premenovanie sa nevykonalo.

| Original analytický symbol | Proposed meaning name | Area | Opora |
|---|---|---|---|
| `FUN_1010_BFD8` | `DispatchEpisodeLevelWallTrigger` | level_scripts | Report – navrh |
| `FUN_1010_BEF4` | `BeginE1M7ScriptedShadeEvent` | level_scripts | Report – navrh |
| `FUN_1010_BF20` | `HandleE1M10Trigger1` | level_scripts | Report – navrh |
| `FUN_1010_BF70` | `HandleE1M10Trigger2` | level_scripts | Report – navrh |
| `FUN_1010_BFA4` | `HandleE2M10Trigger1` | level_scripts | Report – navrh |
| `FUN_1010_BFBE` | `HandleE3M1Trigger1` | level_scripts | Report – navrh |
| `FUN_1010_BF8A` | `HandleE3M10Trigger1` | level_scripts | Report – navrh |
| `FUN_1010_C356` | `DispatchE2M10ObjectCollisionScript` | level_scripts | Report – navrh |
| `FUN_1010_C2B8` | `AdvanceE2M10CollisionScript` | level_scripts | Report – navrh |
| `FUN_1010_C5E2` | `SelectLevelShadeAndFillColors` | level_scripts | Report – navrh |
| `FUN_1010_CC7C` | `ProjectObjectAndCacheViewScale` | object_runtime | Report – navrh |
| `FUN_1010_9E20` | `UpdatePlayerProjectilePool` | object_runtime | Report – navrh |
| `FUN_1010_9AAC` | `TrySpawnPlayerProjectile` | object_runtime | Report – navrh |
| `FUN_1010_A930` | `SelectProjectileSequenceVariantA` | object_runtime | Report – navrh |
| `FUN_1010_A956` | `SelectProjectileSequenceVariantB` | object_runtime | Report – navrh |
| `FUN_1010_D1A2` | `InitializeRuntimeObjectMetadata` | object_runtime | Report – navrh |
| `FUN_1010_B594` | `SelectAndPlayPlayerAttackSound` | sound_events | Report – navrh |
| `FUN_1010_7664` | `UpdateShotTriggeredGuardWakeCache` | sound_events | Report – navrh |
| `FUN_1010_247A` | `GetDoorClassRelativeSelector` | sound_events | Report – navrh |
| `FUN_1010_C772` | `DispatchBsfOperation` | bsf | Only historia – overit |
| `FUN_1010_60AA` | `LoadAndDecodeBsfTextBlock` | bsf | Only historia – overit |
| `FUN_1010_C696` | `CheckBsfXorIntegrity` | bsf | Only historia – overit |
| `FUN_1018_32E4` | `XorTransformBsfBytes` | bsf | Only historia – overit |
| `FUN_1018_15B4` | `ParseFormattedText` | bsf | Only historia – overit |
| `FUN_1018_17D8` | `RenderFormattedTextPage` | bsf | Only historia – overit |
| `FUN_1018_19A6` | `RunTextHelpViewer` | bsf | Only historia – overit |
| `FUN_1010_4592` | `LoadSoundArchiveDirectories` | midi_selection | Only historia – overit |
| `FUN_1010_E3B0` | `RequestIndexedSoundEffect` | sound_events | Only historia – overit |

## Results testov and specifically files

C++17 kompilácia with `-Wall -Wextra -Wpedantic -Werror` was úspešná.
**4/4 test skupiny** verify: storage layout and posun vloženého OBJECT;
unsigned frame compared with explicitnému signed-offset výkladu; kontextové accessors;
and nezmenenie bytes during usage read-only view. Result is stored v
`tests/cpp_test_results.txt`.

These test confirm own doplnkového source modelu. Nepotvrdzujú
original hru, timing nor correct all older reportov.

- New binary verify functions v this kole: **0**.
- Original game run / runtime trace: **0**.
- Proposal aliasov podložené repo reportmi: **19**.
- Historical aliasy require primary check: **9**.
- Exact MIDI selector with overenou adresou z tohto kola: **0**.
- Writes on GitHub and premenovania v IDA/Ghidre: **0**.

`rename_register.json` has during each symbole area, verziu/address, reason,
source and boundary confidence. `object_field_comments.patch` upravuje only komentáre
original headers and does not change členy nor their type. `src/ObjectSemanticViews.hpp`
is separate local doplnok; was not connect to main CMake project.

## Podklady, according to ktorých possible audit zopakovať

Repository `marek177/Nitemare3d-reversed`; specifically git-blob SHA are also v JSON:

- `analysis/nite3w_user_sav_story_flags_2026-09-23.md` — blob `cf14797841707cbfac65b7d47ad85d11375a2188`.
- `analysis/nite3w_projectile_pool_2026-09-23.md` — blob `1a1329ea6b6ce4325181c51c0f3a593b419e0dc5`.
- `analysis/nite3w_guard_wake_cache_2026-09-23.md` — blob `b26e1a3ca7b7edad07040aefd5e067c664694ff0`.
- `src/game/ObjectSystem.hpp` — blob `9b113feb4fdb52ba800a7f45d0aa79af5cdd51cd`.
- `docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md` — blob `2f813587de67f22819459b632291891037eee628`.
- `docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md` — blob `4a56728507cd0940a460992294fd3245fb9e221f`.
- `docs/RE_AUDIT_CHEATS_AUDIO.md` — blob `9fbd71d07caf47f881fc25c3e8a4ae02580fda5f`.
- `analysis/nite3w_img_seqdef_2026-09-23.md` — blob `ccdbc4381dcf44d2a2bf08a47e0773df9f793c31`.

Doplnkový podklad: `marek177/Nite3d-win3.11`,
`docs/win16/audit-2026-09-24.md`, blob
`0f95e2f81e95beb5b6d6aa82b0d32375ef284c05`.
Historical BSF/audio addresses are explicitly separate from these repo podkladov.

## Najbližší primary analysis

Najviac new poznania teraz prinesie sprístupnený EXE or complete Ghidra C/ASM
export exact reference build: verify BSF `C772/60AA/C696`, SND loader
`4592` and audio `E3B0`; from their callerov search actual MIDI selector. During skriptoch
is prioritou order writerov `51A4/51A5`, during OBJECT all writery/reader-y
`+03/+08/+14/+16` rozdelené according to class. Register is pripravený, no missing bodies
sa must not add domysleným pseudokódom.