# Nitemare 3D DOS v2.0 — DEMO.1 prvé RNG volanie a zmena stavu aktéra (v12)

**Dátum:** 19. október 2026  
**Verzia hry:** Nitemare 3D DOS v2.0 (`nd-3-20`), originálny `N3D.EXE` spustený v DOSBox-X N3D Advanced History v3.  
**Statický obraz:** nekomprimovaný `N3D-E-20.EXE`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.  
**Dôkaz:** `demo_first_rng_actor_minimal_v12.n3dt` (170 CPU inštrukcií, 695 udalostí) + originálny 10 MiB runtime trace (50 824 kompletne uložených inštrukcií, 206 563 úplných udalostí). Automatická kontrola **PASS** pre oba súbory.

## Čo v12 uzatvára

Najprv bola hra spustená cez `DEBUGBOX N3D.EXE`. Breakpoint `BP 17DE:01A6` zasiahol pri reálnom výbere `Main Menu → Demo`. Táto adresa je explicitná inicializácia `PUSH 1` → `CALL 1A12:31E6`, **už nezávisle overená trace v11**. Po zastavení *pred* setterom som nastavil nový breakpoint `BP 17DE:01A0`. Hra následne pokračovala v DEMO režime. Prvý zásah druhého breakpointu pri ďalšom pokračovaní je prvý RNG vstup po tomto resetovaní (v tomto riadenom behu).

Na prvej RNG inštrukcii `17DE:01A0` som spustil `N3DTRACE START` so zapnutými čítaniami a zápismi pamäte a pokračoval cez `RUN`. CPU trace **začína presne** na tejto inštrukcii; neobsahuje BIOS/bootloader ani skoršiu inicializáciu hry. Príslušné screenshoty `07-seed-breakpoint.png`, `09-first-rng-check15.png` a `10-trace-started.png` sú pribalené.

### Presný reťazec

| Krok | CPU adresa / údaj | Runtime dôkaz |
|---|---|---|
| 1 | `17DE:01A0` → `1A12:31F8` | prvá CPU inštrukcia v trace, `CALL RNG` |
| 2 | `DS:[24B8]`, `DS:[24BA]` | prečítané `0001` a `0000`, linear `0x31E08`, `0x31E0A` |
| 3 | `1A12:3213`, `1A12:3216` | zapísané `E2C0`, `0029`, so zaznamenanými starými hodnotami |
| 4 | `17DE:01A5` | RNG wrapper sa vracia s `AX=0029` = **41** |
| 5 | `0CEB:0A3B` | `RETF` pokračuje vo volajúcej rutine s `AX=0029` |
| 6 | `ES:SI=2A21:2A92` | aktér má lineárnu základnú adresu `0x2CCA2` |
| 7 | `ES:[SI+0x17]` | čítanie hodnoty **0**, určuje masku `3` |
| 8 | `ES:[SI+0x14]` | zápis `00 → F8` (signed −8) |
| 9 | `ES:[SI+0x06]` | zápis `0000 → 0018` (24) |
| 10 | `ES:[SI+0x0B]` | zápis stavu **3 → 6** |

RNG matematika: `state=(state*0x343FD+0x269EC3) mod 2^32`; pre pôvodný stav `1` dostávame `0x0029E2C0`, funkcia vracia `(state >> 16)&0x7FFF = 41`.

V binárke je **priamo overená volajúca inštrukcia** pri file offsete `0x58A6` (`0CEB:0A36`), bajty `9A A0 01 BA 0F` = far CALL RNG wrapper; ďalší príkaz na offsete `0x58AB` je `MOV ES,[BP+8]`. Stack reads návratu overujú dvojicu `0A3B:0CEB`. Statická sekvencia od `0CEB:0A3B` porovnáva `byte ptr ES:[SI+0x17]` s `1`, pomocou `SBB/AND/ADD` vytvára masku `3` alebo `7`, potom vyberá vetvu pomocou `AX & mask`. V konkrétnom runtime `mode=0`, teda `41 & 3 = 1`. Vykonaná vetva nastavuje `ES:[SI+0x14] = F8`, zatiaľ čo neskôr nasleduje `ES:[SI+6] = 24` a `ES:[SI+0x0B] = 6`.

**Dôležitá nová informácia:** prvým RNG spotrebiteľom po DEMO resete v tomto behu je **rutina aktéra v segmente `0CEB`** (`0CEB:0A36`), nie časovač `1061:1D5B`, ktorý bol zachytený v predchádzajúcom bežnom E1M1 behu. Toto nie je dôkaz, že medzi dvoma režimami je odlišný globálny RNG algoritmus; mení sa aktivovaná vetva a okolnosti herného stavu.

## Rozsah a hranice dôkazu

Trace skončil na explicitnom **limite 10 MiB**, nie na konci DEMO. Dekodér prečítal 50 824 kompletných CPU inštrukcií a 206 563 úplných udalostí vrátane čítaní pamäte. Súhrn emulátora hlási 50 825 inštrukcií a 206 564 udalostí: kód trace inkrementuje počítadlá **pred kontrolou dátového limitu**, takže posledný odmietnutý záznam sa do textových čítačov zahrnul, ale do binárneho súboru už nie. Preto pre dôkaz používame počty úplne parsovaných binárnych záznamov. Obsahuje prvé RNG volanie, potom prevažne súvisiaci herný/obrazový výpočet. **Len prvé RNG volanie** sa nachádza v tomto krátkom okne; nevyplýva z toho, že zvyšok DEMO ďalší RNG nevolá. Udalosti `DS:[1738]` (absolútny tick) sa v tomto výreze nečítali/nepísali, a tak **presné číslo DEMO ticku nie je známe**. Nevieme ani index spracovávanej vstupnej udalosti `DEMO.1` či presnú triedu aktéra; tie zostávajú samostatnými úlohami. Priame CPU/memory dôkazy nezaručujú dokonale rovnaký pixelový výstup alebo súhrnný výsledný RNG stav po prehratí.

## Reprodukcia na tom istom builde

1. Spustiť pôvodné `N3D.EXE` v Linux DOSBox-X N3D Advanced History v3 cez `DEBUGBOX N3D.EXE` (terminál/PTY potrebný pre debugger).
2. Nastaviť `BP 17DE:01A6`; pokračovať `RUN`, v hre vybrať `Main Menu → Demo`.
3. Na zasiahnutom breakpointe pre seed nastaviť `BP 17DE:01A0`; pokračovať `RUN`. Prvý následný zásah je zachytený RNG vstup.
4. Nastaviť `N3D_TRACE_DIR`, `N3D_TRACE_MEMORY=1`, `N3D_TRACE_READS=1`, `N3D_TRACE_AUTOSTART=0`, `N3D_TRACE_LIMIT_MB=10`, `N3D_TRACE_VRAM=0` a ostatné video možnosti vypnuté; vykonať `N3DTRACE START`, `RUN`.
5. Pri vstupe do RNG vytvorenú `.n3dt` binárku overiť skriptom `python3 verify_demo_first_rng_v12.py trace-000000.n3dt N3D-E-20.EXE`. Skript kontroluje RNG stav pred/po, návrat, volajúcu adresu, prácu so zásobníkom a zmeny aktéra.
6. Na krátkom výreze (`demo_first_rng_actor_minimal_v12.n3dt`) je ten istý dôkaz reprodukovateľný bez veľkého originálneho záznamu.

## Ďalší cieľ v13

**Statika ako prvá:** zmapovať `0CEB:0A36` na nadradený dispatch a triedu aktéra (cez volajúcich, typové polia a dátové záznamy); analyzovať všetky vetvy masky `3/7` a dosiahnuteľnosť pri `mode=0/1`. Potom **cielený runtime** na kontrolu `DS:[1738]` a indexu `DEMO.1` *už pri RNG breakpointe*, a až následne pokračovať na 2. RNG volanie a poradie naprieč subsystémami.
