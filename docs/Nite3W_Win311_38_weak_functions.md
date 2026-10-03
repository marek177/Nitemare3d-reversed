# Nite3W Win16/Windows 3.11 – analysis 38 slabo match functions

## Range and conclusion

compare dekompilácie: Nite3W 1.3, 1.6, 1.8 and 1.10. Check sa same segment address, called functions, Win16 API, constant, strings, work with global dátami and adjacent functions.

All 38 items has telo. Was not find function, which by was v Ghidre prázdna for error dekompilácie or actually missing. Slabé automatické score spôsobovali especially relocations vtable/data, change addresses string and very short wrappery.

Subsequent analysis našla `_AFX_VERSION() == 0x0250`, therefore Microsoft MFC 2.5. Väčšinu všeobecne named frameworkových class therefore possible assign ku specific MFC class. Nezostáva function with completely unknown činnosťou. Original sum „13 neistých“ was arithmetic error; v table was označených 14 items.

## Katalóg

| # | Function (1.10) | Proposed working name | Finding activity | Confidence |
|---:|---|---|---|---|
| 1 | `FUN_1000_036a` | `ExceptionBaseCtor` | Initializes basic object výnimky and its vtable. | high |
| 2 | `FUN_1000_0868` | `FileHandleCtorInvalid` | Constructor file-wrappera; sets handle on `-1`. | high |
| 3 | `FUN_1000_0890` | `FileHandleCtor` | Constructor file-wrappera with provided handle. | high |
| 4 | `FUN_1000_3282` | `LoadFrameworkStringResourceFF` | Tenký Win16 wrapper nad `LoadString`, uses resource ID `0xFF`. | high |
| 5 | `FUN_1000_338c` | `CMenu::CMenu` | MFC 2.5 `CMenu`; nuluje `HMENU` on `this+4`. | high |
| 6 | `FUN_1000_33f4` | `CMenu::~CMenu` | During existing handle calls `DestroyMenu`. | high |
| 7 | `FUN_1000_6694` | `CFrameWnd::~CFrameWnd` | Ničí vnorený `CString` on `+0x46` and continues `CWnd` cleanupom. | high |
| 8 | `FUN_1000_9ebc` | `CDialogBar::CDialogBar` | MFC `CDialogBar`; calls `CControlBar` constructor and sets own vtable. Identita confirmed odlíšením from adjacent `CStatusBar` and `CToolBar` konštruktorov. | high |
| 9 | `FUN_1008_028c` | `GdiDcObjectCtor` | Constructor GDI/DC wrappera; nuluje handle and state členy. | high |
| 10 | `FUN_1008_0342` | `GdiDcObjectDtor` | If own DC, calls `Divide`; then restores base vtable. | high |
| 11 | `FUN_1008_0c2c` | `ReleaseWindowDcDtorA` | Získa stored DC, calls `ReleaseDC` and continues základným deštruktorom. | high |
| 12 | `FUN_1008_0c9e` | `ReleaseWindowDcDtorB` | Second variant same RAII cleanupu for window DC. | high |
| 13 | `FUN_1008_0d38` | `CGdiObject::CGdiObject` | MFC `CGdiObject`; nuluje `HGDIOBJ` on `this+4`. | high |
| 14 | `FUN_1008_0e18` | `CGdiObject::~CGdiObject` | Disconnect handle z MFC map and calls `Divide`. | high |
| 15 | `FUN_1008_1ed4` | `CDocTemplate::GetDocString` | Rozdelí resource string according to LF (`10`) and selects item to `CString`. | high |
| 16 | `FUN_1008_2242` | `CDocTemplate::~CDocTemplate` | Free menu/resource handly, string and základnú MFC class. | high |
| 17 | `FUN_1008_24d8` | `CWnd::CWnd` | MFC `CWnd`; initializes base and nuluje link on `+0x1A`. | high |
| 18 | `FUN_1008_2ac2` | `CView::~CView` | Disconnect view from dokumentu and continues `CWnd` cleanupom. | high |
| 19 | `FUN_1008_3ea4` | `fopen`/`_fsopen` wrapper | CRT wrapper nad file-open routine; uses sa for `order.txt`, `debug.txt` and archívy. Is not to class. | high |
| 20 | `FUN_1008_60fe` | `AbnormalProgramTermination` | Calls Win16 `FatalAppExit` with textom „ABNORMAL PROGRAM TERMINATION“. | high |
| 21 | `FUN_1008_673a` | `ReleaseRuntimeGlobalBlock` | Free global Win16 memory block through `GlobalFree`. | high |
| 22 | `FUN_1010_0006` | `CNite3DApp::CNite3DApp` | Game class odvodená z MFC `CWinApp`; original name is working. | high structure |
| 23 | `FUN_1010_0424` | `CloseDialogAfterApply` | Calls game apply/cleanup handler and terminate dialog result `6`. | high |
| 24 | `FUN_1010_085e` | `CNite3DDocument::CNite3DDocument` | Game class odvodená z MFC `CDocument`; working name. | high structure |
| 25 | `FUN_1010_097c` | `CNite3DRenderWindow::CNite3DRenderWindow` | Game render/input window directly derived z `CWnd`; vtable `0x0BA0` contains prípravu window, key handlery and `OnSize`. Original autorský name is not zachovaný. | high function, working name |
| 26 | `FUN_1010_3100` | `PaintGameWindowWithPalette` | `BeginPaint`, selection and realizácia palette, vykreslenie/present, `EndPaint`. | high |
| 27 | `FUN_1010_31aa` | `InstallOrAnimateGamePalette` | Creates 256-color palette or animuje 236 items from index 10; update WinG DIB table. | high |
| 28 | `FUN_1010_3b16` | `SetPaletteColor` | Writes RGB to palette buffera; in Windows update palette, v DOS path writes VGA DAC `3C8/3C9`. | high |
| 29 | `FUN_1010_4868` | `LoadIndexedMapBlock` | Opens data file, seek on `index*0x2000+0x202`, loads exactly 8192 bytes map block. | high |
| 30 | `FUN_1010_498a` | `SelectEpisodeAndLoadMapHeader` | Z parametra zostaví three names file and z first loads 0x202-byte map header/directory. | high |
| 31 | `FUN_1010_5132` | `LoadResourceDirectoryTable` | From file on offsete `0xC0` loads 474-byte table records. | high |
| 32 | `FUN_1010_5cfc` | `EnsureImageDirectoryLoaded` | Lazy-load 0xC0-byte index archívu; returns offset record `index*6`. | high |
| 33 | `FUN_1010_5f12` | `LoadImageArchiveEntry` | According to 6-byte index record seekne on offset and loads item archívu to target buffera. | high |
| 34 | `FUN_1010_90c2` | `Reset` | Nuluje two globally state flags use obsluhou Win16 message/input. | high |
| 35 | `FUN_1018_1ee0` | `ShowCombinationResult` | Zostaví and displays result combinations; for empty content vypíše „It'with empty“, then restores image. | high |
| 36 | `FUN_1018_2508` | `ShowWeaponJammedMessage` | Displays message „Your weapon appears to be jammed“. | high |
| 37 | `FUN_1018_308e` | `ShowWarningDialog` | Format varargs text, pozastaví game output/sound, pípne and displays `MessageBox` „Warning“, then status restores. | high |
| 38 | `FUN_1018_3118` | `FatalErrorAndExit` | Format error, displays `MessageBox` „Fatal Error“, terminate subsystémy and proces with code 1. | high |

## Viacverziové findings

- Functions `1008:028C` up to `1008:673A` are in all four EXE functional same. Menia sa especially vtable and data segment relocations.
- Functions `1010:0424`, `1010:085E` and `1010:097C` sa v zostave 1.3 on same mieste nenachádzajú; v 1.6, 1.8 and 1.10 are stabilné. To skôr mean vloženie or reorganizáciu class than damage.
- Game functions palette, dátových archívov and message have dostatok charakteristických API call, size block and text on spoľahlivú identify.
- During konštruktoroch/deštruktoroch is exact activity confirmed, no without RTTI or symbol cannot on 100 % restore original C++ names class. Therefore are names working.

## Odporúčané premenovanie v Ghidre

After identify MFC possible safely use names `CMenu`, `CGdiObject`, `CDocTemplate`, `CWnd`, `CView`, `CFrameWnd`, `CControlBar`, `CStatusBar`, `CToolBar`, `CDialogBar`, `CDocument` and `CWinApp`. During frameworkových class already prefix `prob_` netreba. `CNite3DApp`, `CNite3DMainFrame`, `CNite3DDocument` and `CNite3DRenderWindow` are functional exact working names, nie original symbol.

## Doplnenie vtable 1010

- `1010:05D4`: aplikácia odvodená z `CWinApp`.
- `1010:0792`: main rám derived z `CFrameWnd`; constructor `FUN_1010_0670`, deštruktor `FUN_1010_06A0`.
- Main rám contains `CStatusBar` on `this+0x4E` and `CToolBar` on `this+0x80`.
- `1010:08DC`: game dokument derived z `CDocument`.
- `1010:0BA0`: renderovacie/input window derived z `CWnd`.
- `FUN_1010_09BE`: wrapper nad MFC `PreCreateWindow` logic, nie deštruktor.
- `FUN_1010_09E8`, `09FA`, `0A2A`: key/system-key handlery direction to common input dispatchera `FUN_1010_8CD2`.
- `FUN_1010_0A3C`: `OnSize`; stores rozmery to `this+0x1C/+0x1E`, sets renderovacie `HWND` and calls obnovu bufferov.
- `FUN_1010_8CD2`: shared keyboard dispatcher; processes Shift/Ctrl/Alt/Esc/Space/Enter/šípky, status key and game hotkeys.

## Distinguish MFC control-bar class

- `FUN_1000_53D8` is basic `CControlBar::CControlBar`.
- `FUN_1000_5464` is `CStatusBar::CStatusBar`: creates status-bar font, pane table and count width text.
- `FUN_1000_5720` is `CToolBar::CToolBar`: sets button/image rozmery and pracuje with bitmapovým resource.
- `FUN_1000_9EBC` is `CDialogBar::CDialogBar`: nepridáva own data arrays, only changes vtable after konštrukcii `CControlBar`.

Najdôležitejší opravný bod compared with original automatickému auditu: `FUN_1000_3282` is not prevod znaku on large písmeno; according to tela is wrapper nad `LoadString` with resource ID `0xFF`.