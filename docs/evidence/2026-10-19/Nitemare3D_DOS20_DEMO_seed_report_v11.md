# Nitemare 3D DOS v2.0 — DEMO `seed=1`: statické + runtime uzavretie

**Dátum:** 19. 10. 2026  
**Zdroj:** používateľom dodaný archív `all-nite3d.zip`, DOS v2.0 `nd-3-20`.  
**Nástroj:** DOSBox-X N3D Advanced History v3 (Linux, `DEBUGBOX N3D.EXE` cez pseudoterminál).  
**Referenčný nekomprimovaný EXE:** `N3D-E-20.EXE`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.

## Overený výsledok

**DEMO režim v menu funguje:** po zvolení `Main Menu → Demo` sa spustila automatická demonštrácia a zobrazilo sa `Nitemare-3D -- Demo Mode` v úrovni `1:11`. Toto je samostatný gameplay runtime test (`seed-demo-v9`).

**RNG seed setter vykonaný pri spustení DEMO:** v ďalšom behu (`seed-demo-v11`) sa cielený breakpoint na `17DE:01A6` aktivoval bezprostredne po výbere Demo. Debugger ukázal `PUSH 0001` a `CALL 1A12:31E6` pri `DS=2F95`. Cielený N3DTRACE začína práve týmito dvoma inštrukciami, nie inicializáciou emulátora.

### Presný CPU a pamäťový dôkaz

| Sekvencia | CPU miesto | Operácia | Stav |
|---:|---|---|---|
| 1 | `17DE:01A6` | `push 1` | konštanta seed=1 |
| 2 | `17DE:01A8` | far call | `1A12:31E6` |
| 3 | `1A12:31E6` | vstup setteru | DS=`2F95` |
| 6 | `1A12:31EC` | 16-bitový zápis `DS:[24B8]` | `0001 → 0001` |
| 7 | `1A12:31EF` | 16-bitový zápis `DS:[24BA]` | `0000 → 0000` |
| 12 | `154D:2721` | návrat do volajúcej inicializácie | setter dokončený |

Oba zápisy majú zaznamenanú predchádzajúcu hodnotu (`hasold=1`). Absolútne lineárne adresy sú **`0x31E08`** (low) a **`0x31E0A`** (high). Po inicializácii je stav `0x00000001`. Už pred inicializáciou mal v tomto behu tú istú hodnotu — ide teda o **explicitný reset na 1**, nie o dôkaz, že práve setter vložil dovtedy odlišnú hodnotu.

*Doklady:* `runtime_seed_proof_minimal.json`, `demo_seed_first13.n3dt`, `verify_seed_demo_v11.py`, full raw `trace-000000.n3dt`, snímka `09-breakpoint-display.png`.

### Staticky uzavretý priamy volací reťazec

| Súborový offset MZ | Runtime CS:IP | Úloha |
|---|---|---|
| `0xFD3E` | `154D:28AE` | Vetva menu, jump-table index 6 |
| `0xFD62` | `154D:28D2` | `DS:[4152]=1` (režim Demo) |
| `0xFD68` | `154D:28D8` | Near call inicializačnej rutiny |
| `0xFB8C` | `154D:26FC` | Inicializácia režimu |
| `0xFBAC` | `154D:271C` | Far call pevného seed wrappera |
| `0xFF46` | `17DE:01A6` | `push 1` |
| `0xFF48` | `17DE:01A8` | Far call seed setteru |
| `0x152C6` | `1A12:31E6` | Zápis RNG stavu |

V skúmanej nekomprimovanej binárke sa nachádza **jedno priame volanie** seed wrappera (`9A A6 01 BA 0F` na `0xFBAC`) a **jedno priame volanie** samotného seed setteru (`9A E6 31 EE 11` na `0xFF48`). To nepredstavuje úplný dôkaz neprítomnosti nepriamych volaní alebo aliasovaných zápisov; tie sa musia posúdiť zvlášť. Štyri miesta v kóde priamo kontrolujú `DS:[4152]` (`0x99CB`, `0xACFA`, `0xDE10`, `0xF15F`).

### Rozsah záznamov

| Záznam | CPU udalosti | Pamäťové zápisy | Dôvod skončenia |
|---|---:|---:|---|
| Celý prvý v11 trace | 31 836 | 2 483 | nastavený limit 3 MiB |
| Výrez dôkazu | 13 | 9 | úmyselne ukončený po návrate do volajúceho |

Oba prešli rovnakou automatickou kontrolou a plný trace obsahuje časť nasledujúcej inicializácie/vykresľovania. **Neposkytuje však kompletný DEMO beh**.

## Reprodukcia

1. DOSBox-X v3 spustiť s virtuálnou konzolou/PTY (inak jeho PDCurses debugger nemusí byť dostupný) a pôvodným `N3D.EXE`.
2. V debuggeri nastaviť `BP 17DE:01A6`, pokračovať `RUN`.
3. Po zobrazení Main Menu šípkou dole štyrikrát vybrať **Demo**, stlačiť Enter.
4. Na breakpointe `17DE:01A6` spustiť `N3DTRACE START` a `RUN`, zaznamenať prvé udalosti do `.n3dt`.
5. Overiť: `python verify_seed_demo_v11.py trace-000000.n3dt N3D-E-20.EXE`.

Skript `seed_static_proof_v10.py` kontroluje bajtové signatúry volaní a vetvy menu. Skript `verify_seed_demo_v11.py` validuje CPU priechod, register AX, **staré aj nové hodnoty** oboch RNG slov a návrat k volajúcej funkcii.

## Zvyšné otvorené otázky

- **Prvý RNG draw po DEMO resete** a jeho presný tick a volajúci subsystém ešte nie sú zaznamenané.
- **Poradie všetkých DEMO udalostí a RNG volaní** vrátane stavu na konci DEMO, porovnania s DOS v1.9 a Windows verziami, ešte nie je uzavreté.
- **Bežná hra** a jej inicializácia RNG sú samostatné; tento výsledok preukazuje vetvu *Demo* a nesmie sa automaticky generalizovať na nový normálny level.

**Záver:** statický reťazec `Demo → DS:[4152] → init → push 1 → srand(1)` je priamo spojený s vykonaným breakpointom a strojovým trace. Tento konkrétny dôkazový bod možno označiť za *uzavretý*. Kompletná DEMO/RNG deterministická parita zostáva otvorená.
