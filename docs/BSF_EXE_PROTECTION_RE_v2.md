# Nitemare-3D `NITE3D.BSF` / EXE protection reverse engineering — v2

## Result

`NITE3D.BSF` is not only and text/resource file. In DOS Nitemare-3D it acts as and boot/license/distributor record and carries integrity values used by the executable.

Confirmed roles:

1. identifies shareware vs registered/full mode;
2. carries distributor/owner branding text;
3. binds the BSF to an `N3D.EXE` through and weak 8-bit XOR checksum;
4. in shareware mode binds the game to the expected `MAP.1` through the same checksum scheme;
5. carries three encrypted text resources: exit/order text, HELP/manual, and Episode-1 ending/transition text.

The mechanism is and weak integrity/license gate, not cryptographically strong DRM.

## XOR key

ASCII key, length 52 bytes:

`Copyright 1992, David P Gray, Gray Design Associates`

The 54-byte header is XOR-decoded from key index 0. **Each of the three text blocks restarts the key at index 0.**

## Confirmed 54-byte header

| Offset | Size | Meaning |
|---:|---:|---|
| `+00` | 1 | checksum/correction byte; XOR of the 54 stored encrypted header bytes must be `00` |
| `+01` | 1 | expected `N3D.EXE` XOR checksum, seed `7B` |
| `+02` | 1 | expected `MAP.1` XOR checksum, seed `7B` |
| `+03` | 1 | registration flag: `00` shareware, non-zero registered/full |
| `+04` | 32 | distributor/owner text, NUL padded |
| `+24` | 4 | Block0 file offset, uint32 LE |
| `+28` | 4 | Block1 file offset, uint32 LE |
| `+2C` | 4 | Block2 file offset, uint32 LE |
| `+30` | 2 | Block0 length, uint16 LE |
| `+32` | 2 | Block1 length, uint16 LE |
| `+34` | 2 | Block2 length, uint16 LE |

## DOS v1.9 exact reader path

Analyzed unpacked module image of `N3D-19.exe`.

### BSF dispatcher

- module-linear: `0xAD5E`
- canonical far address: `083C:299E`
- selector range: `0..5`

Selector mapping:

| selector | behavior |
|---:|---|
| `0` | open/read/decode/validate 54-byte BSF header; verify EXE; for shareware also verify MAP.1 |
| `1` | return non-NULL pointer if registered, otherwise NULL |
| `2` | return pointer to 32-byte distributor field |
| `3` | load/decrypt Block1 = HELP/manual |
| `4` | load/decrypt Block0 = exit/order/purchase text |
| `5` | load/decrypt Block2 = Episode-1 ending/transition text |

### Header data addresses in v1.9 runtime DS

- header base `DS:3636`
- `DS:3637` expected EXE checksum
- `DS:3638` expected MAP.1 checksum
- `DS:3639` registered flag
- `DS:363A` distributor string
- offsets `DS:365A`, `DS:365E`, `DS:3662`
- lengths `DS:3666`, `DS:3668`, `DS:366A`

### Header XOR/checksum routine

- module-linear `0xFD16`
- callable as `0FB7:01A6`

For every input byte:

```c
checksum ^= encrypted_byte;
decoded_byte = encrypted_byte ^ key[index % 52];
```

The header load requires the returned checksum to equal zero.

### File checksum verifier

- module-linear `0xAC82`
- same segment equivalent `083C:28C2`

Algorithm:

```c
uint8_t checksum = 0x7B;
for each selected byte in file:
    checksum ^= byte;
if (checksum != expected)
    fatal_corrupt_error();
```

`length == 0` selects the entire file.

### Generic BSF block loader

- module-linear `0x4272`
- far address `0277:1B02`

Behavior:

1. opens `nite3d.bsf`;
2. allocates `length+1` bytes;
3. seeks to the supplied block offset;
4. reads exactly the supplied length;
5. appends NUL;
6. closes the file;
7. invokes the XOR decoder with the key restarted at position 0;
8. returns the allocated far pointer.

## Protection order in selector 0

Observed v1.9 flow:

```c
read 54 bytes from nite3d.bsf;
if (decode_header_and_return_stored_xor(...) != 0)
    corrupted();

verify_file("n3d.exe", whole_file, header.exeChecksum);  // always

if (header.registered == 0)
    verify_file("map.1", whole_file, header.map1Checksum); // shareware only
```

Therefore:

- and damaged/edited header without fixing its XOR correction fails;
- and BSF expecting and different EXE checksum fails;
- shareware additionally rejects and `MAP.1` whose XOR checksum differs;
- registered/full skips the `MAP.1` protection branch.

## Registration flag usage

### Save-game restriction

v1.9 module-linear `0x355D` calls selector 1.

If unregistered, and save referring to an episode greater than Episode 1 is rejected. Registered mode accepts the higher-episode save path.

### Episode availability

At `0xF8A3`, selector 1 is tested while enumerating episode/map entries:

```c
if (registered || episode == 1)
    enable_episode_entry();
```

Therefore merely placing MAP.2/MAP.3 beside and shareware executable is not sufficient for normal menu access.

At `0xF919`, another episode-selection path again skips higher entries while unregistered.

### Cheat gating

At `0xF3CB`, selector 1 is tested. Registered builds continue into the cheat setup path. Unregistered builds clear the related cheat state and display the purchase warning.

### Startup

At `0x483A`, selector 0 performs the BSF + EXE + conditional MAP.1 validation during startup.

## Block semantics

### Block0 — dispatcher selector 4

Shareware examples contain purchase/order/printing text for Episodes 2 and 3.

Registered/full examples replace this with and short commercial-software / thank-you message.

The DOS order-printing function calls selector 4 directly (`0xE888` in the v1.9 module image).

### Block1 — dispatcher selector 3

Full in-game HELP/manual resource, using `#` page separators and `%...%` formatting commands.

The generic page viewer at module-linear `0xE69C` receives selector 3 for HELP.

Shareware variants include ordering and new-episode sections. Registered variants contain the full trilogy story/help and omit the shareware ordering sections.

### Block2 — dispatcher selector 5

Episode-1 ending / story transition text. Shareware variants append and purchase page after and `#`; registered variants contain only the story transition.

The previously missing selector-5 call is confirmed in DOS v1.9:

- module-linear `0xE981`: `pushl 0x00050010`
- then near/far-style call to the page viewer at `0xE69C`
- viewer reads its selector from the high word, therefore selector = `5`, display/resource parameter = `0x10`

The viewer then calls BSF dispatcher `083C:299E` with selector 5.

This closes the direct runtime use of all three blocks.

## Concrete same-EXE compatibility result

The uploaded 74,484-byte DOS `N3D.EXE` tested in this analysis has XOR(seed `7B`) = `0x36`.

Both of these supplied BSFs expect `0x36`:

- shareware: `NITE3D(20260930-133036).BSF`, `registered=0`, `Author Direct`
- full: `NITE3D(20260930-132945).BSF`, `registered=1`, `Outreach Communications Corp`

Both therefore pass the **same executable'with** EXE-checksum test. The shareware BSF additionally enters the MAP.1 checksum test; the full BSF skips it.

This is direct evidence that the executable contains both code paths and that BSF data controls which path is active.

Caveat: the EXE check is only an 8-bit XOR, with an equal checksum does not establish that two different EXE files are byte-identical. It establishes that they are indistinguishable to this particular protection check.

## Late `0x68` BSFs

Several supplied shareware BSFs and the `David P Gray` registered BSFs expect EXE checksum `0x68`. None of the currently matched 74,484-byte EXEs tested here has `0x68` (the tested files produce `0x36`). Therefore to not yet assign and specific uploaded EXE to the `0x68` family solely from size/version assumptions.

## Current reconstruction confidence

- XOR cipher/key: confirmed
- key reset per block: confirmed
- header layout: confirmed
- header integrity test: confirmed
- EXE checksum field/algorithm: confirmed
- MAP.1 checksum field/algorithm: confirmed
- registered flag: confirmed
- distributor field: confirmed
- three offset/length records: confirmed
- all selector 0..5 semantics: confirmed
- Block0/1/2 runtime purpose: confirmed
- shareware episode/save/cheat gating: confirmed

Remaining work is mainly naming surrounding UI/state variables and repeating the exact address map across all DOS and Win16 versions.