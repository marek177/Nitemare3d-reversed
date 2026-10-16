# WORX Toolkit 2.1 — RE-1TO1-MAX v0.16: MIDI route 3A67/MPU 58F8 + stream 5F3E

**16. októbra 2026** · **RE-first, presné originálne strojové bajty**, dva pôvodné DOS obrazy:

- N3D DOS v1.9, unpacked MZ load image SHA-256 `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e`, WORX CS image base `0x15BB0`;
- N3D DOS v2.0, unpacked MZ load image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`, WORX CS image base `0x15BF0`;
- oba sú úplne rozbalené MZ s hlavičkou `0x1C00`. Všetky nižšie `CS:xxxx` offsety sú pre DOS v2.0; starší v1.9 má pre tieto rozsahy `IP_old=IP_new+4`. Originálne EXE nie sú publikované.

## 1. Dôležitá oprava kontraktu v0.15: transformácia AX pred 3A67

`3A4D` má `MOV AH,AL; AND AH,F0h; AND AL,0Fh`, **následne** zapisuje `2DC4/2DC8/2DC5/2DC6` a prepadne na `3A67`.

Predtým bol do callbacku `MidiDispatchTail3a67` nesprávne prenášaný celý `AX` z cache `CS:[track*2+2D63]`. Po novom dostáva **`AX=(status&F0h)<<8 | (status&0Fh)`**, teda presný register pri vstupe `3A67`. Testy v0.15 boli opravené a preverujú hodnoty `AX=9000h` pre `90h`, `C003h` pre `C3h` aj integračnú vetvu. Toto neopravuje len popis: od `AH` závisí priamy nibble dispatch `3A74..3A7E`.

## 2. `3A67–3B03` — úplný lokálny routing shell, nie jeho vnorené telá

### Ak `CS:[2DBC] & 06h == 0`

1. `PUSH CS; POP DS`: pôvodné `DS` nie je obnovené, **`DS = actual CS`**.
2. `PUSH AX,CX,SI`, z pôvodného `AH` vytvorí index status-high-nibble, z `CS:[2DA4+SI]` načíta `CL` a nuluje `CH`.
3. `CX == 0` ide priamo na `POP SI/CX/AX; RET`, bez portového prístupu.
4. Inak pošle `AL=CS:[2DC8] | CS:[2DC4]` cez `CALL 58F8`. **Nasledujúci `JCXZ` číta CX po návrate** — nezakladať rozhodnutie na pôvodnej tabuľke, ak FAR callback zmenil CX.
5. Ak CX != 0, vykoná `DEC CX`, pošle `AL=CS:[2DC5]` cez `58F8`, opäť kontroluje CX; pri nenulovom CX vykoná `DEC CX` a pošle `AL=CS:[2DC6]`.
6. `POP SI,CX,AX` obnoví *iba* tieto tri registre. `DS`, `DX`, `ES`, `DI`, `BX` môžu byť pozmenené vnoreným handlerom. 3A67 direct branch **nemá explicitné CLC pri svojom RET**.

Lokálna C++ implementácia `MidiRouting3a67` prijíma zvyšok `3A4D` cez `MidiDispatchTail3a67`, číta živé globály pri každom kroku a vyžaduje skutočný `PortIO`. Neukladá natvrdo historický segment `15BFh`; aktuálne `CS` sa injektuje. Ak chýba nevyhnutný backend, zlyhá explicitne.

### Ak `CS:[2DBC] & 06h != 0`

- `status_type > 90h` a `<= B0h`: `CALL 3941`; `status_type > B0h` a `<= C0h`: `CALL 3E34`; `status_type > C0h`: bez callbacku.
- `status_type <= 90h`: volá `3B5B`, predtým môže zmeniť `CS:2DC5 = (CS:2DC5 + CS:2DA3) mod 256`.
- Ak `CS:2DC9 & 20h` je nastavený, transpozícia sa **preskočí**, keď `(2B4D==1 && channel==9)` alebo `(2B4D!=1 && channel>=0Bh)`. Bez bitu 20h sa vykoná bez ohľadu na tieto špeciálne výnimky.
- `3B02 CLC; RET` sa vykoná na tejto nepriamej/synth vetve, nie na direct branch `3AA7..3AAA`.
- Obsah `3941`, `3E34`, `3B5B`, ich nepriame callee, OPL registrácia hlasov a PC speaker sú **explicitné otvorené back-endy**, nie falošné implementácie.

## 3. `58F8–5925` — presný lokálny MPU-401 byte sender

`PUSH AX,CX,DX`, `AH=AL`, `CX=FFFFh`, `DX=0331h`, opakovane `JCXZ; DEC CX; IN AL,DX; TEST AL,40h; JNE`.

- Po maximálne **65 535** čítaniach `IN 0331h` funkcia ukončí polling; ak každý status obsahoval bit `40h`, **nespraví žiadny `OUT` ani FAR callback**.
- Pri pripravenom porte: obnoví bajt z `AH`, `DX=0330h`, `OUT DX,AL`, potom obnoví `DX,CX,AX` a testuje `CS:[3898]`.
- Keď je `CS:[3898]!=0`, vykoná **`CALL FAR CS:[3896]`**. Toto je ďalší otvorený backend; môže modifikovať návratové registre a zmeniť `CX` pri nasledujúcom `3A93/3A9D JCXZ`.
- Ak je `CS:[3898]==0`, návrat bez FAR callbacku. Port `0330h/0331h` predstavuje konkrétny originálny hardvérový protokol, nie jeho simuláciu.

Model `mpu_send_58f8` vykonáva 65 535-poll cap a presné poradie čítaní/zápisov. Callback sa musí explicitne dodať, ak je jeho volanie dosiahnuté; chýbajúci callback vyhodí výnimku až **po fyzickom `OUT`** do injektovaného backendu. Reálne časovanie/IRQ zostáva otvorené.

## 4. `5F3E–5FBE` — stream header gating a dispatch

Tento shell sa spúšťa **až po** `5F17–5F3D`, ktoré nastavuje `CS:2DEA=1` a prípadne vykoná fill do `ES:DI` — tento prefix bol auditovaný v0.13, ale nie je súčasťou `stream_route_5f3e`.

- Len ak `(CS:[48DF] | CS:[48E1]) == 0` **a** `CS:[48EE] == 0`, vykoná nové header/file čítania.
- Pri `CS:[4740]&1`: prepíše **celý `CS:4740` na `00h`**, zavolá `5A3F` s `AL=D0h` a až potom `OUT 0Ah,05h`.
- `CALL 312E(BX=1,ES=CS,DI=48E3h)`: ak vráti `AX!=1`, okamžite `CALL 4741; STC; RET`.
- Ak vráti `AX==1`, pokračuje `CALL 312E(BX=3,ES=CS,DI=48DFh)`. **Jeho návratový AX už nekontroluje**, takže je možné odoslať staré/čiastočné bajty do ďalšieho mode dispatch, keď DOS čítanie vráti menej bajtov.
- Presné poradie výberu módu `CS:[48E3]`: `0Ch -> 5FD2`, `03h -> 5FF3`, `08h -> 5FBF`, `09h -> 6092`, `02h -> 60E8`, `01h -> 6037`, **všetko ostatné** -> `CALL 4741; STC; RET`.
- Bolo možné použiť už hotové lokálne v0.14 podkontrakty módov `08h` a `0Ch`. Módy `01h/02h/03h/09h` sa len prenesú na povinný callback podľa presného targetu; **nie sú tým považované za portované**.

Takto zostáva rozdiel medzi *dosiahnutou vetvou* a *úplným transitive behavior* explicitný.

## 5. Reprodukovateľné originálne byte dôkazy a testy

Dva verifikátory pracujú s pevnými SHA-256, kompletnými porovnávanými rozsahmi a súpisom ich lokálnych vetiev/volaní:

| Úsek | Pôvodné bajty | Opcode kotvy | Lokálne skoky | Priame CALL | Rozdielne bajty DOS v1.9/v2.0 |
|---|---:|---:|---:|---:|---:|
| `3A67–3B03` a `58F8–5925` | 203 | 32 | 17 | 6 | 18, všetky operand +4 |
| `5F3E–5FBE` | 129 | 17 | 13 | 4 | 13, všetky operand +4 |
| **Spolu** | **332** | **49** | **30** | **10** | **31** |

Dôkazy: `data/worx21_midi_routing_v016.json`, `data/worx21_stream_routing_v016.json`. Verifikátory `tools/audit_midi_routing_v016.py`, `tools/audit_stream_routing_v016.py` vrátane testov negatívnej mutácie.

```
python tools/audit_midi_routing_v016.py /path/N3D_DOS_v1.9_IDA.EXE /path/N3D_DOS_v2.0_IDA.EXE
python tools/audit_stream_routing_v016.py /path/N3D_DOS_v1.9_IDA.EXE /path/N3D_DOS_v2.0_IDA.EXE
cmake -S . -B build
cmake --build build
WORX_N3D_V19_EXE=/path/N3D_DOS_v1.9_IDA.EXE WORX_N3D_V20_EXE=/path/N3D_DOS_v2.0_IDA.EXE ctest --test-dir build --output-on-failure
```

**Lokálna akceptácia:** 11/11 CTest skupín úspešných (C++17 + statické Python testy) s oboma pôvodnými EXE; zámerná mutácia originálneho bajtu je zamietnutá hash kontrolou. Toto potvrdzuje iba presné lokálne machine-derived kontrakty a ich izolované testy, **nie** 100 % audio/timing/IRQ paritu.

## 6. Ďalšie neznáme, v priorite

1. `3B5B..3CB8`: transitive OPL / PC speaker, najmä per-channel hlasové tabuľky, všetky fallback vetvy, CALL 38A7 a skryté state aliasy.
2. `5FF3..6149`: dokódovanie módov 03,09,02,01; helper `610C`, `312E` úplné DOS služby, následné EOF/wrap/CF, `4741` close.
3. `58F8` nepriame `CS:3896` callback a jeho reálny read/write/flags; hardware port 0330/0331 timing.
4. `555D–5663` eight-voice PCM mix: 8-voice loop, refill, 16:16 phase a sample pointer alias; nejde to korektne uzavrieť samotnými prefixmi.
5. Originál/clone trace iba na to, čo nie je staticky rozhodnuteľné: porty, IRQ, XMS, DMA, PIC a emulačná parita.
