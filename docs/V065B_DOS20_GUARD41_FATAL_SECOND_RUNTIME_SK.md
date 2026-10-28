# DOS V2.0 GUARD41 — nezávislé opakovanie deferred runtime trace (v0.65B)

**Dátum:** 20. 10. 2026. **Dôkaz:** dve nové samostatné vykonania nezmeneného originálneho DOS v2.0, prirodzené Main Menu → Demo. Žiadne úpravy pôvodného EXE, RAM alebo DEMO.1. Nejde o pôvodný zdrojový kód ani o originál-versus-remake 1:1 test.

## Proveniencia

| Vstup | SHA-256 |
|---|---|
| Originálny packed DOS v2.0 `N3D.EXE` | `a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485` |
| Originálne `DEMO.1` | `25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840` |
| Úplný novo skompilovaný DOSBox-X Advanced History v3 + deferred v0.65 ELF | `11631a6cb93bc9cbf595d63165be2072bfd76c21530e9e744430f3282d19c42d` |
| Krátky originálny `N3DTRC01` CPU trace | `b73a47225c9d869f90ce02d48088133a65fe9960fc3593e2aa13a633e609de17` |
| Dlhý originálny `N3DTRC01` CPU trace | `6b43f12e9a1e4789ca1f51077be151a8232c07bafcc550bff194dc45c076db3f` |

Úspešný úplný GitHub build: https://github.com/marek177/Nitemare3d-reversed/actions/runs/39460300490 (artefakt `dosboxx-n3d-v065-linux-elf`). Na hoste bola doplnená samostatne zostavená knižnica `libSDL2_net-2.0.so.0`. Runtime: Linux Xvfb, SDL2, `core=normal`, `cycles=fixed 75000`, bez mixer zvuku. Trigger: `CS:IP=0CEB:1333`, `opcode4=26886410`, `ES:SI=2A21:2A78` (GUARD 41). Originálne image offsety rátané pomocou aktuálnej MZ relokácie.

## Nový presný inštrukčný dôkaz

**Krátka session:** `20 000 I + 50 785 R + 12 156 W = 82 941` kompletných udalostí, ukončené `INSTRUCTION_BUDGET`, nie `SIZE_LIMIT`. Bezchybné monotónne poradie CPU/event ID.

| CPU ordinal | Originálne miesto | Práve vykonaný účinok |
|---:|---|---|
| 1 | `0CEB:1333`, `IMG:5FA3` | GUARD41 +0x10 HP **111→0** |
| 6–7 | `IMG:5FAD→9FB4` | skutočné volanie death-variant selektora |
| 22, 75, 128 | `1061:1C13`, `IMG:9FE3` | RNG #16–18; AX **491, 2995, 11942** |
| 74, 127, 180 | `1061:1C3F`, `IMG:A00F` | `%7` index **1,6,0**; ZF **1,1,0** (dve odmietnutia, prijatie) |
| 215 | `0CEB:0875`, `IMG:54E5` | GUARD41 +00 `0x0410→0x0429` |
| 218 | `0CEB:087E`, `IMG:54EE` | linked WORLD +03 `0x13→0x29` |
| 223 | `0CEB:088B`, `IMG:54FB` | GUARD41 timer +06 `2→3` |
| 225 | `0CEB:0892`, `IMG:5502` | GUARD41 next +0C `05→09` |
| 227 | `0CEB:0899`, `IMG:5509` | GUARD41 state +0B `06→00` |
| 256–257 | `0CEB:13AF/13B3` | skóre `DS:4182` **0→100**, high `DS:4184` **0→0** |
| 4016 | `0CEB:13CF`, `IMG:603F` | linked MAP marker linear `0x2F181` **A5→00** |
| 4020 | `0CEB:13D6` | GUARD41 handler epilóg pri `SI=2A78` |

RNG lower/high 16-bit zápisy na `0x31E08/0x31E0A` sú skutočné `W` udalosti, poskytujú presnú chronológiu `A6E9C9A6→81EB59D1→0BB31550→AEA69ED3`. Pre-state CPU samotnej inštrukcie nesmie byť mylne interpretovaný ako post-state.

**Dlhá nezávislá session:** `600 000 I + 128 982 W`, čítania vypnuté pre úsporu priestoru, ukončené `INSTRUCTION_BUDGET`. Rovnaké GUARD41 fatálne zápisy v rovnakých CPU ordinaloch. Cez celý instrumentovaný W stream sme v 26-bajtovom GUARD41 recorde našli **iba päť** zápisov (HP, header, timer, next state, state), a v súvisiacej 80-bajtovej WORLD oblasti **jeden** (+03 frame). Po úvodnej smrti sa ďalší W do týchto dvoch oblastí až po #600000 nevyskytol. To sa netýka neinstrumentovaných priamych/aliasovaných prístupov.

**A/B rozdiel:** prvých **1120** CPU pre-state rekordov dvoch originálnych behov je bitovo identických; prvý rozdiel je pri CPU #1121. Z 20 000 zodpovedajúcich ordinalov sedí 4 084. Dlhý beh má vypnuté reads; bez kontrolovaného clock/IRQ testu však neidentifikujeme presnú príčinu divergencie a nevyhlasujeme celkovú timing paritu.

## Dôkazový balík a negatívne testy

Súkromný konverzačný artefakt `N3D_GUARD41_DOS20_DEATH_V065_20261020.zip` má SHA256 `5e29cc6d82669818f51588b8dc69c9f7764728b7738ab4f7907378a458328918`, 21 súborov a obsahuje **oba úplné surové trace**, metadata, screenshots, CSV timeline a štandardnoknižničný Python verifier (`scripts/verify_v065.py --self-test`). V tomto behu verifier **PASS**, 5/5 cielených korupcií stop použilo zlyhanie s vypnutou hash bránou. Komerčné N3D binárky nie sú súčasťou balíka ani GitHubu.

**Otvorené:** RNG #15 pred lethal writerom, original DOS V2.0 `state0→9→0x0A`, jeho RNG #19, eventual drop/pool cleanup, a synchronizované originál-versus-clean-room zero-diff. 600 000 CPU krokov ≠ určitý počet herných tickov; neoznačovať drop za neprítomný alebo smrti úplne ukončenú.

**Záver:** ďalšia nezávislá originálna V2.0 session potvrdila presnú fatálnu vetvu až po GUARD41 return. Bez zmeny globálnych 1:1 percent a bez zmeny aktívneho rendereru.