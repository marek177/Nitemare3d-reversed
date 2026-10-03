# Nite3W 1.10 — audit according to check list functions and analysis unknown

Date: 2026-09-23  
Platform: Win16 / Windows 3.x NE  
Primary file: `nite3w(10).exe`  
SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`

## Finding

During opätovnej check surových bytes segment 1 sa podarilo opraviť three important medzery v list functions:

- `1:002E` is farový pointer to segment 3 on `3:00C8`, nie start functions.
- V areas `1:03E8–1:047F` are two 6-byte virtuálne dispatch thunky and three separate text methods: `Text`, `TabbedTextOut` and `DrawText`.
- Methods with zero počtom priamych call have farové references z tabuliek v segment 4. „0 direct XREF“ therefore does not mean „does not use sa“.

All 12 areas z priloženej tables som aplikoval on this skupinu. Prehľad below oddeľuje to, what dokazujú bytes and relocations, from name class and behového behavior, which still require confirmation.

## Range and origin evidence

Check binary file has 230 400 bytes and is NE executable file for Windows 3.x (3.10), with 10 segment. `nite3w(20260921-205703).exe` has totožný SHA-256, therefore is same content. Segment 1 sa v file starts on physical offset `0x04C0`; its addresses `segment:offset` possible therefore directly check proti výpisu bytes.

usage podklady: raw bytes EXE, NE relocation audit, `NITE3W_function_candidates.csv`, dekompilačný export `nite3w110.exe.c`, existing audit first desiatich functions, rekonštruovaná header MFC 2.5 and current hlboké/main audity Nitemare3D.

Inventory states 967 deklarovaných functions for Nite3W 1.10. Existing audit hovorí, that all were assign k probable subsystému, pričom first 200 dostalo detailnejší manuálny audit and neskoršie parts sa analyzovali after vybraných témach. identify between version is evidence identity, nie complete evidence behavior. This dokument therefore neoznačuje all 967 functions for preverené všetkými 12 bodmi.

## New reconstruction

### 1. `1:002E` — pointer, nie telo functions

On offset `1:002E` lies word `0x00C8`. Following word on `1:0030` has NE internú relocation to segment 3. On disku contains `0x003A`, what is next článok relocation string, nie konečný segment selektor. After load tak vznikne farový reference on offset `0x00C8` v segment 3.

V existing handlerových finding is `1010:00C8` rekonštruovaná method `CNite3DApp::OnAppAbout`. Okolitý block contains MFC command/message-map data. Exact name array, to whose pointer belongs, needs to still confirm decode entire MFC record, but function boundary on `1:002E` is vyvrátená.

**Consequence:** item `1:002E` v kandidátskom CSV needs to preradiť z candidates on function on relocation data pointer.

### 2. `1:03E8` and `1:03F4` — virtuálne dispatch thunky

Obe routines have same 6-byte tvar:

1. Zoberú `this` z `SS:[SP+4]` — during farovom call lies for 4-byte return address párom.
2. Through object load its farový vptr helper `LES`.
3. Urobia farový indirect skok on virtuálnu item vtable.

Differences:

| Address | Vtable displacement | Address next target |
|---|---:|---|
| `1:03E8` | `+0x7C` | depends from vptr object |
| `1:03F4` | `+0x78` | depends from vptr object |

Is dispatch adaptéry, nie o normal bodies with own state logic. Their corresponding classes and konečné virtuálne targets sa určia up to after find object, ktorých vptr sa uses during call.

V dátovom block during string `CWnd` on `1:059E` are farové pointer on `1:03F4` and `1:03E8` (pointer offset `1:05B4` and `1:05BE`). To viaže thunk-y on MFC runtime/message-map area. First wordy during record are `0x0001` and `0x0002`, after nich nasleduje `0x000A`; exact meaning entire record and original names handlerov ponechávam open.

### 3. `1:0400` — `CDC`-like wrapper nad `GDI#33`

Telo siaha from `1:0400` after `RETF 0x0C` on `1:041E`. Code:

- loads object z `BP+6`,
- z array `this+4` loads HDC,
- prenesie five 16-bit argumentových slov,
- calls import `GDI#33` during `1:0419`.

Structure zásobníka sa exactly match with `Text(hdc, x, y, lpString, count)`: HDC + x + y + dvojwordový farový pointer on string + count znakov. Win16 map GDI denotes ordinal 33 as `Text`; type and count argumentov correspond also interface this functions. Function preserves return v `AX`, which pochádza z GDI calls.

**Confidence:** high for obal TextOut and arrays object; original meno classes is derived.

### 4. `1:0422` — `CDC`-like wrapper nad `USER#196`

Telo starts on `1:0422`, calls `USER#196` through relocation on `1:044B` and ends `RETF 0x16` on `1:0458`. Code prenesie HDC z `this+4` and nine 16-bit slov z argumentov.

First nine slov after HDC sa rozkladá on:

`x, y, lpString (far pointer), chCount, nTabPositions, lpnTabStopPositions (far pointer), nTabOrigin`.

Win16 USER ordinal list map `USER#196` on `TabbedTextOut`. Its 8-parametrová signatúra corresponds to exactly count slov v surovom call. API returns packed 32-bit rozmery; code stores `AX` to `[SI]`, `DX` to `[SI+2]` and returns `SI`. To corresponds to hide output bufferu for 4-byte result type `CSize`-like, no specific MFC type needs to confirm through caller.

Function neoveruje pointer `SI` before write. If API returns nulu, stores sa nula to oboch field result and returns sa pass buffer. Interface TabbedTextOut dovoľuje zero count tab-stopov with zero pointer; v this case sa uses predvolený interval eight priemerných šírok znaku.

**Confidence:** high for API and data tok; medium for exact return C++ type.

### 5. `1:045C` — `CDC`-like wrapper nad `USER#85`

Telo siaha from `1:045C` after `RETF 0x0E` on `1:047D`. Z `this+4` loads HDC and prenesie six argumentových slov. Relocation on `1:0478` direction on `USER#85`; Win16 USER ordinal list map this ordinal on `DrawText`. Stack shape sedí on HDC, text far-pointer, count znakov, RECT far-pointer and format mask. Return value API remains v `AX`.

### 6. Methods v pointer table segmentu 4

NE interné relocations v segment 4 contain repeated farové references on methods v segment 1:

| Method | Field pointer v segment 4 |
|---|---|
| `1:0388` | `4:4F88`, `4:5004`, `4:5080`, `4:50FC`, `4:4D14` |
| `1:03A0` | `4:4F8C`, `4:5008`, `4:5084`, `4:5100`, `4:4D18` |
| `1:03B8` | `4:4F94`, `4:5010`, `4:508C`, `4:5108`, `4:4D20` |
| `1:0400` | `4:4F90`, `4:500C`, `4:5088`, `4:5104` |
| `1:0422` | `4:4F98`, `4:5014`, `4:5090`, `4:510C` |
| `1:045C` | `4:4F9C`, `4:5018`, `4:5094`, `4:5110` |
| `1:0480` | `4:4FA0`, `4:501C`, `4:5098`, `4:5114` |
| `1:04C0` | `4:4FA4`, `4:5020`, `4:509C`, `4:5118` |

Four paralelné blocks have same order text/GDI obalov. Next block on `4:4D14` references on skoršie obaly, but v check relocation list neobsahuje trojicu `0400/0422/045C`. To is strong evidence pointer tabuliek for viac CDC-type class; their exact names and link on konštruktory needs to still add.

## Aplikácia 12 bodov check list

| Area | Finding for this skupinu | What remains unknown |
|---|---|---|
| **Identita** | SHA-256, NE format, platform, segment and boundary new telies are verify v specific file. | Complete order all actual input bodov and exact boundary each kandidáta mimo this areas. |
| **Interface** | Stack offset, `RETF` cleanup, HDC `this+4`, import ordinals and TabbedTextOut hidden output buffer are rekonštruované. | Caller-side prototyp and exact C++ return type `TabbedTextOut`; original declaration MFC wrapperov. |
| **Členstvo v class** | HDC on `this+4` sedí on `CDC16`-like layout. Relocations ukazujú repeated method tables; thunk-y sa branch through vptr. | Exact names four class/tabuliek and all virtuálnych targets. |
| **Locally data** | `TabbedTextOut` uses `SI` as result pointer and `PUSH/POP SI`; other two obaly do not have meaning locally values. | Meaning next local/stackových slotov in all function kandidátskeho list. |
| **Memory** | Obaly explicitne read `this+4`; `TabbedTextOut` writes 4 bytes to caller bufferu. Thunk-y read object vptr and pointer z vtable. | Whether existing zero dereferencie or invalidné DC/RECT/string pointer filtrujú call. |
| **Structures and arrays** | `CDC`-like vptr/HDC layout and 4-byte result rozmerov are podopreté. | Complete layout pointer tabuliek, MFC message-map record during `CWnd` and ownership all fields. |
| **Constant** | `0x04` is HDC offset; `0x78/0x7C` are dispatch displacement; GDI/USER ordinals are spárované with API. | Meaning `0x000A` v adjacent MFC data and next neoznačených literálov v 967 function. |
| **Row** | Text obaly have lineárny tok: argumenty → API → return/write. Thunk-y robia indirect farový skok. | Which specifically runtime classes poskytujú target virtuálne sloty and when sa call. |
| **Calls** | `GDI#33`, `USER#196`, `USER#85` are confirmed NE relocation; interné far-pointer targets are map. | Complete call/caller graph including near calls, vtable dispatchu, callbacks and jump tables for all functions. |
| **Vedľajšie effects** | Text API draw to HDC. `TabbedTextOut` returns rozmery; during set `TA_UPDATECP` can change current position DC. Explicitnú change global game state som v this skupine did not find. | actual DC/text-state during each game callsite and to, whether sa result draw objaví v hre or only v MFC shelli. |
| **Boundary cases** | Wrappery nerobia own check HDC/string/RECT; zero `SI` v `1:0422` vedie k write without guard. API dostáva count znakov, nie length odvodenú only from zero terminátora. | As systémové DLL process invalidné pointer, negative counts and incorrect tab-stop arrays; whether call these input vylučuje. |
| **Evidence** | Raw instructions, physical offset, relocation miesta, importy and repeated pointer tables are available and reprodukovateľné. | Runtime breakpoint trace on original Win16 build-e and separate confirmation tých istých signatúr in Win16 1.8. |

## Check xrefov: priamy call version farový pointer

`NITE3W_function_candidates.csv` contains 688 row candidates and 367 z nich has `direct_xrefs=0`. Subsequently som prepojil kandidátske addresses with NE internými relocation: search som offset slova tesne before relocation segment slovom and skontroloval target segment. During 252 z 367 items sa našiel at least one farový pointer, whose offset sa match with address kandidáta.

This number is tool result, nie count confirm call. Farový pointer can be vtable entry, callback, message-map handler or other pointer on code; each source needs to klasifikovať according to okolitého record and callsite. Three MFC text obaly are priamym príkladom: candidate `1:0400` has zero count priamych call, but four relocation references v table segment 4.

**Consequence:** next xref audit has osobitne viesť priame `CALL`, far-pointer relocations, references z vtable/message-map tabuliek and pointer, ktorých semantic is still neurčená.

## remain unknown for Nite3W

### Priorita P0

1. **Prepojiť all 367 candidates without priamych XREFov with relocation and dátovými table.** Najprv odlíšiť real functions, vtable/callback targets, pointer on data and incorrect boundaries functions.
2. **Add exact graf constructor → vptr → pointer table → virtuálny target.** Začať štyrmi table v segment 4 okolo `4F88`, `5004`, `5080`, `50FC` and block during `CWnd`.
3. **Continue v read/write runtime records GUARD/OBJECT.** Win16 1.10 meaning OBJECT `+0x12/+0x18` and GUARD `+0x12` are static closed v specific read/write path. Remains freshness `OBJECT+0x18` during projectile damage, order projekcie and výstrelu, DOS cache/projection parita, class-specific verify and separate projectile `+0x0D`. Podrobnosti: `Nite3W_OBJECT_GUARD_field_read_write_closure_2026-09-23.md`.

### Priorita P1

4. **Close GUARD/combat dispatch.** Remains complete table state × strategy × timer × animation × movement × sound including tried and DOS parity.
5. **Measure sequences and timer.** Remains frame divide, loop/one-shot/alternate behavior, audio links and kalibrácia tick jednotiek for IMG/SEQDEF.
6. **confirm trigger, USER.SAV and map eventy v behu.** Static mapy flagov, TRIGGER1/TRIGGER2 and 64-byte cache are partially mapped; activation, save/load during eventu and DOS/Win16 1.8 differences remain open.
7. **Add render/runtime comparison.** Pixel test WinG/DOS, projectile boundary state, wall class `0x2D` completion and exact redraw/collision effect.

These body are v súlade with posledným master and deep-unknowns auditom. Already map behavior sa has still označovať as static, until ho nepotvrdí debugger or check game test.

## Specifically additional tests

1. On Win16 debuggri set breakpointy on `1:03E8`, `1:03F4`, `1:0400`, `1:0422` and `1:045C`. Record `SS:SP`, `this`, `this+4`, argumenty and return registers.
2. During `03E8/03F4` subtract farový vptr z object, dereferencovať `vptr+0x7C`/`vptr+0x78` and record konečný `CS:IP`.
3. During `0422` track caller buffer on `BP+0x1A`; confirm, whether ho caller uses as 4-byte `CSize`-like result and as interpretuje `DX:AX`.
4. During startup/handler path track writes first 4 bytes new object; spárovať result vptr with table segment 4 and runtime-class descriptorom.
5. Opakovať same breakpointy on hashi Win16 1.8. Preserve differences versions; nepovažovať same address for evidence same functions.
6. For increase items without priameho XREFu save raw source relocations and okolitý 10–20-byte record before add name.

## Zhrnutie pripravené on implement

Podporené static modely:

```text
CDC-like TextOut(this, x, y, farString, count):
    hdc = *(WORD16 *)(this + 4)
    return GDI#33(hdc, x, y, farString, count)

CDC-like TabbedTextOut(this, x, y, farString, count,
                       tabCount, farTabStops, tabOrigin, resultBuffer):
    hdc = *(WORD16 *)(this + 4)
    packedSize = USER#196(hdc, ...)
    *(DWORD16 *)resultBuffer = packedSize
    return resultBuffer

CDC-like DrawText(this, farString, count, farRect, flags):
    hdc = *(WORD16 *)(this + 4)
    return USER#85(hdc, farString, count, farRect, flags)

Virtual dispatch thunk:
    object = *(WORD16 *)(SS:SP + 4)
    vptr = far_pointer_at(object + 0)
    far_jump(vptr + slot_offset)
```

Nepridávať fixed name classes, vtable target nor behavior during incorrect caller pointer, until their nepotvrdí next stopa.

## Zdroje

### Locally binary and auditné podklady

- `nite3w(10).exe`, SHA-256 above; segment 1, physical offset `0x04C0`.
- `Nitemare3D_nite3w_xref_audit_2026-09-22.zip`: `ne_relocation_sites.csv`, `ne_relocation_summary.json`, parser NE relocation.
- `NITE3W_function_candidates.csv` and `nite3w110.exe.c`.
- `Nite3W_first10_function_dependency_audit_2026-09-23.md`.
- `Nite3W_MFC25_class_reconstruction.hpp`.
- `Nitemare3D_Reverse_Engineering_Master_Reference_2026-09-23.md`.
- `Nitemare3D_deep_unknowns_2026-09-23.md`.

### API names and signatúry

- [Wine Win16 GDI source — GDI.33 TextOut](https://github.com/wine-mirror/wine/blob/master/dlls/gdi.exe16/gdi.c#L3429-L3436)
- [Wine Win16 USER ordinal table — USER.85 DrawText and USER.196 TabbedTextOut](https://fossies.org/linux/misc/wine-11.18.tar.xz/wine-11.18/dlls/user.exe16/user.exe16.spec)
- [Microsoft Learn — TabbedTextOutA signature and packed width/height return](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-tabbedtextouta)

**Overall confidence:** high for identitu importov, boundary tiel, stack cleanup and explicit memory operations; medium for map CDC-like/vtable class; low for original names specific MFC class and behové usage without debugger trace.