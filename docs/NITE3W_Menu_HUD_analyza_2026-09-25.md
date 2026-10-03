# NITE3W — audit Menu/HUD

**Date:** 25. 9. 2026. **Range:** Win16 NITE3W 1.10; existing analysis and current rekonštruovaný C++ code. **Output:** analytická message, reprodukčné test and proposal úpravy load.

## What sa v this priechode actually vykonalo

Prečítané were project messages and source files through connect GitHub. Six load file C++ was prenesených locally and their content verify proti Git blob SHA-1. Reference commit and individual check súčty are v `source_manifest.json`. Original also upravené load were skompilované and run on 14 synthetic test.

**Original NITE3W.EXE nor actual UIF.DAT were not during this priechode k dispozícii.** Nebolo performed new disassemblovanie their bytes, measure v DOSBox-X/Windows 3.1 nor comparison original framebufferov. Addresses EXE below are prevzaté z identify project analysis, nie novým independent confirm z binaries. Úpravy were not zapísané to GitHubu.

Reference EXE according to messages WITH11: version 1.10, 230 400 bytes, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Write `3:xxxx` mean number NE segment and offset. Is not to runtime selector nor univerzálna address for all vydania.

### Levels evidence

- **REPO-EXE:** older analysis states priamy static evidence z original EXE; v this priechode prečítaný and compare, nie opätovne disassemblovaný.
- **SOURCE:** directly prečítané telo súčasného rekonštruovaného source code.
- **TEST:** actually running local reprodukčný test.
- **INFERRED:** odvodenie, which needs to verify separate evidence.
- **OPEN:** missing exact evidence or complete reconstruction.

## 1. Najdôležitejší poznatok: HUD is not only draw

Message WITH2 identify `DS:4C1D` as byte zdravia player. Branch `3:A4CE..A502` value without znamienka obmedzí on 100, writes ju back and displays. Ide therefore also o mutáciu game state, nielen o output on image. Status evidence: REPO-EXE.

```text
health = min_unsigned(health, 100)
uložiť health späť do DS:4C1D
formátovať/zobraziť health
```

WITH2 states also path zberu liečenia, which najprv test `health < 100`, then pripočítajú value and up to subsequent HUD/update branch ju obmedzí. Ilustračný consequence during prírastku 20: 95 → 115 → 100. This numeric example is odvodenie z opísanej operations, nie capture runtime priebeh.

**Consequence for port:** change on čisto display function `drawHud(const State&)` is safe up to vtedy, when sa original write move to explicitnej update state with zachovaním needed poradia. Vynechanie write can meniť zdravie after zbere predmetu. Value 0xFF sa tu interpretuje as 255, nie as -1. Clamp on 100 itself osebe is not detekcia smrti.

Priame call `A4CE` z `BA54` sa v this priechode nedokázalo. These two addresses therefore must not be without check call graphu spojené vymyslenou šípkou.

## 2. Zapojenie HUD to kresliaceho cyklu

WITH11 states for branch Win16 1.10 `3:DA4B..DA80` this postupnosť:

| Address | Role listed v audite |
|---|---|
| `3:D8FC` | Osobitná otáčacia/state branch |
| `3:D78C` | Zvýšenie render generácie and render/projection |
| `3:BBCA`, `3:BA54` | Nadväzujúce player/HUD branches |
| `3:1E00` | Update door records |
| `3:9E20` | Update projectile poolu |
| `3:3AB8` | Prezentácia image; its vyvolanie is condition |

Separate kalibračná path `3:D7C0` is according to toho istého auditu `D78C → BA54 → 3AB8`. HUD branch sa therefore nachádza between render and prezentáciou also v kalibračnej path. To **nedokazuje**, that sa always draw each pixel HUD. Vnútri can be compare starých values, dirty flags, cache or condition for individual elements. Tie remain OPEN.

WITH3 udáva framebuffer 320 × 200 and viewport x=8..311, y=4..155 including okrajových coordinates, therefore 304 × 152. Z toho cannot vyvodiť exact obdĺžniky portrétu, number and ikon. increase screens zahŕňa also rámovanie.

## 3. Inventory data, which HUD uses or has use

Following addresses are for reference branch Win16 1.10, according to WITH1–WITH3. Znalosť source array is not automaticky evidence exact draw read.

| Data item | Source | Confirmed / open |
|---|---|---|
| Zdravie | `DS:4C1D`, byte | Source also clamp/write v `A4CE..A502` are v WITH2 identify; exact glyfy/obdĺžnik nie |
| Score | `DS:4C16` | WITH3 pomenúva spodné word; netvrdiť, that entire score is only 16-bit |
| Strieborná ammo | `DS:4C1F` | Source named; complete tok to specific widgetu open |
| Laserová ammo | `DS:4C20` | Source named; exact display open |
| Ammo prútika | `DS:4C44` | Source named; exact display open |
| Active weapon | `DS:4C23` | 0 laser, 1 prútik, 2 strieborná pištoľ, 3 kontinuálny laser; 0xFF nenastavená |
| Color keys | `DS:4C28` | Mask inventory; complete link bit → color → ikona open |
| Cards | `DS:4C29` | Mask inventory; WITH4 viaže bit 0 on červenú kartu, nie all HUD sloty |
| Pentagramy | `DS:4C45` | Bits 0/1/2/3 are according to WITH1 červený/zelený/modrý/žltý; výrezy ikon open |
| Player position | `DS:4BF6`, `DS:4BF8` | World coordinates; exact read and format HUD array open |

Numeric pár pod ikonou weapons is according to visual auditu WITH1 field v map, nie time. WITH3 states 64 svetových jednotiek on cell. Výraz `(worldX >> 6, worldY >> 6)` is therefore prirodzený candidate for display; without priameho HUD read however does not close order osí, case korekciu o 1 nor format.

Three visible pointer sa must not automaticky assign trom address ammo only therefore, that obe skupiny have count three. Needed is reader/draw xref for specifically array.

## 4. Right panel, automapa and portréty

### Automapa

WITH4 already pomenúva block `USER.SAV +0xC5A3..+0xD5A2` as 4096-byte raster/index buffer automapy. Range has exactly 4096 bytes, what corresponds to 64 × 64. Meaning each byte values remains partial. Is podstatne viac than neurčitý „unknown save block“.

WITH1 however still necháva function right čierneho obdĺžnika HUD open. Buffer automapy and visible panel are not still spojené evidence o target obdĺžniku draw calls. Therefore conclusion znie: **existencia data automapy is doložená v project, exact link on specific HUD panel is not v this priechode uzavretá.**

### Portrét

WITH1 states visually confirmed change vzhľadu according to state player. Undetermined remain count images, boundary HP, case temporary pain status, selection smrti and links on specifically grafické items. Z clampu zdravia cannot odvodiť prahy portrétov. Nevytvárať v reconstruction svojvoľnú table for example after 20 HP and nepomenovať ju as original.

## 5. Menu: what is v súčasnom source code

Priame read WITH5 ukazuje following model. This is SOURCE evidence o reconstruction, nie completion extrakcia natívnych Windows menu resource ID.

| Status | Count | Items v order |
|---|---:|---|
| Game is not active | 6 | New game; Configure game...; Load game...; Instructions; Demo; Quit |
| Game is active | 7 | New game; Configure game...; Load game...; Save game...; Instructions; Return to game; Quit |
| Konfigurácia | 3 | Hardware...; Cheats...; Done |
| Choice difficulty levels | 3 | Be gentle!; I'm tough!; Let'with party! |
| Choice episodes | 1 or 3 | According to `hasCompleteTrilogy(edition)` |

Important detail: active game v this code **nepridáva only two items**, but at the same time removes Demo. Therefore has 7, nie 8 items. Kratší text v WITH6 this difference completely nerozpisuje.

WITH6 states, that jednoepizódová edícia command Cheats ukazuje, but reject aktiváciu without complete trilógie. Display items and povolenie its účinku therefore needs to test osobitne. Also states 22 position for návod; verejný model nenahrádza original plné text all strán.

`Menu.cpp` zostavuje lists items and action. Itself this file does not close hit-test, kurzor, key repeated, draw, sound confirm, modalitu dialog, resource ID nor MFC dispatch.

## 6. Osobitná Windows/MFC layer

WITH7 and WITH8 identify `CMenu`, `CCmdTarget`, map HMENU on `0x4548` and descriptor CMenu on `0x0746`. To confirms architektúru natívneho menu, nie complete table game commands.

During rozbore handlerov needs to distinguish execute command from update its vzhľadu. Dokumentácia Microsoft CCmdUI (WITH12) opisuje `Enable`, `SetCheck` and `SetRadio` as change state element use interface. Finding `SetRadio` therefore itself osebe nedokazuje, that daná function naozaj changes distinguish. same zaškrtnutie music is not evidence štartu/prepnutia playback.

Moderná dokumentácia slúži on vysvetlenie tohto distinguish, nie as evidence exact Win16 ABI or specific historical map ID. Complete string požadovaná for each command is:

```text
menu/accelerator ID → dispatch → vykonávací handler → zápis stavu/akcia
                       ↘ UI-update handler → enabled/check/radio stav
```

Historical uvádzané addresses key adaptérov, names F4/F5 whether resource ID, which sa v this priechode nepodarilo directly verify, are not povýšené on newly confirmed findings.

## 7. New priamy audit C++ load for UI grafiku

### 7.1 Fixed directory sa cannot spoľahlivo count condition konca payloadu

WITH9 reads 6-byte records `(uint16 length, uint32 offset)` and ends, when `offset + length == fileSize`. This condition can identify last obsadený payload, but does not have to identify last slot fixed address.

Synthetic test creates profil with 32 slotmi, obsadenými 0..16 and prázdnymi 17..31. Original function returns **17 items**, nie 32. Proposed explicitná path `loadFixedDirectory(path, 32)` returns all 32 including prázdnych slotov. Status: SOURCE + TEST.

**Profil 32 slotov is v this priechode test predpoklad. actual UIF.DAT sa neotvoril.** Result therefore is not novým measure original file nor evidence damage display v original hre. Is evidence obmedzenia existing generického load during fixed address.

Proposed API ponecháva original generický `load()` nezmenený. call must poznať correct count slotov and explicitne zvoliť fixed path; patch still does not change call miesta celej aplikácie.

### 7.2 Payload prekrývajúci directory

Original code checks range file, but dovolí neprázdny payload začínajúci on offset 0, therefore v address. Synthetic damage input was prijatý. Fixed profil reject neprázdny payload, whose offset is menší than `entryCount * 6`. Is to ochrana before incorrect file, nie evidence, that original game this status creates.

### 7.3 Rozmery PCX: zúženie 65 536 on nulu

WITH10 count rozmery z krajných coordinates and ihneď their prevádza on `uint16_t`. For `xmin=0, xmax=65535` is math width 65 536, after zúžení however 0. Analogicky for height. Test confirm, that original dekodér also input prijal. Proposal najprv count v `uint32_t` and verify range reprezentácie; oba cases then reject.

### 7.4 Zero RLE length

Token 0xC0 can length behu 0. Original dekodér ho spotrebuje without output pixel; proposal ho reject. This is **intentionally prísnejšia valid field**, nie tvrdenie o dokázanom behavior original NITE3W dekodéra. Before plošným nasadením needs to verify real historical assety.

## 8. Actually run test

Kompilátor GCC 14.2.0, C++20, Linux. Original and upravené variant were test with AddressSanitizer and UndefinedBehaviorSanitizer; were not message diagnostic sanitizérov. Output is v dvoch text protokoloch.

| Check | Original code | Proposal |
|---|---|---|
| PCX obyčajné pixely and palette | PASS | PASS |
| PCX RLE lines | PASS | PASS |
| PCX doplnenie riadkov | PASS | PASS |
| Synthetic PCX 320 × 200 | PASS | PASS |
| Missing palette reject | PASS | PASS |
| Skrátený pixel tok rejected | PASS | PASS |
| Príliš long beh rejected | PASS | PASS |
| Width 65 536 reject | FAIL | PASS |
| Height 65 536 reject | FAIL | PASS |
| Zero RLE beh rejected, strict policy | FAIL | PASS |
| Zachovaných all 32 slotov | FAIL | PASS |
| Last slot obsadený | PASS | PASS |
| Payload mimo file rejected | PASS | PASS |
| Neprázdny payload v address rejected | FAIL | PASS |
| **Sum** | **9/14** | **14/14** |

Five neúspešných check **does not mean five missing v original NITE3W.EXE**. Two check sa týkajú jednej classes errors with zúžením rozmeru; jedna is sprísnená field. Test verify only define own load on synthetic input. Neoverujú pixel match original HUD, state machine menu nor correct all file game.

## 9. Register open question and evidence needed on uzavretie

| Area | current | Specific missing evidence |
|---|---|---|
| Zdravie | Známy source also clamp from messages | Priamy caller/callee tok and runtime order relative to zberu predmetu |
| Ammo | Known source bytes | read specific widgetu, format, case cache |
| Score | Známa spodná part values | Entire width, format, count number, pretečenie |
| coordinate | Array identify visually | Exact prevod, order osí, index from 0/1 |
| Portrét | Viac state visually | Count výrezov and exact prahy/state priority |
| Inventory | Source mask | Complete map bit → item → grafika → target obdĺžnik |
| Automapa | Známy save buffer | Target draw, meaning index and link on right panel |
| Obnova HUD | Known miesto render branches | Dirty flags, old values, complete vs partial obnova |
| UIF grafika | Test generický/fixný loader | Original directory, all type items, grafické index and palette |
| Game menu | Prečítaný model items | Original state, obsluha input, draw and modalita |
| Windows menu | Známa MFC infraštruktúra | Complete resource ID/accelerator/message-map/handler prepojenie |
| Runtime ekvivalencia | V this priechode neoverená | Párové logy state and framebufferov original vs reconstruction |

Zvýšenie percenta completion entire Menu/HUD sa tu netvrdí: neexistuje closed inventory all its functions and vetiev. Measure result tohto priechodu is check šiestich file, specifically reprodukcie load, proposal opráv and exact oddelenie game state, draw and Windows menu.

## 10. Content package and usage

`original/formats/` contains exactly verify versions šiestich file; `patched/formats/` proposed change. `test/hud_resource_test.cpp` creates only synthetic data. `resource_loader_proposal.patch` is diff relative to reference file. `README.md` contains zostavenie and limity integrácie. Original binaries nor grafika game are not part of package.

## Zdroje

Project messages are sekundárnym evidence o original EXE; source files are priamym evidence o súčasnej reconstruction. References are pripnuté on read commit. Technické conclusions z test are supported priloženými reprodukciami and protokolmi.

- **WITH1:** [docs/HUD_UI_RE.md](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/docs/HUD_UI_RE.md)
- **WITH2:** [docs/PLAYER_HEALTH_RE.md](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/docs/PLAYER_HEALTH_RE.md)
- **WITH3:** [src/game/RecoveredRuntime.hpp](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/src/game/RecoveredRuntime.hpp)
- **WITH4:** [docs/PROJECT_FINDINGS_DELTA_2026-09-23.md](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/docs/PROJECT_FINDINGS_DELTA_2026-09-23.md)
- **WITH5:** [src/ui/MenuModel.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/src/ui/MenuModel.cpp)
- **WITH6:** [docs/MENU_INSTRUCTIONS_CHEATS.md](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/docs/MENU_INSTRUCTIONS_CHEATS.md)
- **WITH7:** [analysis/nite3w_Win16_mfc_memory_2026-09-25.md](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/analysis/nite3w_win16_mfc_memory_2026-09-25.md)
- **WITH8:** [docs/WIN16_MFC_RE_SUMMARY.md](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/docs/WIN16_MFC_RE_SUMMARY.md)
- **WITH9:** [src/formats/DatArchive.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/src/formats/DatArchive.cpp)
- **WITH10:** [src/formats/Pcx8.cpp](https://github.com/marek177/Nitemare3d-reversed/blob/45777ac20d0bf5bb57b0452d1a8281eddd87ee03/src/formats/Pcx8.cpp)
- **WITH11:** [Win16 viacverziový audit 24. 9. 2026](https://github.com/marek177/Nite3d-win3.11/blob/791394730187ae0ded48e423fd11aa0d68f70f10/docs/win16/audit-2026-09-24.md)
- **WITH12:** [Microsoft Learn — CCmdUI](https://learn.microsoft.com/en-us/cpp/mfc/reference/ccmdui-class?view=msvc-170), verify 25. 9. 2026. usage only on distinguish execute command and update UI, nie on historical ABI.