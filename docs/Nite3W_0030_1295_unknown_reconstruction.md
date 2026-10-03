# Nite3W Win16 – reconstruction hide MFC and štartovacích functions

## Conclusion

V úseku `1010:0030–1295` sa nachádza aplikačný štart, MFC dialog „About“, idle loop and parser parametrov command row. Ghidra viacero z these functions nerozdelila, hoci their boundary are jednoznačné according to `ENTER/LEAVE/RET`, relocation and vtable pointer.

## Rekonštruované functions

| Address | Proposed name | Activity | Confidence |
|---|---|---|---|
| `1010:0026` | `ConstructGlobalApp` | Calls constructor `1010:0006` on global inštancii aplikácie. | high |
| `1010:0030` | `CNite3DApp::InitInstance` | Sets MFC dialog background, loads MRU/profile set, creates `CSingleDocTemplate`, zaregistruje ho, runs new dokument and initializes game window. | high |
| `1010:009A` | `CAboutDlg::CAboutDlg` | Constructor `CDialog` with resource ID `100`, vtable `0554`. | high |
| `1010:00BE` | `CAboutDlg::Provided` | Empty/optimalizovaný MFC DDX verify; `retf 4`. | stredne high |
| `1010:00C2` | `CAboutDlg::GetRuntimeClass` | Returns runtime-class descriptor on DS offset `0x16`; základná class returns descriptor on `0x2A`. | high |
| `1010:00C8` | `CNite3DApp::OnAppAbout` | Creates About dialog, opens ho modálne and calls deštruktor. | high |
| `1010:00EC` | `CNite3DApp::OnIdle` | Calls MFC `CWinThread::OnIdle`; if already MFC does not have work, executes game idle step `1010:DB94`; always returns TRUE. | high |
| `1010:010C` | `CAboutDlg::OnInitDialog` | Calls basic init handler and vyplní About dialog text/number through `1010:0C54`. | high |
| `1010:0C54` | `InitAboutDialogControls` | Sets text check About window, version, copyright/distribúciu and registračný status. | high |
| `1010:1118` | `CNite3DApp::ProcessStartupCommandLine` | Rozdelí command line on tokeny, process choice and during invalid parametri displays „Invalid command line“. | high |
| `1010:5207` | `ApplyRenderWidth` | Z values `DAT_1048:4BD4` computes stred and boundary viewportu compared with width 320 pixel; update render. | high |

## Parser switch `1010:1118`

Parser uses druhé písmeno after `-` and jump-table on `1010:1172`. Numeric parametre reads through `%d`, text through `%s`.

| Switch | Target premenná/action | Meaning confirmed z xrefov |
|---|---|---|
| `-b` | `DAT_1048:46AE = 1` | skip normal úvodného štartu; ide to fast/special štartu game |
| `-c N` | `DAT_1048:469C = N` | verify jednej z troch render/palette values; uses sa as `7E63` |
| `-d N` | `DAT_1048:4698 = N` | override intenzity/levels osvetlenia; uses sa as `7E60` |
| `-e N` | `DAT_1048:46A8 = N` | verify difficulty level during fast štarte (`DAT_1048:4102`) |
| `-f N` | `DAT_1048:469A = N` | override druhej renderovacej/palettovej values; uses sa as `7E62` |
| `-l N` | `DAT_1048:46A6 = N-1` | štart on zadanom level; interné level ID is zero-based |
| `-o` | `DAT_1048:46AB = 1` | zapne debug output to `debug.txt` |
| `-p PATH` | `DAT_1048:46BE = PATH` | sets prefix/cestu for game data files |
| `-r` | `DAT_1048:46B8 = 1` | aktivuje demo recording/replay mode (status 1 v demo state machine) |
| `-s` | `DAT_1048:46AA = 0` | v this version sa after initialize nikde nečíta; probably historical/nepoužitý switch |
| `-w N` | `DAT_1048:4BD4 = N & 0xFFF8` | sets width render viewportu, zarovnanú on 8 pixel |

Unknown písmená, missing values or token without `-` vedú k message `Invalid command line`. Parser after each tokene continues through `strtok`-ekvivalent `FUN_1008:6B06`.

## Important technické dôsledky

`-w` is not only UI choice. `1010:5207` z nej directly computes `DAT_1048:53E0–53F0`, therefore stred viewportu, left/right boundary and projection centrum. Therefore is to hidden input to raycast/render konfigurácie.

`-l` and `-e` are plne functional only total with fast štartom `-b`; without neho sa values save, but normálna úvodná state mašina their does not have to okamžite use.

`-o` is confirmed debug mechanizmus: premenná `46AB` sa test v routine write `debug.txt`.

`-s` is naopak candidate on remove z dokumentácie new remaku, pokiaľ sa nepotvrdí v inej version. V analyzovanej `nite3w(10).exe` sa only sets and subsequently does not have read xref.

## Overenie

- priama disassemblácia segment 3 confirm function boundaries and call-site;
- NE relocation tables confirm references on MFC vtable and interné functions;
- string resources confirm text `Nitemare-3D for Windows V1.10`, `Invalid command line`, `debug.txt` and registračný status;
- `1010:5207` was verify výpočtom boundaries for 320-pixel framebuffer;
- `1010:1118` has 22-entry jump table for choice `b–w`, pričom active are exactly choice listed v table.

Conclusion: this block already is not unknown on úrovni činnosti. Remain only original symbol names niekoľkých MFC wrapperov and exact historical purpose nepoužitého `-s`.