# Nitemare 3D DOS v2.0 — E1M1, originálny runtime FIRE/USE/Alt (v0.85–v0.86)

**21. 10. 2026. Skutočne vykonané dva nové testy pôvodného DOS v2.0 v upravenom Linux DOSBox-X; nejde o simuláciu ani o original↔remake behaviorálnu/pixelovú paritu.**

## Originálna identita a metodika

- Originál `N3D-E-20.EXE` (116 606 B), SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`, E1M1, DS `2F95`, load image `8240`; živé FEFA (18B) a 1021E (16B) opcode prefixy sa zhodujú s originálnou EXE.
- Skutočné X11 **XTest keyDown/keyUp** na ovládacom okne pôvodného emulátora; game EXE, IMG, MAP aj guest RAM zostali nezmenené. Všetky pamäťové merania sú **read-only** cez `/proc/PID/mem`.
- Sledované DS: `3F50` vstupná maska; `4156` smer; `4162/4164` hráč XY; `4540` render counter; `1738/173C` pomocné hodiny; `41B6` osem 42-bajtových slotov; episode/level `626A/626C`.

## Vykonané nové runtime merania

| Fakt | v0.85 | v0.86 | Spolu |
|---|---:|---:|---:|
| Originálne vzorky RAM | **935** | **781** | **1716** |
| Vzorky so zhodnou maskou po injektovaní klávesov | **917** | **771** | **1688** |
| Prechodové vzorky so starou maskou | 18 | 10 | 28 |
| Fázy | 13 | 11 | 24 |
| Akceptované XTest stlačenia/uvoľnenia | 14 | 10 | 24 |
| Medián host pollingu | 12,314 ms | 12,310 ms | — |
| Najväčšia medzera host pollingu | **446,357 ms** | **48,602 ms** | — |

### Úplná pôvodná pravdivostná tabuľka `DS:3F50`

| Držané klávesy | Originálna maska |
|---|---|
| žiadne | `0x0000` |
| Ctrl / FIRE | `0x0080` |
| Alt | `0x0100` |
| Ctrl+Alt | `0x0180` |
| Space / USE | `0x0200` |
| Ctrl+Space | `0x0280` |
| Alt+Space | `0x0300` |
| Ctrl+Alt+Space | `0x0380` |

v0.85 priamo preukázal všetkých 6 kombinácií bez `Ctrl+Alt` a triple. v0.86 potvrdil všetkých **8/8** masiek, oba poradia stlačenia Ctrl/Alt aj postupné uvoľnenie. Každá fáza dosiahla svoju očakávanú masku a v jej stabilnej záverečnej časti sa maska nevrátila na nesprávnu hodnotu.

Zachytené nezhody boli iba na hraniciach fáz. **Pozor:** v0.85 sa pri zapnutí Space držala predchádzajúca maska v prvých siedmich vzorkách, posledná až ~442 ms od prvého vzorkovania tej fázy. Host scheduling mal pritom medzeru 446 ms. Nie je prípustné z toho vyvodzovať emulovanú latenciu USE či DOS tikovú frekvenciu. V0.86 mali všetky prechodové nezhody podobu prvej vzorky fázy a maximálny nameraný host gap bol 48,6 ms.

## Ďalšie pôvodné gameplay fakty a limity

- Pri oboch experimentoch zostali `X=1371, Y=3587, angle=312` stabilné, zatiaľ čo render counter ďalej rástol.
- Osem 42B blokov projektilovej tabuľky `DS:41B6` sa v odčítaniach nemenilo. **Nie je to dôkaz, že FIRE nefunguje:** aktuálna zbraň môže byť hitscan, bez munície alebo inak obsluhovaná; nebol vykonaný inštrukčne presný audit ammo/writer eventov. Surové `DS:4C1F/4C20/4C44` sa neznačia ako „ammo“ bez samostatného opcode dôkazu.
- Všetky 3 klávesy boli na konci uvoľnené. Následná samostatná read-only kontrola v stále bežiacom DOS2 ukázala **5/5 mask=0**, rovnakú XY/angle a pokračujúci render-counter.
- `DS:3F50` odráža held-key bitovú masku. Tieto merania **nepreukazujú per-tick poradie FIRE/USE, dosah akčných dverí ani vznik projektilu**, a vôbec neporovnávajú C++ remake.

## Validácia a reprodukcia

Používateľský konverzačný ZIP `N3D_DOS20_E1M1_LIVE_ACTION_KEYS_Runtime_V085_V086_20261021.zip` obsahuje autentické odvodené CSV/JSON, dva **skutočne vykonané** XTest skripty, nezávislý audit a **15/15** lokálnych auditných regresií (2 pozitívne overenia originálnych behov, 13 mutačných negatívnych prípadov). Auditné regresie **nie sú** ďalšie originálne herné behy. Konzolové skripty s host PID/guest memory base sú viazané na konkrétnu reláciu — na novom hoste ich nepoužívajte bez opätovného overenia.

Obsahové odtlačky originálne nameraných CSV:
- v0.85: `da0c99ca99216e87476c25efe48a8b80a4bd3f06cd1f89f16cfef75ea25355ac`
- v0.86: `7a63230c511d8f60986c173e91a0f3b2eb7b93efca6882caf840b2b0e46b48c2`

**Žiadne originálne komerčné EXE, IMG/MAP ani úplná RAM nie sú zahrnuté v balíku či repozitári.** Záznam dokladá nové vykonané behy pôvodnej hry, nie hotový remake.

## Ďalší P0 runtime krok

Inštrukčne sledovať pôvodný **FIRE weapon state / fire-clock / ammo / 8-slot projektilový scheduler**, a USE pri konkrétnom ActionSpot alebo dverách; porovnať držanie/uvoľnenie a rovnaký deterministický tick s C++ kandidátom. Náhodné per-frame nulovanie Ctrl+Alt alebo Ctrl+Space bez originálneho dispatcher dôkazu sa nesmie implementovať.
