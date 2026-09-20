# NITE3W.EXE deep reverse audit — 2026-09-20

Input: nite3w(8).exe
SHA-256: 12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481
Size: 230400 bytes (0x38400)
Format: 16-bit Windows NE executable, target Windows 3.x (NE target OS=2), linker version 5.

## Confirmed NE layout

NE header offset: 0x80
Segments: 10
Imported modules: 9
Automatic data segment: 10
Initial heap: 0x4262
Initial stack: 0x2EE0
Alignment shift: 4 (16-byte sectors)
Resource entries reported by NE header: 0

File-backed segments:
1: file 0x004C0, length 0xDCE2, flags 0x1D50
2: file 0x0E8A0, length 0x73FE, flags 0x1D50
3: file 0x15FC0, length 0xEFBC, flags 0x1D50
4: file 0x25260, length 0x563C, flags 0x1D50
7: file 0x2A9C0, length 0x1646, flags 0x0D51
10: file 0x2C040, length 0x8EAE, flags 0x0D51

Segments 5, 6, 8 and 9 have no file image and are allocation/BSS-style segments.

## Confirmed imported modules

1. KERNEL
2. WING
3. DISPDIB
4. GDI
5. USER
6. KEYBOARD
7. COMMDLG
8. MMSYSTEM
9. SHELL

The WING + DISPDIB imports are strong evidence that the Windows build has a dedicated WinG/DIB display path rather than being a trivial DOS executable wrapper. MMSYSTEM confirms Windows multimedia API integration.

## Embedded framework/class evidence

Strings in the executable include:
- NITE3W
- NITE3W Windows Application
- CMainFrame
- CNite3wDoc
- CNite3wView
- CObject
- CFile
- CPtrList
- CDialog
- CMenu
- CCmdTarget
- CWinApp
- AfxFrameOrView
- AfxMDIFrame
- AfxControlBar
- AfxWnd
- CWnd
- CPrintDialog
- CFileDialog
- CException / CFileException / CArchiveException / CMemoryException

This establishes substantial Microsoft MFC runtime/framework code in the binary. Reverse-engineering must distinguish MFC/library routines from Nitemare-specific engine routines to avoid false function counts and false gameplay identifications.

## Immediate reverse-engineering consequences

1. Treat segments 1-4 primarily as executable-code candidates and audit their call graph separately from framework thunks.
2. Segment 10 is the automatic data segment and is a priority target for global state, tables and object/static data.
3. Cross-reference calls/import fixups to WING, DISPDIB and GDI to isolate the framebuffer/presentation boundary. Engine rendering immediately upstream of that boundary is a high-value raycaster target.
4. Cross-reference MMSYSTEM imports to isolate sound/music/timer paths.
5. Cross-reference KEYBOARD/USER calls to isolate input handling and separate it from gameplay input-state processing.
6. Identify file-open/read/seek paths and trace filename/extension consumers to recover MAP.*, IMG.*, OBJECTS.*, WALLS.*, UIF.DAT and SND.DAT loaders.
7. Do not label MFC constructors/destructors/message-map glue as game-engine functions merely because they are reachable from the entry path.

## Audit status

- Binary/NE structure: started, confirmed.
- Segment map: confirmed at NE-table level.
- Import-module map: confirmed.
- Framework fingerprint: confirmed (MFC).
- Renderer audit: pending call/fixup-level classification.
- AI/enemy audit: pending.
- map/IMG/WALLS/OBJECTS/UIF/SND loader xrefs: pending.
- damage/difficulty/score tables: pending.
- door/curtain/teleport mechanics: pending.
- joystick/gamepad path: pending.
- hidden/debug/unused code: pending.
- full function/xref catalogue: pending.

This document records only findings directly supported by the current executable scan. Hypotheses are deliberately separated from confirmed facts.
