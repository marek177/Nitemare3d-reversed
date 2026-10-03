# WolfVSwap Editor

C# / .NET 8 WinForms editor for classic Wolfenstein 3D `VSWAP.*` files.

## V1 features
- Reads VSWAP header, page offsets and lengths
- Separates Walls / Sprites / Sounds from `SpriteStart` and `SoundStart`
- 64×64 wall decoding
- Classic post-based sprite decoding with transparency
- PNG export (single/all)
- PNG replacement for walls and sprites
- Rebuild / Save As VSWAP
- Automatic `.bak` when overwriting
- Drag-and-drop VSWAP opening
- x64 and x86 publish scripts

## Build
Install .NET 8 SDK, then:
`dotnet build -c Release`

Or run:
- `publish-x64.bat`
- `publish-x86.bat`

## Important
Keep backups of original game data. V1 intentionally does not edit digitized sound chunks.

The palette class is currently embedded as a VGA-compatible palette approximation. For pixel-perfect retail Wolf3D colors, the next revision should embed the exact `wolfpal.inc` table from the selected Wolf4SDL source/version.

## V2 fixes
- Visible preview title explicitly shows `WALL ####` or `SPRITE ####`
- `Ctrl+A` selects all items in the current filtered list
- Multi-selection enabled
- Export Selected exports all selected graphic chunks
- Wall chunks are always decoded with the wall decoder; sprite chunks with the post-sprite decoder
- Status bar displays exact wall/sprite/sound ranges parsed from the VSWAP header

Reference implementation checked against SLADE's WolfArchive VSWAP support.

## V3
- Wolf3D sprite decoder corrected to SLADE's `SIFWolfSprite` algorithm.
- Correct post pixel address: `(start >> 1) + pixelOffset`.
- Transparent 64x64 sprite canvas preserves original horizontal placement.
- Checkerboard transparency preview.
- Batch output is separated into `Walls` and `Sprites` directories.
- Invalid sprite posts/offsets produce explicit errors instead of silently creating blank PNG files.

Note: exact retail WL6 palette replacement is still separate work; V3 focuses on fixing the blank sprite decoder first.