# WORX Toolkit 2.1 — RE-1TO1-MAX v0.13 (16. 10. 2026)

## 0. Dôkaz a hranica tvrdenia

**Vstup:** pôvodný *úplne rozbalený* `N3D_DOS_v2.0_IDA.EXE` (178 528 B; hlavička 0x1C00; image 0x29D60 B; SHA256 image `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`). WORX kód v segmente `15BF`, image base `0x15BF0`. **Binár bol priamo načítaný a jeho strojové bajty porovnané.** Nezamieňať s N3D-UNFU ani s iným buildom WORX.

v0.13 **nezvyšuje počet úplne rekonštruovaných API obslúh**: naďalej 41/79 nenulových, 38 nenulových otvorených, 3 nulové *v počiatočnom obraze*. Namiesto umelého percentuálneho rastu uzatvára hlbšie interné časti. Nový audit `tools/audit_audio_inner_v013.py` má 10 rozsahov s SHA256 a 36 adresných strojových svedkov; reprodukovateľný manifest: `data/worx21_audio_inner_static_v013.json`.

## 1. `15BF:49BC–4A11` — DSP/DMA okno (implementované v C++)

| IP | Pôvodná operácia | Dôležitý kontrakt |
|---|---|---|
| `49BF` | `xor al,al; out 0Ch,al` | reset DMA flip-flopu cez port `0Ch`, 1 zápis |
| `49C3` | `in al,02h` **dvakrát** | iba **druhé** prečítanie určuje `CX = sample << 8` |
| `49CE` | `AX=CS:[2DDF]; cmp cx,ax; jae` | unsigned dolná kontrola pred odčítaním |
| `49DB` | `cmp cx,0400h; jae` | unsigned minimálny rozdiel 1024 |
| `49E4` | `cmp cx,1000h; jle` | **signed** horná kontrola; `8000h–FFFFh` môže prejsť |
| `49ED` | `DX=CS:[48DD]; [49BA]=DX; [48DD]=CX` | starý DMA kurzor sa zachová |
| `49FC` | `cmp cx,dx; jge` | **signed** rozhodnutie o wrap; inak `[48DD]=0`, `CX=1000h` |
| `4A0A` | `sub cx,dx; [48DB]=cx` | presne 16-bitový rozdiel |

`poll_dma_49bc` realizuje AX/CX/DX a uvedené CS/portové efekty cez explicitný `PortIO` backend. Pôvodné `CLI/STI`, DS=CS, ISA DMA časovanie, IRQ preklady a skutočné hodnoty portu nie sú hostom emulované.

**Nový rozhodujúci okraj:** ak druhé DMA čítanie vráti `FFh`, base `CS:[2DDF]=0100h`, medzivýsledok `FE00h` sa pri `JLE` považuje za záporný a **prejde**; následné znamienkové `JGE` môže spustiť reset kruhového kurzora. Prepis `if (cx > 0x1000) return;` by bol nesprávny.

## 2. `15BF:5DF2–5E18` — music gateway (presné priame vetvy, transitive OPEN)

```
if (CS[2DEA] != 1) return;
CX = 0;
if (CS[48E3] == 02h || CS[48E3] == 0Ch) {
    CALL 49BCh;         // DMA subkontrakt je modelovaný
    if (CX == 0) return;
}
CALL 5F17h;             // Vnútorné telo a jeho callees zostávajú OPEN
return;
```

`5F17h` sa v iných módoch než `02h/0Ch` volá **aj bez úspešného DMA pollingu**. V C++ je to povinný injektovaný `MusicStream5f17`; tichý falošný úspech nie je dovolený. Príkaz `AH=42h` má **iba uzatvorený entry control-shell**, nie transitive 1:1 funkciu.

## 3. `15BF:4476–44B2` — outer MIDI tick scheduler, nie celý track parser

- Ak `CS:[2D62]==0`, návrat ešte pred zmenou tick čítačov.
- Inak `CS:[2C54]++` s 16-bit wrap; `CMP` proti `CS:[2C5A]` je **unsigned**, pri `>=` sa tick nuluje a inkrementuje `[2C56]`.
- `CS:[2DC0]=0`, `CX=CS:[2C58]`.
- Telo volá `44B3`, inkrementuje `CS:[2DC0]` a vykonáva `LOOP 44A9`.
- Po ukončení `LOOP` riadenie **prepadne do `44B3` ešte raz**, pretože tam nenastáva návrat.
- Pre `2C58=2` teda za podmienky návratu track handlera vznikne sekvencia indexov `[0,1,2]`. Pre `2C58=0` vznikne `65536+1` vstupov do track handlera (LOOP dekrementuje nulu na `FFFFh`). To môže znamenať extrémnu prácu / čítanie mimo logického zoznamu a nesmie sa „opraviť“ na for-loop nula iterácií.
- Ak `2C54` pretečie `FFFF→0000`, unsigned porovnanie typicky **nezvýši** `[2C56]` pri nenulovom prahu.

`midi_tick_outer_4476` verne zachováva túto riadiacu kostru a explicitne volá `MidiTrack44b3`, ale **samotné telo `44B3..45DC` nie je portované**. Ten obsahuje MIDI dispatch `3A4D`, čítanie VLQ `45F9`, skladby `4265/4389`, zmeny PIT `466A` a externý pamäťový stream cez `ES:DI`.

## 4. `15BF:45F9–462F` — 32-bitové MIDI variable-length delta (implementované)

Sekvencia na každom bajte: `BL=(es:di++)`, `AL|=(BL & 7Fh)`, ak `BL < 80h` → návrat, inak **sedemkrát** `SHL AX,1; RCL DX,1` a pokračovanie. Výsledok je `DX:AX` modulo `2^32`. Neobsahuje explicitný limit dĺžky na 4 bajty. `DI` sa inkrementuje modulo `2^16`; pamäť `ES` sa musí dodať cez `FarByteMemory`.

Hostiteľský parameter `safety_max_reads` je **len ochrana proti nekonečnému čítaniu**; pri prekročení vyhodí chybu. Nie je to vlastnosť pôvodného DOS kódu.

## 5. `15BF:555D` — PCM mixing (v0.13 čiastočná rekonstrukcia)

Doteraz presne modelované kroky:

- `555D`: najskôr `CALL 49BC`; pri nulovom `CX` návrat bez zmeny scratch dĺžky.
- `5568..557D`: `ES:DI = CS:[2DDF] + CS:[49BA]`, `CS:[478B]=CX`, `SHR CX,1`, `AX=8080h`, `REP STOSW`. **Presne 2·floor(CX/2)** bajtov sa prepisuje na `80h`; posledný nepárny bajt sa nevymaže.
- `557E..5663`: príznak aktivity pre **8 slotov** (`BX=0,2,...,0Eh`, pri `BX>=10h` koniec). Samotné audio slučky, resampling, refill a playlist operácie ešte nie sú uzatvorené.
- `5625..563D`: `sample` načítaný cez DS:SI, `AX=(uint16)sample>>1`, `AX-=0040h`, `DX=CS:[4BBF+BX]<<2` (2x SHL 16-bit), `IMUL DX` signed 16x16, `ADD BYTE PTR ES:[DI],AH` bez saturácie, výstup **modulo 256**.

Implementácia `pcm_mix_byte_5625` je presný strojovo odvodený primitiv, `pcm_clear_prefix_5568` je iba pre-clear prefix (nepredstiera 8-voice mixer). Pre úplné uzavretie potrebujeme `5863` → far callback `CS:[21C8]`, `5502` → `56F0/5792/4C75`, celé per-voice intervaly a 16.16 pitch stepping.

## 6. `15BF:5F17–5F3D` — streaming scratch-fill (implementovaný prefix)

Funkcia vždy nastaví `CS:[2DEA]=1`, načíta počet `CX=CS:[48DB]`, a keď `CX>0`, nastaví `ES:DI` z `CS:[2DDF]` + `CS:[49BA]` a vykoná `REP STOSB`. Hodnota `AL` je **80h iba pri `CS:[48E4]==0`, inak 00h**. Pri nulovej dĺžke sa nemenia bajty bufferu, ale stále sa nastaví príznak `[2DEA]`. Implementované vo `stream_fill_prefix_5f17`, bez nasledujúceho spracovania súborov `5F3E+`.

## 7. `FF 51` tempo event `15BF:455D–458B` a PIT helper `466A–469E`

Príkaz **nezisťuje deklarovanú dĺžku MIDI meta udalosti**. Na `455D` vykoná `INC DI` (preskočí 1 bajt dĺžky) a následne načíta presne tri bajty (1× `DL`, 1× `AX` little endian, potom `XCHG AL,AH`). Výsledná hodnota `DX:AX` je 24-bit big-endian tempo:

```
tempo24 = (byte0 << 16) | (byte1 << 8) | byte2
Q = tempo24 DIV CS:[2C5A]    // DIV BX, 16-bit AX quotient; x86 #DE if invalid
P = Q * 1E73h                // unsigned 16×16 MUL => DX:AX
timer = (high16(P) * 10) mod 65536
CALL 466Ah                  // if CS:[201E] != 1: PIT init and FFFFh / timer
CS:[2C49] = timer           // only AFTER successful helper return
```

`466A` pri aktívnom PIT (`CS:[201E] != 1`) vykonáva ďalšie **unsigned 16-bit DIV** s `FFFFh/timer`; nulové `timer` preto vyvolá druhú CPU #DE vetvu. Zapisuje `[2DB6]` a `[2DB4]` na rovnaký podiel a potom porty **`OUT 43h,34h`; `OUT 40h,low(timer)`; `OUT 40h,high(timer)`**. Pri `CS:[201E]==1` bez portových zmien, ale `[2C49]` sa stále aktualizuje.

Implementované v `tempo_ff51_455d` s 16-bit aritmetikou a explicitným `PortIO` na PIT. Výnimka C++ `std::overflow_error` je hostiteľské rozpoznanie guest `#DE`, **nie reprodukcia CPU trap stacku**. ES pamäť je explicitne injektovaná; skutočné timing a DOS chyby zostávajú otvorené.

## 8. Testy a dôkazy

- Nové `tests/test_audio_inner.cpp`: port reset + 2 reads, signed `JLE/JGE` boundaries, oba music modes, nulový track count, wrap ticku, 16-bit `DI` wrap, VLQ 10 bajtov modulo 2^32, nepárne PCM clear, oba typy stream fill (`80h` a `00h`), tempo `FF51`, PIT output a obidve `DIV` fault vetvy.
- Vzorový 8-bit mixing byte porovnaný s nezávislým výpočtom micro-op stavu pre **256 vstupných vzoriek × 256 hlasitostí × 5 destinácií = 327 680 kombinácií**.
- `tests/test_audio_inner_static.py`: offline kontrola uloženého manifestu aj voliteľná nezávislá kontrola pôvodného machine image (`WORX_N3D_V20_EXE`).
- V tejto relácii: **7/7 CTest skupín na GCC a 7/7 na Clang úspešných**, s overeným pôvodným EXE. Windows/Visual Studio build a zvukový runtime originálu neboli spustené.

**Kritická hranica:** originálne bajty + testy izolovaných operácií ≠ 100 % audio parity. Najmä stav DMA portov, PCI/ISA routing, IRQ interleaving, celé telá 44B3/5F17/555D a nepriamy XMS callback zostávajú otvorené.
