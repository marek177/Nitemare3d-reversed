# Nitemare 3D — renderer research v0.74: reálny DOS2 16.16 wall-column backend

**20. októbra 2026. Dôkazový stupeň: ORIGINAL_RUNTIME_BOUNDED (starý originálny trace) + NOVÝ TESTOVANÝ C++ PORT, nie celohrová pixelová parita.**

## Výsledok v kóde

Pridané [`src/re/N3DDos20IndexedWallColumn.hpp`](../src/re/N3DDos20IndexedWallColumn.hpp). Je to samostatná C++20 implementácia **už vybraného** 64-texelového stenového stĺpca, nie klasický DDA raycaster a ani náhrada hotového projektu.

Podporované časti:

- plnohodnotné 320×200 **indexed8** obrazové dáta a 2 MiB **interleaved VGA** snapshot v štýle dodaného DOSBox-X;
- deterministické **16.16** vzorkovanie zdrojového stĺpca, celočíselná frakcia/inkrement bez `double`;
- voliteľná **256-bajtová XLAT** prevodná tabuľka vstupných farebných indexov, napr. originálny `SS:BX=D20C` (žiadny automaticky vymyslený shade);
- rozlíšenie stránky `A000` (0) / `A400` (1) a správnej VGA roviny z `screenX & 3`;
- zdrojové IMG pixely v **column-major**: 64×64 a 128×64, pričom 128×64 obsahuje dve samostatné plné 64×64 steny; fyzická súradnica U sa zadáva explicitne;
- stena nemá transparentný `0x1F` (tento index je špecifický pre DOS sprite raster);
- pred vykreslením sa validuje celý rozsah vzoriek a cieľových pixelov, takže neplatný vstup nezanechá čiastočne prekreslenú snímku.

**Originálny ukotvený test:** DOS v2.0 writer `097A:0599..05D5`, šírka jedného logického stĺpca, `x=8`, `y=59..100`, `CX=42`, `step=0x00018F9C`, index na začiatku `149→139`, na konci `143→134`, VGA plane 0. Tieto koncové hodnoty boli zaznamenané v predchádzajúcom originálnom runtime dôkaze. Nový test používa **syntetické medzivzorky**; nesmie sa prezentovať ako čerstvý replay autentických DS/SS/VRAM dumpov.

## Zapisovacia adresa a prenos do moderného framebufferu

```text
original VGA aperture: DI = 80*y + floor(x/4)
DOSBox-X interleaved snapshot: offset = (page * 0x10000) + 4*DI + (x & 3)
modern indexed8 framebuffer: offset = 320*y + x
color output: (XLAT == null) ? source : XLAT[source]
texel cursor: uint32 source16_16 += uint32 step16_16 (wrapping 32-bit)
```

Neodvodzuje sa orientácia steny z DDA a program nemení `Raycaster.cpp` ani `src/main.cpp`. Volajúci musí najskôr presne dopočítať **VEC owner → span → wall-U → source frame → 16.16 V sampling → shade LUT**.

## Regresné testy

Nový [`tests/dos20_indexed_wall_column_test.cpp`](../tests/dos20_indexed_wall_column_test.cpp) overuje 42 jednotlivých zápisov, prvý a posledný originálny známy XLAT preklad, presné planar interleaved adresy, rozdiel oboch VGA stránok, dve plné 64×64 polovice 128×64 IMG, zapisovanie indexu `0x1F` do steny a odmietnutie chybných vstupov bez poškodenia výsledného framebufferu.

```bash
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug --target n3d_dos20_indexed_wall_column_test
ctest --test-dir build -C Debug -R '^n3d_dos20_indexed_wall_column_test$' --output-on-failure
```

GitHub Actions workflow [`renderer-v074-indexed-wall-column.yml`](../.github/workflows/renderer-v074-indexed-wall-column.yml) kompiluje a spúšťa tento test na Linuxe aj Windows. **Testy nepotrebujú pôvodný komerčný EXE, MAP, IMG ani RAM dump.** Úspešný CTest preukazuje konzistentnosť implementovaného zúženého kontraktu, nie 1:1 celého renderera.

## Čo je naďalej otvorené

1. Získanie autentických originálnych a kandidátnych snímok pri **tom istom ticku a rovnakom EXE/MAP/IMG/PAL variante**.
2. Dokončenie plnej DOS v2.0 cesty `MAP → 28B VEC → owner → 18B spans → exact wall-U` a originálneho výberu IMG sekvencie/animácie.
3. Prepojenie správnej **16.16 vertical source** a DOS shading tabuľky s týmto novým stĺpcovým consumerom pre všetkých 304 screen x.
4. Presný sprite queue/raster, dynamické steny/dvere, HUD, page flip a 6-bit DAC časovanie.
5. **Zero-diff 64 000 indexed bajtov + 768 DAC bajtov**, opakovane na viacerých stavoch. Kým toto nebude preukázané, nový raster je experimentálny a DDA iba diagnostické.

Bez novej autenticity a viacstupňového diff sa nesmie zvyšovať označenie `PIXEL 100%`.
