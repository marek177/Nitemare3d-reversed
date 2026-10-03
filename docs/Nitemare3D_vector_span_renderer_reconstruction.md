# Nitemare 3D – rekonštrukcia Win16 vektorového/span rendereru a DOS porovnanie

Stav analýzy: 2026-09-23  
Primárny zdroj: Win16 `nite3w110.exe.c`; DOS porovnanie: `N3D-DOS-UNFULL-v20.exe.c`  
Rozsah: tvorba stenových vektorov, perspektívna projekcia, stĺpcová viditeľnosť a tvorba spanov

## Záver

Renderer nepoužíva klasický pixelový raycaster typu Wolfenstein 3D. Mapa sa najprv prevedie na osovo orientované stenové vektory. Tie sa zoradia podľa štyroch svetových orientácií, perspektívne premietnu a vložia do 320-prvkového stĺpcového owner buffera. Súvislé stĺpce patriace rovnakému vektoru sa potom komprimujú na najviac 50 spanov. Pre každý span sa vypočíta 16.16 interpolácia vertikálnej projekčnej hodnoty.

Ide teda o hybridný **vector/span renderer s raycastingovým princípom viditeľnosti po obrazovkových stĺpcoch**.

## Rekonštruovaná pipeline

1. `FUN_1018_4046` prechádza 64×64 mapu v štyroch smeroch.
2. `FUN_1018_3e82`/`FUN_1018_3d54` vytvárajú 28-bajtové stenové vektory.
3. `FUN_1018_4006` spája susedné kompatibilné hrany predĺžením konca o 64 svetových jednotiek.
4. `FUN_1018_3430` rozdelí vektory podľa orientácie 0–3 do štyroch zoznamov (limit 333 na zoznam) a zoradí ich.
5. `FUN_1010_e798` vykoná transformáciu vzhľadom na kameru, near-plane clipping a perspektívnu projekciu koncových bodov.
6. `FUN_1018_3564` rasterizuje horizontálny rozsah každého vektora do 320-prvkového owner buffera `0x53FE`; pri konflikte vyberá bližšiu stenu geometrickým porovnaním.
7. `FUN_1018_3940` spracúva zoradené zoznamy dovtedy, kým sú pokryté všetky požadované stĺpce, a potom doplní kandidátov pri hraniciach viditeľného svetového rozsahu.
8. `FUN_1010_6266` zbehne owner buffer a súvislé behy rovnakého vektora skomprimuje na spany (limit 50).
9. `FUN_1010_6152` pre každý span pripraví lineárnu 16.16 interpoláciu vertikálnej projekcie.

## Štruktúra stenového vektora (28 bajtov)

| Offset | Typ | Význam | Istota |
|---:|---|---|---:|
| `+00` | `uint8` | ID/typ mapovej hrany | vysoká |
| `+01` | `int8` | posun variantu textúry/snímky | stredná |
| `+02` | `uint8` | runtime stav | nižšia |
| `+03` | `uint8` | runtime stav/aktivácia | stredná |
| `+04` | `uint8` | objektový alebo obrazový index používaný neskôr | stredná |
| `+05` | `uint8` | príznaky; bit 0 = aktívny/renderovateľný, bit 3 = špeciálna hrana | vysoká |
| `+06` | `uint8` | odvodená trieda steny/obrazu | vysoká |
| `+07` | `uint8` | orientácia steny `0..3` | veľmi vysoká |
| `+08..0B` | 4 B | nulované pracovné polia | stredná |
| `+0C` | `int16` | svetové X začiatku | veľmi vysoká |
| `+0E` | `int16` | svetové Y začiatku | veľmi vysoká |
| `+10` | `int16` | svetové X konca | veľmi vysoká |
| `+12` | `int16` | svetové Y konca | veľmi vysoká |
| `+14` | `int16` | obrazovkové X ľavého premietnutého konca | veľmi vysoká |
| `+16` | `int16` | vertikálna projekčná hodnota ľavého konca | vysoká |
| `+18` | `int16` | obrazovkové X pravého premietnutého konca | veľmi vysoká |
| `+1A` | `int16` | vertikálna projekčná hodnota pravého konca | vysoká |

Poznámka: projekcia môže prehodiť oba konce, aby platilo `screenXLeft <= screenXRight`; spolu s X sa prehodia aj hodnoty na `+16/+1A`.

## Štruktúra viditeľného spanu (20 bajtov)

| Offset | Typ | Význam | Istota |
|---:|---|---|---:|
| `+00` | `uint16` | offset far pointera na stenový vektor | veľmi vysoká |
| `+02` | `uint16` | segment far pointera na stenový vektor | veľmi vysoká |
| `+04` | `int16` | prvý obrazovkový stĺpec | veľmi vysoká |
| `+06` | `int16` | interpolovaná vertikálna hodnota v prvom stĺpci | vysoká |
| `+08` | `int16` | posledný obrazovkový stĺpec | veľmi vysoká |
| `+0A` | `int16` | interpolovaná vertikálna hodnota v poslednom stĺpci | vysoká |
| `+0C` | `int32` | krok interpolácie vo formáte 16.16 | veľmi vysoká |
| `+10` | `uint16` | počiatočná zlomková časť 16.16 akumulátora | vysoká |
| `+12` | `int16` | počiatočná celá časť vzhľadom na horizont `DAT_1048_53F0` | vysoká |

## Pseudokód projekcie

```c
bool project_vector(Vector28 *v) {
    // svetové body sa prevedú do súradníc kamery pomocou dvoch
    // trigonometrických koeficientov DAT_1048_4C46/4C48
    depth0 = camera_transform(v->x0, v->y0);
    depth1 = camera_transform(v->x1, v->y1);

    // minimálna hĺbka 0x4000; pri prieniku sa koniec oreže na near plane
    clip_to_near_plane(&endpoint0, &depth0, 0x4000);
    clip_to_near_plane(&endpoint1, &depth1, 0x4000);

    sx0 = centerX + horizontalScale * lateral0 / depth0;
    sx1 = centerX + horizontalScale * lateral1 / depth1;
    py0 = horizonY + verticalScale / depth0;
    py1 = horizonY + verticalScale / depth1;

    if (sx1 < sx0) swap_endpoints();
    v->screenLeft = sx0;  v->projLeft = py0;
    v->screenRight = sx1; v->projRight = py1;
    return overlaps_viewport(v->screenLeft, v->screenRight);
}
```

## Pseudokód stĺpcovej viditeľnosti

```c
clear(columnOwner[first..last]);
remainingColumns = viewportWidth;

for (vector in orientation_sorted_front_candidates) {
    if (!(vector->flags & ACTIVE) || !project_vector(vector))
        continue;

    x0 = max(vector->screenLeft, viewportLeft);
    x1 = min(vector->screenRight, viewportRight);
    for (x = x0; x <= x1; ++x) {
        if (columnOwner[x] == NULL) {
            columnOwner[x] = vector;
            --remainingColumns;
        } else if (vector_is_in_front_at_intersection(vector,
                                                       columnOwner[x])) {
            columnOwner[x] = vector;
        }
    }
    if (remainingColumns == 0)
        break;
}
```

Konfliktný test v `FUN_1018_3564` nepočíta všeobecný Z-buffer. Využíva fakt, že všetky steny sú osovo orientované, a podľa dvojice orientácií porovnáva ich konštantnú X/Y súradnicu a rozsah druhého vektora. To je lacnejší ekvivalent výberu najbližšej steny pre daný obrazovkový lúč.

## Pseudokód tvorby spanov

```c
for each maximal run [x0..x1] with identical columnOwner[x] {
    Vector28 *v = columnOwner[x0];
    Span20 *s = next_span();
    s->vector = v;
    s->firstX = x0;
    s->lastX = x1;

    dx = v->screenRight - v->screenLeft;
    dy = v->projRight - v->projLeft;
    s->step16_16 = dx ? ((int32_t)dy << 16) / dx : 0;
    s->firstProjected = v->projLeft + dy * (x0-v->screenLeft) / dx;
    s->lastProjected  = v->projLeft + dy * (x1-v->screenLeft) / dx;
    s->fraction = low16((x0-v->screenLeft) * s->step16_16);
    s->integer = high16((x0-v->screenLeft) * s->step16_16)
                 + v->projLeft - horizonY;
}
```

## Statické overenie

Nasledujúce nezávislé znaky sa navzájom zhodujú:

- každý vektor má presne `0x1C` (28) bajtov;
- generátor používa dlaždicu veľkosti 64 a koncové body sú násobky 64 alebo stred dlaždice (`+32`);
- spájanie kompatibilných vektorov predlžuje presne jednu os o 64;
- štyri orientačné zoznamy korešpondujú so štyrmi smermi hrany;
- projektor zapisuje páry `(+14,+16)` a `(+18,+1A)` a pri obrátenom X ich prehodí spolu;
- owner buffer používa 4-bajtový far pointer na každý stĺpec;
- adresovanie `x*4 + 0x53FE` a obrazový rozsah 320 stĺpcov dávajú 1280-bajtový buffer;
- span builder porovnáva oba 16-bitové diely far pointera, takže behy patria skutočne rovnakému vektoru;
- interpolátor používa `(dy << 16) / dx`, čo jednoznačne potvrdzuje signed 16.16 krok;
- limity v programe sú 1000 vektorov, 333 položiek v orientačnom zozname a 50 viditeľných spanov.

## Audit pixelovej cesty (23. 9. 2026)

Stenový pixelový zapisovač už nie je neznámy. `FUN_1010_66b0` vyberá sequence/frame, pre každý spanový stĺpec počíta U cez `FUN_1010_ebd6` a okrajovú korekciu `FUN_1010_6422`, zapisuje per-column wall visibility hodnotu a volá `FUN_1010_3e44`. Ten vyberá lineárnu WinG cestu `FUN_1010_366a` alebo planar VGA cestu.

- Textúrový stĺpec začína na `frame_base + U * 0x40`; priľahlé textúrové stĺpce sú vzdialené 64 bajtov.
- Tabuľkové dvojice na offsetoch `0x247E/0x2480` riadia vertikálny zdrojový krok cez 16-bitový zlomkový akumulátor. Orezanie inicializuje textúrový offset a zlomkovú časť cez `0x2C7F/0x2E7E`.
- Lineárny cieľ používa adresu `y * 0x140 + x` a krok `0x140` na scanline; planar VGA cesta používa `page * 0x10 + y * 0x50 + x/4` a sequencer `0x3C4/0x3C5`.
- Shade 0 zapisuje pôvodný texel; iné hodnoty používajú `DAT_1048_8094[texel]`. Stenový pixel loop kopíruje každý vzorkovaný texel; nenašiel sa v ňom transparent-key test.

### Sprite priehľadnosť a wall occlusion

Win16 `FUN_1010_6348 → FUN_1010_cc7c → FUN_1010_6914 → FUN_1010_3f80` vyberá, premieta, slotuje a kreslí spritey. Sloty sú 18-bajtové záznamy od `0x6270`, kresliaci cyklus prechádza 100 slotov. Sprite pixel s indexom `0x29` (`')'`) sa preskočí. Každý sprite stĺpec číta wall visibility hodnotu z `0x58FE`; VEC flag `+05 bit 0x10` tento test obíde. Sprite zapisovač nový visibility/depth údaj neukladá, preto sa prekrytie sprite–sprite riadi slotovým poradím, nie vlastným Z-bufferom.

### Oprava mapových tried

V dodaných `MAP.1–3` sa triedy stien `0x3D/0x3E` nevyskytujú v wall-ID lookup tabuľke. Aktívne závesové triedy v dodaných mapách sú `0x3F/0x40`: `MAP.1` používa wall ID `0x70/0x72/0x74` a `0x71/0x73/0x75`; `MAP.2` používa `0xAA/0xAB`. Riadky `WALLS.1/.2` ich pomenúvajú `DOORVC`/`DOORHC`, „curtain“. Wall zapisovač je nepriehľadný, takže triedy 0x3F/0x40 samy osebe nedokazujú alpha/maskovanie.

### DOS statické porovnanie

DOS `FUN_1000_213e` skladá 18-bajtové spany z owner poľa `0x4564` a DOS `FUN_1000_202a` používa 16.16 interpoláciu. Kresliaci blok okolo `FUN_1000_25dc` aktualizuje per-column visibility pole `0x47E4`, počíta textúrovú súradnicu a volá stĺpcový writer na `0x1A2E`; planar VGA pitch je `0x50`. DOS sprite vetva používa obdobný wall test a bypass bit `0x10`, ale transparentný index je `0x1F`, nie Win16 `0x29`. Pre veľké DOS kresliace bloky sú hranice funkcií v dekompiláte neisté, preto to nie je dôkaz pixelovej parity.

## Zostávajúce brány k 100 %

| Brána | Stav |
|---|---|
| Kompletné hodnoty a význam tabuliek `0x247E`, `0x2480`, `0x2C7F`, `0x2E7E`; presné zaokrúhľovanie na hranách | Otvorené |
| Všetky prechody animácií, variantov textúr a čiastočného otvorenia dverí | Otvorené; statická kresliaca vetva to sama nerozhodne |
| Presná identita palety a `DAT_1048_8094` voči DOS VGA | Otvorené; dostupný `game.pal` je PCX 320×200 s vloženou paletou, nie surový originálny `GAME.PAL` |
| Poradie a orezanie všetkých prekrývajúcich sa tried spriteov | Statické slotovanie a wall test sú zmapované, vizuálne poradie nebolo porovnané s originálom |
| Win16 WinG vs DOS VGA framebuffer | Otvorené; chýba kontrolovaný beh pôvodných binárok a zhodné framebuffer snímky |
| HUD/zbraň/UI kompozícia a úplná vykresľovacia sekvencia | Mimo tejto wall/sprite pixelovej stopy |

Na skutočné „100 %“ treba zachytiť pôvodné indexované framebuffer snímky pre deterministické scény, spolu s paletou, build hashom, mapou, kamerou, časovačmi a medzivýsledkami owner/span bufferov. Bez originálneho behu by tvrdenie o pixelovej zhode nebolo podložené. Úplné stopy a testovacie prípady sú v [audite pixelovej cesty](Nitemare3D_renderer_pixel_path_audit_2026-09-23.md).