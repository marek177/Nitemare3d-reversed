# Nitemare 3D — renderer v0.76: DOS2 IMG frame + shade XLAT + perspektívne U

**Dátum: 20. 10. 2026. Závažná hranica dôkazu:** samostatný C++20 code path pre 304 obrazových stĺpcov prešiel na Linuxe aj Windows, ale **pixel-perfect originál ↔ remake zostáva NEPREUKÁZANÝ**. `Raycaster.cpp` stále vykonáva iba diagnostické DDA.

## 1. Vytvorené moduly

- [`N3DDos20ShadeXLAT.hpp`](../src/re/N3DDos20ShadeXLAT.hpp) — port pôvodnej DOS 2.0 rutiny **0x16CE** s RGB6 Manhattan nearest-color a striktne prvým minimom.
- [`N3DDos20WallMaterialBinding.hpp`](../src/re/N3DDos20WallMaterialBinding.hpp) — stavový IMG wall-resource cache, SEQDEF/frame výber, čítač VEC +03/+04, byte layout `10 + width*height` a celočíselné perspektívne texture-U odvodené zo **Win16 1.10** `66B0 → EBD6 → 6422`.
- [`N3DDos20SpanWallPipeline.hpp`](../src/re/N3DDos20SpanWallPipeline.hpp) — rozšírený callback s **voliteľným siedmym argumentom**, skutočným `spanYQ4` pre konkrétny stĺpec. Staršie šesťargumentové syntetické material resolvery stále fungujú. 16.16 geometriu už netreba hádať zo screen X.
- [`N3DDos20IndexedWallColumn.hpp`](../src/re/N3DDos20IndexedWallColumn.hpp) — existujúci raster spracuje 304 pripravených origin-layout stĺpcov; 128×64 je stále dvojica plných 64×64 stien.

## 2. IMG wall sequence a frame výber

Overený statický layout originálneho IMG.N:

```text
0000..03FF  wall directory: 256 × UINT32 stream offset
0400..07FF  object directory: 256 × UINT32
0800..61FF  low/wall SEQDEF: 256 × 90 B
6200..BBFF  object/high SEQDEF
BC00..EOF   raw IMG frame streams

SEQDEF for wallId = 0x0800 + 90*wallId:
  +00 WORD frame interval
  +02 BYTE frame count
  +03 BYTE extended flag

Each frame = 10B header (width, height, ...) + width*height pixels
Frame pixels = column-major: at [u*height + v]
```

Cache je vytvorená v poradí originálnych 28B VEC, deduplikuje podľa **wall directory absolute stream offset**, nie podľa WallId. Kontroluje, že `VEC+04` predstavuje správnu cache indexovú položku. `VEC+03` vyberá frame, pri indexe mimo rozsahu sa vykreslí posledný frame (bez tichého fallbacku na prvú textúru). Samotný návrat však **nemaže/nemutuje** pôvodné `VEC+03`; jeho prípadnú DOS runtime vedľajšiu operáciu treba ešte zvlášť uzavrieť.

Test: wall ID 5 a 6 používajú rovnaký stream a rôzne animationFrame 0/1; wall ID 7 používa iný 128×64 stream. Nesprávny alias alebo selector po vytvorení catalogu končí fail-closed, nie textúrou náhodnej steny.

## 3. Originálne 16CE shade / DS globály

```text
shadeIndex = WORD DS:6278  (0..7)
paletteRgb6[768] = DS:4A64
shadeLevels[8] = [0,4,8,12,16,20,30,40]

for source=0..255:
    targetRGB6 = max(0, paletteRGB6[source] - shadeLevel)
    for candidate=0..255:
        distance = abs(Rd)+abs(Gd)+abs(Bd)
        if distance < previousMinimum: winner=candidate
    XLAT[source] = winner   # DS:D20C family
```

Pribudlo `shade::prepareFromDosSegment(ds, prepared)` a diagnostický `matchesStoredDosXlat(ds, prepared)`. Posledný test **nie je automatický dôkaz SS:BX = DS:D20C**: je platný len pri overenom segmentovom mapovaní. Statické testy používajú syntetické RGB6 palety, odlišujú RGB8 prepočítaný cez `>>2`, duplicitné RGB a shade0 neidentitu. Fade/DAC efekt sa **nemieša** s produkciou indexovaných pixelov.

### 3.1 Doslova DOS2: lokálna výnimka shade pre orientácie 0 a 1

Pri novej kontrole archivovaného Ghidra exportu originálnej DOS v2.0 rutiny `2500/25DC` sa našla konkrétna podmienka pred `1A2E`: **ak je globálna shade úroveň DS:6278 nenulová, `DS:430E == 0` a orientácia VEC patrí medzi 0/1, lokálny shade selector sa nastaví na 0**. Pre orientácie 2/3 sa ponechá pôvodný shade index. `DS:430E` označujeme iba ako opaque display/shading stav; jeho ostatné runtime účinky sa z tohto porovnania nedajú vyvodiť.

`MaterialBinder` teraz prijíma **active shade** a samostatne pripravený **shade-zero XLAT**, vyberie správnu tabuľku pre aktuálny VEC a výsledok bezpečne odovzdá stenovému rasteru. Ak by sa mala použiť shade-zero tabuľka a nie je dodaná, pripravovanie stĺpcov sa zastaví ako `InvalidWallMaterial` — žiadny nezdokumentovaný identity fallback. Test porovnáva ten istý IMG index 79 so shade4 (výsledok 11 v syntetickej RGB6 palete) a so shade0 (výsledok 79), aj odmietnutie chýbajúcej shade-zero tabuľky.

Táto výnimka je **konkrétna DOS statická sémantika**, nie dôkaz, že všetky možné runtime kombinácie globálneho stavu `430E` boli vykonané. Aplikuje sa na indexed wall XLAT, nie na DAC fade/palette-phase.

---

## 4. DOS-native perspektívne U: CEDC + caller 25DC + edge 22CA

Po dodatočnom statickom prečítaní originálneho dekompilovaného `FUN_1000_cedc` (`N3D-DOS-UNFULL-v20.exe.c`, rovnaká rodina DOS v2.0) a jeho volajúceho `25DC` pribudla samostatná **DOS-native** vetva `perspectiveUDosFromDS`.

Táto vetva **nepoužíva Win16 trig table ani odhad uhol→octant**, ale skutočné DOS renderer globály:

| DOS adresa | Čítaná hodnota |
|---|---|
| `DS:415C` | selector: nula → `sinQ10` deliteľ; nenula → `cosQ10` deliteľ |
| `DS:41B2` | `sinQ10` 16-bit signed |
| `DS:41B4` | `cosQ10` 16-bit signed |
| `DS:3686` | 32-bit vertical numerator |
| `DS:368A` | 32-bit inverse projection scale |
| `DS:4550` | center screen X |
| `DS:4162/4164` | hráčove world X/Y |

Matematika `CEDC` používa originálny `spanYQ4` (horné slovo 16.16 span fázy), orientáciu VEC a priečneho player-relative súčinu. Dve možnosti deliteľa a štyri kombinácie orientácie prepájajú `screenTerm = ((screenX-centerX)*inverseScale)/spanYQ4` s `verticalTerm = verticalNumerator/spanYQ4`. Volajúci `25DC` doplní 16-bit `local20`, inverziu podľa class/flags/orientácie a záverečnú korekciu DOS `22CA`. Pre `22CA` sa používa zrekonštruovaná Win16 `6422` vetvová rodina, ktorá má samostatné DOS statické potvrdenie.

**Nová predvolená voľba `MaterialBinder` je `DosNativeCedc22ca`.** Nevyžaduje Win16 `Trig360` ani hodnotu uhla z UI, pretože číta originálne DS Q10 a výpočtové konštanty. Pôvodná funkcia `perspectiveUCandidate` zostáva ako prepínateľná `Win16CrossBuildEbd6` kontrola. Na syntetických identických DS/trig vstupoch (0°/90°) dávajú obidve rovnaké U; zdrojové 128×64 dve plné steny sa nekomprimujú.

**Dôkazová hranica:** port je odvodený z pôvodného DOS C/dekompilácie a sémantiky 25DC, nie z kompletného inštrukčne presného CFG/trace výpisu 8086 pre každú možnú overflow a endian/alias vetvu. Matematika používa väčšie medzisúčiny tam, kde pôvodný build mohol mať 16/32-bit wrap. Ani DOS-native pomenovanie nie je oprávnenie tvrdiť pixel perfect bez priamo párovaného originálneho `U`/framebufferu.

### 4.1 Podmienka shade pri DOS orientácii

Lokálna podmienka `DS:6278 > 0 && DS:430E == 0 && VEC.orientation∈{0,1}` vyberá **shade 0** aj v prípade, že global shade má inú úroveň. Material binder má preto zvlášť `shading` a `shadingZero`, obidve z rovnakej base RGB6 palety. Chýbajúca shade-zero LUT, neplatná DS:6278 hodnota alebo shade tabuľka z predošlého ticku vedú k odmietnutiu stĺpca namiesto fallbacku. Pozorované správanie vychádza z pôvodnej DOS `25DC` dekompilácie; ďalšie účinky `DS:430E` ostávajú neznáme.

---

## 5. CI testy a reprodukcia

- [`tests/dos20_shade_xlat_test.cpp`](../tests/dos20_shade_xlat_test.cpp) — 8 shade indexov, nearest-color ties, neg-at-zero clamp, DS palette/shade/D20C diagnostika, integrácia s pixel writerom.
- [`tests/dos20_wall_material_binding_test.cpp`](../tests/dos20_wall_material_binding_test.cpp) — raw IMG 0xBC00 layout, alias dedup, frame clamp, 128×64 polovice, cardinal U, curtain flip, nulový deliteľ, 304 stĺpcov, shade z DOS DS, poškodené/stale selector prípady.
- CI pre shade: [renderer-v076-shade-xlat.yml](../.github/workflows/renderer-v076-shade-xlat.yml) — Windows + Linux C++20/CTest a Linux UBSan.
- CI pre binder: [renderer-v076-material-binding.yml](../.github/workflows/renderer-v076-material-binding.yml) — Windows + Linux C++20/CTest a Linux UBSan.

```bash
cmake -S . -B build-v076 -DN3D_ENABLE_SDL3=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build-v076 --config Debug --target n3d_dos20_shade_xlat_test n3d_dos20_wall_material_binding_test
ctest --test-dir build-v076 -C Debug -R 'n3d_dos20_(shade_xlat|wall_material_binding)_test' --output-on-failure
```

Testovacie IMG sekvencie a RGB6 palety sú generované v kóde testov; sú to **syntetické dôkazy**, nie skutočný framebuffer remaku proti pôvodnej hre. CI nerozbaľuje ani nedistribuuje komerčné originálne IMG, MAP, DEMO, EXE ani pamäťové dumpy.

## 6. Zostávajúce 1:1 brány

1. Inštrukčne dopresniť už portovaný DOS2 `25DC→CEDC→22CA→1A2E` reťazec vrátane 16/32-bit wrap, cardinal/nulových deliteľov a skutočného runtime poradia volaní; porovnať každé U s originálnym 8086 trace pri identickom stĺpci.
2. Overiť IMG cache stream/frame alias a štart frame cez originálne `IMG.1` + `DS:62AC` VEC snapshot; aktualizovať prípadné mutačné vedľajšie efekty frame clamp.
3. Na identickom hernom ticku vykonať originál vs port **VEC/OWNER/SPAN/FRAME/DAC** bránu [v0.72](../tools/n3d_v072_stage_frame_gate.py): `64 000` indexed8 a `768` DAC komponentov, nulová tolerancia.
4. Doplniť pohyblivé steny/dvere, originálne animácie (engine clock + zdieľaný RNG), sprite compositor a HUD, správny VGA page/palette event order.
5. **Kým všetko preukázane nesedí, hlavný herný `Raycaster.cpp` zostáva diagnostický DDA.** V0.76 implementuje prípravu wall materiálov, nie úplnú pixel-perfect hru.

Základné originálne dosiahnuté časti zostávajú ohraničené na predchádzajúci E1M1 checkpoint: 304 ownerov, 9×18B spanov a presný 42-pixelový scaled writer. Nová material-binding fáza bola testovaná iba so syntetickými IMG/DS dátami.