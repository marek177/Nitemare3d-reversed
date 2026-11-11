# DOS 2.0: DSP status wrapper a štyri formátové reťazce

## Rozsah a CFG

Vstup 0C2B:0020 končí RETF na 0C2B:00A9. Obalový rozsah `[0C2D0,0C35A)` má 138 B; prieskum CFG od vstupu dosiahne **48 inštrukcií / 136 B**. Bajty 0C2B:006B a 0089 sa z tohto vstupu nedosiahli; do kódu sa nezapočítali a samotné nedosiahnutie ich neoznačuje za padding. Priame vetvy sú uzavreté na hranice inštrukcií, pokračovanie za CALL predpokladá návrat callee. Žiadna skoková tabuľka nie je súčasťou tohto tela.

Vstupné argumenty na zásobníku sa nečítajú. Stav poskytuje BYTE DS:3CC8 a WORDy DS:3CCA/3CCC. Tieto globály ležia mimo file-backed obrazu, preto sa im nepripisujú historické NON-CODE bajty. Funkcia vytvorí 64 B lokálny buffer na SS:[BP-40h], zachová SI a BP, v AX vracia zvolenú hodnotu SI. Explicitne neprepína DS/ES/SS; ich zachovanie cez externé rutiny je otvorená závislosť.

## Rekonštruované vetvenie

```text
if byte DS:3CC8 != 0:
    call 10BF:073D()                   # výsledok sa tu nepoužije
    r = signed16(call 10BF:076F(DWORD DS:3CCA))
    si = (r >= 0) ? WORD DS:3CCC : 0
    if WORD DS:3CCC == si:
        format(local64, DS:1740, WORD DS:3CCA, WORD DS:3CCC)
    else:
        format(local64, DS:1763)
else:
    si = signed16(call 10BF:073D())
    if si > 0:
        format(local64, DS:1782, si)
    else:
        format(local64, DS:179D)
debug_log(local64)
return AX = si
```

Všetky tri formátovacie call sites smerujú na CRT 11EE:278C. Následný logger je 0476:0078, analyzovaný v predchádzajúcej dávke. Lokálny near pointer odvodený zo SS sa odovzdáva bez explicitnej zmeny DS; správny prístup formátovača/loggera k nemu závisí od modelu pamäte a CRT ABI. Neoznačuje sa za uzavretý iba preto, že texty a call sites sú známe.

Mená „DSP“ a „IRQ“ sú priamo z reťazcov; úplný hardvérový kontrakt rutin 10BF:073D/076F sa touto analýzou nepotvrdzuje. Dôležité dôsledky lokálneho CFG:

- Vo forced vetve pri nekladnom zmysle sondy rozhoduje konkrétne test `r < 0`; nula je prijatá ako nezáporný výsledok.
- Pri `r < 0` sa SI vynuluje. Ak je DS:3CCC tiež nula, porovnanie napriek tomu vyberie forced-success text. Úspešná formulácia textu sama nedokazuje úspešnú sondu.
- V automatickej vetve sa pri `si <= 0` vyberie fallback text, ale záporné SI sa neprepisuje na nulu. AX môže vrátiť zápornú hodnotu.
- Ak logger nič nevypíše pre vypnutý debug príznak, sondovanie a formátovanie pred ním sa aj tak vykonajú, ak sa ich callee vrátia.

## Presné NON-CODE polia

| DS offset | Obrazový interval, koniec exclusive | B | Text bez NUL |
|---|---|---:|---|
| 1740 | [28E50,28E73) | 35 | `SB DSP forced on port %xH, IRQ %d\n` |
| 1763 | [28E73,28E92) | 31 | `Unable to force DSP detection\n` |
| 1782 | [28E92,28EAD) | 27 | `SB DSP detected at IRQ %d\n` |
| 179D | [28EAD,28EDD) | 48 | `SB DSP not detected - defaulting to PC speaker\n` |

Spolu **141 B**, každý interval vrátane NUL, s konkrétnym spotrebiteľom a SHA-256 v `data_fields.csv`. Pri konvenčných 16-bit `%x` a `%d` majú maximálne formátované výsledky vrátane NUL 41, 31, 31 a 48 B. Tieto dĺžky sa zmestia do 64 B; nejde o nezávislý dôkaz kontraktu ani bezchybnosti skutočného CRT formátovača.

## Reprodukcia a pokrytie

`audit_pass1_dsp_status.py IMAGE INVENTORY DECODER_DIR OUT` overuje identitu obrazu, bajty každého dosiahnutého začiatku, CFG, externé call targets a štyri NUL hranice. Výstupy v `pass1_dsp_status/`: `instructions.csv`, `cfg_edges.csv`, `calls.csv`, `formats.csv`, `data_fields.csv`, `summary.json`. Prvý pokus lineárneho dekódovania odhalil dve diery v inventári; výsledný skript preto vykonáva prieskum CFG a nepridáva tieto bajty k vykonateľnému telu.

Promóciu reprodukuje `promote_pass1_fields.py IMAGE pass1_debug_logger/noncode_intervals.csv pass1_dsp_status/data_fields.csv pass1_dsp_status`. Všetkých 141 B prešlo z CLASSIFIED ONLY do PARTIAL. `verify_pass1_partition.py` nezávisle overil **634 intervalov**, presné členstvo 57 295 B, SHA, nulové diery a prekryvy. Aktuálne: **54 558 B PARTIAL, 2 693 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**.

Regenerovaný centrálny katalóg: 42 funkčných rozsahov, 1 450 inštrukcií / 3 354 B kódu, 55 404 B typovaných dát celého obrazu; v pôvodnom NON-CODE je typovaných 54 556 B. Rozdiel 2 B oproti PARTIAL zostáva neuzavretý relokačný WORD. Replay prípady zostávajú 6 091 a prirodzené runtime testy 0. Táto dávka zatiaľ nie je na GitHub.

## Aktualizácia 13 oblastí

Nové sémantické percento by bolo počet uzavretých jednotiek / úplný inventár jednotiek oblasti. Menovatele stále chýbajú; nové percentá sú N/A. Predošlé hodnoty sú orientačné. Nové výsledky majú stav PARTIAL.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Neznáme / blokátor | Konkrétny ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | bez nového dôkazu | prirodzené stavy | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 141 B / 4 formáty | runtime vstupy | sledovať DS:3CCA/3CCC |
| Tabuľky a ukazovatele | 93 % | N/A | lokálny 64 B buffer | SS/DS ABI | CRT 278C |
| Funkcie / ASM / CFG | 90 % | N/A | 48 inštrukcií a obe vetvy detekcie | hardvérové callee | 10BF:073D/076F |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | bez nového dôkazu | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bez nového dôkazu | clipping | payload spotrebitelia |
| GUARD / bossovia | 93 % | N/A | bez nového dôkazu | lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | bez nového dôkazu | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | bez nového dôkazu | LOAD parity | porovnať stav |
| Windows Win16 | 92 % | N/A | bez nového Win dôkazu | DS callerov | caller guardy |

## Runtime testy na vykonanie

Na izolovanej kópii zachytiť vstupy/AX oboch sond, DS:3CC8/3CCA/3CCC a finálny buffer. Matica: auto výsledky záporný/nulový/kladný; forced sonda záporná/nezáporná a požadované IRQ nula/nenula; debug flag zapnutý/vypnutý. Overiť DS a SS pri CRT 278C aj loggeri a porovnať návrat AX s textom. Riadené nahradenie návratu sondy je samostatný experiment a nesmie sa počítať za prirodzené hardvérové správanie. Priložený Linuxový DOSBox-X zatiaľ nemá v tejto relácii zistený spustiteľný Linux guest; stav je v `RUNTIME_BUNDLE_PROBE_REPORT.md`.
