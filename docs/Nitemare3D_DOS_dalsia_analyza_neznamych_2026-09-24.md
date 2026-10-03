# Nitemare3D — next analysis unknown v DOS buildoch

Date: 24. 9. 2026. Nadväzuje on `Nitemare3D_MSDOS_all_available_versions_audit_2026-09-24.md`.

**Result:** new analysis and 501 úspešných izolovaných scenarios objasnili load palette, two different methods selection farieb, XMS interface and prenosy, jednu incorrect hraničnú branch XMS, CONFIG.SAV and additional switches. This is not completion analysis celej game nor all historical vydaní.

## 1. Range and rules evidence

Pracoval som directly with štyrmi completely rozbalenými DOS image verify v predchádzajúcom audite. Names file nor old dekompilované names functions sa nepoužili as evidence their meaning.

| Build | Size obrazu | SHA-256 obrazu |
|---|---:|---|
| V1.0 | 154 448 B | `113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a` |
| V1.7 | 170 848 B | `df85d457e752860dc8fc8c39c4c36ba1c62f03b0e704f1365ee618d8ed8447ff` |
| V1.9 | 171 296 B | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |
| V2.0 | 171 360 B | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |

Addresses code below are hexadecimálne **offset v rozbalenom load image**, nie offset v zabalenom EXE. `DS:xxxx` denotes address v DGROUP specific build. Its relatívny segment is postupne `2360`, `2754`, `276D`, `2771`; during actual run needs to pripočítať load segment.

- **Confirmed staticky:** specifically instructions, riadiaci tok, data reference or bytes file.
- **Confirmed izolovane:** performed original x86 instructions v Unicorn; náhrady systémových služieb are explicitly listed.
- **Derived:** meaning follows z multiple nadväzujúcich evidence; case game consequence can require entire beh.
- **Open:** evidence so far missing. Automatické matching functions nor count test ho nenahrádzajú.

Win16 sa v this pokračovaní znovu nerozoberal. Results sa naň automaticky neprenášajú. actual separate DOS V1.8 still is not k dispozícii. Older formuláciu, that candidate `N3D(5).EXE` was compare only partially, already previous DOS audit prekonal: its complete result image sa match with V1.9.

## 2. GAME.PAL: exact source farieb is already známy

In all four buildoch load executes:

1. Opens doslovný name `game.pal`.
2. Presunie position o **−768 bytes from konca file**.
3. Loads 768 individual bytes and each stores after operation `value >> 2`.
4. Writes zero index to portu `03C8h` and 768 result zložiek to `03C9h`.
5. Calls initialize map 16 logical farieb and file zavrie.

Provided GAME.PAL have 1 924 bytes, therefore palette starts on offset **1 156 / 0484h**. SHA-256 each z these four file is `efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f`. Prefix 1 156 bytes this load does not use; its entire format thereby is not objasnený.

| Build | load | Array 768 zložiek | Write to DAC | Map 16 farieb |
|---|---|---|---|---|
| 1.0 | `29BA` | `DS:48BA` | `167C` | `289C` |
| 1.7 | `2A16` | `DS:49D2` | `168A` | `28F8` |
| 1.9 | `2A16` | `DS:4A62` | `168A` | `28F8` |
| 2.0 | `2A16` | `DS:4A64` | `168A` | `28F8` |

Izolovaný test execute actual load, prevod also slučku OUT. Nahradené were operations open, seek, read and close; return actual bytes corresponding GAME.PAL. Capture sa exact track 769 portových write. Physical VGA card nor entire program sa nespúšťali.

**Correction previous state:** GAME.PAL already is not only found, but its usage and result color zložky are verify. Historical right entire distribučného package remains separate question.

## 3. Game uses two rozdielne methods selection colors

### Logical colors interface

For 16 target RGB trojíc sa prehľadá all 256 farieb. Selects sa najmenšie:

`(R − r)² + (G − g)² + (B − b)²`

During equal remains first, therefore najnižší index. Is not sum absolútnych difference. call helper actually multiplies value samu sebou (`IMUL`); skorá working hypotéza o absolútnej value was test vyvrátená and corrected.

Targets 0–7 use zložky 0 or 42, with výnimkou colors 6 = `(42,21,0)`. Targets 8–15 use 21 or 63. Bits 4/2/1 určujú R/G/B.

Result for provided palette is in all build same:

| Logical index | Index palette | Logical index | Index palette |
|---:|---:|---:|---:|
| 0 | 0 | 8 | 10 |
| 1 | 192 | 9 | 208 |
| 2 | 254 | 10 | 255 |
| 3 | 209 | 11 | 221 |
| 4 | 112 | 12 | **161** |
| 5 | 239 | 13 | 61 |
| 6 | 149 | 14 | 175 |
| 7 | 20 | 15 | 31 |

Jednorazová initialize branch clear flag cache and naplní 16-byte table. During vymazanom flag additional call only returns stored index. Complete uzavretie all indirect writerov flag sa netvrdí.

### Stmavovacia table

This routine najprv subtracts from each zložky colors value according to level and result obmedzí zdola nulou. Najbližšiu farbu then selects according to:

`abs(R − r) + abs(G − g) + abs(B − b)`

Opäť vyhráva first index during equal. result is 256-byte table remapovania.

| Level | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Subtract value | 0 | 4 | 8 | 12 | 16 | 20 | 30 | 40 |

| Build | Routine | Selektor level | Output table |
|---|---|---|---|
| 1.0 | `16C0` | `DS:60CE` | `DS:D052` |
| 1.7 | `16CE` | `DS:61E6` | `DS:D17A` |
| 1.9 | `16CE` | `DS:6276` | `DS:D20A` |
| 2.0 | `16CE` | `DS:6278` | `DS:D20C` |

Execute was all eight úrovní × four build, always with check all 256 output index. During this routine was not nahradený none helper.

**Consequence for reconstruction:** obe search cannot zlúčiť to jednej „najbližšej colors“ without zachovania difference metriky.

### Spresnenie indikátora hit in V2.0

Previous audit identify logical farbu 12 v obsluhe indikátora. Teraz vieme, that with provided GAME.PAL sa map on **index 161**, whose 6-bit RGB is **`(63,21,15)`**. Applies to for load základnú palette; prechodné fade/flash change physical palette and result image during prirodzenom hit remain neoverené.

## 4. Six indirect miest belongs XMS ovládaču

Address ovládača pochádza z `INT 2Fh`, `AX=4310h`; predtým prebehne detekcia with `AX=4300h`. Detektor checks bit `80h` v AL, nie exact equal AL with `80h`.

Six miest calls this far pointer with funkciami:

| AH | Role | Result wrappera during success |
|---|---|---|
| `08` | Najväčší free XMS block | `DX:AX = 0 : count KiB` |
| `09` | Allocate | `DX:AX = 0 : handle` |
| `0A` | Free | `DX:AX = 0 : 0` |
| `0B` | Prenos | `DX:AX = 0 : 1` |
| `0C` | Uzamknutie | Physical address prenesená to `DX:AX` |
| `0D` | Odomknutie | `DX:AX = 0 : 1` |

identify ABI is verify also relative to original špecifikácii Microsoft/Lotus/Intel/AST, **XMS 3.0, január 1991**, archivovanej on [Metropoli BBS](https://files.mpoli.fi/unpacked/software/programm/general/gcgpe10.zip/xms30.txt). Is primary dokument uchovaný on zrkadle.

| Build | Detekcia | Far pointer v DS | Query / Alloc / Free / Move / Lock / Unlock |
|---|---|---|---|
| 1.0 | `7980` | `33B2` | `79A6 / 79BE / 79E0 / 79FA / 7A22 / 7A40` |
| 1.7 | `7C96` | `3480` | `7CBC / 7CD4 / 7CF6 / 7D10 / 7D38 / 7D56` |
| 1.9 | `7DFA` | `350C` | `7E20 / 7E38 / 7E5A / 7E74 / 7E9C / 7EBA` |
| 2.0 | `7E04` | `350E` | `7E2A / 7E42 / 7E64 / 7E7E / 7EA6 / 7EC4` |

During error sa code BL presúva to DH and AX is zero. Allocate wrapper pritom **nevymaže DL**; low byte can zostať z návratu ovládača. Return therefore cannot bezpodmienečne modelovať as exact `error << 24`. call path skúma znamienko DX.

Move wrapper temporary sets DS:SI on move record and calls ovládač through ES, where si preserves original data segment. DS also SI subsequently restores.

**Status inventory:** z original 37 indirect miest on build is teraz six klasifikovaných as XMS calls. **31 remains v this pokračovaní neklasifikovaných.** Function count sa thereby does not determine; physical address ovládača vzniká up to during behu. Other memory path libraries WORX sa thereby automaticky neuzatvárajú.

## 5. Confirmed hraničná branch XMS during 32 MiB

Initialize code pracuje with počtom KiB v AX, but compares ho podpísanými skokmi `JLE/JGE`.

| Najväčší free block return function 08h | Behavior this initialize path |
|---|---|
| 0–63 KiB | XMS vypne |
| 64–2 048 KiB | Pokúsi sa allocate danú size |
| 2 049–32 767 KiB | Pokúsi sa allocate 2 048 KiB |
| **32 768–65 535 KiB** | Value sa vyhodnotí as negative and **XMS vypne** |

Condition sa týka **najväčšieho free block return ovládačom**, nie overall nainštalovanej RAM.

If allocate failure, path XMS sa vypne. If failure lock, game calls free on already získaný handle, vypne XMS and prejde through debug message o neúspešnom uzamknutí. Success uchová flag for subsequent cleanup.

verify: nine values size × three results ovládača × four build = **108 scenarios**. Running was original end initialize from check zapnutia XMS after save result flag. INT 2Fh, ovládač and debug listing were nahradené row návratmi; previous konvenčné allocate were not part of tohto test.

**Confidence:** strojová branch and its result are confirmed. To, which real historical ovládač v ktorej konfigurácii returns danú vysokú value, sa netestovalo. Is not evidence pádu celej game during 32 MiB RAM.

## 6. XMS cache prenáša entire kilobajty

Oba move helpery count:

`transfer_bytes = 1024 * ((requested_bytes + 1023) // 1024)`

Input length is neznamienkové 16-bit word, but add and divide v this path zachovajú rozšírenú value. Requirement 65 535 bytes tak creates prenos 65 536 bytes.

**Write to XMS:** skontroluje `used_KiB + needed_KiB <= capacity_KiB`. If sa nezmestí, returns `DX:AX = FFFF:FFFF` and ovládač nevolá. Otherwise pripraví 16-byte move record, prenesie data on `used_KiB * 1024`, zväčší used and returns original byte offset.

**read z XMS:** pripraví opačný move z provided offset to konvenčného far pointer. This helper itself does not use same check used/capacity and does not change used.

| Offset record | Size | Meaning |
|---|---:|---|
| `+00` | DWORD | Zaokrúhlený count bytes |
| `+04` | WORD | Source handle; 0 for konvenčnú memory |
| `+06` | DWORD | Source offset or zabalený segment:offset |
| `+0A` | WORD | Destination handle; 0 for konvenčnú memory |
| `+0C` | DWORD | Destination offset or zabalený segment:offset |

| Build | Write / read | Handle | Capacity KiB | usage KiB |
|---|---|---|---|---|
| 1.0 | `753A / 75F6` | `DS:33AA` | `DS:33AC` | `DS:33AE` |
| 1.7 | `77A6 / 7862` | `DS:3478` | `DS:347A` | `DS:347C` |
| 1.9 | `790A / 79C6` | `DS:3504` | `DS:3506` | `DS:3508` |
| 2.0 | `7914 / 79D0` | `DS:3506` | `DS:3508` | `DS:350A` |

confirm is 192 scenarios including 0/1/1 023/1 024/1 025/3 072/8 192/65 535 bytes and prekročenia kapacity. Check sa entire pass record and change read; itself physical prenos execute nahradený ovládač.

**Open:** size and lifetime each caller bufferu, complete ownership cache, all eviction branches and fallback on disk. Zaokrúhlený prenos can read/write viac than logical length data; without auditu specific allocate sa z toho nesmie vyhlásiť pretečenie bufferu.

## 7. CONFIG.SAV has separate 16-byte block

| Build | load | Start bloku |
|---|---|---|
| 1.0 | `32F0` | `DS:3F9C` |
| 1.7 | `33E0` | `DS:40B4` |
| 1.9 | `33DE` | `DS:4144` |
| 2.0 | `33DE` | `DS:4144` |

Is not player block USER.SAV size 92/94 bytes. Defaultný content is in all four build:

`30 01 00 00 32 32 3C 46 01 01 01 00 00 00 00 00`

| Relatívny offset | Type | Default | Meaning / status |
|---|---|---:|---|
| `+00` | WORD | 304 | Width game výrezu |
| `+02` | WORD | 0 | **Unclosed.** Initializes and serializuje sa, priamy separate spotrebiteľ v preskúmanom CFG nenájdený |
| `+04` | BYTE | 50 | Value ovládača Mouse; spotrebovaná škálovacím helperom |
| `+05` | BYTE | 50 | Value ovládača Joystick; spotrebovaná škálovacím helperom |
| `+06` | BYTE | 60 | Value hlasitosti Music |
| `+07` | BYTE | 70 | Value hlasitosti Sound FX |
| `+08` | BYTE | 1 | Zapnutie Mouse |
| `+09` | BYTE | 1 | Zapnutie Music |
| `+0A` | BYTE | 1 | Zapnutie Sound FX |
| `+0B` | BYTE | 0 | Zapnutie Joystick |
| `+0C` | BYTE | 0 | UI choice „Omniscient (all-knowing)“ |
| `+0D` | BYTE | 0 | UI choice „Omnipotent (all-powerful)“; známa condition potlačenia damage |
| `+0E` | BYTE | 0 | UI choice „Omnifarious (all things)“ |
| `+0F` | BYTE | 0 | UI choice „Omnificent (all-cunning)“ |

assign name opiera static code o actual 18-byte menu records and far pointer on text; evidencia contains 32 takých väzieb across build. Itself name cheatu sa nepovažuje for complete opis its game účinkov.

Specifically V2.0: Mouse and Joystick helpery `709A / 70B8` use different divide 50 and 200 and upper obmedzenie derived z druhého input. Music and Sound FX path `C35A / C700…` prevádzajú zadanú value multiply 15 and divide 100. Their exact zariadenie and all boundary input are not this rozborom complete test.

load najprv writes defaulty. File process, only if open returns handle **väčší than nula**. During inom result ostanú defaulty; zvlášť sa verify also return handle 0. Prijatý file must mať exactly 16 bytes, otherwise sa calls error path. Then sa loads block, file zavrie and prepočítajú sa rozmery.

Test pokryli missing file, handle 0, valid change block and size 15/17 bytes. During nesprávnej size sa test zastavil during input to error routines; netvrdí sa verify entire terminate programu.

## 8. Meaning next CLI switch

| Switch | New conclusion | Range evidence |
|---|---|---|
| `-a prefix` | Prefix path for configuration/save path, connect doslova before name | Constructor execute in V1.7/1.9/2.0; in V1.0 switch missing |
| `-w n` | Width game výrezu; parser clear lower three bits | Parser static, geometria also its math auxiliary execute v four build |
| `-d n` | Level stmavovacej tables | Parser → field → selektor → verify routine in all four |
| `-f n` | Index palette for lower field pozadia, therefore podlahu | Writer and dvojica upper/lower VGA fill priechodu static in all four |
| `-c n` | Index palette for upper field pozadia, therefore strop | Same string evidence; uses low byte values |
| `-e n` | Value episodes | V2.0 parser `4B82`, odovzdanie through `4C59`, menu/start → episode argument level loadera |
| `-l n` | Požadované level number; during štarte sa subtracts 1 | V2.0 `4B94`, `FAA1…`, loader `DBEA` writes result to `DS:626C` |
| `-b` | Flag prenášaný to úvodnej/menu and terminate path | Exact user purpose **remains open**; nenazýva sa without evidence „benchmark“ nor „skip menu“ |

### Prefix cesty

Test confirm `SAVE\` + `user.sav` → `SAVE\user.sav`, but also `SAVE` + `user.sav` → `Save.sav`. Oddeľovač sa itself nepridáva. Constructor does not have v preskúmanom tele check length. Neodporúča sa z toho odvodzovať kapacitu bufferu without complete layoutu.

In V2.0 sa prefix preukázateľne uses during config load/write and generických save/read helperoch (`341D`, `347F`, `34BE`, `35B3`, `38F4`). load GAME.PAL opens directly `game.pal`; `-a` therefore cannot opísať as general directory all assetov.

### Geometria výrezu

For width `w` routine odvodí:

`height = w >> 1`, `left = (320 − w) >> 1`, `top = left >> 1`.

Nasledujú right/lower okraje and stredy. During obvyklom `w=304` is výrez 304×152, left upper roh `(8,4)`, right lower `(311,155)` including. Výpočty use arithmetic posuny and 16-bit save; complete verify behavior all possible slov sa netestovalo.

Itself parser `-w` nor this prepočet v skúmanej path neobmedzuje value on normal range. Test `w=328` compute negative left and upper coordinate. To is evidence math path, nie confirmation correct render invalid konfigurácie.

During `-d` is table define for 0–7. V preskúmanom nadväzujúcom read is not upper check index. During `-c/-f` sa uses low byte, without konverzie through map 16 logical farieb. Normálne fallbacky are level 2, podlaha 2, strop 7; iná game branch can these set prepísať.

## 9. verify and opakovateľnosť

| Skript / area | Scenario | What was nahradené |
|---|---:|---|
| `palette_test.py` | 52 | During loaderi DOS file I/O; porty capture. Logical map and shade routine without náhrad |
| `xms_test.py` | 96 | INT 2Fh and XMS ovládač |
| `xms_transfer_test.py` | 192 | XMS ovládač; checks sa pripravený move record, nie physical RAM |
| `config_test.py` | 53 | DOS file I/O for config; path/viewport math without náhrad |
| `xms_init_tail_test.py` | 108 | INT 2Fh, XMS ovládač and debug listing; execute only zvolený end initialize |
| **Total** | **501** | **None complete beh game nor actual ovládač** |

Package contains test, original rozbalené image, small párové GAME.PAL, needed CFG CSV, address výpisy, results, manifest SHA-256 and README with command. usage libraries: Capstone 5.0.7, Unicorn 2.1.4. Test nevykonávajú original proces from input bodu after gameplay.

Each count denotes specifically test scenario. Is not to count objasnených functions nor percento pochopenia game.

## 10. What still remains unknown

Update register preserves all **40 areas × 4 build = 160 row**. These areas are not umelo marked as hotové after rozbore one auxiliary.

Najdôležitejšie open celky:

- Complete GUARD graf state, strategy, LOS/sluch, all writery state and their prirodzená reach.
- Collisions player, door and projectile including rohov, block, damage poradia and complete výpočtu zásahov zbraní.
- All USER.SAV arrays, rebasing, boundary block and restore during active animation/projectile.
- RNG spotreba, seed/reset, IRQ/field, DEMO record and deterministické playback.
- Entire rasterizer, clipping, UV, sprite/wall order, fade effect and pixel match framebufferu.
- Complete memory/cache lifetime, disk fallback and remain 31 neklasifikovaných indirect miest on build.
- All zariadenia, input hrany, audio priority, WORX/IRQ cleanup and error terminate.
- Detailná semantic `CONFIG.SAV +02`, all effect cheatov, `-b` and all incorrect CLI input.
- IMG/UIF/SEQDEF differences, párové E2/E3 package ku každému EXE and historical vydania, which are not provided.

Najbližšie specifically nadväzujúce steps are ownership cache nad confirm XMS helpermi, čitatelia and writery config/save fields and reach AI prechody. For hardvérové and time questions needs to row entire beh with identify EXE, dátovým package and record events.

**Conclusion:** pribudli reprodukovateľné new evidence, including specific XMS hraničnej errors. Is not podklad on tvrdenie „everything unknown vyriešené“ or „the entire game zrekonštruovaná“.