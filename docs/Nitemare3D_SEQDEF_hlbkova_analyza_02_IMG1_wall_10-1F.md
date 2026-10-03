# Nitemare3D SEQDEF: IMG.1 wall 0x10–0x1F

Individual analysis, 28. 9. 2026. Primary underlying: IMG.1 (SHA-256 0d7b5bf9and3348be263d337201bd98e867f765b87be3f15666164c39763dc1267), WALLS.1. Records sa locate on `0x0800 + 0x5A × ID`; original directory image is on `4 × ID`. WALLS.1 link same index with change editora, nie with zaručenou runtime function.

Each record has 90 bytes. During all item v this batch is `extension_flag=0`, all bytes from `+0x04` to `+0x59` are zero and `+0x02` contains count frames. Different hashe frames prove different pixel data; without play game neurčujú exact visual effect nor kadenciu visible player.

| ID | Name according to WALLS.1 | SEQDEF | Image | Interval | Frames | Shared image with |
|---|---|---:|---:|---:|---:|---|
| `0x10` | Living Room - Panel Left (`REVWALL`) | `0x0DA0` | `0x3CCFA` | 0 | 1 | — |
| `0x11` | Kitchen - Sink Area (`WALL`) | `0x0DFA` | `0x3ED04` | 0 | 1 | — |
| `0x12` | Kitchen - Fuse box (`SPECIAL1`) | `0x0E54` | `0x40D0E` | 0 | 1 | — |
| `0x13` | Kitchen - Stove Area (`WALL`) | `0x0EAE` | `0x41D18` | 0 | 1 | — |
| `0x14` | Kitchen - Plain (`WALL`) | `0x0F08` | `0x43D22` | 0 | 1 | — |
| `0x15` | Kitchen - Door (red key) (`WARP_L1`) | `0x0F62` | `0x45D2C` | 0 | 1 | `0x5A` |
| `0x16` | *Kitchen - Door (stairs up) (`WALL`) | `0x0FBC` | `0x47D36` | 0 | 1 | `0x94`, `0x96`, `0x98` |
| `0x17` | *Kitchen - Door (stairs down) (`WALL`) | `0x1016` | `0x49D40` | 0 | 1 | `0x97` |
| `0x18` | Kitchen - Panel Right (`REVWALL`) | `0x1070` | `0x4BD4A` | 0 | 1 | — |
| `0x19` | Kitchen - Panel Left (`REVWALL`) | `0x10CA` | `0x4DD54` | 0 | 1 | — |
| `0x1A` | Beige Hallway - Plain (`WALL`) | `0x1124` | `0x4FD5E` | 0 | 1 | — |
| `0x1B` | Beige Hallway - Panel Right (`REVWALL`) | `0x117E` | `0x51D68` | 0 | 1 | — |
| `0x1C` | Beige Hallway - Panel Left (`REVWALL`) | `0x11D8` | `0x53D72` | 0 | 1 | — |
| `0x1D` | Grey Hallway - Plain (`WALL`) | `0x1232` | `0x55D7C` | 0 | 1 | — |
| `0x1E` | Grey Hallway - Panel Right (`REVWALL`) | `0x128C` | `0x57D86` | 0 | 1 | — |
| `0x1F` | Grey Hallway - Panel Left (`REVWALL`) | `0x12E6` | `0x59D90` | 0 | 1 | — |

## Individual records

### `0x10` — Living Room - Panel Left (`REVWALL`)

- **Confirmed:** SEQDEF `0x0DA0`, image pointer `0x3CCFA`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0040`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `086f3da280da`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x11` — Kitchen - Sink Area (`WALL`)

- **Confirmed:** SEQDEF `0x0DFA`, image pointer `0x3ED04`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0044`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `100d659fce0a`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x12` — Kitchen - Fuse box (`SPECIAL1`)

- **Confirmed:** SEQDEF `0x0E54`, image pointer `0x40D0E`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0048`.
- **Confirmed:** 1 decoded frames; rozmery `64x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `4f079444e45f`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `SPECIAL1` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x13` — Kitchen - Stove Area (`WALL`)

- **Confirmed:** SEQDEF `0x0EAE`, image pointer `0x41D18`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x004C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `d2e2d19e86ea`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x14` — Kitchen - Plain (`WALL`)

- **Confirmed:** SEQDEF `0x0F08`, image pointer `0x43D22`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0050`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `54be1cf8f828`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x15` — Kitchen - Door (red key) (`WARP_L1`)

- **Confirmed:** SEQDEF `0x0F62`, image pointer `0x45D2C`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0054`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `1db591b89d90`. Check streamu: `OK`.
- **Confirmed:** same image pointer use also ID `0x5A`. Their own SEQDEF records sa must assess separate.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WARP_L1` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x16` — *Kitchen - Door (stairs up) (`WALL`)

- **Confirmed:** SEQDEF `0x0FBC`, image pointer `0x47D36`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0058`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `c2e68e0e35b8`. Check streamu: `OK`.
- **Confirmed:** same image pointer use also ID `0x94`, `0x96`, `0x98`. Their own SEQDEF records sa must assess separate.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x17` — *Kitchen - Door (stairs down) (`WALL`)

- **Confirmed:** SEQDEF `0x1016`, image pointer `0x49D40`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x005C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `390d9a082827`. Check streamu: `OK`.
- **Confirmed:** same image pointer use also ID `0x97`. Their own SEQDEF records sa must assess separate.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x18` — Kitchen - Panel Right (`REVWALL`)

- **Confirmed:** SEQDEF `0x1070`, image pointer `0x4BD4A`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0060`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `835cc310a675`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x19` — Kitchen - Panel Left (`REVWALL`)

- **Confirmed:** SEQDEF `0x10CA`, image pointer `0x4DD54`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0064`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `dac8f250a7ea`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x1A` — Beige Hallway - Plain (`WALL`)

- **Confirmed:** SEQDEF `0x1124`, image pointer `0x4FD5E`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0068`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `9244c3a53eb3`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x1B` — Beige Hallway - Panel Right (`REVWALL`)

- **Confirmed:** SEQDEF `0x117E`, image pointer `0x51D68`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x006C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `57604b871dad`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x1C` — Beige Hallway - Panel Left (`REVWALL`)

- **Confirmed:** SEQDEF `0x11D8`, image pointer `0x53D72`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0070`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `790af1391067`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x1D` — Grey Hallway - Plain (`WALL`)

- **Confirmed:** SEQDEF `0x1232`, image pointer `0x55D7C`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0074`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `dbb41e4f3862`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x1E` — Grey Hallway - Panel Right (`REVWALL`)

- **Confirmed:** SEQDEF `0x128C`, image pointer `0x57D86`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0078`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `cd1c62e14760`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x1F` — Grey Hallway - Panel Left (`REVWALL`)

- **Confirmed:** SEQDEF `0x12E6`, image pointer `0x59D90`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x007C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `5a4fe5d53b45`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

## Notes k version and evidence

- `0x12` is v `WALLS.1` marked `SPECIAL1` (fuse skrinka). Its SEQDEF poskytuje only jednu frame; if game changes status skrinky, this specific stream neposkytuje next frame. Change through other ID or runtime status remains open.
- `0x15` has v `WALLS.1` designation `WARP_L1` (doors with red key). Its SEQDEF has jednu frame and interval 0; itself name nedokazuje condition key nor teleport. Same image pointer shared `0x5A`.
- `0x16` and `0x17` are named as doors schodov nahor/nadol and use separate jedno-frame streamy. Shared pointer with higher ID are listed during individual item.
- File `MAP.1` is available, but v this batch was not confirmed its code relationship between whole and wall selectorom; therefore are not listed counts occurrence v map.

- According to previous static auditu is vzorec offset SEQDEF supported v Win16 1.10 and 1.8 also DOS 2.0. This batch checks directly IMG.1 and WALLS.1; priame comparison each next EXE still nebolo performed.
- `alias_ids` v source inventory use hexadecimal numbers **without** prefixu. For example `70,71` mean `0x70,0x71` (desiatkovo 112,113).
- Zero interval during jedinej frame mean data interval 0, nie evidence vypnutej runtime animations.
- Next batch follow on `IMG.1` wall `0x20–0x2F`.