# WORX Toolkit 2.1 — nové statické výsledky v0.12

**Dátum:** 16. 10. 2026  
**Rozsah:** len WORX Toolkit 2.1 integrovaný v originálnom rozbalenom Nitemare 3-D DOS v2.0.  
**Stupnica:** binárne dôkazy sú viazané na MZ image SHA256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`; algoritmický kontrakt != úplné emulované zariadenie/IRQ; cross-game implementácie sú iba kandidáti.

## Aktuálna bilancia 82 známych selektorov

- **37** predchádzajúcich priamych obslúh: `LEAF_BYTE_AUDITED` (v0.11).
- **4** nové obsluhy: `BODY_AND_DEPS_AUDITED` (v0.12): AH **12h,19h,29h,2Eh**.
- **38** nenulových obslúh `ENTRYPOINT_ONLY` vyžaduje rekonštrukciu vnútorného algoritmu.
- **3** nulové sloty *v počiatočnom obraze* `00h,27h,28h` bez dôkazu runtime nemennosti.
- Súčet **41** neznamená 50 % zvukovej či časovej parity — všetky veľké mixery/track parsers sa môžu za jedným selektorom skrývať.

### AH=12h — CS:3E2B..3E5A

1. Zapíše `AL` do `CS:2DC4`, `BL` do `CS:2DC5` **pred** vetvou.
2. Test `CS:[2DC9] & 20h`; ak nenulový, podmienka `AL >= B0h` preskočí indexovaný zápis.
3. Inak zapíše `BL` na adresu `DS:[2BA7+zeroextend(AL)]` (DS=CS nastavuje vonkajší INT63 dispatcher).
4. Vonkajší handler zachová registre mimo AX/DX a cez `IRET` obnovuje vstupné flags.

### AH=19h — CS:335B..337A

1. Načíta `CS:[2DF3]` — DOS file handle.
2. Pri handle != `FFFFh` volá DOS `INT21h` s `AH=3Eh` a `BX=handle`.
3. **Bez ohľadu na DOS CF** nastaví `CS:[2E10]=0`, `CS:[2DF3]=FFFFh`.
4. Príkaz si ukladá AX a BX, ale nie DX. Vonkajší `INT63` vystavuje zmenené DX, ak ho vonkajšia DOS služba zmenila. Preto C++ prijíma explicitný callback `DosFileIO` a nepredstiera DOS-success.

### AH=29h — CS:41F6..4264

1. `CLI`; lokálne uchová `AX` a `DX`; vynuluje `CS:2012/2014`.
2. Jedenkrát číta port `201h`; horné štyri bity sa po `SHL` testoch zapisujú invertované ako 0/1 na `CS:2019..2016`.
3. Výsledné `AL` po štyroch `SHL` odošle na port `201h` **40-krát**.
4. Nasleduje **800** čítaní portu `201h`; bit0 každého čítania pripočíta k `CS:2012` a bit1 k `CS:2014` (16-bitové čítače).
5. Ak `CS:201A == 0`, skopíruje `2012 -> 201A`, `2014 -> 201C`. Kalibračná podmienka kontroluje iba **prvú** os.
6. AX/DX sa vrátia z lokálneho stacku; IRQ časovanie a fyzické vybíjanie joystickov sú mimo C++ modelu.

### AH=2Eh — CS:3E67..3E76 → helper CS:466A..469E

1. `CLI`, `AX=FFFFh`, zavolá spoločný PIT helper.
2. Ak `CS:[201E]==1`, helper sa okamžite vráti bez zápisov portov.
3. Inak v helperi `DX=0, AX=FFFFh`, `DIV BX` s `BX=FFFFh`, výsledok = **1**; zapíše `CS:2DB6=1`, `CS:2DB4=1`.
4. Zapíše do portov presne `(43h,34h)`, `(40h,FFh)`, `(40h,FFh)`.
5. Po návrate sa `CS:201E=1`, nasleduje `STI`, `RET`; vonkajšie `IRET` obnoví pôvodné flags. Reentrancia v STI okne nie je simulovaná.

## IRQ0 / INT08 statická rekonštrukcia

### Inicializácia — `15BF:2E7D` (výrez)

- `15BF:2F03` načíta PIT delič `0952h` (=2386) a `CALL 466Ah` nastaví PIT.
- Helper počíta `FFFFh / 0952h` = **27**, ukladá do `CS:2DB6` a **aj** do `CS:2DB4`.
- `CS:3ED4` v pôvodnom MZ obraze = `FFFFh`. `CS:40E5` začína na 0.
- Prvý tick po init preto pri normálnom priebehu splní `++2DB4 >= 2DB6` a reťazí sa na starý BIOS `INT08`.

### Obsluha IRQ0 — `15BF:4150..41B2`

1. `CLD; CLI`. Pri `CS:[2DBC]&16h !=0` `CALL 4476` (*interné MIDI/CMF telo ešte otvorené*).
2. `INC CS:[2DB4]`; pri `counter >= CS:[2DB6]` vynuluje čítač, vykoná `PUSHF; CALL FAR CS:[000A]`, potom `IRET`. Na tejto vetve **nevysiela vlastný EOI**, necháva ho pôvodnému handleru.
3. Inak inkrementuje `CS:[3ED4]`, vyšle PIC EOI `OUT 20h,20h`.
4. Keď inkrementované `CS:[3ED4] == 0`, `CALL 40E7`; inak `INC CS:[40E5]` (počítadlo preskočených obslúh, nie preukázaný front na dobehnutie).
5. `DEC CS:[3ED4]`, `IRET`. Počiatočné `FFFFh` sa tak po úspešnej obsluhe obnoví.

### Obsah privátnej audio obsluhy — `15BF:40E7..414F`

1. Pred prácou prepne SS:SP na privátny stack, pri vstupe používa `CLI`, po prepnutí `STI`; synchronný C++ model **NEEMULUJE** segmenty/IF ani vnorené reálne IRQ.
2. Z `CS:[2C4D]:[2C4B]` odčíta 16-bitovú kvantitu `CS:[2C49]` pomocou `SUB low; SBB high` (mod 2³²).
3. **Testuje znamienko horného slova** (`CMP CS:[2C4D],0; JGE`). Ak je horné slovo záporné, nastaví `CS:[2C53]=1`. Tento postup príznak počas pozitívnych tickov **nenuluje**.
4. Ak `CS:[2DBC] & 20h`, `CALL 555Dh` (PCM). Potom nezávisle pri `CS:[3ED6]!=0`, `CALL 5DF2h` (MIDI/scheduler).
5. Oba callbacky a ich nepriamo vyvolané funkcie ešte nie sú 1:1; v C++ majú *iba* explicitné hook rozhrania.

## Štyri dôležité novo uzavreté hraničné fakty, NIE dokončené celé obsluhy

| Mechanizmus | Strojový dôkaz | Dôsledok pre 1:1 |
|---|---|---|
| `AH=2Fh` MIDI/timer | `44B1: LOOP 44A9` **bez RET**, hneď za ním je vstup `44B3` (`PUSH CX`) | Po ukončení `LOOP` existuje dosiahnuteľný **fall-through do tela helpera**. Bez ďalších podmienok nesmie model vložiť pred `44B3` návrat. |
| `AH=4Eh` PCM clear | `5577 SHR CX,1; 5579 MOV AX,8080h; 557C REP STOSW` | Tento úsek vyčistí iba `2*floor(CX/2)` bajtov na `80h`; pri nepárnej dĺžke posledný bajt **tento úsek** nemení. Neskorší mix ho môže zmeniť. |
| `AH=3Fh` DSP parameter | `5C70 DX=000F, AX=4240h; 5C76 DIV BX` | Pre `BX` od 1 do 15 je `1000000/BX > FFFFh`; 16-bit x86 vyvolá chybu delenia (BX=0 má samostatný návrat `FFFFh`). Ostatné vetvy otvorené. |
| `AH=52h` mimo tabuľky | `CALL CS:[2020h+2*AH]`; `20C4h` je mutabilný čítač (writer `2358 INC CS:[20C4]`) | `AH=52h` už indexuje **stavový údaj**, nie stabilný handler. Neexistuje automatické bezpečné „unknown AH“ správanie originálu. |

## Čo NIE JE dokázané

- Kompletný 16-bit CPU/port/IRQ stav, stack frame, vedľajšie účinky výnimočných stavov; fyzický DOS/XMS/AdLib/SB model.
- Celé algoritmy `4476` (event/parser), `555D` (PCM mixer), `5DF2` (music), volané nepriamo z ISR.
- Zhodná audio/MIDI/PCM stopa originálu a náhrady ani postupnosť skutočne vnorených ISR pri `STI`.
- Úplné cesty pri 38 nenulových otvorených vstupoch a dynamicky modifikovaných jump-table slotoch.

## Prísny akceptačný princíp

Funkcia sa označí za **uzavretú na hranici C++ kontraktu** len vtedy, keď sú auditované konkrétne originálne inštrukcie, rozhrania, čítania/zápisy, presné register width, každá známa vetva a všetky externé volania explicitne reprezentované. **Úplné 100 % parity** vyžaduje aj transitive callee, DOS hardware odpovede, vlákna IRQ a bitovo identický zvuk.

Strojovo kontrolované evidencie: `data/n3d_v20_int63_dispatch.json`, `data/worx21_int08_static_evidence.json`; skripty `tools/audit_dispatch_binary.py`, `tools/audit_int08_re_first.py`.
