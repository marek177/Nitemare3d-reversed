import json
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'pass1_startup_segments';s=json.loads((d/'summary.json').read_text());p=json.loads((d/'independent_partition_check.json').read_text())
text='''# PASS1: startup segmenty, BSS a DOS verzia

Šesť bajtov v troch WORD poliach má nový dôkaz. Skutočný čistý posun v mape je **2 B CLASSIFIED ONLY → PARTIAL**, ostatné 4 B boli už PARTIAL. Typované polia a predchádzajúce zdroje sa môžu prekrývať; report nepočíta 6 B ako novú byte coverage. Žiadny DEEP VERIFIED.

| Image interval (koniec exkluzívny) | Offset v DGROUP | Nový dôkaz |
|---|---|---|
|[297EC,297EE)|20DC|SS WORD snapshot SP po dvoch sentinel PUSH|
|[29830,29832)|2120|verzia DOS po XCHG AL,AH: major v hornom BYTE|
|[29832,29834)|2122|pôvodný AX z DOS version vetvy: major v dolnom BYTE|

Výklad 2122 ako startup_mode v staršej malej dávke sa týmto spresňuje: lokálna hodnota vzniká z DOS version výsledku. Neskoršie porovnanie AL s 2 sa preto nemá samo interpretovať ako herný režim. Staršie zdrojové záznamy sú historické; aktuálne spresnenie je pass1_startup_segments/data_fields.csv. Úplný zmysel všetkých neskorších použití tým nie je uzavretý.

## Statický kontext a vykonaný úsek

11EE:0018 nastaví AH=30h, INT21 a skontroluje AL>=2. Replay začína až v 0025 s poskytnutým AX a PSP kontextom a končí pred 00B3. Celý packed EXE entry, DOS version interrupt, chybný prechod a voliteľný callback sa nevykonávajú. Export startup_prefix_context.csv overuje pôvodné bajty aj nezávislý disassembly rozsahu 0018..00B3. Nie je to nový celý funkčný rozsah v bounded katalógu.

```text
DI = relocated DGROUP segment
SI = min((PSP.word[2] - DI) mod 65536, 1000h)
CLI; SS = DI; SP += E02Eh; STI
ak ADD SP pretieklo: error cesta (v tejto dávke nereplayovaná)
SS:2122 = incoming AX; swap AL/AH; SS:2120 = AX
SS:20E0 = low16(SI << 4) - 1
SS:20E2 = SS
SP &= FFFEh; SS:20E6 = SP
push FFFEh; SS:20EC = SP
push 0001h; SS:20E8 = SS:20EA = SS:20DC = SP
PSP.word[2] = SI + DI
INT21/AH4A s ES=PSP a BX=(nový top - PSP)
SS:211E = DS // stále PSP v tomto bode
ES = SS; CLD
zero ES:[2650h,E030h)
DS = SS // 00B1 PUSH SS,00B2 POP DS
```

Pred voliteľným inicializátorom v 00B3 je preto v tejto ceste **DS=ES=SS=DGROUP** a DF=0, IF=1. Rovnosť sa nesmie preniesť cez ľubovoľné neskoršie callee bez vlastného dôkazu. Startup zápisy cez SS do 20E2 a okolitého near-heap stavu majú v tomto okne doloženú väzbu na následný DS. Pred 00B2 pritom DS ostáva PSP; automatické mapovanie všetkých skorých DS operandov na DGROUP by bolo chybné.

BSS je [2650,E030) v DGROUP, presne 47 584 B, image-relative [29D60,35740). Začína na konci rozbaleného file image a nepatrí medzi 57 295 auditovaných file bajtov. Rovnosť rozsahu tu potvrdzuje pôvodná REP STOSB a guard kontrola, nie nulový vzhľad dát. DOS resize interrupt je modelovaný ako úspešný a zachovávajúci registre; prirodzené failure správanie sa neuzatvára.

## Kontrolovaná emulácia a limity

720 prípadov = 2 nenulové load bázy (1000h,2000h) × 6 vstupných SP × 6 dostupných paragraph rozdielov × 5 version AX × 2 počiatočné IF. SP 0010,0011,0100,1000,1FD0,1FD1; paragraph rozdiely 1,10,FFF,1000,1001,FFFF. Verzie AX 0002,0003,0106,070A,FFFF sú seedované testové hodnoty, nie zoznam skutočných DOS vydaní. Počiatočný DF je vždy nastavený; pôvodné CLD ho odstráni. Relokácie pochádzajú zo skutočného EXEPACK obrazu.

Overené všetky uvedené stavové WORD, celý BSS rozsah a dva guard BYTE, PSP top, resize argumenty, výsledné segmenty, SP a IF/DF. Nulové odchýlky. Testované SP nepretiekli pri ADD E02Eh a sentinel sa nachádza za nulovaným BSS. Nízke/pretékajúce SP, iné DOS verzie/failure výsledky a prirodzený EXE loader zostávajú otvorené. Prirodzený DOSBox-X runtime0.

Reprodukcia: audit_replay_pass1_startup_segments.py IMAGE INVENTORY DECODER EMULATOR OUT; promote_pass1_fields.py s mapou pass1_bsf_dispatch; verify_pass1_partition.py. Kanonický image SHA-256 e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297. Iced-x861.21.0, Unicorn2.1.4. cases.csv a summary.json uchovávajú parametre a hash dôkazu.

## Meranie

**57 069 B PARTIAL, 182 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu 57 295 B. Nezávislá kontrola 878 intervalov overila presné členstvo, všetky SHA a nulové diery/prekryvy. Integrita partition nie je úplná sémantická verifikácia. Nové lokálne dôkazy zatiaľ nie sú v poslednej publikovanej GitHub snímke.

'''
text+=f"SHA mapy `{p['map_sha256']}`; SHA cases `{s['cases_sha256']}`.\n\n"
text+='''## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A; staré orientačné hodnoty sa neprepočítavajú z úspešných prípadov alebo integrity mapy.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|BSS mimo file baseline|prirodzený loader|EXEPACK entry trace|
| Dátové typy a konštanty |95 %|N/A|2 B nové, 4 B spresnené|182 B iba klasifikované|zvyšné alias odkazy|
| Tabuľky a ukazovatele |93 %|N/A|startup SS/DS väzba|neskoršie zmeny segmentov|callee segment kontrakty|
| Funkcie / ASM / CFG |90 %|N/A|startup prefix720 prípadov|chybná a voliteľná vetva|init hook closure|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|CRT segment kontext oddelený|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|startup odlišnosti|NE autodata init|

## Runtime testy na vykonanie

V DOSBox-X zaznamenať prirodzený post-EXEPACK CS:IP, AX version, PSP, vstupné SP a registre pri 0025/00B3. Overiť skutočný resize výsledok a DS=ES=SS pred callbackom a po ňom. BSS zeroing sledovať samostatne od file coverage. Win16 startup má vlastný segmentový model; DOS invariant sa naň neprenáša. PE32 sa nevytvára.
'''
(r/'PASS1_STARTUP_SEGMENTS_REPORT.md').write_text(text,encoding='utf-8')
