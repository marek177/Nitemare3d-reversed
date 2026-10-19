# Nitemare 3D — RE MAX NEXT 2: statický audit nepriamych volaní a hĺbkovej referencie

**Dátum:** 19. 10. 2026. **Metóda:** striktná statika, read-only, bez DOSBox-X gameplay, bez zmeny GitHubu.  
**Analyzovaný zdroj:** `N3D_DOS19_EXE_linear_all(1).asm` (archivovaný DOS 1.9 lineárny disassembly export). Vo vstupnom ASM je 116 044 súvislých dekódovaných bajtov. SHA-256 týchto **rekonštruovaných bajtov** je `1699be5dc6db8a18d1131c369eb0cbaffd7c748127d6170d6f8dc04a07fa81de`. **Toto nie je hash ani nová verifikácia celého pôvodného EXE.** 

**Dôležitá hranica:** Lineárny dekóder interpretoval aj vložené dátové tabuľky ako strojové inštrukcie. V tomto balíku preto nikdy nezamieňame `linear decoded candidate` za reálne vykonateľný `CFG edge`. Potvrdené je znenie analyzovaného exportu a explicitné opcode anchory, nie celý originálny dosah.

## 1. Úplný pracovný census 77 kandidátov

Z pôvodných 77 lineárne dekódovaných nepriamych CALL/JMP miest je teraz **každé individuálne opísané** v `dos19_indirect_77_reviewed.csv` (adresa, opkódy, kategória, lokálny dôkaz, otvorený ďalší krok).

| Rodina | Počet miest | Stav |
|---|---:|---|
| `CS:[BX+disp]` NEAR JMP dispatchery | 23 | Všetkých 23 bolo číselne dekódovaných; CFG a niektoré dosiahnuteľnosti OPEN |
| XMS ovládač cez `INT 2Fh AX=4310h` | 13 | Pôvod vstupného pointera lokálne uzavretý, implementácia ovládača externá |
| Starý INT09 handler cez `DS:3F52` | 1 | Silná lokálna atribúcia; úplný helper/alias OPEN |
| Ďalšie kandidáty | **40** | Rozdelené do konkrétnych rodín nižšie |
| **Spolu** | **77** | Nie je to počet vykonateľných funkcií |

### Rozdelenie ďalších 40 miest

- **6 × pravdepodobne dátový false-positive**: `15EE0`, `15EF6`, `1B3FD`, `1B52A`, `1B544`, `1B6EF`. Sú v oblastiach s numerickými/relokačnými tabuľkami a nesúvislými alebo neplatnými lineárne dekódovanými inštrukciami; neoznačovať zatiaľ formálne DEAD bez recursive CFG.
- **1 × lokálne zostrojený DOS INT trampoline**: `IMG:143D9`. Rutina zapisuje na stack `CD xx CB` (pre INT25/26 aj špeciálnu kombináciu), vytvorí FAR pointer cez `SS:BP-0E` a až potom volá. Nie je to záhadná callback tabuľka.
- **1 × lokálne určený NEAR target**: `IMG:11FC0` číta `DS:20DC`, ktorý kód `IMG:11F92` nastavuje na `0x01EF`. Pre normalizovanú bázu lokálneho CRT segmentu `0x11EA0` ide o `IMG:1208F` (existujúci lokálny entry).
- **1 × potvrdená vetva starého INT08 handlera**: `IMG:176BF`; `IMG:16685..16693` volá DOS `INT21 AH=35 AL=08` a ukladá starý offset+segment do `CS:000E/0010`; pri `IMG:16727..16735` ho rutiny cez `INT21 AH=25 AL=08` obnovujú. Volanie `176BF` je `PUSHF; CALL FAR CS:[000E]; IRET`.
- **2 × I/O/hardvérový callback hook**: `IMG:17005` (po I/O 388h/389h) a `184ED` (po I/O 330h) zdieľajú far pointer `CS:389A/389C`; nastavuje ho `IMG:16FD4/16FD9` medzi `CLI/STI`. Identita skutočného volajúceho callbacku ešte nie je uzavretá.
- **1 × loader/relokačný transfer**: `IMG:1B7F3`, po obnove `DS/ES/SS/SP` a nastavení `BX=0` preskakuje cez `JMP FAR CS:[BX]`; patrí do handoff/loader rodiny, nie do guard/projectile dispatcheru.
- **1 × indexovaný CS NEAR CALL**: `IMG:168A5` používa `SI=2*old_AH` a `CS:[SI+2024h]`. Úplná pointer-table segmentová identita a hranica možných AH hodnôt zostáva OPEN.
- **27 × ďalšie CRT / nastaviteľné callbacky a funkčné argumenty**: skupiny `DS:2534/2536/2538` (strážené hodnotou `DS:2532==D6D6`), `DS:2540` (s počtom `DS:2542`), formátovací dispatcher `DS:2344/2348/234C/2350/2358/235C`, ďalšie voliteľné FAR hooky, argumentové komparátory a pokračovacie FAR JMP. Ide o bližšie identifikované **rodiny** — nie o úplné dokázanie ich dynamických cieľov.

#### XMS oprava segmentového aliasu

`IMG:07E86` nie je doslovné `CALL FAR DS:[350C]`, ale `CALL FAR ES:[350C]` (prefix `26h`). Predtým však `IMG:07E78..07E7A` vykoná `ES ← DS` a až potom `IMG:07E7E` prepne `DS` na dátový segment volaného objektu. To vysvetľuje, prečo callback stále číta pôvodne inicializovaný XMS vstup bez toho, aby sa zamieňal nový DS kontext. Či medzi týmito inštrukciami môže dôjsť k vonkajšiemu aliasovaniu iným mechanizmom, patrí do globálneho dôkazu.

## 2. `CS` jump-table audit — 23 tabuliek / 408 WORD záznamov

- **23** registrovaných nepriamych NEAR JMP dispatch miest, pri ktorých sa podarilo odvodiť bázový segment, miesto tabuľky a počet lokálne dekódovaných slov.
- **408** číselne dekódovaných tabuľkových záznamov, **225 jedinečných cieľových adries**; identické ciele sa prirodzene používajú opakovane.
- **56** položiek ukazuje na adresy, ktoré nie sú začiatkom *lineárne* dekódovanej inštrukcie. Nie je to samo o sebe chyba ani dôkaz mŕtveho kódu: lineárny výpis môže byť vnútri tabuliek nesprávne zarovnaný. Recursive CFG sa ešte musí zrekonštruovať.
- Väčšina tabuliek má pred JMP lokálnu normalizáciu indexu a unsigned gate (`CMP AX,max; JA default`), takže lokálny rozsah indexu je konkrétny.

**Špecifické nálezy:**

- `IMG:0850D` → score dispatch 25 tried (`08..20`), `IMG:085C6` → damage dispatch 20 tried (`0C..1F`), `IMG:09CF2` a `09EB4` → dve odlišné SFX tabuľky po 24 triedach.
- `IMG:09819` obsahuje **9** pôvodných DOS 1.9 HUD akcií `0..8`; je v súlade s neskorším dôkazom o vložení akcie 4 vo v2.0.
- `IMG:133BB` je format/character dispatcher 25 tried, ktorý môže skákať aj do skorších blokov CRT.
- **`IMG:1353E` používa predchádzajúcu tabuľku `IMG:134DC`**, nie inline tabuľku za JMP. Osem lokalizovaných WORD entry smeruje na existujúce bloky `13543..13625`. Avšak `IMG:13531 XLAT`, následné `SHR AL,4` bez znalosti hodnotového rozsahu LUT pri `DS:22C8` samotné **nevylučuje index 8..15**. Platný runtime rozsah je stále P0 dokazovacia povinnosť. Nejde o potvrdenú chybu hry.

Všetky záznamy sú v `dos19_23_jump_tables.csv` a `dos19_408_table_targets.csv`. `next2_static_closure.py` pri spustení znova kontroluje opkódy a každú vypočítanú adresu.

## 3. Nové uzavretie: producer `DS:4550` pre `OBJECT+18` damage

Priamy DOS1.9 writer na `IMG:03378` je súčasťou pôvodnej inicializácie/render viewport geometrie. Input `W=WORD DS:4144`; kód `IMG:03332..0337F` vykonáva 32-bitové znamienkové odčítanie a polovičné posuny. Pre doménu `0 <= W <= 320` je výsledok **presne**:

```text
DS:4550 = floor((320 - W)/4) + floor(W/4)
        = 80 ak W mod 4 == 0
        = 79 inak
```

`IMG:033DF` nastavuje počiatočné `DWORD DS:4144 ← 0x130` (W=304), teda referencia je **80**. Ďalšia vetva `IMG:04C31` vykonáva `AND BYTE DS:4144,F8h` (ak prebehne, spodné tri bity W sa nuluju). Nie je preukázané, že W nemôže byť zmenené aj nepriamo parserom alebo chybným vstupom pred prepočtom.

`IMG:08592` číta `WORD OBJECT+18`; `IMG:08596` odčíta `DS:4550`; `IMG:085A3` a ďalšia aritmetika zahŕňajú RNG. `IMG:0B47A` je lokálny projekčný writer 28-bajtového actor záznamu. Pre všetky šírky 0..320 bol instruction-level referenčný model testovaný proti nezávislému celočíselnému vzorcu (321/321).

**Evidenčné rozlíšenie:** V analyzovanej lineárnej code sekcii je `IMG:03378` **jediný doslovný zápis** na `DS:4550`; 12 ďalších syntaktických prístupov je čítacích. To **nevylučuje** nepriame `LES/ES`, bulk zápisy do dátového segmentu, `SAVE/LOAD` a chybný vstupový stav. Toto je lokálne uzavretie pôvodu referencie, nie globálna uzávierka `OBJECT+18` alebo prirodzenej dosiahnuteľnosti záporného rozdielu.

## 4. Zmeny statusov, bez umelého zvyšovania percenta

| Dôkazová povinnosť | Predtým | Teraz | Čo ešte zostáva |
|---|---|---|---|
| Generický DOS interrupt cez FAR pointer | UNKNOWN indirect | **LOCAL TARGET CONSTRUCTION CLOSED** | I/O/OS účinky mimo samotného kódu |
| Saved INT08 vector chain | OPEN | **LOCAL POINTER ORIGIN + RESTORE CLOSED** | IRQ preklad a časovanie |
| DS:20DC CRT near hook | OPEN | **LOCAL FIXED TARGET CLOSED** | Vstupná cesta a knižničný kontext |
| CS:389A I/O callback origin | OPEN | **LOCAL WRITER IDENTIFIED** | Identita vstupného callbacku |
| Šesť sporných FF opcode v dátach | COUNTED AS UNKNOWN CODE | **LIKELY DATA** | Recursive CFG potvrdenie |
| 23 CS dispatch tabuliek | tabulky čiastočne známe | **408 WORD targetov zrekonštruovaných** | Všetky target body a 1353E LUT rozsah |
| `DS:4550` pôvod a normálna aritmetika | producer neuzavretý | **LOCAL PRODUCER + W=0..320 CLOSED** | Nepriame/LOAD writery, šírka mimo doménu |
| OBJECT+18 full last-writer -> hit | OPEN | **OPEN** | Alias writers, renderer culling, gameplay preconditions |
| Full statické/semantické core 100 % | NOT PROVEN | **NOT PROVEN** | Kompletné CFG/dátový tok všetkých buildov |

## 5. Nasledujúce statické úlohy (bez runtime)

1. **Recursive CFG** zo skutočných MZ/NE vstupov a relokácií, osobitne pre oblasť `15E80..15F20`, dátové oblasti `1B3xx..1B6xx` a 56 table-target/linear-decode konfliktov.
2. **PTR producers** pre CRT/format hooky `DS:2532/2534`, `DS:235C`, `DS:2540` a ďalšie (vrátane inicializovaných dátových WORD, ktoré nie sú doslovne zapísané v code).
3. **Index-doména `1353E`**: načítať pôvodný dátový segment a LUT pri `DS:22C8`, potom dokázať výstupnú hornú nibble `<= 7` alebo definovať behavior pri iných hodnotách.
4. **Rozsah `DS:4144`**: všetci parser/LOAD writers, invariant šírky pred prepočtom; napriek formule 79/80 nevyvodzovať nekontrolované stavy ako prirodzene dosiahnuteľné.
5. **OBJECT+18**: aliasová analýza kompletnej 28 B štruktúry cez heap, SAVE/LOAD, sprite pool, projectile hit, renderer; otestovať dosiahnuteľnosť `storedDepth < reference` alebo formálny dôkaz, že nikdy nemôže nastať.
6. Rovnaké statické dôkazy opakovať na presne hashovaných DOS2 a Win16 originoch. Samotný starší Ghidra export nie je náhrada originálneho byte-anchoru.

## Reprodukcia

```bash
python3 next2_static_closure.py --asm "N3D_DOS19_EXE_linear_all(1).asm" --out derived
python3 next2_depth_reference.py --asm "N3D_DOS19_EXE_linear_all(1).asm" --out derived
```

Skripty vyžadujú exact SHA256 rekonštruovaného 116044B ASM výrezu a explicitné opcode okná. V archíve výsledkov **nie je priložený komerčný EXE ani kompletný pôvodný opcode dump**. Výsledky sa nedajú použiť na tvrdenie, že originál bol v tomto kroku spustený alebo overený všetok jeho spustiteľný kód.
