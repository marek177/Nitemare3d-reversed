# GAME.PAL Builder v4

Windows WinForms utility for building 256-colour raw palettes for Nitemare 3D, Wolfenstein 3D-style VGA data and generic RGB8 games.

## New in v4
- Input image preview.
- Indexed palette view with hexadecimal indexes 00-FF.
- Clean 16x16 palette image preview and PNG export.
- Click a colour to see RGB8 and VGA6 values.
- SLADE-style square 16x16 palette image import.
- Wolf3D labelled 16x16 grid auto-detection (works with the supplied 349x334 reference image).
- Presets for Nitemare 3D DOS, Nite3W Windows, Wolf3D, Doom/Heretic/Hexen raw RGB and generic VGA/RGB.
- Raw GAME.PAL export: 768 bytes, 256 RGB triplets.
- x86 and x64 self-contained single-file publish scripts.

## Build
Install .NET 8 SDK on Windows and run:

    publish-all.bat

Outputs:

    publish\x86\GamePalBuilder.exe
    publish\x64\GamePalBuilder.exe

## Palette formats
- VGA6 export stores RGB components in 0..63.
- RGB8 export stores RGB components in 0..255.
- Both are raw 768-byte files (256 * 3 bytes).

For Nite3W specifically, the exact on-disk GAME.PAL component range should still be verified against the executable/game data before treating RGB8 as definitively original.