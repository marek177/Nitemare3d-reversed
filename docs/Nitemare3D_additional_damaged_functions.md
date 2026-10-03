# Nitemare 3D – additional damage and suspicious functions

Date: 2026-09-22  
Vstupy: DOS 1.0/1.7/1.8/2.0 and Nite3W 1.3/1.6/1.8/1.10 C exporty

## Confirmed failure decompile

V four DOS exportoch sa locate 15 explicit message `Unable to decompile`. Windows exporty do not have nor jedno takéto message.

| Version | Function | Error Ghidry | Probable cause |
|---|---|---|---|
| DOS 1.0 | `FUN_1000_0AE0` | AddressOutOfBounds `0x1DEC0002` | far pointer/segment incorrectly merge on linear address |
| DOS 1.0 | `FUN_1000_4800` | AddressOutOfBounds `0x1DEC0002` | same segment problem; predchodca neskoršej `4A86` |
| DOS 1.0 | `FUN_1000_9992` | Cannot marshal address space | invalid space varnode or incorrect boundary |
| DOS 1.0 | `FUN_1000_99F8` | AddressOutOfBounds `0x1DEC0002` | far pointer/segment |
| DOS 1.7 | `FUN_1000_0AEA` | AddressOutOfBounds `0x21E00002` | that certain logical routine as 1.0 `0AE0` |
| DOS 1.7 | `FUN_1000_9010` | AddressOutOfBounds `0x21E00002` | segment pointer; corresponds to areas DOS 2.0 `917E` |
| DOS 1.7 | `FUN_1000_9B72` | AddressOutOfBounds `0x21E00002` | segment pointer or incorrect stack type |
| DOS 1.7 | `FUN_1000_9D34` | Forced measure caused intersection | two protichodné data/row branches merge to one SSA uzla |
| DOS 1.8 | `FUN_1000_0AEA` | AddressOutOfBounds | stable damage across version |
| DOS 1.8 | `FUN_1000_4A86` | AddressOutOfBounds | nástupca areas DOS 1.0 `4800` |
| DOS 1.8 | `FUN_1000_9540` | Forced measure caused intersection | probable ekvivalent problem DOS 1.7 `9D34` |
| DOS 1.8 | `FUN_2000_0556` | Cannot marshal address space | runtime/render segment with incorrect address-space type |
| DOS 2.0 | `FUN_1000_0AEA` | AddressOutOfBounds `0x21FD0002` | stable segment problem |
| DOS 2.0 | `FUN_1000_4A86` | AddressOutOfBounds `0x21FD0002` | stable segment problem |
| DOS 2.0 | `FUN_1000_917E` | AddressOutOfBounds `0x21FD0002` | corresponds to areas DOS 1.7 `9010` |

Numbers `1DEC:0002`, `21E0:0002` and `21FD:0002` appear as version posunuté segment addresses. Ghidra their interpretation as invalidation linear address `0xSSSS0002`. Correction therefore requires correct 16-bit segment/far-pointer type, nie supplement missing bytes.

## probable merge blocks v DOS 2.0

Following bodies are neprimerane large and at the same time have weak cross-version similar. To is strong signál, that Ghidra pohltila viac functions, switch table or data.

| Function DOS 2.0 | Row | Nearest older candidate | Row | Status |
|---|---:|---|---:|---|
| `FUN_2000_9364` | 6417 | DOS 1.7 `FUN_2000_9194` | 6527 | kriticky merge block |
| `FUN_2000_2C16` | 5632 | DOS 1.7 `FUN_2000_2A46` | 5555 | kriticky merge block |
| `FUN_2000_0592` | 5235 | runtime area 1.7 | 6527 | kriticky merge block |
| `FUN_1000_84FE` | 3755 | DOS 1.8 `FUN_1000_86D2` | 2789 | probable merge |
| `FUN_1000_70D6` | 3246 | DOS 1.8 `FUN_1000_84F4` | 2435 | probable merge |
| `FUN_1000_89A2` | 3102 | DOS 1.8 `FUN_1000_84F4` | 2435 | probable merge/overlap |
| `FUN_1000_86DC` | 2605 | DOS 1.8 `FUN_1000_86D2` | 2789 | boundary sa between version differ |
| `FUN_1000_954A` | 2507 | DOS 1.7 `FUN_1000_8390` | 1626 | probable merge |
| `FUN_1000_87D8` | 1493 | DOS 1.7 `FUN_1000_866A` | 860 | probable merge |
| `FUN_1000_9CF2` | 1253 | DOS 1.8 `FUN_1000_9CD6` | 1526 | nestabilná boundary |
| `FUN_1000_9EB4` | 1004 | DOS 1.7 `FUN_1000_93DC` | 1237 | nestabilná boundary |
| `FUN_1000_B5B8` | 898 | DOS 1.8 `FUN_1000_B57C` | 722 | possible merge |
| `FUN_1000_4BE0` | 757 | DOS 1.8 `FUN_1000_4C49` | 675 | overlap sa candidate |
| `FUN_1000_4C49` | 751 | DOS 1.8 `FUN_1000_4C49` | 675 | same address, other boundary |
| `FUN_1000_4AD4` | 732 | DOS 1.8 `FUN_1000_4C49` | 675 | overlap sa candidate |
| `FUN_1000_8590` | 693 | DOS 1.8 `FUN_1000_8586` | 461 | possible merge |
| `FUN_1000_5F74` | 415 | DOS 1.8 `FUN_1000_5F74` | 616 | probable split v DOS 2.0 |
| `FUN_1000_9E4E` | 454 | DOS 1.8 `FUN_1000_9E32` | 557 | possible split |

## Additional varovné signály

V exportoch is total 2819 warning markerov, mostly `Removing unreachable block`. Itself such warning does not mean damage function: time arise z optimalizácie, switch dispatchu or nepresného prototype. Prioritu has only vtedy, when sa kombinuje with at least one z these character:

- internal target `CALL` neleží on start recognize functions;
- v tele sa locate `RETF` and for it next valid prolog;
- same routine has v inej verzii viac separate functions;
- telo has stovky up to thousand row and nízku cross-version similar;
- decompile uses absurdné stack offset or unrelated segment;
- several `FUN_*` starts v range jednej existing functions.

## Windows branch

Nite3W 1.3/1.6/1.8/1.10 does not have explicit failure decompile. From 967 functions versions 1.10 has only 38 weak or no older match. Most prominent simultaneous candidate is `FUN_1010_31AA` (109 row) compared with Nite3W 1.6 `FUN_1010_3136` (92 row), but difference can be legitímna modification, nie damage.

## Priorita opravy

1. set segmented far-pointer types for rodiny `0AE0/0AEA`, `4800/4A86` and `9010/917E`.
2. Fix forced-measure rodinu `9D34/9540` according to disassembly and predchodcu/nástupcu.
3. Split three largest blocks `2000:9364`, `2000:2C16`, `2000:0592` according to internal call targetov and `RET/RETF`.
4. Check overlap sa trio `1000:4AD4`, `4BE0`, `4C49`.
5. Up to then handle smaller split/measure candidate and unreachable warningy.

## Conclusion

Okrem original known troch problem exist najmenej **12 next explicit nezdekompilovaných input** v older DOS versions and approximately **18 vážnych split/measure candidates** v DOS 2.0. Multiple addresses are version podoby tej istej logical routines, so is not 30 completely different game functions. Windows branch is podstatne clear.