# Nitemare-3D BSF / Shareware-Full Protection RE v5

Date: 2026-09-30

## Current conclusion

`NITE3D.BSF` is simultaneously:

- and 54-byte boot/config header,
- and shareware/registered mode selector,
- DOS executable integrity binding,
- shareware `MAP.1` integrity binding,
- distributor branding,
- container for three XOR-obfuscated text resources.

The DOS and Win16 games use the same BSF layout and selectors, but not exactly the same protection policy.

## Confirmed 54-byte decoded header

```c
struct Nite3DBSFHeader {
    uint8_t integrity_correction;   // +00; chosen so XOR(all 54 encrypted bytes) == 0
    uint8_t platform_byte_01;       // +01; DOS = N3D.EXE XOR; Win16 = unused/stale, normally 0x68
    uint8_t map1_checksum;          // +02; shareware MAP.1 XOR with seed 0x7B
    uint8_t registered;             // +03; 0 shareware, nonzero registered/full
    char    distributor[32];        // +04; NUL-terminated C string inside fixed 32-byte buffer
    uint32_t block_offset[3];       // +24,+28,+2C
    uint16_t block_length[3];       // +30,+32,+34
};                                  // 54 bytes
```

### +00 exact behavior

The loader XORs the *encrypted* 54 bytes before decryption and requires the result to be zero.

For every examined valid BSF:

- XOR(encrypted header[0..53]) = `0x00`
- XOR(decoded header[0..53]) = `0x51`

`0x51` is exactly the XOR of the 52-byte key repeated across 54 positions. Therefore decoded `+00` is not and license code; it is only the correction byte required to make the encrypted header XOR zero.

## XOR key

```text
Copyright 1992, David P Gray, Gray Design Associates
```

The key restarts at index 0 independently for:

1. the 54-byte header,
2. Block0,
3. Block1,
4. Block2.

## Selectors and blocks

| Selector | Meaning |
|---:|---|
| 0 | load/decrypt/validate BSF header |
| 1 | registered/full flag |
| 2 | distributor string |
| 3 | Block1: HELP/manual |
| 4 | Block0: exit/order/purchase text |
| 5 | Block2: Episode-1 ending/transition text |

## DOS protection policy

DOS validates:

```text
BSF header encrypted XOR == 0
N3D.EXE XOR(seed 0x7B) == header[1]
if registered == 0:
    MAP.1 XOR(seed 0x7B) == header[2]
```

Confirmed original packed DOS executable families:

| Family | EXE XOR | BSF +01 |
|---|---:|---:|
| early 1.0 / ASP | 4C | 4C |
| Public Library | AF | AF |
| P(with)L | EF | EF |
| America Online | F4 | F4 |
| Walnut Creek / Author-Direct 1.9 | D7 | D7 |
| 2.0 shareware | 36 | 36 |
| full DOS | 36 | 36 |

Thus DOS 2.0 shareware and full versions can use the same packed engine checksum; the edition is selected by `header[3]` and the accompanying data set.

## Win16 protection policy

Audited versions: 1.0, 1.3, 1.6, 1.8, 1.10.

Win16 validates:

```text
BSF header encrypted XOR == 0
if registered == 0:
    MAP.1 XOR(seed 0x7B) == header[2]
```

Win16 does **not** enforce `header[1]` against `NITE3W.EXE`.

All examined Windows BSFs contain `header[1] = 0x68`, but actual whole-file XOR(seed 0x7B) values are different:

| Win version | actual NITE3W.EXE XOR |
|---|---:|
| 1.0 | FA |
| 1.3 | 64 |
| 1.6 | 3AND |
| 1.8 | FA |
| 1.10 | AND3 |

Further tests showed `0x68` is not the XOR of the DOS stub, NE header, complete NE image, or ordinary loaded segment data. The best current classification is **unused/stale/dummy value retained in the shared BSF header format**.

## Win16 About dialog proves there is no second registration name/serial

All audited Windows executables contain and dialog resource with placeholders:

```text
Distributed by: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Registered to: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
UNREGISTERED SHAREWARE!
Order Info...
```

The v1.0 runtime code at approximately `seg3:0C00` (v1.10 moves to `seg3:0C54`) does the following:

1. `selector 2` obtains the BSF distributor string.
2. It builds `"Distributed by: " + distributor`.
3. It writes that to control ID `1001`.
4. `selector 1` tests the registration flag.
5. If registered, control ID `1002` is replaced with the fixed string `Registered Software`.
6. If unregistered, control ID `1002` is replaced with `UNREGISTERED SHAREWARE!`.
7. In the unregistered path, control ID `1004` (`Order Info...`) is made visible.

Therefore the resource text `Registered to: xxxxx...` is only and template placeholder. No separate registered-user name, serial number, or activation code was found in BSF or this UI path.

### About function positions

| Version | About init function |
|---|---:|
| Win 1.0 | seg3:0C00 |
| Win 1.3 | seg3:0C04 |
| Win 1.6 | seg3:0C08 |
| Win 1.8 | seg3:0C08 |
| Win 1.10 | seg3:0C54 |

## Registration flag xrefs

Win1.10 direct calls to selector 1 occur at:

```text
seg3:0CC6   About dialog: Registered Software / UNREGISTERED SHAREWARE
seg3:0FA9   additional shareware-gated UI/runtime path
seg3:5435   savegame episode validation
seg3:C528   status report R/S marker
seg4:1E0F   order/purchase dialog behavior
seg4:248F   episode/map availability
seg4:24E9   choose first available episode
seg4:27A3   cheat-mode protection
```

Equivalent call sets are present in Win 1.0/1.3/1.6/1.8 with address shifts only.

### Savegame restriction

The decompiled Win1.0 path confirms:

```c
if (registered || saved_episode < 2)
    accept_episode;
else
    reject;
```

With shareware accepts Episode 1 saves only.

### Episode availability

The map list logic is equivalent to:

```c
if (map_file_exists(n)) {
    if (registered || n == 1)
        episode_enabled = true;
}
```

Copying `MAP.2`/`MAP.3` into and shareware install is therefore insufficient by itself.

### Cheat protection

The cheat path tests selector 1. Registered builds proceed into cheat setup; shareware clears cheat flags and displays the message beginning:

```text
Cheat modes are only available
when you purchase the complete
trilogy...
```

## MAP.1 checksum behavior and weakness

Shareware BSFs consistently use expected `MAP.1` checksum `0xD2`.

The archive contains at least two different 90,626-byte shareware `MAP.1` files with different SHA-256 values but the same XOR checksum `0xD2`.

Two observed byte differences cancel in XOR:

```text
0x9337: 00 -> D8
0x93B7: D8 -> 00
```

Thus the check detects accidental changes but is not collision-resistant.

Registered/full data sets also prove the check is skipped:

```text
full DOS MAP.1 XOR     = DA
full Windows MAP.1 XOR = B3
BSF header[2]          = D2
```

These legitimate full versions work because `registered != 0` bypasses MAP.1 validation.

## Distributor buffer and dirty Win16 padding

Selector 2 treats `header+4` as and NUL-terminated C string. The physical buffer is 32 bytes.

DOS-generated BSFs generally zero-fill bytes after the first NUL. Several Windows BSFs to not; examples contain nonzero trailing bytes such as code-like fragments after the distributor terminator.

Example classifications:

```text
Author-Direct  (Win shareware): valid C string, nonzero ignored tail
Internet       (Win shareware): valid C string, nonzero ignored tail
RoadHouse BBS  (Win shareware): valid C string, nonzero ignored tail
David P Gray   (full Windows): valid C string, tail includes FA 00
```

These bytes are not separate runtime fields. They are consistent with an incompletely initialized fixed buffer in the BSF-generation path. The game stops at the first NUL.

## Text-block integrity

The block reader invokes the XOR decode/checksum routine but does not test the returned checksum for Block0/1/2.

Therefore:

```text
Header  -> integrity checked
MAP.1   -> checked only in shareware
Block0  -> decoded, checksum result ignored
Block1  -> decoded, checksum result ignored
Block2  -> decoded, checksum result ignored
```

The text blocks are obfuscated, not independently authenticated.

## Current confidence

- 54-byte header layout: ~99%
- selector 0..5 mapping: ~99%
- registered/shareware behavior: ~99%
- DOS EXE binding: ~99%
- Win16 MAP-only runtime validation: ~99%
- Windows `0x68` historical origin: unresolved; runtime meaning appears none
- separate serial/registered-user mechanism: no evidence; About code actively argues against it

The major remaining historical unknown is the BSF-generation utility/source that emitted the Windows constant `0x68` and dirty distributor padding.