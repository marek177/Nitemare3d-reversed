# Nitemare3D — audit unknown areas all available MS-DOS build

**Date:** 24. 9. 2026. **verify versions:** V1.0, V1.7, V1.9, V2.0.  
**Range:** identita and unpack programov, comparison code, selected detailed rozbory, isolated emulačné test and register remain question. The entire game nor all historical release are not this auditom closed.

## 1. Result

This prechod priniesol new evidence, nie only prepis starých list:

1. Files series `N3D-E-*` still obsahovali internal kompresiu EXEPACK. Restore are complete image four programov and their relocations. Independent execute original dekompresorov dalo same bytes.
2. `N3D-E-18.EXE`, `N3D-E-18(1).EXE` and `N3D-UNP.EXE` are identical with provided V1.9. Also original `N3D(5).EXE` sa after remove DIET and EXEPACK match with V1.9. actual V1.8 v check underlying missing.
3. Old record `FUN_2000_9364` starts v compress file byte text Microsoft runtime. Is not supported, that is obrovskú game function. Corrected is map 14 records lie for unchanged prefixom.
4. V2.0 adds timer indikácie hit on `DS:417A`. player block has therefore 94 B; V1.0, V1.7 and V1.9 save 92 B.
5. V2.0 move calculation prichádzajúceho damage before two ochranné check. Older versions these check execute before calculation. To can ovplyvniť also odbery RNG v corresponding class.
6. `GUARD+12h` is v examined selektore cache direction animations. V1.0 has moreover different choice banky during state 6 and strategy 2.
7. Calculation distance uses own integer odmocninu with neštandardným round. Its behavior was verify for all input 0–7938 v each from four build.
8. Provided `MAP.1` z folder V1.9 and V2.0 sa differ only move object 216 v E1M5 o jednu whole. Their `IMG.1` and `UIF.DAT` sa also differ.

**Meaning state:** `Confirmed` = directly supported listed byte or test; `Inferred` = interpretation with open link; `Unknown` = nezískaný evidence. Isolated emulation functions is not record behu whole game.

## 2. Identita programov and hranice rozsahu

| Version in inside programu | EXEPACK file | Size complete image | Relocations | Original CS:IP, relative k load image |
|---|---|---:|---:|---|
| V1.0 | N3D-E-10.EXE | 154 448 B | 1 639 | 119B:0010 |
| V1.7 | N3D-E-17.EXE | 170 848 B | 1 657 | 11D1:0018 |
| V1.9 | N3D-E-19.EXE | 171 296 B | 1 669 | 11EA:001C |
| V2.0 | N3D-E-20.EXE | 171 360 B | 1 670 | 11EE:0018 |

SHA-256 complete image, without MZ headers and before add segment load:

| Version | SHA-256 |
|---|---|
| V1.0 | `113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a` |
| V1.7 | `df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff` |
| V1.9 | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |
| V2.0 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |

Identitu support also original DIET files v `nitemare3d-shareware+images.zip`: `nite3d10/N3D.EXE`, `nite3d(1.7)/N3D.EXE`, `nite3d19/N3D.EXE`, `nite3d20/N3D.EXE`. Their complete unpack image sa after byte match with above listed. Folder `nite3d_3` contains next copy V1.9. Check include also archive `msdos version.zip` and `sh -nite-3d.zip`.

To dokazuje identitu these provided programov. Nedokazuje to, that archive contain all release versions or that all pribalené assety are neupravené historical distribúcie. Videá marked V1.1 do not replace missing EXE this versions.

## 3. Correction base older analysis

### Two layer rozbaľovania

Original DOS EXE has v check distribúciách external DIET obal. Provided files `N3D-E-*` have this obal remove, but still contain EXEPACK with podpisom `RB`, spätným copy/vypĺňaním and own relocation table.

| Version | Prefix, which sa unpack does not change | End prefixu, exkluzívne |
|---|---:|---|
| V1.0 | 87 954 B | `15792h` |
| V1.7 | 88 622 B | `15A2Eh` |
| V1.9 | 89 026 B | `15BC2h` |
| V2.0 | 89 086 B | `15BFEh` |

For touto boundary cannot generally use right „address v image = offset v EXE − 512“. Naopak, earlier evidence z unchanged prefixu remain usage, if was correct interpretation instructions and segment.

Independent verify:

- Python dekodér process copy/vypĺňacie blocks and relocation tables.
- Emulator execute original EXEPACK stub, stop sa before CRT štartom and its output sa compare with dekodérom after applying relocation. All four compare sa match.
- V2.0 sa moreover exactly zhoduje with obrazom v dodanom `N3D_UNPACKED_CLEAN.EXE`.
- Original four DIET EXE z large archive dali same final image.

### Register functions

Old register has 519 DOS riadkov. Z nich 505 starts v nezmenenom prefixe; **to nepotvrdzuje their names, boundary nor complete pochopenie**. increase 14 requires opravu mapovania.

Najvýraznejší case:

| Old data item | Priamy evidence | Correction |
|---|---|---|
| `FUN_2000_9364`, data rozsiahly runtime block | Its stará position `19364h` sa map on `27748h` unpack V2.0. Bytes start `oft Corp`, therefore continuation text `Microsoft Corp`, after ktorom nasledujú error message. | This štart is data candidate, nie supported input functions. Old thousand row decompile sa must not rátať as jedna pochopená function. |
| `FUN_2000_5CB7` | Lies v baliacich metadata/command. | Does not have priamy ekvivalent bytes in execute image. |
| `FUN_1000_6A70` named `Render` | Reads HP, compares hit, subtract HP, saturuje on nulu and launch fatal branch. | Proposed name: `ApplyIncomingActorDamage`. |

Podrobnosti: `DOS_519_packed_to_unpacked_register.csv`, `DOS_14_shifted_or_invalid_seeds.csv`.

## 4. Difference V1.9 → V2.0: hit and stored player block

### Size and specifically arrays

| Version | Base block v DS | Length SAVE/LOAD | HP | Difficulty v examined calculation | New timer |
|---|---|---:|---|---|---|
| V1.0 | `3FAC` | `5C` = 92 B | `3FDF` = +33h | `3FD6` = +2Ah | this vložka neprítomná |
| V1.7 | `40C4` | `5C` = 92 B | `40F7` = +33h | `40EE` = +2Ah | this vložka neprítomná |
| V1.9 | `4154` | `5C` = 92 B | `4187` = +33h | `417E` = +2Ah | this vložka neprítomná |
| V2.0 | `4154` | `5E` = 94 B | `4189` = +35h | `4180` = +2Ch | `417A` = +26h, signed word |

Priamy evidence in V2.0: prenosy on `36E9h` and `39E7h` use length `5Eh` and pointer `4154h`. V1.9 on those istých miestach uses `5Ch`. V1.0 are correspond length on `35DBh/38D1h`, in V1.7 on `36EBh/39E9h`.

Reset V2.0 on `A07Ch` zeros 23 dwordov and provided word, total 94 B. On `A0ACh` writes timer `FFFFh`, čiže −1. V1.9 reset `A060h` zeros only 23 dwordov, 92 B.

**Confirmed / High:** size, addresses, initialization and prenos daného block. **Unknown:** complete meaning all others bytes and complete compatibility whole save file. Konvertor nesmie only slepo copy 94 bytes to starého build.

### Order calculation hit

V1.0/V1.7/V1.9:

```text
ak ochranný bajt != 0 alebo režim == 2: návrat
damage = vypočítaj poškodenie aktérom
HP = max(0, HP - damage)
pri smrteľnom zásahu spusti príslušnú smrteľnú vetvu
aktualizuj príslušný panelový údaj
```

V2.0, routine obrazu `6A70h`:

```text
damage = vypočítaj poškodenie aktérom
ak damage != 0: indicator_countdown = 3
ak DS:4151 != 0 alebo DS:3CD4 == 2: návrat
HP = max(0, HP - damage)
pri smrteľnom zásahu spusti príslušnú smrteľnú vetvu
aktualizuj príslušný panelový údaj
```

Write timer is on `6A93h`; ochranné check are up to on `6A99h/6AA0h`. Therefore nonzero result calculation can set indicator also vtedy, when this branch HP nezníži. actual reach during each mode game needs to confirm whole behom. V class use RNG sa during same invoke functions can change also order random odberov; nebolo performed complete comparison DEMO behov.

### Spotreba timer and vykreslenie

Update on `A236h` uses signed comparison. If is timer nonnegative, decrements ho and calls draw dispatcher `980Ch` with code 4, until remains nonnegative, otherwise with code 3.

| Update from set values 3 | New value | Code kreslenia |
|---:|---:|---:|
| 1 | 2 | 4 |
| 2 | 1 | 4 |
| 3 | 0 | 4 |
| 4 | −1 | 3 |
| 5 | −1 | none z this branches |

Code 3 on `98ACh` vyplní rectangle farbou/index 0. Code 4 on `98C6h` obtain farbu for logical index `0Ch` and enter to common path. Parametre are **x=256, y=162, width=62, height=36**. Function `1EA6h` executes výplň on oboch target page through `1E34h`. This nízkoúrovňová routine uses row step 80 B, divide X four and VGA mask through porty `3C4h/3C5h`.

Designation „indikácia hit v areas automapy/HUD“ is support call tokom and coordinate; exact result RGB odtieň and visible effect v original frame remain open. Value 3 is count call this update, nie automatic three frames nor determine count milisekúnd.

## 5. Prichádzajúce damage: vzorec and classes

This calculation belongs zásahom player actor. Is not to evidence complete model player weapon.

| Version | Calculation damage | Helper distance | Round odmocniny |
|---|---|---|---|
| V1.0 | `8350` | `F7E6` | `F786` |
| V1.7 | `866A` | `FB48` | `FAE8` |
| V1.9 | `87CE` | `FCDC` | `FC7C` |
| V2.0 | `87D8` | `FD18` | `FCB8` |

coordinate actor `OBJECT+10h/+12h` sa arithmetic posunú o 6 and subtract sa player tile-based coordinate. Helper count sum square and calls own odmocninu. For doménu coordinates 64×64 map applies `0 <= n <= 7938`, without overflow sum.

```text
q = floor(sqrt(n))
distance = n                         ak n <= 1
distance = q + (n - q*q >= q - 1)   inak
base = 100                          ak distance <= 0
base = 100 / distance               inak, celočíselné delenie
```

For example `(dx,dy)=(1,1)` can n=2 and distance=2; ordinary `floor(sqrt(2))` by dalo 1. During n=5 this function returns 3. Dosadenie normal odmocniny without exact round therefore can change damage.

| OBJECT class | Value before modification difficulty |
|---|---|
| `08` | `RNG & 7` |
| `09`, `0A` | `RNG & 15` |
| `0B` | `base >> 2` |
| `0C`, `1D`, `1E` | `base` |
| `11`, `12`, `13`, `14` | `RNG & 31` |
| `16` | 100, if corresponding word has value 3 or story byte is not zero; otherwise 33 |
| `19` | 100 |
| other including default branches | `base >> 1` |

Difficulty in above listed worde: **0 → value/2**, **2 → value×2**, ostatná value → without modification. Exact prepojenie number items change must remain separate from these internal values. For V2.0 are condition classes `16` on `DS:626A == 3` or `DS:430A != 0`; addresses older build are v `damage_build_map.csv`.

Vzorec and class dispatch sa match during 3 600 test four original machine routines. Distance also odmocnina sa execute original code; only RNG was replaced check návratom 31. To nekontroluje kvalitu nor order odberov actual RNG.

## 6. GUARD: direction, step and cache animations

### Smery and movement steps

| Direction v `GUARD+11h` | Znamienko X | Znamienko Y |
|---:|---:|---:|
| 0 | 0 | −1 |
| 1 | +1 | −1 |
| 2 | +1 | 0 |
| 3 | +1 | +1 |
| 4 | 0 | +1 |
| 5 | −1 | +1 |
| 6 | −1 | 0 |
| 7 | −1 | −1 |

During zero vector sa direction does not change. Routine krokov writes signed bytes `GUARD+13h/+14h`: size nonzero component is **16 during `GUARD+0Ah == 2`**, otherwise **8**. Diagonal has two nonzero component; itself this routine their nenormalizuje. Speed for sekundu thereby still is not determine, because depends from plan update.

| Version | Choice smeru | Calculation krokov | Selektor cache/banky |
|---|---|---|---|
| V1.0 | `4A3C` | `4B98` | `4AB6` |
| V1.7 | `4BBC` | `4D24` | `4C36` |
| V1.9 | `4D20` | `4E88` | `4D9A` |
| V2.0 | `4D20` | `4E88` | `4D9A` |

### Meaning `GUARD+12h`

Selektor computes osemsmerový index:

```text
bias = 3, ak GUARD+0Fh == 0; inak 4
direction = (bias + GUARD+11h - view_helper_result) & 7
ak GUARD+12h == direction a force == 0: návrat
GUARD+12h = direction
vyber banku podľa state/strategy a položku podľa direction
GUARD+00h = vybrané slovo
OBJECT+03h = dolný bajt vybraného slova
```

This is **Confirmed / High** for daného readable/write. Array funguje as cache selection directional animations; named „pain timer“ nevysvetľuje these operations. Does not mean to still, that were verify all its write v each state. Value 8 sa natural differs from each result `&7` and can force restore; complete audit miest set 8 remains role.

### Confirmed difference banky in V1.0

Offset are relative k sequential define; each directional item is word.

| Status / strategy | V1.0 | V1.7, V1.9, V2.0 |
|---|---|---|
| state 6, strategy 2 | banka `+24h` | banka `+04h` |
| state 6, other strategy | banka `+24h` | banka `+24h` |
| state 8, 16, 17 | banka `+14h` | banka `+14h` |
| other examined state | banka `+04h` | banka `+04h` |

768 isolated skúšok verify selection, force flag and repeated usage cache. Orientation helper was set on return 0 and tables obsahovali distinguish synthetic values. Therefore is evidence logic selection, nie evidence complete visual behavior all enemies. next 260 skúšok without replacement callee verify direction and movement step.

## 7. Launch switches

Restore table covers all branches tohto parsera, including reject písmen. Reads `argv[i][0] == '-'` and second znak; itself table nepremieňa large písmená on small.

| Skupina | V1.0 | V1.7 / V1.9 / V2.0 | Finding meaning |
|---|---|---|---|
| `-o` | yes | yes | debug output; confirmed branch and priloženým TECHNOTE |
| `-p` | yes | yes | force PC speaker branches according to TECHNOTE |
| `-q` | **nie** | yes | explicit DSP port v hex and IRQ v dec; two parsované values |
| `-s` | yes | yes | potlačenie autodetekcie sound device according to TECHNOTE |
| `-t` | yes | yes | vypnutie timer interrupt branches; fallback according to TECHNOTE |
| `-x` | yes | yes | vypnutie usage rozšírenej memory according to TECHNOTE |
| `-r` | yes | yes | writes word record branches: in V2.0 `DS:3CD6 = 1`; complete DEMO tok is not nanovo closed |
| `-a` | **nie** | yes | parsovanie to configuration array, in V2.0 `3CDC`; final meaning open |
| `-b/-c/-d/-e/-f/-l/-w` | yes | yes | branches and targets known, nie all semantic meaning closed |

In V2.0 `-q` sets `3CC8=1`, parsuje port to `3CCA` and IRQ to `3CCC`. Formats v DS are `%x` and `%d`; code checks successful oboch konverzií. `-w` parsuje word to `4144`, mask its lower byte value `F8h` and calls next helper. Without rozboru tohto auxiliary sa does not have automatic name its use function.

Documentation source is provided `TECHNOTE.TXT`; is not independent test sound hardvéru. This audit nerobil error input nor beh initialization device.

## 8. Differences provided data

`MAP.1` has v compare folder 90 626 B: 514 B headers and 11 block after 8 192 B. Headers V1.9/V2.0 are identical.

| Mapa | Index cells / column and line file, from 0 | Wall | Object V1.9 | Object V2.0 | Offset cells v MAP.1 |
|---|---|---:|---:|---:|---|
| E1M5 | 2202 / column 26, line 34 | 212 | 0 | 216 | `9336h` |
| E1M5 | 2266 / column 26, line 35 | 212 | 216 | 0 | `93B6h` |

Is move one object, nie two add veci. file coordinate tu use konvenciu `index = row*64 + column`; their orientation relative to game osiam and specific editoru sa thereby nepredpokladá. Class table v `MAP.1` map object 216 on class `27h`. Separate provided `OBJECTS.1` denotes `00D8` as `TRUNK` with opisom `Trunk (Pentagram, Health)`; this name has lower confidence than priamy byte difference, because come from z iného priloženého package.

| File | Observed v provided archive |
|---|---|
| MAP.1 | V1.0/V1.7/V1.9 folder contain same bytes; V2.0 has listed two change whole. |
| IMG.1 | V1.9 1 975 616 B; V2.0 2 244 774 B. Content sa differs, individual change banky still are not complete rozlúštené. |
| UIF.DAT | V1.9 526 520 B; V2.0 528 372 B. Difference is confirmed hashom; meaning all zmien open. |
| SND.DAT | Identical hash in all four folder. To nedokazuje same call events or timing. |
| DEMO.1 | Identical v provided folder V1.7/V1.9/V2.0; v check folder V1.0 is not presence. |
| GAME.PAL | File with this name existuje and has 1 924 B; its origin and role v actual DOS loaderi are not this auditom verify. |

Do not transfer these observed without výhrady on all historical distribuované package. Original combinations EXE + MAP + IMG sa must dokladať separate.

## 9. Structural prechod whole available code

Rekurzívny prechod začal on actual CRT input each unpack image. Track priame calls, obidve branches condition and ohraničené `CS:[BX+table]` dispatch tables. Records contain addresses, bytes, targets and unresolved indirect miesta.

| Build | Candidate input call including štartu | Ohraničené switch tables | Unresolved indirect miesta v this prechode |
|---|---:|---:|---:|
| V1.0 | 516 | 22 | 37 |
| V1.7 | 520 | 22 | 37 |
| V1.9 | 522 | 22 | 37 |
| V2.0 | 522 | 22 | 37 |

**These numbers are not counts completion semantic rozborov nor zaručené counts functions.** Indirect calls, IRQ, address callbacky and nevracajúce sa runtime branches require added. V candidate toku V1.0 are 3 prekryté byte position and in V2.0 4; V1.7/V1.9 v this check prekrytie do not have. To is open check boundaries, nie reason mark entire candidate tok for confirmed code.

Normalize cross-version comparison v `diff_*.csv` and `instruction_map_*.csv` serve on search candidates. Mask relocation values and priame targets row. Match therefore sama nedokazuje same callee, data nor behavior. Exact conclusions above were check separately.

## 10. What remains unknown

Separate register has **40 areas × 4 build = 160 row**. Each states finding, open question and missing type verify. None z these wide areas sa automatic does not denote for 100 % complete.

| Priorita | Area | Specific remain evidence |
|---|---|---|
| P0 | Register code | Complete actual boundary, indirect targets, IRQ and separate data after unpack; fix old names. |
| P0 | GUARD | For each status, strategy and triedu process write → handler → timer → movement → animation → sound. verify LOS, sluch, alarm and bossov. |
| P0 | Collisions and boj | Exact rohy/field player, shift during wall, occupied doors, weapons, projectiles, all HP writery and simulation hits. |
| P0 | USER.SAV | Each field v 92/94 B bloku, other blocks, pointer rebasing and LOAD during animations or letu. |
| P0 | Time, RNG, DEMO | Overall track odberov and call, actual frekvencia, IRQ/field, deterministický replay after change between build. |
| P0 | Renderer | Fixed-point okraje, clipping, wall/sprite shading and original framebuffer compare during same stave. |
| P1 | Walls and skripty | SAFE/TRUNK, ONE_SHOT/SPECIAL1, teleporty, elevator, push exception and all MAP mutation. |
| P1 | Content and data | Meaning difference IMG/UIF, original episodes 2/3 assign ku každému build, unused classes and sequential banky. |
| P1 | Multimedia and DOS | Audio events, WORX/OPL/SB/PC speaker, XMS ownership, input device and restore after error. |
| P1 | Missing release | Original EXE actual V1.8 and next release, for example binary underlying k videám V1.1. |

### Distinguish additional test

1. **Indicator hit V2.0:** set watchpoint on `DGROUP:417A`, stop during `6A93h` and `A236h`, record HP and four subsequent calls update. verify timing and actual farbu/umiestnenie.
2. **Difference animations GUARD:** during same actor set/reach state 6, strategy 2; track banku `+24h` in V1.0 and `+04h` v newer build. Needs to record, whether is takáto combination v corresponding map natural reach.
3. **Save:** save status during active indicator and compare its +26h v player block before/after LOAD. Then rozšíriť test on projectile, doors and GUARD animation.
4. **RNG:** invoke same prichádzajúcu RNG class during active ochrane v starom and novom build and track input to damage/RNG auxiliary. Thereby sa verify consequence move check v whole runtime.
5. **Render:** capture image, palette, position, uhol, status door and corresponding tables v original. Themselves gameplay video nepreukáže pixel identitu.

All addresses tohto documentation are **offset complete image**, if is explicit listed DS or CS:IP. For debugger needs to add actual segment load k relative segment. Absolute addresses z one behu sa must not slepo transfer to iného.

## 11. Range overenia

| Test | Count | What sa actually execute |
|---|---:|---|
| EXEPACK | 4 build | Original dekompresor; zastavenie before CRT, comparison entire image and relocation. |
| Original DIET distribúcie | 4 build | Unpack to EXEPACK and identical final image. |
| Direction and step GUARD | 260 cases | Original small routines without nahradenia callee. |
| Cache and banky GUARD | 768 cases | Original selektor; synthetic tables, orientation helper returns 0. |
| Wrapper damage | 48 cases | Original branches; calculation damage, fatal callee and subsequent update are check replaced. |
| Vzorec damage | 3 600 cases | Original calculation and distance; RNG returns check value 31. |
| Odmocnina | 31 756 vstupov | All 7 939 vstupov 0–7938, osobitne v each builde. |
| New timer | 5 update | Original spotreba timer; calls draw dispatchera capture namiesto rasterizácie. |
| Complete beh game with video/debuggerom | **0** | Nepredstiera sa full runtime verify. |

Isolated test verify specific question. Their sum is not metrika percent completion game. Was not execute inštalácia DOSBoxu nor hranie all map.

## 12. Podklady on next implement

Prepare on usage v corresponding ohraničenom range:

- selection profilu V1.0/V1.7/V1.9/V2.0 according to identity obrazu;
- exact method unpack and restore relocations;
- distinguish 92/94 B player block and timer +26h;
- order ochranných check v incoming-damage wrapperi;
- arithmetic prichádzajúceho damage and own round distance v map doméne;
- map direction, krokov and select bankových right GUARD;
- complete table písmen tohto CLI parsera, with open meaning označenými separate;
- exact difference dvoch buniek provided E1M5.

These results nestačia on verný complete port without next open time. Do not replace all structures, all animations nor all branches game.

**Overall confidence:** high for identity, unpack, listed bytes and performed isolated cases; medium for broader visually and game named; open for natural reach all state, exact time and ekvivalenciu entire behu.

Sprievodný package contains complete unpack image `.image` without MZ headers, relocations, selected assembly listing, candidate grafy, version differences, registers, test and skripty. Files `.image` serve on analysis; are not separate DOS run file.