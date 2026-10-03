# Nite3W Win16 – analysis handlerov `1010:0006–0B4C`

## Conclusion

Block contains MFC aplikačnú class, skupinu update use interface, main rám, dokument and render/input window. Is not damaged functions. Handlery are short therefore, lebo prepájajú MFC message map with global state game jadra.

## Rekonštruovaná architektúra

| Vtable | Working class | Base MFC | Role |
|---|---|---|---|
| `1010:05D4` | `CNite3DApp` | `CWinApp` | životný cyklus aplikácie and registration global app inštancie |
| `1010:0792` | `CNite3DMainFrame` | `CFrameWnd` | main rámové window, palette, activation/deaktivácia, status bar and toolbar |
| `1010:08DC` | `CNite3DDocument` | `CDocument` | dokumentová part MFC doc/view architektúry |
| `1010:0BA0` | `CNite3DRenderWindow` | `CWnd` | target WinG render, size image and key input |

## Functions and proposed names

| Address | Proposed name | Finding activity | Confidence |
|---|---|---|---|
| `1010:0006` | `CNite3DApp::CNite3DApp` | Calls `CWinApp` constructor and sets game vtable `05D4`. | high |
| `1010:01DC` | `UpdateEnemyAutoMapperCommand` | MFC `ON_UPDATE_COMMAND_UI` for `32783`/F10; získa enabled/check status through `FUN_1010_0E2C`. | high |
| `1010:0210` | `UpdateWallAutoMapperCommand` | MFC `ON_UPDATE_COMMAND_UI` for `32782`/F9; získa enabled/check status through `FUN_1010_0DEE`. | high |
| `1010:0244` | `UpdateMusicCommand` | MFC UI update command `32778`/F2; reads hudobný flag and update check status during change. | high |
| `1010:026A` | `UpdateSoundCommand` | MFC UI update command `32779`/F3; reads audio flag and update check status during change. | high |
| `1010:0290` | `UpdateWeaponCommand0` | Vyhodnotí available weapon slotu 0 and whether is slot zvolený. | high |
| `1010:02C2` | `UpdateWeaponCommand1` | Vyhodnotí available weapon slotu 1 and whether is slot zvolený. | high |
| `1010:02F4` | `UpdateWeaponCommand2` | Vyhodnotí available weapon slotu 2 and whether is slot zvolený. | high |
| `1010:0326` | `UpdateWeaponCommand3` | Vyhodnotí available weapon slotu 3 and whether is slot zvolený. | high |
| `1010:0358` | `UpdateQuickSaveCommand` | UI update command `32781`/F5; povolí Quick Save only during active hre. | high |
| `1010:037C` | `UpdateQuickLoadCommand` | UI update command `32780`/F4; povolenie viaže on active hru. | high |
| `1010:039C` | `UpdateStatusReportCommand` | UI update command `32784`/Tab; povolí status report only during active hre. | high |
| `1010:0424` | `ApplyAndCloseDialogResult6` | Calls game apply/cleanup handler and `EndDialog(..., 6)`. | high |
| `1010:0670` | `CNite3DMainFrame::CNite3DMainFrame` | Konštruuje `CFrameWnd`, vložený `CStatusBar` on `+0x4E` and `CToolBar` on `+0x80`. | high |
| `1010:06A0` | `CNite3DMainFrame::~CNite3DMainFrame` | Zastaví game subsystémy and deštruuje toolbar, status bar and `CFrameWnd`. | high |
| `1010:0716` | `CNite3DMainFrame::OnPaletteChanged` | Calls basic MFC handler and realizuje game palette for `HWND` odosielateľa. | high |
| `1010:0730` | `CNite3DMainFrame::OnQueryNewPalette` | Realizuje game palette for main window and continues základným MFC handlerom. | high |
| `1010:0748` | `CNite3DMainFrame::OnActivateApp` | Calls MFC base handler and stores/restores input flags during deaktivácii/aktivácii. | high |
| `1010:085E` | `CNite3DDocument::CNite3DDocument` | Calls `CDocument` constructor and sets vtable `08DC`. | high |
| `1010:097C` | `CNite3DRenderWindow::CNite3DRenderWindow` | Calls `CWnd` constructor and sets vtable `0BA0`. | high |
| `1010:09BE` | `CNite3DRenderWindow::PreCreateWindow` | Wrapper nad MFC prípravou `CREATESTRUCT`; sets parametre create window. | high |
| `1010:09E8` | `CNite3DRenderWindow::OnKeyDown` | Pass virtuálny key and flags common dispatcheru `8CD2`. | high |
| `1010:09FA` | `CNite3DRenderWindow::OnSysKeyDown` | Process systémový/Alt key; during Alt+Tab executes MFC focus/activation path. | high |
| `1010:0A2A` | `CNite3DRenderWindow::OnKeyUp` | Pass free key common dispatcheru. | high |
| `1010:0A3C` | `CNite3DRenderWindow::OnSize` | Calls base `CWnd` handler, sets renderovacie `HWND`, stores rozmery on `+0x1C/+0x1E` and restores buffer. | high |
| `1010:0AF8` | `UpdateWindowSize1xRadio` | For command `32771` compares rozmery view with `320×200` and through `CCmdUI::SetRadio` sets radio item. | high |
| `1010:0B22` | `UpdateWindowSize2xRadio` | For command `32772` compares rozmery view with `640×400` and sets radio item. | high |
| `1010:0B4C` | `UpdateWindowSize3xRadio` | For command `32791` compares rozmery view with `960×600` and sets radio item. | high |

## weapon UI handlery

`FUN_1010_0D0E(slot, &enabled, &selected)` confirms four UI weapon sloty:

- available sa odvodzuje z bitmasky `DAT_1048_4C2A`,
- checks sa, whether is game active (`DAT_1048_46B4 == 1`),
- zvolený slot is `DAT_1048_4C24`,
- handlery `0290`, `02C2`, `02F4`, `0326` set enable/check status corresponding items menu or toolbaru.

## Activation aplikácie and input

`FUN_1010_0E6A(active)` during deaktivácii stores `DAT_1048_4BE1/4BE2`, zeros their and restores input/render status. During opätovnej aktivácii values returns. To bráni zaseknutému movement or streľbe after Alt+Tab.

`FUN_1010_8CD2(key, flags)` is shared keyboard dispatcher. Evidované are Shift, Ctrl, Alt, Escape, Space, Enter, šípky and game skratky. Status drží especially v `DAT_1048_3756`, `DAT_1048_3757` and `DAT_1048_0108`.

## Overenie through original NE file

Priame decode MFC message-map z NE segment 1 assign handlerom these ID: `01DC→0x800F`, `0210→0x800E`, `0244→0x800A`, `026A→0x800B`, `0290–0326→0x8006–0x8009`, `0358→0x800D`, `037C→0x800C`, `039C→0x8010`, `0AF8→0x8003`, `0B22→0x8004` and `0B4C→0x8017`. String resources subsequently poskytli exact use names.

Check disassemblácia original bytes at the same time opravila error dekompilátora during `0AF8–0B4C`: functions are not empty forwarding thunky. read width and height object on offset `+0x1C/+0x1E`, compare their with `320×200`, `640×400` or `960×600` and pass boolean tretej virtuálnej method `CCmdUI`, therefore radio/check update.

## remain neistota

V this analyzovanom block already nezostáva unknown activity handlera. Neisté can be only doslovné original names C++ method, because symbol were remove; working names above are meaning exact.