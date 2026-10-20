# DOS v2.0 renderer: originálny VGA → RGB cache oracle (2026-10-20)

**Status: ORIGINAL_RUNTIME_BOUNDED / NOT remake pixel-perfect parity.**

## Overený výsledok

Nezávislý offline replay dvoch **už existujúcich originálnych DOS v2.0 runtime archívov** vytvoril doslovne rovnaké bajty emulátorového RGB cache:

| Pôvodný zdroj | Párové cache obrazy 320×400 | Porovnané RGB pixely | Chybné RGB komponenty |
|---|---:|---:|---:|
| UIF Please Wait fade-in | 21 | 2,688,000 | 0 |
| E1M1 | 17 | 2,176,000 | 0 |
| DEMO | 3 | 384,000 | 0 |
| **Spolu** | **41** | **5,248,000** | **0 / 15,744,000** |

Tá istá pôvodná scéna môže byť zachytená opakovane; 41 obrazov **nie je 41 nezávislých herných tickov**.

Dodatočne: originálna Main Menu (UIF záznam 6) / Please Wait (UIF záznam 4) stránka má každá presnú zhodu **64,000/64,000 indexov** s pôvodným PNG8 referenčným decode a **768/768 6-bit DAC** komponentov. Počas 21 archivovaných fade-in RGB cache frame je pôvodný 2 MiB VRAM snapshot nemenný. Existuje 23 DAC uploadov, ale len 21 párových RGB cache capture; chýbajúce obrazy sa nepredstierajú.

## Dokázaný display model tejto DOSBox-X reprezentácie

- VGA VRAM: 2,097,152 bajtov (emulátorové interleaved planes).
- Index `pixel(x,y)` z `vram[0x10000*page + 4*(80*y + (x>>2)) + (x&3)]`. Page 0 = A000, page 1 = A400. Hodnoty CRTC start/line compare z iných tickov sa nesmú považovať za ľubovoľný page selector.
- RGB 6→8 bit: **`(component << 2) | (component >> 4)`**, nie iba `component*4`.
- 320×200 indexované dáta → presne 320×400 RGB24, každý riadok dvakrát. Syntetická validácia zahŕňa 4-pass negative tests.
- Toto je **original VRAM+DAC ↔ original RGB cache** kontrola. Nie je to porovnanie originálu s portom.

## Reprodukovateľnosť

Originálne archívy **neobsahuje tento repozitár**; osobné dôkazy používateľa:

- `N3D_DOS20_RENDER_UIF_PAGEFLIP_FADEIN_20261019.zip`, SHA-256 `b2d7f144e3740b0c825e5ce0435a6a6afdcc873a178003e0dd24207d64d126ad`
- `N3D_DOS20_RENDER_RUNTIME_20261019.zip`, SHA-256 `26995d0ebf2e5e0bde8561b85d85ad6174278a2237b3c202c63444eec49f2207`

Standalone overovač **jedného originálneho checkpointu** je `tools/n3d_dos20_indexed_oracle.py`. Vstup je úplný 2 MiB VRAM snapshot, 768 B DAC a párový 320×400 RGB24 PPM:

```bash
python3 tools/n3d_dos20_indexed_oracle.py \
  --vram vga-000001.vram \
  --dac vga-000001.pal \
  --cache-ppm rgb-000012.ppm \
  --page 1
python3 -m unittest discover -s tests -p test_n3d_dos20_indexed_oracle.py
```

Test má 4 prípady, používa iba Python stdlib a nemá copyrightované herné assety. Pokiaľ je Python 3 dostupný, CTest zaregistruje `n3d_dos20_indexed_oracle_py`. Kompletný nezávislý 41-frame replay a 13 syntetických prípadov sú súčasťou externého experimentálneho v0.66 dôkazového balíka (nie produkčného `main`).

## Čo zostáva otvorené

**Zero-diff originál ↔ remake** ešte neexistuje. DOS V2.0 projekcia, VEC owner traversal, edge clipping, perspektívne wall-U/V, shade LUT, dynamické steny, sprite compositor, párovanie identických herných tickov, RGB DAC a framebuffer page pri jednotlivých replay stavoch zostávajú produkčnými parity bránami. Win16 sémantické porty `E798`, `EBD6`, `3940` nie sú dôkazom DOS identity bez cross-build overenia.

Aktívny `src/renderer/Raycaster.cpp` zostáva iba **diagnostický DDA preview**. Na originálny VEC renderer sa má prepnúť až po overení opakovateľného korpusu `64,000 indexed + 768 DAC` bajtov s nulovou toleranciou.
