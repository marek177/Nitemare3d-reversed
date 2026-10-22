# Nitemare 3D DOS v2.0 — E1M1 kombinované šípky a uvoľnenie vstupu

**22. 10. 2026 | dôkazová trieda: FRESH ORIGINAL DOS2 RUNTIME | moderná 1:1 behaviorálna parita: NOT TESTED**

V novej izolovanej relácii originálneho `N3D-E-20.EXE` v upravenom Linux DOSBox-X Advanced History v3 som automatizovane odoslal originálnej hre skutočné X11/XTest udalosti stlačenia a uvoľnenia ↑, → a ↓. Načítala sa mapa **E1M1**, obtiažnosť „I'm tough!“. V bežiacom emulátore som našiel aktuálny DOS 64KiB dátový segment porovnaním pôvodnej `DS:4A64` palety a `DS:62AC` VEC záznamov. Externý hostiteľský sampler čítal `DS:4162/4164` (X/Y), `DS:4156` (smer), `DS:4540` (render counter) a `DS:1738` (čítač). Interval vzorkovania bol približne **12 ms**.

**Pôvodný EXE:** SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. **DOS IMG.1:** `faf0cec3502d8b86ebb30a432b46b467e349864987f91a1c26358a9a5ca58cb1`. **DOS MAP.1:** `3eddb0ad3a29e93d63fa16e9b8cfbb434d3699a84bd5372ed2d6f4a1e89c42fc`. Počiatočný herný stav: `X/Y=(1440,3616)`, smer `0`, 592 VEC, 9 viditeľných spanov.

## Test A: kombinované šípky, dva poriadky uvoľnenia

| Aktivita | Začiatok | Koniec | ΔX / ΔY / Δsmer | Zmena render count |
|---|---|---|---|---:|
| Bez klávesov | (1440,3616,0) | (1440,3616,0) | 0 / 0 / 0 | 12 |
| Držané ↑+→ | (1440,3616,0) | (1508,3492,130) | +68 / −124 / +130 | 26 |
| Uvoľnené →, stále ↑ | (1508,3492,140) | (1508,3492,140) | 0 / 0 / 0 | 22 |
| Uvoľnené oba | (1508,3492,140) | (1508,3492,140) | 0 / 0 / 0 | 19 |
| Znova držané ↑+→ | (1508,3492,140) | (1432,3500,245) | −76 / +8 / +105 | 21 |
| Uvoľnené ↑, stále → | (1422,3505,250) | (1422,3505,345) | 0 / 0 / +95 | 19 |
| Uvoľnené oba | (1422,3505,350) | (1422,3505,350) | 0 / 0 / 0 | 22 |

**Meranie:** 461 vzoriek, 7 fáz. Samotné → po uvoľnení ↑ spôsobuje otáčanie bez translačného pohybu; pozorované prírastky smeru počas držania → sú po 5 jednotiek. Uvoľnenie oboch klávesov spôsobilo stabilitu XY/smeru počas pokračujúceho renderovania. Samotné ↑ pri `(1508,3492,140)` nevyvolalo pohyb; obraz ukazuje blízky stenový roh/policu. Ide o hypotézu kolízie, nie o potvrdenú runtime vetvu kolízneho kódu.

## Test B: kontrola ↑ a ↓ pri smere 350

| Aktivita | Začiatok | Koniec | ΔX / ΔY / Δsmer | Zmena render count |
|---|---|---|---|---:|
| Bez klávesov | (1422,3505,350) | (1422,3505,350) | 0 / 0 / 0 | 10 |
| Držané samotné ↑ | (1422,3505,350) | (1376,3291,350) | −46 / −214 / 0 | 25 |
| ↑ uvoľnené | (1375,3291,350) | (1375,3291,350) | 0 / 0 / 0 | 17 |
| Držané samotné ↓ | (1375,3291,350) | (1402,3441,350) | +27 / +150 / 0 | 15 |
| ↓ uvoľnené | (1405,3461,350) | (1405,3461,350) | 0 / 0 / 0 | 17 |

**Meranie:** 273 vzoriek, 5 fáz. Samotné ↑ a ↓ sa na otvorenejšej trase skutočne hýbu; po uvoľnení sa poloha stabilizuje. V niektorých prepínacích medzerách sa medzi poslednou vzorkou pred uvoľnením a prvou po uvoľnení stihol vykonať ďalší update. To **nepreukazuje zotrvačnosť ani presné oneskorenie v tickoch**, pretože vzorkovanie nebolo inštrukčne atómové.

## Dôkazový výsledok a ďalší krok

- **734 originálnych vzoriek**, 12 fáz, získaných z dvoch nových kontrolných sekvencií v tej istej bežiacej originálnej DOS2 relácii.
- CSV a JSON boli overené nezávislým kontrolným skriptom vrátane fáz, počtov, render counterov a stacionárnych úsekov.
- User-visible originálne súbory merania, reprodukčné XTest Python skripty, grafy a dôkazové screenshoty sú priložené používateľovi v konverzačnom ZIP **`N3D_DOS20_E1M1_COMBINED_KEYS_Runtime_20261022.zip`**, SHA-256 `e9560ae99d8ad80ffdf6f2da4cec5f2cc07ae2110c0018caeea2dacbfaebfbb2`. **Nepublikujem používateľove EXE, IMG, MAP ani celé RAM/VRAM.**
- **Zatiaľ NIE JE zmeraná moderná C++ remake parita.** CPU per-instruction order, originálne key-bit masky, kolízna vetva a deterministický gameplay tick sú samostatné dôkazové úlohy. Nesmie sa zamieňať hostiteľský čas s presným počtom herných tickov.
- Najbližší runtime pass: zaznamenať **KEYSTATE → movement/rotation update → player XY commit** vo vykonávacích trace, obzvlášť pri kolíznom kontakte pri smere 140, následne spustiť rovnaký vstup na remake a reportovať prvú divergenciu.

**Žiadne zmeny aktívneho diagnostického `Raycaster.cpp` alebo `src/main.cpp` sa v tomto teste nevyžadujú.**
