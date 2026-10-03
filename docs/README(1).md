# GAME.PAL Builder

Small WinForms tool for building a raw 256-color RGB palette for Nitemare 3D-style data.

## Supported image input modes
1. **Indexed image palette** – preserves the original palette/index order from an 8-bit indexed PNG/BMP/GIF.
2. **Palette sheet grid** – samples cells left-to-right, top-to-bottom. Default is 16x16 = 256 colors. Useful for Wolf3D palette sheets.
3. **Quantize image** – Median Cut reduction to 256 representative colors.
4. **First 256 unique colors** – scans image pixels from top-left to bottom-right.

## Output
- `GAME_DOS.PAL`: 768 bytes = 256 × (R,G,B), channels scaled to VGA DAC range **0..63**.
- `GAME_WIN.PAL`: 768 bytes = 256 × (R,G,B), channels in **0..255**.

The application can also load an existing 768-byte raw `.PAL` and auto-detect 6-bit palettes when all bytes are <= 63.

## Build on Windows 11
Install the .NET 8 SDK, then in this folder:

```bat
dotnet build -c Release
```

Single-file x64 publish:

```bat
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

Single-file x86 publish:

```bat
dotnet publish -c Release -r win-x86 --self-contained true -p:PublishSingleFile=true
```

## Important note
The program intentionally exposes both raw RGB encodings because classic DOS VGA palettes typically store DAC values in 0..63, while Windows-side tools often use 0..255 RGB. For exact Nite3W compatibility, compare the reader code or a known-good GAME.PAL before treating the Windows 8-bit variant as definitive.