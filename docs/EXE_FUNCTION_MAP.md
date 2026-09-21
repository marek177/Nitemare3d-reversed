# NITE3W.EXE function map (work in progress)

Addresses use `NE-segment:offset` notation. Names are reconstructed descriptive names unless explicitly identified by surviving symbols/strings.

| Address | Reconstructed role | Confidence | Evidence |
|---|---|---|---|
| `3:1296` | FindDoor-like lookup | medium | failure path references `Door not in map` |
| `3:133A` | FindPush-like lookup | high | failure path references `Push not in map`; scans push records |
| `3:14A8` | Initialize door table | high | hard maximum `0x40` |
| `3:16D6` | Initialize panel table | high | hard maximum `0x20` |
| `3:181C` | Initialize push table | high | runtime class `0x28`, max `0x0C` |
| `3:21B6` | StartPush | high | copies cardinal movement increments and sets 8-step counter |
| `3:2210` | UpdatePushes | high | updates fixed-point XY, map object cell, decrements counter |

## Renderer path recovered 2026-09-21

The renderer is a projected-vector/span pipeline, not a Wolfenstein-style
per-column tile-grid DDA. The complete instruction evidence, file offsets and
comparison with Catacomb Abyss, Hovertank 3-D and Wolfenstein 3-D are in
[`analysis/nite3w_renderer.md`](../analysis/nite3w_renderer.md).

| Address | Reconstructed role | Confidence | Evidence |
|---|---|---|---|
| `3:2F36` | create 320x200 WinG framebuffer | high | stores returned pixel selector and clears exactly 64,000 bytes |
| `3:3612` | fill ceiling/floor | high | direct indexed-buffer writes with 320-byte stride |
| `3:366A` | draw textured wall column | high | `texture_x << 6`, fixed-point vertical sampling, framebuffer stride 320 |
| `3:374E` | draw scaled sprite | high | depth test, transparent palette index `0x29`, stride 320 |
| `3:6152` | initialize wall-span interpolation | high | writes interpolation fields in a `0x14`-byte span record |
| `3:6266` | coalesce column owners into wall spans | high | scans `0x53FE + 4*x`, maximum 50 records |
| `3:6422` | wall/special-wall column clip | medium | orientation/type branches can reject a column; full case meanings open |
| `3:66B0` | rasterize wall spans | high | per-x interpolation, depth update and wall-column call |
| `3:6914` | projected-sprite pass | high | 100 records, `0x12`-byte stride |
| `3:D78C` | render-frame orchestrator | high | calls visibility, span, clear, wall, object and sprite stages in order |
| `3:E516` | set view angle/trig state | high | normalizes degrees, derives 45-degree octant and trig components |
| `3:E798` | transform/project wall vector | high | camera transform, near clip and projected endpoints |
| `3:EBD6` | wall texture-coordinate helper | medium | orientation-dependent fixed-point coordinate calculation |
| `4:3564` | project vector and claim columns | high | clips a projected interval and fills empty owner entries |
| `4:3940` | traverse four sorted vector lists | high | front-to-back list traversal stops when viewport coverage is complete |

Additional executable anchors include diagnostics for missing door/push records, maximum door/panel/push counts, undefined wall/object classes and empty object-class lookups. These are useful anchors for continuing door, panel, pushable and object-class dispatch reconstruction.


## 2026-09-18 cross-audit anchors

The Ghidra/IDA cross-audit adds the following durable anchors. Ghidra addresses use its synthetic Win16 selectors; logical NE segment numbers remain the canonical form for executable reconstruction.

| Ghidra address / area | Reconstructed role | Confidence | Evidence |
|---|---|---|---|
| `1000:036A` | far C++/MFC helper candidate | medium | `__stdcall16far`, 10 callers, writes far-pointer-like values using selector `1018h` |
| `1000:9504` area | GDI presentation/blit path | high | direct `GDI::BITBLT` call |
| `1000:97E4` area | indexed framebuffer/DIB presentation path | high | direct `GDI::STRETCHDIBITS` call |
| `1000:91xx` area | DIB creation helper | high | direct `GDI::CREATEDIBITMAP` call |
| `1010:8CD2` | high-fanout switch dispatcher candidate | medium | 18 callers and a multi-case dispatch table |
| `1010:99xx` area | keyboard/input state path | high | direct `USER::GETASYNCKEYSTATE` plus auto-data flag accesses |
| `1048:0D90` strings | door/push lookup diagnostics | high | `Door not in map`, `Push not in map` |
| `1048:0DB0` strings | runtime door/panel limits | high | `MAXDOORS exceeded (%d)`, `MAXPANELS exceeded (%d)` |
| `1048:0CE8` / `0D24` strings | object/sound cache statistics | high | reload/thrash diagnostic counters |

### Address mapping note

Ghidra uses synthetic selectors `1000,1008,1010,...,1048` for the ten logical NE segments. They must not be copied literally as overlapping IDA flat segment bases. For the non-overlapping IDA reconstruction layout starting at `0x100000`, map selector `1000 + 8*(n-1)` to slot `0x100000 + 0x10000*(n-1)` and then add the 16-bit offset. Example: Ghidra `1008:3718` (logical segment 2 entry point) maps to IDA linear `0x113718`.
