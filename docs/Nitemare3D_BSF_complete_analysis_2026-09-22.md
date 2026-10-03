# Nitemare-3D `NITE3D.BSF` — complete static audit

**Date:** 2026-09-22  
**Primary code:** Win16 `NITE3W.EXE` 1.10  
**Comparison:** Win16 1.3, 1.6, 1.8; DOS and Windows BSF, total 10 variantov

## Result

`NITE3D.BSF` is not file symbol, class nor skompilovaného code. Is to šifrovaný
text kontajner use príručky, registračného/objednávkového text and
conclusion text. Has fixed 54-byte header and three for sebou stored blocks.

Format, šifra, layout headers, all six operations loadera, three blocks,
text row classes and all priame xrefy on centrálny dispatcher in Win16 1.10
are identify. V file are not C++ RTTI, vtable nor object classes.

## Šifra

Each load úsek sa dešifruje separate repeated XOR kľúčom length `0x34`:

```text
Copyright 1992, David P Gray, Gray Design Associates
```

Algoritmus:

```c
for (i = 0; i < length; ++i)
    data[i] ^= key[i % 0x34];
```

Šifra sa reštartuje from `key[0]` for header also for each z troch block. Win16
1.10 ju executes function `4:32E4` (`FUN_1018_32e4`). Has two priame vstupy:

1. `3:60AA` — dešifruje vybraný text block;
2. `3:C772`, branch `0` — dešifruje 54-byte header.

## Header — 54 bytes (`0x36`)

| Offset | Type | Proposed name | Meaning | Status |
|---:|---|---|---|---|
| `00` | `uint8` | `header_xor_balance` | Vyrovnávací byte; XOR all **zašifrovaných** 54 bytes headers is `0` | CONFIRMED |
| `01` | `uint8` | `exe_xor_expected` | Očakávaná check programu; DOS full value `0x36` exactly corresponds to `0x7B XOR všetky bajty N3D.EXE` | CONFIRMED DOS / UNUSED WIN |
| `02` | `uint8` | `map1_xor_expected` | Očakávaná check `MAP.1`; value `0xD2` was verify on oboch store `MAP.1` | CONFIRMED |
| `03` | `uint8` | `registered_or_full` | `0` shareware, `1` full/registered | CONFIRMED |
| `04–23` | `char[32]` | `distributor` | NUL-terminate distribútor/registration | CONFIRMED |
| `24` | `uint32` | `block1_offset` | Start objednávkového/registračného text | CONFIRMED |
| `28` | `uint32` | `block2_offset` | Start main príručky | CONFIRMED |
| `2C` | `uint32` | `block3_offset` | Start conclusion/objednávkového text | CONFIRMED |
| `30` | `uint16` | `block1_length` | Length bloku 1 | CONFIRMED |
| `32` | `uint16` | `block2_length` | Length bloku 2 | CONFIRMED |
| `34` | `uint16` | `block3_length` | Length bloku 3 | CONFIRMED |

All ten file spĺňa three invarianty: first block starts on `0x36`, blocks are
kontinuálne without medzier and third block ends exactly on EOF.

## Dispatcher `3:C772` — operations 0 up to 5

Proposed name: `BsfDispatch(uint16 selector)`.

| Selector | Result | usage arrays/block | Status |
|---:|---|---|---|
| `0` | Loads and dešifruje header; verify XOR headers; during shareware checks entire `MAP.1` | header | CONFIRMED |
| `1` | Returns far pointer on `registered_or_full`, only if is nonzero; otherwise `NULL` | `+03` | CONFIRMED |
| `2` | Returns far pointer on distribútora | `+04` | CONFIRMED |
| `3` | Allocate, loads and dešifruje main príručku | block 2 (`+28/+32`) | CONFIRMED |
| `4` | Allocate, loads and dešifruje registračný/objednávkový text | block 1 (`+24/+30`) | CONFIRMED |
| `5` | Allocate, loads and dešifruje conclusion/objednávkový text | block 3 (`+2C/+34`) | CONFIRMED |

Selektory `>5` return `NULL`. Text blocks dostanú one extra zero byte for
koncom, so result is always valid C string.

## Functions loadera and proposed names

| Win16 1.10 | Proposed name | Role | Confidence |
|---|---|---|---|
| `3:60AA` | `BsfReadDecryptBlock` | opens BSF, alokuje `length+1`, seek, read, NUL, XOR-decrypt | CONFIRMED |
| `3:C696` | `VerifyWholeFileXor` | seed `0x7B`, XOR entire file, comparison with očakávaným byte | CONFIRMED |
| `3:C772` | `BsfDispatch` | six operations nad header and block | CONFIRMED |
| `4:32E4` | `BsfXorCryptAndRawChecksum` | XOR šifra; return is XOR original zašifrovaných bytes | CONFIRMED |
| `4:15B4` | `ParseHelpDirective` | parser `%...%` commands | CONFIRMED |
| `4:17D8` | `Render` | render text after najbližší `#` | CONFIRMED |
| `4:19A6` | `OpenBsfHelpViewer` | loads selector, spočíta strany, initializes and vykreslí viewer | CONFIRMED |
| `4:1A4A` | `PrintOrderForm` | tlač objednávkového formulára; related UI subsystém | CONFIRMED |

### Posuny between verziami Win16

| Function | 1.3 | 1.6 | 1.8 | 1.10 |
|---|---:|---:|---:|---:|
| block reader | `3:5E92` | `3:6006` | `3:6006` | `3:60AA` |
| whole-file XOR verifier | `3:C474` | `3:C5E8` | `3:C5E8` | `3:C696` |
| dispatcher | `3:C550` | `3:C6C4` | `3:C6C4` | `3:C772` |
| XOR decrypt | `4:2FB2` | `4:3222` | `4:32EC` | `4:32E4` |

Differences 1.6/1.8 during same address dispatcheru confirm, that jadro BSF format
sa nemenilo; posunula sa only part segmentu 4.

## Globally premenné Win16 1.10

### Dešifrovaná header v dátovom segment `1048`

| Address | Name |
|---:|---|
| `38F2` | `g_bsf_header.header_xor_balance` |
| `38F3` | `g_bsf_header.exe_xor_expected` |
| `38F4` | `g_bsf_header.map1_xor_expected` |
| `38F5` | `g_bsf_header.registered_or_full` |
| `38F6–3915` | `g_bsf_header.distributor[32]` |
| `3916` | `g_bsf_header.block1_offset` |
| `391A` | `g_bsf_header.block2_offset` |
| `391E` | `g_bsf_header.block3_offset` |
| `3922` | `g_bsf_header.block1_length` |
| `3924` | `g_bsf_header.block2_length` |
| `3926` | `g_bsf_header.block3_length` |

### Help viewer

| Address | Proposed name | Meaning |
|---:|---|---|
| `3ABA` | `g_help_text_base` | far pointer on start dešifrovaného block |
| `3ABE` | `g_help_page_ptr` | far pointer on current stranu |
| `3AC6` | `g_help_page_and_count` | low word = current strana, high word = count strán |
| `3AC8` | `g_help_page_count` | prekrývajúci sa high word above listed values |
| `3ACA` | `g_help_font_or_color_bank` | index banky usage during vykresľovaní znakov; exact origin name PARTIAL |
| `3ACC...` | `g_help_glyph_cache` | 4-byte items grafiky/glyphov use rendererom |

## XREF audit Win16 1.10

### Priame calls `BsfDispatch` (`3:C772`): 12

| Call site | Nadradená function | Selector | Meaning |
|---:|---:|---:|---|
| `3:0C80` | `3:0B4C` | `2` | distribútor/registration text |
| `3:0CC8` | `3:0B4C` | `1` | full/shareware status |
| `3:0F16` | `3:0EF6` | `0` | initialization and valid BSF |
| `3:0FAB` | `3:0F64` | `1` | feature/registration gate |
| `3:5437` | `3:5388` | `1` | compatibility/obmedzenie during read data |
| `3:C52A` | `3:C4FA` | `1` | registered/shareware text v titulku/UI |
| `4:19B5` | `4:19A6` | parameter | viewer for block 3/4/5 |
| `4:1E11` | `4:1CAE` | `1` | finding full stavu |
| `4:1E29` | `4:1CAE` | `4` | objednávkový/registračný block |
| `4:2491` | `4:244C` | `1` | povolenie items menu |
| `4:24EB` | `4:24BC` | `1` | povolenie/choice items menu |
| `4:27A5` | `4:2746` | `1` | cheat gate; during shareware zeros cheat choice |

`OpenBsfHelpViewer` has four priame calls: `3:0DC8`, `3:98B6`, `3:DC53` and
`4:2992`. Zbalené 32-bit `push` instructions prenášajú viac 16-bit argumentov; z nich
viewer uses selektory main príručky and conclusion text.

### Xrefy on literál `nite3d.bsf`

In Win16 1.10 is jedna dátová value `1048:1946` and four okamžité referencie v
`BsfDispatch`: `3:C7A1`, `3:C7B2`, `3:C7ED`, `3:C84F`.

DOS `N3D-UNFU` contains six separate copy string on file offset
`1AB48`, `1AB53`, `1AB74`, `1AB9A`, `1ABA5`, `1ABB0`. Therefore skorší data item „six
xrefov on one string“ needs to spresniť: v DOS image is six literalov/copy;
in Win16 is one literál with štyrmi priamymi referenciami.

## Text classes/commands

Parser supports these všeobecné classes between znakmi `%...%`:

| Syntax | Range | Function | Usage directly v BSF |
|---|---:|---|---|
| `%Cnnn%` | numeric value | sets text farbu/atribút | yes |
| `%d%` | without numbers | restores predvolenú farbu/atribút | yes |
| `%oNN%` | `0..255` | vloží grafický object/image z data game | yes |
| `%cNN%` | `0..15` | alternatívny color atribút | nie v skúmaných BSF |
| `%bNN%` | `0..15` | render atribút/pozadie | nie v skúmaných BSF; exact semantika PARTIAL |
| `%BN%` | parser numbers | render/layout command | nie v skúmaných BSF; PARTIAL |
| `%pNN%` | `0..31` | prepnutie image/palette source | nie v skúmaných BSF; PARTIAL |
| `#` | — | end strany | yes |

Render reject command long than 8 znakov. Strany sa count as
`1 + count znakov #`.

### Confirmed `%oNN%` links z text príručky

| ID | Meaning v príručke |
|---:|---|
| `5` | color key |
| `10` | color ID card |
| `19` | potion/health |
| `25` | magic eye — energia automapy |
| `26` | crystal ball — zobrazenie enemies |
| `31–34` | four color pentagramy |
| `37`, `40` | plasma guns |
| `38` | magic wand |
| `39` | silver pistol |
| `41` | silver bullets |
| `42` | plasma charges |
| `43` | spell books |
| `44` | scroll |
| `73` | combination safe |
| `74` | trunk |
| `23`, `85` | ilustračné enemy/scene objects v shareware príbehu; exact name PARTIAL |
| `249`, `250` | distribučné/logo image during PSL kontaktoch; exact asset PARTIAL |

## Ten analyzovaných variant

| Variant | Flag | Distributor | Block 1 | Block 2 | Block 3 | Strany bloku 2 |
|---|---:|---|---:|---:|---:|---:|
| full-DOS | 1 | Outreach Communications Corp | 474 | 9 141 | 581 | 21 |
| full-Windows | 1 | David P Gray | 95 | 9 640 | 581 | 22 |
| sh-DOS-10 | 0 | Author Direct Network | 1 657 | 12 058 | 972 | 29 |
| sh-DOS-17 | 0 | Shareware | 1 657 | 12 830 | 972 | 31 |
| sh-DOS-18 | 0 | Walnut Creek | 1 657 | 12 830 | 972 | 31 |
| sh-DOS-19 | 0 | Author-Direct | 1 657 | 13 117 | 972 | 32 |
| sh-DOS-20 | 0 | Author Direct | 1 657 | 13 109 | 972 | 32 |
| sh-Win-13 | 0 | The RoadHouse BBS | 530 | 13 327 | 985 | 32 |
| sh-Win-16 | 0 | Author-Direct | 530 | 13 878 | 985 | 34 |
| sh-Win-18 | 0 | Internet | 530 | 13 868 | 985 | 34 |

Identical dešifrované skupiny:

- DOS shareware block 1 is identical in versions 1.0/1.7/1.8/1.9/2.0;
- Windows shareware block 1 is identical in versions 1.3/1.6/1.8;
- DOS shareware block 3 is identical in all piatich versions;
- Windows shareware block 3 is identical in all troch versions;
- full DOS and full Windows have identical block 3;
- main príručka sa interim menila; only DOS 1.7 and 1.8 are byte-identical.

## Obsahové findings

- Full príručka directly dokumentuje all three episodes, mouse/joystick, `F9` automapu,
  `F10` enemies, secret-panel detector, weapons, ammo, pentagramy, safes and trunks.
- Shareware blocks contain objednávkový formulár, informácie o next dvoch episode,
  cheat modes, map browser and distribučné kontakty.
- Format `%oNN%` is next independent evidence väzieb between BSF manuálom and IMG/OBJECT
  identify. Especially ID `37–44` confirm weapons and ammo, `25–26` HUD/map
  power-upy and `31–34` štvoricu pentagramov.

## Status uzavretia

| Area | Status |
|---|---:|
| šifra/dešifrovanie | 100 % |
| header and blocks | 100 % |
| meaning selectorov 0–5 | 100 % |
| Win16 1.10 dispatcher xrefy | 100 % staticky visible priamych call |
| Win16 globally arrays BSF | 95–100 % |
| use `%C/%d/%o/#` commands | 100 % |
| nepoužité všeobecné `%b/%B/%c/%p` commands | 60–80 %; needed analysis render |
| DOS loader functional boundary/xrefy | approximately 70 %; format and content are already confirmed |

Najväčšie remain unknown already are not v itself BSF format: is exact
semantiku nepoužitých render commands `%b/%B/%c/%p` and named four
shareware images `%o23/%o85/%o249/%o250` according to IMG indexu.

## Reprodukcia

Part of auditu is `nite3d_bsf_analyzer.py`. Is read-only, verify invarianty,
dešifruje all blocks and creates UTF-8 text, JSON manifest and CSV table.

```bash
python nite3d_bsf_analyzer.py path/to/NITE3D.BSF -o decoded
```