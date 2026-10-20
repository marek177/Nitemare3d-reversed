> Archived supplied source report: REPORT_SK(20261020-200403).md. Integrated as attributed evidence; private source artifacts and its original-data verifier were not rerun for this bulk update. See [current validation and limits](../../BULK_UPDATE_20261020.md).

# Nitemare 3D DOS v2.0 — D02-N: pôvodné čítania/zápisy GUARD + pôvodný reštart DEMO

**Dátum dôkazu:** 20. 10. 2026  
**Úroveň:** `ORIGINAL_RUNTIME_BOUNDED` + `ORIGINAL_STATIC_SHA_GATE`  
**Nie je to:** celý prvý globálny divergence point, porovnanie originál ↔ remake, úplná deterministická parita ani dôkaz, že iba CPU-cycles spôsobujú všetky odlišnosti.

## 1. Vstupy a meracia metóda

Dva samostatné behy **originálneho DOS v2.0** v DOSBox-X N3D Advanced History v3 pod Xvfb, s originálnym `DEMO.1`, konfigurácie `cycles=fixed 3000` a `cycles=fixed 7000`. Externý hostiteľský filter `LD_PRELOAD` zachytáva z pôvodného `N3DTRC01` iba inštrukcie cieľových adries plus pôvodné RAM čítania (`R`) / zápisy (`W`) vybraných polí. Nekopíruje ani nemení bajty pôvodného herného EXE alebo dát. Stopa sa spúšťa po načítaní hry; výber bol obmedzený na **DEMO scheduler návštevy 1024–1110** a hra bola zastavená na návšteve 1111.

Identita:

- Pôvodný komprimovaný EXE SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Pôvodný dekomprimovaný **MZ load image** (171 360 bajtov): `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.
- Pôvodné DOS `DEMO.1`: `25ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840`.
- Nameraná MZ fyzická báza oboch behov: `0x8240`. GUARD pool segment `2A21`, herný DS `2F95`.
- Overené originálne opcode kotvy: **17/17**. Niektoré musia byť overené na inštrukčnej hranici vrátane predpony (`IMG:C014` vynuluje celý dword). 

| Meranie | 3000 | 7000 |
|---|---:|---:|
| CPU inštrukcie prebehnuté od začiatku trace (počítadlo emulátora) | 659 058 390 | 1 085 009 972 |
| Zachované vybrané CPU inštrukcie `I` | 31 295 | 34 019 |
| Zachované pamäťové čítania `R` | 27 880 | 30 944 |
| Zachované pamäťové zápisy `W` | 13 683 | 13 472 |
| Zachované pôvodné záznamy I/R/W spolu | **72 858** | **78 435** |
| Hranica sledovaných návštev | 1024–1110 | 1024–1110 |

Výberové logovanie znamená, že sme nenasnímali všetky CPU vetvy alebo každý bajt RAM. Poradie udalostí vo vnútri originálneho trace sa zachovalo pomocou nezmenených poradových čísel CPU inštrukcie a udalosti. Emulátor bol inštrumentovaný a prehrávanie mohlo byť ovplyvnené časovaním hostiteľa; dve rôzne konfigurácie preto **nie sú čistý kauzálny experiment iba jednej premennej**.

## 2. Najskoršia zachytená odlišná GUARD vetva je už na návšteve 1024

Pri rovnakom poradovom čísle návštevy scheduleru **1024** je frame counter `DS:16FE = 1031` na oboch behoch, ale **slow counter sa už líši**: `DS:16F6` po zvýšení = **972** (3000) oproti **490** (7000). Pri štyroch aktéroch **GUARD 5–8** číta dispatcher počiatočný `GUARD+0x0B` stav `7` v oboch behoch. Následne:

- **3000:** po pomocnej rutine `IMG:5BE5` vykoná vetvu, číta `GUARD+0x0A` na `IMG:5BF7`, zapisuje stav **7→2** na `IMG:5C6C` u GUARD 5/6/7/8.
- **7000:** vetva na `IMG:5BED` preskočí toto čítanie/zápis; aktéri zostávajú v stave 7 počas tohoto checkpointu.

Kľúčové pôvodné ASM bajty sa zhodujú:

```asm
IMG:5BE5  E8 5A F7           CALL IMG:5342
IMG:5BEB  0A C0              OR AL,AL
IMG:5BED  0F 84 2F 03        JE IMG:5F20
IMG:5BF7  26 80 7F 0A 03     CMP BYTE PTR ES:[BX+0A],03
IMG:5C6C  26 C6 47 0B 02     MOV BYTE PTR ES:[BX+0B],02
```

**Záver (ohraničený):** prvá odlišná GUARD vetva v **sledovanom intervale**, nie úplne prvá príčina celej sekvencie. `IMG:5342` treba ďalej dosledovať s pozíciou hráča, pozíciou a orientáciou objektu, výsledkom AL a súvisiacimi hodinami; samotný GUARD timer nie je dostatočné vysvetlenie tejto skoršej vetvy. Slow counter je rozdielny už pri štarte sledovaného okna.

## 3. Prečo sa GUARD 5 pri špeciálnom stave 21 vrátil do iného stavu

Skutočné pôvodné RAM zápisy/čítania v `D02N_*_mem_events.csv` dokazujú:

| Pri návšteve | Beh 3000 | Beh 7000 |
|---|---|---|
| 1042 / `IMG:6113` | `GUARD5.state`: **5→21** | `GUARD5.state`: **0→21** |
| 1042 / `IMG:610C` | Zápis `GUARD5+0x0C=5` | **Žiadny zápis**, zostáva staršia hodnota `4` |
| 1046 / `IMG:5F14` | Čítanie `+0x0C=5` | Čítanie `+0x0C=4` |
| 1046 / `IMG:5F17` | Návrat `state 21→5` | Návrat `state 21→4` |
| Následok | GUARD5 dostane RNG časovač v návšteve 1048 | GUARD5 prejde ešte ďalšou stavovou vetvou a RNG časovač v 1052 |

Originálny kód `IMG:6103` testuje či predchádzajúci stav nie je `0`; pri nenulovom stave ho prenesie do `+0x0C` (`IMG:610C`) pred zápisom špeciálneho stavu `0x15` na `IMG:6113`. Neskôr návratová vetva `IMG:5F14/5F17` číta `+0x0C` a obnoví `+0x0B`. Je to **presná lokálna mechanická príčina iného návratu GUARD5**.

Aj v originálnych zápisoch na `IMG:574F` je potvrdené celé **16-bitové WORD** časovača `DX`, nie iba jeho nízky bajt:

| Beh | Scheduler | GUARD → časovač |
|---|---:|---|
| 3000 | 1044 | 6→8, 7→9, 8→14 |
| 3000 | 1048 | 5→13 |
| 7000 | 1052 | 5→8, 6→9, 7→14, 8→13 |

**Pozor na dôkazový rozsah:** ide o presné preukázané zápisy pri dvoch behoch, nie všeobecný výsledok pre všetkých GUARD a všetky obtiažnosti.

## 4. Originálny DEMO reštart overený pamäťovými zápismi

V **7000-cycles** behu na návšteve **1085**:

1. `IMG:F9C3`: `DS:3CD6` DEMO režim **4→5**.
2. `IMG:F993`: DEMO režim **5→3**.
3. `IMG:C014`: `DS:4540` render generation **1114→0**, pôvodné opcode `66 C7 06 40 45 00 00 00 00`.
4. `IMG:6CFC`: DEMO input `DS:3F50` **0x0090→0x0000**.
5. `IMG:BF36`: render generation sa znovu zvyšuje od 0.
6. Návšteva **1086**, `IMG:6DDA`: DEMO režim **3→4**.
7. Návšteva **1092**, `IMG:6DF6`: prvý znovu aplikovaný input **0x0002**.

To je dôkaz konkrétneho **resetu herného/frame stavu a nového začiatku DEMO**, nie iba podobnosti rekordov. Pri 3000-cycles v tom istom okne `DS:4540` neprešiel resetom a pri návšteve 1092 sa ďalej opakuje posledná maska `0x0090`. Toto nijako nedokazuje definitívnu koncovú politiku prehrávača vo všetkých podmienkach.

## 5. Úroveň uzavretia a ďalšie dôkazy

| Dôkazová povinnosť | Stav po D02-N |
|---|---|
| Zaznamenať skutočné GUARD+0x06/+0x0A/+0x0B/+0x0C | **ORIGINAL RUNTIME VERIFIED — v okne 1024–1110 pre aktérov 5–8** |
| Prečo GUARD5 obnoví 5 alebo 4 zo state21 | **ORIGINAL STATIC + RUNTIME VERIFIED — lokálny mechanizmus** |
| Vstup do rozdielnej vetvy GUARD na návšteve 1024 | **ORIGINAL RUNTIME VERIFIED — ohraničený scenár** |
| Prečo prvotne zlyhá/podarí sa vetva pomocníka 5342 | **OPEN — pôvodné súradnice, AL a LOS + clock causal gate** |
| DEMO 7000-cycles skutočne reštartuje state | **ORIGINAL RUNTIME VERIFIED — reset pri návšteve 1085** |
| Kompletná časová kauzalita a nezávislosť od host instrumentation | **OPEN** |
| Original ↔ clean-room binárne stavové, timing, framebuffer/audio zero-diff | **OPEN** |

Nasledujúca etapa D02-O: pri prvom rozchode zachytiť `AL` návrat z `IMG:5342`, world X/Y hráča, GUARD→OBJECT prepojenie a X/Y/zorný test, lokálne/frame/slow kvantizačné kľúče. Rozhodovať podľa prvého **podmieneného CPU branch** a jeho pôvodných vstupov; nesprávne nezrovnávať behy podľa indexov návštev, ak `slowCount` je výrazne iný.

## 6. Reprodukcia

Balík obsahuje pôvodné **rôzne surové filtrované trace** (`traces/`) a odvodené CPU+R/W CSV (`evidence/`), priamy filter kód a nástroje (`src/`), regresné testy (`tests/`) a dvojicu konfiguračných súborov. Pôvodné komerčné EXE/DEMO/IMG/MAP ani kompletné RAM dumpy nie sú súčasťou balíka.

Po získaní správneho pôvodného dekomprimovaného MZ load image (SHA podľa §1):

```bash
python3 src/d02n_proof.py \
  --image /private/N3D-DOS20-original-unpacked-load-image.bin \
  --3000 traces/D02N_3000_original_rw_sparse.n3dt \
  --7000 traces/D02N_7000_original_rw_sparse.n3dt \
  --output /tmp/d02n-proof.json
python3 -m unittest discover -s tests -p 'test*.py' -v
```

**D02-N:** 17/17 pôvodných opkódových kotiev, oba original CPU+RAM trace úspešne overené, **18/18 syntetických regresných testov PASS**, integračný pôvodný test originálnych trace PASS. Percentá projektu ani GitHub neboli umelo navýšené.
