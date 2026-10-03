# Nite3W 1.10 — MFC and memory links: check exact percent

Date: 24. 9. 2026.

## Range and result

Preverené are publikované repository audity v fixed revíziách. This step neobsahuje new read original EXE, complete XREF exportu nor new beh game. Findings z auditov are marked as prevzaté evidence; arithmetic dôsledky are derived. Reference EXE has according to auditov SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

Previous konverzačné score approximately 98,1 % (±0,6 percentuálneho bodu) does not have v verify podkladoch supported count uzavretých väzieb nor overall menovateľ. Is not therefore possible z neho compute verify exact score 98,530 % or 99,152 %. Listed odchýlka is not supported štatistický interval spoľahlivosti.

## Exactly prepočítateľné pointer

| Pointer | Count | Calculation | Meaning |
|---|---:|---:|---|
| Strong/exact medziverziová match Win16 block | 929 / 967 | 96.070321 % | Podpora identity functions; NIE complete MFC/memory. |
| Blocks without takejto matches | 38 / 967 | 3.929679 % | Does not mean 38 completely unknown functions. |
| Interné segment fixupy z relocation miest | 4 904 / 6 082 | 80.631371 % | Zloženie relocation; NIE podiel completion analysis. |
| Other relocation miesta | 1 178 / 6 082 | 19.368629 % | Are not automaticky nevyriešené. |
| Completely closed MFC/memory links | K / N nedoložené | Undetermined | Requires item register and its complete. |

Source počtov: WITH1. Count 6 082 is not complete graf read, write and call; dokument explicitly upozorňuje on near call/jump and references without relocation.

## New arithmetic check memory data

Z data WITH2:

- Automatický data segment NE 10: start v file `0x2C040`, stored length `0x8EAE` = 36 526 B.
- Last byte its store image: `0x34EED`; first byte for ním: `0x34EEE`.
- Initial heap: `0x4262` = 16 994 B; initial stack: `0x2EE0` = 12 000 B.
- Arithmetic sum these troch size: `0xFFF0` = 65 520 B.

This sum is not evidence specific runtime field zásobníka, free 16 bytes nor layout heapu. To requires check minimálnej allocate, zarovnania and behavior loadera.

According to WITH1 has VEC kapacitu 1 000 records after 28 B. Plná capacity therefore requires **28 000 B**, what is viac as uvádzaný initial local heap 16 994 B. Takýto plný separate pool sa nezmestí entire to tohto nezväčšeného initial heapu. Z toho nevyplýva specific allocator: needs to doložiť far/global allocate, other segment or zväčšenie/different layout memory. WITH2 states segment 5, 6, 8 and 9 without store file image; cannot their during inventarizácii runtime memory vynechať.

## Specifically open strings

WITH3 ponecháva static open links constructor → vptr → table → target and complete ownership allocate/cleanup all mode.

| String | What must doložiť complete uzavretie |
|---|---|
| Allocate → save pointer → use → free | Type/size, own, aliasy, úspešné i error path, invalidácia. |
| Object MFC → handle → temporary/persistent map | Exact attach/detach/cleanup targets and nezameniteľná lifetime obalu and systémového object. |
| Constructor → vptr/vtable → indirect call | Relocation target each relevantnej items; nie only found string name classes. |
| RuntimeClass → name/základná class/create function | Format according to specific Win16 build and verify relocations. |
| Cache slot → buffer → výmena → zrušenie starých odkazov | Všetci own and use, error reload, reset and termination. |

Microsoft WITH4/WITH5 confirms general difference lifetime temporary obalu and handle. For example Divide for CDC removes temporary objects CDC, but nezničí corresponding HDC. Is reference semantic, nie o evidence exact implement or layoutu MFC in Win16 Nite3W.

## Four older address kandidáty

Addresses below pochádzajú z predchádzajúcej konverzácie, nie z new verify their instructions. Table only prevádza offset according to segment map WITH2 for predpokladu exportového map `1000 → NE 1`, `1008 → NE 2`.

| Candidate v exporte | NE segment:offset | Derived file offset | Status target |
|---|---|---|---|
| `1000:338C` | `1:338C` | `0x0384C` | Neoverený v this kroku. |
| `1008:003A` | `2:003A` | `0x0E8DA` | Neoverený v this kroku. |
| `1008:0266` | `2:0266` | `0x0EB06` | Neoverený v this kroku. |
| `1000:05E8` | `1:05E8` | `0x00AA8` | Neoverený v this kroku. |

This are not addresses runtime selectorov nor evidence, that remain already only four links.

## Meranie next pokroku

Odporúčaný base registra: `ID, EXE_hash, subsystem, source_NE_address, field_or_slot, relation_type, target_NE_address, owner, lifecycle, static_status, runtime_status, evidence, exclusions`.

Static pokrytie = 100 × count completely uzavretých items / count all items fixed define registra. separate needs to uviesť, whether is register complete: podiel from známych items nesmie predstierať podiel from all actual väzieb programu.

Runtime pokrytie = 100 × performed and vyhodnotené scenario / all scenario define test sady. Nesmie sa miešať with static score.

V this kroku: new byte-level uzavretia MFC väzieb **0**, new runtime records **0**. To is not 0 % doterajšieho project; is to exact designation work execute v this specific kroku.

## Zdroje

- WITH1: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_core_function_map_2026-09-23.md
- WITH2: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/analysis/nite3w_exe_deep_audit_2026-09-20.md
- WITH3: https://github.com/marek177/Nite3d-win3.11/blob/791394730187ae0ded48e423fd11aa0d68f70f10/docs/win16/audit-2026-09-24.md
- WITH4: https://learn.microsoft.com/en-us/cpp/mfc/tn003-mapping-of-windows-handles-to-objects?view=msvc-170
- WITH5: https://learn.microsoft.com/en-us/cpp/mfc/reference/cdc-class?view=msvc-170