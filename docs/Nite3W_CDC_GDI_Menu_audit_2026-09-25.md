# Nite3W — životný cyklus obalov CDC/GDI/Menu

Date: 25. september 2026.

## Range and evidence boundary

Skontrolovaný repository: `marek177/Nitemare3d-reversed`, commit
`9d485e82a84ef1241eff7165c390c82eaff47970`.

This step kombinuje audit actual C++ code portu, locally kompilačné and observačné test and comparison with dokumentovaným kontraktom MFC/Windows. Original NITE3W.EXE was not v this kroku available on new priamy binary analysis nor run. Addresses original programu below are prevzaté z existing registra, nie nanovo find v assemblerovom výpise. Reference build v existing audite has SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. [WITH1–WITH3]

Moderná dokumentácia Microsoftu slúži as kontrakt and check rámec; sama nepotvrdzuje specific implement MFC in Win16. Osobitne sa nepreberá novodobá organizácia map according to vlákien to original programu without evidence.

## 1. Prevzaté binary kotvy

Following offset are according to registra v NE segment 10. Number segment NE is not current selektor DS v run aplikácii. [WITH1–WITH3]

| Rodina | Mapa | Runtime-class descriptor | Size obalu | Offset/count handle fields |
|---|---:|---:|---:|---|
| CDC | `44F2` | `0696` | `0A` | `+04`, two 16-bit arrays, therefore `+04` and `+06` |
| CGdiObject | `451C` | `06D6` | `06` | `+04`, jedno array |
| CMenu | `4548` | `0746` | `06` | `+04`, jedno array |

V registri are also `CClientDC` (`06A6`, size `0C`), `CWindowDC` (`06B6`, `0C`) and `CPaintDC` (`06C6`, `2C`). Z difference size still cannot without read and write safely name all provided arrays. CDC has after dvoch handle field also additional two bytes; their meaning sa this auditom does not close. [WITH2]

Shared map has two 16-byte slovníky and three 16-bit parametre:

| Offset | Meaning |
|---:|---|
| `00` | permanentná map |
| `10` | temporary map |
| `20` | offset runtime classes |
| `22` | offset first handle array v obale |
| `24` | count handle fields |

Sum is `0x26` = 38 bytes. Hash `(handle >> 4) % bucketCount` slúži on search; is not to count own systémového object. [WITH1, WITH2]

## 2. New reprodukovaný problem: zarovnanie HandleMap16

First 45 row `Win16MfcMemory.hpp` define structures without local set balenia and then požaduje `sizeof(HandleMap16) == 0x26`. During štandardnom x64 zarovnaní v usage kompilátoroch contain 32-bit arrays vyvolajú štvorbajtové zarovnanie. result size is 40 bytes and static check failure. [WITH2, T1]

| Kompilátor / environment | Original size | After local pack(2) | Result |
|---|---:|---:|---|
| GCC 14.2, Linux x86_64 | 40 | 38 | Original static_assert failure; corrected prejde |
| Clang 17, Linux x86_64 | 40 | 38 | Original static_assert failure; corrected prejde |

Pozor: v measure case sa nemenia internal offset `0,16,32,34,36`. Problem is final added structures and its zarovnanie. Is error reprezentácie v modernom C++, nie evidence incorrect original Win16 object.

Priložený `Win16MfcMemory_layout.patch` ohraničuje four binary records helper `#pragma pack(push, 2)` / `#pragma pack(pop)` and adds check offset. Does not change globally balenie project. Test was izolovaný výrez structure, nie complete build game nor MSVC. During read binary file is still vhodné decode little-endian arrays explicitne; correctly `sizeof` samo neoprávňuje neoverený `reinterpret_cast` to ľubovoľných bytes.

## 3. Životný cyklus: obal is not systémový object

Needs to distinguish at least three independent veci: lifetime C++ obalu, its registration v map and required free natívny object. Permanentná map does not mean nesmrteľný object nor automaticky výhradné ownership. Also local obal on zásobníku can be during svojho života permanentne connect. Temporary obal type only sprostredkuje prístup k cudziemu handle. [M1]

Existing audit states this shared postup: search permanentný obal, then temporary and up to during neúspechu create new through runtime class. During čistení sa before virtuálnym zánikom obalu nulujú handle arrays. Thereby deštruktor obalu nedostane zapožičaný natívny object on zničenie. During CDC needs to zohľadniť two arrays, nie only first. [WITH1, WITH2; M2–M4]

Logical model, nie new dekompilát:

```text
FromHandle(h)
    permanentný obal existuje -> vrátiť ho
    dočasný obal existuje     -> vrátiť ho
    inak                     -> vytvoriť dočasný obal

Povolené čistenie dočasných obalov
    zneplatniť/odpojiť všetky handle polia obalu
    ukončiť život C++ obalu
    nevolať deštrukciu zapožičaného systémového objektu
```

Zero handle is not free natívneho object. Nor čistenie temporary map nenahradí `ReleaseDC` or `EndPaint`, which must execute correct nadobúdateľ source. Dokumentácia at the same time nepovoľuje spoliehať sa on temporary pointer through neskoršie process message. [M1–M3]

Repository already has `WindowRegistry::beginTemporaryScope`, `endTemporaryScope` and presúvateľný, nekopírovateľný `TemporaryWindowScope`; during poklese hĺbky on nulu sa čistia temporary window. Therefore is not correctly tvrdiť, that port does not have žiadnu podporu vnorenia. This specific class however handles window. Common behavior CDC/GDI/Menu and exact Win16 spúšťacie path thereby are not supported. Verejné `clearTemporary()` moreover v this class samo nekontroluje hĺbku; difference between núteným and condition čistením needs to define. [WITH6]

## 4. New findings from actual headers portu

`NativeHandleWrapper.hpp` and `HandleRegistry.hpp` were stored without change; their Git blob SHA-1 súhlasí with value konektora. Dvanásť observačných check sa match reprodukovalo GCC also Clangom. „OBSERVED“ mean confirmation listed behavior portu, nie confirmation correct emulácie MFC. [WITH4, WITH5; T2]

### 4.1 Owned is only designation

`NativeHandleWrapper<int>` is triviálne deštruovateľný. Class does not have free field nor user deštruktor. Its itself zánik therefore nevolá `Divide`, `ReleaseDC`, `EndPaint`, `Divide` or `DestroyMenu`. Without auditu higher layer sa to nesmie mark for dokázaný únik celej game; is to jasná boundary schopností tohto obalu. [WITH5, T2]

### 4.2 Copy and move nedokazujú prenos výhradného own

Copy obalu with `Owned` preserves same handle also `Owned` v oboch object. same implicitný move ponechá source object with original handle also own označením. Dnes to samo nespôsobuje dvojité systémové free, because missing free deštruktor. Add ho without súčasného vyriešenia copy/move by however was nebezpečné. [WITH5, T2]

### 4.3 Attach vie prekryť živý handle

`attach(88, Owned)` on obale with value `77` only nahradí arrays. Starú value neuvoľní nor nevráti. For budúci own obal needs to explicitný kontrakt: connect only to prázdneho object or row `reset` correct free field. [WITH5, T2]

### 4.4 Všeobecná map before deštruktorom nenuluje handle

`HandleRegistry::clearTemporary()` executes `temporary_.clear()`. Test with diagnostic obalom zaznamenal input to its deštruktora with nonzero handle. General register therefore itself nevynucuje invariant original auditu „vynulovať handles before deštruktorom“. Safe can zabezpečiť nevlastniaci type temporary obalu, but interface to nevynucuje: factory smie return also obal `Owned`. [WITH4, T2]

### 4.5 AttachPermanent ruší existing temporary obal okamžite

Method starts `temporary_.erase(handle)`. Diagnostic test confirmed okamžité call deštruktora temporary obalu. Already return pointer sa thereby zneplatní; on pokles hĺbky temporary scope sa nečaká. Is to confirmed behavior portu. Whether exactly corresponds to specific original Win16 Attach, remains without výpisu its code open. Permanent-first lookup itself nevyžaduje okamžité mazanie temporary items. [WITH4, T2]

### 4.6 Two rozdielne meaning odpojenia

`NativeHandleWrapper::detach()` returns natívnu value and vyprázdni obal. Naproti tomu `HandleRegistry::detachPermanent()` odoberie item z map and returns still naplnený obal, also with `Owned`. To is not samo osebe error name registra, but is not to hotová náhrada MFC `Detach`. Existing `WindowRegistry::detach` correctly adds second step `wrapper->detach()`. [WITH4–WITH6, T2]

### 4.7 Zero handle does not have osobitnú branch

Generické `fromHandle(0)` creates temporary item and returns referenciu on obal with invalid value. Test to reprodukuje. exact požadovanú reakciu compatibility layer needs to zadefinovať and compare with specific Win16 input; this generická method return referenciu nemôže sama return zero pointer. [WITH4, T2]

## 5. CDC: important is origin HDC

| Origin source | Zodpovedajúce termination according to dokumentovaného API |
|---|---|
| `CreateDC`, `CreateIC`, `CreateCompatibleDC` | `DeleteDC` |
| `GetDC`, `GetWindowDC` | `ReleaseDC` with corresponding window |
| `BeginPaint` | `EndPaint` with corresponding window and PAINTSTRUCT |
| Only `FromHandle` nad cudzím HDC | Terminate obal without own deštrukcie cudzieho HDC |

`CClientDC`, `CWindowDC` and `CPaintDC` existujú just for difference dvojice získania and terminate. Jediná branch „Owned -> Divide“ therefore is not enough. [M2, M5–M7]

Two arrays CDC neznamenajú two independent own. V dokumentovanom CDC predstavujú output and atribútový kontext; can be same. During Detach sa obe nulujú. V registri Nite3W is confirmed count and field fields; exact named oboch, different values and all free path needs to confirm their specific use. [WITH2, M2]

## 6. GDI: selection to DC and ownership are different veci

Safe completion work with own draw object requires restore original selection v DC and up to then free own object. `Divide` during invalid or just vybranom object according to dokumentovaného kontraktu failure. Needs to record also return value, nie only prítomnosť calls. [M8]

Pointer on obal starého vybraného object can be temporary; its save on neskoršie process message is not zárukou lifetime. Nor save itself handle nezaručuje, that original own object nezruší. [M1, M3]

Two provided boundary: stock object získaný through `GetStockObject` is not normal súkromná allocate aplikácie; moderná dokumentácia states, that its vymazanie is not needed. Zmazanie pattern brush at the same time automaticky nevymaže its source bitmapu. These rules pomáhajú determine auditné branches, but are not evidence their usage v Nite3W. [M8, M9]

## 7. Menu: map obalov version strom systémových menu

`CMenu::Divide` disconnect temporary obal; `CMenu::DestroyMenu` ničí systémové menu. Natívne `DestroyMenu` is rekurzívne, so zanikajú also podmenu. Obal podmenu therefore does not have be automaticky druhým výhradným own tej istej branches stromu. [M4, M10]

`RemoveMenu` vie podmenu disconnect without zničenia. `Divide` during item with podmenu podmenu zničí. `SetMenu` nahradí previous menu, but old samo nezničí. During analysis needs to track also zánik menu connect k window and zabezpečiť, aby other obal neskôr nezničil already zaniknutý or znovu usage handle. [M4, M10–M12]

## 8. address role, which remain open

Existing všeobecné kotvy `1:06C0` (runtime CreateObject) and `1:0730` (create-callback dispatch) pomáhajú dohľadať tvorbu obalov. Specifically addresses CDC/GDI/Menu Attach, Detach, FromHandle and deštruktorov available katalóg neposkytuje. Following names are auditné roly on assign k verify code, nie already verify symbol: [WITH2, WITH3]

| Auditná rola | recognize evidence, which needs to získať |
|---|---|
| `MfcHandleMap_FromHandle` | permanentný lookup, temporary lookup, runtime factory |
| `MfcHandleMap_ClearTemporaryHandlesAndDelete` | cyklus according to handleCount; zero before virtuálnym deštruktorom |
| `CDC_DetachBothHandles` | remove asociácie and zero +04/+06 |
| `CClientDC_ReleaseDCAndDetach` | ReleaseDC, related HWND and termination asociácie |
| `CPaintDC_EndPaintAndDetach` | EndPaint and related paint structure |
| `CGdiObject_DeleteObjectPath` | DeleteObject, result and status mapy/obalu |
| `CMenu_DestroyMenuPath` | DestroyMenu, odpojenie and ownership podmenu |

Najhodnotnejšie runtime evidence: repeated FromHandle on same handle; vnorenie 2 -> 1 -> 0; connect permanentného obalu nad existing temporary; two arrays CDC before deštruktorom; difference DC free API; vybraný GDI object and return z Divide; disconnect/zánik menu stromu; error branches allocate; opätovné usage same numeric values handle.

V each record needs to odlíšiť address C++ obalu from natívneho handle. Themselves same numeric HDC/HMENU v dvoch distance time nepreukazuje totožný object.

## 9. Uzáver tohto kroku

Novo doložená is error zarovnania v declaration moderného portu and dvanásť specific pozorovaní its obalov and map. Pripravená local correction sa týka only binary layoutu. Own behavior nebolo potichu change: safe patch requires zvoliť kontrakt own and nevlastniaceho obalu and verify relevantné original path.

This audit does not change percento poznania EXE and neoznačuje original CDC/GDI/Menu runtime ownership for completion. Code portu is possible further sprísniť already teraz; complete identita with Win16 requires specific listing or beh original programu. Was not execute write to GitHubu.

## Reprodukcia testov

From zložky package:

```sh
python build_evidence.py
python run_checks.py
```

First skript creates nemenné snapshoty and skontroluje their Git blob SHA-1. Second uses available GCC/Clang. Original layout has intentionally vyvolať error kompilácie; corrected layout and observačné test have process. Test nevolajú Windows API. Logy pochádzajú z Linux x86_64. Source files sa dajú preniesť to Windows tool, MSVC however v this audite test was not.

## Zdroje

WITH1. Existing binary audit: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/analysis/nite3w_win16_mfc_memory_2026-09-25.md

WITH2. Layouty and fakty: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/re/Win16MfcMemory.hpp

WITH3. address katalóg: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/re/Win16MfcAddresses.hpp

WITH4. Generický register: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/platform/HandleRegistry.hpp

WITH5. Natívny obal: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/platform/NativeHandleWrapper.hpp

WITH6. Okenný register and vnorenie: https://github.com/marek177/Nitemare3d-reversed/blob/9d485e82a84ef1241eff7165c390c82eaff47970/src/platform/WindowRegistry.hpp

M1. Microsoft TN003: https://learn.microsoft.com/en-us/cpp/mfc/tn003-mapping-of-windows-handles-to-objects?view=msvc-170

M2. CDC: https://learn.microsoft.com/en-us/cpp/mfc/reference/cdc-class?view=msvc-170

M3. CGdiObject: https://learn.microsoft.com/en-us/cpp/mfc/reference/cgdiobject-class?view=msvc-170

M4. CMenu: https://learn.microsoft.com/en-us/cpp/mfc/reference/cmenu-class?view=msvc-170

M5. CClientDC: https://learn.microsoft.com/en-us/cpp/mfc/reference/cclientdc-class?view=msvc-170

M6. CWindowDC: https://learn.microsoft.com/en-us/cpp/mfc/reference/cwindowdc-class?view=msvc-170

M7. CPaintDC: https://learn.microsoft.com/en-us/cpp/mfc/reference/cpaintdc-class?view=msvc-170

M8. DeleteObject: https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-deleteobject

M9. GetStockObject: https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-getstockobject

M10. DestroyMenu: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-destroymenu

M11. RemoveMenu: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-removemenu

M12. SetMenu: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setmenu

T1. Own kompilačné measure: `test_results/layout_*.log` and `test_results/results.json`.

T2. Own observačné test actual headers portu: `lifecycle_observations.cpp` and `test_results/lifecycle_observations_*.log`.