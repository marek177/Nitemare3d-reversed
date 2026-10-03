# Nite3W — CDC/GDI/Menu: pokračovanie analysis lifetime

Date: 25. september 2026. Auditná etapa: 2.

## Range and origin evidence

Skontrolovaný commit `marek177/Nitemare3d-reversed`:
`5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f`.

Four headers v `snapshot/platform/` are obsahovo totožné with load Git blobmi; their Git SHA-1 also SHA-256 are v `source_manifest.json`. Two pochádzajú z previous auditného package and were compare with current Git blob SHA; two were stored z new load and takisto hashovo verify. Repository sa from first auditu posunul, these four files however obsahovo zostali nezmenené. [WITH1–WITH4]

New evidence v this etape pochádzajú z kompilácie and execute moderného C++ code portu, z row vyvolania výnimky and z izolovanej check memory errors. Original NITE3W.EXE was not available locally on new analysis; pokus získať shareware archív z verejného zrkadla failure. Original Win16 program sa nespúšťal and new addresses FUN_xxxx sa nevyhlasujú for find. Moderná dokumentácia Microsoftu is check kontrakt, nie evidence specific historical implement.

## 1. Najdôležitejší new evidence: neúspešné connect stratí old assign

current `HandleRegistry::attachPermanent` najprv zmaže temporary obal and then executes potenciálne allocate vloženie to permanentnej map. [WITH1]

```cpp
void attachPermanent(Handle handle, Wrapper wrapper) {
    temporary_.erase(handle);
    permanent_.insert_or_assign(handle, std::move(wrapper));
}
```

Test `test/permanent_alloc_failure.cpp` uses actual type `NativeHandleWrapper<int>`, nie alternatívny own obal. After create temporary items cielene vyvolá `std::bad_alloc` during najbližšom C++ `operator new` during permanentného vloženia.

Result v GCC also Clangu:

```text
bad_alloc_caught=1
injected_allocation_failures=1
temporary_count_after_failure=0
permanent_count_after_failure=0
LOSS_OF_PREVIOUS_ASSOCIATION=1
```

Before operation existoval temporary obal; after neúspešnej operation neexistuje none assign. Výnimka therefore nevrátila register to previous state. Niekdajší pointer on temporary obal is invalid also napriek tomu, that new operation neuspela.

This is not tvrdenie o porušení základnej výnimkovej garancie entire kontajnera: remain kontajnery are usage. Is nesplnenie strong transakčnej own „neúspech does not change original assign“, ktorú safe layer can požadovať. Failure was vložené test; nedokazuje actual nedostatok memory v hre nor failure Windows API. [T2]

## 2. Register can obsahovať key, which nezodpovedá handle obalu

`findPermanent()` and `fromHandle()` return meniteľný obal. Its verejné `attach()` and `detach()` nemenia map. [WITH1, WITH2]

### Zmena values

Test N05: vložené `(77 -> wrapper(handle=77))`; subsequently sa through získaný obal executes `attach(88, Owned)`. Then search kľúča 77 returns obal with handle 88, but key 88 v map is not.

### Priame odpojenie

Test N06: priame `detach()` obalu zeros handle, but key 77 zostane. Neskoršie `fromHandle(77)` finds permanentnú item and returns empty obal. Factory sa nespustí.

### Nesprávna factory

Test N07: `fromHandle(77, factoryReturning88)` stores obal with handle 88 pod kľúčom 77. Register neoveruje match.

These results odhaľujú missing kontrakt between map and verejnou mutáciou obalu. Neznamenajú, that normal factory in `WindowRegistry` returns nesprávnu value; that v súčasnom code passes input handle correctly. Riziko sa týka generického interface and mutácie its result. [T1]

Požadovaný invariant for proposed compatibility register:

```text
každá živá registrácia kľúča h -> obal má primárny handle h
odpojenie obalu -> aktualizuje sa aj príslušná registrácia
```

For CDC needs to osobitne determine, which z its dvoch fields forms key. This invariant netvrdí, that oba HDC must be always same.

## 3. Move registra and move ochranného range are not zameniteľné

`TemporaryWindowScope` uchováva pointer on specific `WindowRegistry`. Move itself scope tokenu is implement: source token sa vyprázdni and zodpovednosť for jedno termination prevezme target token. Check test C04/C05 confirm correctly behavior. [WITH3, T1]

Itself `WindowRegistry` however does not have zakázané copy nor move. [WITH3]

Tests N02/N03 vykonali:

```text
pôvodný register: vytvor scope -> hĺbka 1
pôvodný register: vytvor dočasný obal
presuň register do iného objektu
ukonči pôvodný scope
```

V cieli zostala hĺbka 1 and temporary item. Original scope still odkazoval on original object, therefore target hĺbku neznížil. Nor next correctly vyvážený scope v cieli to neopraví: executes only 1 -> 2 -> 1. Čistenie during nule sa nespustí.

This test does not mean nevyhnutný persistent únik after zániku entire registra: its map sa during zániku still zničia. Dokazuje neuskutočnené scope čistenie during remain života move registra.

Test N04 moreover confirmed, that copy registra prenesie numeric hĺbku and creates second sadu obalov with same `Owned` označením. Is extension previous findings o copy itself obalu on entire register. Dnešné obaly still do not have deštruktor natívneho source, so this test nevzniklo dvojité systémové free. [WITH2, T1]

For port is konzervatívne riešenie zakázať move and copy registra or umiestniť status on stabilnú address and define ownership scope tokenov. Is not to tvrdenie o presúvaní object v original Win16 programe.

## 4. Priame čistenie obchádza vnorenie

Test N01 reprodukoval status `temporaryScopeDepth=2`, after ktorom verejné `clearTemporary()` vyprázdnilo map without zníženia hĺbky. [WITH3, T1]

Predošlý audit on this branch upozornil from source code; teraz ide also o execute test. Itself existencia núteného čistenia does not have to be error, pokiaľ is explicitly určená for example on termination procesu. Interface however nerozlišuje normal requirement on čistenie and nútené zneplatnenie obalov during active range.

Check test C01–C03 confirm, that normálne vnorenie without priameho `clearTemporary()` funguje: internal end obal preserves, external ho removes.

## 5. Opätovný input z factory changes result FromHandle

Test N10 použil row factory, which during svojho execute connect permanentný obal for just search handle. External `fromHandle()` after návrate z factory znova neskontroluje permanentnú map, creates temporary item and returns ju. result are two items and temporary return, hoci permanentný obal already v time návratu existuje. [WITH1, T1]

This is hraničný scenario generického callbackového interface. current jednoduchá factory in `WindowRegistry` takýto spätný input neobsahuje. Is not to evidence, that opätovný input nastáva v original nite3w.

Possible kontrakt: zakázať mutáciu registra during factory or after its návrate znovu vyhodnotiť map and safely terminate nepotrebný kandidátsky obal. Themselves zopakovanie lookupu nerieši automaticky ownership kandidátskeho systémového source.

## 6. Duplicitné connect removes kontextové data

Test N08: permanentný obal window has `Owned`, parent context 11 and pointer on associated object. Subsequent `attachBorrowedPermanent(77)` all these data overwrite novým obalom: ownership is Borrowed, parent context 0 and associated object null. [WITH1, WITH3, WITH4, T1]

If is opätovné connect zamýšľaná operation, needs to define, what sa has stať with starým kontextom and case required free. V súčasnom interface sa original value call nevracia and duplicitný key sa neodmieta.

## 7. Prípravný cleanup helper is not automaticky zapojený

`WindowWrapper` has `prepareTemporaryCleanup()`. Generický register however nevolá žiadnu takú method; uses only zmazanie elements kontajnera. [WITH1, WITH4]

Test N11 použil diagnostic obal with match named helperom. After čistení: 0 zavolaní helpera, 1 deštruktor with nonzero handle. Is posilnenie already známej medzery, nie next evidence deštrukcie natívneho window.

## 8. Izolovaný ASan evidence previous invalid pointer

`test/stale_temporary_asan.cpp` úmyselne spraví:

```text
získa ukazovateľ na dočasný obal
attachPermanent pre rovnaký handle
prečíta handle cez starý ukazovateľ
```

GCC also Clang AddressSanitizer message `heap-use-after-free`. Negatívny test sa spúšťa výhradne as separate proces, must skončiť nonzero and is not part of safe observačnej sady. [T3]

This posilňuje previous finding o zneplatnení temporary pointer. Is not new pád original EXE. Normal MFC dokumentácia also upozorňuje on obmedzenú lifetime temporary pointer; this test however izoluje specific time zneplatnenia v našom porte. [M1]

## 9. Spresnenie CDC/GDI/Menu kontraktov

Following fakty pochádzajú z modernej dokumentácie Microsoftu; dôsledky for audit are naše check rules. Is not newly confirmed Win16 addresses.

### 9.1 Región is not bitmapa

During successful `SelectObject` for ne-regiónový object return reprezentuje previous object. During regiónoch return reprezentuje zložitosť regiónu; is not to handle on old object. Analysis therefore does not have automaticky posielať each return z takejto branches to `CGdiObject::FromHandle`. Jedna bitmapa sa moreover nemôže súčasne vybrať to dvoch DC. [M2]

`SelectClipRgn` uses copy regiónu. Source región sa can neskôr zmazať without zániku set copies clip. Všeobecné right „each vybraný GDI object must zostať živý“ is for takúto branch incorrectly. [M3]

### 9.2 SaveDC and RestoreDC patria to sledovania kresliaceho stavu

`Save` stores data o vybraných object and draw mode on zásobník; during failure returns nulu. `RestoreDC` vie restore previous status without next explicitného `SelectObject`. During restore sa removes restore record also neskoršie records on zásobníku. [M4, M5]

Consequence for audit: jednoduché matching posledného SelectObject and nasledujúceho Divide is not enough. Needs to track also úspešné save/restore state. Save at the same time is not evidence hlbokej copies bitmapy nor prevodu own source; takúto property listed kontrakt neuvádza.

### 9.3 ReleaseDC is not DestroyDC

`ReleaseDC` terminate corresponding usage získaného kontextu; is not to general evidence zániku systémového object. Dokumentácia distinguishes normal/okenné DC and class/private DC, on which does not have same effect. `Divide` naopak removes create DC and nepatrí on kontext získaný through GetDC. [M6, M7]

Consequence for measure: viesť osobitne interval získania/use HDC and lifetime natívneho object. Count ReleaseDC sa does not have without next zameniť for count zničených HDC.

### 9.4 Menu: result API is rozhodovací bod

SetMenu can failure. Also during success previous menu nezničí. For proposed moderný model sa therefore change evidencie own new menu confirms up to after successful result; old menu needs to evidovať oddelene. [M8]

DestroyMenu ničí also podmenu and also has result success/neúspech. One úspešný systémový step can zneplatniť viac obalov podmenu, nielen priamy obal koreňa. [M9]

To are rules for check reconstruction. Exact historical order disconnect map and systémového calls v MFC remains on verify. Z dokumentácie API cannot odvodiť, that original obal during neúspechu automaticky execute rollback.

## 10. Results testov

| Overenie | GCC 14.2 | Clang 17 |
|---|---|---|
| 17 pozorovaní: Debug | All reproduced | All reproduced |
| 17 pozorovaní: Release + NDEBUG | All reproduced | All reproduced |
| 17 pozorovaní: UBSan | Without diagnostic UB | Without diagnostic UB |
| 17 pozorovaní: ASan | Without memory diagnostic | Without memory diagnostic |
| Row bad_alloc, actual obal | Strata starého assign confirmed | Strata starého assign confirmed |
| Izolovaný negatívny ASan test | Očakávaný heap-use-after-free | Očakávaný heap-use-after-free |

Conclusion sada: 12 separate kompilácií and run: 8 observačných, 2 allocate and 2 intentionally error. V observačnom file is 17 different check, nie 136 different finding; z toho 11 is hraničných pozorovaní and 6 check. Nie all are new independent errors: part prehlbuje already known medzery. Test nepoužívajú assert, so sa nestratia during NDEBUG. ASan leak detection was vypnutá; netvrdí sa execute audit únikov.

Content logov and return codes are v `results/`; runner akceptuje negatívne test only during nonzero result and výskyte očakávanej diagnostic.

## 11. Proposed order opráv and pokračovania

1. Stabilizovať relationship scope -> register: zabrániť copy/move active row state or use stabilne address status.
2. Zabezpečiť súlad registra and handle: obmedziť priamu mutáciu registrovaných obalov, define duplicitné Attach and koordinované Detach.
3. define transakčný kontrakt Attach: neúspech nesmie without dokumentovaného reason zničiť previous usage assign.
4. Separate normal odložené and nútené čistenie. Zapojenie cleanup helpera must handle all handle arrays CDC and own kontrakt, nie only name methods.
5. Before zavedením natívneho free doriešiť API origin source, GDI regióny/Save/RestoreDC and menu stromy.

These proposal are not aplikovaným patchom. Prehodenie dvoch row Attach or add univerzálneho deštruktora samo nevyrieši identitu starých obalov, duplicitné ownership and spätné input.

K tomuto package is add plan `native_trace_checklist.json`: is requirement on budúci record, nie o data nameraný trace. NE addresses unknown functions remain null. Podiel completion EXE sa this auditom neprepočítava and to GitHubu nebolo nič zapísané.

## Reprodukcia

```sh
python run_checks.py
```

Requirement: Python 3.10+ and GCC or Clang with C++20 and available sanitizer runtimami. verify Linux x86_64, nie MSVC/Windows/Win16. Source headers sa before test check according to Git blob SHA-1. Sada contains separate intentionally incorrect ASan program: nespúšťať ho as súčasť game.

## Zdroje

WITH1. https://github.com/marek177/Nitemare3d-reversed/blob/5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f/src/platform/HandleRegistry.hpp

WITH2. https://github.com/marek177/Nitemare3d-reversed/blob/5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f/src/platform/NativeHandleWrapper.hpp

WITH3. https://github.com/marek177/Nitemare3d-reversed/blob/5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f/src/platform/WindowRegistry.hpp

WITH4. https://github.com/marek177/Nitemare3d-reversed/blob/5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f/src/platform/WindowWrapper.hpp

M1. https://learn.microsoft.com/en-us/cpp/mfc/tn003-mapping-of-windows-handles-to-objects?view=msvc-170

M2. https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-selectobject

M3. https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-selectcliprgn

M4. https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-savedc

M5. https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-restoredc

M6. https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-releasedc

M7. https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-deletedc

M8. https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setmenu

M9. https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-destroymenu

T1. `tests/next_observations.cpp`, `results/*_debug.log`, `results/*_release_ndebug.log`, `results/*_ubsan.log`, `results/*_asan.log`.

T2. `tests/permanent_alloc_failure.cpp`, `results/*_allocation_failure.log`.

T3. `tests/stale_temporary_asan.cpp`, `results/*_stale_pointer_negative.log`.