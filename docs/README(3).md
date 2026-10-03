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


## v4.1 - Corridor 7 profile

Added **Corridor 7: Alien Invasion (VGA6)** as a dedicated game profile.
The profile exports a raw 256-colour palette as 768 bytes (256 x RGB), with each channel converted to VGA DAC 6-bit range 0-63.
It can be used with imported palette images, indexed images, or existing 768-byte palette data.

The generic Save VGA6 and Save RGB8 buttons remain available for manual override.