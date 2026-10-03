# Nite3W 1.10 – reconstruction hide object functions 1010:1296–14AND8

Analyzovaný image: `nite3w(10).exe`, Win16 NE, segment 1010. Conclusions are derived z dátových structure, call and repeated usage; is not premenovanie according to itself addresses.

## Zrekonštruované functions

| Address | Rekonštruovaný name | Role | Confidence |
|---|---|---|---|
| `1296` | `FindDoorLinkControllerByCellPointer(cell)` | Prehľadá primary radiče on `DS:9DD6` after `0x16` byte. Compares far pointer cells on `+0x08/+0x0A` with pointer call; is not dvojicu svetových coordinates. During nenájdení calls `0xD90`. | high |
| `12E8` | `FindClass3MotionControllerByCellPointer(cell)` | Finds v separate field on `DS:A356` record, whose far pointer map cells is on `+0x10/+0x12`. Array has other layout than radiče from `9DD6`; uses ho branch object classes `3`. | high |
| `133A` | `FindPushableSlotByMapCellPointer(cell)` | Prehľadáva 6-byte sloty on `DS:A616`; first word is index 28-byte entity. Compares far pointer map cells entity on `+0x6D72/+0x6D74` with offset and segment from call; is not coordinate. During nenájdení calls `0xDA0`. | high |
| `1394` | `FindNearestVisibleDoorLinkController(actor)` | iterate through `DS:9DD6` radiče, compares Manhattanovu distance v map cell k target `+0x10/+0x12` and test LOS through `FUN_1010_D50A`. Returns najbližší visible door/spárovaný target, nie ľubovoľný map object. | high |
| `1476` | `DoorLinkStateAllowsPassage(controller)` | Returns TRUE, if `controller+0x0C` is `0` or `4`. Kolízna branch `FUN_1010_700A` this predikciu uses on rozhodnutie, whether through radič possible process. Meaning state `4` and its normal write remain open. | high for comparison bytes; medium for name |
| `1492` | `DoorLinkStateIsClosed(controller)` | Returns TRUE only during `controller+0x0C == 1`. Calls sa total with `1476` nad radičom find through `FUN_1010_1296`; is not test classes projectile. | high |
| `14A8` | `Build()` | After load level prejde map `64×64`. For wall property bit `0x08` creates up to 64 records, finds two 28-byte dynamic wall objects v cell, stores their far pointer and initializes controller state `1`; bit `0x20` sa zosúladí with orientation oboch time. | high |
| `21B6` | `StartPushableObjectMotion(object_cell, destination_cell)` | USE branch for class `(` finds slot according to far pointer cells object. If slot is not active and target wall-property cell does not have bit `0x02`, stores two bytes vector z player state `+0xA4/+0xAC` and sets read on `8`. | high for static test/writes |
| `2210` | `UpdatePushableObjectMotion()` | Beží v simulačnom update cykle. For active slot computes novú world position and cell; during prechode cell requires `DAT_1048_7F94[cell_object_id] & 0x06 == 0`. Prijatý step move second byte map, update coordinate, sort render index through `FUN_1010_C9A6` and decrements read. Block step read does not change. | high for static tok |

## Important depend

`FUN_1018_09F2` calls after load/reset level v order:

`14A8 → 16D6 → 181C → 7664`.

`14A8` creates primary paired-wall radiče. `12E8` search separate class-3 group-motion radič on `DS:A356`. `1394` selects najbližší visible radič z array `DS:9DD6` for strategy-1 movement; `1476/1492` test its status, nie class object.

## What still is not completely rozhodnuté

Original výklad values `0/1/3/4` as všeobecných type or projectile classes sa ruší: v radiči `DS:9DD6` is values state array `+0x0C`. State `0–3` have popísané prechody below; status `4` is helperom označený as priechodný, but its normal write so far missing.

## Praktický result

This block already possible prepísať to čitateľného C pseudokódu and use during oprave Ghidra symbol. During test needs to verify especially boundary tabuliek (0x16-byte records, max. counts `DAT_1040:0000/0002/0004`) and error path `0xD90/0xDA0`.
## Correction and extension: three different runtime arrays (Win16, 23. 9. 2026)

### Identita and zdroje

Analyzovaný file `nite3w(10).exe` is NE for Windows 3.10. SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` sa match with neskoršou copy `nite3w(20260921-205703).exe`. Third NE segment starts on file offset `0x15FC0`. Raw 16-bit disassembly on `1010:1296`, `1476`, `1492` and `1D4E` confirms stride `0x16`, priame comparison state array and countdown. Archívny export `NITE3W18.EXE(1).c` ukazuje zodpovedajúci tok Win16 1.8 on posunutých address.

### Layout working fields

| Range DS | Size and capacity | Confirmed usage |
|---|---|---|
| `9DD6–A355` | `64 × 0x16 = 0x580` | Primary spárované wall/door radiče. `FUN_1010_14A8` their creates for cells with wall-property bitom `0x08` and searches two 28-byte runtime wall entity. |
| `A356–A615` | `32 × 0x16 = 0x2C0` | Separate group-motion radiče for cells, ktorých second class table returns `3`; `FUN_1010_16D6` save up to four component pointer. Same stride does not mean same layout. |
| `A616–A65D` | `12 × 6 = 0x48` | Index sloty for osobitnú skupinu 28-byte entít with markerom `'('`; `FUN_1010_181C` and `FUN_1010_133A` their pripravujú and search. Meaning movement operations remains partial. |
| `A65E–A69D` | `64` bytes | Guard-wake cache, separate reset and process `FUN_1010_7664`. |
| `A69E–C69D` | `64×64×2 = 0x2000` bytes | Dvojbajtové map cells. |

verify check v build function confirm kapacity `0x40`, `0x20` and `0x0C`. Primary array sa save to USER.SAV v range `0x580` bytes.

### Confirmed state and time model array `DS:9DD6`

| Status v `+0x0C` | Confirmed meaning v toku code |
|---:|---|
| `0` | Open, priechodný status; beží auto-close countdown. |
| `1` | Initial and completion close status; `FUN_1010_1492` ho test directly. |
| `2` | Otvárací movement; `FUN_1010_1E00` moves obe parts after `2` interných units on update and after reach target sets `0`. |
| `3` | Zatvárací movement; that istá routine moves obe parts opačným direction and after reach target sets `1`. |
| `4` | `FUN_1010_1476` ho same as `0` označí for priechodný. Normal writer sa v check lifecycle did not find; nepovažuje sa for confirmed normálny prechod. |

record arrays: `+0/+4` are far pointer on two movement wall entity; `+8` is far pointer map cells; `+0x0C` is controller state; `+0x0E` is open countdown; `+0x10/+0x12` are target coordinate; `+0x14` is action/audio latch use with SFX branch `0x25/0x26`.

Interakčná path `FUN_1010_188A` switches `1/3 → 2` (open) and `0/2 → 3` (close), with provided check orientations during wall znakoch `'='` and `'>'`. During začatí zatvárania sets collision bit on oboch time. After completion open `FUN_1010_1E00` this bit z oboch time clear; completion movement sets `+0x0E=32`.

`FUN_1010_1D4E` odpočítava `+0x0E` only v state `0`. When dôjde on nulu, začne zatvárať only if second byte map cells is `0` and player nestojí v tej cell. Otherwise sets timer on `4` and check zopakuje after four simulation update-och. Wall ID `0x3B` and `0x3C` preskakujú countdown branch. Slovník `WALLS(9).1` their denotes as `Bedroom 3 - Plain` and `Bedroom 3 - Window`; ide only o ID → name koreláciu, nie o evidence, that this file provided runtime own skúmanému EXE.

Kolízna path `FUN_1010_700A` uses oba predikáty `1476/1492` nad controllerom find through `1296`. Function has also special branch for asset ID `0x33–0x3C`, therefore these rules neaplikujem univerzálne on each wall ID.

### Druhé 22-byte array on `DS:A356`

`FUN_1010_16D6` creates maximálne 32 controllerov for object-class `3` cells. Each record contains four component pointer on `+0x00/+0x04/+0x08/+0x0C`, far pointer map cells on `+0x10` and phase word on `+0x14`. Interakcia v `FUN_1010_1A22` sets phase `2` and changes target coordinate connect time; second loop v `FUN_1010_1E00` their moves after dvoch interných units and after reach targets čistí map/kolízne links. Exact asset/frame and original named this animations remain open.

### Static confirmation and runtime boundary

State compare, kapacity, step movement and retry interval are directly v Win16 instruction and match sa with zodpovedajúcimi branch available dekompilačného exportu 1.8. Is static confirmation. Game sa tu nespúšťala v check Win16 environment; exact image, SFX during each hrane and usage nezvyčajného state `4` remain on runtime trace.


### Correction and upresnenie: pushable entity and far-pointer lookup

V callsite in `FUN_1010_1A22` sa to `FUN_1010_21B6` posiela far pointer cells with object `(` also far pointer adjacent target cells. `21B6` posiela first pointer to `133A`. This path dokazuje, that `133A` compares pointer cells stored v entity record-e `+0x6D72/+0x6D74`, nie player coordinates. Name `FindActorMoveSlotAtPosition(x,y)` sa ruší.

`181C` during level setup-e zakladá sloty for entity with byte `+6 == '('` and nuluje their active read. During USE sa movement reject, if slot already pracuje or target wall-property cell has bit `0x02`. Otherwise stores signed-byte komponenty z player state `+0xA4/+0xAC` and sets eight krokov. V `2210` úspešný step update world position also second byte map cells; during prechode cell sa checks mask `0x06` v `DAT_1048_7F94`. `FUN_1010_C9A6` restores render ordering. If is step zablokovaný, position nor read sa nemenia, so code test znova next tick.

`14A8 → 16D6 → 181C → 7664` is level-setup string; `2210` sa calls v simulačnej loop through `d974`. Class `3` on `DS:A356` remains separate group-motion system. Exact units vector pushu, meaning bitov masiek, runtime speed and animation remain open.