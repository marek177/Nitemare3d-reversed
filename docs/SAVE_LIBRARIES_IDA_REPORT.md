# Nitemare-3D — Save Game, Libraries and IDA Report

Date: 2026-09-17

## Evidence used

Direct original binaries / databases supplied by the user:

- `NITE3W.EXE` (230,400 bytes; Win16 NE)
- `nite3w.exe.i64`
- `USER.SAV` (55,015 bytes)
- `CONFIG.SAV` (20 bytes)
- `WING.DLL` (Win16 NE)
- `wing.dll.i64`
- `DISPDIB.DLL` (Win16 NE)
- `dispdib.dll.i64`
- original MAP data used to verify the current level image in `USER.SAV`

This report labels data as confirmed only where the original binaries/save files support it.

---

# 1. CONFIG.SAV

`CONFIG.SAV` is exactly 20 bytes. `NITE3W.EXE` initializes a contiguous 20-byte configuration block at near-data address `0x4BD4`, loads exactly 20 bytes from `config.sav`, and rejects a file whose length is not 20 bytes with the string `config.sav obsolete, please delete and restart`.

The supplied file is:

```text
30 01 00 00 C0 03 58 02 32 37 28 32 00 01 01 00 00 00 01 00
```

## Confirmed field map

| File offset | Runtime address | Size | Supplied value | Meaning | Confidence |
|---:|---:|---:|---:|---|---|
| `0x00` | `0x4BD4` | 4 | `0x00000130` = 304 | 3-D viewport width / render width | High |
| `0x04` | `0x4BD8` | 2 | 960 | window width (`Size x3`) | 100% |
| `0x06` | `0x4BDA` | 2 | 600 | window height (`Size x3`) | 100% |
| `0x08` | `0x4BDC` | 1 | 50 | mouse sensitivity/scaling | High |
| `0x09` | `0x4BDD` | 1 | 55 | joystick sensitivity/scaling | High |
| `0x0A` | `0x4BDE` | 1 | 40 | MIDI/music volume, percent-like 0..100 | 100% |
| `0x0B` | `0x4BDF` | 1 | 50 | SFX volume, percent-like 0..100 | 100% |
| `0x0C` | `0x4BE0` | 1 | 0 | mouse enable/use flag | High |
| `0x0D` | `0x4BE1` | 1 | 1 | music enabled | 100% |
| `0x0E` | `0x4BE2` | 1 | 1 | sound effects enabled | 100% |
| `0x0F` | `0x4BE3` | 1 | 0 | joystick enabled | 100% |
| `0x10` | `0x4BE4` | 1 | 0 | Omniscient cheat | 100% |
| `0x11` | `0x4BE5` | 1 | 0 | Omnipotent cheat | 100% |
| `0x12` | `0x4BE6` | 1 | 1 | Omnifarious cheat | 100% |
| `0x13` | `0x4BE7` | 1 | 0 | Omnificent cheat | 100% |

Defaults reconstructed from `NITE3W.EXE` are 304 render width, 320x200 window, control values 50/50/60/70, music and SFX enabled, mouse/joystick disabled, and all four cheat flags disabled.

---

# 2. USER.SAV — exact record size and layout

`NITE3W.EXE` hard-codes a save-slot record size of:

```text
0xD6E7 = 55,015 bytes
```

The file seeking code uses `slot_index * 0xD6E7`, proving that `USER.SAV` is a fixed-record save container and can hold multiple slots. The supplied `USER.SAV` is exactly one record long.

The write routine was reconstructed from the original EXE. Every write length below sums exactly to `0xD6E7`.

| Offset | Size | Confirmed / current interpretation |
|---:|---:|---|
| `0x0000` | 4 | record size / format guard = `0x0000D6E7` |
| `0x0004` | 41 | save-slot description/name buffer; supplied text begins `465401` |
| `0x002D` | 2 | episode number; supplied value `1` |
| `0x002F` | 2 | zero-based level index; supplied value `0` => E1M1 |
| `0x0031` | 4 | saved game tick/time base used when rebasing timers after load |
| `0x0035` | `0x2000` (8192) | current 64x64 map state, 2 bytes/cell |
| `0x2035` | `0x005E` (94) | compact gameplay/player/global state block; individual fields still being labeled |
| `0x2093` | `0x6D60` (28000) | fixed-capacity runtime entity/state array; exact record class labeling still pending |
| `0x8DF3` | `0x2648` (9800) | fixed-capacity runtime entity/state array; exact class labeling pending |
| `0xB43B` | `0x0A28` (2600) | fixed-capacity runtime state array; exact class labeling pending |
| `0xBE63` | `0x0580` (1408) | 64 x 22-byte runtime records; exact class labeling pending |
| `0xC3E3` | `0x0020` (32) | auxiliary per-record state list |
| `0xC403` | `0x0150` (336) | runtime state block |
| `0xC553` | `0x0008` | runtime state block |
| `0xC55B` | `0x0048` (72) | runtime state block |
| `0xC5A3` | `0x1000` (4096) | 64x64 byte-per-cell state map; likely map/visibility-related, exact semantic label pending |
| `0xD5A3` | `0x0040` (64) | runtime state block |
| `0xD5E3` | `0x0100` (256) | 256-byte runtime lookup/state block |
| `0xD6E3` | 1 | floor palette index; supplied `0x0C` |
| `0xD6E4` | 1 | ceiling palette index; supplied `0x11` |
| `0xD6E5` | 2 | level render/environment parameter (`0x7E60`); exact semantic label still pending |

## E1M1 verification

The 8192-byte block at `USER.SAV+0x35` matches original Episode 1 Level 1 `MAP.1` at **8188 of 8192 bytes (99.951%)**.

The four changed object bytes are:

```text
(48,52) object 0xA5 -> 0x00
(49,52) object 0x00 -> 0xA5
(22,54) object 0xA4 -> 0x00
(19,53) object 0x00 -> 0xA4
```

This is direct evidence that save games persist the current mutable map/object positions rather than only storing an episode/level number and reloading a pristine map.

The load routine also rebuilds runtime pointers and adjusts stored timers against the current clock after the raw blocks are restored; therefore not every byte in `USER.SAV` is a simple user-facing stat.

---

# 3. Direct libraries imported by NITE3W.EXE

`NITE3W.EXE` is a Windows 16-bit NE executable (target OS Windows) with 10 NE segments and **9 direct imported modules**:

1. `KERNEL`
2. `WING`
3. `DISPDIB`
4. `GDI`
5. `USER`
6. `KEYBOARD`
7. `COMMDLG`
8. `MMSYSTEM`
9. `SHELL`

The executable does **not** import an external MFC DLL. It contains MFC classes/resources and exports `_AFX_VERSION`, which means the MFC/runtime framework is statically linked into this build.

The binary contains the version string:

```text
Nitemare-3D for Windows V1.10
```

## Roles

| Module | Role in Nitemare-3D |
|---|---|
| `KERNEL` | Win16 core services: memory, files, loader, timing, process/task support |
| `GDI` | standard Windows drawing, fonts, bitmaps, palettes/DC operations |
| `USER` | windows, messages, menus, dialogs and input/window management |
| `KEYBOARD` | legacy Win16 keyboard driver/API interface |
| `COMMDLG` | standard common dialogs such as file dialogs |
| `MMSYSTEM` | MCI MIDI sequencing, wave audio, joystick/multimedia services |
| `SHELL` | Windows shell integration |
| `WING` | high-performance DIB rendering path |
| `DISPDIB` | special VGA 256-color full-screen DIB path |

`joystick.drv` is referenced dynamically by the game but is not a direct NE imported module.

---

# 4. WING.DLL IDA / NE report

## Binary identity

- Format: Win16 NE DLL for Windows 3.10+
- 20 NE segments
- Direct imports: `KERNEL`, `GDI`, `DISPLAY`, `USER`, `MMSYSTEM`, `VER`
- Version strings: `WinG Version 1.0`
- Microsoft copyright strings: 1993-1994

## Exports

| Ordinal | Name | Entry |
|---:|---|---|
| 1 | `WEP` | seg1:053A |
| 2 | `___EXPORTEDSTUB` | seg16:0B28 |
| 1001 | `WINGCREATEDC` | seg14:0266 |
| 1002 | `WINGRECOMMENDDIBFORMAT` | seg14:027A |
| 1003 | `WINGCREATEBITMAP` | seg14:0298 |
| 1004 | `WINGGETDIBPOINTER` | seg14:02BC |
| 1005 | `WINGGETDIBCOLORTABLE` | seg14:02DC |
| 1006 | `WINGSETDIBCOLORTABLE` | seg14:0300 |
| 1007 | `WINGCREATEHALFTONEPALETTE` | seg2:0000 |
| 1008 | `WINGCREATEHALFTONEBRUSH` | seg4:0A60 |
| 1009 | `WINGSTRETCHBLT` | seg16:02B6 |
| 1010 | `WINGBITBLT` | seg16:0273 |
| 1500 | `WINGINITIALIZETHUNK16` | seg8:0000 |
| 1501 | `WINGTHUNK16` | seg8:007A |
| 2000 | `REGISTERWINGPAL` | seg1:07FE |
| 2001 | `EXCEPTIONHANDLER` | seg17:0000 |

## WinG functions actually imported by NITE3W.EXE

Nitemare-3D imports exactly six WinG ordinals:

```text
1001 WinGCreateDC
1002 WinGRecommendDIBFormat
1003 WinGCreateBitmap
1006 WinGSetDIBColorTable
1009 WinGStretchBlt
1010 WinGBitBlt
```

It does not directly import WinGGetDIBPointer, GetDIBColorTable, halftone helpers, thunk helpers, RegisterWinGPal or ExceptionHandler.

The IDA database contains the expected WinG strings/symbols and import/export metadata. It also exposes WinG's own debugging/profile infrastructure (`Debug`, `DebugPalette`, profiling messages, video-driver tests), but that infrastructure belongs to WinG and is not the Nitemare-3D developer console.

Additional WinG dynamic/secondary dependencies visible in strings include `WINGDE.DLL`, `toolhelp.dll`, Win32s thunk support and the active Windows display driver.

---

# 5. DISPDIB.DLL IDA / NE report

## Binary identity

- Format: Win16 NE DLL
- 3 NE segments
- Direct imports: `GDI`, `USER`, `KERNEL`
- File/Product Version: **3.11**
- Description: `VGA 256 Color DIB Display DLL`
- Microsoft Windows component

## Exports

| Ordinal | Name | Entry |
|---:|---|---|
| 1 | `DISPLAYDIB` | seg2:0270 |
| 2 | `DISPLAYDIBEX` | seg2:0000 |
| 99 | `WEP` | seg2:028E |

`NITE3W.EXE` imports only:

```text
DISPDIB ordinal 1 = DISPLAYDIB
```

This confirms that the original game has two distinct display paths: normal WinG/windowed DIB rendering and the legacy special full-screen DisplayDib path.

---

# 6. NITE3W.EXE NE / IDA summary

- File format: 16-bit NE Windows application
- Target OS: Windows
- 10 segments
- 9 imported modules
- Resident module name: `NITE3W`
- Exported symbol: `_AFX_VERSION`, ordinal 1
- Nonresident description: `NITE3W Windows Application`
- Embedded application string: `Nitemare-3D for Windows V1.10`
- MFC framework strings/classes are embedded, indicating a statically linked MFC application.

Important already-recovered original routines relevant to this report:

- CONFIG initialization/load/save around segment 3 offsets `0x52AE..0x5387`
- USER.SAV fixed-record query/read around `0x5388..0x5465`
- USER.SAV write routine around `0x5466..0x574A`
- USER.SAV load/restore routine begins around `0x574B`
- hard-coded save-record length `0xD6E7`
- floor/ceiling palette globals `0x7E62/0x7E63`

## Current reverse-engineering status for these three requested areas

| Area | Completion |
|---|---:|
| `CONFIG.SAV` byte layout | ~98-100% |
| `USER.SAV` physical record layout | 100% |
| `USER.SAV` semantic labeling of every internal runtime block | ~55-60% |
| direct DLL/module dependency list | 100% |
| NITE3W -> WinG/DispDib API mapping | 100% |
| WING.DLL export table | 100% |
| DISPDIB.DLL export table | 100% |
| IDA-level naming of every internal WinG/DispDib function | not complete; many internal routines remain unnamed |
