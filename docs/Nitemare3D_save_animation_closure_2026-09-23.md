# Nitemare 3D: uzavretie USER.SAV a IMG/SEQDEF

**Dátum:** 23. 9. 2026  
**Typ:** statický audit Win16 1.10, kontrola Win16 1.8 a DOS v2.0, priame parsovanie troch dodaných IMG súborov  
**Rozsah:** 94-bajtový hráčsky/herne stavový blok v `USER.SAV`; adresáre, 90-bajtové SEQDEF záznamy, streamy snímok a časovanie animácií.

## Stav uzavretia

- **Fyzické rozloženie a čítanie/zápis 94-bajtového bloku:** potvrdené. Blok je na offsete `0x2035` slotu, dĺžka slotu je `0xD6E7`; čítač aj zapisovač prenášajú presne `0x5E` bajtov.
- **Vnútorné offsety 94-bajtového bloku:** všetkých 94 bajtov je priradených k rozsahu a pri poliach s priamymi čítačmi/zapisovačmi je statické použitie pomenované. Zostáva niekoľko bajtov bez priameho xrefu, takže úplný sémantický význam bloku ešte nie je dokázaný.
- **IMG/SEQDEF formát:** adresáre, obe banky, rozloženie 90-bajtového záznamu, hranice streamov, aliasy a počty snímok sú staticky uzavreté pre tri dodané IMG súbory. Tým sa opravuje starý výklad, podľa ktorého low bank prekrývala adresáre.
- **Časovanie:** cesta od intervalu po termín snímky je staticky uzavretá vo Win16 1.10 a porovnaná s DOS v2.0. Konkrétny selector → trieda/runtime entita → viditeľná animácia a niektoré zriedkavé alternatívy vyžadujú riadené spustenie hry.

„Všetky offsety sú pokryté“ tu znamená úplný fyzický inventár. Neznamená to, že každý bajt má dokázaný príbehový alebo gameplay názov, ani že všetky runtime prechody boli pozorované.

## Podklady a identita vstupov

| Vstup | Identita / SHA-256 | Použitie |
|---|---|---|
| Win16 1.10 EXE `nite3w.exe` | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` | čítač/zapisovač save, loader a animátory |
| Win16 1.10 C export `nite3w110.exe.c` | `71ca365f8c6a61fa9cadad8631e9fcd6ce134e36c714878889c75b7399280168` | hlavný čitateľný podklad pre callsite-y |
| Win16 1.8 C export `NITE3W18.EXE(1).c` | `0917624ccdc53a98a6ea04760689d989692bf2d86b818d86fd2a26c889f8cc94` | kontrola rovnakej bankovej aritmetiky |
| DOS v2.0 C export `N3D-DOS-UNFULL-v20.exe.c` | `5b4c671ca5864916f250324d226378a8ce6ee3278220a832fc7f139e49796d54` | kontrola sekvenčného načítania a animátora |
| `IMG.1` | 2,250,921 B; `0d7b5bf9a3348be263d337201bd98e867f765b87be3f15666164c39763dc1267` | wall/object adresáre, SEQDEF, snímky |
| `IMG.2` | 1,843,068 B; `61554b68a56ea04f0fe5b5cacaf6938aa13a6905e8702d77f659a242623d748c` | rovnaká validácia |
| `IMG.3` | 1,798,340 B; `4599dac2ee3e387e6311d6d9a422582848ce7d4d6dbbfba74172777a50541a1c` | rovnaká validácia |
| `USER.SAV` | 55,015 B; `ebb0dd3fc62e3ca27cdc5c5a9163b98e3489c0d0fb02d8a13a58df380a596cce` | fyzická dĺžka slotu a save dát |

Kľúčové Win16 funkcie: `FUN_1010_5466` (zápis), `FUN_1010_574C` (čítanie), `FUN_1010_BA16` (inicializácia), `FUN_1010_4B86` (načítanie sekvencie), `FUN_1010_4C8A` (registrácia/zdieľanie), `FUN_1010_6EE0`, `FUN_1010_700A`, `FUN_1010_B94E`, `FUN_1010_B9B2`, `FUN_1010_80F8`, `FUN_1010_9E20` a `FUN_1010_D6C6`. DOS porovnanie: `FUN_1000_2CF4`, `FUN_1000_241E`, `FUN_1000_BDF8`.

## 1. `USER.SAV`: fyzický záznam a opätovné zostavenie stavu

Slot má dĺžku `0xD6E7` (55,015) bajtov. Save/load funkcie kopírujú 94 bajtov z `DAT_1048_4BE8` na offset slotu `0x2035` a späť. Po načítaní sa odvodené adresy/cache ukazovatele znovu vytvárajú z koordinát a mapy; linked-list indexy sa rekonštruujú a entity deadline-y sa posúvajú na aktuálny `GetTickCount`. Tieto položky preto nie sú trvalé procesné adresy uložené v save.

`FUN_1010_BA16` vynuluje blok a nastaví aspoň: zbraň `0xFF`, HP 100, obtiažnosť 1, krátky timer `0xFFFF`, hodnoty `DAT_4C32=4` a `DAT_4C2F=1`; potom aplikuje cheat stav. Celé blokové kopírovanie samo osebe nedokazuje význam bajtov bez samostatného čítača/zapisovača.

Nižšie uvedené offsety sú relatívne k `DAT_1048_4BE8` a k 94 bajtom na `USER.SAV+0x2035`. Viacbajtové čísla sú x86 little-endian.

| Offset | Šírka | Globál(e) | Staticky doložené použitie |
|---:|---:|---|---|
| `+0x00` | 1 | `4BE8` | Latch: event nastaví 1; pri nenule sa preskočí jedna vetva korekcie pozície. Účel na úrovni hry neuzavretý. |
| `+0x01` | 1 | `4BE9` | Bez priameho čítača/zapisovača v C exporte; kandidát na zarovnanie/výplň, nepotvrdené. |
| `+0x02..03` | u16 | `4BEA` | Smerový uhol, normalizovaný do 0–359°. |
| `+0x04..05` | u16 | `4BEC` | Sektor odvodený zo smeru delením 45. |
| `+0x06..07` | u16 | `4BEE` | Zaokrúhlený oktant smeru. |
| `+0x08..09` | u16 | `4BF0` | Maska `1 << sector` filtrovaná cez `0x99`; výber pohybovej/kolíznej osi. |
| `+0x0A..0B` | u16 | `4BF2` | X súradnica dlaždice (`worldX >> 6`). |
| `+0x0C..0D` | u16 | `4BF4` | Y súradnica dlaždice (`worldY >> 6`). |
| `+0x0E..0F` | u16 | `4BF6` | X súradnica hráča vo world units. |
| `+0x10..11` | u16 | `4BF8` | Y súradnica hráča vo world units. |
| `+0x12..19` | 4 × u16 | `4BFA–4C00` | Štyri cursory do zoradených VEC/actor edge listov; príslušné zoznamy začínajú na `6982`, `6EB6`, `73EA`, `791E`. Sú runtime indexy/cursory, nie uložené ukazovatele. |
| `+0x1A..1D` | 2 × u16 | `4C02`, `4C04` | Cursory do dvoch ďalších kandidátnych/object edge listov (`839A`, `8916`). |
| `+0x1E..1F` | u16 | `4C06` | Dominantná os, odvodená od absolútnej hodnoty sin/cos. |
| `+0x20..25` | 3 × u16 | `4C08–4C0C` | Bresenhamov akumulátor a delty používané pri pohybe/kolízii. |
| `+0x26..27` | u16 | `4C0E` | Krátky timer: štartuje na `0xFFFF`, po interakcii/útoku sa nastaví na 3 a znižuje vo funkcii `BBCA`; presná hranica viditeľnej akcie nie je uzavretá. |
| `+0x28..29` | u16 | `4C10` | Po načítaní odvodené mapové tile offset/index: `(tileY*0x40+tileX)*2-0x5962`. |
| `+0x2A..2B` | u16 | `4C12` | Druhý odvodený pointer/sentinel; po načítaní sa obnovuje na statickú hodnotu okolo `0x1040`; cieľová dátová rola neúplná. |
| `+0x2C..2D` | u16 | `4C14` | Obtiažnosť 0/1/2; damage cestu mení na polovicu/dvojnásobok/normálnu. Menu ju priraďuje. |
| `+0x2E..31` | u32 | `4C16` | Skóre; HUD ho zobrazuje a pickupy zvyšujú. |
| `+0x32..33` | u16 | `4C1A` | Index VEC/object posledného útočníka, ktorý sa použije na vyhľadanie súradníc útočníka. |
| `+0x34` | 1 | `4C1C` | Aktuálny tile object/class selector. |
| `+0x35` | 1 | `4C1D` | HP hráča; nová hra nastaví 100. |
| `+0x36` | 1 | `4C1E` | Zvyšuje ho pickup class `0x35`; priame gameplay čítanie sa nenašlo. „Extra life“ je zatiaľ interpretácia, nie potvrdený názov. |
| `+0x37` | 1 | `4C1F` | Munícia pre weapon selector 2. |
| `+0x38` | 1 | `4C20` | Munícia pre selector 3/default cestu. |
| `+0x39` | 1 | `4C21` | Pickup class `0x38` pridáva 20 s limitovou kontrolou `<100`; ďalší čítač sa nenašiel. Class `0x38` nie je v troch dodaných MAP súboroch. |
| `+0x3A` | 1 | `4C22` | Špeciálny/panelový charge; class `0x32` pridá `1 << subtype`, cap 99; secret-panel cesty kontrolujú a míňajú jednotku. |
| `+0x3B` | 1 | `4C23` | Aktuálna zbraň; `0xFF` znamená žiadnu. |
| `+0x3C` | 1 | `4C24` | Zaradený weapon selector. |
| `+0x3D` | 1 | `4C25` | Bez priamej referencie v C exporte; význam neurčený. |
| `+0x3E..3F` | u16 | `4C26` | Režim výberu zbrane v UI (1/2). |
| `+0x40` | 1 | `4C28` | Bitfield štyroch kľúčov; class `0x2F` pickup a HUD používajú bity. Presné ID→bit sa odvíja od subtype/objektu. |
| `+0x41` | 1 | `4C29` | Druhý bitfield karty/ID; class `0x30` a HUD ho čítajú. Dodané OBJECTS/MAP dáta identifikujú dva ID card objekty. |
| `+0x42` | 1 | `4C2A` | Bitfield vlastnených zbraní, class `0x36` pickup. |
| `+0x43` | 1 | `4C2B` | Nastaví sa pri class `0x37`, ale priamy čítač sa nenašiel; class v troch MAP súboroch chýba. |
| `+0x44` | 1 | `4C2C` | Magic Eye aktívny flag; class `0x3B`, OBJECTS názov “Magic eye”, toggle a charge `4C43`. |
| `+0x45` | 1 | `4C2D` | Crystal Ball aktívny flag; class `0x3A`, OBJECTS názov “Crystal ball”, toggle a charge `4C42`. |
| `+0x46` | 1 | `4C2E` | Interakčný/zbraňový lock latch; trigger marker G/H prepína ho, nenulový input vedie do jam hlášky. Presný rozsah locku nie je istý. |
| `+0x47` | 1 | `4C2F` | Inicializuje sa na 1; priamy reader sa nenašiel. |
| `+0x48` | 1 | `4C30` | Action latch: nastaví sa po vyriešení inputu a spotrebuje/vynuluje vo `A2CE`. |
| `+0x49` | 1 | `4C31` | Bez priamej referencie; inicializuje sa na 0. |
| `+0x4A..4B` | u16 | `4C32` | Inicializuje sa na 4; gameplay reader sa nenašiel. |
| `+0x4C..51` | 6 | `4C34–4C39` | Šesť bajtov bez priameho čítača/zapisovača v dostupnom C exporte; iba bloková init/kópia. Rezervované/nezistené. |
| `+0x52..53` | u16 | `4C3A` | Režim animácie weapon selector HUD: 0 idle, 1 dopredu, 2 dozadu. |
| `+0x54..55` | u16 | `4C3C` | Aktuálny HUD weapon selector frame/index; pri animácii sa zvyšuje/znižuje k hranici. |
| `+0x56..57` | u16 | `4C3E` | HUD súradnicová/layout hodnota načítaná z vybratého weapon recordu; presný názov neuzavretý. |
| `+0x58..59` | u16 | `4C40` | Druhá HUD súradnicová/layout hodnota z weapon recordu; presný názov neuzavretý. |
| `+0x5A` | 1 | `4C42` | Crystal Ball charge; pickup class `0x3A` pridá 20 do 100, aktívny stav ho míňa v sim-time. |
| `+0x5B` | 1 | `4C43` | Magic Eye charge; pickup class `0x3B` pridá 20 do 100, aktívny stav ho míňa v sim-time a používa ho map/highlight helper. |
| `+0x5C` | 1 | `4C44` | Munícia weapon selector 1. |
| `+0x5D` | 1 | `4C45` | Štyri progress bity; nastavujú sa pickupmi class `0x3C` (OBJECTS pomenúva ID `0x1F–0x22` ako farebné Pentagramy). Texty sa vyberajú podľa bitov a vetva vyžaduje masku `0x0F`; presné bit→farba mapovanie ešte nie je úplne doložené. |

### Čo ostáva z 94 bajtov

Priamym xrefom sa nepodarilo pomenovať `+0x01`, `+0x3D`, `+0x43`, `+0x47`, `+0x49`, `+0x4A..4B` a `+0x4C..51`; niektoré sa nastavujú alebo menia, no ich herný reader nebol nájdený. Význam `+0x00`, `+0x26..27`, `+0x2A..2B`, `+0x36`, `+0x39` a `+0x46` je len čiastočný. `+0x56..59` sú použité, ale ich presný layout názov sa nepozná. Môže ísť o prístupy cez assembly, neexportovanú funkciu alebo nepriame indexovanie; „nenašiel sa C xref“ nie je dôkaz, že bajt nehrá rolu.

Pokračovanie na skutočné sémantické 100 % potrebuje raw disassembly/reference audit týchto adres v presne rovnakej Win16 binárke a/alebo dynamické save/load testy, ktoré menia každé podozrivé pole. Presný príbeh `+0x36` a tried `0x37/0x38`, ako aj pentagram bitov, si vyžaduje asset/map párovanie naprieč buildmi.

## 2. IMG adresáre, SEQDEF banky a frame streamy

### Súborový layout

| IMG rozsah | Dĺžka | Obsah |
|---:|---:|---|
| `0x0000..0x03FF` | `0x400` | 256 little-endian u32 wall image offsetov |
| `0x0400..0x07FF` | `0x400` | 256 little-endian u32 object image offsetov |
| `0x0800..0x61FF` | `0x5A00` | 256 × 90 B low/wall SEQDEF záznamov |
| `0x6200..0xBBFF` | `0x5A00` | 256 × 90 B high/object SEQDEF záznamov |
| `0xBC00..EOF` | variabilné | image frame streamy |

Loader `FUN_1010_4B86` skladá offset z vybraného 16-bit selectoru násobeného `0x5A`, pričom high byte dostane `+8`. Preto je offset `0x0800 + selector*90`, nie `8 + selector*90`. Pri wall selector `id` to dá low bank `0x0800+90*id`; pri object selector `0x100|id` (a osobitnej class-5 wall ceste) to dá high bank `0x6200+90*id`. Rovnaký výpočet je v Win16 1.8 `FUN_1010_4B86` a DOS v2.0 `FUN_1000_2CF4`. Low bank teda **neprekrýva** adresáre; začína hneď za oboma adresármi. Starý výklad vznikol nesprávnym prečítaním `+'\b'` v dekompilovanom výraze ako obyčajného offsetu 8 namiesto horného bajtu `0x08`.

### 90-bajtový SEQDEF

| Offset | Šírka | Pozorovaná rola |
|---:|---:|---|
| `+0x00..01` | u16 | Interval animácie; Win16 používa priamo v ms pre deadline. |
| `+0x02` | u8 | Počet po sebe idúcich frame záznamov; runtime alokácia je `count × 10` B. |
| `+0x03` | u8 | Ak je nenulový, loader alokuje/kopíruje rozšírených 90 B do sekvenčného runtime stavu. |
| `+0x04..13` | 8 × u16 | Prvá tabuľka per-facing selector/phase slov. |
| `+0x14..23` | 8 × u16 | Druhá tabuľka per-facing selector/phase slov. |
| `+0x24..33` | 8 × u16 | Tretia tabuľka per-facing selector/phase slov. |
| `+0x34`, `+0x36`, `+0x38` | 3 × u16 | Stavovo špecifické selector/frame slová pre stavy 2, 3 a 4. |
| `+0x3A..47` | 7 × u16 | Kandidáti alternatívnej akcie; náhodný výber testuje nenulový high byte. |
| `+0x48` | u8 | Bez priameho použitia nájdeného v C exporte. |
| `+0x49` | u8 | Povolenie selector-7 shortcutu v konkrétnej vetve. |
| `+0x4A..57` | 7 × u16 | Druhá tabuľka kandidátov alternatívnej akcie. |
| `+0x58` | u8 | Bez priameho použitia nájdeného v C exporte. |
| `+0x59` | u8 | Povolenie druhého selector-7 shortcutu v konkrétnej vetve. |

Funkcia `FUN_1010_6EE0` volí z troch facing tabuliek podľa triedy/stavu a orientácie. Low byte vybraného slova funguje ako selector; celé slovo sa používa aj v phase-threshold ceste `FUN_1010_CBD4`. `FUN_1010_700A` číta tri stavové slová. `FUN_1010_B9B2` a `FUN_1010_B94E` vyberajú z príslušných siedmich slov podľa high-byte kandidátov; `FUN_1010_80F8` potom zvolenú hodnotu spotrebuje. Tabuľky sú teda aktívne runtime riadenie smerových/akčných snímok, nie neinterpretované prívesky. Z názvu polí sa nedá bezpečne vyvodiť konkrétna herná akcia pre každý selector.

### Frame záznam a súborový stream

Adresárny u32 ukazuje na prvý frame 10-bajtový header. Overený stream je sekvenčný: po headeri nasleduje `width × height` pixelových bajtov a ďalší frame začína na `offset + 10 + width*height`. Rozmery sú v prvých dvoch bajtoch headera. Loader alokuje runtime pixel buffer a používa ďalšie sloty ako runtime pomocné/pointer polia; surové bajty `+2..+9` sa nenačítavajú ako samostatné významové metadata v správaní, ktoré bolo možné potvrdiť. Header na disku preto nemožno bezpečne pomenovať ako 10 B sériový runtime frame struct.

Každý nenulový directory selector bol dekódovaný podľa SEQDEF count a skontrolovaný proti hranici nasledujúceho unikátneho image pointeru (pri poslednom wall stream-e proti začiatku object streamov; pri poslednom object stream-e proti EOF). Všetky streamy prešli bez header/payload overflow a dekódovaný počet sa rovná SEQDEF count. Opakované u32 offsety sú aliasy sekvencií; nie je správne počítať každý alias ako novú pixelovú animáciu.

| Súbor | Banka | Nenulové ID | Unikátne streamy | Rôzne snímky v streamoch | Alias navyše | Intervaly (nenulové ID) |
|---|---|---:|---:|---:|---:|---|
| IMG.1 | wall | 150 | 117 | 189 | 33 | 0:134, 100:4, 150:10, 200:2 |
| IMG.1 | object | 167 | 92 | 651 | 75 | 0:155, 50:4, 100:5, 150:3 |
| IMG.2 | wall | 144 | 93 | 130 | 51 | 0:134, 100:1, 150:7, 200:2 |
| IMG.2 | object | 160 | 89 | 610 | 71 | 0:148, 50:4, 100:5, 150:3 |
| IMG.3 | wall | 142 | 116 | 168 | 26 | 0:125, 100:3, 150:14 |
| IMG.3 | object | 136 | 82 | 404 | 54 | 0:124, 50:4, 100:5, 150:3 |

Úplný 1,536 riadkový inventár obsahuje všetkých 256 ID v oboch bankách pre každý súbor vrátane null offsetov, sekvenčného selectoru, SEQDEF offsetu, interval/count/flag, aliasov, stream konca, frame offsetov, rozmerov, payload veľkostí a kontroly hraníc: `Nitemare3D_IMG_SEQDEF_frame_inventory_2026-09-23.csv`.

## 3. Časovanie a prechod snímok

Win16 `FUN_1010_D6C6` získa `GetTickCount`/`timeGetTime`. `DAT_4746` prejde do deadline výpočtu bez konverzie, preto dodané intervaly sú milisekundy. Po termíne updater spracuje presne jeden frame a nastaví ďalší deadline od aktuálneho času; neexistuje catch-up slučka. State 1 opakuje sekvenciu, state 2 je one-shot cesta. Interval 0 znamená, že deadline je už splnený pri ďalšom update; sám osebe nedokazuje statickú snímku. Hlavná Win16 simulation step má minimum 40 ms, takže pozorovaná vizuálna kadencia môže byť obmedzená aj simulačným plánovačom.

DOS `FUN_1000_241E` tiež posúva najviac o jednu snímku na expirovaný termín. `FUN_1000_BDF8` môže použiť BIOS tick násobený `0x37` (približne 55 ms) alebo DOS čas; časová presnosť preto nie je totožná s Win16 `GetTickCount`. DOS generický animátor má loop/one-shot/reverse režimy a náhodné alternatívne výbery, no ich výsledná prezentácia a väzba na každú triedu sa musí overiť dynamicky.

## 4. Konkrétne zvyšné dôkazy pre úplné sémantické uzavretie

1. Raw disassembly/XREF audit pre nepriame alebo neexportované prístupy k `DAT_4BE9`, `DAT_4C25`, `DAT_4C2B`, `DAT_4C2F`, `DAT_4C31`, `DAT_4C32`, `DAT_4C34..4C39` a presné layout roly `DAT_4C3E/4C40`; vykonať nad hashom uvedenou Win16 1.10 binárkou.
2. Save/load kontrolované zmeny pre každý vyššie uvedený kandidát na neznáme pole, vrátane porovnania bajtových diffov po známych gameplay udalostiach.
3. V runtime prejsť reprezentatívne facing, state 2/3/4, obe alternate tabuľky, selector-7 shortcut a 0/50/100/150/200 ms intervaly. Zaznamenať selector, vybranú sekvenciu, časový termín a zobrazený frame.
4. Spárovať každú z troch IMG s presným EXE/epizódou/MAP/WALLS/OBJECTS buildom; statická platnosť formátu nedokazuje, že všetky súbory patria do tej istej inštalácie.
5. Potvrdiť runtime rozdiely Win16 1.8/DOS 2.0 voči Win16 1.10. V dostupnom prostredí nebol nájdený Wine/DOSBox emulátor, preto tento report neuvádza runtime pozorovania.

Do vykonania týchto bodov možno s istotou označiť fyzický save layout, statické použitie väčšiny polí 94 B a parsovanie dodaných IMG dát za uzavreté. Sémantických 100 % a runtime 100 % dostupné dôkazy nepodporujú.