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
