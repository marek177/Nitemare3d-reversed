# NITE3W – next audit hlavných systémov (prechod 2)

**Date: 25. septembra 2026.** Téma: boundary between load define, životnosťou mapy, ohňom, zdravím/HUD and blokmi USER.SAV.

## Result and range

New reprodukcie: neplatná lifetime tabuliek define v `LevelState`, nesúlad priechodnosti ohňa between dvoma modulmi and partial write during postupnom skladaní dvoch separate kontrolovaných save operations. Doplnené are tests poradia zdravotných operations, integrity save and opravy map odkazov.

Pripravené are **two locally kódové opravy and correction one zastaraného komentára**. None write on GitHub was not vykonaný. Original EXE, original game data and entire SDL program sa v this prechode nespúšťali. This is audit exact C++ frames and their väzieb on already stored address audity, nie new disassembly EXE nor new metrika its pokrytia.

During read branches `main` was verify commit `5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f`, whose priamym rodičom is `9d485e82a84ef1241eff7165c390c82eaff47970`. New commit adds projectile save kodek. Základné files were according to potreby znovu prečítané; four závislosti sa prebrali z previous dodaného package on rodičovskom commite.

**All 13 file v `baseline/` was verify proti Git blob SHA-1.** Exact commit, origin, URL, size and SHA-256 each file are v `source_manifest.json`. `baseline/` mean existujúcu modernú rekonštrukciu, nie original source code game. During rozbore original pravidiel are citované messages prevzatou provenienciou, nie znovu certifikovaným disassembly.

## Register result

| ID | Finding | Druh evidence | Result |
|---|---|---|---|
| B01 | LevelState uses define after zániku their object. | Own reprodukcie; Clang ASan. | Locally corrected vlastníctvom values. |
| B02 | Predvolene vytvorený LevelState during verify priechodnosti uses null pointer. | Vlastná reprodukcia; Clang UBSan. | Odstránené same zmenou vlastníctva, is not druhú nezávislú opravu. |
| B03 | Malý and medium CAUSTIC fire: pomocný modul povoľuje prechod, LevelState ho odmieta. | Shared test exact zdrojov on syntetických define. | Confirmed nesúlad, game logic nezmenená. |
| B04 | GUARD write can prebehnúť before odmietnutím nasledujúceho projectile write. | Own test krátkeho pamäťového bufferu. | New local dvojblokový preflight helper. Separate kodeky thereby are not marked for chybné. |
| B05 | Pickup, HP clamp and damage are not zameniteľné operations. | Sekvenčný example and 51 200 kombinácií pomocného modelu. | Exact integračné obmedzenie; nie evidence specific priebehu originálnej game. |
| B06 | Obnovenie HP is not respawn; status 2 remains also during HP 100. | Tests skladania existujúcich health helperov. | Confirmed kontrakt call, nie new error helpera. |
| B07 | Save kodek preserves verify bytes and rebinding does not change nesúvisiace arrays. | Tests byte zmien, canary okolia and odmietnutia without mutácie. | V preskúmanom range without nájdenej errors. |
| B08 | Úspešný rebinding is not validácia hrateľného projectile. | Rebinding with stavom 255 and stepX 32767 during platných coordinate. | Výslovná boundary API; prijatie is not error bezstratového kodeku. |
| B09 | Komentár HazardSystem still denotes DAT_53F2 for interval aktualizácie ohňa. | Comparison with novším Win16 auditom časovania. | Local correction komentára, without zmeny rytmu or values damage. |

## 1. Lifetime define and mapy

### Príčina

`LevelState::create()` accepts define as `const DefinitionTable&`, but stores only their addresses:

```cpp
out.objectDefs_ = &objectDefs;
out.wallDefs_ = &wallDefs;
```

After návrate z factory sa neprenáša ownership tabuliek. `wallAllowsMovement()` and `objectBlocksMovement()` neskôr use these addresses. Pokiaľ call udrží original tables nažive, this specific problem sa nevyvolá. Rozhranie however prijme also dočasné objects and tables vytvorené v krátko žijúcej load function.

### Reprodukcie

`tests/lifetime_probe.cpp` distinguishes:

- `temporaries`: obidve define vzniknú as dočasné návratové values `DefinitionTable::load()` during call factory. Following test priechodnosti vyvolá **stack-use-after-scope**.
- `locals`: load function si creates locally tables and returns LevelState. After návrate vznikne **stack-use-after-return**.
- `object-temporary`: table stien remains nažive, zanikne only dočasná table object. Call object klasifikácie separate confirm neplatný prístup.
- `default`: `LevelState state; state.cellAllowsPlayer(2,1);` uses original zero pointer. UBSan confirmed call členskej functions through null pointer.

This are errors reproduced through verejné C++ rozhranie. Is not thereby confirmed, that existing main program uses exactly these životnosti and for bežného spustenia padá. Check AddressSanitizerom sa opiera o its dokumentované detekcie usage after zániku scope and after návrate functions: https://clang.llvm.org/docs/AddressSanitizer.html

### Local correction

`LevelState` vlastní value frames obidvoch tabuliek namiesto vypožičaných pointerov. Factory their skopíruje and other methods use členské objects.

Dôsledky are zámerné and otestované: dočasné objects can zaniknúť, return z loadera is bezpečný, copy and presunutý LevelState nepotrebujú define call. Predvolený empty status during testovanej otázke on priechodnosť safely returns false; **is not thereby inicializovanou hrateľnou úrovňou**.

New vlastnícky kontrakt is **frame during vytvorení**. V original code prepis externej define FLOOR on SOLID dodatočne zmenil result existujúcej levels z priechodnej on nepriechodnú; after oprave remains level during original define. Implicitné live zmeny sa thereby intentionally rušia. Kopírovanie has pamäťovú/cenovú réžiu; meranie výkonu celej game sa nevykonalo. Alternatívny proposal by mohol explicitne zdieľať nemenné tables with spoločným vlastníctvom, was not however potrebný on this lokálnu opravu.

## 2. Fire between klasifikáciou and movement

Test uses **synthetic**, nie provided original OBJECTS define. Have same assign, aké states existing `HazardSystem.hpp`: ID 0x3B, 0x3C, 0x3D with triedou CAUSTIC.

| ID | Pomocný meaning | `fireHazardBehavior().passable` | `cellAllowsPlayer()` | Pokus o movement to cells |
|---|---|---|---|---|
| 0x3B | Large fire | false | false | Zamietnutý |
| 0x3C | Medium fire | true | false | Zamietnutý |
| 0x3D | Malý fire | true | false | Zamietnutý |

`nonBlockingObjectClass()` nezahŕňa CAUSTIC and `objectBlocksMovement()` does not use pomocný modul ohňa. Two moduly therefore poskytujú rozdielnu odpoveď. Test udržal tables define nažive, so this result is not následkom pamäťovej errors B01.

**Is not correctly only zaradiť celú triedu CAUSTIC between priechodné objects.** Taká zmena by according to existing pomocného modulu uvoľnila also large fire. Needed is prepojenie exact identity object, vlastností, dynamických podmienok and damage branches. assign grafických ID sa nesmie without evidence preniesť on all DOS/Win16 vydania or upravené data balíky.

V package sa this game logic **neopravuje**. Diagnostika naďalej vypisuje `EXPECTED_UNRESOLVED fire_passability_mismatches=2`.

### Zastarané timing v komentári

`HazardSystem.hpp` states DAT_53F2 as kalibrovaný interval aktualizácie during damage. Novší audit `Nite3d-win3.11@7913947/docs/win16/audit-2026-09-24.md`, part 2.3, this interpretáciu explicitly opravuje: damage belongs k slow update, v mode 0 nominálne 8 Hz without dobiehania vynechaných krokov; DAT_53F2 is raw priemer kalibrácie renderu. Other modes have different cestu plánovania.

Patch 03 prenáša this already doloženú opravu to komentára. Preserves enum, names fields, values 100/10/2 also results priechodnosti. Is not new časové meranie or automatické dokázanie škody for sekundu.

## 3. USER.SAV – separate check bloku is not enough on shared write

Skontrolované range are relatívne k jednej vybranej pozícii save:

| Block | Start | End, nezahrnutý | Size |
|---|---|---|---|
| GUARD | 0xB43B | 0xBE63 | 2600 bytes |
| Projectiles | 0xC403 | 0xC553 | 336 bytes |

Separate functions correctly odmietajú príliš krátky target for **its** block still before zápisom. To however does not mean transakčné behavior their postupnej combinations.

### Exact proti-example

Pamäťový buffer has size `0xC553 - 1`, therefore for GUARD stačí, but missing last byte požadovaný projectile blokom:

```cpp
writeGuardSaveBlock(slot, guards);       // úspech; cieľ sa zmení
writeProjectileSaveBlock(slot, shots);   // výnimka: príliš krátky cieľ
```

After výnimke v pamäti zostane new GUARD block. Therefore is not bezpečné z výnimky druhej operations vyvodiť „nezmenilo sa nič“ and increase buffer without next ochrany use as dokončené save.

**None file on disku sa v this pokuse neprepisoval.** Is synthetic skladanie rozhraní, nie finding, that specific existujúca save UI path poškodzuje files. Separate kodeky this shared kontrakt nesľubujú.

### New pomocný code

`UserSaveBlockTransaction.hpp` adds `tryWriteGuardAndProjectileBlocks()`. Before prvým zápisom verify end oboch blokov. During krátkom buffere returns false and none byte nezmení; during platnom buffere can same result as obe separate operations. Nezasahuje to areas mimo these blokov.

This is **moderný dvojblokový preflight v pamäti**, nie rekonštruovaný original symbol, validácia celej USER.SAV structures, confirmation hrateľnosti all fields, synchronizácia vlákien nor atomické save file on disk. Name nezískava vymyslenú address FUN_*.

## 4. Zdravie and HUD – order is part of pravidiel

On existujúcich health helperoch was vykonaný this synthetic test:

| Order | Medzikrok | Konečný result |
|---|---|---|
| 99 HP → pickup +20 → damage 100 → HUD clamp | After pickupe 119 HP; damage nechá 19. | 19 HP, gameState 0 |
| 99 HP → pickup +20 → HUD clamp → damage 100 | HUD najprv decrements 119 on 100. | 0 HP, gameState 2 |

Are to same values and same pomocné operations, only v inom order. V systematickej kontrole 100 počiatočných HP values × 2 pevné pickupy × 256 škodových bytes vzniklo **51 200 kombinácií**, z ktorých **5 377** malo different konečný pár HP/status and **625** different smrteľný/nesmrteľný result. Is not podiel chýb v hre, probable výskytu nor pokrytie EXE; is to comparison dvoch umelo zvolených kompozícií.

Source vysvetľuje why: original branch 3:AND4CE according to uloženého auditu nielen formátuje value, but ju writes back to HP. Therefore cannot its efekt in vernej rekonštrukcii ľubovoľne presunúť or vynechať only therefore, that sa HUD just nekreslí.

**This test nepotvrdzuje, that first order v origináli nastane just between pickupom and konkrétnym útokom.** On to needs to exact cestu call and prípadne runtime stopu. Novší Win16 audit moreover dokumentuje v jednej frame branch order render/projection → player/HUD branches → doors → projectiles → prezentácia → input. Own všeobecné „input → všetka simulácia → render“ therefore nesmie automaticky nahradiť original order.

### HP and status smrti are not tá istá premenná

`restoreTo100()` after stave `{HP=0, gameState=2}` vyprodukuje `{HP=100, gameState=2}`; damage receiver further damage potlačí. Pevný pickup can on same vstupnom stave zapísať `{HP=20, gameState=2}`. Helpery intentionally nerobia respawn nor kompletné rules spotreby predmetu. Is kontrakt call, nie novú chybu v already zdokumentovaných value helperoch.

Podobne is not correctly without evidence use enemy receiver on all environmentálne škody: audit zdravia distinguishes death through status 2 and druhú hazard branch with stavom 3. Kompletné zapojenie tej druhej branches sa tu nevytvorilo.

## 5. What new save tests actually potvrdili

Preskúšaná was kombinácia oboch blokov, nie only osamotené call novej projectile functions:

- Write GUARD and projectile v oboch poradiach can same target. Each byte before blokmi, between nimi and for nimi remains nezmenený.
- projectile rekord passed **10 752** jednobajtovými zmenami (42 pozícií × 256 values); encode(decode(bytes)) zachoval result record.
- Moreover independent kontroly verify little-endian deadline 0x78563412, signed coordinate −1 and −32768 and zachovanie unknown bytes/stavu. Nejde therefore only o two navzájom opačne chybné prevody, which by náhodou vytvorili správny round trip.
- Write GUARD timeru for all 65 536 values changes only bytes +06/+07 testovaného rekordu, other bytes remain same.
- Rebinding during platných coordinate and základni 0xE000 writes očakávané offsety and segments; mimo four pointer bytes does not change status, deadline, steps nor unknown arrays.
- **256** chybných cases rebindingu covers obe osi, each z eight pozícií, four chybné coordinate and stavy 0/1/2/255. Odmietnutie preserves entire pool including skorších platných rekordov. Nadmerné základne 0xE001 and 0xFFFF sa also odmietnu without zmeny.

Check new kodeku v this range **did not find porušenie uvedených byte kontraktov**. Does not mean to complete testovanie all 2^(336×8) possible blokov nor confirmation complete save formátu.

### boundary between transportom and hrateľnosťou

During platných coordinate prejde rebinding also with `state=255` and `stepX=32767`; these values intentionally does not change. Dekódovanie and rebinding are not validátormi kompletnej stavovej logiky projectile. Považovať their success for povolenie spustiť simuláciu is chýbajúca vrstva integrácie, nie error bezstratového transportu. Prípadná validácia aktívnych/neaktívnych rekordov must preserve unknown bytes for forenzný round trip and rozlišovať modernú validačnú politiku from dokázanej compatibility originálnych saveov.

## Performed verify and obmedzenia

| Overenie | Status |
|---|---|
| Git blob identita 13 baseline zdrojov | Success, all files. |
| GCC 14.2, Debug and Release | Shared diagnostika before/after oprave also six opravených lifetime režimov passed. |
| Clang 17, Debug, Release and ASan+UBSan | Shared diagnostika before/after oprave and six opravených lifetime režimov passed. |
| Clang ASan/UBSan before opravou | Očakávané specifically diagnózy during dočasných table, lokálnych table, only dočasnej object table and default stave. |
| Separate CMake/CTest projekt, Clang Release | 7/7 testov prešlo. |
| Aplikovanie all audit-2 patchov on baseline | Success; result sa byte zhoduje with `patched/`. |
| Aplikovanie audit-2 patchov after all minimálnych opravách auditu 1 | Success; none prepisovanie novších/nesúvisiacich file. |

GCC hromadný beh sa after 29 dokončených invokáciách skončil časovým limitom nástroja during next prekladu. Dokončené results are v `validation_gcc_partial.json` and príslušných logoch. ASan+UBSan baseline boundary test v GCC also passed, **entire GCC sanitizer matica however is not označená for dokončenú**. Clang matica is kompletná v `validation_clang.json`. Časový limit was not zamieňaný with chybou testovaného code.

Shared diagnostika has before opravou **1 882 859 kontrol** and after doplnení dvojblokového preflight testu **1 882 863**. These counts are not counts preskúmaných functions or new nálezov. Its success explicitly zahŕňa očakávanú reprodukciu neopraveného nesúladu ohňa and rizikovej priamej dvojice save call. Corrected variant at the same time testuje bezpečnú novú wrapper cestu.

Complete game repository, all its older regresie, MSVC/Windows, original mapy/define, actual USER.SAV files, entire SDL program and originálna Win16/DOS EXE were not testované. Zmena vlastníctva neodstraňuje previous known slabiny jednotkových kolízií, súbehu tlačení, parsera or duplicitných bojových konštánt. Older patche remain separate.

## Files, patche and reprodukcia

- `baseline/`: 13 exact verify C++ zdrojov.
- `patched/`: local proposal vlastníctva, new dvojblokový wrapper and corrected komentár.
- `tests/lifetime_probe.cpp`: pamäťové and vlastnícke reprodukcie.
- `tests/boundaries_probe.cpp`: fire, health order, save integrity, rebinding and dvojblokový preflight.
- `patches/01_owned_definition_snapshots.patch`, `02_two_block_save_preflight.patch`, `03_correct_fire_timing_comment.patch` and shared `all_audit2_changes.patch`.
- `logs/`, `source_manifest.json`, `validation_*.json`, `patch_validation.json`: performed evidence.

Príklady spustenia v environment with Python 3 and GCC/Clang (nástrojový runner was verify on Linuxe):

```sh
python run_audit.py clang debug
python run_audit.py clang release
python run_audit.py clang asan_ubsan
python run_audit.py gcc debug
python run_audit.py gcc release
```

Alternatívny separate build without SDL and original data:

```sh
cmake -S . -B build-local -DCMAKE_BUILD_TYPE=Release
cmake --build build-local
ctest --test-dir build-local --output-on-failure
```

`prepare_patches.py` reprodukuje local proposal from baseline. New patche needs to aplikovať as differences; **nekopírovať entire snapshot through živý repository**, v ktorom can pribudnúť additional zmeny. Without original komerčných assetov, fontov whether cudzieho binárneho programu.

## Dopad on status analysis

Historický working interval **70–85 %** sa this prechodom neprepočítava. Pribudli reprodukovateľné integračné poznatky and locally opravy, nie new meranie pokrytia EXE. Priame original runtime records získané v this prechode: **0**. New directly disassemblované original functions: **0**.

Najdôležitejšie additional game prepojenia v this výseku are exact identita/priechodnosť ohňa, zachovanie poradia HP operations v plánovači and oddelenie bezstratového save transportu from validácie and obnovy actually hrateľného stavu.

## Primárne projektové podklady

Source URL are jednotlivo v manifeste. Kontextové address messages:

1. `marek177/Nitemare3d-reversed@5b80ac0`, `docs/PLAYER_HEALTH_RE.md`, blob `9e99ee59d61cac2877025be098f294debeae5a6b`: https://github.com/marek177/Nitemare3d-reversed/blob/5b80ac0cfbe4c667e0696d711bd8313f7be3bb8f/docs/PLAYER_HEALTH_RE.md
2. `marek177/Nite3d-win3.11@7913947`, `docs/win16/audit-2026-09-24.md`, blob `0f95e2f81e95beb5b6d6aa82b0d32375ef284c05`, novo prečítané lines 88–148, especially parts 2.3–2.4: https://github.com/marek177/Nite3d-win3.11/blob/791394730187ae0ded48e423fd11aa0d68f70f10/docs/win16/audit-2026-09-24.md
3. `HazardSystem.hpp`, `LevelState.hpp/.cpp`, `PlayerHealthRuntime.hpp`, `GuardSaveBlock.hpp`, `ProjectileSaveBlock.hpp` and their závislosti according to `source_manifest.json`.