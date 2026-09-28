# Nite3W Win16/Windows 3.11 – analýza 38 slabo zhodných funkcií

## Rozsah a záver

Porovnané dekompilácie: Nite3W 1.3, 1.6, 1.8 a 1.10. Kontrolovala sa rovnaká segmentová adresa, volané funkcie, Win16 API, konštanty, reťazce, práca s globálnymi dátami a susedné funkcie.

Všetkých 38 položiek má telo. Nebola nájdená funkcia, ktorá by bola v Ghidre prázdna pre chybu dekompilácie alebo skutočne chýbala. Slabé automatické skóre spôsobovali najmä relokácie vtable/dát, zmenené adresy reťazcov a veľmi krátke wrappery.

Následná analýza našla `_AFX_VERSION() == 0x0250`, teda Microsoft MFC 2.5. Väčšinu všeobecne pomenovaných frameworkových tried preto možno priradiť ku konkrétnym MFC triedam. Nezostáva funkcia s úplne neznámou činnosťou. Pôvodný súčet „13 neistých“ bol aritmetická chyba; v tabuľke bolo označených 14 položiek.

## Katalóg

| # | Funkcia (1.10) | Navrhnutý pracovný názov | Zistená činnosť | Istota |
|---:|---|---|---|---|
| 1 | `FUN_1000_036a` | `ExceptionBaseCtor` | Inicializuje základný objekt výnimky a jeho vtable. | vysoká |
| 2 | `FUN_1000_0868` | `FileHandleCtorInvalid` | Konštruktor file-wrappera; nastaví handle na `-1`. | vysoká |
| 3 | `FUN_1000_0890` | `FileHandleCtor` | Konštruktor file-wrappera s dodaným handle. | vysoká |
| 4 | `FUN_1000_3282` | `LoadFrameworkStringResourceFF` | Tenký Win16 wrapper nad `LoadString`, používa resource ID `0xFF`. | vysoká |
| 5 | `FUN_1000_338c` | `CMenu::CMenu` | MFC 2.5 `CMenu`; nuluje `HMENU` na `this+4`. | vysoká |
| 6 | `FUN_1000_33f4` | `CMenu::~CMenu` | Pri existujúcom handle volá `DestroyMenu`. | vysoká |
| 7 | `FUN_1000_6694` | `CFrameWnd::~CFrameWnd` | Ničí vnorený `CString` na `+0x46` a pokračuje `CWnd` cleanupom. | vysoká |
| 8 | `FUN_1000_9ebc` | `CDialogBar::CDialogBar` | MFC `CDialogBar`; zavolá `CControlBar` konštruktor a nastaví vlastnú vtable. Identita potvrdená odlíšením od susedných `CStatusBar` a `CToolBar` konštruktorov. | vysoká |
| 9 | `FUN_1008_028c` | `GdiDcObjectCtor` | Konštruktor GDI/DC wrappera; nuluje handle a stavové členy. | vysoká |
| 10 | `FUN_1008_0342` | `GdiDcObjectDtor` | Ak vlastní DC, volá `DeleteDC`; potom obnoví base vtable. | vysoká |
| 11 | `FUN_1008_0c2c` | `ReleaseWindowDcDtorA` | Získa uložené DC, volá `ReleaseDC` a pokračuje základným deštruktorom. | vysoká |
| 12 | `FUN_1008_0c9e` | `ReleaseWindowDcDtorB` | Druhý variant rovnakého RAII cleanupu pre window DC. | vysoká |
| 13 | `FUN_1008_0d38` | `CGdiObject::CGdiObject` | MFC `CGdiObject`; nuluje `HGDIOBJ` na `this+4`. | vysoká |
| 14 | `FUN_1008_0e18` | `CGdiObject::~CGdiObject` | Odpojí handle z MFC mapy a volá `DeleteObject`. | vysoká |
| 15 | `FUN_1008_1ed4` | `CDocTemplate::GetDocString` | Rozdelí resource reťazec podľa LF (`10`) a vyberie položku do `CString`. | vysoká |
| 16 | `FUN_1008_2242` | `CDocTemplate::~CDocTemplate` | Uvoľní menu/resource handly, reťazec a základnú MFC triedu. | vysoká |
| 17 | `FUN_1008_24d8` | `CWnd::CWnd` | MFC `CWnd`; inicializuje základ a nuluje väzbu na `+0x1A`. | vysoká |
| 18 | `FUN_1008_2ac2` | `CView::~CView` | Odpojí view od dokumentu a pokračuje `CWnd` cleanupom. | vysoká |
| 19 | `FUN_1008_3ea4` | `fopen`/`_fsopen` wrapper | CRT wrapper nad file-open rutinou; používa sa pre `order.txt`, `debug.txt` a archívy. Nie je to trieda. | vysoká |
| 20 | `FUN_1008_60fe` | `AbnormalProgramTermination` | Volá Win16 `FatalAppExit` s textom „ABNORMAL PROGRAM TERMINATION“. | vysoká |
| 21 | `FUN_1008_673a` | `ReleaseRuntimeGlobalBlock` | Uvoľní globálny Win16 pamäťový blok cez `GlobalFree`. | vysoká |
| 22 | `FUN_1010_0006` | `CNite3DApp::CNite3DApp` | Herná trieda odvodená z MFC `CWinApp`; pôvodný názov je pracovný. | vysoká štruktúra |
| 23 | `FUN_1010_0424` | `CloseDialogAfterApply` | Zavolá herný apply/cleanup handler a ukončí dialóg výsledkom `6`. | vysoká |
| 24 | `FUN_1010_085e` | `CNite3DDocument::CNite3DDocument` | Herná trieda odvodená z MFC `CDocument`; pracovný názov. | vysoká štruktúra |
| 25 | `FUN_1010_097c` | `CNite3DRenderWindow::CNite3DRenderWindow` | Herné renderovacie/vstupné okno priamo odvodené z `CWnd`; vtable `0x0BA0` obsahuje prípravu okna, klávesové handlery a `OnSize`. Pôvodný autorský názov nie je zachovaný. | vysoká funkcia, pracovný názov |
| 26 | `FUN_1010_3100` | `PaintGameWindowWithPalette` | `BeginPaint`, výber a realizácia palety, vykreslenie/present, `EndPaint`. | vysoká |
| 27 | `FUN_1010_31aa` | `InstallOrAnimateGamePalette` | Vytvorí 256-farebnú paletu alebo animuje 236 položiek od indexu 10; aktualizuje WinG DIB tabuľku. | vysoká |
| 28 | `FUN_1010_3b16` | `SetPaletteColor` | Zapíše RGB do paletového buffera; vo Windows aktualizuje paletu, v DOS ceste zapisuje VGA DAC `3C8/3C9`. | vysoká |
| 29 | `FUN_1010_4868` | `LoadIndexedMapBlock` | Otvorí dátový súbor, seek na `index*0x2000+0x202`, načíta presne 8192 bajtov mapového bloku. | vysoká |
| 30 | `FUN_1010_498a` | `SelectEpisodeAndLoadMapHeader` | Z parametra zostaví tri názvy súborov a z prvého načíta 0x202-bajtový mapový header/adresár. | vysoká |
| 31 | `FUN_1010_5132` | `LoadResourceDirectoryTable` | Zo súboru na offsete `0xC0` načíta 474-bajtovú tabuľku záznamov. | vysoká |
| 32 | `FUN_1010_5cfc` | `EnsureImageDirectoryLoaded` | Lazy-load 0xC0-bajtového indexu archívu; vracia offset záznamu `index*6`. | vysoká |
| 33 | `FUN_1010_5f12` | `LoadImageArchiveEntry` | Podľa 6-bajtového indexového záznamu seekne na offset a načíta položku archívu do cieľového buffera. | vysoká |
| 34 | `FUN_1010_90c2` | `ResetInputState` | Nuluje dva globálne stavové príznaky používané obsluhou Win16 správ/vstupu. | vysoká |
| 35 | `FUN_1018_1ee0` | `ShowCombinationResult` | Zostaví a zobrazí výsledok kombinácie; pre prázdny obsah vypíše „It's empty“, potom obnoví obraz. | vysoká |
| 36 | `FUN_1018_2508` | `ShowWeaponJammedMessage` | Zobrazí správu „Your weapon appears to be jammed“. | vysoká |
| 37 | `FUN_1018_308e` | `ShowWarningDialog` | Formátuje varargs text, pozastaví herný výstup/zvuk, pípne a zobrazí `MessageBox` „Warning“, potom stav obnoví. | vysoká |
| 38 | `FUN_1018_3118` | `FatalErrorAndExit` | Formátuje chybu, zobrazí `MessageBox` „Fatal Error“, ukončí subsystémy a proces s kódom 1. | vysoká |

## Viacverziové zistenia

- Funkcie `1008:028C` až `1008:673A` sú vo všetkých štyroch EXE funkčne rovnaké. Menia sa najmä vtable a dátové segmentové relokácie.
- Funkcie `1010:0424`, `1010:085E` a `1010:097C` sa v zostave 1.3 na rovnakom mieste nenachádzajú; v 1.6, 1.8 a 1.10 sú stabilné. To skôr znamená vloženie alebo reorganizáciu tried než poškodenie.
- Herné funkcie palety, dátových archívov a hlásení majú dostatok charakteristických API volaní, veľkostí blokov a textov na spoľahlivú identifikáciu.
- Pri konštruktoroch/deštruktoroch je presná činnosť potvrdená, no bez RTTI alebo symbolov nemožno na 100 % obnoviť pôvodné C++ názvy tried. Preto sú názvy pracovné.

## Odporúčané premenovanie v Ghidre

Po identifikácii MFC možno bezpečne použiť mená `CMenu`, `CGdiObject`, `CDocTemplate`, `CWnd`, `CView`, `CFrameWnd`, `CControlBar`, `CStatusBar`, `CToolBar`, `CDialogBar`, `CDocument` a `CWinApp`. Pri frameworkových triedach už prefix `prob_` netreba. `CNite3DApp`, `CNite3DMainFrame`, `CNite3DDocument` a `CNite3DRenderWindow` sú funkčne presné pracovné názvy, nie pôvodné symboly.

## Doplnenie vtable 1010

- `1010:05D4`: aplikácia odvodená z `CWinApp`.
- `1010:0792`: hlavný rám odvodený z `CFrameWnd`; konštruktor `FUN_1010_0670`, deštruktor `FUN_1010_06A0`.
- Hlavný rám obsahuje `CStatusBar` na `this+0x4E` a `CToolBar` na `this+0x80`.
- `1010:08DC`: herný dokument odvodený z `CDocument`.
- `1010:0BA0`: renderovacie/vstupné okno odvodené z `CWnd`.
- `FUN_1010_09BE`: wrapper nad MFC `PreCreateWindow` logikou, nie deštruktor.
- `FUN_1010_09E8`, `09FA`, `0A2A`: klávesové/system-key handlery smerujúce do spoločného vstupného dispatchera `FUN_1010_8CD2`.
- `FUN_1010_0A3C`: `OnSize`; uloží rozmery do `this+0x1C/+0x1E`, nastaví renderovacie `HWND` a volá obnovu bufferov.
- `FUN_1010_8CD2`: spoločný keyboard dispatcher; spracúva Shift/Ctrl/Alt/Esc/Space/Enter/šípky, stav klávesov a herné hotkeys.

## Rozlíšenie MFC control-bar tried

- `FUN_1000_53D8` je základný `CControlBar::CControlBar`.
- `FUN_1000_5464` je `CStatusBar::CStatusBar`: vytvára status-bar font, pane tabuľku a počíta šírky textov.
- `FUN_1000_5720` je `CToolBar::CToolBar`: nastavuje button/image rozmery a pracuje s bitmapovým resource.
- `FUN_1000_9EBC` je `CDialogBar::CDialogBar`: nepridáva vlastné dátové polia, iba mení vtable po konštrukcii `CControlBar`.

Najdôležitejší opravný bod oproti pôvodnému automatickému auditu: `FUN_1000_3282` nie je prevod znaku na veľké písmeno; podľa tela ide o wrapper nad `LoadString` s resource ID `0xFF`.