# v0.32 RE MAX — pôvodné binárne dôkazy a ohraničené uzávery

**Dátum:** 2026-10-14. **Východiskový stav:** v0.31.  
**Rozsah:** Win16 NITE3W v1.10, DOS v1.0/v1.2/v1.9/v2.0, jedna skutočná Win16 USER.SAV vzorka.  
**Dôkaz:** priama kontrola originálnych používateľom dodaných binárnych súborov, MZ/NE segmentov, krátkych strojových inštrukcií a fyzickej SAVE vzorky. Bez spustenia pôvodnej hry alebo pôvodného CPU trace.

## Stav po pokuse uzavrieť všetkých osem oblastí

Slovo „uzavreté“ v tomto reporte znamená **konkrétnu lokálnu statickú otázku**, nie celý subsystém či 100 % behaviorálnu/timing paritu.

| # | Otázka s binárnym dôkazom | Výsledok | Čo ešte nie je uzavreté |
| --- | --- | --- | --- |
| 1 | Win16 PUSH destination wall property gate | **STATICKY UZAVRETÉ:** `3:21E0` testuje `[wallID + 0x7E94] & 0x02` a pri nenule odmietne aktiváciu | ostatné START preconditions, dynamická blokácia v ticku, DOS parity |
| 2 | Win16 USER.SAV HP poloha | **FYZICKY UZAVRETÉ:** blok od `0x2035`, HP `+0x35 = 0x206A`; skutočný `user.sav` tam obsahuje 100 | časovanie LOAD, okrajové prechody, neplatné SAVE, odlišné DOS rekordy |
| 3 | Externé GUARD pain/Dracula writery | **ADRESY UZAVRETÉ:** 7 dovtedy neznámych zápisových miest nižšie | kompletný writer XREF census a všetky class/boss vetvy |
| 4 | Dva Win16 DEMO/input bity | **STATICKY UZAVRETÉ:** masky `0x20` a `0x40` vrátane kombinácie | zvyšné bity, DOS record semantics, seed-1 call ordering |
| 5 | Identita 5 originálnych EXE profilov | **HASHOVO UZAVRETÉ:** 3 DOS unpacked load images, jeden DOS 1.2 packed release kandidát s interným textom V1.2, Win16 v1.10 NE | DOS 1.2 unpacked image hash, ďalšie historické buildy, odlišné vydania a ich funkčná parita |
| 6 | DOS v2.0 door auto-close retry | **STATICKY UZAVRETÉ:** `1000:0ACF` zapisuje `word [door+0A]=4` v obštrukčnej vetve | presný nasledujúci update, vnorenia, paired doors a verziový rozdiel |
| 7 | Win16 plný projectile pool | **LOKÁLNA VETVA UZAVRETÁ:** pri `8` aktívnych slotoch return skôr ako ammo-helper call | celková weapon cadence, ostatné callsites, ammo side-effects, DOS a Multi Plasma |
| 8 | DOS v2.0 secret-panel retraction/cleanup | **LOKÁLNA VETVA UZAVRETÁ:** ±2, koncový stav a cleanup VEC/flags/map | presný **prvý priechodný tick** a poradie kolízie počas pohybu |

**Kompletná 1:1 runtime uzávierka týchto ôsmich širokých subsystémov: NIE.** Neexistuje nový originálny runtime záznam. Celkové percentá parity sa preto nezvyšujú.

## 1. Originálne identity (žiadne binárky v GitHube)

Každý DOS image hash nižšie sa počíta *po odstránení MZ hlavičky* (`e_cparhdr * 16`), nie z pôvodného celého súboru. V1.2 je naopak samostatne označený **packed raw MZ**, neprezentovaný ako unpacked image.

| Build / vstupný súbor | Hashed rozsah | Bajtov | SHA-256 |
| --- | --- | ---: | --- |
| DOS v1.0 `N3D_DOS_v1.0_IDA.EXE` | MZ load image | 154448 | `113ea529e4247a5991f9dde2bd49e04b61f5714a8ea838d027014cac261e004a` |
| DOS v1.2 `N3D-12.exe` | **celý packed MZ**, interný text V1.2 | 115856 | `f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5` |
| DOS v1.9 `N3D_DOS_v1.9_IDA.EXE` | MZ load image | 171296 | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |
| DOS v2.0 `N3D_DOS_v2.0_IDA.EXE` | MZ load image | 171360 | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |
| Win16 v1.10 `nite3w(20261014-102213).exe` | celý NE EXE | 230400 | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |

Starý `v022::Win16Unknown` identifikátor zostal kvôli spätnej kompatibilite s C++ používateľmi, ale jeho fingerprint je už konkrétny Win16 v1.10. Pre DOS 1.2 zostáva v `v022` *unpacked* profil OPEN, kým nebude tento image skutočne dekódovaný a odtlačok potvrdený.

## 2. Inštrukčné dôkazy — Win16 NE segment 3

Poloha segmentu 3 sa zistí z **NE segment table** (`ne_lfanew`, offset tabuľky, align shift), nie jednoduchým sčítaním jedného pevného offsetu pre všetky buildy.

| Win16 offset | Bezprostredný zmysel |
| --- | --- |
| `21E0` | `test byte [wallID+7E94h],02h`; vetva `JNE` odmieta PUSH |
| `55A7` | `push 005Eh; push 4BE8h`; kopírovanie 94 B herného bloku |
| `81F3` | `GUARD+12h = 08h` (direction cache invalidácia, nie timer) |
| `8290` | `GUARD+0Ch = GUARD+0Bh`, **len ak starý state != 0** (`8282` test) |
| `8297` | `GUARD+0Bh = 15h` |
| `A16D` | `OBJECT+06h = 14h` |
| `A17A / A17F / A184` | Dracula `state=08h, nextstate=02h, timer=0001h` |
| `9903 / 992B` | input mask `20h` zdvojnásobí base move+turn, `40h` nastaví oba na 1 |
| `992F / 993B` | Pri súčasných `20h+40h` vyhráva `40h`; obidve hodnoty sa nastavia na 1 |
| `9AC2` | kontrola `slotIndex==8`; pri true skok do zlyhania |
| `9AC7 / 9ACC` | `AL=0; RETF` skôr ako volanie `A97C` (ammo helper) |

Zdravie: `4C1D - 4BE8 = 0x35` a `USER.SAV+2035h+35h = USER.SAV+206Ah`. Dodaná SAVE vzorka s dĺžkou presne `0xD6E7` a korektným length markerom obsahuje na tejto pozícii hodnotu `0x64`. Vzorky iných dĺžok (napr. 54756 B) sa **neinterpretujú nasilu** rovnakým formátom.

## 3. DOS v2.0 image – lokálne pravidlá

| Offset DOS v2.0 load image | Dôkaz |
| --- | --- |
| `0A83` | podmienená vetva pri obsadení/obmedzení zatvárania |
| `0ACF` | `mov word es:[si+0Ah],0004h` |
| `0BDD / 0BE2` | výber krokov `+2` alebo `-2` pre pohyb VEC hranice |
| `0BF4` | zapisuje zvolenú deltu do koncových súradníc |
| `0C02..0C29` | zistenie dosiahnutého konca, zmena stavu, čistenie príznaku pri príslušnej vetve |
| `0C8E..0D21` | per-panel stav 2, postupné VEC úpravy o 2, opätovné udržanie stavu počas pohybu |
| `0D8D..0DCB` | pri splnenom dokončovacom teste čistí VEC príznaky a mapovú bunku |

Pri poslednom bode **nemáme experiment** určujúci, kedy presne hráč prvýkrát prejde cez pohybujúcu sa stenu. Zápis do VEC/mapy nie je automaticky dôkaz kompletného poradia detekcie kolízie, zvlášť pri vnorenom update.

## 4. Opakovateľnosť

Nový read-only verifier `tools/n3d_v032_static_verify.py` očakáva lokálne vlastnené originálne vstupy:

```sh
python tools/n3d_v032_static_verify.py \
  --dos10 "N3D_DOS_v1.0_IDA.EXE" \
  --dos12 "N3D-12.exe" \
  --dos19 "N3D_DOS_v1.9_IDA.EXE" \
  --dos20 "N3D_DOS_v2.0_IDA.EXE" \
  --win16 "nite3w.exe" \
  --save "user.sav"
```

Odlišný build/hash **fail closed**; verifier nepoužije adresy z inej verzie.
Pri presnom hashi kontroluje opcode windows na príslušných NE/DOS obrazoch.
SAVE parser len prečíta hodnotu, nesmie odhadovať LOAD timing ani opraviť
HP alebo obsah originálneho súboru. Výstup uvádza `original_runtime_executed=false`.

Skutočne vykonané na dodaných súboroch v tomto audite:
- 5/5 identifikačných profilov sedí;
- 16/16 kontrol Win16 segment-3 opcode windows sedí;
- 8/8 DOS v2.0 opcode windows sedí;
- jedna 55 015 B USER.SAV vzorka má HP na `0x206A` s hodnotou 100;
- **0 pôvodných realtime CPU trace** — nemožno zvyšovať parity %.

V CI bežia len syntetické testy bez distribúcie pôvodného EXE alebo SAV.
Kompletné runtime poradie FAST/MAIN, všetky GUARD writery, DOS DEMO reader,
plný projectile lifecycle, prvý passability tick panelu a prvý LOAD tick
zostávajú **OPEN**. Pri ďalšom runtime zázname použi prísne porovnanie
`tools/n3d_edge_trace_compare.py` a `tools/n3d_trace_compare.py`.
