# Nitemare 3D – DOS startup / EXEPACK / pôvodný vstup / príkazový riadok

Dátum: 2026-10-15. Metóda: striktne statické čítanie EXE bajtov, MZ polí, EXEPACK stubu a 16-bitovej disassemblácie. Žiadny runtime test.

## Identita zdrojov

| Zostava | SHA-256 | Veľkosť |
|---|---|---:|
| DOS 1.0 | `7035d185d27a4629664e9a300b77870577195205bbabcd17bbaf74a9ecf4cd04` | 115,152 B |
| DOS 1.1 | `21659bde829e5ed9917a775bc438cf205ba1ed7b0309e3681eb7fd945adf2bec` | 115,768 B |
| DOS 1.2 | `f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5` | 115,856 B |
| DOS 1.5 | `244e2e9a4abb4455d271562f01d25c38a5f5e1623e9cce653bf314a76bcc5eef` | 115,904 B |
| DOS 1.7 | `6abf5745d1b2862267be16395d6fd37b46c41fc3ad4248973883f5e1db8efcc2` | 116,068 B |
| DOS 1.9 | `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8` | 116,556 B |
| DOS 2.0 | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` | 116,606 B |

Poznámka: `nd-3-18/N3D-E-18.EXE` je hashovo totožný s 1.9; nemožno ho označiť za samostatne overenú DOS 1.8. Porovnanie tak pracuje s DOS 1.9 a nie s neoverenou 1.8.

## Tri rozdielne vstupné miesta

1. `MZ e_cs:e_ip` – začiatok EXEPACK stubu, s offsetom `e_cparhdr*16 + e_cs*16 + e_ip`.
2. `EXEPACK stub CS:0000` – uložené pôvodné `IP`, `CS`, `SP`, `SS`. Pôvodný bod sa staticky číta ako `e_cparhdr*16 + original_cs*16 + original_ip`. V skúmaných obrazoch je týchto 100 bajtov priamo prítomných a u referenčných IDA EXE zhodných.
3. `CALL FAR` v startup kóde na relatívnom offsete `+0xC2` – hlavná C funkcia, ktorá číta `argc/argv`. Je to reverzne odvodená funkcia podobná `main`, nie preukázaný pôvodný symbol.

| Verzia | EXEPACK entry | Original entry | Original file offset | `main` kandidát | Main file offset |
|---|---|---|---|---|---|
| 1.0 | `1B1B:0010` | `119B:0010` | `0x11BC0` | `044E:0320` | `0x04A00` |
| 1.1 | `1B40:0010` | `11BC:0018` | `0x11DD8` | `0452:0334` | `0x04A54` |
| 1.2 | `1B45:0010` | `11C2:0018` | `0x11E38` | `0453:0330` | `0x04A60` |
| 1.5 | `1B48:0010` | `11C7:001C` | `0x11E8C` | `0458:0328` | `0x04AA8` |
| 1.7 | `1B52:0010` | `11D1:0018` | `0x11F28` | `045F:0332` | `0x04B22` |
| 1.9 | `1B6F:0010` | `11EA:001C` | `0x120BC` | `0476:0326` | `0x04C86` |
| 2.0 | `1B72:0010` | `11EE:0018` | `0x120F8` | `0476:0326` | `0x04C86` |

## Bajtový audit

- Prvých 100 bajtov EXEPACK rozbaľovača: **100/100 rovnakých** vo všetkých siedmich zostavách. Rozbaľovač používa `REP MOVSB`, `RETF` a potom spätné kódovanie blokov so značkami `B0/B1/B2/B3`.
- Prvých 100 bajtov pôvodnej startup rutiny: **88/100 rovnakých**, rozdiely len v číselných operandoch (rozmiesťnenie pamäte).
- Prvých 100 bajtov `main` kandidáta: **87/100 rovnakých** naprieč všetkými siedmimi zostavami; ďalší behaviorálne relevantný rozdiel v CLI parseri je za týmto oknom.
- Rozdiely v prvých 100 bajtoch pôvodného startup kódu sú na relatívnych bajtových offsetoch: `0x0E`, `0x0F`, `0x24`, `0x25`, `0x3D`, `0x3E`, `0x43`, `0x44`, `0x4E`, `0x4F`, `0x51`, `0x52`.

### Operandová matica pre štyri hlavné zostavy

| Relatívny offset | Význam inštrukcie | 1.0 | 1.2 | 1.5 | 1.9 |
|---|---|---|---|---|---|
| `+0x0E` | `mov di,imm16` – relokovaný segmentový operand | `2360` | `239B` | `274A` | `276D` |
| `+0x24` | `add sp,imm16` | `DE6E` | `DF8E` | `DF5E` | `E02E` |
| `+0x3D` | `mov ss:[addr],ax` #1 | `201C` | `2110` | `20E2` | `2120` |
| `+0x43` | `mov ss:[addr],ax` #2 | `201A` | `210E` | `20E0` | `211E` |
| `+0x4E` | `mov ss:[addr],ax` #3 | `1FDA` | `20CE` | `20A0` | `20DE` |
| `+0x51` | `mov bx,imm16` | `1FDC` | `20D0` | `20A2` | `20E0` |

Pre verzie 1.0, 1.7, 1.9 a 2.0 je staticky overené, že 100 pôvodných startup bajtov sa zhoduje s plnšie rozbaleným IDA EXE. V ich relokačných tabuľkách je fixup na `original-entry+0x0E`, teda `mov di,imm16` má za behu relokovanú hodnotu. Preto neslobodno interpretovať na disku uložený `imm16` ako absolútny runtime segment.

### Potvrdené funkcie startupu

`MOV AH,30h; INT 21h` sa pýta na verziu DOS; `CMP AL,02h` vylučuje DOS pred 2.0. Nasleduje určenie pamäťového limitu cez `PSP:0002`, inicializácia zásobníka, úprava pamäťového bloku `INT 21h/AH=4Ah`, inicializačné far volania a far volanie na hlavný kód. V prvých 100 bajtoch nie je žiadna priama herná mechanika.

## Prvý významný rozdiel: parser príkazového riadka

`main` funkcia číta argumenty `argc` na `[BP+6]` a `argv` na `[BP+8]`. Nasleduje spracovanie druhého znaku argumentu po `-`, `CBW`, dolná hranica `SUB AX,0x62/0x61`, horná hranica `CMP AX,0x16/0x17`, a vetvenie cez `JMP WORD PTR CS:[BX+table]`. Tabuľka skokov sa dekóduje ako 16-bitové offsety v aktuálnom CS.

| Zostava | Rozsah dekodéra | Vetva `-a` | Vetva `-q` |
|---|---|---|---|
| 1.0 | `b–x` | mimo rozsahu | default |
| 1.1 | `b–x` | mimo rozsahu | `0452:0450` |
| 1.2 | `b–x` | mimo rozsahu | `0453:044C` |
| 1.5 | `b–x` | mimo rozsahu | `0458:0444` |
| 1.7 | `a–x` | `045F:03E8` | `045F:0470` |
| 1.9 | `a–x` | `0476:03DC` | `0476:0464` |
| 2.0 | `a–x` | `0476:03DC` | `0476:0464` |

**Reálne nové kódové cesty:** od v1.1 sa `-q` mapuje na vlastný handler; od v1.7 sa `-a` mapuje na vlastný handler. V 1.0 `-q` ide cez spoločnú predvolenú vetvu; v 1.5 `-a` padá mimo prípustného rozsahu. Nie je to len posun dátovej adresy.

### Handler `-a`, DOS 1.9

```asm
; main=0476:0326, tabuľka na CS:039E, priamy case a -> CS:03DC
push 3CDCh           ; argument 3
push 0AA6h           ; argument 2
inc si               ; ďalšie argv
mov bx,si
add bx,si
push [bx+di]         ; argument 1 = argv[++index]
call 11EA:27E8       ; helper
add sp,6
call 0277:0C6E       ; ďalšia inicializačná rutina
jmp ...              ; spoločné pokračovanie
```

Presný užívateľský význam parametra `-a`/`-q` zatiaľ **nebol dokázaný**. Predchádzajúce tvrdenia typu „sound“ alebo „quiet“ by boli hádaním. Za potrebné statické pokračovanie sa považuje dátový tok cez pomocnú funkciu a jej cieľové globálne premenné, poradie zápisov a kontrola chýbajúcej hodnoty.

## Limity a ďalšie kroky

- Ide o statickú rekonštrukciu; dosiahnuteľnosť chybových vetiev vo všetkých prostrediach nebola meraná runtime.
- `E18` označuje 1.9 identický obraz, **samostatné 1.8** nebolo v tomto dátovom súbore nájdené.
- Hlavný startup `main` kód nie je nutne celý herný engine; herný callgraph pokračuje cez ďalšie far volania. `argc/argv` interpretácia má priamu inštrukčnú oporu.
- Pokračovať čisto staticky: `-a` parameter -> helper `11EA:27E8` -> stav; `-q` `1.0` vs `1.1`; celý 1.0/1.5/1.9 command switch CFG; až potom runtime pre nerozhodnuteľné vstupy.

## Sprievodné súbory

`manifest.csv` identifikuje binárky a adresy, `byte_matrix_*.csv` mapujú všetkých 100 bajtov, `cli_switch_cases.csv` eviduje presné jump-table cieľové adresy, `.asm` obsahujú surovú disassembláciu (pri tabuľkách pozor na interpretáciu dát ako inštrukcií). `analyze_n3d.py` reprodukuje kľúčové údaje na vlastných EXE.
