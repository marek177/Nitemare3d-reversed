# NITE3W: register adries and fields

**Range:** Win16 NITE3W build z binaries `nite3w(20260921-205703).exe`  
**SHA-256:** `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`  
**Date auditu:** 23. september 2026

## Zhrnutie

Register covers all **555 global `DAT_*` labelov**, **967 recognize dekompilovaných input functions** and **84 string labelov** z provided exportu `nite3w110.exe.c`. During global is teraz **105** adries assign k podporenému meaning or k doloženej structure; **450** remains explicitly open. Open items contain xref functions and ukážky výrazov, aby sa dali continue raw-assembly auditom.

This is complete **inventory adries v danom exporte**, nie tvrdenie, that all bytes programu already have známu function. `DAT_*`, `FUN_*` and `s_*` are analytické names z Ghidra/exportu, nie original symbol autora. Type dekompilátora are only hinty. During unknown field sa meaning nevymýšľa.

## address konvencie and segments

Write `1048:4C4A` mean Ghidra memory block `1048`, offset `4C4A`. Column `ne_segment_ordinal` v CSV prepája blocks with NE table. Is not to prenositeľná far-pointer selector value before NE relocation/fixup.

| Ghidra block | NE segment | Type and hranice |
|---|---:|---|
| `1000`, `1008`, `1010`, `1018` | 1–4 | Kódové segment. file offset and stored length are v `nite3w_ne_segment_map.csv`. |
| `1030` | 7 | Initialize data, file offset `0x2A9C0`, length `0x1646`. |
| `1040` | 9 | Zero-fill runtime arena, available to offset `0xC69D`; end allocate `0xC69E`. |
| `1048` | 10 | Initialize auto-data/strings, file offset `0x2C040`, length `0x8EAE`; valid offset končia before `0x8EAE`. |

**Important correction:** cache from offset `A65E` lies v runtime segment 9, therefore `1040:A65E`, nie v segment 10 (`1048`). Holý write `DAT_A65E` is nejednoznačný and address `1048:A65E` is mimo length segment 10. `USER.SAV+0xD5A3` uchováva 64 bytes cache z `1040:A65E`.

## Main globally addresses

### Svet and runtime counters

| Address | Meaning | Opora |
|---|---|---|
| `1040:0000` | Count párových wall/door controller records; table `1040:9DD6`, 64 × 22 B. | read/writes `FUN_1010_14A8`, `1296`, `1D4E`. |
| `1040:0002` | Count class-3 group-motion records; table `1040:A356`, 32 × 22 B. | `FUN_1010_16D6`, `12E8`, save/load. |
| `1040:0004` | Count push records; table `1040:A616`, 12 × 6 B. | `FUN_1010_181C`, `2210`. |
| `1040:0006` | Start 1,000 VEC records × 28 B. | Stride, loop limity and save length. |
| `1040:6D66` | Start 350 OBJECT records × 28 B. | `7E58`, entity loops and save length. |
| `1040:93AE` | Start 100 GUARD records × 26 B. | `7E5E`, guard loops and save length. |
| `1040:A65E–A69D` | 64-byte one-shot guard-wake cache. | Reset, selector read/write and USER.SAV round-trip. |
| `1040:A69E–C69D` | 64×64 mapa after dvoch bajtoch on bunku. | End sa zhoduje with NE segment 9 minAlloc `0xC69E`. |
| `1048:7E56` | Count VEC records (max 1,000). | `FUN_1010_4C8A`, `FUN_1018_3430`, `FUN_1018_4046`. |
| `1048:7E58` | Count OBJECT records (max 350). | Loops from `1040:6D66`, `FUN_1010_4C8A`. |
| `1048:7E5E` | Count GUARD records (max 100). | Loops from `1040:93AE`, `FUN_1010_847E`. |

### Mapa and tables

| Address | Meaning |
|---|---|
| `1048:8194` | MAP header: 16-bit count levelov. |
| `1048:8196–8295` | 256-byte wall ID → class table. |
| `1048:8296–8395` | 256-byte object ID → class table. |
| `1048:7E94–7F93` | 256-byte wall-property table. |
| `1048:7F94–8093` | 256-byte object-property table. |
| `1048:8094–8193` | 256-byte color/palette remap table. |
| `1048:7E64`, `7E74`, `7E84` | Buffery for zostavené `map.N`, `img.N`, `demo.N` path. |

### Player, konfigurácia and weapon

| Address | Meaning |
|---|---|
| `1048:4BD4–4BE7` | Exact 20-byte CONFIG.SAV block: render width, window size, citlivosti, audio flags/call and four cheat flags. Detail is v `nite3w_runtime_field_layout.csv`. |
| `1048:4BE8–4C45` | 94-byte zmiešaný player/game save block; known internal arrays are below and other remain open. |
| `1048:4BF6`, `4BF8` | X/Y player coordinates. |
| `1048:4C14` | Difficulty use damage paths. |
| `1048:4C1D` | HP player. |
| `1048:4C1F`, `4C20`, `4C44` | Ammo for weapon selectors 2, 0 and 1. Selector 3 does not have normal ammo branch v preskúmanom helperi. |
| `1048:4C23` | current weapon selector. |
| `1048:4C29` | Credential/card bitmask. |
| `1048:4C2A` | Weapon-availability bitmask. |
| `1048:4C46`, `4C48` | Signed fixed-point X/Y directional komponenty. |
| `1048:4C4A–4D99` | 8 × 42 B projectile slotov, end `4D9A` exkluzívne. |

### Input, DEMO and game events

| Address | Meaning |
|---|---|
| `1048:0108`, `010C` | current and previous key-event byte for DEMO record. |
| `1048:010A` | Handle open DEMO file. |
| `1048:3756`, `3757` | Main 16-bit input mask and second modifikačný byte. |
| `1048:375E`, `375F`, `3762`, `3766` | Last DEMO event/maska/time for recording; byte `3761` is not v exporte usage. |
| `1048:46B4` | Game active flag. |
| `1048:46B6` | Main game/UI state word, nie boolean. |
| `1048:46B8` | DEMO automat stavov 1–5. |
| `1048:51A4–51AB` | Eight event bytes: panel mask, Cannon gate, story latch, one-shot flags and dark-event flag. `51A9/51AA` are setované/stored, but reader sa v this exporte did not find. |

### Projection and renderer

| Address | Meaning |
|---|---|
| `1048:3A72` | Projection faktor. |
| `1048:53DC` | 32-bit loop/generation counter; jednotka is not známa as ms. |
| `1048:53E4`, `53E6` | Left/right projection boundary. |
| `1048:53EE`, `53F0` | Vertikálny stred and projection base/horizon. |
| `1048:53F2` | Kalibrovaný min simulation/render interval, minimálne 40. |
| `1048:53F6`, `53F8`, `53FA` | movement step, turn step and substep limit `2×53F6`. |
| `1048:53FE` | 320 column × 4 B far-pointer owner buffer. |
| `1048:5E7E`, `5E88` | Count visible spans and array 50 × 20 B. |
| `1048:697A/697C/697E/6980` | Counts four VEC orientačných list, max 333 each. Lists začínajú `6982`, `6EB6`, `73EA`, `791E`. |
| `1048:51AC`, `4744` | 8-byte wall and OBJECT/GUARD animation cache descriptors; counts v `7E5A` and `7E5C`. |
| `1048:7E60`, `7E62`, `7E63` | Shade index and two fill/color bytes. |

Argumenty command row `-b/-c/-d/-e/-f/-l/-o/-p/-r/-s/-w` are rozpísané for each global v CSV. Findings o `-s` have status OPEN: v audited version sa value sets, but neskôr sa nečíta.

## Runtime records: arrays after offsetoch

`nite3w_runtime_field_layout.csv` contains each known array also unknown range. Najdôležitejšie rozmery are:

| Record | Base | Capacity × stride | Zhrnutie |
|---|---|---:|---|
| VEC | `1040:0006` | 1,000 × 28 B | Wall edge, flags, orientation, world endpoints and projected endpoints. |
| OBJECT | `1040:6D66` | 350 × 28 B | Class-dependent entity; embedded projectile variant has animation fields and map pointer. |
| GUARD | `1040:93AE` | 100 × 26 B | Timer, strategy/stavy, HP, facing, perception and movement. |
| Paired wall/door | `1040:9DD6` | 64 × 22 B | Far pointers, controller state/timer and target coordinates. |
| Class-3 group motion | `1040:A356` | 32 × 22 B | Four component pointers, cell pointer, phase. |
| Push | `1040:A616` | 12 × 6 B | Entity index, signed motion components, eight-step counter. |
| Projectile | `1048:4C4A` | 8 × 42 B | 14 B Bresenham/motion state + 28 B embedded OBJECT. |
| Visible span | `1048:5E88` | 50 × 20 B | VEC pointer, screen endpoints, 16.16 slope and interpolation. |

### Base offset in vloženom projectile OBJECT

Projectile table uses offset from start 42-byte slotu. Internal OBJECT table uses offset from addresses `slot+0x0E`, ktorú allocator passes to `FUN_1010_CC7C`. Therefore `slot+0x11` = `OBJECT+0x03` (frame), `slot+0x12` = `OBJECT+0x04` (sequence selector), `slot+0x20` = `OBJECT+0x12` (world Y), `slot+0x16…+0x19` = `OBJECT+0x08…+0x0B` (32-bit animation deadline) and `slot+0x26…+0x27` = `OBJECT+0x18` (clipped projected screen row consumed by damage). These arrays sa **neprekrývajú**. `GUARD+0x12` is directional sprite/sequence-cache key; damage writes 8 as invalidáciu.

## Coverage, hranice and open items

- All `DAT_*` labelov z exportu is v global CSV. During each row are preserved heuristic read/write counts, functional xrefs and sample expressions. These counts are not raw-instruction proof.
- All recognize `FUN_*` entrypointov z exportu is v `nite3w_function_address_index.csv`, including signatúry and row source exportu, if sa dal determine.
- String index decode bytes directly z file offset `0x2C040 + segment-10 offset`, nie z Ghidra labelu. Kódová stránka CP1252 is prezentačný decode; column raw hex preserves original bytes.
- Segment 9 runtime arrays are referencované v exporte also as literal offset (`0x6D66`, `0x93AE` atď.), therefore their cannot zredukovať only on `DAT_*` names.
- Remain open predovšetkým neklasifikované globals, other VEC/OBJECT/GUARD bytes, exact internal 94-byte save block, `51A9/51AA`, DEMO record byte `+3`, time jednotka `53DC`, runtime current `OBJECT+0x18` during projectile hit and DOS projection/cache parity. Arrays `OBJECT+0x12/+0x18` and `GUARD+0x12` are static named v `Nite3W_OBJECT_GUARD_field_read_write_closure_2026-09-23.md`.
- Functional meaning are scoped on this hash-identify Win16 build version. Neprenášať automaticky on DOS nor other NITE3W versions.

## Files

- `nite3w_global_address_register.csv`: each global label and its xrefy/meaning/open questions.
- `nite3w_runtime_field_layout.csv`: arrays VEC, OBJECT, GUARD, door/group/push, projectile, visible span, DEMO, CONFIG.SAV and USER.SAV.
- `nite3w_function_address_index.csv`: all dekompilované function entry point addresses.
- `nite3w_string_address_index.csv`: string symbol, segment and file offset, raw bytes and decode text.
- `nite3w_ne_segment_map.csv`: Ghidra blocks relative to NE segment ordinals and file boundary.