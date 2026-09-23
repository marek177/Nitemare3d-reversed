# Nitemare 3D — hlboká mapa projektilov a streľby (Win16 v1.10)

Dátum: 2026-09-23  
Rozsah: iba Windows 16-bit build NITE3W v1.10; DOS zostáva samostatná, zatiaľ neporovnaná vetva.

## Podklady a istota

Statická analýza dekompilačného exportu `nite3w110.exe.c` a Win16 binárky
`nite3w(20260921-205703).exe` (SHA-256
`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`).
Nižšie uvedené čítania a zápisy sú priamo viditeľné v exporte. Nevykonal som
runtime trace pôvodnej hry; presný čas v milisekundách, správanie DOS build-u a
niektoré mená polí preto zostávajú otvorené.

## Nové uzavreté zistenia

1. **USER.SAV blok `0xC403–0xC552` je projektilový pool.** Funkcia
   `FUN_1010_5466` zapisuje 336 bajtov (`0x150`) priamo z
   `&DAT_1048_4c4a`. `FUN_1010_574c` ich načíta späť na rovnakú adresu.
   `8 × 42 B = 336 B`, takže ide o presne osem projektilových záznamov.
   Blok, ktorý bol v predošlom audite označený ako anonymných 336 B, je týmto
   vyriešený s vysokou istotou.
2. **Projektilový záznam je kompozitný:** prvých 14 bajtov je pohybový stav;
   zvyšných 28 bajtov je vložený runtime OBJECT, ktorý sa odovzdáva bežnej
   projekčnej/renderovacej rutine `FUN_1010_cc7c`.
3. **Polia `+0x00…+0x06` implementujú Bresenhamovský line traversal.**
   `FUN_1010_e516` vytvorí os, chybový čítač a jeho prírastky; `FUN_1010_9d30`
   podľa nich posúva projektil po jednej súradnicovej jednotke a testuje bunku
   po každom malom kroku.
4. **Hodnota ±20 nie je lifetime ani cleanup.** `FUN_1010_9e20` zavolá
   `FUN_1010_cc7c` iba ak sa X alebo Y projektilu líši od hráčovej súradnice o
   viac než 20. `cc7c` pridá viditeľný objekt do projekčného zoznamu, vypočíta
   jeho projekciu a uloží projekčný údaj; nezruší projektilový stav. Toto
   opravuje predošlý opis, ktorý označil `cc7c` za cleanup.
5. **`record+0x28` nie je vek projektilu.** Je to vložené OBJECT pole
   `+0x1A`, ktoré projekčná rutina používa ako vertikálny posun sprite-u.
   Za letu rastie z 5 po 20 a pri náraze prestane rásť. Zásah/kolidovanie sa
   rieši oddelene v rovine mapových súradníc.
6. **Pred-multiplier damage závisí od renderovaného projekčného údaja cieľa.**
   `FUN_1010_cc7c` zapisuje do `OBJECT+0x18` projekčnú mierku odvodenú z
   kamery; `FUN_1010_9fa2` používa to isté pole v základe damage. Ide teda o
   vzdialenosť/veľkosť cieľa premietnutú do kamery, nie o konštantu pevne
   priradenú zbrani.

## Volacie a dátové cesty

| Fáza | Rutina | Potvrdená úloha |
|---|---|---|
| Vstup streľby | `FUN_1010_8b06` | Rozdelí hitscan režim zbrane ID 2 od projektilového režimu ID 0, 1, 3. |
| Kadencia/ammo | `FUN_1010_aa90`, `FUN_1010_a97c` | Kontroluje update čítač kadencie; odpočíta muníciu. `9aac` najprv vyhľadá voľný slot a až potom zavolá ammo helper; pri plnom poole sa helper vôbec nezavolá, takže munícia sa nespotrebuje. |
| Smer | `FUN_1010_e516` | Normalizuje uhol na 0–359, vypočíta pevné trigonometrické komponenty a Bresenhamove prírastky. |
| Alokácia | `FUN_1010_9aac` | Nájde prvý voľný z ôsmich slotov, inicializuje let, pozíciu, smer, sequence a render objekt. |
| Update | `FUN_1010_d9c6` → `FUN_1010_9e20` | Scheduler volá projektilový update v sekundárnom časovacom cykle; v tom istom cykle beží projekcia scény. |
| Pohyb/kolízia | `FUN_1010_9d30` → `FUN_1010_9b64` | Vykoná `DAT_1048_53fa` malých krokov; po každom kroku testuje mapovú bunku, guard alebo wall. |
| Animácia | `FUN_1010_9e20` | Flight animácia sa cyklí; impact animácia dobehne a zmení stav slotu na voľný. |
| Render | `FUN_1010_cc7c` | Projekcia vloženého OBJECT do viditeľného zoznamu, depth/scale cache a projekčný vertical offset. |
| Damage | `FUN_1010_80f8` → `FUN_1010_9fa2` | Zníži HP, nastaví pain/recovery alebo death; damage berie projekčný údaj cieľa, typ objektu, zbraň a obtiažnosť. |
| Save/load | `FUN_1010_5466`, `FUN_1010_574c` | Serializuje/deserializuje celý 336-bajtový pool. Po load-e sa odvodené mapové odkazy znovu vypočítajú. |

## Presná mapa záznamu (42 bajtov)

Základ poolu je `DAT_1048_4c4a`; slot `i` leží na `base + 42*i`.
Číselné offsets sú hexadecimálne.

| Offset | Význam | Dôkaz / hranica istoty |
|---:|---|---|
| `+0x00` | Voľba hlavnej osi: 1 keď je X komponent väčší, inak Y | `e516` zapisuje porovnanie absolútnych trig. komponentov; `9d30` podľa hodnoty volí os hlavného kroku. |
| `+0x02` | Bresenhamov chybový čítač, inicializovaný ako `2*minor − major` | Výpočet v `e516`, porovnávanie so 0 a prírastky v `9d30`. |
| `+0x04` | Chyba pre menší krok: `2*minor` | `e516` → `9d30`. |
| `+0x06` | Korekcia chyby: `2*(minor − major)` | `e516` → `9d30`. |
| `+0x08` | Znamienko X kroku (`−1` alebo `+1`) | `9aac` ho volí z normalizovaného uhla; `9d30` ním posúva X. |
| `+0x0A` | Znamienko Y kroku (`−1` alebo `+1`) | Analogicky. |
| `+0x0C` | Stav: 0 voľný, 1 let, 2 impact animácia | Alokátor `9aac`, update `9e20`, kolízia `9d30`, dokončenie impactu `9e20`. |
| `+0x0D` | Nepomenované bajtové pole | V analyzovanej ceste sa nepodarilo určiť stabilný význam. |
| `+0x0E…+0x29` | Vložený runtime OBJECT záznam, 28 B | `cc7c` dostáva ukazovateľ `projectile + 0x0E`; ďalšie polia sa mapujú podľa OBJECT layoutu. |
| `+0x11` | Frame index vloženej animácie | Nuluje sa pri spawne/náraze, zvyšuje sa podľa termínu sekvencie. |
| `+0x12` | Flight/impact sequence index | `a930`/`a956`, mení sa podľa weapon ID. |
| `+0x13` | OBJECT flags | Pri spawne sa nastaví bit `0x01` a vymaže bit `0x10`; pri náraze sa `0x10` nastaví. Bit `0x01` povoľuje projekciu v `cc7c`. |
| `+0x14` | OBJECT type field, hodnota `5` v projectile template | Pri inicializácii render/sequence template sa nastavuje `DAT_1048_4c5e=5`. |
| `+0x16…+0x19` | 32-bit absolútny deadline animácie | Porovnáva sa s 32-bit globálnym časom; prírastok pochádza zo sequence tabuľky. Jednotka nie je prevedená na ms. |
| `+0x1A…+0x1D` | Far pointer do aktuálneho MAP segmentu: offset + segment | Na spawne skopíruje hráčov MAP pointer; po load-e sa offset prepočíta z uloženého projectile X/Y a segment nastaví na načítaný MAP segment. Či sa pointer aktualizuje pri každom pohybe, zostáva otvorené. |
| `+0x1E…+0x1F` | Aktuálne X súradnice | Na spawne = X hráča; potom mení `9d30`. |
| `+0x20…+0x21` | Aktuálne Y súradnice | Na spawne = Y hráča; potom mení `9d30`. |
| `+0x26…+0x27` | Projekčná mierka/depth cache (`OBJECT+0x18`) | `cc7c` zapisuje `local_8`; rovnaké pole cieľového OBJECT číta damage výpočet `9fa2`. |
| `+0x28` | Vertikálny posun vloženého OBJECT (`OBJECT+0x1A`) | Inicializuje sa na 5, za letu rastie po 20; `cc7c` ho používa na posun projekčnej výšky. |
| `+0x0F`, `+0x10`, `+0x15`, `+0x24…+0x25`, `+0x29` | Nepomenované alebo template polia | Zostávajú na ďalší writer/reader audit. |

### Line traversal a speed

`FUN_1010_e516` z uhla pripraví komponenty X/Y, zvolí dominantnú os a nastaví
Bresenhamov error term. `FUN_1010_9d30` potom opakuje až
`DAT_1048_53fa` krát za update: krokne dominantnú os; ak error prejde cez nulu,
krokne aj druhú os. Po každom podkroku `FUN_1010_9b64` vypočíta mapovú bunku z
X/Y a testuje jej property.

`DAT_1048_53fa` nie je pevná konštanta: `FUN_1010_d7d0` ju nastavuje na
`2 * DAT_1048_53f6`, pričom `53f6` sa odvodzuje z nameraného času viacerých
update/render priechodov. Tým je potvrdené CPU/timer kalibrovanie počtu
podkrokov. Presnú rýchlosť v jednotkách za sekundu bez runtime merania
neuvádzam.

Hranica `±20` v `9e20` má iný účel: ak `abs(projectileX-playerX)>20` **alebo**
`abs(projectileY-playerY)>20`, zavolá sa `cc7c` na projekciu vloženého OBJECT-u.
Ak je projektil bližšie v oboch osiach, tento render call sa preskočí. Slot sa
v tejto vetve nemení ani neuvoľňuje; collision/movement sa rieši osobitne.

### Sequence a animácia

`FUN_1010_9e20` indexuje sequence tabuľku stride `8 B` podľa sequence ID:

- počet frame-ov: word na `0x4744 + 8*sequence_id`;
- interval/ďalší deadline: dword od `0x4746 + 8*sequence_id`;
- pri stave 1 sa frame po termíne zväčší a loopuje späť na 0;
- pri stave 2 sa frame zväčšuje bez loopu; po dobehnutí frame count sa stav nastaví na 0.

Flight/impact sequence ID sú `base + offset`; `base` je runtime index
projektilového OBJECT sequence banku:

| Weapon ID | Flight offset | Impact offset |
|---:|---:|---:|
| 0 | 0 | 1 |
| 1 | 2 | 3 |
| 2 (hitscan) | 0 | 1 |
| 3 | 0 | 1 |

Toto je sequence index mapovanie, nie ešte mapovanie na zvukový sample.

## Kolízia a damage

### Projektilová kolízia

`FUN_1010_9b64` testuje wall property a object class pre práve navštívenú
mapovú bunku. Ak je tam guard flag, vyhľadá guard record a porovná súradnice
projektilu s guardom: zásah nastane, keď rozdiel na oboch osiach neprekročí 9
world-coordinate jednotiek. Potom sa volá `FUN_1010_80f8`.

Pri explodable wall property (`0x10`) sa vyvolá event `0x29`, runtime objekt
wall triedy sa preklasifikuje na `0x2D` a začne explózna sekvencia. Odstránenie
stavebného wall/collision stavu po dokončení sekvencie zostáva neuzavreté.

### Range-scaled damage

`FUN_1010_e5d8` prepočíta world-relative vektor do projekcie kamery. Forward
komponent tvorí deliteľ; druhý výstup je `DAT_1048_3a72 / forward +
DAT_1048_53f0`. Render rutina `cc7c` tento výstup posunie doprava o 4 a uloží
do `OBJECT+0x18`.

`FUN_1010_9fa2` tvorí základ:

```text
raw = ((target_OBJECT[0x18] - DAT_1048_53ee) * 8) + (RNG % 25)
```

Z toho vyplýva, že väčší projekčný scale index (bližší/väčší na obrazovke cieľ)
dáva väčší raw damage. Toto je aritmetická inferencia z projekčného vzorca a
field writer-u; presné tickové poradie renderu oproti výstrelu treba ešte
potvrdiť dynamicky. Potom `9fa2` aplikuje class/weapon shifts a obtiažnosť:

| Target object class | Transformácia raw damage pred difficulty |
|---:|---|
| `0x0C`, `0x1D` | `>> 3` |
| `0x0D` | weapon 1: `>> 1`; ostatné: `>> 3` |
| `0x0E`, `0x11`, `0x14` | weapon 2: `>> 1`; ostatné: `>> 3` |
| `0x0F`, `0x10` | weapon 1: `>> 8`; ostatné: `>> 1` |
| `0x12`, `0x13` | `>> 2` |
| `0x15` | 0 (vykoná sa aj vedľajšia rutina `FUN_1018_083e`) |
| `0x16` | damage 3 iba ak `episode==3` alebo `DAT_1048_51a6 != 0`; inak 0 |
| `0x17` | weapon 1: `>> 8`; ostatné: `>> 2` |
| `0x18` | weapon 1: `>> 8`; weapon 2: `>> 4`; ostatné: `>> 3` |
| `0x19` | 0 |
| `0x1A`, `0x1B`, `0x1C` | weapon 1: `>> 1`; ostatné: 0 |
| `0x1E` | weapon 1: 0; ostatné: `>> 3` |
| `0x1F` | weapon 1: 0; ostatné: `>> 2` |
| ostatné triedy | bez class shift |

Po triede sa difficulty 2 delí 2; difficulty 0 násobí 2; ostatná hodnota
nemení raw damage. Výsledok sa saturuje na `255`. Neletálny zásah odpočíta HP,
nastaví guard timer `+0x12=8` a prejde do pain/recovery cesty. Smrteľný zásah
nastaví HP na nulu, spustí death vetvu a pripočíta class score.

## USER.SAV offsety — vyriešenie anonymného bloku

Dĺžky priamo zapisované v `FUN_1010_5466` sedia na offsety z bajtového auditu
USER.SAV:

| Začiatok | Dĺžka | Koniec (exkl.) | Obsah |
|---:|---:|---:|---|
| `0x2093` | `0x6D60` (28 000) | `0x8DF3` | runtime vector array |
| `0x8DF3` | `0x2648` (9 800) | `0xB43B` | 350 × 28 B OBJECT |
| `0xB43B` | `0x0A28` (2 600) | `0xBE63` | 100 × 26 B GUARD |
| `0xBE63` | `0x0580` (1 408) | `0xC3E3` | 64 × 22 B door/state records |
| `0xC3E3` | `0x20` (32) | `0xC403` | 32 panel activation bytes copied from each panel record `+0x14` |
| **`0xC403`** | **`0x150` (336)** | **`0xC553`** | **8 × 42 B projectile pool (`DAT_1048_4c4a`)** |
| `0xC553` | `0x08` | `0xC55B` | `DAT_1048_51a4` |
| `0xC55B` | `0x48` (72) | `0xC5A3` | 12 × 6 B push records |

Pri load-e sa offset v `+0x1A…+0x1D` každého projectile render OBJECT-u
znovu vypočíta z jeho uložených X/Y a segment sa nastaví na načítaný MAP
segment. `FUN_1010_574c` zároveň obnovuje smer zbrane cez `FUN_1010_e516`.
Či sa animácie po load-e presne zachovajú pri reštarte globálneho času, treba
ešte overiť; projectile deadline sa načíta ako súčasť poolu. Počas letu sa
pole s mapovým pointerom v `9d30` priamo nemení, preto zostáva otvorené, či ho
upravuje iná cesta alebo ide o referenciu na bunku spawnu.

## Otvorené položky pre ďalší prechod

- Porovnať celý pool writer/reader s DOS 2.0; bez DOS dekompilu netreba
  prenášať Win16 layout na DOS.
- Zistiť jednotky `DAT_1048_53fa` a 32-bit globálneho času; preveriť, kedy sa
  kalibračná hodnota mení pri prepnutí fullscreen/windowed režimu.
- Nájsť všetkých writerov/readers pre zatiaľ nepomenované bajty embedded OBJECT-u,
  najmä projectile `+0x0D`, `+0x0F`, `+0x10`, `+0x15`, `+0x24…+0x25`, `+0x29`;
  overiť, či far pointer na mapovú bunku sleduje let alebo zostáva na bunke spawnu.
- Dynamicky potvrdiť poslednú projekčnú cache cieľa v momente damage a vzťah
  raw damage k skutočnej vzdialenosti.
- Dokončiť wall class `0x2D` completion writer, ktorý odstráni wall collision.
- Mapovať weapon sequence indexy na SND.DAT sloty; samotný sequence index
  nepreukazuje zvuk.
- Zostáva behaviorálne overiť, či GUARD hitbox tolerance `9` platí rovnako pre
  všetky guard class/sprite varianty.

## Primárne rutiny na kontrolu v dekompilačnom exporte

`FUN_1010_8b06`, `FUN_1010_9aac`, `FUN_1010_e516`, `FUN_1010_9d30`,
`FUN_1010_9b64`, `FUN_1010_9e20`, `FUN_1010_cc7c`, `FUN_1010_e5d8`,
`FUN_1010_80f8`, `FUN_1010_9fa2`, `FUN_1010_a930`, `FUN_1010_a956`,
`FUN_1010_d7d0`, `FUN_1010_d9c6`, `FUN_1010_5466`, `FUN_1010_574c`.
