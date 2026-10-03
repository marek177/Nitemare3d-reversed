# Movement and collisions player — next analytický prechod

**Date:** 24. 9. 2026  
**Target:** continue v analysis boundaries player movement NITE3W, nie only zopakovať percentuálny estimate.  
**Skontrolovaný repository:** `marek177/Nitemare3d-reversed`, commit `9e002c10d0449885af883177d36c3037f2179e82`.

## 1. Result

Vykonaná was check existujúcich auditov, ručný analysis rekonštrukčného movement code and locally spustenie its nezmenených functions on syntetických mapách. Five usage zdrojových file has identical Git blob hash with obsahom získaným through GitHub. Results are v `results.json`.

**Original NITE3W.EXE sa v this kroku nespustilo nor nanovo nedisassemblovalo.** V pracovnom priečinku nebolo provided. Vyhľadanie `nite3w` and `Nitemare` v pripojenom Drive nevrátilo files; to is not evidence, that original prílohy neexistujú v inej knižnici. Findings o original EXE are therefore naďalej findings prevzaté z specific existujúcich auditov, nie new merania original.

Rozlišujeme:

| Designation | Meaning |
|---|---|
| REPO_STATIC | Directly visible v skontrolovanom rekonštrukčnom zdrojovom code. |
| REPO_TESTED | Locally reproduced behom uvedeného rekonštrukčného code. |
| AUDIT_REPORTED | States existing audit original EXE; v this kroku without novej kontroly original bytes. |
| MODEL_DERIVED / MODEL_TESTED | Derived or verify v modeli with výslovnými predpokladmi. |
| OPEN | Question, ktorej odpoveď this step nedokazuje. |

## 2. Difference no.. 1: koncová cell namiesto kolízneho obalu

`LevelState::tryMovePlayer()` computes `nx`, `ny`, then `floor(nx)`, `floor(ny)`. verify priechodnosť this jednej cells and dodatočnú distance from posúvateľných object. Is not tu calculation nábežnej hrany player obalu ±27 nor priebežné prechádzanie požadovaného posunu after units. **REPO_STATIC, REPO_TESTED. [WITH1]**

Existing audit NITE3W opisuje 27-jednotkový polovičný rozmer osovo zarovnaného obalu, 64 jednotiek on bunku and nábežnú hranu kontrolovanú pomocnou routine `3:84F4`. **AUDIT_REPORTED. [WITH3]**

Consequence v rekonštrukcii: stred player can postúpiť to polohy, v ktorej by modelovaný obal already zasiahol susednú wall, hoci stred itself remains in voľnej bunke. Nejde only o kozmetickú odchýlku vykresľovania: changes sa dosiahnuteľná poloha during wall, rohoch and object.

## 3. Difference no.. 2: osové kĺzanie existuje, but integrátor is not same

call `src/main.cpp` naozaj executes:

```cpp
world.tryMovePlayer(moveX, 0.0, true);
world.tryMovePlayer(0.0, moveY, true);
```

Therefore by was incorrectly napísať, that reconstruction vôbec does not have kĺzanie. Test with player `(639,672)` and požiadavkou `(+2,+2)` during wall on stĺpci 10 confirmed zamietnutie X and prijatie Y: result `(639,674)`. This počiatočná poloha slúži only as check existing code; is not platná v modeli ±27 during this wall. **REPO_STATIC, REPO_TESTED. [WITH2]**

Difference compared with auditu is v inom rozdelení posunu: reconstruction urobí entire X-posun and then entire Y-posun, until audit opisuje jednotkové steps hlavnej osi with celočíselným riadením vedľajšej osi. Exact počiatočná error, rozhodovanie during rovnosti, order podkrokov and behavior after odmietnutí osi still are not this balíkom rekonštruované. **AUDIT_REPORTED / OPEN. [WITH3]**

## 4. Difference no.. 3: status door is not vstupom rozhodovania reconstruction

`wallAllowsMovement()` povoľuje names tried `FLOOR`, `ACTIONSPOT` and prefix `TRIGGER`. During nezmenenom ID/triede `DOORVL` v syntetickom teste nepovolí prechod and neprijíma none door runtime status. **REPO_STATIC, REPO_TESTED. [WITH1]**

Audit opisuje other cestu: wall flags `0x08` → vyhľadanie 22-byte record door → check `DoorRuntime+0x0C`, pričom skúmaná brána akceptuje value 0 or 4. **AUDIT_REPORTED. [WITH3]**

V modelových testoch are therefore 0 and 4 priechodné, but do not have automaticky ľudské names „open“ or „zatvorené“. This step neodhalil their úplnú stavovú sémantiku. Test with týmito číslami nemeria none actual doors v original hre: reads their only obmedzený model. Rekonštrukčná function also array does not have.

Themselves visually odsunutie door therefore is not enough as náhrada original pravidla priechodnosti. Najnovší Win16 audit moreover zaraďuje aktualizáciu door `3:1E00` before spracovanie player vstupu `3:9806` v skúmanej frame branch. During budúcom compare needs to zachytiť status use just during kolízii, nie náhodný susedný render. **AUDIT_REPORTED. [WITH5]**

## 5. Difference no.. 4: movement sa object can v rekonštrukcii skončiť v player

Synthetic object PUSH začínal v bunke `(10,10)`, therefore v strede `(672,672)`. Player was v cieľovej bunke `(11,10)`, v strede `(736,672)`. Cieľový MAP object byte was zero.

`beginPush(10,10,1,0)` vrátil true. After eight `tickPushables()` mal object polohu `(736,672)` and player zostal on same polohe. **Prekrytie stredov was actually reproduced v rekonštrukčnom code. REPO_TESTED.**

Príčina v this code: cieľový test požaduje priechodnú wall and `cell.object == 0`, but netestuje polohu player. Itself tick moves object without korekcie player. `positionBlockedByPushable()` is call during player pokuse o movement, nie as priebežná prevencia vstupu object to player. [WITH1]

**This is not evidence errors original NITE3W.** Original reakcia on obsadenú cieľovú bunku remains open. During next rozbore needs to odlíšiť blokovanie cells, player obal ±27 and separate prah 42 v existujúcom registri; these veličiny cannot without callerov zameniť. Register itself during prahu 42 states čiastočnú sémantiku. [WITH6]

## 6. Dotyk is not only priechodnosť

Test vstupu on synthetic FOOD object confirmed, that `tryMovePlayer()` movement prijme and ponechá object ID nezmenené. Function neobsahuje pickup/special-touch dispatch nor player health/inventory system. **REPO_STATIC, REPO_TESTED. [WITH1]**

To samo osebe does not mean, that originál must each FOOD always odstrániť: can rozhodovať plné zdravie, inventory whether other status. Confirms to however, that rekonštrukčný movement neimplementuje vedľajšie effects dotyku opísané during `3:84F4`/`3:CF60`. Tie are different úlohou from geometrickej priechodnosti. **AUDIT_REPORTED. [WITH3]**

## 7. Exact modelové boundary and coordinate

**All following coordinate are synthetic svetové units, nie merania original MAP.1 nor živého NITE3W.** Rekonštrukčný code uses dlaždicové double coordinate; test their for zrozumiteľnosť multiplies 64. Input numbers delené 64 are v these testoch binary exact.

Model uses:

```text
ľavá kontrolovaná bunka  = floor((x - 27) / 64)
pravá kontrolovaná bunka = floor((x + 27) / 64)
horná kontrolovaná bunka = floor((y - 27) / 64)
dolná kontrolovaná bunka = floor((y + 27) / 64)
```

Oba final body are zahrnuté to vzorkovania. For pevnú wall začínajúcu on `x=640` is during this modeli last bezpečný celočíselný stred `x=612`; `x=613` can `x+27=640`. On druhej strane walls zaberajúcej `640..703` is first bezpečný stred `x=731`. During jednobunkovej chodbe `640..703` vychádzajú povolené stredy `667..676`, therefore ten celočíselných pozícií.

**Final nerovnosti are výslovný predpoklad modelu.** Calculation does not close otázku, whether originál v each branch vzorkuje just these body, whether uses kontakt on hrane same and whether has korekciu o jednu jednotku. Zmena on polootvorený obal by mohla posunúť hraničný result. To must rozhodnúť assembler and/or original trace.

| Scenár | Before | Requirement | Zmerané after — repository | Vypočítané after — obmedzený model | Result |
|---|---|---|---|---|---|
| `free_one_unit` | `(612, 672)` | `(1, 0)` | `(613, 672)` | `(613, 672)` | match |
| `static_x_positive_contact` | `(612, 672)` | `(1, 0)` | `(613, 672)` | `(612, 672)` | difference |
| `static_x_negative_contact` | `(731, 672)` | `(-1, 0)` | `(730, 672)` | `(731, 672)` | difference |
| `static_y_positive_contact` | `(672, 612)` | `(0, 1)` | `(672, 613)` | `(672, 612)` | difference |
| `static_y_negative_contact` | `(672, 731)` | `(0, -1)` | `(672, 730)` | `(672, 731)` | difference |
| `corridor_left_limit` | `(667, 672)` | `(-1, 0)` | `(666, 672)` | `(667, 672)` | difference |
| `corridor_right_limit` | `(676, 672)` | `(1, 0)` | `(677, 672)` | `(676, 672)` | difference |
| `wall_slide` | `(612, 672)` | `(4, 4)` | `(616, 676)` | `(612, 676)` | difference |
| `convex_corner_xy` | `(612, 612)` | `(1, 1)` | `(613, 613)` | `(613, 612)` | difference |
| `door_state_0` | `(639, 672)` | `(1, 0)` | `(639, 672)` | `(640, 672)` | difference |
| `door_state_4` | `(639, 672)` | `(1, 0)` | `(639, 672)` | `(640, 672)` | difference |
| `door_state_2_contact` | `(612, 672)` | `(1, 0)` | `(613, 672)` | `(612, 672)` | difference |
| `large_delta_tunnel` | `(608, 672)` | `(128, 0)` | `(736, 672)` | `(612, 672)` | difference |
| `last_safe_x` | `(608, 672)` | `(4, 0)` | `(612, 672)` | `(612, 672)` | match |
| `object_contact` | `(612, 672)` | `(1, 0)` | `(613, 672)` | `(612, 672)` | difference |

During `convex_corner_xy` is X→Y zvolená modelová politika; nepredstavuje evidence original poradia during diagonále. During door is status 0/4/2 input only modelu, nie existing API repozitára. During `large_delta_tunnel` is záťažový test API: delta 128 jednotiek skips celú wall and skončí in voľnej bunke. **Normal main loop this large posun negeneruje** — normalizuje vektor and limituje dt on 0,05 with, so during moveSpeed 2,1 vychádza najviac 6,72 svetovej units celkového posunu for iterate. Is not tvrdenie, that bežná chôdza pravidelne iterate through celými wall. [WITH2]

Pätnásť scenarios was vybraných cielene on boundary differences. Trinásť different result is not trinásť nezávislých chýb and pomer 13/15 is not percento nepresnosti celej game.

## 8. New geometrické uzavretie v rámci modelu

During šírke 54 menšej than width cells 64 zasahuje nábežná hrana najviac two cells v priečnom smere. Z platnej nekolíznej počiatočnej polohy possible during jednotkovom osovom kroku v statickej mape rozhodnúť o novom prekrytí pomocou dvoch koncových bodov nábežnej hrany.

Test passed all 512 vzorov obsadenosti okolia 3×3, all 64×64 celočíselných polôh stredu v prostrednej bunke and four smery. Neplatné počiatočné polohy vyradil. Zostalo **257 152 platných konfigurácií** and **1 028 608 compare** dvojbodového testu with celým vzorkovaným obalom. Rozporov: **0**. **MODEL_TESTED.**

Is uzavretie this geometrickej vlastnosti for uvedený konečný model. Test nezahŕňa dynamickú zmenu mapy during kroku, dotykové skripty, zmenu door stavu uprostred calls, already prekrytého player, damage pointery, original 16-bit pretečenia nor three for-commit helpery.

During same pointe/bunke on oboch koncoch possible geometrickú value read raz, but **nesmie sa automaticky deduplikovať count dotykových callbackov** without findings original behavior. Geometrická ekvivalencia does not mean ekvivalenciu vedľajších účinkov.

## 9. Three helpery before commitom remain important

`DEMO_FORMAT_RE.md` states three pomocné calls before konečným zápisom polohy and explicitly hovorí, that their effects needs to still rekonštruovať. Known offsety X/Y and prevod `>>6` therefore samy o sebe neuzatvárajú autoritatívny result movement. [WITH4]

Odporúčané order next original rozboru:

| Target | What must be supported |
|---|---|
| `3:84F4` | Exact order wall/object testov and hookov; cached vs. znovu read flags; behavior during zhodných dvoch bunkách. |
| `3:8604`, set during `3:E552` | Initial akumulátor, rovnosť prahov, znamienka, order hlavných/vedľajších krokov, reakcia on odmietnutú os. |
| `3:8A20` | Addresses and complete input/výstupné effects all troch for-commit helperov; last writer X/Y. |
| `3:E3B0` | Vedľajší effect branches nárazu to pevnej walls and podmienky its calls. |
| `3:1476`, `3:1E00` | Complete door stavová matica, obsadenie priestoru, priechodnosť during zmeny stavu and order in frame. |

Addresses are dokumentačné NE segments/offsety, nie directly usage Windows selektory. [WITH5]

Potrebný original trace for one pokus has obsahovať hash EXE and MAP, počiatočné X/Y, požadovaný vektor, all pokusy o osový step, testované cells and flags, status door usage during kontrole, result helperov, konečné X/Y and event zmeny cells. Itself screenshot or two nečasovo previazané polohy nestačia on určenie, which branch rozhodla.

## 10. Testovanie and percentá

Locally results:

- 15 cielených compare nezmenenej implement with obmedzeným modelom; 13 rozdielov, 2 matches.
- Three additional kontrolné scenáre: existing osové kĺzanie, zachovanie FOOD ID during vstupe, posun PUSH to stredu player.
- 1 028 608 kontrol geometrického modelu, without rozporu.
- CMake/CTest: jedna testovacia binárka, úspešný beh.
- Opakovaný beh with AddressSanitizer and UndefinedBehaviorSanitizer: identické JSON results, without hlásenej diagnostiky v skúmaných scenároch.
- New behy original NITE3W: **0**.

Previous „90–95 %“ was orientačné value hlavného statického mechanizmu, nie calculation dokončenia all functions, vedľajších účinkov nor implement. This step ho automaticky nezvyšuje. Dokazuje konkrétnu medzeru between existujúcimi poznatkami and vykonávanou rekonštrukciou and poskytuje reprodukovateľné tests. Complete end-to-end percento without registrácie and váženia all požadovaných vetiev is not supported.

Repository on GitHube was not menený. Package is local audit and testovacia sada, nie potichu aplikovaná correction nor dokončený port.

## Zdroje

[WITH1] `src/game/LevelState.cpp`, commit `9e002c10d0449885af883177d36c3037f2179e82`: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/game/LevelState.cpp

[WITH2] `src/main.cpp`, same commit: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/main.cpp

[WITH3] `docs/PLAYER_COLLISION_RE.md`, same commit: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/docs/PLAYER_COLLISION_RE.md

[WITH4] `docs/DEMO_FORMAT_RE.md`, same commit, part o for-commit helperoch: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/docs/DEMO_FORMAT_RE.md

[WITH5] `marek177/Nite3d-win3.11/docs/win16/audit-2026-09-24.md`, load blob `0f95e2f81e95beb5b6d6aa82b0d32375ef284c05`: https://github.com/marek177/Nite3d-win3.11/blob/main/docs/win16/audit-2026-09-24.md

[WITH6] `src/game/RecoveredRuntime.hpp`, first part, same commit: https://github.com/marek177/Nitemare3d-reversed/blob/9e002c10d0449885af883177d36c3037f2179e82/src/game/RecoveredRuntime.hpp

Locally primárne results: `results.json`, `results_sanitized.json`, `source_manifest.json`, `ctest.log`, `sanitizer.log`. Test source: `collision_probe.cpp`.