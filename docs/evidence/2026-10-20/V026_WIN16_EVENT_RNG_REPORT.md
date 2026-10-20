> Archived supplied source report: REPORT_SK(20261020-202944).md. Integrated as attributed evidence; private source artifacts and its original-data verifier were not rerun for this bulk update. See [current validation and limits](../../BULK_UPDATE_20261020.md).

# Nitemare 3D — v26: prvý úplný Windows EVENT RNG draw

**20. 10. 2026 · DOS V2.0 / Windows V1.10 · statika + cielený Win16 runtime**

## Hlavný výsledok

Vo Windows 3.11 a upravenom DOSBox-X Advanced History v3 sa podarilo **v jednom nezmenenom `NITE3W.EXE` a jednom procese** zastaviť hernú EVENT rutinu pred RNG, hneď po návrate a po zápise časovača.

| Fáza | Skutočný `CS:IP` | CPU / pamäť | Dôkaz |
|---|---|---|---|
| Pred volaním | `14C7:BADD` | `DS=148F`, RNG `DS:[0A90..0A93]=01 00 00 00` | `EVIDENCE/rng_before.png` |
| Po volaní | `14C7:BAE2` | `AX=0029` (41), RNG `C0 E2 29 00` | `EVIDENCE/rng_after.png` |
| Po zápise časovača | `14C7:BAF0` | `DS:[38EE]=00C9` (201), zobrazené ako živá anotácia disassemblera | `EVIDENCE/timer_stored_value.png` |

Runtime disassemblácia priamo ukazuje:

```asm
14C7:BADD  CALL FAR 14BF:32D2 ; RNG wrapper
14C7:BAE2  MOV CX,00F0       ; 240
14C7:BAE5  CWD
14C7:BAE6  IDIV CX
14C7:BAE8  ADD DX,00A0       ; +160
14C7:BAEC  MOV [38EE],DX
14C7:BAF0  PUSH 0000        ; breakpoint po zápise
```

Prvý krok originálneho RNG počíta:

`S1=(1 * 0x343FD + 0x269EC3) mod 2^32 = 0x0029E2C0`

`R1=(S1>>16)&0x7FFF=41`, časovač `160+(41%240)=201`.

**Dôležitý detail zdrojového dôkazu:** pri treťom bode automatizovaný debugger zle spracoval ručne zadávaný príkaz `D 148F:38EE` a v logu uvádza `148F:03EE`. Záber preto **nepoužíva** nesprávny horný data-view na dokazovanie časovača. Príslušná *živá anotácia priamo pri inštrukcii `MOV [38EE],DX`* jednoznačne ukazuje `ds:[000038EE]=00C9`, a registre ukazujú `DX=00C9`. Táto limitácia je ponechaná v reporte, nič nie je domýšľané.

## DOS / Windows

Na DOS strane v25 potvrdila zásobníková stopa `1061:1D5B → RNG wrapper → RNG core` pri seede 1. Zodpovedajúci Windows callsite `3:BADD` je teraz **nielen staticky párovaný, ale aj vykonaný** s reálnym stavom pred/po a s uloženým intervalom 201. Strojové inštrukcie oboch binárok používajú rovnaké `IDIV 240` a `ADD 160`.

Oba testy používajú kompatibilné epizódové dáta; v26 Windows testovaný `MAP.1` sa od referenčnej DOS E1M1 líši **presne dvoma objektovými bajtmi**, ktoré pridávajú Skeleton `0x90` a Mrs. H. `0x94` (offsety `0x1CAB`, `0x1CAF`). Výsledok prvého EVENT RNG preto nemožno považovať za dôkaz simultánneho spoločného ticku. Predchádzajúci DOS test však ukázal rovnaký prvý stav aj bez tejto dvojice.

## Rozsah uzavretia

- **Uzavreté:** skutočný Windows RNG EVENT callsite, jeho návrat, zmena RNG stavu, výsledný `AX=41`, zápis EVENT interval 201.
- **Staticky podložené:** ekvivalentná aritmetika a volajúca EVENT rutina v DOS V2.0.
- **Otvorené:** úplná DOS entry/return dvojica z jedného behu, hranice tickov, prvých 16 súvislých RNG volaní, účinok rozdielu `EVENT→FLAGS` (DOS) verzus `FLAGS→EVENT` (Windows), všetky ďalšie RNG konzumenty.

## Reprodukcia

`python3 TOOLS/verify_v26.py --dos ORIGINAL_EXE/N3D-UNFU.exe --win ORIGINAL_EXE/NITE3W.EXE --observations RESULTS/runtime_observations.json`

Skript overí hlavičky MZ/NE, kódové bajty okolo volania, matematiku RNG a zaznamenané hodnoty. **Nečíta automaticky registre z obrázkov**; tie sú v `EVIDENCE/` uchované nezmenené a `runtime_observations.json` ich obsahuje ako transparentný prepis.

Na nové spustenie experimentu v pôvodnom Linux kontajneri slúži `TOOLS/v26_win16_live_probe.py` (vyžaduje existujúce Windows 3.11 / DOSBox-X / WinG laboratórium; obsahuje cesty použité v tomto prostredí). Pôvodné herné EXE sa nepatchuje.
