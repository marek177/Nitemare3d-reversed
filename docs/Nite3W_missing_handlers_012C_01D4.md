# Nite3W Win16 – restore handlery `1010:012C–01D4`

## Result

V original `nite3w(10).exe` sa between konštruktorom aplikačnej classes and element handlerom recognize Ghidrou nachádza 12 valid functions. Ghidra their nevytvorila as separate functions, therefore v text dekompilácii completely missing. Are not damage: is MFC `ON_COMMAND` adaptéry, which menia command ID z menu/toolbaru on virtuálny key and call shared dispatcher `FUN_1010_8CD2`.

## Exact reconstruction

| Address | Command ID | Resource meaning | Pass VK | Proposed name |
|---|---:|---|---:|---|
| `1010:012C` | `32774 / 0x8006` | weapon 1 – Single Shot Laser | `0x31` (`1`) | `OnSelectWeapon1` |
| `1010:013A` | `32775 / 0x8007` | weapon 2 – Magic Wand | `0x32` (`2`) | `OnSelectWeapon2` |
| `1010:0148` | `32776 / 0x8008` | weapon 3 – Pistol | `0x33` (`3`) | `OnSelectWeapon3` |
| `1010:0156` | `32777 / 0x8009` | weapon 4 – Continuous Laser | `0x34` (`4`) | `OnSelectWeapon4` |
| `1010:0164` | `32785 / 0x8011` | Exit game/menus | `0x1B` (Esc) | `OnExitGameOrMenu` |
| `1010:0172` | `32783 / 0x800F` | Enemy Auto-Mapper | `0x79` (F10) | `OnToggleEnemyAutoMapper` |
| `1010:0180` | `32782 / 0x800E` | Wall Auto-Mapper | `0x78` (F9) | `OnToggleWallAutoMapper` |
| `1010:018E` | `32778 / 0x800A` | Toggle music | `0x71` (F2) | `OnToggleMusic` |
| `1010:019C` | `32781 / 0x800D` | text: Quick Save (F5) | `0x73` (F4) | `OnQuickSave` |
| `1010:01AA` | `32780 / 0x800C` | text: Quick Load (F4) | `0x74` (F5) | `OnQuickLoad` |
| `1010:01B8` | `32779 / 0x800B` | Toggle sound | `0x72` (F3) | `OnToggleSound` |
| `1010:01C6` | `32784 / 0x8010` | Status report | `0x09` (Tab) | `OnStatusReport` |
| `1010:01D4` | `32786 / 0x8012` | Game instructions/help | priame call `FUN_1010_0DAA` | `OnGameInstructions` |

Last line is adjacent trinásta function, ktorú Ghidra síce v strojovom toku nerozdelila correctly, but does not use keyboard dispatcher; opens game help/instructions.

## Confirmed rozpor F4/F5

String resources hovoria:

- `32780`: „(F4) Quick Load last saved game“
- `32781`: „(F5) Quick Save current game“

Strojový code however executes opačné key:

- handler Quick Save `1010:019C` send `VK_F4 (0x73)`;
- handler Quick Load `1010:01AA` send `VK_F5 (0x74)`;
- game frame dispatcher calls during `0x73` function `FUN_1018_22A4`, which uses string `SAVE` on dátovej address `1048:1E5A`;
- during `0x74` calls `FUN_1018_230A`, which uses string `LOAD` on `1048:1E8E`.

Therefore is error/inverziu v text popise original Win16 game: actual behavior binaries is **F4 = save, F5 = load**. Menu commandy rešpektujú actual implement and injektujú prehodené key.

## Rekonštruovaný C++ vzor

```cpp
void CNite3DApp::OnSelectWeapon1()       { DispatchKey(VK_1, 0); }
void CNite3DApp::OnSelectWeapon2()       { DispatchKey(VK_2, 0); }
void CNite3DApp::OnSelectWeapon3()       { DispatchKey(VK_3, 0); }
void CNite3DApp::OnSelectWeapon4()       { DispatchKey(VK_4, 0); }
void CNite3DApp::OnExitGameOrMenu()      { DispatchKey(VK_ESCAPE, 0); }
void CNite3DApp::OnToggleEnemyAutoMap()  { DispatchKey(VK_F10, 0); }
void CNite3DApp::OnToggleWallAutoMap()   { DispatchKey(VK_F9, 0); }
void CNite3DApp::OnToggleMusic()         { DispatchKey(VK_F2, 0); }
void CNite3DApp::OnQuickSave()           { DispatchKey(VK_F4, 0); }
void CNite3DApp::OnQuickLoad()           { DispatchKey(VK_F5, 0); }
void CNite3DApp::OnToggleSound()         { DispatchKey(VK_F3, 0); }
void CNite3DApp::OnStatusReport()        { DispatchKey(VK_TAB, 0); }
```

## evidence string

1. NE relocation chain segment 1 assign každému command ID far pointer to segment `1010`.
2. Priama 16-bit disassemblácia on target address ukazuje constant VK and far call `1010:8CD2`.
3. NE string resources poskytujú text meaning command ID.
4. Dispatcher `1010:9806` confirms konečnú activity F2/F3/F4/F5/F9/F10, Tab, Esc and weapon key.

Confidence operations all listed functions: **high / directly confirmed binary**.