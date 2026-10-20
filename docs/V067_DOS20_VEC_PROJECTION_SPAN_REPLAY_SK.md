# Nitemare 3D — DOS v2.0 render VEC -> owner -> span, v0.67

**Dátum:** 2026-10-20 · **Úroveň dôkazu:** `ORIGINAL_RUNTIME_BOUNDED` (offline replay skutočného DOS2 snapshotu). **Pixel-perfect originál ↔ remake: OTVORENÉ.**

## Prelomový nález v staršom runtime archíve

Archív `N3D_DOS20_RENDER_SCALED_COLUMN_20261019.zip`, `proof/stack_segment.bin`, obsahuje autentický 65 536-B snapshot globálneho/stack segmentu pôvodnej hry DOS v2.0 počas originálneho škálovaného pixelového writeru. Pôvodný EXE packed SHA-256: `a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485`; samotný 64 KiB dump SHA-256: `1878c03fbd7f40d06dd87691e608d6143c16de0dcb347894d0e0bd6c2a49d98e`. **Nové spustenie DOSBox-X sa v tomto passe neuskutočnilo.**

Po dekódovaní pôvodných offsetov:

| Field | DOS2 offset/interpretácia | Namieraný stav |
|---|---|---|
| `DS:4162/+2` | hráč X, Y | `1440,3620` |
| `DS:41B2/+2` | smerové Q10 | `177,1008` |
| `DS:367E` | horizontálna projekčná konštanta | `178` |
| `DS:3686` | DWORD vertikálna projekčná konštanta | `81715200` |
| `DS:4550/+4` | obrazové centrum X, YQ4 | `160,1280` |
| `DS:4548/+2` | viewport `left,right` | `8,311` |
| `DS:4564` | 320 × WORD near owner | 304 nenulových položiek, 9 súvislých behov |
| `DS:4D64` | WORD počet spanov | `9` |
| `DS:4D6E` | 18 B span záznamy | presne `9×18=162 B` |
| VEC `+0C..+12` | svetové endpointy | 9 VEC |
| VEC `+14..+1A` | projektované `(X,YQ4)×2` | **36/36** presných slov |

### Projekcia CAB8, pozorovaný podpriestor

Pre world `(worldX,worldY)` a kameru `(playerX,playerY)` používame lokálne `dx = worldX - playerX`, `dy = playerY - worldY`. Pre zachytenú orientáciu:

```
depth    = dx * 177 + dy * 1008
lateral  = dx * 1008 - dy * 177
screenX  = 160 + trunc_toward_zero(lateral * 178 / depth)
screenYQ4 = 1280 + trunc_toward_zero(81715200 / depth)
```

Z 18 world endpointov sa zhodovalo všetkých **36 projektovaných WORD hodnôt**. Dva VEC sa museli otočiť podľa `screenX`, pretože pôvodný binary triedi endpointy vzostupne. Jeden endpoint je za near plane a používa `depth=0x4000`; pri vertikálnej stene zostane X nemenné, ale korekcia Y vychádza z celočíselnej rovnice pre near depth. Jej výsledný pixelový endpoint `(491,6267)` sa zhoduje byte-exact so snapshotom. Iné near-plane vetvy, cardinal headings, pretečenia a clippingy zostávajú otvorené.

### Owner -> 18B span -> interpolácia 202A/213E

9 neprerušených owner behov v `DS:4564`, projekčné endpointy a horizont `1280` reprodukujú presne všetkých **162/162 originálnych bajtov** na `DS:4D6E`. Originálny hash 162 bajtov aj nezávisle prerátaný hash:

`cbf157a07ce343dc9da1fa501fdac40e8338d6d9bd3d65d786e60c4c8edb88cd`

Každý 18B DOS span má v tomto stave pozorované polia: `+00 pointer WORD`, `+02 firstX`, `+04 firstY`, `+06 lastX`, `+08 lastY`, `+0A signed slope32 (16.16)`, `+0E phase32 (16.16)`. Pozorovaný `slope = trunc_toward_zero((y2-y1)*65536/(x2-x1))`. 9/9 sklonov aj obidva projektované koncové Y sa zhodujú s originálom.

**Nový edge-case:** keď prvý span začína na ľavej hranici `x=8` a jeho VEC má premietnutý začiatok `x=-18`, počiatočný phase akumulátor používa **jeden dodatočný slope krok**: originál `0x014B800F` namiesto priamo interpolovaného `0x014E38F2`. Pri ostatných ôsmich VEC tento posun nie je; najmä VEC s `x0=-44`, no `spanFirst=41`, ho nedostáva. Podmienka `spanFirst == viewportLeft && vecScreenX1 < viewportLeft` reprodukuje pozorovaný záznam. **Je to hypotéza generalizácie z jediného stavu, nie univerzálne uzavretá vetva.**

## Nový kód a testy

- `Dos20VecProjectionEvidence.hpp` — integer kamera/projekcia, jeden overený near clip, endpoint swap; odmietne neoverené vetvy.
- `Dos20OwnerSpanEvidence.hpp` — 16-bit near owner, 18-bajtový DOS span, presný 16.16 phase/model, odmieta owner diery a limit 50 bez runtime dôkazu.
- `n3d_dos20_owner_span_oracle.py` — nezávislá Python stdlib rekonštrukcia pôvodného 64KiB segmentu; nevkladá hru alebo pamäťový dump do repozitára.
- `dos20_vec_projection_evidence_test.cpp`, `dos20_owner_span_evidence_test.cpp` — samostatné C++20 regresné testy, voliteľne priamo proti pôvodnému snapshotu.
- `test_n3d_dos20_owner_span_oracle.py` — 8 self-contained syntetických unittestov vrátane poškodenej projekcie, owner diera, IDIV truncation, chybná medza a poškodené SPAN.

**Overenie:** kompilácia dvoch C++ testov GCC 13/C++20; oba úspešné s autentickým 64 KiB segmentom; oba úspešné UBSan; Python 8/8; plné CMake Debug `N3D_ENABLE_SDL3=OFF` build a CTest **77/77 PASS**. Mnohé ostatné testy sú syntetické a nepokrývajú herné scény. Produktívny renderer (`src/renderer/Raycaster.cpp`) bol ponechaný nezmenený ako explicitný diagnostický DDA preview.

### Reprodukcia

```bash
python3 tools/n3d_dos20_owner_span_oracle.py \
  --archive /path/to/N3D_DOS20_RENDER_SCALED_COLUMN_20261019.zip \
  --out original_v067_dos20_replay.json
python3 -m unittest discover -s tests -p test_n3d_dos20_owner_span_oracle.py -v
cmake -S . -B build-v067 -DCMAKE_BUILD_TYPE=Debug -DN3D_ENABLE_SDL3=OFF
cmake --build build-v067 --parallel 4
ctest --test-dir build-v067 --output-on-failure
```

## Zostávajúce brány do 1:1

1. Vygenerovať DOS2 28B VEC priamo z MAP a overiť ich proti ďalšiemu originálnemu checkpointu (tento dôkaz začína *už vytvorenými* VEC).
2. Presne reprodukovať konfliktný DOS2 výber ownerov a traversal z originálneho VEC listu (teraz berieme *originálny* owner buffer zo snapshotu).
3. Dopárovať DOS2 perspective U, clipped vertical V, image sequence, shade a wall pixel writers ku každému z deviatich spanov.
4. Rovnaký deterministický herný tick, kamera, map/EXE/IMG/PAL SHA; prvý **originál ↔ remake** framebuffer 64 000 indexed + 768 DAC **zero-diff**. Potom sprite/HUD/page flips a ďalšie levely.

Bez týchto bodov je označenie *pixel-perfect 1:1* nepravdivé. V0.67 zmenšuje geometrickú neistotu pre jeden pôvodný E1M1 render frame; nie je hotový renderer.