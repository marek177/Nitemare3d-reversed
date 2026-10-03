# NITE3W 1.10 — priamy binary audit Menu/HUD

**Date:** 25. 9. 2026. **Range:** two files provided v this rozhovore; static analysis EXE, rozbalenie data, check image dekodérov and test odvodených modelov.

## Conclusion

Directly z bytes are teraz supported main HUD dispatcher, 26 vetiev its switch, 38 initialize image descriptorov, exact selection 11 zdravotných portrétových slotov, signed/unsigned difference between druhmi ammo, update coordinates, right panel automapy and three variant interného main menu. separate is vyčítané natívne Windows menu and links its commands on MFC obsluhy.

**Original game was not run.** Confirmed static operations are not measure behavior Windows 3.x, pixel match celej game nor complete auditom all functions menu. New names functions are analytické names, nie restore original symbol autora.

## 1. Identita and evidence

| File | Size | SHA-256 |
|---|---:|---|
| nite3w(20260925-063336).exe | 230400 B | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |
| uif(5).dat | 527595 B | `d1d5a1f59283530ee025c6a95d3cc6300854929213dbd9fed881a696688a8a4d` |

EXE sa hashom match with referenciou NITE3W Win16 1.10. Is NE file with desiatimi segment. Addresses `3:A3B6` v this dokumente mean **poradové number NE segment and offset**, nie load selector. `DS:` denotes offset v automatickom dátovom segment 10.

Code segmentu 3 starts v file on `0x15FC0`, segment 4 on `0x25260`, segment 7 on `0x2A9C0`, segment 10 on `0x2C040`. For example file offset functions `3:A3B6` is `0x20376`.

Relocation strings were rozbalené on **6082 miest**. For example raw `CALL BA63:A3B6` on `3:BA56` is not call to actual segment BA63. Word contains prepojovací data item relocations; target is `3:A3B6`. V priloženom `annotated_core.asm` is to explicitly marked as `RESOLVED_CALL`.

Table source contains **54 items**: 19 string-table, 12 group-cursor, 12 cursor, 5 dialog and after jednej menu, accelerator, version, bitmap, icon and group-icon. Zero older array headers is not evidence prázdnej tables source. This finding opravuje older tvrdenie o neprítomnosti source.

evidence files v ZIP: `input_manifest.json`, `ne_resources.json`, `annotated_core.asm`, `binary_anchor_results.json`. Inline skokové tables are zapísané as data `.word`, nie as falošné instructions.

## 2. What actually contains UIF.DAT

Directory forms 32 records after 6 B: `uint16 length`, `uint32 absoluteOffset`, little endian. First payload starts on `0xC0 = 192 = 32 × 6`. Sloty 0–16 are obsadené; 17–31 are completely zero. Payload 16 ends exactly on EOF.

| Slot | Meaning | Type |
|---:|---|---|
| 0–2 | Three bitmapové fonty; their load is supported z EXE | Own binary format |
| 3 | Titulný image | PCX 320 × 200 |
| 4 | Please Wait | PCX 320 × 200 |
| 5 | Game rám and pozadie HUD | PCX 320 × 200 |
| 6 | Main Menu | PCX 320 × 200 |
| 7 | Choose an Episode | PCX 320 × 200 |
| 8 | Select Difficulty Level | PCX 320 × 200 |
| 9 | Config Screen | PCX 320 × 200 |
| 10 | Config Screen with nápovedou k switch and posuvníku | PCX 320 × 200 |
| 11 | Select Cheat Modes | PCX 320 × 200 |
| 12 | Load and File | PCX 320 × 200 |
| 13 | Save and File | PCX 320 × 200 |
| 14 | Level Completed | PCX 320 × 200 |
| 15 | Order Now | PCX 320 × 200 |
| 16 | Pozadie prehliadača návodu | PCX 320 × 200 |
| 17–31 | Empty rezervované sloty | None payload |

All 14 PCX was decoded. Priložené PNG are náhľady original images with their store palette; **are not to frames run game**. Image Level Completed already contains static tvár as part pozadia; to is not evidence, that z UIF pochádza meniaca sa zdravotná sada HUD portrétov.

Fontový selection `4:018A` uses number fontu and through `3:5F12` loads corresponding raw UIF slot. Destinačné blocks v segment 7 have kapacitu `0x4B0` on font. Subsequently sa zostavuje table 128 glyph pointer; input metriky are part of own fontových data. Image loader `3:5D72` uses PCX branch.

**Correction working hypotézy:** numeric arrays HUD sa format on text and draw bitmapovým fontom. Is not needed predpokladať separate UIF image each number for each pointer.

### Skúška starého and proposed load on real file

Original `DatArchive::load()` returns 17 items, because ends during descriptor-e, whose payload siaha on EOF. Proposal `loadFixedDirectory(path,32)` preserves all 32 items, including 15 prázdnych. **Nor original load nestratil none from 14 obsadených PCX images.** Difference is v zachovaní identity prázdnych slotov, nie v počte úspešne load images.

Oba C++ dekodéry poskytli for each PCX exactly same 64000 index colors and 768 bytes palette as independent dekodér Pillow. Result: 14/14 matches for original and 14/14 for proposed dekodér.

## 3. Main HUD dispatcher and obnovovanie

**`3:A3B6 → Hud_Dispatch`** accepts numeric operation 0–25. During element usage according to `DS:01F4` initializes 38 descriptorov from `DS:3768`, each after 10 B, through `3:608E`. End areas is `DS:38E4`.

| Operation | Target block | Meaning auditovanej branches |
|---:|---|---|
| 0 | AND42AND | Plná postupná update main fields and rámu |
| 1 | AND92C | Return without work |
| 2 | AND42AND | Predná layer weapons; return before next poľami |
| 3 | AND43B | Episode and level |
| 4 | AND488 | Score |
| 5 | AND4CE | Zdravie, portrét, text HP |
| 6 | AND549 | For separate operation 6 only return |
| 7 | AND54F | Strieborná ammo |
| 8 | AND5AND1 | Laserová ammo |
| 9 | AND5F3 | Ammo prútika |
| 10–11 | AND92C | Return without work |
| 12 | AND648 | Ikona active weapons |
| 13 | AND675 | Keys |
| 14 | AND6DB | Maska kariet |
| 15–17 | AND92C | Return without work |
| 18 | AND721 | Dekoratívna predná layer and condition text |
| 19 | AND787 | Pointer values DS:4C42 |
| 20 | AND847 | Pointer values DS:4C43 |
| 21 | AND8AF | Small state indikátor DS:46AD |
| 22 | AND8E0 | Player coordinates |
| 23–25 | AND7AC / AND7C2 / AND7FA | Operations condition kurzorového prekrytia/pozadia; complete user kontext remains partial |

These addresses are **blocks v jednej function**, nie 26 separate functions. Table has six priamych targets návratu AND92C; operation 6 is next effect no-op. Operations 0 and 2 shared input block, but distinguishes their subsequent condition. Itself existencia calls operations 16/17 therefore v this build does not mean execute osobitného draw.

**`3:BA54 → Hud_DrawFrameForeground`** executes exactly:

```text
Hud_Dispatch(18)
Hud_Dispatch(2)
Hud_Dispatch(24)
return
```

Is not to call complete HUD nor zdravotnej operations 5 v each frame. Zdravie sa update also event: for example `3:8C8D`, `3:BEED`, `3:D03E` call AND3B6 with operation 5 after zodpovedajúcom damage or liečení. Movement update coordinate array up to during change cells.

result model is **jednorazová príprava assetov + event controlled arrays + right predná layer**. To does not close all globally dirty flags, znovukreslenie after prekrytí window nor modes dvoch image strán.

## 4. Zdravie and jedenásť portrétových slotov

On `3:A4CE..A4D9` sa executes unsigned obmedzenie zdravia on 100 and write back to `DS:4C1D`. Following instructions AND4DC..AND4F0 dávajú:

```cpp
health = min_unsigned(health, 100);
portraitSlot = 13 + (health + 9) / 10;
portraitDescriptor = 0x3768 + 10 * portraitSlot;
```

| HP after obmedzení | Slot |
|---|---:|
| 0 | 13 |
| 1–10 | 14 |
| 11–20 | 15 |
| 21–30 | 16 |
| 31–40 | 17 |
| 41–50 | 18 |
| 51–60 | 19 |
| 61–70 | 20 |
| 71–80 | 21 |
| 81–90 | 22 |
| 91–100 | 23 |

Portrétová draw branch uses x=3, y=162. Is to **11 reach slotov**; without corresponding IMG cannot confirm, whether are all visually different, nor their exact rozmery. V this branch is not doložená osobitná choice temporary bolestivého portrétu. Finding nevylučuje additional prepísanie image inde.

HP text uses format `%d%%`. Keďže routine zdravotný byte also changes, nahradenie výlučne read-only draw by vynechalo part original behavior. Move clampovania to modernej simulácie must be vedomé rozhodnutie with check poradia.

## 5. Ammo, score, text arrays

### Signed pasca v dvoch druhoch ammo

Strieborná branch AND54F and laserová AND5AND1 have `CMP AL,100; JLE; ...; CBW`. JLE is signed comparison, CBW znamienkovo rozširuje byte. Prútik AND5F3 uses unsigned clamp as HP.

| Raw byte | Silver/laser: stored → format | Prútik: stored → format |
|---|---|---|
| 0–100 | original → 0–100 | original → 0–100 |
| 101–127 | 100 → 100 | 100 → 100 |
| 128–255 | original → −128 up to −1 | 100 → 100 |

Example `0xFF`: silver/laser branch uchová 255 and format `-1`, prútik stores also format 100. Is static consequence during zadaní takého byte; **nie o tvrdenie, that ho normal game prirodzene reach**. During portovaní needs to separate verný model this branches from úmyselnej opravy hraničných values.

### Score and format

AND488 vkladá on zásobník DWORD z DS:4C16 and uses `%lu`: HUD reads **32-bit unsigned score**, nielen spodné word. V this audite sa thereby does not close behavior all producentov score during pretečení.

Text function `4:0374` sets font, clear array, zistí width text and draw ho zarovnaný doprava; are visible calls for two image stránky. Základné argumenty fields:

| Array | x | y | Width array | Format |
|---|---:|---:|---:|---|
| Episode : level | 50 | 171 | 31 | `%d : %d` |
| Score | 50 | 191 | 31 | `%lu` |
| HP | 7 | 192 | 10 | `%d%%` |
| Silver | 109 | 164 | 20 | `%d` |
| Laser | 109 | 177 | 20 | `%d` |
| Wand | 109 | 190 | 20 | `%d` |
| coordinate | 140 | 192 | 19 | `%d,%d` |

Table states **argumenty text fields**, nie width konečných string whether all their glyphov. During príliš long number can zarovnanie zasiahnuť mimo očakávaného array; takýto image was not runtime odmeraný. Episode is DS:7E52, level is DS:7E54+1.

## 6. coordinate: exact prevod and when sa changes HUD

`3:8A20` contains commit position. On `8A4D/8A51` writes svetové X/Y to DS:4BF6/4BF8. Then executes **SAR o 6 bitov** and results compares with DS:4BF2/4BF4.

```text
cellX = arithmetic_shift_right(int16(worldX), 6)
cellY = arithmetic_shift_right(int16(worldY), 6)
pri zmene bunky:
    DS:4BF2 = cellX
    DS:4BF4 = cellY
    Hud_Dispatch(22)
```

Branch AND8E0 reads already these cell values, nie directly world coordinates, and format their as **X,Y without +1**. Separate operation 22 is condition DS:46B4==1; during complete operation 0 is osobitná výnimka. So is field, nie time. For normálne nezáporné coordinate is prevod divide 64; for negatívne values needs to preserve signed arithmetic posun, nie C++ divide with zaokrúhlením k nule.

## 7. Right panel: priamy evidence automapy

**`3:B1A4 → Automap_Dispatch`** has ten vetiev. Returns far pointer `6:0000`, where is 4096-byte buffer. Indexovanie is:

```cpp
index = cellX * 64 + cellY; // stĺpcové uloženie; NIE cellY*64+cellX
```

Branch 5 on B274 writes/bliká značkou player, computes start výrezu and calls copy 3:41AND2:

```cpp
originX = clamp(cellX - 31, 0, 2);
originY = clamp(cellY - 18, 0, 28);
source = 6:(originX * 64 + originY);
sourceDimensions = 64,64;
copyDimensions = 62,36;
destination = 256,162;
```

**Right čierny panel is supported as draw area automapy:** x=256..317, y=162..197, therefore 62 × 36 pixel. B24C same obdĺžnik maže. Branch 6 on B304 iterate through guard and zakresľuje condition body after subtract same initial. Prítomnosť call v BBCA viaže draw on corresponding map/detekčné modes.

Finding does not mean, that is automapa always zapnutá or that note all palette index and type značiek. Taktiež is not new image complete map získaný from save file: none save was not v this priechode provided.

Values DS:4C42 and DS:4C43 have separate 18 × 7 pointer on x=233/y=181 and x=211/y=181. Vyplnená width is `floor(min_unsigned(value,100)*18/100)`. Their mode links vedú through flags DS:4C2D/4C2C; named detector/map power is derived z usage. Complete restore mode and their status after save/load still nebolo runtime confirmed.

## 8. Odkiaľ are portréty and ikony

`Hud_Dispatch` nečíta portrétové sloty z UIF address. `3:608E` finds through `3:2398` zodpovedajúci object class **0x3E** and calls `3:5F98`. This loader opens name stored v DS:7E74; konštrukcia name during 3:49AND8 uses `img.` and `%s%d`, therefore `img.N`.

V address IMG sa uses position `(objectId + 0x100)*4`, loads sa offset sequences and skip sa previous image. Each preskakovaný record has 10-byte header and raster width × height. Subsequently sa loads požadovaný subframe.

| Local descriptor slot | Supported usage |
|---|---|
| 0–3 | Ikona according to DS:4C23, on x=135/y=162 |
| 4–7 | Kľúčové bits 1,2,4,8; fixed position (167,162), (189,162), (167,182), (189,182) |
| From 8 | Draw branch kariet; podrobnosť below |
| 10–12 | Dekoratívne parts upper areas |
| 13–23 | Zdravotné portrétové sloty |
| 24 | Descriptor prednej vrstvy weapons |
| Additional | Condition prekrytia/kurzorové zázemie; nie all meaning closed |

**Neobvyklosť kariet:** branch AND6DB iterate eight bitov DS:4C29, descriptor-mi 8–15 and x=211+22×bit. Z toho cannot vyhlásiť eight normálnych kartových type. Above bits zasiahnu also sloty use inde and potenciálne areas mimo očakávaného panel; legálny range mask needs to spárovať with OBJECTS and producentmi mask. V this audite sa also values during game nevyskytli, because game nebežala.

Separate reader DS:4C45 for pentagramy v auditovanom main dispatcheri supported was not. Older predpokladané assign pentagramovej mask ku specific mriežke HUD therefore remains open. Is not evidence, that daná mask whether its display neexistuje inde.

On complete assign visual mien, farieb and rozmerov are needed **IMG.1 and OBJECTS.1 z same inštalácie**, case corresponding dvojice next episode.

## 9. Interné main menu: three variant

Vyčítané records menu v segment 7 have stride **18 B**. Supported are action byte +0, selection byte +4, x/y +10/+12 and far pointer text +14. Other arrays sa tu nepovažujú for completely named.

| Table | Count | Items v order |
|---|---:|---|
| 7:0FAA | 6 | New game; Configure game…; Load game…; Instructions; Demo; Quit |
| 7:1028 | 7 | New game; Configure game…; Load game…; Save game…; Instructions; Return to game; Quit |
| 7:10B8 | 7 | New game; Configure game…; Load game…; Save game…; Instructions; Restart at last save; Quit |

`4:2370 → Ui_SelectMainMenuVariant` najskôr restores selection byte v dvoch sedempoložkových table according to action 11. Then selects basic variant according to aktivity game and DS:46B4. Restart variant sa selects during **state==3**, nezápornom save slote, successful result 3:5388 and match episodes also level store record with current state. During match is prítomné also call 3:574C; all its vedľajšie effects this audit does not close.

Therefore is not exact tvrdiť „after each smrti sa displays restart“. Code has specific status, check save and its matches. Súčasné dvojstavové `mainMenu(bool gameActive)` z previous repository reportu this tretiu branch samo nevie reprezentovať.

## 10. Natívne Windows menu and map message

V EXE existuje also separate natívne menu **resource type 4, ID 2**, on file offset `0x34F40`, allocate length 192 B. Has four skupiny Game, View, Window, Help and nine final commands.

| Command | ID | Execute function | Update selection items |
|---|---|---|---|
| Size x1 | 0x8003 | 3:0AND94 | 3:0AF8 |
| Size x2 | 0x8004 | 3:0AA2 | 3:0B22 |
| Size x3 | 0x8017 | 3:0AB0 | 3:0B4C |
| DOS Mode | 0x8005 | 3:0AND6E | V this table is not assign same trojica size-update vetiev |
| Instructions | 0xE145 | 3:0AE2 | — |

Message map during 1:02AND0 uses 10-byte records. Execute commands have v this MFC table message 0 and signature 10; update obsluhy message 0xFFFF and signature 35. Update branches for size compare dvojice 320×200, 640×400 and 960×600 and call virtuálnu update items. Execute branches call 3:2D9C with argumentmi 0/1/2. These two role sa must not zameniť.

Accelerator resource type 9, ID 2, file `0x35200`, contains 18 päťbajtových records plus zarovnanie. **Alt+Enter has ID 0x8016**, so far what menu DOS Mode has **0x8005**. Alt+Enter ide through 3:0AEA to input branches 3:8CD2; kliknutie menu DOS Mode ide through 3:0AND6E, confirmation dialog and other call path. Complete ekvivalencia oboch ciest sa this static čiastkovým auditom nevyhlasuje.

Prítomnosť akcelerátora still nedokazuje, that each its generický frameworkový command is v hre functional use. Commands, status zaškrtnutia, popisy, key skratky and game menu needs to viesť as different layer.

## 11. Pomenovanie functions and hranice

Strojovo čitateľný file `function_names.csv` contains proposal mien with distinguish function/block. Zásadné functions:

- 3:AND3B6 — Hud_Dispatch
- 3:BA54 — Hud_DrawFrameForeground
- 3:B1AND4 — Automap_Dispatch
- 3:608E — Hud_LoadClass3EFrame
- 3:5F98 — Img_LoadIndexedFrame
- 3:5F12 — Uif_ReadRawEntry
- 3:5D72 — Uif_LoadPcxScreen
- 4:018AND — Ui_SelectBitmapFont
- 4:0374 — Ui_DrawRightAlignedTextField
- 4:2370 — Ui_SelectMainMenuVariant

AND4CE, AND54F, AND5AND1, AND5F3, AND8E0 and B274 are v this audite named **blocks**, nie novoobjavené separate functions. Automatické premenovanie generických FUN symbol without check boundaries sa therefore neodporúča.

## 12. What was actually performed

| verify | Result | What result mean |
|---|---|---|
| Byte/relocation/data check provided file | 59/59 | Including 32 separate check range UIF slotov; is not 59 analyzovaných functions |
| PCX decode original C++ load | 14/14 | All obsadené image items úspešne load |
| PCX decode proposed C++ load | 14/14 | Same image; moreover preserved empty sloty address |
| Comparison with Pillow | 28/28 exact matches | 14 image × two dekodéry; compare sa index pixel and palette |
| C++ modelové test | 19/19 skupín | Derived vzorce/rozhodnutia; nie emulácia original procesora |
| CMake/CTest | 3/3 run test | Modelový test + obe real UIF skúšky |
| Spustenie NITE3W in Windows | 0 | Nebolo performed |

Modelové test zahŕňajú all 256 values zdravotného and muničného byte, all 65536 bit vzorov signed coordinate and 4096 normal field v map. Modely are not complete render, nenahrádzajú save I/O and samy osebe nezvyšujú runtime pokrytie. Their target is capture specifically already supported rules and chrániť their before incorrect portovaním.

## 13. What remains open

Najbližší missing data input is corresponding IMG + OBJECTS: recognize farieb kľúčov/kariet, all portrétov, rozmerov, animation and výrezov. Further remains check complete input menu (mouse, repeated key, focus), complete životný cyklus dialog, all operations prekrytia, exact meaning markerov automapy, restore HUD after change window and after save/load, finálna palette and pixel match in all display mode.

**Without menovateľa all relevantných functions, vetiev and runtime scenarios sa nevytvára new overall percento hotovosti.** Pokrok is specific: old question during main dispatcheri, zdravotnej table, automape, coordinate and treťom menu have teraz address static evidence.

## Reprodukcia and content package

`README.md` v ZIP contains commands CMake, Python and opis depend. Original EXE, UIF and fontové payloady are not to package skopírované. Náhľady PCX are decode z use provided file. Selected kódové výrezy and derived modely slúžia on audit; is not original source codes game nor o its run port. To GitHubu sa this priechodom nič nezapísalo.