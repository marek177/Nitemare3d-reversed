# Nitemare3D SEQDEF: IMG.1 wall 0x00–0x0F

First batch individual analysis, 28. 9. 2026. Primary underlying: IMG.1 (SHA-256 0d7b5bf9and3348be263d337201bd98e867f765b87be3f15666164c39763dc1267), WALLS.1. Records sa locate on `0x0800 + 0x5A × ID`; original directory image is on `4 × ID`. WALLS.1 link same index with change editora, nie with zaručenou runtime function.

Each record has 90 bytes. V this batch have all `extension_flag=0`, all bytes from `+0x04` to `+0x59` are zero and `+0x02` contains count frames. Different hashe frames prove different pixel data; without play game neurčujú exact visual effect nor kadenciu visible player.

| ID | Name according to WALLS.1 | SEQDEF | Image | Interval | Frames | Shared image with |
|---|---|---:|---:|---:|---:|---|
| `0x00` | Invalid (`NULL`) | `0x0800` | `0` | 0 | 1 | — |
| `0x01` | Dining Room - Plain (`WALL`) | `0x085A` | `0xBC00` | 0 | 1 | — |
| `0x02` | Dining Room - Small Picture (`WALL`) | `0x08B4` | `0xDC0A` | 0 | 1 | — |
| `0x03` | Dining Room - Sconces (`WALL`) | `0x090E` | `0xEC14` | 100 | 2 | — |
| `0x04` | Dining Room - Hutch (`WALL`) | `0x0968` | `0x12C28` | 100 | 2 | — |
| `0x05` | Dining Room - Large Picture (`WALL`) | `0x09C2` | `0x16C3C` | 100 | 2 | — |
| `0x06` | Dining Room - Window (`WALL`) | `0x0A1C` | `0x1AC50` | 0 | 1 | — |
| `0x07` | Dining Room - Curtains (`WALL`) | `0x0A76` | `0x1CC5A` | 0 | 1 | `0x70`, `0x71` |
| `0x08` | Dining Room - Panel R (`REVWALL`) | `0x0AD0` | `0x1EC64` | 0 | 1 | — |
| `0x09` | Dining Room - Panel L (`REVWALL`) | `0x0B2A` | `0x20C6E` | 0 | 1 | — |
| `0x0A` | Living Room - Plain (`WALL`) | `0x0B84` | `0x22C78` | 0 | 1 | — |
| `0x0B` | Living Room - Curtains (`WALL`) | `0x0BDE` | `0x24C82` | 0 | 1 | `0x72`, `0x73` |
| `0x0C` | Living Room - Window (`WALL`) | `0x0C38` | `0x26C8C` | 0 | 1 | — |
| `0x0D` | Living Room - Bookcase (`WALL`) | `0x0C92` | `0x28C96` | 0 | 1 | — |
| `0x0E` | Living Room - Fireplace (`WALL`) | `0x0CEC` | `0x2ACA0` | 150 | 8 | — |
| `0x0F` | Living Room - Panel Right (`REVWALL`) | `0x0D46` | `0x3ACF0` | 0 | 1 | — |

## Individual records

### `0x00` — Invalid (`NULL`)

- **Confirmed:** SEQDEF `0x0800`, image pointer `0`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0000`.
- **Confirmed:** image pointer is zero; no frame cannot z this items load. Value `frame_count=1` sama osebe does not create image.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `NULL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x01` — Dining Room - Plain (`WALL`)

- **Confirmed:** SEQDEF `0x085A`, image pointer `0xBC00`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0004`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `1a22402fd182`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x02` — Dining Room - Small Picture (`WALL`)

- **Confirmed:** SEQDEF `0x08B4`, image pointer `0xDC0A`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0008`.
- **Confirmed:** 1 decoded frames; rozmery `64x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `775fddaa9919`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x03` — Dining Room - Sconces (`WALL`)

- **Confirmed:** SEQDEF `0x090E`, image pointer `0xEC14`, interval `100`, count frames `2`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x000C`.
- **Confirmed:** 2 decoded frames; rozmery `128x64;128x64`, 2 different pixel obsahov. Shortened SHA-256 frames: `f6c2657a1bec, d6a9449e6cbd`. Check streamu: `OK`.
- **Derived:** item poskytuje animation with different frame; exact movement and condition playback require check calls v EXE and behu game.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x04` — Dining Room - Hutch (`WALL`)

- **Confirmed:** SEQDEF `0x0968`, image pointer `0x12C28`, interval `100`, count frames `2`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0010`.
- **Confirmed:** 2 decoded frames; rozmery `128x64;128x64`, 2 different pixel obsahov. Shortened SHA-256 frames: `93896ab0b121, ce1e0374346a`. Check streamu: `OK`.
- **Derived:** item poskytuje animation with different frame; exact movement and condition playback require check calls v EXE and behu game.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x05` — Dining Room - Large Picture (`WALL`)

- **Confirmed:** SEQDEF `0x09C2`, image pointer `0x16C3C`, interval `100`, count frames `2`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0014`.
- **Confirmed:** 2 decoded frames; rozmery `128x64;128x64`, 2 different pixel obsahov. Shortened SHA-256 frames: `9700ed1f6d19, 35f010e3fee1`. Check streamu: `OK`.
- **Derived:** item poskytuje animation with different frame; exact movement and condition playback require check calls v EXE and behu game.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x06` — Dining Room - Window (`WALL`)

- **Confirmed:** SEQDEF `0x0A1C`, image pointer `0x1AC50`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0018`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `43cc095eb5b4`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x07` — Dining Room - Curtains (`WALL`)

- **Confirmed:** SEQDEF `0x0A76`, image pointer `0x1CC5A`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x001C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `cdd48a121f10`. Check streamu: `OK`.
- **Confirmed:** same image pointer use also ID `0x70`, `0x71`. Their own SEQDEF records sa must assess separate.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x08` — Dining Room - Panel R (`REVWALL`)

- **Confirmed:** SEQDEF `0x0AD0`, image pointer `0x1EC64`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0020`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `18a700ee351f`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x09` — Dining Room - Panel L (`REVWALL`)

- **Confirmed:** SEQDEF `0x0B2A`, image pointer `0x20C6E`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0024`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `331aee54a929`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x0A` — Living Room - Plain (`WALL`)

- **Confirmed:** SEQDEF `0x0B84`, image pointer `0x22C78`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0028`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `b1ba18f1d9f1`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x0B` — Living Room - Curtains (`WALL`)

- **Confirmed:** SEQDEF `0x0BDE`, image pointer `0x24C82`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x002C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `284acd1af486`. Check streamu: `OK`.
- **Confirmed:** same image pointer use also ID `0x72`, `0x73`. Their own SEQDEF records sa must assess separate.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x0C` — Living Room - Window (`WALL`)

- **Confirmed:** SEQDEF `0x0C38`, image pointer `0x26C8C`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0030`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `4859da0c64a8`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x0D` — Living Room - Bookcase (`WALL`)

- **Confirmed:** SEQDEF `0x0C92`, image pointer `0x28C96`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0034`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `0f467ca54970`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x0E` — Living Room - Fireplace (`WALL`)

- **Confirmed:** SEQDEF `0x0CEC`, image pointer `0x2ACA0`, interval `150`, count frames `8`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x0038`.
- **Confirmed:** 8 decoded frames; rozmery `128x64;128x64;128x64;128x64;128x64;128x64;128x64;128x64`, 8 different pixel obsahov. Shortened SHA-256 frames: `e825afdb11c9, b49eb807fd23, d024e3200c55, 56d7ab763c0e, 730a968e3fd9, cdb36dee6e5c, 5b31aaea6db7, 20f2087ba5d1`. Check streamu: `OK`.
- **Derived:** item poskytuje animation with different frame; exact movement and condition playback require check calls v EXE and behu game.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `WALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

### `0x0F` — Living Room - Panel Right (`REVWALL`)

- **Confirmed:** SEQDEF `0x0D46`, image pointer `0x3ACF0`, interval `0`, count frames `1`, extension `0`; data arrays `+0x04..+0x59` are zero. Source: `IMG.1` on uvedenom offsete and directory `0x003C`.
- **Confirmed:** 1 decoded frames; rozmery `128x64`, 1 different pixel obsahov. Shortened SHA-256 frames: `ec22a8ed3b0c`. Check streamu: `OK`.
- **Derived:** this image stream does not have viac as jednu frame; behavior walls v hre can be controlled other stavom or selectorom.
- **So far undetermined:** specifically usage v MAP.1, game event and behavior across verziami. Designation `REVWALL` v `WALLS.1` samo o sebe nedokazuje playback this sequences.

## Notes k version and evidence

- According to previous static auditu is vzorec offset SEQDEF supported v Win16 1.10 and 1.8 also DOS 2.0. This batch checks directly IMG.1 and WALLS.1; priame comparison each next EXE still nebolo performed.
- `alias_ids` v source inventory use hexadecimal numbers **without** prefixu. For example `70,71` mean `0x70,0x71` (desiatkovo 112,113).
- Zero interval during single frame mean data interval 0, nie evidence vypnutej runtime animations. For `0x03–0x05` are two rozličné frames and interval 100; for `0x0E` eight rozličných frames and interval 150.
- Next batch follow on `IMG.1` wall `0x10–0x1F` and add occurrence v map, if is possible safely determine their code.