# Nitemare 3D DOS v2.0 — Renderer 1:1, pass v0.70

**Dátum:** 20. 10. 2026. **Dôkaz:** `ORIGINAL_RUNTIME_BOUNDED` + CPU opcode coverage originálneho DOS v2.0 z predtým zachytených archívov. **Nie je to nový beh emulátora ani dôkaz 1:1 pixelového framebufferu medzi originálom a portom.**

## 1. Zásadný nový nález — úplný pôvodný DOS FEFA

Z archívu `N3D_DOS20_RENDER_RUNTIME_20261019.zip` (13 `.n3dt` stôp, **14 102 829** udalostí typu `I`) som zrekonštruoval sémantiku originálnej DOS funkcie `0xFEFA..0x1003D`, nie Win16 nahrážku. Celých **324/324 strojových bajtov** sú pozorované, 0 konfliktných opcode bajtov. Odlišných vykonaných opcode-adresných štartov bolo **128**, vykonaných inštrukcií v tomto rozsahu **315 257**. Úplný obraz kódu má SHA-256 `96cbfb9580f39715ff74f6b991f8645efd40e1c5771da55ec5a05ff97ef6ca12`. *Zdrojové binárne bajty ani disassembláciu hry nedistribuujem; SHA a výsledný sémantický model sú reprodukovateľné vstupným archívom.*

Presná DOS FEFA sémantika (stará orientácia → nová orientácia; všetky porovnania striktne `>`/`<`; starší owner ostáva pri rovnosti):

| Starý → nový | Nahradiť, keď... |
|---|---|
| 0 → 2 | `new.x0 > old.x0 && new.y0 < old.y0` |
| 0 → 3 | `new.x1 < old.x1 && new.y0 < old.y0` |
| 1 → 2 | `new.x0 > old.x0 && new.y1 > old.y1` |
| 1 → 3 | `new.x1 < old.x1 && new.y1 > old.y1` |
| 2 → 0 | `new.x1 > old.x1 && new.y1 < old.y1` |
| 2 → 1 | `new.x1 > old.x1 && new.y0 > old.y0` |
| 3 → 0 | `new.x0 < old.x0 && new.y1 < old.y1` |
| 3 → 1 | `new.x0 < old.x0 && new.y0 > old.y0` |

Ostatných 8 orientačných párov vrátane rovnakej orientácie vlastníka nemení. `VEC+05 & 1` je vstupný gate; ak je nastavený, volá sa projekcia `CAB8`. Neobsadený stĺpec sa pridelí novému VEC a zníži sa zostávajúci počet. Poradie traversal zostáva významné.

Dynamické trace vykonali **7 z 8 vetiev orientačného konfliktu**. Vetva `old 0 → new 2` má rekonštruované strojové bajty a syntetické testy, no v sledovaných behoch nebola pozorovaná ako vykonaná. **Úplná opcode znalosť nie je to isté ako úplné runtime pokrytie.**

## 2. Oba pôvodné „nesprávne projekčné výsledky“ — CAB8 skorý návrat

V originálnom kóde `CAB8` pred výpočtom horizontalnej projekcie zapisuje `VEC+16` a `VEC+1A` (YQ4). Potom na `CBEB..CBF2` porovná, či **obe Y hodnoty prevyšujú** `(DS:454E + 0xB4) << 4`. V našom originálnom 64KiB E1M1 checkpointe je `DS:454E=155`, preto limit **5360**.

| VEC | Nové YQ4 vypočítané modelom | Originálne uložené YQ4 | Early return | X writer |
|---|---|---|---|---|
| `0x8A28` | `5514,6267` | `5514,6267` | áno | nevykonaný |
| `0x9A90` | `6267,6267` | `6267,6267` | áno | nevykonaný |

Pôvodné X v checkpointe (`-908/-374`, respektíve `0/0`) **nie sú dôkazom novo prepočítanej horizontalnej projekcie**; táto vetva ich vôbec nezapisuje. Model ich nesmie nahrádzať odhadnutými X, ani umelo opravovať per-VEC hodnoty. Overený CPU trace má pre konkrétne porovnanie pri `0xCBF2` **437 skokov na `0xCED6`** (predčasný návrat) a **89 pokračovaní `0xCBF6`**.

Tým v ohraničenom checkpointe `72` navštívených VEC dostávame:

- **70 presných plných projekcií** zo svetovej geometrie;
- **2 správne klasifikované skoré cull vetvy, 4/4 presné Y WORDy**;
- **304/304 presných 16-bit ownerov**, bez hardcoded opráv `x=18/40/175/269`;
- **162/162 bajtov 9 DOS spanov** presných.

## 3. Zostávajúce DOS opcode medzery

| Orig. rozsah | Bajtové pokrytie | Otvorený rozsah/podmienka |
|---|---:|---|
| `0xFEFA..0x1003D` | **324/324** | žiadny chýbajúci opcode bajt; runtime vetva 0→2 nepozorovaná |
| `0xCAB8..0xCEDB` | **1009/1060** | `0xCD9D..0xCDCF` (51 bajtov), zriedkavý/cardinal clip path |
| `0x1021E..0x104BD` | **656/672** | 4×4B pozície `10408..0B`, `1043D..40`, `10472..75`, `104A6..A9` |

Na začiatku `1021E` existujú **11 byte pozícií s nulovým alternatívnym pre-state obsahom v troch oknách**. Počas tejto analýzy ich nepovažujem za dokázanú samomodifikáciu ani za legitímnu náhradnú opcode cestu. Kontrola patrí do budúceho runtime passu.

## 4. Implementácia a testy

- `src/re/N3DDos20VisibilityOpcodeContract.hpp`: originálny DOS2 FEFA 8-párový model, aktívny flag, CAB8 vertical-cull vstupný kontrakt;
- `src/re/Dos20VisibilityReplayV070.hpp`: opravený experimentálny 72-VEC forward replay (DOS owner matrix, CAB8 early-cull), bez pripojenia do živej hry;
- `tools/n3d_v070_dos_trace_opcode_census.py`: nový bezpečný originálny trace census; vypíše iba pokrytie, SHA a počty vetiev, **nie originálne opcode bajty**;
- `tools/n3d_v070_cab8_cull_oracle.py`: SHA-gated original memory vertical-cull oracle;
- `tools/n3d_dos20_visibility_oracle_v070.py`: opravený Python dopredný replay;
- `tests`: C++ syntetické matice (320 000 kombinácií), originálny 64KiB checkpoint, mutačné regresie a formátové testy.

**Overenie lokálne:** C++20 `-Wall -Wextra -Werror -pedantic` a UBSan (oba moduly) PASS, Python unittest **27/27** s pôvodnými používateľskými vstupmi, archived local CMake/CTest **84/84 PASS** (s experimentálnymi v0.65–v0.70). Lokálna checkout báza je staršia než aktuálny GitHub main, preto toto číslo nie je dôkazom úplného CI na aktuálnom head-e. SHA256 `Raycaster.cpp` a `main.cpp` sa integráciou nezmenili.

## 5. Reprodukcia na používateľových pôvodných dátach

```bash
python3 tools/n3d_v070_dos_trace_opcode_census.py \
  --trace-zip /local/N3D_DOS20_RENDER_RUNTIME_20261019.zip \
  --output /tmp/v070_opcode_census.json
python3 tools/n3d_v070_cab8_cull_oracle.py \
  --snapshot /local/stack_segment.bin \
  --output /tmp/v070_cab8_cull.json
python3 tools/n3d_dos20_visibility_oracle_v070.py \
  --archive /local/N3D_DOS20_RENDER_SCALED_COLUMN_20261019.zip
```

**Nezahrnuté v balíku:** pôvodná hra, memory dump, originálne runtime trace, textúry IMG/MAP/EXE, celý doslovný asm. Výstupný balík obsahuje len vlastný analytický kód, testy a odvodené výsledky.

## 6. Ďalší 1:1 cieľ

Staticky uzavrieť 51B CAB8 cardinal vetvu a 16B 1021E continuation, potom otestovať v ďalších kamere/úrovniach, regenerovať 592 world VEC zo zhodného MAP, doplniť DOS wall `U/V`, shading, dynamické steny/sprite/HUD a urobiť **rovnaký originálny vs port framebuffer**: 64 000 indexov a 768 DAC komponentov s nulovým rozdielom. **Zmena produkčného DDA je zatiaľ predčasná.**
