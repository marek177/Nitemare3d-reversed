# Nitemare 3D DOS v1.9: two table routines

Source: rozbalený `N3D-E-19.EXE`, 116 556 bytes, SHA-256 `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8`. Static check 16-bitového strojového code and krížová check exportom `N3D-E-18.EXE.c` (identical EXE zostava). Without runtime stopy.

## Confirmed

| Routine | Range v image / file | Behavior |
| --- | --- | --- |
| `1000:1126` | `0x1126–0x11BE` / `0x1326–0x13BE` | Cyklus `SI=0..255`: loads byte `DS:[SI+D30C]`, sets selected bits output byte and stores to `DS:[SI+D00A]`. `RETF` on `11BE`. |
| `1000:11C0` | `0x11C0–0x1261` / `0x13C0–0x1461` | Cyklus `SI=0..255`: loads `DS:[SI+D40C]`, sets selected bits and stores to `DS:[SI+D10A]`. `RETF` on `1261`. |

Each routine starts own `ENTER 2,0`, `PUSH SI` and ends own `POP SI`, `LEAVE`, `RETF`. Therefore exportované značky `FUN_1000_114b` and `FUN_1000_11c5` are internal branches/loop, **nie additional separate functions**. Výrezy instructions `0x1126–0x11BE` and `0x11C0–0x1261` have SHA-256 `4f50d9b41d2b67130ba85cc2995c18b402bc962428976358f2b507c24758c6f0` and `0e572adc607262d25fe3d8b5505e6ee75b38f3ae8131a86d7e5083d1d9ad66f2`.

### Bits first output (`1126`)

For input `x` are after priechode explicitne set: bit 0 = `(1<=x<=0x30) OR (0x31<=x<=0x40)`; bit 1 = `1<=x<=0x40`; bit 2 = `1<=x<=0x30`; bit 3 = `0x31<=x<=0x40`; bit 4 = `0x2E<=x<=0x2F`; bit 5 = 0; bit 6 = `0x47<=x<=0x48`. Bit 7 routine does not change and local byte `[BP-1]` before prvou iterate neinicializuje; its result value cannot z tohto code determine. This is important also for reprodukciu tables.

### Bits druhého output (`11C0`)

Bit 0 = `0x06<=x<=0x3D`; bit 1 = `0x08<=x<=0x2D`; bit 2 = `0x2F<=x<=0x3D`; bit 3 = `0x08<=x<=0x25`; bit 4 = 0; bit 5 = `x==0x2A`; bit 6 = `x==0x04`. Bit 7 remains z neinicializovaného local byte. Výrazy with XOR v dekompiláte correspond write one target bitu, what confirm instructions `SHL`, `AND`, `XOR` on `122A–124C`.

## Derived and unknown

Routines konštruujú 256-byte tables bit own z dvoch 256-byte input tabuliek. Exact meaning input ID, purpose individual bitov, initialize calls and behavior bitu 7 are so far unknown. Themselves prahy values nedokazujú, that is specific type walls or object.

Next test: nájsť all priame also indirect calls `1000:1126`/`1000:11C0`, identify source tabuliek `DS:D30C` and `DS:D40C`, and during behu record `[BP-1]` before element write plus output bytes for `x=0, 4, 0x2A, 0x2E, 0x30, 0x31, 0x40, 0x47`. Result určí purpose tabuliek and whether bit 7 actually depends from previous obsahu zásobníka.

**Pokrytie:** two verify function boundaries and their explicit bit condition; semantic names and runtime dosah remain open. This does not change verify overall function count DOS v1.9, which still was not určený.