# Nitemare-3D NITE3D.BSF / DOS + Win16 protection reverse engineering — v3

## Main conclusion

`NITE3D.BSF` is and common DOS/Win16 boot/license/resource format. Both platforms use the same 54-byte encrypted header and the same three encrypted text blocks. The registration flag at decoded header `+03` controls shareware vs registered/full behavior.

AND key platform difference is now confirmed:

- **DOS** uses `BSF[+01]` as the weak XOR checksum for `N3D.EXE`, and in shareware mode uses `BSF[+02]` for `MAP.1`.
- **Win16** uses the header integrity check and, in shareware mode, `BSF[+02]` for `MAP.1`, but no genuine code reference to decoded header `+01` was found in Win16 v1.0/v1.3/v1.6/v1.8/v1.10. In Win16 this byte is retained for format compatibility but is effectively unused by the loader.

This corrects the earlier over-generalization that the EXE checksum is enforced on both platforms.

## Common 54-byte decoded header

| Offset | Size | Meaning |
|---:|---:|---|
| `+00` | 1 | header correction/checksum byte; XOR of the 54 stored encrypted bytes must be zero |
| `+01` | 1 | expected DOS `N3D.EXE` XOR checksum, seed `0x7B`; unused by confirmed Win16 loader paths |
| `+02` | 1 | expected `MAP.1` XOR checksum, seed `0x7B` |
| `+03` | 1 | registration flag: `0` shareware/unregistered, nonzero registered/full |
| `+04` | 32 | distributor/owner string |
| `+24/+28/+2C` | 4 each | Block0/1/2 file offsets |
| `+30/+32/+34` | 2 each | Block0/1/2 lengths |

XOR key (52 bytes):

`Copyright 1992, David P Gray, Gray Design Associates`

Header and each text block restart the XOR key from index 0.

## Block/selector mapping — common DOS and Win16

| selector | result |
|---:|---|
| `0` | load/decode/validate 54-byte header |
| `1` | registered test/pointer |
| `2` | distributor string |
| `3` | Block1 = HELP/manual |
| `4` | Block0 = exit/order/purchase/commercial text |
| `5` | Block2 = Episode-1 ending/transition text |

The Win16 loader switch maps the fields identically to DOS:

- selector 3 -> offset `header+0x28`, length `header+0x32`
- selector 4 -> offset `header+0x24`, length `header+0x30`
- selector 5 -> offset `header+0x2C`, length `header+0x34`

## Win16 version matrix

Addresses are segment-relative offsets from the analyzed NE executables.

| Win version | BSF dispatcher | header DS | registered | distributor | EXE byte | MAP byte | XOR decoder | key DS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.0 | seg3:`C544` | `3836` | `3839` | `383A` | `3837` | `3838` | seg4:`2F0E` | `1EA4` |
| 1.3 | seg3:`C550` | `3836` | `3839` | `383A` | `3837` | `3838` | seg4:`2FB2` | `1EA4` |
| 1.6 | seg3:`C6C4` | `38EE` | `38F1` | `38F2` | `38EF` | `38F0` | seg4:`3222` | `1F5C` |
| 1.8 | seg3:`C6C4` | `38EE` | `38F1` | `38F2` | `38EF` | `38F0` | seg4:`32EC` | `1F5C` |
| 1.10 | seg3:`C772` | `38F2` | `38F5` | `38F6` | `38F3` | `38F4` | seg4:`32E4` | `1F60` |

Block fields are always `header+24/+28/+2C` and `header+30/+32/+34`.

### Decoder identity

The Win16 XOR routine is 62 bytes in all five versions. After normalizing only the immediate address of the key string, its bytes are **identical in v1.0, v1.3, v1.6, v1.8 and v1.10**.

Core behavior:

```c
uint8_t decode(uint8_t *p, uint16_t len) {
    uint8_t check = 0;
    for (uint16_t i = 0; i < len; ++i) {
        check ^= p[i];
        p[i] ^= key[i % 52];
    }
    return check;
}
```

## Win16 selector 0

The v1.0 decompilation and matching machine-code structure in all later Win16 versions show:

```c
open("nite3d.bsf");
read(header, 54);
close();

if (decode(header, 54) != 0)
    fatal_error();

if (header.registered == 0)
    verify_xor_file("map.1", header.map1Checksum);
```

The Win16 file verifier uses the same weak XOR seed `0x7B` scheme.

### Important Win16 EXE-check result

For each analyzed Win16 version, the code references decoded `header+02` (MAP checksum) and `header+03` (registered flag). No genuine memory access to `header+01` was found. AND raw `38EF` occurrence in Win v1.8 resolves to bytes inside and far-call operand, not and read of `header+01`.

Therefore the Win loader does **not** reproduce the DOS self-EXE checksum gate.

## Win16 registered UI branch

In Win v1.0, startup UI calls selector 1. Machine code selects:

- selector 1 non-NULL -> string `Registered Software`
- selector 1 NULL -> string `UNREGISTERED SHAREWARE!`

Thus BSF registration state is surfaced directly as edition branding.

## Win16 indirect text viewer closes selectors 3 and 5

Win16 has and generic page/text viewer wrapper. It forwards and selector from its argument at `[BP+8]` to the BSF dispatcher.

Wrapper locations:

| version | wrapper | dynamic dispatcher call |
|---|---:|---:|
| 1.0 | seg4:`15C0` | `15CF` |
| 1.3 | seg4:`1632` | `1641` |
| 1.6 | seg4:`1874` | `1883` |
| 1.8 | seg4:`193E` | `194D` |
| 1.10 | seg4:`19A6` | `19B5` |

Confirmed selector values passed to this wrapper include `3` and `5`.

### selector 3 — HELP/manual

Examples from Win v1.0 include packed word arguments equivalent to selector 3:

- seg3:`0D74` call path -> selector 3
- seg3:`96B8` call path -> selector 3; decompilation shows and key/event path calling `FUN_1018_15C0(0x10, 0x80003)`
- seg4:`257A` -> selector 3

The decoded Block1 content is the in-game manual/help resource, consistent with these call paths.

### selector 5 — Episode-1 ending

Win v1.0 seg3:`D9C1` contains:

```asm
66 68 05 00 07 00    pushl 00070005h
6A 10                push 0010h
9A C0 15 ...         call text_viewer
```

With the wrapper'with selector at `[BP+8]`, this supplies selector `5`.

The call sits in an end/post-game state machine (`DAT_...45F6` dispatch and related state flags), matching decoded Block2'with Episode-1 ending/transition text.

The equivalent selector-5 pattern persists in v1.3/v1.6/v1.8/v1.10 at the correspondingly shifted call sites.

## Win16 selector 4 — order/purchase block

Win v1.0 has an otherwise poorly recovered small function beginning around seg4:`1A24`:

```asm
enter 4,0
push si
push 4
call BSF_dispatcher
...
```

It receives the Block0 pointer, invokes and Windows message box/dialog flow using the caption `Nitemare-3D for Windows V1.0`, checks for response `6`, and then frees the block. This is consistent with Block0'with decoded order/purchase text in shareware and commercial/thank-you text in registered BSFs.

Equivalent selector-4 calls exist in all later Win16 versions.

## Registration-dependent behavior confirmed in Win16

The v1.0 decompilation exposes selector-1 calls in several independent systems:

1. **Startup branding** — `Registered Software` vs `UNREGISTERED SHAREWARE!`.
2. **Savegame validation** — higher-episode save state is accepted only through the registered path.
3. **Episode enumeration/availability** — higher episode entries require registered mode; Episode 1 remains available in shareware.
4. **Episode selection** — another path repeats the registered gate.
5. **Cheats** — unregistered path clears cheat state and displays: `Cheat modes are only available when you purchase the complete trilogy...`.
6. **BSF order/help/end text selection** through selectors 3/4/5.

These patterns are structurally preserved across the five Win16 executables.

## Supplied BSF population

22 supplied BSF samples were decoded successfully.

Observed registration/checksum families:

- early shareware EXE checksum families: `4C`, `AF`, `EF`, `F4`, `D7`
- later shareware family: predominantly `68`
- registered/full families observed: `36` and `68`
- **all 22 samples have `MAP.1` checksum `D2`**

Examples:

- `ASP-CD`: shareware, EXE `4C`, MAP `D2`
- `Public (software) Library`: shareware, EXE `AF` or later `68`, MAP `D2`
- `P(s)L`: shareware, EXE `EF`, MAP `D2`
- `America Online`: shareware, EXE `F4`, MAP `D2`
- `Walnut Creek`: shareware, EXE `D7` or later `68`, MAP `D2`
- `Author Direct`: shareware, families `36` and `68`
- `Outreach Communications Corp`: registered/full, EXE field `36`
- `David P Gray`: registered/full, EXE field `68`

The identical `D2` value is consistent with one stable protected Episode-1 `MAP.1` across these distribution variants.

## Protection model, revised

### DOS

```text
BSF header XOR integrity
        |
        +-- check N3D.EXE XOR against BSF[1]
        |
        +-- registered? -- yes --> full path
                         \
                          no --> check MAP.1 XOR against BSF[2]
                                + gate Episodes 2/3, saves, cheats
```

### Win16

```text
BSF header XOR integrity
        |
        +-- registered? -- yes --> registered/full path
                         \
                          no --> check MAP.1 XOR against BSF[2]
                                + gate Episodes 2/3, saves, cheats

BSF[1] is retained in the common format but not used by the confirmed Win16 loader.
```

## Security characterization

This is and **weak integrity/licensing scheme**, not cryptographic DRM:

- repeating 52-byte XOR key;
- 8-bit XOR checksums;
- one-byte registration flag;
- plaintext-equivalent decoded resources after XOR;
- deterministic structure shared by DOS and Windows.

Its historical purpose appears to be distribution branding, shareware/full mode selection, and preventing casual mixing of shareware data/build components rather than resisting deliberate reverse engineering.

## Current confidence

- common DOS/Win16 header layout: **confirmed**
- key and per-block reset: **confirmed**
- registered flag `+03`: **confirmed**
- distributor `+04`: **confirmed**
- all three block meanings: **confirmed**
- selector 0..5 semantics on DOS: **confirmed**
- selector 0..5 structure on Win16: **confirmed**
- Win16 selector 3/4/5 runtime use: **confirmed**
- Win16 v1.0/1.3/1.6/1.8/1.10 decoder continuity: **confirmed**
- DOS EXE checksum field `+01`: **confirmed**
- Win16 non-use of `+01`: **strongly confirmed by loader/xref audit**
- shareware MAP.1 check: **confirmed on both platforms**
- registration-dependent episode/save/cheat behavior: **confirmed**

Remaining high-value work: identify/match the late DOS EXE whose weak checksum is `0x68`, map every surrounding Win16 function to semantic names, and add platform-aware validation/editing to the BSF Reader.