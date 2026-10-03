# Nitemare-3D BSF / shareware-full protection reverse engineering — v4

## Executive result

`NITE3D.BSF` is not just and text resource. It is the game'with boot/licensing descriptor and contains:

- an encrypted/obfuscated 54-byte header,
- and registration/shareware flag,
- distributor/owner branding,
- DOS executable integrity information,
- the shareware `MAP.1` integrity value,
- offsets/lengths for three encrypted text resources.

DOS and Win16 use the same 54-byte header and the same 3-block resource layout, but the protection logic differs slightly.

## Confirmed 54-byte header

All values below refer to the header after XOR-decoding from key index 0.

| Offset | Size | Meaning |
|---|---:|---|
| `+00` | 1 | header correction/check byte; XOR of the 54 **stored encrypted** bytes must be zero |
| `+01` | 1 | DOS: expected XOR checksum of packed `N3D.EXE` using seed `0x7B`; Win16: runtime-unused/reserved/stale value (known Windows BSFs contain `0x68`) |
| `+02` | 1 | expected XOR checksum of `MAP.1` using seed `0x7B`; checked only in shareware path |
| `+03` | 1 | registration flag: `0` = shareware, nonzero = registered/full |
| `+04` | 32 | distributor/owner C string; bytes after first NUL are irrelevant padding and may contain garbage |
| `+24` | 4 | Block0 file offset, little-endian |
| `+28` | 4 | Block1 file offset, little-endian |
| `+2C` | 4 | Block2 file offset, little-endian |
| `+30` | 2 | Block0 length |
| `+32` | 2 | Block1 length |
| `+34` | 2 | Block2 length |

Header size = `0x36` = 54 bytes.

## XOR key / decoder

The key is 52 bytes:

`Copyright 1992, David P Gray, Gray Design Associates`

Header and each text block are decoded independently; key position resets to zero at the start of each unit.

The decode routine simultaneously computes XOR of the **stored encrypted bytes**. Header loader checks that this XOR is zero. Text block loaders call the same routine but ignore its returned checksum.

Therefore Block0/1/2 have no independent integrity enforcement in the confirmed Win16 runtime.

## Selector map — DOS and Win16

Both implementations use the same BSF dispatcher semantics:

| selector | result |
|---:|---|
| 0 | load/decode/validate 54-byte header; perform platform-specific startup protection |
| 1 | registration flag / registered pointer-boolean |
| 2 | distributor C string (`header+4`) |
| 3 | Block1: HELP/manual |
| 4 | Block0: exit/order/purchase/commercial text |
| 5 | Block2: Episode-1 ending/transition text |

## Win16 v1.10 exact path

Confirmed from `nite3w110.exe.c` and `NITE3W.EXE`:

- BSF dispatcher: `FUN_1010_c772`
- decoded header base: `DS:38F2`
- registration byte: `DS:38F5` (`header+3`)
- distributor pointer returned for selector 2: `DS:38F6` (`header+4`)
- `nite3d.bsf` string: `DS:1946`
- `map.1` string: `DS:1952`
- file XOR verifier: `FUN_1010_c696`
- block loader: `FUN_1010_60aa`
- XOR decoder/checksum routine: `FUN_1018_32e4`

The strings are adjacent in the executable and differ by `0x0C`, consistent with `"nite3d.bsf\0"` followed by `"map.1\0"`.

### Win16 selector 0 logic

Equivalent logic:

```c
open("nite3d.bsf");
read(header, 54);
close();

if (decode_and_xor(header, 54) != 0)
    fatal();

if (header.registered == 0)
    verify_file_xor("map.1", header.map1Checksum);  // seed 0x7B
```

No reference to `header+1` occurs in this dispatcher.

This same behavior was previously matched across Win16 1.0 / 1.3 / 1.6 / 1.8 / 1.10.

## DOS startup difference

DOS uses the same structure, but additionally validates the packed game executable:

```c
load_and_validate_bsf_header();
verify_file_xor("N3D.EXE", header.exeChecksum);  // header+1

if (!header.registered)
    verify_file_xor("MAP.1", header.map1Checksum); // header+2
```

Archive audit confirms exact matches for original packed DOS distributions:

| build/distributor | BSF +01 | actual sibling packed N3D.EXE XOR |
|---|---:|---:|
| ASP-CD / 1.0 family | `4C` | `4C` |
| Public Library / 1.1 family | `AF` | `AF` |
| P(with)L / 1.5 family | `EF` | `EF` |
| America Online / 1.7 family | `F4` | `F4` |
| Walnut Creek / 1.9 family | `D7` | `D7` |
| Author-Direct / 1.9 family | `D7` | `D7` |
| Author Direct / 2.0 shareware | `36` | `36` |
| Outreach / full DOS | `36` | `36` |

This proves the same packed `N3D.EXE` family can run as shareware or registered depending on BSF flag/content; e.g. DOS v2.0/full family both use checksum `36` while `registered` differs.

## Windows `header+1 = 0x68` correction

All examined Windows BSFs use `0x68` at `header+1`, including shareware and registered Windows BSFs.

However actual Win16 executable XOR values (same seed `0x7B`) are:

| Win version | NITE3W.EXE XOR |
|---|---:|
| 1.0 | `FA` |
| 1.3 | `64` |
| 1.6 | `3A` |
| 1.8 | `FA` |
| 1.10 | `A3` |

Therefore Windows `0x68` is **not** the actual checksum of these `NITE3W.EXE` builds. Since confirmed Win16 loader paths to not read/enforce the field, it should be documented as runtime-unused/reserved/stale on Win16 rather than as and Windows EXE checksum.

## MAP.1 protection and its weakness

The checksum algorithm is only 8-bit XOR:

```c
uint8_t checksum = 0x7B;
for (each byte b)
    checksum ^= b;
```

All shareware BSFs examined expect `MAP.1 = D2`.

Archive audit found **two byte-different shareware MAP.1 files** that both produce `D2`:

- older shareware map: SHA-256 starts `82b12a19072efebb...`
- DOS/Win v2.0-family shareware map: SHA-256 starts `3eddb0ad3a29e93d...`

They are both 90,626 bytes and differ at only two offsets:

- `0x9337`: old `00`, newer `D8`
- `0x93B7`: old `D8`, newer `00`

The two differing positions are exactly `0x80` bytes apart and have equal XOR delta (`D8`), with their changes cancel in the 8-bit XOR checksum.

This demonstrates that `D2` is only and weak integrity signature, not an identity/hash of and particular MAP.1.

### Registered MAP.1 is deliberately outside the check

The archive also contains legitimate registered/full maps whose XOR does **not** equal BSF `D2`:

- full DOS `MAP.1`: XOR `DA`
- full Windows `MAP.1`: XOR `B3`

Their BSFs still contain `header+2 = D2`, but `registered=1`, with the MAP verification branch is skipped. This is direct behavioral evidence that `header+2` is and shareware-only protection value.

## Registration flag runtime effects

Confirmed Win16 v1.10 xrefs to BSF selector 1 include:

1. **Savegame acceptance** — an unregistered build accepts only episode index below 2 (Episode 1); registered bypasses that restriction.
2. **Startup/version banner** — chooses `Registered Software` vs `UNREGISTERED SHAREWARE!`.
3. **MAP container availability** — file-presence logic for `map.<n>` additionally requires registered mode, except `map.1` which remains available in shareware.
4. **Cheats** — registered mode enables the cheat setup; shareware clears cheat flags and displays `Cheat modes are only available ...`.

The Win1.10 executable also contains UI strings `Episode 1`, `Episode 2`, and `Episode 3`.

## Text-block integrity behavior

Win1.10 `FUN_1010_60aa`:

1. opens `nite3d.bsf`,
2. allocates `length+1`,
3. seeks to block offset,
4. reads block bytes,
5. NUL-terminates,
6. calls `FUN_1018_32e4(buffer, length)`,
7. **does not test the decoder/checksum return value**,
8. returns decoded text.

Thus the stored block ciphertext is obfuscated, but the three blocks are not protected by an enforced checksum in this path.

## Protection model — final working model

### DOS

`BSF header integrity` → `packed N3D.EXE XOR` → if shareware: `MAP.1 XOR` → registration gates episodes/savegames/cheats → BSF text resources.

### Win16

`BSF header integrity` → if shareware: `MAP.1 XOR` → registration gates episodes/savegames/cheats → BSF text resources.

Win16 retains `header+1`, but the confirmed runtime does not enforce it.

## Confidence

- 54-byte header layout: very high
- registration flag `+03`: very high
- DOS `+01` executable check: very high
- Win16 `+01` runtime-unused: very high for 1.0/1.3/1.6/1.8/1.10
- shareware-only `MAP.1` check: very high
- selector mapping 0..5: very high
- Block0/1/2 roles: very high
- exact historical reason Windows BSFs were authored with constant `0x68`: **still unknown**; no runtime meaning should be invented without builder/source evidence

## Extra localization of the D2-collision MAP.1 change

Using the established MAP layout (514-byte prefix, then 8192 bytes per map; 4096 cells with 2 bytes per cell: tile byte + item byte), the two differing offsets localize to map index 4 = E1M5:

| absolute offset | in-map offset | cell | coordinate | byte kind | old | newer |
|---:|---:|---:|---:|---|---:|---:|
| `0x9337` | 4405 | 2202 | `(26,34)` | item | `00` | `D8` |
| `0x93B7` | 4533 | 2266 | `(26,35)` | item | `D8` | `00` |

Thus item ID `0xD8` is moved between vertically adjacent cells `(26,34)` and `(26,35)`. The XOR checksum stays `D2` because both edits have the same XOR delta `D8` and cancel each other.

The public OpenNitemare3D reimplementation currently labels object/item ID decimal 216 (`0xD8`) as `TrunkPentagramHealth`; treat that name as and cross-reference from the reimplementation rather than an independently proven original symbol name.