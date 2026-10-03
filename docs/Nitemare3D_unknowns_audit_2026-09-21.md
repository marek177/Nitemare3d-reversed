# Nitemare 3D — audit neznámych štruktúr (1. etapa)

Zdroj dôkazov: originálny Win16 `NITE3W.EXE` V1.10 (230 400 B), NE segmenty a relokačné/bezprostredné odkazy na interné diagnostické reťazce. Dátum: 2026-09-21.

## Nové priamo potvrdené limity

| Oblasť | Limit | Segment:kód | Dôkaz |
|---|---:|---|---|
| dvere | 64 | `3:14EB–14F6` | porovnanie s `0x40`, hlásenie `MAXDOORS exceeded` |
| panely | 32 | `3:171E–1725` | limit `0x20`, `MAXPANELS exceeded` |
| posuvné objekty/pushes | 12 | `3:183A–1847` | limit `0x0C`, `MAXPUSHES exceeded` |
| obrazové sloty | 70 | `3:4BB3–4BBE` | limit `0x46`, `MAXIMAGE exceeded` |
| renderované segmenty | 50 | `3:62F8–6304` | limit `0x32`, `MAXSEG exceeded` |
| objekty | 350 | `3:D1EA–D1F2` | limit `0x015E`, `MAXOBJ exceeded` |
| guards | 100 | `3:D28C–D298` | limit `0x64`, `MAXGUARD exceeded` |
| vector list | 333 | `4:34E1–34EF` | limit `0x014D`, `MAXVECLIST exceeded` |
| vectors | 1000 | `4:4073–407E` | limit `0x03E8`, `MAXVEC exceeded` |

Tieto hodnoty nie sú odhady zo správania hry. Sú priamo vložené do hraničných kontrol v originálnom EXE.

## Opravené mapovanie polí USER.SAV

Predchádzajúci audit poznal veľkosti blokov, ale nie ich triedy. Kombinácia presných limitov z EXE a veľkostí blokov umožňuje potvrdiť:

| Offset v save | Veľkosť | Nová interpretácia | Výpočet | Istota |
|---:|---:|---|---:|---|
| `0x2093` | 28 000 | pole vektorov | `1000 × 28 B` | vysoká |
| `0x8DF3` | 9 800 | pole objektov | `350 × 28 B` | potvrdené |
| `0xB43B` | 2 600 | pole guards | `100 × 26 B` | potvrdené |
| `0xBE63` | 1 408 | pole dverí | `64 × 22 B` | potvrdené |
| `0xC403` | 336 | zatiaľ neidentifikovaný runtime blok | — | otvorené |
| `0xC55B` | 72 | pole pushes | `12 × 6 B` | potvrdené |

Pôvodný aritmetický odhad `350 × 80 B` a `100 × 98 B` bol nesprávny. Priamy kód používa pre objekty krok `0x1C` a pre guards krok `0x1A`. Blok 28 000 B sa zhoduje s `MAXVEC=1000 × 28 B`. Rendererový zoznam pri `0x5E88` používa krok `0x14 = 20 B`, kapacitu 50 a je samostatnou prechodnou štruktúrou.

Poznámka: save blok 336 B pri `0xC403` ešte nemožno nazvať priamo poľom 12 šesťbajtových push záznamov. Skutočný runtime push zoznam má `12 × 6 = 72 B` a zapisuje sa osobitne z adresy `0xA616`. Blok 336 B preto zostáva významovo otvorený.

## Priamo potvrdené runtime polia

### Object record — 28 B

- báza `0x6D66`;
- kapacita 350, čítač `0x7E58`;
- indexovanie `index × 0x1C`;
- `+0x00`: object ID/class byte;
- `+0x01`: odvodený variant/frame/orientation byte;
- `+0x02`, `+0x03`: nulované stavové bajty;
- `+0x05`: flags;
- `+0x06`: sequence/type odvodený z class tabuľky;
- `+0x07`: guard index, ak má objekt guard flag;
- `+0x08`: 32-bit runtime hodnota/timer — nulovaná pri vytvorení;
- `+0x0C`, `+0x0E`: súradnice/pointerová väzba; pri mapových objektoch sa zapisujú pozície v jednotkách 64;
- `+0x10`, `+0x12`: ďalšie X/Y hranice alebo koncové súradnice.

### Guard record — 26 B

- báza `0x93AE`;
- kapacita 100, čítač `0x7E5E`;
- indexovanie `index × 0x1A`;
- `+0x06`: 16-bit timer — opakovane testovaný a znižovaný;
- `+0x08`: index priradeného 28-bajtového object recordu;
- `+0x0A`: strategy kandidát;
- `+0x0B`: aktuálny `state`;
- `+0x0C`: `next_state`;
- `+0x0D`: pomocný stav/frame/direction — presný názov otvorený;
- `+0x0E`: sequence-definition index;
- `+0x0F`: porovnávací/anim-state flag;
- `+0x10`: strength/health kandidát; číta sa a znižuje v damage vetve;
- `+0x11`, `+0x13`, `+0x14`: smer a odvodené pozičné hodnoty;
- `+0x17`: runtime flag nastavovaný v guard logike.

Väzba požadovaných polí je teda v jednom 26-bajtovom zázname: `strategy +0x0A → state +0x0B → next_state +0x0C`, kým 16-bitový `timer` leží na `+0x06` a pravdepodobný `strength` na `+0x10`.

### Doors, panels a pushes

- doors: báza `0x9DD6`, `64 × 22 B`;
- panels: báza `0xA356`, `32 × 22 B`; každý záznam obsahuje až štyri far pointery a stavové pole;
- pushes: báza `0xA616`, `12 × 6 B`; `+0x00` je index objektu, `+0x04` stavový byte;
- door a panel používajú rovnakú veľkosť 22 B, ale samostatné polia a čítače;
- push lookup prevádza uložený object index násobením `×0x1C` a porovnáva objektové súradnice.

## Oddelené triedy a lookup funkcie

EXE má samostatné chybové vetvy:

- `Door not in map`: odkazy z `3:12DA`, `3:132C`, `3:15E9`;
- `Push not in map`: `3:1384`;
- `Wall class %d undefined`: `3:238D`;
- `No objects of class %d in level`: `3:2417`;
- `No seqdef defined for guard`: `3:501E`;
- `Guard not in map`: `3:83C2`;
- `Object not in map`: `3:AD75`, `3:ADC8`;
- `Vector not in map`: `4:3919`.

To potvrdzuje, že door, push, guard, object a vector nie sú iba rôzne flagy jedného univerzálneho záznamu. Majú samostatné lookup/validation vetvy a aspoň niektoré aj samostatné pevné polia.

## Dôležitý rozdiel oproti Wolf3D

Objavené limity `MAXSEG=50`, `MAXVECLIST=333` a `MAXVEC=1000` podporujú už zistený záver, že renderer Nitemare 3D pracuje s vektormi a projektovanými segmentmi. Nie je to iba klasický Wolf3D grid-DDA renderer s jedným zásahom steny pre každý stĺpec obrazovky. Borland/Wolf3D zdroje sú preto vhodné najmä na rozpoznanie runtime, vstupu, zvuku a správcu pamäte, nie ako 1:1 model rendereru.

## Čo ostáva neznáme

1. Presný význam zostávajúcich polí 28-bajtového object a 26-bajtového guard záznamu.
2. Definitívne potvrdenie názvov `strategy` na `guard+0x0A` a `strength` na `guard+0x10` cez diagnostický formátovací kód.
3. Význam anonymného 336-bajtového save bloku pri `0xC403`.
4. Presné väzby `warp_l1`, `warp_l2`, kľúče/karty a remote-door príkazy.
5. Guard tabuľka `state → next_state → timer`, vrátane stratégie a strength.
6. Význam 333-prvkovej `VECLIST` oproti 1000-prvkovému hlavnému poľu `VEC`.

## Cross-version audit Win16 1.3 / 1.6 / 1.8 — prvý merateľný prechod (2026-09-22)

Zdroj: Ghidra C exporty `NITE3W13.EXE.c`, `NITE3W16.EXE.c`, `NITE3W18.EXE.c` a
`NITE3W_function_candidates.csv`. Oprava druhým prechodom: pôvodné čísla 3 281/3 313
boli všetky výskyty `FUN_*` vrátane volaní, nie deklarácie. Tabuľka používa počet
unikátnych symbolov. Ani ten ešte nemusí byť presný počet pôvodných zdrojových funkcií,
pretože Ghidra niektoré callbacky nerozpoznala ako funkcie.

| Build | Rozpoznané `FUN_*` deklarácie | Diagnostické reťazce | Stav |
|---|---:|---|---|
| 1.3 | 959 | bez `debug.txt`, `dstopen.img` a rozšírenej synth diagnostiky | CONFIRMED v dodanom exporte |
| 1.6 | 965 | `debug.txt`, `dstopen.img`, `SeqID`, `MOD_*SYNTH`, `numseq` | CONFIRMED v dodanom exporte |
| 1.8 | 965 | rovnaká skupina diagnostických reťazcov ako 1.6 | CONFIRMED v dodanom exporte |

Rozdiel `+6` je rozdiel rozpoznaných symbolov, nie ešte dôkaz šiestich skutočne nových
rutín. Napríklad build 1.3 odovzdáva triedeniu callback na raw offsete `0x3032`, ale
Ghidra na tomto mieste nevytvorila `FUN_*`; v 1.6 je ekvivalentný comparator už
rozpoznaný ako `FUN_1018_32f8`. Časť rozdielu teda vzniká kvalitou analýzy.

### Nové potvrdené runtime vetvy

- `FUN_1018_336c` je podmienený logger. Ak je globálny debug flag `DAT_1048_46ab`
  nenulový, otvorí alebo znovu otvorí `debug.txt`, zapíše formátovanú správu a súbor
  zavrie. Toto potvrdzuje skutočný debug logging mechanizmus, nie iba pasívny reťazec.
- `FUN_1018_2f32` sa pokúša načítať `dstopen.img`; pri úspechu vykoná grafické/paletové
  operácie a čaká približne 2000 časových jednotiek. `FUN_1018_2f5c` túto rutinu volá
  pri úvodnej vetve programu. Súbor teda pravdepodobne predstavoval nepovinný úvodný
  splash/opening asset, nie dôkaz ďalšej epizódy.
- `FUN_1018_26de` obnovuje štyri cheat hodnoty z menu štruktúry. Ak kontrolná rutina
  `FUN_1010_c6c4(1)` zlyhá, všetky štyri hodnoty vynuluje a zobrazí hlásenie
  `Cheat modes are only available ...`. Cheat systém je preto reálna runtime funkcia,
  ale je uzamknutý kontrolou režimu/licencie; presnú podmienku ešte treba reverznúť.
- Dispatcher `FUN_1018_2776` má explicitné príkazy `0x11`, `0x12..0x17`, `0x1A..0x21`,
  `0x26..0x28`. Vetvy `0x12..0x14` nastavujú hodnotu 0–2, čo je silný dôkaz iba troch
  používateľských obtiažností. Nie je tu štvrtá menu obtiažnosť.
- Save/load UI iteruje presne desať slotov. Hodnota 10 v tejto vetve je počet save
  slotov, nie počet levelov alebo epizód.
- Vektorový audit potvrdzuje 28-bajtový krok záznamu (`+0x1C`), štyri triedené zoznamy
  s limitom 333 prvkov (`0x14D`) a hlavný limit 1000 prvkov. Štyri VECLIST skupiny sú
  rozdelené podľa byte poľa na offsete `+7` s hodnotami 0, 1, 2, 3 a každá sa triedi
  samostatne; nejde o jediný spoločný 333-prvkový zoznam.

### Function-candidate census

`NITE3W_function_candidates.csv` obsahuje 688 kandidátov. Z nich 367 má nula priamych
XREF a 321 aspoň jeden priamy XREF. Nulový XREF zatiaľ neznamená dead code: množina
obsahuje entrypointy, callbacky, jump-table ciele a funkcie volané nepriamo. Ďalší krok
musí každý z 367 záznamov zaradiť do `indirect callback / exported entry / orphan /
false-positive / confirmed dead`.

### Episode 4/5 a hidden difficulty — aktuálny dôkaz

V tomto prechode sa nenašiel nový reťazec, dispatcher ani menu príkaz pre Episode 4,
Episode 5 alebo štvrtú obtiažnosť. Tento výsledok ešte nie je absolútny dôkaz
neexistencie: zostáva overiť hardcoded bounds v level-loaderi, menu resource dáta,
všetky nepriame dispatch tabuľky a DOS buildy. `dstopen.img` je samostatná stopa po
chýbajúcom úvodnom obrázku a nemá zatiaľ žiadnu väzbu na ďalšiu epizódu.

## Druhý auditný prechod — limity, cheat gate a zero-XREF (2026-09-22)

### Episode/level model

- `DAT_1048_7e52` je episode number používané explicitne s hodnotami 1, 2 a 3.
- `DAT_1048_7e54` je zero-based level index. Finálne a špeciálne vetvy porovnávajú
  hodnoty 0, 1, 6, 8 a 9; hodnota 9 zodpovedá desiatemu levelu.
- Hudobná/progresová tabuľka sa indexuje výrazom
  `level + episode * 10 + 0x1FA`. Toto priamo potvrdzuje bloky po desať levelov.
- Episode-specific event dispatcher má vetvy pre `episode == 1`, `2`, `3`; epizóda 4
  ani všeobecná vetva pre `episode > 3` v tomto dispatcheri nie je.
- Jedna efektová rutina sa vykoná, ak episode nie je 2 a zároveň nejde o Episode 3
  po desiatom leveli. Táto podmienka nie je dôkaz E4: skôr chráni špecifický efekt
  pred E2 a koncom E3.

**Priebežný záver:** engine jednoznačne pracuje s tromi blokmi po desať levelov.
Zatiaľ sa nenašla dosiahnuteľná Episode 4/5. Definitívny dôkaz ešte vyžaduje zmerať
skutočnú dĺžku tabuľky pri `0x1FA` a overiť bounds check v loaderi.

### Cheat gate spresnený

`FUN_1010_c6c4(1)` nevyhodnocuje priamo obtiažnosť. Vracia nenulový pointer iba vtedy,
keď byte `DAT_1048_38f1` nie je nula. Cheat menu potom:

1. načíta štyri hodnoty z menu štruktúry,
2. zavolá `FUN_1010_c6c4(1)`,
3. pri nenulovom výsledku cheaty ponechá a zatvorí menu,
4. pri nulovom výsledku všetky štyri hodnoty vynuluje a zobrazí zákazové hlásenie.

Inicializačná vetva `FUN_1010_c6c4(0)` načíta a kontroluje 54-bajtový blok pri
`0x38EE`; gate byte leží v tomto bloku na `+3`. Je teda pravdepodobnejšie, že ide o
build/registration/distribution flag než o difficulty flag. Presný názov a pôvod bloku
ostáva `PARTIAL`, kým sa nezistí názov načítaného súboru a validácia 54 bajtov.

### Zero-XREF rozdelenie

| Segment | Kandidáti | Zero direct-XREF | S XREF | Zero podiel |
|---:|---:|---:|---:|---:|
| 1 | 260 | 136 | 124 | 52,3 % |
| 2 | 184 | 141 | 43 | 76,6 % |
| 3 | 165 | 45 | 120 | 27,3 % |
| 4 | 79 | 45 | 34 | 57,0 % |
| **Spolu** | **688** | **367** | **321** | **53,3 %** |

Segment 2 má extrémne veľa zero-XREF kandidátov a pravdepodobne obsahuje veľký podiel
runtime/library kódu alebo chybných hraníc funkcií. V segmente 4 tvorí 28 z 45
zero-XREF kandidátov hustý zhluk `4:54F7–4:563B`; krátke, tesne susediace adresy sú
silný znak dát/jump-table omylom označených ako funkcie. Týchto 28 sa nesmie počítať
ako potvrdený dead code bez disassembly validácie.

### Kandidáti na reálne pridané subsystémy po 1.3

Sekvenčné párovanie funkcií a nové reťazce ukazujú tri silné skupiny zmien:

- podpora `dstopen.img` a úvodnej obrazovky;
- formátovaný logger do `debug.txt` vrátane novej variadickej write rutiny;
- rozšírená enumerácia a diagnostika MIDI zariadení (`SeqID`, `MOD_SQSYNTH`,
  `MOD_FMSYNTH`, `MOD_SYNTH`, `numseq`).

Comparator vektorov a časť posunutých funkcií zatiaľ nie sú označené ako nové — môžu
byť iba staré rutiny, ktoré Ghidra v 1.3 nerozpoznala alebo pomenovala na inom offsete.

## Tretí auditný prechod — guard state machine, combat a score (2026-09-22)

Zdroj: priame vetvy `FUN_1010_7ab2`, `FUN_1010_8006`, `FUN_1010_8054`,
`FUN_1010_9e62`, `FUN_1010_9ef4`, `FUN_1010_a13c` vo Win16 1.8 exporte.

### Guard runtime record — potvrdený stride a nové polia

`FUN_1010_8006` iteruje guard array krokom `0x1A`, teda **26 bajtov**. Každý guard
odkazuje cez `guard+0x08` na 28-bajtový object/world record (`index * 0x1C + 0x6D66`).

| Guard offset | Priamo pozorované použitie | Stav |
|---:|---|---|
| `+0x00/+0x01` | začiatok a rozsah animačných frame ID | PARTIAL |
| `+0x06` | všeobecný state timer/countdown | CONFIRMED |
| `+0x08` | index 28 B world/object recordu | CONFIRMED |
| `+0x0A` | behavior/strategy mode | CONFIRMED |
| `+0x0B` | aktuálny AI/state kód | CONFIRMED |
| `+0x0C` | návratový/ďalší state po animácii alebo timeri | CONFIRMED |
| `+0x10` | HP/strength; znižuje sa o weapon damage | CONFIRMED |
| `+0x11` | smer/orientácia použitá pri pohybe a projektiloch | PARTIAL |
| `+0x12` | po zásahu sa nastavuje na 8; pain/invulnerability cooldown | PARTIAL |
| `+0x13/+0x14` | podpísané X/Y offsety pri scriptovanom pohybe | CONFIRMED |
| `+0x17` | uložený výsledok direction/visibility testu | PARTIAL |

### AI state dispatcher `guard+0x0B`

Dispatcher explicitne obsluhuje stavy `0x00–0x15`:

| State | Pozorované správanie | Interpretácia |
|---:|---|---|
| `00` | cyklí frame range, odpočítava timer, potom prejde na `+0x0C` | timed animation/idle |
| `01` | iba odpočítava timer, potom state `02` | wait/delay |
| `02` | movement/chase helper, prechod do `03` | chase/move |
| `03` | test útoku/viditeľnosti, prechod do `04` | attack decision |
| `04` | attack helper, hit/projectile helper, následná state voľba | attack |
| `05` | samostatný movement/behavior handler | special move |
| `06` | pohyb + countdown, návrat do `03` | timed chase |
| `07/08` | reacquire/test, strategy vetva; môžu spustiť state `13` | search/script decision |
| `09` | špeciálna transform/spawn vetva; môže meniť world-object state | transform/script |
| `0A/0B` | bez samostatného case handlera | terminal/inactive candidates |
| `0C/0D` | spoločný movement helper s parametrom 0 | passive/script move |
| `0E/0F/10` | globálne prepínaný cyklus cez flag `DAT_1048_51A5` | toggled scripted cycle |
| `11` | timer, nový smer, nulovanie offsetov a návrat do `07` | reacquire/reset |
| `12` | animácia + znižovanie lokálneho efektu, návrat do uloženého state | pain/recovery |
| `13` | samostatný offsetový/scriptovaný pohyb | scripted displacement |
| `14` | dlhší countdown; pod 96 tickov volá pohybový handler | timed special/death prelude |
| `15` | postup animačnými framami, potom návrat do `+0x0C` | pain/hit animation a recovery |

Názvy pri `PARTIAL` sú behaviorálne interpretácie; číselné stavy a prechody sú
potvrdené priamo switchom.

### Presný difficulty scaling combat systému

Interná difficulty hodnota používaná bojovými funkciami je `0=easy`, `1=medium`,
`2=hard`.

- Weapon damage do guarda (`FUN_1010_9ef4`):
  - easy: výsledok `×2`;
  - medium: `×1`;
  - hard: výsledok `÷2`;
  - výsledok sa saturuje na maximum 255 za jeden zásah.
- Damage guarda do hráča (`FUN_1010_a13c`):
  - easy: výsledok `÷2`;
  - medium: `×1`;
  - hard: výsledok `×2`.
- Enemy damage navyše závisí od vzdialenosti: základ je približne
  `100 / distance`, s class-specific RNG alebo posunmi.

Tým je potvrdené, že obtiažnosť nemení iba počet nepriateľov alebo ich útok. Súčasne
mení obe strany combat rovnice: na hard hráč spôsobí polovicu damage a dostane
dvojnásobok; oproti easy preto môže byť pomer účinnosti až osemnásobne horší.

### Presná class→score funkcia

`FUN_1010_9e62` sa volá pri smrti guarda a výsledok sa pripočíta do 32-bit score
`DAT_1048_4C16`. Ide teda o score, nie HP:

| Enemy class | Score |
|---:|---:|
| `08`, `1A` | 25 |
| `09` | 75 |
| `0A`, `20` | 50 |
| `0B`, `0F`, `10`, `17`, `1B`, `1C` | 100 |
| `0C`, `1D`, `1E` | 250 |
| `0D`, `12`, `13` | 150 |
| `0E`, `14`, `18`, `1F` | 200 |
| `15` | **−1000** |
| `16` | **1000** |
| ostatné/default | 0 |

To definitívne vyvracia hypotézu, že Demon musí mať score 0: class `1D` dostáva
**250 bodov**. Class `20`, predtým podozrivá z nepoužitého obsahu, má explicitne
**50 bodov**. Záporných −1000 pre class `15` silno označuje chránenú/nepriateľsky
nezamýšľanú postavu; class `16` je naopak vysoko hodnotný boss alebo špeciálny cieľ.

### Weapon immunity/weakness dispatcher — nový dôkaz

`FUN_1010_9ef4` vetví podľa enemy class `0x0C–0x1F` a aktívnej zbrane
`DAT_1048_4C23`. Niektoré kombinácie vracajú nulu, iné delia základný damage o
`2`, `4`, `8`, `16` alebo `256`; ide o skutočnú class-specific resistance/immunity
matricu. Class `15` vždy spúšťa textovú/special vetvu a nulový damage, class `19`
má nulový damage, a class `16` má osobitné správanie podľa epizódy. Úplné pomenovanie
zbraní k hodnotám `DAT_1048_4C23` je ďalší krok na zostavenie presnej tabuľky
`weapon × enemy × difficulty`.

## Štvrtý auditný prechod — zbraňové ID, munícia a resistance matrix (2026-09-22)

Zdroj: priame vetvy `FUN_1010_9ef4`, `FUN_1010_a8ce`, `FUN_1010_a932`,
`FUN_1010_aa38`, `FUN_1010_b4e6` a pickup dispatcher `FUN_1010_ceb2`.

### Potvrdená interná architektúra zbraní

- Aktívna zbraň `DAT_1048_4C23` má ID `0..3`; `0xFF` znamená, že nie je vybratá
  žiadna zbraň.
- Ownership mask je `DAT_1048_4C2A`; bit `1 << weapon_id` povoľuje výber.
- Pickup class `0x36` nastaví príslušný ownership bit, vyberie zbraň a doplní
  jej štartovaciu muníciu na 50.
- Výber zbrane `2` nastavuje odlišný runtime mode (`DAT_1048_4C26=1`); zbrane
  `0`, `1` a `3` používajú mode `2`.
- Existujú iba **tri počítadlá munície pre štyri zbrane**:

| Weapon ID | Ammo global | HUD update | Spotreba na výstrel |
|---:|---|---:|---:|
| `0` | `DAT_1048_4C20` | `8` | 1 |
| `1` | `DAT_1048_4C44` | `9` | 1 |
| `2` | `DAT_1048_4C1F` | `7` | 1 |
| `3` | `DAT_1048_4C20` | `8` | 1 |

Zbrane `0` a `3` teda potvrdene zdieľajú ten istý ammo pool. Bežný ammo pickup
pridáva 20 (s hornou hranicou kontrolovanou proti 100); weapon pickup nastaví
príslušný pool na 50. Kombinácia weapon databázy, zdieľaného plasma ammo
poolu a kvalitatívnych resistancií umožňuje priradenie `W0=Single Plasma`,
`W1=Wand`, `W2=Silver Pistol`, `W3=Multi Plasma`. Pomenovanie je potvrdené
krížovou zhodou zdrojov, hoci textové názvy nie sú uložené pri switchi v EXE.

### Presná resistance/immunity matrix

Nasledujúca tabuľka udáva násobiteľ **pred** difficulty scalingom. `1/256`
je prakticky extrémna rezistencia, `0` je imunita. Triedy mimo explicitného switchu
vrátane `08–0B` a `20` používajú základný damage `1×`.

| GUARD class / názov | W0 | W1 | W2 | W3 |
|---|---:|---:|---:|---:|
| `0C` Mrs H. | 1/8 | 1/8 | 1/8 | 1/8 |
| `0D` Zelda | 1/8 | 1/2 | 1/8 | 1/8 |
| `0E` Vampira | 1/8 | 1/8 | 1/2 | 1/8 |
| `0F` Baddie #1 | 1/256 | 1/2 | 1/256 | 1/256 |
| `10` Baddie #2 | 1/256 | 1/2 | 1/256 | 1/256 |
| `11` Dracula | 1/8 | 1/8 | 1/2 | 1/8 |
| `12` Cemetery Gargoyle | 1/4 | 1/4 | 1/4 | 1/4 |
| `13` Garden Gargoyle | 1/4 | 1/4 | 1/4 | 1/4 |
| `14` Dracula-Bat forma | 1/8 | 1/8 | 1/2 | 1/8 |
| `15` Penelope | 0 | 0 | 0 | 0 |
| `17` Tall slim robot | 1/4 | 1/256 | 1/4 | 1/4 |
| `18` Trashcan robot | 1/8 | 1/256 | 1/16 | 1/8 |
| `19` Cannon | 0 | 0 | 0 | 0 |
| `1A` Ghost | 0 | 1/2 | 0 | 0 |
| `1B` Goldie | 1/2 | 1/2 | 1/2 | 1/2 |
| `1C` Greenie | 1/2 | 1/2 | 1/2 | 1/2 |
| `1D` Demon boss | 1/8 | 1/8 | 1/8 | 1/8 |
| `1E` Alien #1 | 1/8 | 0 | 1/8 | 1/8 |
| `1F` Alien #2 | 1/4 | 0 | 1/4 | 1/4 |

Class `15` navyše pri zásahu volá osobitnú textovú vetvu; reťazec v EXE je
`Look over there! It's Penelope ...`. Tým je imunita Penelope a záporné skóre
vzájomne konzistentné. Class `19` (Cannon) je tiež absolútne nezraniteľná bežnou
zbraňovou damage rutinou.

Class `16` (Dr. Hamerstein) nepoužíva bežný násobiteľ. Mimo hodnoty epizódy
`DAT_1048_7E52 == 3` dostane nulový damage; pri hodnote `3` rutina nastaví pevný
základ damage `3` a až potom aplikuje difficulty scaling. Presný príbehový význam
hodnoty epizódy zostáva označený `PARTIAL`, ale podmienka a damage sú `CONFIRMED`.

## Piaty auditný prechod — HP inicializácia, Dracula→Bat a GUARD25 (2026-09-22)

Zdroj: `FUN_1010_83da`, `FUN_1010_a040`, `FUN_1010_af7e`,
`FUN_1010_b536/b5f2/b7b4` a fatal vetva `FUN_1010_8054`.

### Počiatočné HP guardov je 255

Pri vytvorení každého 26-bajtového guard recordu zapisuje `FUN_1010_83da`
priamo `guard+0x10 = 0xFF`. Všetky normálne vytvorené guardy teda začínajú
na **255 HP**; nejde o class-specific HP tabuľku. Rozdielna praktická odolnosť
vzniká cez resistance matrix, vzdialenosť/RNG a difficulty scaling.

Difficulty sa v init path nepoužíva, takže počiatočné HP nemení. Mení
výsledný damage a tým nepriamo počet potrebných zásahov.

### GUARD13 / class `0x14` je Dracula-Bat forma

Pri fatálnom zásahu Draculu (`object class 0x11`) special handler:

- zmení `object+0x06` z `0x11` na **`0x14`**;
- obnoví `guard+0x10 = 0xFF` (nových 255 HP);
- nastaví `state=8`, `next_state=2`, timer `1`;
- nastaví objektovú frame/sequence hodnotu `0x23`;
- spustí sound/event `0x22`.

GUARD13 je teda definitívne interná transformovaná **Dracula-Bat** forma,
nie samostatne umiestňovaný nepriateľ. Normal Bat je class `0x08`, Dracula-Bat
je class `0x14`. Obe používajú death sound `0x23` a rovnaký osobitný animačný
rozsah.

Skóre sa počíta pod aktuálnou class: humanoidná Dracula fáza (`0x11`) dáva
`0`, finálne zabitie Dracula-Bat (`0x14`) dáva **200 bodov**. Staršia hypotéza,
že výsledný Bat dáva 25 bodov ako normal Bat, je vyvrátená.

Dracula pozostáva z dvoch plných 255-HP fáz: efektívne **510 HP pred
resistanciami**. Druhá fáza má multiplier `1/2` pre Silver Pistol a `1/8` pre
ostatné tri zbrane.

### GUARD25 / class `0x20`: fallback profil

Class `0x20` nemá osobitnú vetvu v AI inicializácii, resistance switchi ani
troch sound dispatcheroch. Pri vytvorení cez bežný guard path dostane:

| Vlastnosť | Hodnota |
|---|---:|
| počiatočné HP | 255 |
| počiatočný state / next state | `7 / 2` |
| strategy | `0` |
| weapon multiplier | `1×` pre W0–W3 |
| score | 50 |
| explicit attack/death/alert SND mapping | žiadny; dispatcher použije ID `0` |

GUARD25 nie je plnohodnotne naladený nepriateľ: má generickú AI, HP, damage
a score, ale chýbajú class-specific zvuky, resistance aj potvrdený placement.
Najlepšia klasifikácia je **nedokončený alebo odstránený guard slot**, nie
skrytý boss. Otvorené zostáva spojenie s orphan IMG/seqdef grafikou.

## Nasledujúci audit

Najvyššiu prioritu má sledovanie prístupov k počítadlám a násobiteľom veľkosti záznamov:

- objekt: čítač `0x7E58`, báza `0x6D66`, krok potvrdený na 28 B;
- guard: čítač `0x7E5E`, báza `0x93AE`, krok potvrdený na 26 B;
- doors/panels/pushes: inicializačné rutiny v rozsahu približne `3:12E8–18xx`;
- renderer: čítač `0x5E7E`, báza `0x5E88`, krok potvrdený na 20 B;
- vectors: funkcie okolo `4:34E1`, `4:3919`, `4:4073`.

Každé ďalšie pomenovanie poľa má zostať `CONFIRMED`, `PARTIAL` alebo `INFERRED`; samotná číselná deliteľnosť bloku nestačí na označenie `CONFIRMED`.

## Siedmy auditný prechod — presný enemy damage a runtime recordy (2026-09-22)

Zdroj: priama 16-bit disassemblácia Win16 NE segmentu s damage dispatcherom,
inicializáciou guardov a inicializáciou/runtime slučkami door, panel a push polí.

### Enemy → player damage: presná class-specific tabuľka

Damage rutina najprv vypočíta základ podľa vzdialenosti:

```text
base = distance > 0 ? floor(100 / distance) : 100
```

Následne switch pre classy `0x08–0x1E` použije túto úpravu. Classy `0x1F` a
`0x20` ležia mimo switchu a idú cez default `base / 2`.

| Enemy class | Damage pred difficulty scalingom |
|---:|---:|
| `08` | `random() & 7` = 0–7 |
| `09`, `0A` | `random() & 15` = 0–15 |
| `0B` | `floor(base / 4)` |
| `0C`, `1D`, `1E` | `base` |
| `0D–10`, `15`, `17`, `18`, `1A–1C`, `1F`, `20` | `floor(base / 2)` |
| `11–14` | `random() & 31` = 0–31 |
| `16` | 33, ak `episode != 3` a `DAT_1048_51A6 == 0`; inak 100 |
| `19` | 100 |

Posledný krok je potvrdený globálny difficulty multiplier:

- Easy (`0`): `floor(damage / 2)`;
- Medium (`1`): nezmenený damage;
- Hard (`2`): `damage * 2`.

Tým je class-specific enemy damage dispatcher numericky dekódovaný. Otvorené
zostáva pomenovanie konkrétneho attack/projectile typu, ktorý túto rutinu volá,
a oddelené environmentálne hazardy (large/medium/small fire).

### Úplný súbor priamych writerov guard HP

Pri statickom prechode priamych zápisov na `guard+0x10` boli potvrdené tieto
combat writery:

| Operácia | Význam |
|---|---|
| `guard+0x10 = 0xFF` v create path | každý nový bežný guard začína na 255 HP |
| `guard+0x10 -= scaled_weapon_damage` | jediný priamy bežný weapon-damage zápis |
| `guard+0x10 = 0` vo fatal path | saturácia smrti; byte HP sa nepretečie pod nulu |
| `guard+0x10 = 0xFF` v Dracula transform path | Dracula-Bat dostane nových 255 HP |

Nebola nájdená class-specific inicializačná HP tabuľka. Na absolútnych 100 %
zostáva vylúčiť iba nepriame obnovenie cez load/save alebo script, ktoré nemusí
použiť priamy field-offset zápis.

### Door, panel a push runtime polia

Kapacity, stride a pretečenia sú priamo potvrdené:

| Pole | Báza | Kapacita | Stride | Veľkosť |
|---|---:|---:|---:|---:|
| doors | `0x9DD6` | 64 | 22 B (`0x16`) | 1408 B (`0x580`) |
| panels | `0xA356` | 32 | 22 B (`0x16`) | 704 B (`0x2C0`) |
| pushes | `0xA616` | 12 | 6 B | 72 B (`0x48`) |

Door inicializácia potvrdzuje:

- `+0x00` a `+0x04`: dva far pointery na obe strany/objekty dverí;
- `+0x08`: 32-bit map-cell reference používaná lookupom;
- `+0x0C`: počiatočný stav `1`;
- `+0x10/+0x12`: runtime X/Y pozícia vybraná podľa orientácie strany;
- `+0x14`: počiatočný orientačný/runtime byte `0`.

Door runtime state machine je už číselne potvrdený:

| `door+0x0C` | Význam |
|---:|---|
| `0` | otvorené dvere / čakanie na auto-close |
| `1` | zatvorené, neaktívne dvere |
| `2` | otváranie |
| `3` | zatváranie |

- pohyb oboch strán dverí prebieha krokom **2 pozičné jednotky na update**;
- po skončení state `2` prejde do `0`, po skončení state `3` do `1`;
- po dokončení pohybu sa `+0x0E` nastaví na **32**, teda ide o auto-close
  countdown;
- pri pokuse o zatvorenie sa countdown obnoví na **4**, ak je door cell obsadená
  (`cell+1 != 0`) alebo sa zhoduje s aktuálnou player cell;
- objekty class `0x3B/0x3C` obchádzajú bežnú auto-close vetvu;
- orientácia posuvu sa odvodzuje z object flagu `0x20` a side/orientation poľa;
- prechod do zatvárania nastaví solid/collision bit `0x01` na oboch stranách,
  úplné otvorenie ho z oboch strán odstráni;
- `+0x14` funguje ako jednorazová sound/runtime brána; pri auto-close môže
  spustiť event/SND `0x26` a následne sa nuluje.

Panel inicializácia potvrdzuje:

- `+0x00`, `+0x04`, `+0x08`, `+0x0C`: až štyri far pointery priradené podľa
  side/index hodnoty `0–3`;
- `+0x10`: 32-bit map-cell reference;
- `+0x14`: počiatočný stav `1`.

Panel state `2` posúva súradnicové polia priradených object pointerov vždy o
**2 jednotky na update** smerom k cieľovým hodnotám. Kým sa pohybuje aspoň jedna
zo štyroch strán, state zostáva `2`. Po dokončení sa vyhľadajú panely zdieľajúce
rovnaký object pointer, odstráni sa collision bit `0x01`, v map-cell reference
sa vynulujú oba stavové bajty a `panel+0x14` sa vráti na `0`.

Priama USE vetva potvrdzuje kompletné panelové stavy:

| `panel+0x14` | Význam |
|---:|---|
| `0` | dokončený/odstránený panel |
| `1` | inicializovaný panel čakajúci na aktiváciu |
| `2` | aktivovaný panel v pohybe |

Object class `3` v USE dispatcheri vyhľadá panel podľa 32-bit map-cell reference,
nastaví state `2`, spustí event/SND `0x27` a pripraví cieľové súradnice jednotlivých
strán posunom `+1/-1`. Iné priame writery panel state neboli nájdené.

Push inicializácia potvrdzuje 6-bajtový record:

- `+0x00`: index 28-bajtového world/object recordu;
- `+0x02`: podpísaný X krok načítaný z aktuálneho direction vektora hráča;
- `+0x03`: podpísaný Y krok načítaný z aktuálneho direction vektora hráča;
- `+0x04`: počet zostávajúcich úspešných movement krokov; aktivácia nastavuje `8`,
  runtime po každom úspešnom kroku znižuje až na `0`;
- `+0x05`: padding/reserved; v runtime kóde nemá priameho čitateľa ani writera.

Push aktivácia je odmietnutá, ak je record už aktívny alebo cieľový class flag
obsahuje blokujúci bit `0x02`. Runtime vypočíta cieľovú map cell z nových X/Y,
kontroluje blokujúce class bity maskou `0x06`, pri prechode medzi bunkami prenesie
occupancy byte `cell+1` a starú bunku vynuluje. Potom aktualizuje world-object
`+0x10/+0x12` (X/Y), jeho 32-bit cell reference `+0x0C` a zavolá movement/collision
commit helper. Pri blokovaní sa countdown nezníži, takže objekt zostane aktívny
a ďalší update pohyb skúsi znova.

Tieto výsledky opravujú staršiu neistotu: 72-bajtový save/runtime blok presne
zodpovedá `12 × 6 B` push array.

Pracovný stav po tomto prechode:

| Uzatvárateľná oblasť | Odhad pokrytia |
|---|---:|
| enemy HP lifecycle | **98 %** |
| weapon resistance/immunity | **98 %** |
| enemy → player damage dispatcher | **95 %** |
| door record + základný runtime | **90 %** |
| panel record + movement completion | **95 %** |
| push record + movement runtime | **95 %** |

Percentá vyjadrujú behaviorálne pokrytie konkrétneho podsystému, nie percento
celého EXE.

## Wall-class audit — prvé priame výsledky (2026-09-21)

Zdroj: komentáre priamo v plných tabuľkách `WALLS.1/.2/.3` a diagnostické reťazce Win16 V1.10. Tieto komentáre sú výrazne silnejší dôkaz než odhad podľa názvu triedy.

### CONFIRMED z dátových tabuliek

| Trieda | Význam |
|---|---|
| `WARP_L1..L4` | priechod/dvere zamknuté farebným kľúčom: L1 red, L2 green, L3 blue, L4 yellow; nejde o všeobecný „locked teleport“ |
| `WARP_1..8` | párované vertikálne presuny medzi konkrétnymi schodmi/dumbwaiter bodmi; číslo odlišuje spojovaciu dvojicu/skupinu |
| `WARP_E1`, `WARP_E2` | výťah 1 a 2; viac položiek rovnakej triedy predstavuje jednotlivé poschodia |
| `WARP_S1` | swirling mirror v Bedroom 4 |
| `WARP_S2` | broken mirror / Other Side mirror |
| `DOORV`, `DOORH` | dve orientácie tej istej posuvnej dverovej grafiky |
| `DOORVL/HL`, `VL2/HL2`, `VL3/HL3` | orientácie zamknutých dverí; suffix 2/3 odlišuje grafickú sadu/prostredie (block/HQ), nie úroveň zámku |
| `DOORVI/HI` | dve orientácie dverí Transportation Chamber; písmeno `I` zatiaľ nemá potvrdený slovný rozpis |
| `DOORVR/HR` | remote-controlled door |
| `DOORVC/HC` | curtain door |
| `JAMB` | zárubňa dverí, priamo potvrdené popismi |
| `CONTROL` | očíslovaný control panel; E2 obsahuje ID #1 a #2 |
| `LEVEL_UP` | gateway to next level |
| `LEVEL_UP2` | gateway to skip a level, nie iba neurčitý alternatívny exit |
| `WALL_EX1` | explodable wall/door/hedge/target |
| `WALL_EX2` | tri varianty exploding door v E3 |
| `ONE_SHOT` | disappearing gargoyle (Garden/Cemetery); správny názov je `ONE_SHOT`, nie `ONE_SHOOT` |
| `SPECIAL1` | dve konkrétne E1 udalosti: kitchen fuse box a morphing chalkboard |
| `ACTIONSPOT` | bod pre dancing guards v leveli 9 |
| `TRIGGER1/2` | neviditeľné trigger markery |
| `RETREAT`, `TURN` | osemsmerové AI navigačné markery; `RETREAT` má aj dead-end variant |
| `SAFESPOT` | markery kombinácií sejfu; E1 komentáre uvádzajú `333`, `01532`, `080993`, `372535` |
| `FLEE` | flee marker pre dvere |

### PARTIAL / ešte treba runtime XREF

- `REVWALL`: popisy ukazujú najmä pravý/ľavý panel a prechod medzi materiálmi. Je to pravdepodobne reverzne alebo jednostranne mapovaná stena, nie reverzná push-wall mechanika.
- `ONE_SHOT`: dáta potvrdzujú miznúcu gargoylu, ale ešte nie spúšťač. Názov môže znamenať jednorazovú aktiváciu; bez XREF vetvy `bullet-hit wall` nemožno tvrdiť, že musí ísť o jeden výstrel.
- `SPECIAL1`: dátové použitia sú potvrdené, spoločný runtime mechanizmus (use/touch/shot/script) ešte nie.
- `WARP_S1/S2`: cieľ Other Side je zrejmý z popisu a textov EXE (`The mirror crack'd`, podmienka štyroch pentagramov), presná podmienková vetva sa ešte musí priradiť ku class ID.

### Súvisiace reťazce v EXE

Win16 EXE priamo obsahuje: `Exploding wall not in map`, názvy štyroch kľúčov, hlášky fuse-boxu, portálu Other Side a prasknutého zrkadla, kombinácie sejfu, menu poschodí 1–10 a príkazy `Open remote doors` / `Close remote doors`. To nezávisle korešponduje s triedami v `WALLS.x`.

### Opravy predchádzajúcich hypotéz

1. `WARP_Lx` je farebne zamknutý priechod/dverová stena, nie všeobecný teleport vyžadujúci ľubovoľnú podmienku.
2. `DOORVL2/VL3` nie sú vyššie stupne zámku; tabuľka ukazuje rovnaké štyri farby kľúčov v odlišných sadách dverí.
3. `LEVEL_UP2` explicitne preskakuje level.
4. `ONE_SHOT` sú miznúce gargoyly; spojenie so spawnom Cemetery Guard zatiaľ nie je dokázané.

## Guard AI, damage a skóre — 2. etapa

### Potvrdená damage/death vetva

Funkcia približne pri `3:80F8` vypočíta damage a porovná ho s `guard+0x10`. Pole `+0x10` je preto potvrdené ako aktuálna sila/HP:

- ak `damage >= HP`, zapíše `HP=0`, spustí death vetvu a pripočíta skóre;
- ak `0 < damage < HP`, vykoná `guard+0x10 -= damage`;
- po nefatálnom zásahu zapisuje `guard+0x12 = 8`;
- bežná pain reakcia uloží pôvodný stav do `next_state` a nastaví `state=0x15`;
- handler `0x15` po dokončení animácie obnoví `state=next_state`.

Globálne skóre je 32-bitové na `0x4C16:0x4C18` (`add` + `adc`).

### Potvrdený state dispatcher

Dispatcher pri `3:7B55` povoľuje stavy `0x00–0x15`:

| State | Handler | Zistené správanie |
|---:|---:|---|
| `00` | `7BA2` | animácia/timer; po vypršaní `state=next_state` |
| `01` | `7BE0` | odpočítanie timeru, potom `02` |
| `02` | `7BFA` | aktívna AI/animácia so zvukom typu 3 |
| `03` | `7C3C` | detekčná/prechodová vetva |
| `04` | `7C86` | alternatívna detekčná/útoková vetva |
| `05` | `7CE4` | pomocná prechodová vetva |
| `06` | `7CEC` | pohyb + timer; potom `03` |
| `07` | `7D2A` | aktívna AI; strategy 3 má osobitnú vetvu |
| `08` | `7D7E` | pohyb/AI; môže prejsť do `02` |
| `09` | `7DEC` | špeciálna/kolízna akcia |
| `0A`, `0B` | `80A4` | bez lokálnej akcie |
| `0C`, `0D` | `7E54` | spoločný handler |
| `0E` | `7E6C` | podmienený prechod do `0F` |
| `0F` | `7E9E` | timer/akcia; prechod do `10` alebo `0E` |
| `10` | `7F26` | timer; následne návrat do `0F` |
| `11` | `7F8E` | pohyb + timer; potom `strategy=0`, `state=07` |
| `12` | `7FEE` | čaká na timer/animáciu, potom `state=next_state` |
| `13` | `8038` | pomocná prechodová funkcia |
| `14` | `804A` | dlhý timer a periodická akcia |
| `15` | `807E` | potvrdená pain/hit animácia; návrat do `next_state` |

Definitívne názvy stavov `02–14` zostávajú otvorené, kým sa nepriradia animácie a zvuky. Pole `guard+0x0A` je potvrdený behavior/strategy selector: hodnoty `3` a `5` menia reakciu na zásah.

### Skóre podľa GUARD triedy

Funkcia pri `3:9F10` používa internú triedu z `object+0x06`:

| Typ | GUARD trieda / názov | Skóre |
|---:|---|---:|
| `08` | GUARD1 Bat | 25 |
| `09` | GUARD2 Frankenstein | 75 |
| `0A` | GUARD3 Mummy | 50 |
| `0B` | GUARD4 Skeleton | 100 |
| `0C` | GUARD5 Mrs H. | 250 |
| `0D` | GUARD6 Zelda | 150 |
| `0E` | GUARD7 Vampira | 200 |
| `0F` | GUARD8 Baddie #1 | 100 |
| `10` | GUARD9 Baddie #2 | 100 |
| `11` | GUARD10 Dracula | 0 |
| `12` | GUARD11 Cemetery Gargoyle | 150 |
| `13` | GUARD12 Garden Gargoyle | 150 |
| `14` | GUARD13 Dracula-Bat transformovaná forma | 200 |
| `15` | GUARD14 Penelope | **−1000** |
| `16` | GUARD15 Dr. Hamerstein | **1000** |
| `17` | GUARD16 Tall slim robot | 100 |
| `18` | GUARD17 Trashcan robot | 200 |
| `19` | GUARD18 Cannon | 0 |
| `1A` | GUARD19 Ghost | 25 |
| `1B` | GUARD20 Goldie | 100 |
| `1C` | GUARD21 Greenie | 100 |
| `1D` | GUARD22 Demon boss | 250 |
| `1E` | GUARD23 Alien #1 | 250 |
| `1F` | GUARD24 Alien #2 | 200 |
| `20` | GUARD25, neznáma/nepoužitá | 50 |

GUARD26 Dancers neleží v rozsahu switchu `0x08–0x20`, takže score funkcia preň vracia predvolenú nulu. Záporné skóre Penelope podporuje interpretáciu chránenej alebo neutrálnej postavy.

## Šiesty auditný prechod — MAP hlavička, editor descriptors a IMG frame bloky (2026-09-22)

Zdroj: priame binárne porovnanie originálnych `MAP.1/.2/.3`, `IMG.1/.2/.3`
a textových editorových definícií `WALLS.1/.2/.3` a `OBJECTS.1/.2/.3`.

### MAP formát je presne uzavretý

Veľkosť každého súboru sedí bez zvyšku na:

```text
MAP size = 514 + level_count * 8192
```

| Offset | Veľkosť | Význam | Stav |
|---:|---:|---|---|
| `0x000` | 2 B | little-endian `level_count` | CONFIRMED |
| `0x002` | 256 B | `wall_class[wall_id]` | CONFIRMED |
| `0x102` | 256 B | `object_class[object_id]` | CONFIRMED |
| `0x202` | `level_count × 8192` | levely 64×64; každá bunka je `wall_id, object_id` | CONFIRMED |

`MAP.1` má count 11 a veľkosť 90 626 B; `MAP.2` a `MAP.3` majú count 10
a veľkosť 82 434 B. Dvojica v bunke nie je packed 16-bit flags. Prvý byte je priamy
index do epizódnej wall tabuľky, druhý priamy index do object tabuľky. Runtime class
sa získa cez lookup v hlavičke. Stabilné príklady: wall `01=WALL`, `02=REVWALL`,
`2E=WALL_EX1`, `31=DOORV`, `32=DOORH`, `44=FLOOR`, `47=TRIGGER1`,
`48=TRIGGER2`; object `02=START`, `08..20=GUARD1..25` s medzerami podľa epizódy,
`28=PUSH`, `2B=DUMB`, `2F=KEY`, `30=IDCARD`, `36=WEAPON`, `3E=UIFOBJ`.

Pri porovnaní všetkých použitých ID s definíciami existuje jediná anomália:
`MAP.2`, level 4 (1-based), bunka `(x=61,y=54)` používa `wall_id=0x37` spolu
s `object_id=0x17` (`Tombstone with flower`). `WALLS.2` položku `0x37` nemá a
`wall_class[0x37]=0`; hodnota sa v celej epizóde vyskytne iba raz. Ide o priamu
anomáliu originálnych dát, nie o neznámy packed flag. Susedia sú prevažne floor 17
(`wall_id=0xD1`) a cemetery wall `0x32/0x34`, takže kandidátom je chybný wall ID,
ale zamýšľaná náhrada zatiaľ nie je potvrdená.

### Druhý stĺpec WALLS/OBJECTS nie je runtime hodnota

Štvorznakové položky ako `1010`, `c070`, `c00k`, `f20t` sú MapEdit kresliace
descriptory:

```text
[primary color][secondary color][graph type][character]
```

Preto môže posledný znak byť aj `k`, `t`, `g`, nie iba hex číslica. `c070/c060`
pri vertikálnych/horizontálnych dverách odlišuje editorový graph type 7/6.
Descriptor sa v `MAP.x` neukladá a nemá v sebe wall timing, key state ani runtime
orientation flags. Predchádzajúca hypotéza, že byte-swapped hodnota predstavuje
resource offset alebo 2-tick timer, je vyvrátená.

### IMG kontajner a počet frame

Prvých 256 little-endian 32-bit položiek `IMG.x` tvorí wall-image offset directory
indexované priamo cez `wall_id`. Všetky jeho nenulové položky ukazujú na platný
offset najmenej `0xBC00`. Oblasť od `0x0400` do prvého obrazového záznamu na
`0xBC00` obsahuje ďalšie resource tabuľky, ale **nie** jednu homogénnu tabuľku
12 032 file-offsetov; ich presný rozpis zostáva otvorený. Wall directory offset
ukazuje na obrazový záznam:

```text
uint8 width;
uint8 height;
uint8 metadata[8];
uint8 pixels[width * height];
```

Základná veľkosť záznamu je teda `10 + width*height`. Viacframe resource obsahuje
niekoľko takýchto záznamov bezprostredne za sebou. To umožňuje priamo potvrdiť počet
obrazov/stavov, ale nie ich časový delay.

| Epizóda / wall ID | Resource | Potvrdené záznamy |
|---|---|---:|
| E1 `0x03/04/05` | sconces / hutch / large picture | 2 každý |
| E1 `0x0E` | fireplace | 8 |
| E1 `0x25`, `0x28` | office desk / sconces | 2 každý |
| E1 `0x54/55` | disappearing cemetery/garden gargoyle | 5 každý |
| E1 `0x56` | morphing chalkboard | 6 |
| E1 `0x57` | swirling mirror | 6 |
| E1 `0x70/71` | curtain door V/H | 4 každý |
| E1 `0x90..93` | dumbwaiter endpoints | 16 každý |
| E1 `0x9F/A0` | level exit / skip-level exit | 5 každý |
| E2 `0x0C` | animated cave torch | 8 |
| E2 `0x2A`, `0x36` | disappearing gargoyles | 5 každý |
| E2 `0x3F/40` | level exit / skip-level exit | 5 každý |
| E2 `0x4E/4F/50` | control panel states | 6 každý |
| E2 `0x51` | plasma core | 6 |
| E2 `0x88/89` | block sliding cell door V/H | 6 každý |
| E2 `0xAC/AD` | remote door #1 V/H | 3 každý |
| E3 `0x12` | fiery skeleton head | 4 |
| E3 `0x1C/1D/1E` | exploding fiery doors | 5 každý |
| E3 `0x20` | animated star field | 6 |
| E3 `0x28..2B` | animated fiery cherub/dog/monkey | 4 každý |
| E3 `0x55` | fireball | 7 |
| E3 `0x69/6A` | level exit / skip-level exit | 5 každý |
| E3 `0x8C/8D/8E` | reused house sconces/hutch/picture | 2 každý |
| E3 `0x95` | reused fireplace | 8 |

Tým sa vysvetľuje veľký počet údajných „2-tikových“ stien: hodnota 2 v tomto
kontexte znamená dva uložené obrazové záznamy/stavy. Sama osebe nehovorí, že každý
trvá dva game ticks. Navyše nie každý viacframe blok musí byť automatická slučka:
`ONE_SHOT`, `SPECIAL1`, dvere, control panely a exits sú stavové/scriptované sekvencie.
Skutočný `frame delay`, loop mód a event/sound hook zostávajú v EXE/seqdef dispatcheri.

Osobitná poznámka: E3 `Swirl 1..6` na wall ID `0x0C..0x11` sú šesť samostatných
wall ID s jedným obrazovým záznamom na ID, nie jeden šesťframe blok. Ak sa v hre
animujú, runtime musí prepínať wall/image ID cez inú sequence tabuľku; časovanie
nemôže pochádzať z ich lokálneho IMG bloku.

## Master register neznámych hodnôt — konsolidácia všetkých dostupných auditov

Revízia porovnala hlavný EXE/unknowns audit, save/libraries report, renderer v2/v3, function-candidate mapu, enemy/weapon databázu a video audity Episode 3. Staršie tvrdenia, ktoré už novší EXE audit vyriešil, sa nepovažujú za otvorené (napríklad veľkosti object/guard recordov alebo približná GAME.PAL).

### P0 — blokuje vernú implementáciu hernej logiky

| Oblasť | Presne neznáme | Najlepší ďalší dôkaz |
|---|---|---|
| wall-class dispatcher | wall flags, hlavný USE dispatch, level exits, dvere/zámky a WARP rodiny sú z veľkej časti uzavreté; otvorené zostávajú názvy tried `03–06`, vnútro niektorých helperov a trigger/control reťazec | class tabuľky všetkých epizód + dynamický test `TRIGGER → CONTROL → remote door` |
| animované steny | počet obrazových záznamov je už merateľný priamo v `IMG.x`; otvorený zostáva `delay v tickoch`, loop/ping-pong/one-shot a runtime väzba na sequence dispatcher | watchpoint na wall timer + XREF image/sequence loadera |
| údajné „2-tikové“ steny | početné hodnoty `2` v dátach sú pri viacerých wall ID potvrdené ako **dva obrazové záznamy/stavy**, nie ako delay 2 ticks; skutočný tick delay stále chýba | watchpoint na timer počas známej dvojframe steny |
| `ONE_SHOT` | presný trigger miznúcej gargoyly: strela, Use, proximity alebo jednorazový script; väzba na GUARD11/12 spawn | bullet-wall XREF + kontrolovaný E1/E2 test |
| `SPECIAL1` | ako class `0x08` rozlišuje fuse box a morphing chalkboard; trigger, stav a finálna textúra | vetvy textov `fused the lights` a wall ID `0x12/0x56` z `WALLS.1` |
| `WARP_S1/S2` | podmienky zrkadiel, pentagram maska, cieľový level/position a spotreba/nespotreba stavu | XREF textov Other Side a `The mirror crack'd` |
| `CONTROL` | význam ID #1/#2, remote-door/cannon command mapping a per-panel stav | menu `Open/Close remote doors`, `Enable/Disable remote cannons` |
| dvere | stride 22 B, kapacita 64, pointery, cell reference, state `0–3`, krok 2, countdown 32/4, auto-close obstruction a collision-bit prechody sú potvrdené; otvorené ostáva priradenie všetkých class-specific eventov a presná jednotka ticku | runtime slučky door array `0x9DD6` |
| panely | stride 22 B, kapacita 32, štyri side pointery, cell reference, kompletné stavy `0/1/2`, USE class `3`, event `0x27`, krok 2, completion/link cleanup a collision/map-cell zmeny sú potvrdené; otvorené sú len presné vizuálne názvy variantov a tick jednotka | runtime slučky panel array `0xA356` |
| pushables | stride 6 B, kapacita 12, X/Y step, countdown 8, reserved `+05`, collision mask `0x06`, occupancy transfer a world/cell commit sú potvrdené; otvorené zostáva presné pomenovanie direction tabuľky a kontrola špeciálnej stair-trap vetvy | movement runtime push array `0xA616` |
| ID-card exit logic | ktorá karta otvára `DOORVI/HI`, či sa karta spotrebúva a ako sa odlišuje Transportation Booth | E2/E3 controlled test + XREF `Red/Yellow ID card` |
| finale E3M10 | trigger → Penelope/Hamerstein → boss death → popup → FLI → score/menu | XREF textov `Look! It's Penelope!`, `You've won!` |

### P1 — AI, damage, zbrane a hazardy

| Oblasť | Presne neznáme |
|---|---|
| guard states `02–14` | definitívne názvy a významy handlerov; animácia/zvuk/prechody ku každému stavu |
| strategy values | úplná tabuľka hodnôt, nielen potvrdené špeciálne správanie 3 a 5 |
| guard record | význam polí `+00..05`, `+0D`, `+0F`, `+11`, `+13`, `+14`, `+17..19` |
| object record | presný význam `+01..03`, `+05`, `+08`, `+0C..13` a zostávajúcich bajtov do `+1B` |
| GUARD25 | GUARD13 je vyriešený ako Dracula-Bat; pri GUARD25 zostáva identita grafiky/seqdef a potvrdenie, či bol odstránený pred vydaním |
| GUARD26 Dancers | samostatný AI/script model mimo score switchu |
| enemy HP | init 255, saturácia smrti na 0, jediný priamy bežný damage writer a Dracula-Bat reset na 255 sú potvrdené; otvorené zostáva vylúčenie nepriamych save/script prepisov |
| enemy damage | class dispatcher, distance formula, RNG rozsahy a difficulty scaling sú numericky potvrdené; otvorené zostáva mapovanie handlerov na konkrétne melee/projectile prezentácie |
| fire hazards | presné damage/tick intervaly pre large/medium/small fire; large je podľa hintov smrteľný, čísla chýbajú |
| projectiles | rýchlosť, lifetime, radius/hit test, owner/friendly-fire a damage tabuľka |
| weapons | ID/názvy, ammo pooly, resistance a difficulty scaling sú potvrdené; otvorené zostávajú cadence/spread/range a presný distance→base-damage výpočet |
| pain field `guard+0x12=8` | či je to invulnerability/hit-stun/pain cooldown a v akých tick jednotkách |
| sight/hearing | FOV, vzdialenosť, line-of-sight, reakcia na streľbu a omnificent bypass |
| door/entity collision | kedy guard blokuje dvere, kedy sa dvere zatvoria a ako sa rieši crush/retreat |

### P1 — renderer a world model

| Oblasť | Presne neznáme |
|---|---|
| `VECLIST[333]` vs. `VEC[1000]` | vlastník, životnosť, transformácia a prečo existujú dve kapacity |
| 28 B vector record | kompletné polia, endpointy, normal/orientation, texture reference a clipping flags |
| 20 B visible-span record | presné polia renderer zoznamu `0x5E88`, depth/orientation a texture interpolation |
| sprite renderer | sorting, occlusion cez wall owner buffer, scale, clipping a limit `Too many objects on screen` |
| transparent/masked steny | curtains, grates a transparent chamber door rendering vs. collision |
| `REVWALL` | presný význam: obrátená strana/UV/orientácia/one-sided transition; push-wall hypotéza je slabá |
| floor/ceiling | či sú iba solid palette fills vo všetkých režimoch alebo existujú alternatívne level parametre |
| `0x7E60` | 16-bit level render/environment parameter uložený v save na `0xD6E5` |
| DOS fullscreen renderer | rozdiely planar VGA vetvy oproti WinG: clipping, palette, timing a parity |

### P1 — MAP/WALLS/OBJECTS a save formáty

| Oblasť | Presne neznáme |
|---|---|
| MAP hlavička/level directory | **VYRIEŠENÉ:** `uint16 level_count`, `wall_class[256]`, `object_class[256]`, potom pevné 8192 B levely; otvorené sú už iba runtime mutácie a význam osobitného 11. bloku v `MAP.1` |
| 2 B map cell | **VYRIEŠENÉ:** interleaved `wall_id:uint8, object_id:uint8`; class sa lookupuje cez dve 256-bajtové tabuľky hlavičky, nejde o bitové pole |
| WALLS druhý štvorznakový stĺpec | **VYRIEŠENÉ:** MapEdit kresliaci descriptor `primary color, secondary color, graph type, character`; nie runtime flags ani animačný timer |
| OBJECTS atribúty | štvorznakový kresliaci descriptor je vyriešený; otvorená zostáva úplná runtime behavior/guard/sequence väzba class ID z MAP hlavičky |
| sequence definitions | formát `seqdef`, frame order, frame duration, sound/event hooks a loop typ |
| save `0x2035`, 94 B | jednotlivé player/global polia |
| save `0xC3E3`, 32 B | auxiliary state list |
| save `0xC403`, 336 B | anonymný runtime blok; nesmie sa zamieňať so 72 B push array |
| save `0xC553`, 8 B | význam bloku |
| save `0xC5A3`, 4096 B | visibility/exploration/state map; presný význam každého bajtu |
| save `0xD5A3`, 64 B | význam bloku |
| save `0xD5E3`, 256 B | lookup/state tabuľka |
| timer rebasing | ktoré absolutné tick hodnoty sa po load upravujú oproti saved tick base |

### P2 — zdroje, audio a UI

| Oblasť | Presne neznáme |
|---|---|
| SND.DAT | úplný adresár/chunk formát, VOC varianty, sample rate/time constant, kompresia a prečo jednoduchý extractor znie nesprávne |
| IMG.1–3 | offsetová tabuľka, 10 B hlavička a viacframe bloky sú čiastočne dekódované; otvorený zostáva význam 8 metadata bajtov, transparent index, runtime delay/loop a OS/2 vs DOS rozdiely |
| UIF.DAT | kompletný directory/chunk formát a väzba UI image ID |
| ENDING.FLI | ring frame/chunk kompatibilita a dôvod rozdielu header 488 vs. 489 dekódovaných frames |
| joystick | presný scaling/dead-zone a kalibračný formát `JoyCal0` |
| tick rate | jednotná definícia game ticku pre AI, steny, dvere, damage a animácie; väzba na reálny frame rate |
| difficulty | damage scaling oboma smermi je potvrdený; otvorené sú spawn/AI a prípadné score modifikátory |

### Video-audit medzery a rozpory

- E3M3 zostáva podľa auditov úplne neauditovaný alebo bez samostatného dokončeného reportu.
- E3M5 má editovaný výpadok približne pri 06:40; bez druhého kontinuálneho záznamu nejde o 100 % frame coverage.
- E3M6 existujú dva auditné dokumenty toho istého videa; novší je konzervatívnejší pri fire damage. Hint-book potvrdzuje kategórie, ale číselný damage musí prísť z EXE/testu.
- E3M1 remote-door mechanika je už video-kompletnejšia než starý partial audit, ale presný `TRIGGER1 → DOORVR/HR` dispatch stále potrebuje XREF alebo kontrolovaný test.
- Video potvrdzuje perzistentné farebné kľúče; spotreba ID kariet však zostáva oddelená otvorená otázka.

### Zastarané alebo už vyriešené položky

- object record nie je 80 B, ale 28 B; guard record nie je 98 B, ale 26 B.
- GAME.PAL už nie je aproximácia: posledných 768 B po PCX markeru poskytuje presných 256 RGB trojíc.
- `LEVEL_UP2` je gateway na preskočenie levelu.
- `WARP_L1..L4` sú farebné key-lock triedy; `WARP_1..8` sú konkrétne stair/dumbwaiter skupiny.
- `DOORVL2/VL3` neznamenajú vyšší stupeň zámku, ale odlišnú grafickú/prostrednú sadu.
- `guard+0x10` je potvrdené HP/strength a `guard+0x0A` behavior/strategy selector.
- `MAP.x` hlavička a 2-bajtová bunka sú dekódované; nejde o packed 16-bit flags.
- druhý štvorznakový stĺpec `WALLS.x`/`OBJECTS.x` je kresliaci descriptor editora, nie runtime animačné dáta.

### Odporúčané poradie ďalšej práce

1. Wall-class dispatcher v EXE; class ID v `MAP.x` hlavičke sú už známe.
2. Animated-wall/sequence timer — počty frame sú známe, treba nájsť delay/loop dispatcher.
3. Door/panel/control/trigger recordy a remote-door logika.
4. Guard state handlers + počiatočné HP/damage/difficulty tabuľky.
5. Save neznáme bloky cez párovanie write/read XREF.
6. Renderer vector/span štruktúry a sprite occlusion.
7. SND.DAT/VOC audit proti výstupu Adam Biser extractor.

## Siedmy auditný prechod — wall flags, USE dispatcher a WARP rodiny (2026-09-22)

Zdroj: priame vetvy `FUN_1010_22e8`, `FUN_1010_234c`, `FUN_1010_2470`,
`FUN_1010_19d6`, `FUN_1010_25ac`, `FUN_1010_272e`, `FUN_1018_1e78`,
`FUN_1018_1f02`, `FUN_1018_200e`, `FUN_1018_2066` vo Win16 1.8 exporte,
porovnanie 256-bajtových `wall_class[]` hlavičiek `MAP.1/.2/.3` a názvov vo
`WALLS.1/.2/.3`.

### Runtime wall-property tabuľka je potvrdená

`FUN_1010_2470` prejde všetkých 256 wall ID. Pre každý wall ID načíta jeho triedu z
`wall_class[wall_id]` na `DAT_1048_8196` a vytvorí odvodený byte vlastností v
`DAT_1048_7E94[wall_id]`. Nie je to druhá kópia triedy, ale rýchla bitová tabuľka
pre renderer, kolíziu, USE a trigger logiku.

| Bit | Podmienka pri vytvorení | Priamo pozorované použitie | Interpretácia |
|---:|---|---|---|
| `0x01` | class `01–40` | prenáša sa do world/vector recordov | všeobecná world-geometry vlastnosť; presný názov PARTIAL |
| `0x02` | class `01–40` | movement, line trace a AI collision test | cell obsahuje kolízne relevantnú stenu/dvere |
| `0x04` | class `01–30` | pohyb a line trace ju blokujú bez door-state testu | pevná/interaktívna statická stena |
| `0x08` | class `31–40` | vytvorenie door recordu a kontrola jeho runtime stavu | dvere |
| `0x10` | class `2E–2F` | osobitná projectile-wall vetva | explodable wall family (`WALL_EX1/WALL_EX2`) |
| `0x40` | class `47–48` | pri prechode sa volá trigger handler | `TRIGGER1/TRIGGER2` |

Tým je vysvetlené, prečo sa triedy `0x3F` a `0x40` objavujú v rendereri a door
logike: nie sú to rozmery ani limity. Sú to posledné dve triedy dverí; v dodaných
dátach zodpovedajú `DOORVC` a `DOORHC` (curtain door vertical/horizontal).
