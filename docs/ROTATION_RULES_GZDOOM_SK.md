# Nitemare 3D → GZDoom/ZDoom: pravidlá rotácií

## Typy sa nesmú miešať

1. **ROT8** – osem skutočných smerov. Prvých 32 snímok je 8 smerov × 4 fázy pohybu.
2. **ROT4** – štyri kardinálne smery. Prvých 32 snímok je 4 smery × 8 fáz pohybu. Diagonály sú zatiaľ iba pracovné duplikáty.
3. **ROT0** – kamera-facing/front-only sekvencia. Nepokúšať sa z nej automaticky robiť 8 rotácií.
4. **SPECIAL** – scripted alebo neúplné dáta; osobitný actor/script.

## Doom sprite meno

`PPPPFR`, kde `PPPP` je 4-znakový prefix, `F` je frame letter a `R` je rotácia 0 alebo 1–8.

Príklad Frankenstein walk:

- `FRNKA1 ... FRNKA8`
- `FRNKB1 ... FRNKB8`
- `FRNKC1 ... FRNKC8`
- `FRNKD1 ... FRNKD8`

## ROT8 source formula

N3D u overených bankov ukladá prvých 32 obrázkov po smerových blokoch:

`sourceFrame = directionBlock * 4 + animationPhase + 1`

Teda fáza A = 01,05,09,13,17,21,25,29; fáza B = 02,06,...30 atď.

## ROT4 source formula

Penelope a Dr. Hamerstein majú:

`sourceFrame = directionBlock * 8 + animationPhase + 1`

Vizuálne: bloky sú bočný A, chrbát, spredu, bočný B. Kardinálne mapovanie sa preto dá spraviť bez hádania front/back; iba handedness bočných rotácií 3/7 treba otestovať. Diagonálne 2/4/6/8 sú v `rot4_diagonal_fill_v2.csv` označené ako PROVISIONAL.

## Dôležité

`ROT0` nie je chyba. Zelda, Vampira, gargoylovia, Ghost a ďalší pôvodne používajú front-facing banky, takže ich treba držať oddelene od `ROT8` monsterov.