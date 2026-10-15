# RE MAX v0.35 — oprava RNG censusu: 22 volaní, nie 20

**15. október 2026 — priama analýza používateľom dodaného originálneho DOS v2.0.**

**Pôvodný program:** unpacked DOS v2.0 MZ *load image*, presne 171 360 B,
SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.
Všetky uvedené adresy sú **offsety v unpacked obraze za MZ hlavičkou**, nie
aktuálne absolútne segmenty emulátora alebo Win16 offsety.

## 1. Hlavný nález: doterajšia tabuľka mala neúplný zoznam

Úplný bajtový sken známej priamej far-call sekvencie

```text
9A A0 01 BA 0F    ; CALL FAR 0FBA:01A0
```

všetkých 171 360 B pôvodného load image našiel **22 výskytov** (nie 20):

```text
2478 525E 5582 5666 56A6 573F 58A7 85AD
8860 886C 887C 9A68 9A77 9C98 9CC2 9D6E
9F0C 9F36 9FE3 A047 A12B B276
```

**Nové položky:** `8860` a `886C`. Nejde o dátový false-positive.
Pôvodná rutina výpočtu incoming damage začína na `87D8`, triedový
rozbočovač na `8829` používa 23 WORD cieľov v tabuľke `882E`.
Po normalizácii CS base `83D0` tabuľka obsahuje skutočné adresy:

| Trieda OBJECT+06 | Adresa vetvy | Priamy RNG a následná maska |
| --- | --- | --- |
| `08` | `8860` | jeden odber, `RNG & 7` |
| `09 / 0A` | `886C` | jeden odber, `RNG & 15` |
| `11 / 12 / 13 / 14` | `887C` | jeden odber, `RNG & 31` |

Presné inštrukcie:

```asm
8829   JMP WORD PTR CS:[BX+045Eh]
8860   CALL FAR 0FBA:01A0
8865   AND AX,0007h
886C   CALL FAR 0FBA:01A0
8871   AND AX,000Fh
887C   CALL FAR 0FBA:01A0
8881   AND AX,001Fh
```

Skontrolované sú všetky 23 cieľové WORD hodnoty. Starý strict-verifier
`tools/n3d_trace_audit.py` aj C++ pole v `N3DV020VerificationHarness`
legitímne RNG callsites `8860/886C` odmietali. Oprava je nevyhnutná
na správnu diagnostiku originálneho DEMO a combat záznamu.

**Dôležitá hranica:** 22 je úplný počet *doslovných opcode vzorov pre tento
konkrétny far-call cieľ* v identifikovanom statickom obraze. Nie je to počet
všetkých dynamických RNG volaní počas hry: tie isté callsites sa môžu použiť
opakovane, existujú podmienené a vnorené cesty a treba ešte kontrolovať
prípadné nepriame volania. Originálny runtime trace nebol získaný.

## 2. Nové lokálne priradenia RNG spotrebiteľov

Pre každý callsite možno staticky pomenovať *bezprostrednú aritmetiku,
zápis alebo token*. To ešte automaticky nedokazuje kedy sa podmienka vykoná
vo všetkých mapách a všetkých obtiažnostiach.

| Callsite | Príjemca/vetva | Pôvodný výpočet |
| --- | --- | --- |
| `2478` | SPAN animácia | `RNG & 7`, výber variantu a odmietacie opakovanie |
| `525E` | GUARD state 06 | blokovaná X/Y os, bit0 |
| `5582` | GUARD prechod z 7/8 do 1 | `RNG % 8` → `GUARD+06 timer`, potom state 1 |
| `5666 / 56A6 / 573F` | GUARD planner | rôzne timer/direction vetvy, presná dynamická chronológia otvorená |
| `58A7` | GUARD state 13 | `RNG % 80 + 8` |
| `85AD` | damage/projection formula | `RNG % 25` plus projekčná zložka |
| `8860 / 886C / 887C` | incoming player damage | masky `7 / 15 / 31` podľa triedy |
| `9A68` | efektový parameter | `RNG % 62` → `DS:3632` |
| `9A77` | ďalší parameter toho istého efektu | nasledujúci `RNG % 36` → `DS:3630` |
| `9C98 / 9CC2` | class-SFX variant | `%3+0x17 / %4+0x4B` |
| `9D6E` | class-SFX variant | `%3+0x0B` |
| `9F0C / 9F36` | class-SFX variant | `%3+0x38 / %2+0x36` |
| `9FE3 / A047` | resource variant | `RNG % 7`, tabuľkový rejection loop |
| `A12B` | efektový časovač | `RNG % 240 + 160` → `DS:3634` |
| `B276` | premietaná OBJECT animácia `B22C` | `RNG & 7` → `OBJECT+02`, re-draw pri neplatnom descriptor variante |

V evidencii sú jednotlivé aritmetiky označené ako **static CONFIRMED**
iba na úrovni konkrétnej inštrukcie. Doterajšie GUARD-planner/ordering
spojenia zostávajú `STRONG` tam, kde chýba detailná behová preukázateľnosť.
Úplné názvy zvukov, všetkých scénických efektov a každá runtime
reachability vetva nie sú týmto tabuľkovým auditom potvrdené.

## 3. B276: dôležitý nový zdroj driftu DEMO

V `B22C` (projekčná animácia identifikovaná vo v0.34):

```asm
B242   INC BYTE PTR ES:[SI+03h]       ; OBJECT.frame
...
B276   CALL FAR 0FBA:01A0
B27B   AND AL,07h
B280   MOV BYTE PTR ES:[SI+02h],AL    ; variant
...
B293   CMP BYTE PTR [BP-01h],00h     ; high byte descriptor word
B297   JE  B276h                     ; ďalší RNG draw
B29C   MOV BYTE PTR ES:[SI+03h],AL
```

Po tom, ako frame prekročí limit vybraného variantu, vytvorí sa
**minimálne jeden** RNG draw. Pri každom vylosovanom variante, ktorého
descriptor word má nulový horný bajt, sa volanie opakuje.

To znamená, že **jedna viditeľná animačná udalosť nemusí znamenať jeden RNG
odber**. Počet drawov môže meniť globálny RNG stav pred ďalšou AI, zbraňou
alebo DEMO akciou. Kódová cesta volaná aj cez projekciu projektilov neznamená,
že každý objekt je skutočne viditeľný – platia skoršie príznaky a clipping
podmienky z v0.34.

Ak všetky dostupné voľby spĺňajú odmietaciu podmienku, lokálny kód nemá
explicitnú ukončovaciu hranicu. To **nie je dôkaz zacyklenia v dodaných mapách**:
treba najskôr preveriť skutočné descriptor tabuľky a reachability.

## 4. GUARD 5582: presný samostatný RNG odber

Funkcia `5510` prechádza 26-bajtové GUARD záznamy:
- vyžaduje `GUARD+0A == 0` a zhodu subtype/selector `GUARD+0E`
  s globálnou hodnotou `DS:4188`;
- starý `GUARD+0B state` musí byť `7` alebo `8`;
- potom vykoná `5582 CALL RNG`, `IDIV 8`, uloží remainder
  `0..7` do `GUARD+06` a zapíše `GUARD+0B = 1`.

Presné writer sites sú `5590` (timer) a `5594` (state).
Táto podmienená RNG vetva nebola vo v0.26 priradená ku konkrétnemu
spotrebiteľovi; teraz je lokálny zápis staticky uzavretý.

## 5. Zriedkavá nedosiahnuteľná podmienka v dvoch rutínach

V `9FE3` a `A047` sa náhodné 15-bitové číslo delí signed
`IDIV 7`. Zvyšok pri nezápornom vstupe musí patriť do `0..6`.

Následné `CMP SI,CX; JE retry` porovnáva remainder s `CX=7`.
**Táto konkrétna `JE` vetva je pod pôvodnou RNG návratovou doménou matematicky
nedosiahnuteľná.** Druhá vetva, ktorá testuje nulový bajt tabuľky na
`A00C/A070`, však môže odmietnuť kandidáta a skutočne zopakovať
RNG draw. Nesmie sa teda vymazať celý rejection loop.

Toto je priamo doložený príklad **mŕtvej podmienky v inak aktívnej funkcii**.
Syntetické testy prechádzajú celú konečnú doménu 32768 výsledkov bez
jedinej hodnoty remainder 7.

## 6. Dôsledok pre porovnávanie a 1:1

Vo v0.35 sa opravujú **tri navzájom prepojené zdroje**:

- `N3DV020VerificationHarness.hpp`: 22 položiek namiesto 20;
- `n3d_trace_audit.py`: strict zoznam prijíma aj `8860/886C`;
- `N3DV026GuardRngCoupling.hpp`: rovnakých 22 zoradených položiek
  s doloženými lokálnymi aritmetickými spotrebiteľmi.

V0.30 diferenčný comparator ďalej porovnáva **presné chronologické poradie
volaní** a nepreskupuje riadky. Rovnaký konečný RNG stav nedokazuje, že
boli spotrebované rovnakými subsystémami. Pri zmene viditeľnosti objektu
treba naviac logovať `2478` aj `B276` vrátane opakovaní.

Znovu overiteľný read-only binárny sken:

```sh
python tools/n3d_v035_rng_census.py /path/to/N3D_DOS_v2.0_IDA.EXE
python -m unittest discover -s tests -p "test_n3d_v035_rng_census.py" -v
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build --target n3d_v035_rng_census_test
ctest --test-dir build -R n3d_v035_rng_census_test --output-on-failure
```

Overenie používa SHA-256 gate pred akýmkoľvek povýšením offsetov,
presne porovnáva **22 inline far-CALL vzorov**, 23 položiek dispatch tabuľky
a 23 krátkych inštrukčných kontrol. Originálne bajty EXE nie sú v repozitári.

**Naďalej OPEN:** úplné množstvo nepriamych RNG volaní, vykonané poradie
od DEMO `seed=1`, načítané variant-table dáta v každej scéne, počet
vnorených FAST, presný RNG stav po LOAD a pixel-perfect rendering. Preto
sa **nezvyšuje globálne percento 1:1 parity**. Tento commit opravuje kritický
statický podklad používaný pre budúci skutočný trace.

## v0.36 protected-hit RNG scheduling consequence

The 22 static callsite census was NOT changed by v0.36. Instead the cross-version caller order was refined: when the DOS v2.0 actor-damage receiver `6A70` is invoked, it calls `87D8` **before** the invulnerability and terminal-state guards, whereas DOS v1.0/1.7/1.9 guard first. Classes with RNG damage branches `8860/886C/887C` can therefore advance the v2.0 shared RNG stream despite an unchanged HP value. A nonzero computed damage byte also arms `DS:417A` timer=3 before protection. Do not apply this to all hazard/projectile paths or imply a captured seed=1 DEMO trace. See [v0.36](V036_REMAX_PROTECTED_HIT_RNG_ORDER.md).
