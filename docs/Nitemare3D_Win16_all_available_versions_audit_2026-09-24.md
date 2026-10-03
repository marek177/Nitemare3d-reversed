# Nitemare3D for Windows 3.x / 3.11 — audit all available versions

Date: 24. 9. 2026. Platform: Win16. Range: directly provided EXE 1.3, 1.6, 1.8 and 1.10, their Ghidra C exporty and data attached k shareware 1.3/1.6/1.8.

> Follow analysis all 40 areas is completion v `Nitemare3D_Win16_40_oblasti_hlbkovy_audit_2026-09-24.md`. Each area has separate finding, evidence, version range and next test; open items v this original registri needs to read total with new reportom. Especially DEMO timestamp was subsequently confirmed as generation index; EOF/runtime termination remains open. New report fix also score table, contact difficulty multiplier, virtual key and several pointer/field interpretation older main referencie. Is not complete uzavretie all subsystem.

## Result and hranice

Audit verify identitu four different Windows build, create register **3 856 version functional block** and priniesol new priame findings o time, order update, calibration, palette, sound and difference map. Analysis fix multiple older claim o time. Twelve separate nahraných file `nite3w*.exe` are identical copies referencie 1.10.

**Is not to completion all unknown nor 3 856 manual semantic auditov.** Register is automatic structural inventory. Detailed new check sa concern specific question listed below. Obtain runtime records v this audite: **0**. Additional historical release or registered variant without provided binary file cannot mark for examined. Exist other numbers versions this documentation nepredpokladá.

`Confirmed / High` mean priamy static evidence v byte or data, nie automatic experiment during behu. `Inferred` denotes derived meaning or consequence. `Unknown` remains open. Addresses `3:xxxx` are **ordinal number NE segment and offset**, nie runtime selector, physical address nor Ghidra linear address. Ghidra `FUN_1010_xxxx` v these exportoch corresponds to NE segment 3.

## 1. Identita vstupov

| Version confirmed string v EXE | Size EXE | Functional blocks `FUN_*` | SHA-256 EXE |
|---|---:|---:|---|
| 1.3 | 229 136 B | 959 | `926c0001944b9822cdae10b35c92c2d6cd3772bc774c4c88fb17df7465d1f156` |
| 1.6 | 230 128 B | 965 | `5851849bacd8b03e93444d8a8f34d51c23fecddc73d6b8df7f016885c3b9d418` |
| 1.8 | 230 224 B | 965 | `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22` |
| 1.10 | 230 400 B | 967 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |

First three EXE come from z use `nitemare3d-shareware+images.zip`, internal path are v `build_inventory.csv`. Referencia 1.10 is provided `nite3w.exe`. All four are NE programy with desiatimi segment. C exporty are not original source codes and contain incorrect derived prototypy, far pointer and symbol aliasy.

**identify pasca:** fixed numeric version v `VS_FIXEDFILEINFO` is in all four EXE **1.0.0.1**. Themselves this array does not distinguish release. Decide hash and vstavaný string `Nitemare-3D for Windows V…` on file offset 1.3 `0x2C716`, 1.6 `0x2CA38`, 1.8 `0x2CA98`, 1.10 `0x2CBD6`. Status: Confirmed / High.

## 2. Main correction: two different rytmy game

Previous audity pripisovali GUARD, cooldownom and fire shared interval derived from `DAT_53F2`. **Bytes all four EXE prove other architecture.**

| Role | 1.3 | 1.6 | 1.8 | 1.10 |
|---|---|---|---|---|
| read time | `3:D4A4` | `3:D618` | `3:D618` | `3:D6C6` |
| Counter nominal 8 Hz | `3:D4E8` | `3:D65C` | `3:D65C` | `3:D70A` |
| Counter calibration frame krokov | `3:D528` | `3:D69C` | `3:D69C` | `3:D74A` |
| Render/generation | `3:D56A` | `3:D6DE` | `3:D6DE` | `3:D78C` |
| Calibration | `3:D5AE` | `3:D722` | `3:D722` | `3:D7D0` |
| Slow update AI and state | `3:D752` | `3:D8C6` | `3:D8C6` | `3:D974` |
| Plan | `3:D7A4` | `3:D918` | `3:D918` | `3:D9C6` |
| Spracovanie player vstupu | `3:95E4` | `3:9758` | `3:9758` | `3:9806` |
| Prevent/counter shoot | `3:A86E` | `3:A9E2` | `3:A9E2` | `3:AA90` |
| Contact fire | `3:BC40` | `3:BDB4` | `3:BDB4` | `3:BE62` |

Addresses, lines C exportov, exact clip assembly and NE relocations are v evidence package. First 63 bytes auxiliary routines 8 Hz is in all four EXE identical. Check is independent from normalize C text.

### 2.1 Nominal 8 Hz and omitted steps

Win16 1.10 `3:D70E–D73B` executes:

```text
bucket = ((uint32(time_ms) << 3) modulo 2^32) / 1000
if bucket != previous_bucket:
    previous_bucket = bucket
    logical_slow_counter += 1
return logical_slow_counter
```

Uses DS `022C` for last bucket and DS `0228` for logical counter, oboje 32-bit. During sufficiently time call is normal rytmus 8 krokov/with, therefore nominal 125 ms between krokmi. **Omitted buckety sa do not catch up:** after preskoku z 0 on 1 000 ms sa counter increments raz, nie o eight. Plan also neobsahuje loop, which by znovu execute all missed slow update-y. Confirmed / High.

V mode `mode == 0` plan according to tohto count calls slow update. During `mode != 0` is separate branch: update is naviazaná on nepárnu render generation before its increase, therefore v related this path on each second frame. Global variable is v 1.10 DS `46B8`; exist DEMO path ju use. Nie each nonzero value tu name as one universal mode playback.

**Consequence:** 125 ms is not zaručený time each GUARD kroku for all okolností. Slow stroj, pauzy, change mode and different path can change actual time. To however does not justify replace 8 Hz expression `1000 / DAT_53F2`.

### 2.2 Calibration measure draw, nie five krokov AI

`3:D7D0` v 1.10 executes one prípravný render, measure **five call `D7C0`**, while `D7C0` calls render `D78C`, follow HUD branch `BA54` and presentation `3AB8`. V this measure loop does not call `D974`.

During normal positive time value is derived model:

```text
raw_mean_ms = floor(uint32(end_ms - start_ms) / 5)
DS:53F2 = low16(raw_mean_ms)       // zápis PRED spodným obmedzením
D = max(raw_mean_ms, 40)          // lokálna efektívna hodnota
DS:53F4 = floor((1000 + floor(D/2)) / D)
DS:53F6 = max(1, floor((D+2)/4))
DS:53F8 = max(1, floor((360*D+1400)/2800))
DS:53FA = 2 * DS:53F6
```

Example during raw priemere 10 ms: **53F2 ostane 10**, locally D is 40, frame rate 53F4 is 25, movement step 10, angular step 5, projectile count podkrokov 20. Write `53F2` on `3:D863` sa after local clampovaní on `D873` neopakuje. Confirmed for all four build. Extreme signed/verify cases these calculation remain separate question; pseudocode their nezovšeobecňuje.

| Array | 1.3 DS | 1.6 DS | 1.8 DS | 1.10 DS |
|---|---|---|---|---|
| Render generation | `531A` | `53CC` | `53DC` | `53DC` |
| Raw priemer merania | `5330` | `53E2` | `53F2` | `53F2` |
| Calibration frame tempo | `5332` | `53E4` | `53F4` | `53F4` |
| movement step | `5334` | `53E6` | `53F6` | `53F6` |
| Angular step | `5336` | `53E8` | `53F8` | `53F8` |
| projectile podkroky | `5338` | `53EA` | `53FA` | `53FA` |
| Mode plan | `45F8` | `46A8` | `46B8` | `46B8` |

Frame helper 1.10 `3:D74A` uses `low32(sign_extend_16(53F4) * time_ms) / 1000`. During change result also increments own logical counter only raz. Leave 32-bit clip is simultaneous verného model; is primary bytes `MUL`, vymazanie EDX and `DIV`, nie o unlimited integer multiply.

### 2.3 Shoot and fire: correction jednotiek

In all four EXE is DS `01F6..01F9 = 02 01 03 01`, DS `01FC..01FE = 64 0A 02`.

`AA90(1, …)` increments counter DS `01FA`, saturujúci on 255. Slow update ho calls raz on step. `AA90(0, edge)` accept shot up to after reach prahu, zeros counter; weapon index 3 allow hold input, during others branch sa uses hrana. Input then calls own shoot, v ktorej still platia additional condition.

| Index weapons | Prah slow krokov | Nominal ustálený time prahu during 8 Hz |
|---:|---:|---:|
| 0 | 2 | 250 ms |
| 1 | 1 | 125 ms |
| 2 | 3 | 375 ms |
| 3 | 1 | 125 ms |

These time are **derived**, nie odmerané shot. Phase input relative to next ticku, ammo, pool projectile and weapon animation branch can result kadenciu change. Is not evidence, that each weapon strieľa exactly every listed X ms.

Contact fire remove 100/10/2 HP for **slow update**, if prejde its class/invulnerability prevent. During sufficiently time plan v mode 0 is derived tempo stredného/small fire 80/16 HP/with. Large fire during HP ≤ 100 zabije during element accepted škodovom update. Expression „damage × 1000 / 53F2“ from older auditu is incorrect for this branch.

### 2.4 Order frame branches and cache projekcie

Win16 1.10 `3:DA4B–DA80` confirms this order; 1.3/1.6/1.8 have correspond sequence:

1. `D8FC`: separate otáčacia/state branch.
2. `D78C`: increase generation and render/projection.
3. `BBCA`, `BA54`: follow player/HUD branches.
4. `1E00`: posun door records.
5. `9E20`: update projectile poolu including collision.
6. `3AB8`: presentation, skip during `46B6 == 8`.
7. `9806`: process input, movement player, shoot and USE.
8. set following frame deadline/counteru.

**Confirmation:** render v this branch precede update projectile i input. Is not correctly automatic reconstruct order „input → all simulation → render“.

**What sa thereby neuzavrelo:** `OBJECT+18` sa v `3:CC7C` writes only after prechode projection/visible condition and add sprite slotu. Themselves earlier zavolanie render therefore neobnoví cache each object. During projectile hit mimo this path still needs to compare last write +18 and time damage. Order is static closed; universal current array remains Unknown.

## 3. actual differences Windows release

### 3.1 Palette: 1.8 → 1.10

**Confirmed / High, C + raw instructions + NE importy.**

| Path | Win16 1.8 | Win16 1.10 | Consequence |
|---|---|---|---|
| Initialization palette | `3:3136` take over game colors 10..245 | `3:31AA` selects okraje 10/10 during `46AF != 0`, otherwise all 256 | Branch sa prispôsobuje schopnosti device work with palette. |
| Hromadná animation | `AnimatePalette` only during handle and `46AF != 0` | During handle calls `AnimatePalette`; during `46AF == 0` moreover `3:3100` | V 1.10 pribudne paint/realize/redraw path. |
| Change jednej colors | `3:32B2`, WinG call only during `46AF != 0`; pointer always on base `DS:4D9A` | `3:3360`, WinG call also without this condition; pointer `DS:4D9A + 4*index` | To WinG sa posiela just modify RGBQUAD. |

Last difference is directly v instruction: 1.8 `3:3326 push 4D9A`; 1.10 `3:33C8 add bx,4D9A` and `3:33CD push bx`, while BX already contains `index*4`. Target importu is `WING#1006`.

`46AF` v initialize arise z test `GetDeviceCaps(..., 0x26) & 0x100`, correspond `RASTERCAPS / RC_PALETTE`. Is not general flag „WinG enabled“. identify API is support documentation Microsoftu; Win16 ABI argumenty were during select callsite-och check v assembly. [GetDeviceCaps](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-getdevicecaps).

Visual dosah on specific driver and actual image during fade/dark evente is **Unknown** to runtime compare. Programátorsky needs to these differences leave during emulation specific release.

### 3.2 Sound: 1.6 → 1.8

Win16 1.8 `3:E016` and 1.10 `3:E0C4` during initialize obtain original MIDI and wave hlasitosti to DS `3A5C` and `3A60`, recorded success to `3A64/3A65` and during terminate condition restore stored values. V correspond init/cleanup routine 1.3 `3:DDA4` and 1.6 `3:E016` these get/restore calls are not.

Exact callsite-y 1.8: `E07A` MIDI get, `E091` wave get, `E18B` MIDI restore, `E1A2` wave restore. NE importy `MMSYSTEM#211/#415/#212/#416`; C export their identify as `midiOutGetVolume`, `waveOutGetVolume`, `midiOutSetVolume`, `waveOutSetVolume`. Status: Confirmed / High for these path. Successful on each historical device sa thereby nedokazuje. [MIDI call API](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-midioutgetvolume), [wave call API](https://learn.microsoft.com/en-us/windows/win32/api/mmeapi/nf-mmeapi-waveoutgetvolume).

### 3.3 call introductory image v 1.6

Between 1.3 and 1.6 pribudla v exporte path `1.6 4:2E68 → 3:5AF2`. Pokúša sa load `dstopen.img`; decode reads 128-byte header with introductory byte `0A` and RLE bytes `C0..FF`, render after 320-byte row to 200 row. After success caller displays image and waits 2 000 ms. To supports designation **PCX-like loader**. Exact visible image remains Unknown, because `dstopen.img` v unpack troch shareware package is not. Presence code is not evidence, that sa image during each startup displays.

## 4. Data: nepredpokladať match only according to size

compare were directly files v unpack provided Windows shareware address; claim platia for these specifically package.

| File | 1.3 → 1.6 → 1.8 |
|---|---|
| `IMG.1`, `DEMO.1`, `SND.DAT`, `UIF.DAT`, `GAME.PAL` | byte identical including SHA-256. |
| `MAP.1` | 1.3 = 1.6; 1.8 has exactly two change bytes. |
| `NITE3D.BSF` | All three different; meaning difference was not this prechodom decode. |
| Sada data directly patriaca k provided 1.10 | V this audite was not supported complete package; match cannot automatic transfer. |

### 4.1 E1M5: premiestnený object

Header `MAP.1` is v trojici same and count blokov is 11. During mapovom vzorci `514 + (map_index*8192) + ((y*64+x)*2) + layer`:

| file offset | Mapa | coordinate from nuly | Vrstva | 1.3/1.6 | 1.8 |
|---|---|---|---|---|---|
| `0x09337` | E1M5 | x=26, y=34 | object | `00` | `D8` |
| `0x093B7` | E1M5 | x=26, y=35 | object | `D8` | `00` |

ID `D8` has v match object class table class `27h`. Exact asset name tu is not derived from general name classes. Posun represent difference data, nie automatic change code AI. Confirmed / High.

### 4.2 GAME.PAL we have for these three package

This `GAME.PAL` has 5 459 bytes and is **8-bit PCX 320×200**, nie holých 768 RGB bytes. On `0x1252` is marker `0C`; nasledujúcich 768 bytes from `0x1253` forms 256 RGB triples. Independent decode through Pillow confirm rozmer, mode P and match palette with last 768 byte file.

V package are `GAME_PAL_256_RGB.csv` and `GAME_PAL_RGB_768.bin`, SHA-256 extracted palette `62440016fb400e630187c10d5797588a4c3d225a8e5e872528fac7dd8222784d`. Confidence High for these assety; usage identical palette during ľubovoľnom inom EXE/episode or specific shade events needs to confirm separate.

## 5. Register functions and meaning its numbers

`all_windows_function_blocks.csv` contains each recognize block `FUN_*` from four exportov: source, version, lines, signatúru, hash tela, priame calls and indikáciu indirect call. Sum 3 856 include versions tej istej routines repeated, is not 3 856 different functions game.

Konzervatívne comparison tvaru C tela with address symbol premenovanými according to poradia occurrence found relative to 1.10 jednoznačných candidates 450 v 1.3, 490 v 1.6 and 514 v 1.8. **This are not percent pochopenia nor evidence behavioral matches.** Normalize preserves literals and repeated identity symbol, but does not guarantee same globally data, call address whether correct decompile. increase include change, nejednoznačné small functions and different errors exportu; cannot ho nazvať „everything unknown“.

Previous tracker 65 completion manual auditov sa this automatic does not increase. This prechod provided separate verify questions and evidence; export 52 select C/ASM pairs also is not evidence 52 completion 12-point auditov whole functions.

## 6. What remains unknown across Windows verziami

Register sa sústreďuje on questions, which answer can change reconstruction. „Remains static“ mean, that work does not have to wait on use debugger. „Runtime“ mean, that needs to actual beh on exact build; video samo osebe spravidla neukáže values fields.

| Area | Posun tohto auditu | remain questions and next distinguish step |
|---|---|---|
| Complete versions | 4 unique EXE verify hashom | Additional Windows/registered build: inventarizovať only after obtain their EXE and data. |
| Functional boundary | Register all 3 856 exported block | Remains static: short thunky, merge bodies, nedekódované entry/callback targets. |
| MFC, vtable, message map | Preserved separate from game logic | Remains static: constructor → vptr → table → target for all dosiaľ unnamed items. |
| Initialization and termination | Selected change palette/sound | Remains static: complete ownership allocate and cleanup all mode. |
| Argumenty and debug path | Find new logger/intro branches | Remains static: entire parser and each caller, including call assetov. |
| Main plan | Two rytmy and frame order verify v 4 EXE | Runtime: focus/menu/pause/load prechody and reset count; static close all callerov. |
| Timing | 8 Hz, calibration and without dobiehania closed for check path | Runtime: latencie timer API, wrap, overload and modes DEMO. |
| RNG | Previous algoritmus was not change | Remains static: complete order odberov/seed reset; runtime deterministic replay. |
| Keyboard and input | Input is on konci frame branches | Remains: all hrany, repeated and concurrency input during pauze/strate fokusu. |
| Mouse and joystick | Caller belongs to frame branches | Remains: dead-zone, znamienka, limity and chovanie driver after versions. |
| Player movement | Calibration steps have exact origin | Remains static/runtime: rohy, diagonal, sliding, field and dynamic obstacle. |
| Doors and secret panel | Movement door is after render v frame branch | Remains: all state, block, orientation/tie cases and save/load uprostred movement. |
| Push objects | Slow update is separate domain | Remains: writer state, repeated during block and class-specific effect in all versions. |
| USE, safe, trunk, radio | Without new complete auditu handlerov | Remains static: all condition, success/cancel and change map. |
| Teleporty/elevator | Without universal parity | Remains: occupied target, direction, cancel, available poschodia and reverse prechody. |
| HP, death and restore | Fire time classify | Remains: all other writes HP, concurrency damage and restart/load. |
| Inventory and pickup | Without new complete uzavretia | Remains: limity, prenos between level and version exception. |
| GUARD arrays | Time domain timerov spresnená | Remains static: each class verify and readable/write increase bytes. |
| GUARD AI | Slow update separate from render | Remains: complete state × strategy × class × timer × animation × sound graf. |
| Percepcia/sluch | Not consider render for AI tick | Remains: LOS/FOV rohy and activation wake group during exact map condition. |
| Boss/transform | Without new complete auditu | Remains: Dracula/bat, Cannon, Dancers, final branches and all versions. |
| weapon kadencia | Counter 01FA and prahy have correct jednotku | Remains: animation automatic weapons, first shot, change weapons, ammo/pool concurrency. |
| Damage and hitscan | Render precede inputu v verify branch | Runtime: same status, rôzna field/rotation v jednom frame; all classes/difficulty level. |
| Projectiles | Pool update after render, before inputom | Remains: embedded fields, +0D, DDA scale, all terminate and mimoobrazové hits. |
| Projection cache | Order closed, condition writer supported | Runtime: watch OBJECT+18 and damage for object omitted v last projekcii. |
| Fire/hazardy | 100/10/2 for slow step, nie for render frame | Remains: all contact classes, ochrana, concurrency and mode prechody. |
| Special walls | Previous 1.10 findings preserved | Remains staticky: ONE_SHOT, SPECIAL1 and completion parity 1.3/1.6/1.8. |
| Level triggery | Exact data difference E1M5 | Remains: all episodes, one-shot flags, cancel and save/load during eventu. |
| IMG/SEQDEF | IMG.1 identical v shareware trojici | Remains: each runtime choice facing/state/alternate and exact link on other build/episodes. |
| VEC geometria | Caller order preserved | Remains: flags, invalidation, list lifetime and dynamic-map parity in all build. |
| Projection/clipping | Cache writer has condition | Remains: near-plane, round, equality/tie and verify. |
| wall pixely | Nezameniteľné tempo render | Remains: bit exact sampler and original framebuffer comparison. |
| Sprity | Slotová prevent affects cache | Remains: all overlap, limity slotov and pixel okraje. |
| Palette/shade | GAME.PAL available; 1.10 change API proven | Runtime: WinG/DisplayDib, RC_PALETTE and dark/fade save/load in all mode. |
| HUD/automapa | Slow and frame callsite-y distinguish | Remains: each dirty flag, color, portrait and spotreba power-upov. |
| SFX and MIDI | Assety identical; 1.8 restores volume | Remains: event priority/verify, failure device and original audio comparison. |
| USER.SAV | V exportoch four versions sa vyskytuje sentinel 0xD6E7 | Same length is not enough: remains rebasing, individual arrays, cross-version round-trip and active animations. |
| CONFIG/BSF | BSF are demonstrated different | Remains static: decode semantic differences and link on each EXE. |
| DEMO | DEMO.1 same; nonzero mode has other update branch | Remains: complete automat, timestamp meaning, startup/EOF and real tempo. |
| Postup/score/final | Raw priemer calibration nesmie be substitute with clampom | Remains: all completion branches, ending assety and eventy E2/E3 for other build. |

## 7. Specifically runtime verify

Following test are proposal; **were not performed**. Najprv pair dynamic selector with segment NE given hashu. Save EXE/asset hash, map, player field, direction, mode, time and input. Do not use number NE segment directly as selector v debuggri.

1. **Timing:** v 1.10 track `D70A`, `D974`, `D74A`, `D78C`, DS `0228/022C/0230/0234`, `46B8` and ms clock. During mode 0 and plynulom behu expected approximately 8 slow update-ov/with; during row interrupt verify, that nevznikne catch-up series.
2. **Calibration:** breakpoint after `D863` and after `D89B`; save `53F2`, locally D and `53F4..53FA`. Distinguish raw time and value with minimom 40. For other versions use table above.
3. **Cache damage:** `CC7C` during write OBJECT+18, subsequently projectile collision/damage `9B64/80F8/9FA2`. compare object visible, for okrajom and after fast otočení; record last generation write.
4. **Palette 1.8 vs 1.10:** change jednej nonzero index colors v same state; during `32B2/3360` record index, odoslaný RGBQUAD and framebuffer total with palette. Repeat for `RC_PALETTE` branches.
5. **Sound 1.6 vs 1.8:** original volume → change v hre → row termination; log get/set return distinguish support device from code restore.
6. **E1M5 data:** compare whole (26,34)/(26,35) from nuly v same package; target is confirm visible object 0xD8 and consequences move, nie search change AI v EXE.

## 8. implement usage results

- Introduce build profil according to hashu. Separate EXE identitu from identical/different assetov.
- Preserve two bucket counters and difference mode 0 / nonzero branch; does not add catch-up loop to compatibility mode without labels change behavior.
- Retain raw priemer render measure separate from local effect values and derive krokov.
- Neodvodzovať GUARD, fire hazard and counter 01FA z current FPS.
- Preserve order projection/render → movement door/projectile → presentation → input, if sa reconstruct this original frame branch.
- For 1.10 distinguish palette branches and correct `RGBQUAD[index]` pointer. Older behavior neopravovať potichu during claim exact emulation older versions.
- During 1.8/1.10 restore successful load original hlasitosti during corresponding cleanup.
- During data compatibility not consider same size MAP for identical content. Preserve version move D8.
- Palette z provided GAME.PAL load as PCX palette; interpretation file as first 768 RGB bytes is incorrect.
- Unknown CLASS verify, all animation alternates and cache freshness remain `TBD`.

## 9. Overenie, files and confidence

Performed: hashovanie EXE/exportov/assetov; NE segment and relocations; complete parse 3 856 `FUN_*` tiel; selected C/ASM check; byte anchors for 8 Hz, calibration and tables v each EXE; exact MAP diff; independent PCX decode. Arithmetic example v `verification.json` are model obtain z instructions, nie records behu Nitemare3D.

evidence ZIP contains registers CSV, `ne_metadata.json`, exact clip for each build, extracted palette, valid output and reproduction skripty. Full original game sa to result znovu do not bundle. During reproduction use original input listed v inventory; detailed postup is v README.

Overall confidence: **High for listed priame byte/data findings; Medium for interpretation visible consequence without behu; Unknown for open areas.** Overall percent completion sa this auditom nevypočítava. Precede match functions, automatic covered and runtime confirmation are three different metriky.

Underlying kontinuity: current load `Nitemare3D_Reverse_Engineering_Master_Reference_2026-09-23.md`, `Nitemare3D_deep_unknowns_2026-09-23.md`, `Nite3W_GUARD_audit_2026-09-23.md` and `Nite3W_function_checklist_unknowns_audit_2026-09-23.md`. New conclusions above were subsequently check proti primary EXE and dátam, nie adopted only z these text.