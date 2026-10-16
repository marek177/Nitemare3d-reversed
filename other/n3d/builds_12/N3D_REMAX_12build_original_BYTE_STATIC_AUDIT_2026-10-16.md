# Nitemare 3D – RE-1TO1-MAX: 12-build original-byte static audit

**Dátum:** 16. október 2026  |  **Metóda:** iba statická analýza pôvodných MZ/NE binárok, dekompresia EXEPACK, relokácie, konkrétne opkódy, tabuľky skokov, callsite a dátový tok v ohraničených rutinách. **Žiadny originálny program nebol spustený.**

## 1. Rozsah a integrita

Prvý systematický byte audit pokrýva **sedem DOS verzií (1.0, 1.1, 1.2, 1.5, 1.7, 1.9, 2.0)** a **päť Win16 verzií (1.0, 1.3, 1.6, 1.8, 1.10)**. Záznamy majú jedinečný SHA-256, prefixy a relokácie; 12/12 identít prešli striktne overením. **Tento krok nie je kompletným auditom každého základného bloku/CFG, CALL/indirect edge, ani 1:1 parity.**

| Platforma | Build | Raw EXE [B] | Rozbalený DOS image [B] | Relokácie/fixups | Priame FAR CALL (podložené relokáciami) |
|---|---|---:|---:|---:|---:|
| DOS | 1.0 | 115,152 | 154448 | 1639 | **1386** |
| DOS | 1.1 | 115,768 | 155552 | 1651 | **1397** |
| DOS | 1.2 | 115,856 | 155632 | 1655 | **1401** |
| DOS | 1.5 | 115,904 | 170672 | 1655 | **1399** |
| DOS | 1.7 | 116,068 | 170848 | 1657 | **1401** |
| DOS | 1.9 | 116,556 | 171296 | 1669 | **1413** |
| DOS | 2.0 | 116,606 | 171360 | 1670 | **1414** |
| Win16 | 1.0 | 229,008 | — | 443 | **407** |
| Win16 | 1.3 | 229,136 | — | 443 | **407** |
| Win16 | 1.6 | 230,128 | — | 444 | **409** |
| Win16 | 1.8 | 230,224 | — | 446 | **411** |
| Win16 | 1.10 | 230,400 | — | 446 | **411** |

**Spolu:** 9 811 relokáciami podložených priamych DOS FAR CALL miest + 2 045 Win16 FAR import CALL miest = **11 856 callsite záznamov cez buildy**. Rovnaká rutina v rôznych buildoch sa počíta opakovane. Nepočítame tým NE-interné volania, near `CALL`, nepriamy `FF` dispatch, callbacks, IRQ ani všetky vykonateľné vetvy. To je rozsah jednej konkrétnej triedy hrán, nie celý call graph.

**Doslovný fingerprint:** pri DOS je hashovaný *rozbalený MZ load image bez hlavičky a bez aplikovania loader-relokácií*; pri Windows je hashovaný *celý pôvodný NE EXE*. Každý build je fail-closed pri nezhode. Úplný SHA-256 zoznam v `N3D_12build_identities.csv`.

### Nezávislé testy pravosti DOS rozbalenia

Rozbalenie originálnych EXEPACK súborov bolo porovnané **bajt po bajte** s nezávislými používateľskými súbormi `N3D_DOS_v1.0_IDA.EXE`, `v1.7_IDA.EXE`, `v1.9_IDA.EXE` a `v2.0_IDA.EXE`. Po odstránení ich MZ hlavičiek (6 656 B pre 1.0/1.7; 7 168 B pre 1.9/2.0) sa všetky **4/4 obrazy úplne zhodujú**. Pre nové 1.1/1.2/1.5 majú dostupné rozbalené obrazy korektný interný EXEPACK formát, jednoznačnú relokačnú tabuľku, reťazec verzie a unikátne SHA. Ich prirodzený beh v emulátore zatiaľ nebol testovaný.

## 2. DOS – incoming-actor DAMAGE rutiny (7/7)

| Build | Wrapper (load image) | Damage producer FAR CALL | HP DS offset | Guard poradie | HP slot v dispatcher-i |
|---|---|---|---|---|---:|
| 1.0 | `0x06792` | `0x067B4` | `0x03FDF` | ochrana pred damage | 6 |
| 1.1 | `0x06816` | `0x06838` | `0x040E5` | ochrana pred damage | 6 |
| 1.2 | `0x06822` | `0x06844` | `0x040E5` | ochrana pred damage | 5 |
| 1.5 | `0x06870` | `0x06892` | `0x040B5` | ochrana pred damage | 5 |
| 1.7 | `0x0690C` | `0x0692E` | `0x040F7` | ochrana pred damage | 5 |
| 1.9 | `0x06A70` | `0x06A92` | `0x04187` | ochrana pred damage | 5 |
| 2.0 | `0x06A70` | `0x06A84` | `0x04189` | damage pred ochranou | 5 |

- **1.0–1.9:** ochranný flag a `game_state==2` sa kontrolujú **pred** výpočtom damage, takže producent sa v blokovanej vetve nevolá.
- **2.0:** producent sa volá **pred** týmito kontrolami; ak je `damage!=0`, zapisuje sa `DS:417A = 3` do hit indikátora. Môže preto spotrebovať RNG a nastaviť indikátor aj pri zachovaní HP.
- V pôvodných obrazoch je šesť starých wrapperov dlhých 133 B; 2.0 wrapper 143 B. Adresy mimo tejto funkcie sa z týchto lokálnych zistení neodvodzujú.

## 3. DOS – HUD dispatcher sa zmenil medzi 1.1 a 1.2

| DOS | Dispatcher load image | Počet položiek v jump table | HP slot | HP handler |
|---|---|---:|---:|---|
| 1.0 | `0x0851A` | 24 | 6 | `0x08628` |
| 1.1 | `0x0873A` | 24 | 6 | `0x08848` |
| 1.2 | `0x08746` | 23 | 5 | `0x08857` |
| 1.5 | `0x08798` | 23 | 5 | `0x088A9` |
| 1.7 | `0x08834` | 23 | 5 | `0x08945` |
| 1.9 | `0x08998` | 23 | 5 | `0x08AA9` |
| 2.0 | `0x089A2` | 23 | 5 | `0x08AB3` |

**Overené:** v DOS 1.0/1.1 je v tabuľke **24 slotov (0–23)** a rutinu aktualizácie HP vyvoláva slot **6**; od DOS 1.2 je **23 slotov (0–22)** a volá ju slot **5**. Staršia iniciálna vetva (case 0) iterovala **28 záznamov po 10 bajtoch**. Od 1.2 sa jej slučka nachádza v preambule dispatcher-a, s podmienením na byte-flag (v 1.2 `DS:13E6`) a následným vyčistením flagu. Dokázaný je lokálny kód a uložená tabuľka; všetci globálni writery flagu, vstupné cesty do dispatcher-a a časovanie aktualizácie zostávajú OPEN.

**Presný účinok HP handlera:** všetkých 7 buildov vykonáva rovnakú inštrukčnú postupnosť `MOV AL,[HP] → SUB AL,64h → SBB CL,CL → AND AL,CL → ADD AL,64h → MOV [HP],AL`, ktorá dáva `HP = min(HP,100)` pre všetkých 256 hodnôt `uint8`. Ide o cap pri tomto *konkrétnom HUD update handleri*, nie automatický dôkaz, že všetky writery HP v celej hre saturujú na 100.

## 4. DOS – RNG formula, state layout a 22 presných priamych callerov

| DOS | LCG implementácia | FAR wrapper | DS stav (low word) | Počet priamych volaní wrappera |
|---|---|---|---|---:|
| 1.0 | `0x14C6C` | `0x0F80E` | `DS:23B2` | **22** |
| 1.1 | `0x14DB8` | `0x0FA26` | `DS:24AA` | **22** |
| 1.2 | `0x14E18` | `0x0FA86` | `DS:24A6` | **22** |
| 1.5 | `0x14E6C` | `0x0FAD4` | `DS:2478` | **22** |
| 1.7 | `0x14F08` | `0x0FB70` | `DS:247C` | **22** |
| 1.9 | `0x1509C` | `0x0FD04` | `DS:24B6` | **22** |
| 2.0 | `0x150D8` | `0x0FD40` | `DS:24B8` | **22** |

Každý originálny obraz má presne **jeden** LCG násobiaci blok s konštantami `0x000343FD` a `0x00269EC3`, pred ním prečítaný 32-bitový stav (dve susedné slová), po ňom 32-bitový zápis stavu a vrátený horný word s odstráneným najvyšším bitom:

```c
uint32_t state = state * 0x000343FDu + 0x00269EC3u; // modulo 2^32
uint16_t result = (state >> 16) & 0x7FFFu;
```

**22** relokáciami doložených priamych CALL opkódov `9A` odkazuje v každom builde na tento RNG wrapper. Zoznam 154 inštrukčne podložených miest je v `N3D_DOS_rng_22_calls_each.csv`. Princíp rozdielu v poradí damage/ochrana je stále relevantný: rovnaký počet **statických callsites ≠ rovnaké runtime poradie alebo rovnaký počet RNG draw počas konkrétneho ticku**. Indirect, interrupt a nested prístup do generátora sa tým nevylučuje.

## 5. Win16 NE – 5 buildov a presný vývoj imports

Všetkých päť originálnych Windows EXE má **10 NE segmentových položiek, z toho 6 s dátami na disku** a 9 importovaných modulov (`KERNEL`, `WING`, `DISPDIB`, `GDI`, `USER`, `KEYBOARD`, `COMMDLG`, `MMSYSTEM`, `SHELL`). Počty NE fixup záznamov: **443, 443, 444, 446, 446**. Relokáciami potvrdené FAR import CALL opkódy: **407, 407, 409, 411, 411**. Sú to importované volania s typom fixupu `(source_type 3, target_type 1)`; NE importný modul číslo 8 je **MMSYSTEM**, nie ôsmy segment programu.

| Prvý build | Caller NE 3 | MMSYSTEM ordinal | Názov API (historická ordinal mapa) |
|---|---|---:|---|
| 1.6 | `3:0xDF51` | 201 | `midiOutGetNumDevs` |
| 1.6 | `3:0xDF62` | 202 | `midiOutGetDevCaps` |
| 1.8 | `3:0xE07A` | 211 | `midiOutGetVolume` |
| 1.8 | `3:0xE091` | 415 | `waveOutGetVolume` |

**Konkrétne zmeny:** v Win16 1.6 pribudli `midiOutGetNumDevs` a `midiOutGetDevCaps` (3:DF51, 3:DF62), teda runtime vetvy zisťujúce MIDI zariadenia a schopnosti. V 1.8 pribudli `midiOutGetVolume` a `waveOutGetVolume` (3:E07A a 3:E091), ktoré zapisujú návratové statusy do bajtových premenných (v 1.8 `DS:3A64` a `DS:3A65`). Zoznam importných API zostáva v 1.10 nezmenený, čo **nevylučuje ďalšie interné zmeny**. Názvy podľa referenčného historického 16-bit MMSYSTEM/Wine exportného mapovania: https://sources.debian.org/src/wine/1.8.7-2/dlls/mmsystem.dll16/mmsystem.dll16.spec/ .

## 6. Win16 1.0 vs 1.3 – prvé timing/core vetvy

Najstarší dostupný Windows build **V1.0** (`NITE3W -10.EXE`, 229 008 B, SHA-256 `6476e259a3a763e2985f22ea6655929e5b313f63ca4bcb976f98b6d50b72140c`) sa v staršom inventári nenachádzal. Interný identifikačný reťazec `Nitemare-3D for Windows V1.0` je v NE súbore potvrdený.

| Behavior anchor | Windows 1.0 / segment 3 | Windows 1.3 / segment 3 | Exact bytes checked |
|---|---|---|---:|
| read_time | `0xD498` | `0xD4A4` | 26 **identických** |
| slow_clock | `0xD4DC` | `0xD4E8` | 63 **identických** |
| frame_clock | `0xD51C` | `0xD528` | 65 **identických** |

Osobitná zmena pri kalibrácii: Win16 **1.0 `3:D5A2`** začína `ENTER 4; PUSH SI; CALL ...`, pričom Win16 **1.3 `3:D5AE`** začína `ENTER 6; PUSH SI; CMP DS:45F6,1; JNE ...; CMP DS:45F4,1; JNE ...` a testuje aj `DS:45F8`. V 1.3 sa teda objavili dodatočné **lokálne brány pred kalibračnou vetvou**; neznamená to automaticky, že kalibrácia 1.0 pri skutočnom spustení nemá žiadnu ochranu v caller-och. V oboch variantoch zostáva časový princíp 8 Hz podložený spoločnými 63 identickými bajtmi slow-clock funkcie.

## 7. Ďalšie originálne obaly a Ghidra archív

- `N3D-11.exe` a `N3D-11(1).exe` sú rovnaké bajty (rovnaký SHA-256) – nie dve verzie.
- `N3D - 11 public libraly.EXE` (74 018 B, DIET/MZ) uvádza 1.1, ale úplná byte-for-byte zhoda jeho **dekomprimovaného** obsahu s `N3D-11.exe` sa ešte nedokázala. Zostáva zvlášť ako distribučný obal/variant, nie ďalší potvrdený unikátny programový build.
- `N3D-11.exe.gzf` (600 197 B) je Ghidra projekt/analytický archív, nie spustiteľný DOS EXE; nesmie byť započítaný medzi verzie hry.

## 8. Otvorené presne formulované otázky – ďalší statický RE-first postup

1. **DOS UI dispatcher 1.1→1.2:** dohľadať všetky zapisujúce inštrukcie k preambule `DS:13E6` vrátane alias pointerov; potvrdiť stará index 0 vs nová podmienená preambula pre všetkých volajúcich a všetkých 23/24 slotov.
2. **RNG call path:** pri 22 priamych callsites na každý build vytvoriť mapu caller → subsystém → vetva → write/read → seed chronológia; pre indirect/nested/IRQ spraviť konzervatívny register a CFG bez tvrdenia runtime parity.
3. **Windows audio import:** rozvinúť Win16 1.6 `3:DF4A` MIDI capability loop, Win16 1.8 `3:E07A/E091` a vnorené load/cleanup vetvy na presné C kontrakty so všetkými chybovými návratmi.
4. **Win16 1.0–1.3 kalibrácia:** analyzovať všetkých callerov `3:D5A2`/`3:D5AE`, podmienky DS:45F4/F6/F8 a dôsledky neuskutočnenej kalibrácie.
5. **Celoprogramová CFG/SSA uzávierka:** 11 856 overených direct-FAR edge záznamov je len podmnožina všetkých `CALL`, `JMP`, `FF`, `RET`, nepriameho dispatchu, event loop, CPU flags, pointer-alias zapisovaní, objektovej animácie, schedulera, secret-door, projectile pool, weapon a renderer inner loops. Tie ostávajú otvorené.
6. **Runtime fallback až nakoniec:** DEMO seed=1 CPU event poradie, nested IRQ, prvý passable tick secret panelu, pixel-perfect/clipping a reálny audio cadence nie je možné doložiť iba z volacích zoznamov.

## 9. Artefakty a opakovateľnosť

Audit Python skript `n3d_re_12build_byte_audit.py` fail-closed porovnáva všetky buildové hashe, rozbaľuje EXEPACK iba do pamäte, kontroluje far-pointer relokácie, RNG reťazec a jump-table handler. Výstup je iba evidenčný JSON a 10 CSV tabuliek; **originálne EXE nie sú súčasťou balíka výsledkov**.

```powershell
python n3d_re_12build_byte_audit.py --root <cesta_k_DOS_1.1_1.2_1.5> --dos-compare-dir <cesta_k_DOS_1.0_1.7_1.9_2.0> --win-dir <cesta_k_Win16_EXE> --output-dir <cesta_k_vysledkom>
```

`N3D_REMAX_StaticPrimitives_12build.hpp` obsahuje iba binárne podložené lokálne reference primitives. C++ test `n3d_remax_static_primitives_test.cpp` úspešne overil všetkých 256 bajtových HP vstupov, 100 000 deterministických RNG krokov a 7 build profiles. Ani táto sada nedokazuje game-wide 1:1 parity.

**Stav záveru:** originálne bajty/identity, presné lokálne vetvy a vybrané direct callsite registre – POTVRDENÉ; kompletný callgraph, nepriamy dispatch, runtime interleaving, všetky vetvy a 100 % behavior+timing+rendering – OTVORENÉ. Percentá celkovej parity sa bez runtime/širšej CFG uzávierky nezvyšujú.

**GitHub archivačná poznámka:** Veľká 9 811-riadková DOS FAR CALL tabuľka je v tomto repozitári uložená ako deterministický `static_byte_evidence/N3D_DOS_reloc_anchored_FAR_CALLs.csv.gz` (gzip, pôvodný CSV po rozbalení). Čisté CSV nezmizlo z pôvodného analytického balíka; ide iba o kompaktnú podobu verejného dôkazového exportu.
