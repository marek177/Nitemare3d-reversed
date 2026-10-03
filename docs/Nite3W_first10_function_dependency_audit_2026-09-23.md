# Nite3W Win16: hĺbkový audit depend first 10 functions

Date: 2026-09-23

## Range and order

Primary binary file is `nite3w(10).exe`: Windows NE for Windows 3.10, 230 400 bytes, 10 segment, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Použil som dekompilačný export `nite3w110.exe.c`, kandidátsky list `NITE3W_function_candidates.csv` and NE relocation audit. Kódové bytes and relocations som skontroloval directly v EXE.

„First 10“ tu mean first ten items z existing address sort list `FUN_...` for Nite3W 1.10, nie first ten all potenciálnych input bodov v celom binary file. V segment 1 is before nimi still unclosed candidate `1:002E`; v range `1:03E8–1:045B` are also importové skoky and additional possible obálky, which existing `FUN_...` list nepočítal. Therefore sa this report relationship exactly on doloženú desiatku below; globally order all input bodov remains open.

## Finding role this skupiny

First six items is Win16/MFC podporný code for object podobný `CDC` and calls GDI/USER. Functions 7–9 tvoria mechanizmus zisťovania MFC runtime classes and create object through callback. Function 10 is 32-bit DOS seek nad file handle. V this desiatke sa directly did not find game logic GUARD, OBJECT, zbraní nor stien.

## Súhrnná table

| # | Address / exportné meno | Finding usage | Main data or call | Confidence |
|---:|---|---|---|---|
| 1 | `1000:036A` `FUN_1000_036a` | Initializes vptr základného výnimkového object | Far vptr on segment 4, offset `0x48B8`, then `0x48BC` | High for writes; stredne high for name classes |
| 2 | `1000:0388` `FUN_1000_0388` | CDC obálka for `PtVisible` | `this+4` HDC; GDI ordinal `#103` | High |
| 3 | `1000:03A0` `FUN_1000_03a0` | CDC obálka for `RectVisible` | `this+4` HDC; GDI ordinal `#104` | High |
| 4 | `1000:03B8` `FUN_1000_03b8` | CDC obálka for `ExtTextOut` | `this+4` HDC; GDI ordinal `#351` | High for call, medium for exact type argumentov |
| 5 | `1000:0480` `FUN_1000_0480` | CDC obálka for `GrayString` | `this+4` HDC; USER ordinal `#185`; handle z object on poslednom argumente | High for behavior; medium for type object |
| 6 | `1000:04C0` `FUN_1000_04c0` | CDC obálka for `Escape` | `this+4` HDC; GDI ordinal `#38` | High |
| 7 | `1000:068A` `FUN_1000_068a` | Test, whether object belongs to runtime classes or its predka | Far vptr object, first virtuálna item, string descriptorov through `+0x0C` | High for tok; medium for original name methods |
| 8 | `1000:06C0` `FUN_1000_06c0` | Create object z runtime-class descriptoru | Size `+4`, callback `+8/+0x0A`, allocate, CATCH | High for tok; stredne high for name MFC methods |
| 9 | `1000:0730` `FUN_1000_0730` | Calls tvorivý callback descriptoru nad allocate object | Far callback `+8/+0x0A`, second argument is buffer object | High |
| 10 | `1000:07A0` `FUN_1000_07a0` | Seek v file through DOS function `AH=42h` | Handle `BX`, origin `AL`, offset `CX:DX`, result `DX:AX` | High |

## Functions 1–6: constructor and obálky GDI/USER

### 1. `1000:036A` — basic výnimkový object

Function dostane pointer object, writes to its first four bytes far vptr and returns pointer v `AX`. Raw code writes postupne offset `0x48B8` and `0x48BC`; relocations on miestach `segment 1:0377` and `segment 1:0380` ukazujú, that oba segment wordy direction to segment 4. Ide therefore o change vptr, nie o write string.

Dekompilovaný C export incorrectly displays second word as pointer on `No seqdef defined for guard + 0x16`. To odporuje strojovým byte and NE relocation. Meaning „basic constructor výnimkového object“ podporujú call-site functions `1000:4A02` and `1000:4AE6`: obe allocate object, zavolajú this routine, then set additional vptr and doplnia arrays. Allocate size are 6 and 10 bytes. Exact original meno C++ classes needs to still assign k vtable.

**Uses:** parameter pointer on object, immediates `0x48B8` and `0x48BC`, NE segment fixupy to segment 4. **Nevolá** next function and does not change global status.

### 2–6. CDC obálky

All five obálok loads handle z `[this+4]` and pass ho importovanej function Windows. To corresponds to rekonštruovanému `CDC16` record, where is `hDC` on `+4`. Each obálka returns `void`; stackové `RETF n` ukazuje, koľko bytes argumentov uprace call routine.

| Address | Raw usage | Import confirmed NE relocation | Stack cleanup |
|---|---|---|---:|
| `0388` | HDC z `this+4`, two word argumenty | `GDI#103`, exportný symbol `PTVISIBLE`, relocation `1:0398` | `RETF 6` |
| `03A0` | HDC z `this+4`, two word argumenty | `GDI#104`, `RECTVISIBLE`, `1:03B0` | `RETF 6` |
| `03B8` | HDC z `this+4`, ten wordov z argumentového block | `GDI#351`, `EXTTEXTOUT`, `1:03E0` | `RETF 0x16` |
| `0480` | HDC z `this+4`; last argument is nullable pointer, z whose reads word `+4` | `USER#185`, `GRAYSTRING`, `1:04B6` | `RETF 0x16` |
| `04C0` | HDC z `this+4`, six wordov z argumentového block | `GDI#38`, `ESCAPE`, `1:04DC` | `RETF 0x0E` |

During `0480` sa z posledného argumentu loads handle z offset `+4`. To corresponds to `hObject` v object podobnom `CGdiObject16/CBrush16`, but without caller/prototype evidence remains name type derived. Exact C++ signatúry obálok are not safely rekonštruované only z pseudokódu: viacero Win16 far-pointer argumentov sa rozkladá on separate 16-bit words.

V exporte sa for these obálky nenašli priame calls z iných dekompilovaných functions; kandidátsky CSV states during nich nula priamych xrefov. To dokazuje only absenciu priamych kódových odkazov v this exporte, nie nepoužívanie through vtable or table.

## Functions 7–9: MFC runtime classes and vytvorenie object

### 7. `1000:068A` — runtime-class chain test

Input are pointer on object and 16-bit target class descriptor. Function loads far vptr z object on `+0`, calls element virtuálnu item tables and result považuje for runtime-class descriptor. Then compares descriptor with target; during mismatch track word on descriptor `+0x0C`. Ends during match (`AX=1`) or zero odkaze (`AX=0`). Function nepíše to object nor to global memory.

Behavior corresponds to MFC `IsKindOf`-štýlu check: current class or one z its predkov. Original name methods is not v EXE confirmed. V dekompilovanom exporte sa use class ID/offset `0x514`, `0x686` and `0x5BC`; their names class still are not assign.

### 8. `1000:06C0` — allocate and create runtime object

Function dostane pointer on descriptor. Z array `descriptor+4` loads 16-bitovú size and calls `FUN_1008_5FE0`; that vedie on `FUN_1008_5AB0`, which uses Win16 `LOCALALLOC`, opakuje pokus through global allocator callback and zeros zero requirement on size on 1 byte. Free through `FUN_1008_5FD0` vedie on `LOCALFREE`.

After allocate calls `FUN_1000_0730(descriptor, object_buffer)`. If descriptor does not have callback, free buffer and returns null. If callback existuje and dokončí sa, returns buffer. Okolo create uses `FUN_1000_4422` and `FUN_1000_4446` on message exception-chain record v global `DAT_1048_41B8` and Win16 KERNEL import `#55` (`CATCH`). During výnimke sa restores exception chain, allocate sa free and result is null.

### 9. `1000:0730` — callback runtime classes

Raw strojový code reads dvojwordový far callback on descriptor `+8/+0x0A`. If is pointer zero, returns `0`. If existuje, calls ho far-callom and pass mu second argument, allocate buffer object; then returns `1`. `RETF 4` confirms two 16-bit argumenty.

Dekompilovaný export display only one argument and older working name naznačoval deštruktor. Raw call z `06C0` also `RETF 4` these interpretácie opravujú: is to tvorivý/konštrukčný callback runtime descriptoru, nie deštruktor.

### usage part runtime descriptoru

| Offset | Finding z these functions | Status |
|---:|---|---|
| `+0x00..+0x03` | Functions 7–9 this range nečítajú; probable class-name or descriptor pointer | Unknown v this audite |
| `+0x04..+0x05` | Size allocate object | Confirmed function 8 |
| `+0x06..+0x07` | These functions nečítajú | Unknown |
| `+0x08..+0x0B` | Far callback: low word on `+8`, segment word on `+0x0A` | Confirmed raw far-callom in funkcii 9 |
| `+0x0C` | Reference on základnú runtime class; function 7 track word on this offset | Confirmed as chain link; plný pointer/segment behavior still verify |

## Function 10: DOS seek

### `1000:07A0` — seek and result 32-bitovej position

Function dostáva far pointer on 4-byte output, origin seeku, low and high word offset and file handle. Najprv writes to output `0xFFFF:0xFFFF`. Then sets `AH=0x42`, `AL` loads z argumentu pôvodu, `DX` z nízkeho offset wordu, `CX` z vysokého wordu and `BX` z handle. Calls Win16 KERNEL ordinal `#102` through DOS3CALL path. This is DOS seek `INT 21h/AH=42h`.

If sa sets Carry Flag, ponechá sentinel and returns DOS error code v `AX`. During success stores `AX` on output `+0`, `DX` on `+2` and returns nulu. `RETF 0x0C` confirms celkom 12 bytes argumentov. Call-site functions `1000:0A72` and `1000:0AA8` dopĺňajú handle z file object on `+4`; second uses origin `1` and zero offset, what corresponds to finding current position.

## Zrekonštruované objects and type

| Working type | Array | Evidence and boundary istoty |
|---|---|---|
| `CDC-like Win16 object` | far vptr on `+0`; HDC on `+4` | `0388–04C0` directly read `this+4`; `CDC16` header states `hDC` on `+4`. `hAttribDC` on `+6` is v header, but this desiatka ho does not use. |
| `RuntimeClass-like descriptor` | size `+4`, factory callback `+8/+0x0A`, base link `+0x0C` | Priame prístupy functions 7–9. Exact layout arrays `+0` and `+6` z this desiatky neurčíme. |
| `Exception-like object` | far vptr on `+0`; size allocate 6 or 10 bytes v dvoch caller function | Strong link on výnimkovú tvorbu; original names class and meaning all tail fields remain TBD. |

## Register, stack and locally working values

| Function | Important input/registery | Locally or temporary values | Output |
|---|---|---|---|
| `036A` | `BP+6` → object pointer; `BX` drží its near offset | None meaning local premenná | `AX=BX`, uprace 2 bytes argumentu |
| `0388`, `03A0` | `BP+6` → CDC-like `this`; `BP+8/+0A` → two word argumenty | `BX=this` | void; upracú 6 bytes |
| `03B8` | `BP+6` → `this`; `BP+8…+1A` → ten wordov | `BX=this` | void; uprace `0x16` bytes |
| `0480` | `BP+6` → `this`; `BP+1A` → nullable pointer | `SI` drží pointer, `DI` word handle z `SI+4` | void; uprace `0x16` bytes |
| `04C0` | `BP+6` → `this`; `BP+8…+12` → six wordov | `BX=this` | void; uprace `0x0E` bytes |
| `068A` | `BP+6` → object, `BP+8` → target class offset | `DI` object; `SI` current descriptor; `DX` target | `AX=0/1`; uprace 4 bytes |
| `06C0` | `BP+6` → runtime-class descriptor | 30-byte stack frame; local on catch record; word on allocate buffer; result/error word | `AX` object pointer or 0; uprace 2 bytes |
| `0730` | `BP+6` → descriptor; `BP+8` → object buffer | `SI` descriptor; callback far pointer on `SI+8` | `AX=0/1`; uprace 4 bytes |
| `07A0` | Far pointer on output `BP+6/+8`; origin `+0A`; offset low/high `+0C/+0E`; handle `+10` | Output sentinel `FFFF:FFFF`; `BX/CX/DX/AX` set DOS seek | `AX=0` during success, DOS code during error; uprace `0x0C` bytes |

## Confirmed, derived and open

**Confirmed raw byte/relocation:** addresses and základné boundary routines; CDC HDC read `+4`; GDI/USER import ordinals; runtime chain read `+0x0C`; descriptor size `+4`; callback far-call `+8/+0x0A`; KERNEL `#55` CATCH; DOS seek `AH=42h`, return through CF and write `DX:AX`.

**Strong derived:** function 1 is basic výnimkový constructor; functions 7–9 tvoria MFC runtime-class/object-creation path; `0480` dostáva object podobný `CBrush` and extrahuje its handle. Rekonštruovaný header identify MFC 2.5 (`_AFX_VERSION == 0x0250`), what supports class map, nie however original names all class.

**Additional unknown on rozriešenie:**

1. Whether `segment 1:002E` is real function, table or data; rozhodnúť also boundary possible obálok `03E8–045B` and thereby close actual first desiatky input bodov.
2. assign original MFC class names k vtable offsetom `segment 4:48B8/48BC` and class descriptorom `0x514`, `0x686`, `0x5BC`.
3. Z callers or runtime trace odvodiť exact logical prototypy piatich CDC obálok; obzvlášť type posledného argumentu `GrayString`.
4. verify, whether GDI obálky without priamych xrefov are usage through tables/vtable or is nevolaný MFC code.
5. Run Win3.11 debugger trace for create callback and DOS seek: record class descriptor, far pointer, CF, DOS error code and output `DX:AX`.

## Zdroje evidence

- `nite3w(10).exe`, NE segment 1, physical offset `0x04C0`, SHA-256 listed above.
- `nite3w110.exe.c`, dekompilované functions `FUN_1000_036a` up to `FUN_1000_07a0`; names and type z exportu sa accept only after check raw code.
- `Nitemare3D_nite3w_xref_audit_2026-09-22.zip`, `ne_relocation_sites.csv`: importy GDI/USER/KERNEL and segment fixupy.
- `NITE3W_function_candidates.csv` and `Nitemare3D_first_400_DOS_and_first_400_Nite3W.md`: existing order element desiatky and direct XREF indikácie.
- `Nite3W_MFC25_class_reconstruction.hpp`: rekonštruovaný MFC 2.5 `CDC16` layout.

**Overall confidence:** high for strojové operations, import ordinals, usage offset and DOS seek protokol; medium for original names C++ class/method and exact prototypy Win16 GDI wrapperov. Complete order all candidate input bodov still is not closed.