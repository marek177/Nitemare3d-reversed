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


## Phase 2 — relocation/XREF audit

### CONFIRMED — WinG presentation path is concentrated in segment 3

NE relocation records identify these WinG calls:
- seg3:0x2F77 -> WING ordinal 1001 = WinGCreateDC
- seg3:0x2F51 -> WING ordinal 1002 = WinGRecommendDIBFormat
- seg3:0x2F8D -> WING ordinal 1003 = WinGCreateBitmap
- seg3:0x33CF -> WING ordinal 1006 = WinGSetDIBColorTable
- seg3:0x30E2 -> WING ordinal 1009 = WinGStretchBlt
- seg3:0x32FE -> WING ordinal 1010 = WinGBitBlt
- seg3:0x2EC4 -> DISPDIB ordinal 1

The WinG ordinal names were cross-checked against the historical WinG export specification. The executable therefore has a concrete WinG framebuffer/display setup and blit/presentation cluster around segment 3 offsets ~0x2E96–0x33xx.

Disassembly at seg3:0x2F36 begins a coherent initialization routine. It invokes WinGRecommendDIBFormat / WinGCreateDC / WinGCreateBitmap through relocation-patched far calls and initializes a large pixel-memory region. This is now the primary presentation-boundary anchor for tracing backwards into the software renderer.

### CONFIRMED — multimedia/audio cluster in segment 3

MMSYSTEM relocation targets are heavily concentrated around seg3:0xD686–0xE4A0, with additional calls near 0x8FAB/0x8FCE and one in segment 4.

Observed MMSYSTEM ordinals include:
2, 102, 103, 201, 202, 211, 212, 401, 403, 404, 405, 406, 407, 408, 411, 415, 416, 604, 605, 606, 607, 701, 702, 706.

The same region is adjacent to embedded diagnostics for the sequencer/MCI path:
- "sequencer"
- "MCI temp file"
- "SeqID = %d (DEVTYPE)"
- "SeqID = %d (sequencer)"
- "MOD_SQSYNTH, id=%d"
- "MOD_FMSYNTH, id=%d"
- "MOD_SYNTH, id=%d"
- "Tune %d not found"

This cleanly separates a Windows multimedia subsystem from the core game simulation.

### CONFIRMED — keyboard and joystick paths

KEYBOARD relocations occur at seg1:0x0C64, seg2:0x1104 and seg3:0x8CBF.

Joystick-specific embedded diagnostics/configuration:
- "No joystick driver installed"
- "Joystick is unplugged"
- "Joystick error"
- "system.ini"
- "JoyCal0"
- "joystick.drv"
- "joystick"

The joystick error string has a direct segment-3 immediate-string reference near 0x8EED, making the ~0x8Cxx–0x8Fxx area a high-priority input/joystick cluster.

### CONFIRMED — file/data-loader evidence

The binary contains direct diagnostics and names for:
- snd.dat
- game.pal
- map.
- img.
- demo.
- uif.dat
- ending.fli
- nite3d.bsf
- map.1
- config.sav
- user.sav

It also embeds loader/error labels:
- Read_image()
- Read_img_sequence()
- Read_images()
- Text_read()
- "Error opening file %s"
- "Error reading file %s"
- "Error seeking file %s"
- "Image format invalid"
- "UIF image not found, num=%d"

Immediate references into the automatic data/string segment locate loader candidate clusters:
- MAP name/prefix references: seg3:0x4998 and seg4:0x246C/0x24C6 (plus additional candidate)
- IMG prefix references: dense cluster in seg3 including 0x3E6F, 0x49AA, 0x4DB8, 0x4E8D, 0x4FA5, 0x50B6, 0x68D1, 0x7C36, 0x8191, 0x8301, 0xA83F, 0xA8A9
- UIF.DAT references: seg3 ~0x5D10–0x5F7C
- SND.DAT references: seg3 ~0x4814–0x517A and ~0x9436–0x944E, plus seg1 candidate

These are candidate XREFs from raw immediate matching; each must be validated against instruction boundaries before assigning final function names.

### CONFIRMED — gameplay structures and debug instrumentation

The executable contains unusually useful internal diagnostics:
- "class %d, strength %d, strategy %d"
- "state %d, nextstate %d, timer %d"
- "octant %d, resoct %d"
- "Problem with guard: state=%d, next_state=%d, o_id=0x%x"
- "Guard not in map"
- "Guards left: %d, Panels left: %d"
- "Vectors: %u/%u, Objects: %u/%u, Guards: %u/%u"
- "Frame rate: %u/sec (%u mS), [%u,%u]"
- near/far heap statistics
- tile/object/sound slot reload/thrash statistics
- "Game Statistics"

The direct reference to "class %d, strength %d, strategy %d" occurs at seg3:0xABD7 inside a routine around 0xAB80. Nearby code reads multiple fields from a guard-like record and indexes another table with a 0x1C-byte stride. Other gameplay routines also advance records by 0x1C. This is strong evidence for a 28-byte gameplay/guard record or a closely related 28-byte table element; field semantics still require validation.

### CONFIRMED — doors, panels, pushes and exploding walls

Embedded hard limits/error paths:
- "Door not in map"
- "Push not in map"
- "MAXDOORS exceeded (%d)"
- "MAXPANELS exceeded (%d)"
- "MAXPUSHES exceeded (%d)"
- "Exploding wall not in map"

The "Door not in map" diagnostic is referenced from multiple routines around seg3:0x12DA, 0x132C and 0x15E9. The surrounding disassembly performs coordinate comparisons and iterates fixed-size records, giving a concrete anchor for reconstructing door/map-object lookup structures.

The exploding-wall diagnostic is directly referenced near seg3:0x9C0F. The surrounding routine performs tile-coordinate conversion with arithmetic shifts by 6, searches/creates a map object, and handles object classes 0x2D/0x2F. This is a strong gameplay-mechanics anchor.

### CONFIRMED — map/world fixed-point scale clue

Multiple gameplay routines convert position values to tile coordinates using arithmetic shift-right by 6 (SAR 6). This demonstrates a 64-unit sub-tile/fixed-point coordinate scale in those paths. This should be checked against MAP/object coordinate decoding before generalizing it to every engine coordinate.

### CONFIRMED — object/guard limits and on-screen list

The executable has explicit failure paths:
- "Too many objects on screen"
- "MAXOBJ exceeded (%d)"
- "MAXGUARD exceeded (%d)"
- "MAXVECLIST exceeded (%d)"
- "MAXVEC exceeded (%d)"

"Too many objects on screen" is directly referenced around seg3:0xCEE0, adjacent to code that iterates 0x1C-byte records and compares world/tile coordinates. This is a useful anchor for the visible-object/vector pipeline.

### CONFIRMED — cheat/debug features are real shipped code

Strings include:
- "Position %d,%d  Cheat modes: %s"
- "Cheats..."
- "Omniscient (all-knowing)"
- "Omnipotent (all-powerful)"
- "Omnificent (all-cunning)"
- "Omnifarious (all things)"
- "Cheat modes are only available when you purchase the complete trilogy."
- "debug.txt"
- "Beta release!!!  Do NOT distribute"

The cheat-status format is directly referenced from segment 4 around 0x26F5/0x274B. "debug.txt" has multiple code-segment candidate references. This establishes that debug/cheat instrumentation is not merely external documentation; executable code paths reference it.

### CONFIRMED — remote-control gameplay actions

Menu/action strings include:
- Open remote doors
- Close remote doors
- Enable remote cannons
- Disable remote cannons

These will be traced into their command handlers in the next XREF pass and compared with map/object classes.

### STRONG EVIDENCE

- Segment 3 ~0x2E96–0x33xx is the Windows framebuffer creation/presentation layer.
- Segment 3 ~0xD6xx–0xE4xx is a multimedia/audio/MCI control layer.
- Segment 3 ~0x8Cxx–0x8Fxx contains joystick/input support.
- Segment 3 ~0x12xx–0x16xx is strongly associated with door/map-object lookup and setup.
- Segment 3 ~0x9Bxx–0x9Cxx contains exploding-wall mechanics.
- Segment 3 ~0xABxx contains guard debug/state inspection and exposes useful record fields.
- Segment 3 ~0xCExx contains visible-object/list management.

### HYPOTHESES — not yet promoted to facts

- The 0x1C-byte stride may be the principal guard/object runtime structure. It is confirmed as a recurring record stride, but the exact C struct boundary and all fields are not yet reconstructed.
- Renderer/raycaster code should be upstream of the WinGBitBlt/WinGStretchBlt calls, but no function is yet labelled "raycaster" until the wall-column/ray traversal loop is structurally identified.
- Strength is likely connected to enemy HP/durability, but the binary string alone does not prove whether it is current HP, base HP, attack strength, or another gameplay parameter.

## Updated audit status

- Binary/NE structure: CONFIRMED
- Segment map: CONFIRMED
- Import/fixup map: CONFIRMED, second-pass underway
- WinG display boundary: CONFIRMED
- Multimedia subsystem cluster: CONFIRMED
- Keyboard/joystick cluster: CONFIRMED at import/string-XREF level
- MAP/IMG/UIF/SND loader clusters: LOCATED, function-boundary validation underway
- Door/map-object lookup: LOCATED
- Exploding-wall mechanics: LOCATED
- Guard/state debug path: LOCATED
- 64-unit tile-coordinate conversion: CONFIRMED in multiple gameplay paths
- Cheat/debug code: CONFIRMED
- Full renderer/raycaster decomposition: pending
- wall-column and sprite projection routines: pending
- enemy HP/damage/difficulty/score semantics: pending
- teleport/curtain mechanics: pending
- complete function/caller/callee catalogue: pending


## Phase 3 — renderer boundary and structure-recovery plan

### CONFIRMED — WinG export identities independently cross-checked

The segment-3 presentation anchors from Phase 2 match the historical 16-bit WinG export table:
1001 WinGCreateDC; 1002 WinGRecommendDIBFormat; 1003 WinGCreateBitmap; 1004 WinGGetDIBPointer; 1005 WinGGetDIBColorTable; 1006 WinGSetDIBColorTable; 1007 WinGCreateHalfTonePalette; 1008 WinGCreateHalfToneBrush; 1009 WinGStretchBlt; 1010 WinGBitBlt.

This strengthens the classification of seg3 ~0x2E96–0x33xx as presentation/setup rather than the raycaster itself. WinGBitBlt/WinGStretchBlt copy/stretch an already rendered source DC/bitmap to a destination; therefore the actual wall/sprite rasterization should be sought in callers and data writers upstream of these calls.

### STRONG EVIDENCE — expected renderer split

The binary architecture now supports a three-layer working model:
1. Win16/MFC window and paint/event layer.
2. WinG DIB/framebuffer creation, palette and final blit layer in segment 3.
3. Game-specific software renderer that writes the 8-bit indexed framebuffer before layer 2 presents it.

This is a structural model, not yet a claim about exact function boundaries.

### Next static signatures to promote renderer routines to CONFIRMED

A candidate will only be labelled wall/ray code after finding several of:
- repeated screen-column loop / x increment,
- per-column distance or projected-height calculation,
- texture-column address calculation,
- clipping against viewport top/bottom,
- writes into the WinG bitmap pixel pointer or an intermediate 8-bit buffer,
- traversal using map/tile coordinates,
- fixed-point shifts/multiplies,
- caller relationship leading to the confirmed WinG presentation routine.

Sprite routines will require evidence such as projected x/y, scale by distance, transparent-pixel handling, clipping, and depth/occlusion interaction.

### Guard/object 0x1C record reconstruction matrix

Current status:
- 0x1C stride: CONFIRMED recurring gameplay-table stride.
- class/strength/strategy: CONFIRMED field labels emitted by shipped debug code.
- state/nextstate/timer: CONFIRMED debug labels associated with guard state diagnostics.
- exact byte offsets: NOT YET CONFIRMED.
- whether strength is HP: HYPOTHESIS.

The next pass should correlate every memory operand in the debug-print routine with the argument push order, then propagate those recovered offsets to all 0x1C-stride XREFs. This should turn the anonymous record into a partial C struct without guessing.

### Damage/difficulty/score audit criteria

No value will be named HP/damage/score merely because it changes around an enemy. Confirmation requires one of:
- decrement/comparison leading to death/state transition,
- direct association with a score accumulator after kill,
- difficulty-indexed table access or branch,
- debug/string semantic evidence,
- repeated consistency across more than one enemy class.

### Door / curtain / teleport audit split

Door records already have concrete XREF anchors. Curtain animation and two-destination teleport selection remain separate targets; they must not be folded into the generic door implementation until code/data evidence shows a shared mechanism.

### New deliverables queued

- analysis/nite3w_function_map.csv — segment:offset, provisional name, confidence, callers/callees, subsystem.
- analysis/nite3w_guard_record.md — recovered 0x1C structure with evidence per field.
- analysis/nite3w_renderer.md — framebuffer ownership, render-call chain, wall/sprite routine evidence.
- analysis/nite3w_loaders.md — MAP/IMG/UIF/SND/BSF loader call chains and format observations.


## Phase 4 — guard field offsets recovered; record-stride correction

### CONFIRMED — guard debug fields

Disassembly of seg3 ~0xABA2–0xABE4 around the direct XREF at 0xABD7 allows the printf arguments to be reconstructed exactly. The inspected runtime record contains:
- +0x06 word: timer
- +0x08 word: index into a second definition/class table
- +0x0A byte: strategy
- +0x0B byte: state
- +0x0C byte: nextstate
- +0x10 byte: strength
- +0x11 byte: octant
- +0x12 byte: resoct

The printed class is fetched indirectly: runtime +0x08 is multiplied by 0x1C and used to index a second table; a byte from that definition entry is printed as class.

### CORRECTION

The previous broad working statement that a 0x1C stride represented the general guard/object runtime record was too strong. The new instruction-level reconstruction shows that 0x1C is definitely the stride of the secondary class/definition table used by this debug path.

A different visible-object path at seg3:0xCE91 explicitly uses an IMUL stride of 0x1A (26 bytes). These must be treated as separate structures until further XREF propagation proves relationships.

This correction is recorded explicitly to prevent a speculative struct size from propagating into OpenNitemare3D.

### CONFIRMED — exploding-wall object mutation details

The seg3 ~0x9BD2–0x9C79 path:
- converts two coordinates to tiles using SAR 6;
- searches for an existing map object;
- if absent, requests/creates class 0x2D;
- on an object-type value 0x2E, writes runtime byte +0x03 = 0 and +0x06 = 0x2D;
- on value 0x2F, writes +0x03 = 1 and +0x06 = 0x2D;
- copies/uses byte +0x04 and stores a far pointer at +0x08/+0x0A derived from a table indexed by that byte.

This gives concrete field-write evidence for the exploding-wall runtime object, though field names other than the class/type values remain provisional.

### New repository artifacts

- analysis/nite3w_guard_record.md
- analysis/nite3w_function_map.csv

These files separate instruction-backed facts from hypotheses and will be expanded as XREFs are propagated.
