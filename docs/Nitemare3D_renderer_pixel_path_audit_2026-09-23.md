# Nitemare 3D — audit pixelovej cesty rendereru

**Dátum:** 23. september 2026  
**Rozsah:** Win16 1.10 wall/span a sprite výstup; porovnávacie statické stopy DOS v2.0  
**Výsledok:** pixelová cesta Win16 je staticky sledovaná od viditeľného spanu po framebuffer a spracovanie spriteov. Pixelová zhoda s pôvodnou hrou ani DOS/Win16 zhoda nie sú overené živým behom.

## Záver

Otvorený bod „neznámy finálny pixelový zapisovač“ je uzavretý pre hlavný Win16 stenový a sprite kód: stenový span vyberie textúrový stĺpec, interpolačnú/clipping tabuľku a shade mapu a zapisuje do lineárneho WinG framebufferu alebo do planar VGA obrazovej pamäte. Sprite slučka má samostatnú transparentnú paletovú hodnotu a porovnáva každý stĺpec s per-column wall-visibility bufferom.

To však ešte nie je 100 % kompatibilita. Chýba kontrolovaný beh pôvodných binárok a porovnanie zachytených indexed-color framebufferov; neboli tiež kompletne vyhodnotené všetky hodnoty tabuľkových konštánt a všetky dynamické stavy dverí, animácií a spriteov. V prostredí nie sú dostupné Wine ani DOSBox a súbor s názvom `game.pal` je PCX snímka s vloženou paletou, nie surový originálny `GAME.PAL`.

## Referenčné binárky a hranice dôkazov

| Build | Súbor | SHA-256 | Použitie |
|---|---|---|---|
| Win16 1.10 | `nite3w(20260921-205703).exe` | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` | Primárny zdroj stôp pixelového zapisovača a sprite rendereru. |
| DOS v2.0 | `N3D-UNFU(2).exe` | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` | Statické porovnanie spanov, VGA výstupu a sprite testu. DOS dekompilovaný výpis má poškodené hranice niektorých veľkých funkcií. |

Adresy Win16 sú segment:offset; názvy `FUN_*` sú analytické mená, nie pôvodné symboly. DOS adresy nižšie sú funkčné mená z dekompilovaného výpisu. Pri DOS kreslení sa kvôli zlúčeniu hraníc opieram o viditeľné inštrukčné/pseudokódové úseky, nie o predpoklad, že každá dekompilovaná funkcia zodpovedá jednej pôvodnej funkcii.

## 1. Rámec vykreslenia

`FUN_1010_d78c` (Win16 3:D78C) volá v tomto poradí:

1. `FUN_1018_3940` — naplní per-column vlastníctvo stenových vektorov;
2. `FUN_1010_6266` — zoskupí súvislé stĺpce vlastníka do spanov;
3. `FUN_1010_3db8` — vyplní strop/podlahu;
4. `FUN_1010_66b0` — vykreslí stenové spany;
5. `FUN_1010_6348` — vyberie a premietne viditeľné objekty;
6. `FUN_1010_6914` — prejde sloty objektov a zavolá sprite rasterizáciu `FUN_1010_3f80`.

Z toho vyplýva poradie wall → objekty/spritey. Stenový visibility buffer vzniká pred sprite kreslením.

## 2. Stenový pixelový zapisovač

### Textúra, U a animácia

`FUN_1010_66b0` pre každý 20-bajtový span načíta jeho VEC far pointer, vyberie aktuálny sequence/frame descriptor a frame pointer. Index textúrového stĺpca sa počíta cez `FUN_1010_ebd6`; `FUN_1010_6422` potom vykoná okrajovú korekciu vybraných tried a nakoniec obmedzí index výrazom `(šírka - 1) & hodnota`. Príznak VEC `+05 bit 0x08` obíde uvedenú špeciálnu okrajovú korekciu. Triedy `0x3F` a `0x40` obracajú orientačný bit `+05 bit 0x20` pri výbere textúrového smeru.

### Vertikálne vzorkovanie a zapisovanie

`FUN_1010_3e44` prepína medzi lineárnou WinG cestou `FUN_1010_366a` a planar VGA cestou podľa `DAT_1048_46b0`:

- **Textúra:** počiatočná adresa stĺpca je `base + U * 0x40`; zdroj preto používa 64-bajtový krok na susedný textúrový stĺpec.
- **Vertikálny V krok:** dvojice hodnôt z tabuliek na offsetoch `0x247E` a `0x2480` dávajú zlomkový/integer prírastok zdrojového ukazovateľa pre každý výstupný pixel. Carry zo 16-bitového zlomkového akumulátora mení integer prírastok. Pri hornom orezaní sa počiatočný zdrojový offset a zlomkový stav upravia tabuľkami `0x2C7F` a `0x2E7E`.
- **WinG/DIB framebuffer:** pixel sa uloží na `y * 0x140 + x`; ďalší riadok je `+0x140` (320 bajtov). Cesta zapisuje jeden 8-bitový index na pixel.
- **Planar VGA:** adresa je `page * 0x10 + y * 0x50 + (x >> 2)`; maska sa posiela cez VGA sequencer porty `0x3C4/0x3C5`. Ďalší riadok je `+0x50` (80 bajtov), čo zodpovedá štyrom VGA rovinám.
- **Osvetlenie:** pri shade argumente `0` sa zapisuje pôvodný texture index; pri nenulovej hodnote sa zapisuje `DAT_1048_8094[texture_index]`. Ide o paletový/remap lookup, nie true-color miešanie.
- **Stenová priehľadnosť:** obe vetvy zapisovača kopírujú každý vzorkovaný pixel bez porovnania s transparentným kľúčom. V tejto ceste je preto stenová texelová plocha nepriehľadná; spriteový transparentný test je samostatná logika.

Čo je stále otvorené: úplný dump a pomenovanie všetkých tabuliek `0x247E`, `0x2480`, `0x2C7F`, `0x2E7E`, presné medzné zaokrúhľovanie pri každej výške/ohranení viewportu a presná paletová zhoda zdroja `DAT_1048_8094` s DOS.

## 3. Priehľadnosť a oklúzia spriteov

`FUN_1010_6348` vyberá objekty a volá projekciu/slotovanie cez `FUN_1010_cc7c`. Tá zapisuje 18-bajtové položky do 100 slotov od `0x6270`, pričom sloty vyberá podľa premietnutého vertikálneho rozsahu. `FUN_1010_6914` prechádza sloty vzostupne a pre každý aktívny slot volá `FUN_1010_3f80`.

`FUN_1010_3f80` (Win16 3:3F80) má lineárnu WinG implementáciu `FUN_1010_374e` a planar VGA vetvu:

- pri každom sprite stĺpci číta hodnotu z wall visibility bufferu `0x58FE` a porovná ju s hodnotou sprite záznamu `+0x10`;
- ak VEC flag `+05 bit 0x10` nie je zapnutý, sprite stĺpec sa kreslí iba keď prejde týmto porovnaním; pri zapnutom bite sa wall test obíde;
- pixely s hodnotou `0x29` (ASCII `')'`) preskočí, čím ponechá už vykreslený framebuffer pod nimi;
- sprite rasterizátor do `0x58FE` nezapisuje novú hĺbku. Následné spritey preto nemajú vlastný per-sprite Z test a prekrytie závisí od slotového poradia.

Toto je staticky potvrdený **per-column wall occlusion** test, nie všeobecný per-pixel Z-buffer. Presné vizuálne poradie všetkých tried objektov, varianty frame orientácie a interakcie pri prekrývaní treba ešte porovnať na pôvodnej scéne.

### Dvere/závesy a triedy stien

Kontrola 256-bajtovej wall-ID → class tabuľky v dodaných `MAP.1–3` priniesla:

| Súbor | Mapové ID → trieda | Výskyt v dodaných leveloch |
|---|---|---|
| `MAP.1` | `0x70/0x72/0x74 → 0x3F`; `0x71/0x73/0x75 → 0x40` | Obe triedy sa používajú v niekoľkých leveloch. |
| `MAP.2` | `0xAA → 0x3F`; `0xAB → 0x40` | Obe sa vyskytujú v prvom level bloku. |
| `MAP.3` | žiadne ID pre `0x3F/0x40` | V kontrolovanej tabuľke sa nevyskytujú. |

Zodpovedajúce riadky `WALLS.1/.2` ich pomenúvajú ako `DOORVC`/`DOORHC` „curtain“. Triedy `0x3D` a `0x3E` nemajú priradené ID v kontrolovaných wall class tabuľkách dodaných `MAP.1–3`; staršia poznámka, ktorá ich označila za otvorený prípad aktívnych transparentných wall tried, sa tým opravuje. Nenašiel sa pixelový alpha test v stenovom zapisovači. Či sa vizuálne čiastočné otvorenie konkrétnych dverí realizuje zmenou geometrie, sekvenciou alebo mapovým stavom, treba ešte samostatne sledovať cez všetky update zápisy a originálny beh.

### DOS v2.0 statické porovnanie

DOS `FUN_1000_213e` skladá span zoznam z owner poľa na `0x4564`, s počtom na `0x4D64`, poľom spanov od `0x4D6E` a 9-word/18-bajtovým stride. `FUN_1000_202a` pripravuje 16.16 vertikálnu interpoláciu. Kresliaci blok okolo `FUN_1000_25dc` používa stĺpcový visibility buffer na `0x47E4`, premieta textúrové U cez volanie na offsete `0xCEDC`, aktualizuje visibility hodnotu a volá stĺpcový zapisovač na `0x1A2E`. Viditeľné VGA zápisy používajú planar adresovanie s riadkovým krokom `0x50` a sequencer `0x3C4/0x3C5`.

DOS sprite slučka v dekompilovanom bloku pre triedu/branch `0x0C` používa rovnaký per-column compare s `0x47E4`, ten istý VEC flag `0x10` ako bypass a transparentný index `0x1F`. Rozdiel transparentného kľúča oproti Win16 `0x29` je **skutočný pozorovaný build rozdiel**; nie je bezpečné nahradiť ho spoločnou konštantou bez kontroly presne zodpovedajúcej asset sady.

DOS dekompilovaný výpis má v stene rendereru poškodené/posunuté funkčné hranice, takže podobnosť architektúry je **silná statická zhoda**, nie dôkaz byte-for-byte totožného vykreslenia.

## 4. Farebné vstupy a limity

Dostupný súbor `game.pal` má PCX hlavičku, rozmery 320×200, indexed-color režim a vlastnú vloženú paletu 256 farieb. Je to obrázok, nie surový `GAME.PAL`; pôvod a väzba na referenčné binárky nie sú doložené. Možno ho použiť len ako kandidátny farebný odkaz. Dokým sa nespáruje s originálnym palette loaderom alebo framebuffer capture, nemôže potvrdiť presné RGB výstupy.

## 5. Stav uzavretia

| Otázka | Stav | Dôkaz/obmedzenie |
|---|---|---|
| Win16 span → texture U → V sampling → pixel writer | **Staticky uzavreté** | `66B0 → EBD6/6422 → 3E44 → 366A` a planar VGA vetva. |
| 320-bajtový WinG pitch a 80-bajtový planar VGA pitch | **Staticky uzavreté** | Priame adresné prírastky a sequencer zápisy. |
| Shade remap a stenové alpha | **Staticky uzavreté na úrovni vetvy** | `8094` lookup; stenový writer zapisuje bez transparent testu. Všetky tabuľkové hodnoty/paleta nie sú porovnané. |
| Win16 sprite transparentný kľúč a wall occlusion | **Staticky uzavreté** | Kľúč `0x29`; compare s `0x58FE`; flag `0x10` obchádza test. |
| DOS sprite kľúč a porovnávacia cesta | **Silná statická podpora** | Kľúč `0x1F`, compare s `0x47E4`; dekompilované hranice sú slabšie. |
| Aktívne curtain wall triedy | **Dáta uzavreté pre dodané MAP/WALLS** | Triedy `0x3F/0x40`; `0x3D/0x3E` nepoužité v checked MAP lookups. |
| Medzikrokové dvere/otvorenie, všetky overlap páry a viewport hrany | **Otvorené** | Treba dohľadať každý dynamický zápis a overiť ho na pôvodnej scéne. |
| Presný Win16/DOS pixelový výsledok | **Otvorené — blokuje 100 %** | Nie je zachytený originálny framebuffer z rovnakého deterministického stavu. |

## 6. Akceptačný test potrebný na 100 %

Na oprávnené označenie rendereru za 100 % treba, pre každú build/data kombináciu:

1. spustiť presnú hashnutú binárku a zachytiť indexed framebuffer aj palette state;
2. zafixovať kameru, mapu, door/sequence timers, zorné pole a object slot poradie;
3. pokryť near-plane a viewport hranice, všetky štyri orientácie a každú dvojicu konkurenčných wall orientácií;
4. pokryť zatvorené, každý otvorený medzistav a úplne otvorené dvere; transparent sprite, wall-occluded sprite aj flag-`0x10` overlay; shade levels a animované frame varianty;
5. porovnať DOS VGA a Win16 WinG po normalizácii VGA rovín na indexované pixely, najprv po geometrii, potom po textúre, shade/palette a sprite kompozícii;
6. uložiť referenčné snímky, hashe, map bytes, runtime timers a medzivýsledky owner/span bufferov.

Bez týchto pôvodných framebufferov by percento 100 bolo nepodložené. Aktuálny výsledok uzatvára dôležité statické neznáme, no nedokazuje presnú vizuálnu kompatibilitu.

## Kotvy v exportoch

- Win16 orchestration: `nite3w110.exe.c`, `FUN_1010_d78c` približne riadok 30100.
- Wall render: `FUN_1010_66b0` riadok 23194; `FUN_1010_6422` riadok 23050; `FUN_1010_3e44` riadok 20778; linear writer `FUN_1010_366a` riadok 20073.
- Sprite: `FUN_1010_6348` riadok 22983; `FUN_1010_6914` riadok 23323; planar/dispatcher `FUN_1010_3f80` riadok 20871; linear renderer `FUN_1010_374e` riadok 20142; slot insertion `FUN_1010_cc7c` riadok 29413.
- DOS spans: `N3D-DOS-UNFULL-v20.exe.c`, `FUN_1000_213e` riadok 2853; interpolation `FUN_1000_202a` riadok 2800; wall drawing block `FUN_1000_25dc` začína riadkom 3093.