# NITE3W — cielený audit four areas HUD

Date: 25. september 2026  
Repository skontrolovaný v this kroku: `marek177/Nitemare3d-reversed`  
Reference commit: `9d485e82a84ef1241eff7165c390c82eaff47970`

## Range and origin evidence

**WITH — directly skontrolovaný source:** current `docs/HUD_UI_RE.md`, `docs/DATA_MANIFEST.md` and C++ files `DatArchive.cpp/.hpp`, `BinaryIO.cpp/.hpp` load through GitHub. Four locally copies C++ file have identical Git blob SHA-1 as load files. On nich was skompilovaný and running test program.

**H — prevzatý historical finding:** podrobnosti restore from record previous rozhovoru k output `NITE3W_Menu_HUD_BINARNY_rozbor_2026-09-25.md` (message 25. 9. 2026, 06:58:16 UTC). Entire original artefakt nor original `nite3w(20260925-063336).exe` and `uif(5).dat` were not v this kroku znovu load. Addresses and original binary interpretácie therefore are not novým independent auditom instructions.

**M — new modelový consequence/test:** math test restore vzorcov, synthetic DAT and skúšky missing, which by mohol zaviesť nesprávny port. Is not beh original game nor evidence, that listed errors existujú v súčasnom porte.

**E — primary external source:** oficiálna stránka Gray Design Associates explicitly opisuje automatickú map napájanú magic eyes. Nepotvrdzuje however addresses functions, specifically switches nor pixely.

Original report on GitHube is still označený dátumom 22. 9. 2026. Its odhady `<50 %`, `50–70 %` and `60–70 %` nepredstavujú measure pokrytie. New overall percento this auditom nevzniká.

## 1. Strategy prekresľovania HUD

### Prevzaté binary body (H)

| Miesto | Working meaning |
|---|---|
| `3:A3B6` | Centrálny HUD dispatcher, operations 0–25. |
| `3:BA54` | V zaznamenanej ceste calls HUD operations 18, 2, 24. |
| `3:A4CE` | Block HP, saturácie HP and selection portrétu; operation 5. |
| `3:A54F`, `3:A5A1`, `3:A5F3` | Blocks troch muničných pointer; operations 7, 8, 9. |
| `3:A648` | Block weapons; operation 12. |
| `3:A675`, `3:A6DB` | Blocks kľúčov and kariet; operations 13 and 14. |
| `3:A8E0` | Block map coordinates; operation 22 = 0x16. |

Numbers operations without prefixu `0x` are desiatkové. `A4CE` and podobné addresses označujú blocks in vnútri dispatchera, nie automaticky separate functions. Names are not original symbol autora.

Previous analysis opisuje operation 0 as postupnú/complete update main fields. Operations 0 and 2 have shared input `A42A`; without check their next toku sa must not stotožniť. Operation 18 direction on prednú/dekoratívnu layer and condition text. Operations 19/20 are small pointer spojené with `4C42/4C43`. Operation 24 zostala v restore record without semantic opisu.

movement analysis states update coordinate array during change cells and prevod `world >> 6`. Change HP and next values has event calls HUD.

### What possible close and what nie (analysis H)

HUD has separate address update branches; nejde only o jedinú nedeliteľnú draw function. V zaznamenanej routine `BA54` is not priame call operations 0 nor 5.

**To still nedokazuje, that entire HUD nikdy is not prekreslený v each frame.** Unknown operation 24, indirect calls and branches operations 2 can result change. same is not dokázaná specific implement dirty flags or cache predchádzajúcich values. Prenos already hotového framebufferu to window is iná question than new zostavenie all HUD elements.

Najmenšia open static role is therefore exact telo operations 24, comparison tokov 0/2 and complete list call operations 0. On behavior during restore window, menu or change display mode so far missing complete evidence.

### New consequence for optimalizáciu (M)

Zdravotná branch according to historical rozboru does not change only pixely: writes saturované HP back to game state. Optimalizácia „display value sa nezmení, entire call vynechám“ therefore can change game logic.

Test protipríklad: posledné display HP = 100; after liečení is raw HP = 120. Comparison `min(120,100) == 100` síce hovorí, that number netreba meniť, but vynechaním celej branches by HP ostalo 120. Correct model skončí on 100.

During exact porte needs to preserve normalizačný vedľajší effect and its order; possible vynechávanie draw is separate operation. Test nepreukazuje existenciu this errors v current porte.

## 2. Right čierny panel

### Prevzatá identify (H) and externé confirmation (E)

Previous analysis assign right panel automape through `3:B1A4`, nie only according to vzhľadu. States buffer `6:0000`, 4096 bytes, rozmery 64 × 64, výrez 62 × 36 and target `(256,162)` up to `(317,197)` including okrajových pixel. Zaznamenáva mazanie, blikajúcu player značku and condition body z guard.

Operation 2 has vymazať 4096-byte buffer. Operation 8 is v movement rozbore spojená with vymazaním starej značky, with prístupom through segment stored on `222C` and index `playerTileX*64 + playerTileY`. Zaznamenané order ju umiestňuje before commit novej player field.

Oficiálny opis autora confirms existenciu automatickej map napájanej magic eyes. Itself osebe however is not enough on určenie, which exact branch spôsobí čierny panel v specific okamihu.

### Math model and new check (M)

```text
automapIndex = cellX * 64 + cellY
mainMapCellIndex = cellY * 64 + cellX
mainMapByteOffset = 2 * mainMapCellIndex

originX = clamp(cellX - 31, 0, 2)
originY = clamp(cellY - 18, 0, 28)
localPlayerX = cellX - originX
localPlayerY = cellY - originY
```

All 4096 dvojíc coordinates prešlo check range buffera, jedinečnosti index, výrezu and player značky. V modeli is posun výrezu v osi X only 0–2, so far what v osi Y is 0–28. Is to consequence width 62 z overall 64 buniek; this conclusion predpokladá correct historical zapísaných vzorcov.

For `(3,36)`:

| Veličina | Result |
|---|---:|
| byte index automapy | 228 = 0x00E4 |
| Index cells hlavnej mapy | 2307 = 0x0903 |
| Relatívny byte offset main map | 4614 = 0x1206 |
| Origin výrezu | (0,18) |
| Player v local výreze | (3,18) |
| Player on obrazovke according to modelu | (259,180) |

Zámena `x*64+y` for `y*64+x` changes index v 4032 cell. On 64 diagonálnych cell `x==y` sa neprejaví. Test only after diagonále therefore nemôže odhaliť transpozíciu map.

### Remains open

Exact aktivačné switches, spotreba map energie, condition vykreslenia guard, colors and kategórie buniek, perióda blikania and pixel order individual vrstiev. identify panel and complete reconstruction its behavior are two different level poznania.

## 3. UIF.DAT and priradenie grafiky

### Distinguish numeric priestorov (H)

Restore inventory states 32 address slotov, 17 obsadených (0–16), 15 prázdnych (17–31), three fontové blocks and 14 PCX image 320 × 200. Older inventory assign archívny slot 5 pozadiu/rámu HUD. Meniteľné portréty and ikony however last binary analysis direction through IMG; during portrétoch states object class `0x3E`.

| identify | Is not totožný with |
|---|---|
| Slot address UIF.DAT | Runtime slotom spritu HUD. |
| Runtime portrét 13–23 | file item UIF 13–23. |
| Class object `0x3E` | Number items UIF or priamym index PCX. |
| Count 38 runtime descriptorov uvádzaný v rozbore | Počtom 38 UIF items. |

Itself selection runtime slotov 17–23 by during nesprávnej priamej interpretácii directional on seven prázdnych UIF items. To ukazuje nesúlad takej interpretácie with restore inventory; is not to new verify IMG pixel.

Complete mapovanie must separate strings:

```text
UIF archívny slot -> dekóder -> obrazovka/font -> cieľové pixely
OBJECTS trieda/variant -> IMG záznam/sekvencia -> runtime slot -> HUD blit
```

Exact IMG index all zbraní, kariet, kľúčov and portrétov nor specifically links number on fontové glyphy are not v this audite closed.

### Directly reprodukovaná property current C++ parsera (WITH + M)

`DatArchive::load()` terminate read, when `offset + length == bytes.size()`. Neberie parameter fixed kapacity 32 slotov. increase zero records address after poslednej dátovej item tak to `entries()` nevloží.

On exact, hashom verify copy four source file was skompilovaný C++20 test with `-Wall -Wextra -Werror`. Synthetic file small 32 šesťbajtových slotov, 17 nonzero items and first payload on 192.

| Meranie | Result |
|---|---:|
| Capacity synthetic address | 32 |
| Obsadené items synthetic address | 17 |
| `entries().size()` | 17 |
| `headerBytesUsed()` | 102 = 0x66 |
| `firstPayloadOffset()` | 192 = 0xC0 |
| Neexponovaný increase address | 90 B = 15 × 6 B |
| Return code kompilácie | 0 |
| Return code test | 0 |

**Is not to evidence posunutia index 0–16 or straty their payloadov.** Test skontroloval also correctly order and content all 17 items. Is to difference between interface load use items and inventory fixed address.

Priložená function `audit_fixed_dat_directory(data, slot_count)` preserves also empty sloty and checks boundary. Requires, aby sa capacity určila independent. Does not have sa without evidence set 32 for each DAT archív, especially nie automaticky for SND.DAT.

## 4. Logic portrétu player

### Prevzatý vzorec (H)

V bloku `3:A4CE..A4F0`:

```text
health = min_unsigned(health, 100)
write_health_back(health)
portraitSlot = 13 + (health + 9) / 10
```

Divide is celočíselné. Historical analysis states target portrétu `(3,162)`.

| HP after saturácii | Runtime slot |
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

Vzorec has 11 reach selection. To nepreukazuje 11 visually difference bitmapových obsahov. HP=0 has own selection, but independent pain/god/cheat prekrytie or other write portrétu thereby are not vylúčené.

### New modelové check (M)

Test was 256 nezáporných input 0–255. This range nepredstavuje new určenie bitovej width original HP array.

For each input sa check result range 0–100, range slotov 13–23, členstvo v independent zadanom HP intervale and idempotencia normalizácie. All check passed.

Nesprávna náhrada `13 + hp/10` sa differs during 90 from 101 valid HP values. Remove saturácie by during input HP=119 vybralo slot 25 namiesto slotu 23. HP 100 and 91 have ten certain portrét 23, but different number; HP 90 already prejde on portrét 22. Cache založená only on portrétnom slote therefore nesmie rozhodovať also o update number HP.

## 5. Result and remain boundary

| Area | Vecný posun | Still unclosed |
|---|---|---|
| Prekresľovanie | Separate operations and event branches; named rizikový vedľajší effect HP update. | Operation 24, complete toky 0/2, call full update, restore window. |
| Right panel | Zachovaná older binary identify automapy; formálne verify index and boundary restore modelu. | Switches, energia, colors, guard condition, pixel match. |
| UIF map | Separate archívne/runtime/IMG identify; directly reproduced behavior súčasného parsera. | Complete IMG/OBJECTS assign and glyphové links. |
| Portrét | Exact intervalová table odvodená from zaznamenaného vzorca and test. | Visual jedinečnosť bitmap, next write and osobitné state. |

New test were not run NITE3W and nemenia percento runtime verify original. GitHub was not this krokom change.

## 6. Reprodukcia

Modely and fixed auditný directory:

```sh
python hud_models_and_tests.py
```

C++ probe (z koreňa evidence package, with available C++20 kompilátorom):

```sh
g++ -std=c++20 -O2 -Wall -Wextra -Werror -I source_snapshot dat_archive_probe.cpp source_snapshot/formats/DatArchive.cpp source_snapshot/formats/BinaryIO.cpp -o dat_archive_probe
./dat_archive_probe synthetic_32_slots_17_payloads.dat
```

`build_evidence.py` znovu creates hashom check source files and synthetic input and runs same C++ test. Provided test file is not original UIF.DAT. Kompilácia v this kroku was for Linux; is not publikovanú Windows aplikáciu.

## Zdroje

1. current report HUD, date v dokumente 22. 9. 2026: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/docs/HUD_UI_RE.md
2. current parser: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/DatArchive.cpp
3. API parsera: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/DatArchive.hpp
4. Binary read: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/BinaryIO.cpp
5. Header binary read: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/formats/BinaryIO.hpp
6. Oficiálny opis autora: https://www.dgray.com/n3dpage.htm
7. Historical binary analysis: name `NITE3W_Menu_HUD_BINARNY_rozbor_2026-09-25.md`, restore informácie z previous rozhovoru, nie znovu load entire file.
8. New reprodukovateľné results: `dat_archive_probe_results.json`, `model_test_results.json`, source test and synthetic input v priloženom package.