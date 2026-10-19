# Nitemare 3D — D01 seed=1: ďalší cieľ a statický uzáver

**Dátum:** 19. 10. 2026  
**Metodika:** RE-first; presné pôvodné bajty → podmienený runtime → 1:1 porovnanie.  
**Status:** **D01 OPEN**, čiastočný statický uzáver bootstrapu/rekordov/EOF callsite.  
**Zdroj:** originálny DOS v2.0 `N3D-UNFU.exe`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`; lokálne vlastnené originálne `DEMO.1`. Originálne komerčné dáta nie sú súčasťou správy.

## 1. Úplne konkrétny hlavný cieľ

Pre prirodzené spustenie DEMO.1 preukázať **prvý vykonaný RNG odber po seed reset** s presným pôvodným callerom, dôvodom vetvy, stavom pred/po, návratovou hodnotou a polohou v plánovači. Potom nepretržite pokračovať až po prvý gameplay input a ďalej po EOF.

Nie je prípustné považovať `result=41` za dôkaz, že prvým spotrebiteľom bol konkrétny subsystém. Je to len prvá hodnota matematického LCG zo seedu 1.

## 2. Nové statické original-byte checks

Pôvodný EXE prešiel presnou hash bránou a **16 byte-window kontrolami** v nástroji `n3d_d01_seed1_gate_audit.py`.

| Kód (offset MZ image) | Zistenie | Hranica dôkazu |
| --- | --- | --- |
| `F9AC` | `CALL FAR 0FBA:01A6`, seed-helper | Potvrdený priamy CALL do helpera. |
| `FD46` | `PUSH 1`, `CALL FAR 11EE:31E6`, `ADD SP,2`, `RETF` | Potvrdené nastavenie argumentu; interný kód CRT srand mimo auditovaného okna. |
| `F9B1` | `DS:[4540] = 0` | Návratová hranica po seed-helper volaní a reset generácie obrazu. |
| `F9BA` / `F9BF` | Volanie prípravy klávesnice, potom `E964` | Priama inicializačná kontrolná sekvencia. |
| `6D04` | DEMO mode dispatcher | Lokálna cesta modes 1–5. |
| `6DC9` / `6DDA` | Prvé čítanie ôsmich bajtov a nastavenie mode=4 | Priame okno čítania a writer mode. |
| `6DE4–6DF9` | Porovnanie render counter s record counter; zápis vstupu; čítanie ďalšieho rekordu | Lokálne potvrdené poradie. |
| `6E07–6E0D` | `ADD SP,6; PUSH CS; CALL 6CD0` bez lokálneho `TEST/CMP AX` | Volajúca funkcia nekontroluje počet prečítaných bajtov. Účinky v CRT/na EOF zostávajú OPEN. |

**Podstatné:** `F9AC` a `FD46` sa líšia od RNG draw helpera `0FBA:01A0`. Prvé slúži na *nastavenie seedu*, nie na spotrebovanie RNG čísla.

## 3. DEMO.1 data audit

- Presne **275** osem-bajtových rekordov za 6-bajtovou hlavičkou.
- Prvý `key=0x48E0, input=0x0002, counter=8`.
- Posledný `key=0x74E0, input=0x0090, counter=1074`.
- Počítadlá sú neklesajúce, **4** susedné dvojice majú rovnaký counter.
- Nevyplýva z toho dĺžka skutočného prehrávania v sekundách ani EOF správanie.

Práve údaj o ignorovaní návratovej hodnoty na `6E07` **zužuje** D04, ale sám nezatvára D04: treba overiť implementáciu CRT read, chybový stav, skutočný buffer, ďalšie rekordy a menu/game mode.

## 4. Audit starších experimentálnych N3DT capture súborov

Tri už existujúce capture sessions boli skontrolované **samostatne**, aby sa ich opakované event sequence numbers nikdy neprelínali.

| Capture session | Veľkosť | Seed helper, post-seed return, priamy RNG draw |
| --- | ---: | --- |
| runtime-capture | 2 097 152 000 B | 0 / 0 / 0 |
| focused-trace | 1 468 006 352 B | 0 / 0 / 0 |
| test-trace | 78 643 120 B | 0 / 0 / 0 |
| **Spolu** | **3 643 801 472 B** | **žiadny kvalifikovaný záznam** |

Toto neznamená, že hra RNG nevolala. Naopak, uvedené raw sessions **nedokumentujú požadovaný seed-reset interval**; časť zachytáva činnosť debuggeru. Ich veľkosť nie je dôkazová kvalita.

## 5. Nový nástroj

`n3d_d01_seed1_gate_audit.py` (Python 3, stdlib):

1. **`static`** striktne kontroluje fingerprint a originálne opcode okná a štruktúru DEMO.1. Žiadne originálne bajty ani herné zdroje nenahráva do výstupu.
2. **`trace`** číta rotované N3DT v1 `.n3dt`, vyhľadáva vykonaný seed-helper call, návratovú hranicu a chronologicky prvý priamy `CALL FAR RNG`. Počítanie viaže na ID udalostí, nie sortované offsety; bráni zlepeniu samostatných capture sessions.
3. **`test`** overuje syntetické markery, chronológiu a fail-closed správanie pri chýbajúcom resete.

Použitie:

```bash
python n3d_d01_seed1_gate_audit.py test
python n3d_d01_seed1_gate_audit.py static --exe /sukromne/N3D-UNFU.exe --demo /sukromne/DEMO.1 --output static.json
python n3d_d01_seed1_gate_audit.py trace /sukromne/n3dt/session-xxx --output first_rng.json
```

**Dôležité obmedzenie:** `trace` potvrdí maximálne **prvého kandidáta na priamy RNG CALL po pozorovanom seed-helper return**, nie úplnú absenciu skoršieho nepriamo volaného RNG. Na úplnú D01 je potrebná kontrola indirect CALL a CRT vstupov, stavov RNG a uzavreté hranice capture. Marker obsahuje prvé tri opcode bajty, preto je tolerantný k DOS relocáciám segmentového operandu `CALL FAR`.

## 6. Exaktný akceptačný test D01

- Original DOS2 game/DEMO hash (build-scoped).
- Runtime zachytáva **prirodzené** spustenie demo bez patchovania gameplay state.
- Príslušný interval začína *pred* `F9AC`, prejde helperom `FD46`, potvrdí návrat na `F9B1` a končí *po* prvom/ďalších RNG drawoch.
- Pri každom RNG evente: `caller_offset`, vykonaný `CS:IP`, `state_before`, `state_after`, `AX_result`, `scheduler_invocation`, `call_depth`, `mode`, `slow_counter`, `render_counter`, `consumer`.
- Ak naozaj prvý stav pred draw je `1`, hodnota po draw musí byť `0x0029E2C0`, výsledok `41`.
- Nepriame a wrapper callers nie sú ignorované; bez ich censusu zostane D01 iba **first-direct-only**.
- Záznam je celistvý a ak je neskôr porovnaný s clean-room portom, porovnáva sa bez tichého preusporiadania eventov.

## 7. Nasledujúci konkrétny postup

A. Dokončiť statický transitive callgraph `F9B1 → F9BA → E964`, a pred začatím čiastočných výpisov určiť všetky možné pre-seed/post-seed vratné cesty.  
B. V tracer-e použiť **start-on-post-seed** PC/byte hranicu alebo debuggerom spustiť krátky a overený interval. Nahrávanie počas nevykonávaného debuggeru nie je dôkaz.  
C. V prvom rozsahu pozorovať tiež CRT RNG callee a nepriamy FAR call, nie iba 22 `9A A0 01` opcodes.  
D. Uzavrieť D01, až potom expandovať D02 (RNG ledger cez scheduler/renderer/GUARD až po prvý input), D04 EOF a ďalej PROJECTILE.

**Celkové % sa nemenia.** Toto je lokálne overenie z originálnych bajtov a presnejšie definovaný runtime test, nie ešte prvé úspešné vykonané DEMO RNG pozorovanie.
