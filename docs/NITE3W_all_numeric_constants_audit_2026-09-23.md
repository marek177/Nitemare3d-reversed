# NITE3W 1.10 — audit numeric konštánt

**Date:** 23. 9. 2026  
**Build:** Windows NE, Windows 3.10 / Win16  
**EXE:** 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`  
**Primary pseudokód:** `nite3w110.exe.c`  
**Range:** all bodies 967 functions `FUN_...` z exportu; DOS version is not zahrnutá.

## Finding

V telách 967 functions som zaindexoval **17 721 výskytov numeric, znakových and booleovských literálov**. After zjednotení same numeric values is v exporte **795 different values**. Each výskyt has v sprievodnom CSV name functions, address `segment:offset`, line exportu, original write and okolité C vyjadrenie.

Tých 795 values is not 795 separate game right. Same number v different function can mean offset array, bitovú mask, boundary cyklu, identify messages or score. Therefore CSV preserves each výskyt osobitne and meaning pomenúvam only tam, where ho supports tok programu.

## Counts and spôsob count

| Item | Count | Note |
|---|---:|---|
| Functions with telom v exporte | 967 | All `FUN_...` define find on úrovni file. |
| Celočíselné literály | 16 643 | Znamienko `-` is započítané to values, napr. `-1`. |
| Znakové literály | 926 | Napr. `\0`, `\x01`, `\n`, `\a`, also obyčajné ASCII znaky prevedené on numeric value. |
| Booleovské literály | 152 | `true` sa map on 1, `false` on 0. |
| All zaindexované výskyty | **17 721** | Sum troch row above. |
| Difference numeric values | **795** | Znakové and booleovské values sa zlúčia with same numeric value. |
| Functions with at least jedným takýmto literálom | 913 | 54 tiel does not have v exporte recognize numeric, znakový nor booleovský literál. |

Automatické štítky v CSV popisujú only syntax row — for example bitovú operation, comparison or arithmetic with offset. **Are not automatickým evidence semantic.** Meaning needs to confirm read functions, call and data, as v príkladoch below.

## Confirmed usage

| Constant or skupina | Finding usage | Evidence v exporte | Confidence |
|---|---|---|---|
| `0x40` = 64 and `0x3F` = 63 | Rozmer/stride mriežky: calculation cells uses `y * 0x40 + x`, subsequently multiplies 2 byte; additional path prevádzajú world coordinates posunom `>> 6` and ohraničujú index on 0–63. | `FUN_1010_264A`, lines 18970+; `FUN_1010_2800`, lines 19090+; coordinate read napr. lines 17918–18028. | High for these map path. Same values inde can mať other meaning. |
| `0x1C` = 28 B | Step between record object v initialize loop. | `FUN_1010_d1a2`, line 29697: `local_a = iVar6 * 0x1c + 0x6d66`. | High |
| `0x15E` = 350 | Limit object: during prekročení sa vypíše `MAXOBJ exceeded` with value `0x15E`; ten certain count sa uses also during kroku between pointer v table object. | `FUN_1010_d1a2`, line 29702; `FUN_1010_c906`, line 29210. | High |
| `1000` | Limit vektorov: value sa passes to errors `MAXVEC exceeded`. | `FUN_1018_4046`, line 35505. | High for limit this tables. |
| `0x43FD`, `3`, `0x269EC3`, `>> 16`, `& 0x7FFF` | Generátor random čísel. Auxiliary function skladá 32-bit súčin z 16-bit time: `0x43FD + (3 << 16) = 0x343FD`. Then pripočíta `0x269EC3`; result update 32-bit status and returns upper 15 bitov. | `FUN_1008_6ec8`, lines 16746–16754; multiply `FUN_1008_7118`, lines 16953–16962. | High |
| `0x28` = 40 | Lower boundary kalibrovaného intervalu simulácie/render. Function odoberie five vzoriek, computes priemer and during small value sets minimum `0x28`. | `FUN_1010_d7d0`, lines 30154–30162. | High for minimum; jednotka intervalu and timing v each next call remain separate question. |
| `0x168`, `0x578`, `0xAF0` | Time formula `((local_6 * 0x168 + 0x578) / 0xAF0)` for value store to `DAT_1048_53F8`. | `FUN_1010_d7d0`, line 30171. | High for vzorec; meaning physical jednotiek is not z tohto vzorca itself známy. |
| `0x140` = 320, `0x13F` = 319, `200`, `199` | Path bitmapového/image format uses 320-byte line and 200 row; check use last index 319/199. | `FUN_1010_5b96`, lines 22567–22632; podobná check v `FUN_1010_5d72`, line 22699. | High for this bitmapovú path; nie each `200` v programe is height image. |
| `0x0111`, `0x0201`, `0x0204`, `0x0207`, `0x00A1` | Values v field message events window and their filtrovaní; is Win16/MFC message input, nie o classes game object. | `FUN_1000_11C2`, `FUN_1000_1B52`, `FUN_1000_66DC`, `FUN_1000_67DE`, `FUN_1000_81BE`, lines 1711, 2207, 5987, 6053, 6882–6904. | High for role message values; specifically names each messages needs to viazať on Win16 headers/call path. |
| Classes object `0x08`–`0x20` → return values | Function selects value according to byte classes object on `+6`. call path during smrti aktéra result rozšíri with znamienkom to 32-bitového global súčtu; values sa message as change score. | Map v `FUN_1010_9f10`, lines 26319–26361; add result to `DAT_1048_4c16` during terminate/porazení object v `FUN_1010_80f8`, lines 24641–24672. | High for class odstupňované score; names class needs to párovať with OBJECTS dátami. |
| `0x400000` | Zostavuje sa table values `0x400000 / n`. Is to fixed škála recipročnej tables; its exact usage and format fixed-point needs to confirm čitateľmi tables. | `FUN_1010_2930`, lines 19117–19126. | High for create tables; medium/open for jednotku and subsequent usage. |
| `0xFFFF` and `-1` | Time sentinel or negative result, but nie jednotne. For example file seek najprv writes `0xFFFF:0xFFFF` and during error ponechá sentinel; other functions use `-1` as status návratu. | `FUN_1000_07a0`, lines 1001–1016 and raw-byte audit this functions; additional výskyty are separate rozpísané v CSV. | High for listed seek; each next výskyt needs to klasifikovať according to functions. |

### Triedne score z `FUN_1010_9f10`

Function reads class z `OBJECT+6`. Its result sa during smrti/remove aktéra adds to 32-bitového akumulátora `DAT_1048_4c16`, which sa message as score. `0xFC18` sa during this add znamienkovo rozšíri on `-1000`, so class `0x15` subtracts score.

| Byte classes | Result |
|---|---:|
| `0x08`, `0x1A` | 25 |
| `0x09` | 75 |
| `0x0A`, `0x20` | 50 |
| `0x0B`, `0x0F`, `0x10`, `0x17`, `0x1B`, `0x1C` | 100 |
| `0x0C`, `0x1D`, `0x1E` | 250 |
| `0x0D`, `0x12`, `0x13` | 150 |
| `0x0E`, `0x14`, `0x18`, `0x1F` | 200 |
| `0x15` | -1000 (`0xFC18` as 16-bit signed value) |
| `0x16` | 1000 |
| other | 0 |

Numbers class are tu values `OBJECT+6`, nie automaticky ID from file OBJECTS. Needs to their previazať through table class for specific episode, up to then name enemy or object.

## Why sa same number cannot name globally

| Value | Count výskytov | Príklady different usage |
|---|---:|---|
| `0x10` | 456 | offset/size, bit value also count posunu during skladaní 32-bitovej values. |
| `0x20` | 119 | offset array, bit maska, value `case` also argument API. |
| `0x40` | 139 | rozmer mriežky v map path, offset and bit mask v iných path. |
| `0x1000` | 237 | segment argument during far callbackoch, argumenty runtime/exception call and additional numeric usage. |
| `0xFFFF` | 136 | empty/neudaný sentinel, bit mask or value file interface according to specific path. |

Count v table is count literálových výskytov z CSV, nie count separate meaning. During copy to new source code therefore pomenuj meaning according to usage, for example `TileUnitsPerCell`, `ObjectRecordBytes`, `MaxObjects` or `RngIncrement`; nevytváraj global name type `CONST_0x20`.

## Syntaktické skupiny v celom exporte

These counts vznikli automatickým označením row according to syntaxe. Jedna kategória is assign každému výskytu; kategórie **are not semantic klasifikáciou**.

| Štítok according to row | Výskyty |
|---|---:|
| offset or arithmetic výraz | 5 110 |
| bit operation or posun | 4 295 |
| skalár without rozhodnutého meaning | 4 022 |
| compare výraz | 2 156 |
| indexovanie array | 1 247 |
| riadenie loops | 491 |
| `case` štítok | 380 |
| recognize Win16/runtime argument | 20 |

Najčastejšie values are `0` (4 271 výskytov), `1` (2 404), `2` (1 389), `6` (585), `4` (515), `0x10` (456), `3` (444), `-1` (427) and `8` (425). Their high frekvencia does not mean, that have jediný shared meaning.

## So far unclosed skupiny

1. **Bit mask and flags:** `0x01`, `0x02`, `0x04`, `0x08`, `0x10`, `0x20`, `0x40`, `0x80`, `0x4000`, `0x8000`, `0xC000` and podobné values. V different function kódujú different arrays; needs to their pomenúvať according to specific readera/writera.
2. **Win16/MFC range message and commands:** are visible v dispatchi, no each value potrebuje koreláciu with `WNDPROC`, menu/resource table and callbackom.
3. **Vysoké values and far pointer:** `0xC000`, `0xF000`, `0xFF00`, `0x80000000`, `0xFFFFFFFF` and address podobné numbers can be boundary range, znamienkový bit, mask or pass segment. Without kontextu their cannot mark as game constant.
4. **Colors and palette:** `0xFF00FF`, `0xFF00DA`, `0xFFFFFF` sa objavujú during palette path. `FUN_1010_BA74` their posiela to `FUN_1010_3B16`, which writes zložky palette to runtime tables/hardvérového portu. Exact divide argumentov is ovplyvnené nepresným dekompilovaným prototypom.
5. **table constant mimo tiel functions:** pseudokód pomenúva globally data `DAT_...`, but nevypisuje all their stored bytes. Values v lookup table, string, source Win16 and file MAP/IMG/OBJECTS/WALLS therefore are not zahrnuté v počte 795.
6. **Time units:** divide `1000`, count vzoriek and korekčné constant are v code, but their specific jednotka depends from source tickov and call path.

## Complete and boundary

- Inventory covers numeric, znakové and booleovské literály **v telách 967 dekompilovaných functions**. Nepokrýva values stored only v dátových table, source, externých API or game file.
- Addresses functions and lines v CSV are z exportu C; are not original menami functions nor original name konštánt.
- Doslovné hex values v pseudokóde nemusia be semantic separate constant: 16-bit field can total tvoriť 32-bitovú value, as `0x43FD` and `3` during RNG.
- Static usage are map; this audit neobsahuje novú živú debuggerovú stopu nor visual test each values.

**Confidence:** high for count literálových výskytov v this exporte and for listed priame kódové path; medium for complete semantic named all values. Other lines remain trace-index, nie confirm slovníkom meaning.

## Files with complete inventory

- `NITE3W110_numeric_constant_occurrences.csv` — each výskyt including functions, addresses, row and kontextového výrazu.
- `NITE3W110_numeric_constant_values.csv` — jedna item on each z 795 numeric values, frekvencia and list functions.