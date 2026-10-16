# WORX Toolkit 2.1 / RE-1TO1-MAX v0.14 — uzatvorené statické čiastkové kontrakty

**16. október 2026.** Originálne plne rozbalené súbory:

| Hra | MZ veľkosť | SHA-256 obrazu (za 0x1C00 hlavičkou) |
|---|---:|---|
| N3D DOS v2.0 | 178 528 B | `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297` |
| N3D DOS v1.9 | 178 464 B | `e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e` |

Všetky adresy `CS:xxxx` nižšie sú **adresy originálneho v2.0 WORX kódu**, nie offsety na disku. WORX `CS` obrazový základ je v2.0 `0x15BF0`; fyzický offset do EXE je `0x1C00 + 0x15BF0 + xxxx`. Výsledky v tomto dokumente vznikli čítaním originálnych machine bytes, `objdump -m i8086`, samostatnými C++17 kontraktmi a kontrolou priamych vetviacich inštrukcií.

## 1. `CS:44B3–44ED` — presný vstupný MIDI track gate

Pri vstupe si `BX = (CS:[2DC0] << 1) mod 65536` a testuje bit 0 celého slova `CS:[BX+2C62]`. Ak bit chýba, funkcia sa vracia. Ak je stopa aktívna, zdvojnásobí `BX` a načíta 32-bitové počítadlo z `CS:[BX+2CA2]` (low) a `CS:[BX+2CA4]` (high). Ak je nenulové, vykoná `SUB low,1; SBB high,0` a vráti sa. Pri nule nastaví `ES=CS:[2C5F]`, `DI=CS:[(track*2)+2D22]` a prejde do čítania udalosti `44EE`.

`midi_track_gate_44b3()` modeluje iba tieto rozhodnutia, čítania/zápisy a výstupný cursor. **Nie parser udalostí po `44EE`.** Testuje sa `00010000h→0000FFFFh` aj inactive bit-mask.

## 2. `CS:4553–455B` — neznámy MIDI meta type

Originál vykonáva `XOR AH,AH; MOV AL,ES:[DI]; INC DI; ADD DI,AX` — teda jediný 8-bitový údaj dĺžky, nie MIDI VLQ. Pri `DI=FFFFh`, length `FEh` vyjde `DI=00FEh`. Implementované v `midi_unknown_meta_skip_4553()`.

## 3. `CS:458C–45DC` — End-of-Track spracovanie

- `CS:[(2*track)+2C62] = 0000h` (celé slovo).
- `CX=CS:[2C58]`, `BX=0`; `TEST WORD CS:[BX+2C62],FFFFh` kontroluje **ľubovoľný bit**, nie iba bit0 používaný v `44B3`.
- Pre nenulové slovo na ktorejkoľvek skenovanej pozícii sa spraví `INC WORD CS:[2DC0]` (aktuálny globálny index **+1**, nie index nájdenej stopy) a skok späť na `44B4`.
- Ak nenájde aktívnu pozíciu, `CS:[2C61]` rozhoduje o reštarte. Pri nenule `CS:[2C5C]==1` volá `4389`, inak `4265`, s `ES:DI=CS:[2C5D]`. Všetky volania následne skáču do `44B4`.
- Pri `CS:[2C61]==0` nastaví `CS:[2D62]=0` a tiež skočí do `44B4`.

**Extrémny alias:** `CX=0` s inštrukciou `LOOP` znamená až 65536 skenovacích testov, nie nula. Adresa `CS:2D62` leží `0100h` bajtov, čiže 128 slov, od začiatku skenovanej oblasti `CS:2C62`. Ak všetky skoršie testy vrátia nulu a `CS:[2D62] != 0`, pokladá sa na **129. teste** za aktívnu stopu, hoci ide o globálny príznak hudby. Pri kompletne nulovom stave prejde slučka 65536 testami. Toto je **staticky vyvolateľná okrajová vetva**, nie doklad že nastáva počas normálneho hrania.

V C++ `midi_end_track_458c()` implementuje lokálny scanner a pamäťové účinky. Callbacks `4265/4389` sú povinné injektované závislosti; ich výsledky a ďalší návrat do `44B4` **nie sú simulované ako hotové**. Ak callback chýba, pri dosiahnutej vetve nastane explicitná výnimka.

## 4. `CS:5863–58D7` — XMS refill, argumenty pred FAR CALL

Parametre sa ukladajú do **CS:21CC–21DA**. Celý direct shell modeluje `xms_refill_packet_5863()`:

| Offset CS | Význam vyplývajúci z priamych inštrukcií |
|---|---|
| `21CC` | `0100h`, dĺžka prenosu 256 bajtov |
| `21CE` | **nezmenené**, môže obsahovať hodnotu z predchádzajúceho použitia |
| `21D0` | `CS:[21C6]` (XMS handle / prevádzkový parameter) |
| `21D2` | nízke 16 b `CS:[20C6+4*resource] + cursor` |
| `21D4` | vysoké 16 b `CS:[20C8+4*resource] + carry` |
| `21D6` | `0000h` |
| `21D8` | buffer v CS: `4CEDh + ((voice_bx >> 1) * 0100h)` pre bežných osem hlasov |
| `21DA` | skutočný segment `CS`, nemôže byť natvrdo `15BFh` v novej hostiteľskej aplikácii |

`CS:[54ED+voice_bx]` dostáva pôvodný cursor `CS:[4BCF+voice_bx]`. Nastaví `AH=0Bh`, `SI=21CCh` a vykoná nepriamy **CALL FAR cez `CS:[21C8]`**. Výsledok `AX` sa síce porovná s `0001h`, no následne `POP AX` obnoví vstupný AX. **Pôvodný AX je teda viditeľný pri obyčajnom návrate**. Služba a jej vedľajšie účinky stále závisia od runtime XMS a sú oddelené injektovaným rozhraním `XmsFarService`.

Výslovne **nie je uzatvorená** prístupnosť 256-bajtového bloku, reálny XMS callback, bank prepnutie, CPU stack pri chybe, ani všetky event-path vyvolávajúce 5863.

## 5. Streamer pri mode `08h` a `0Ch`

`5FBF–5FD1` / mode `08h`: `BX=CS:[48DF]`, `ES=CS`, `DI=5E69h`, `CALL 312Eh`, potom **`SUB WORD CS:[48DF],AX` bez `SBB` horného slova `CS:[48E1]`**. Pri `AX>low` sa low-word pretečie. Read backend je explicitný (`Read312e`).

`5FD2–5FF2` / mode `0Ch`: `CX=CS:[48DB]`, `SUB [48DF],CX; SBB [48E1],0; JAE return`. Iba pri skutočnom 32-bitovom podtečení sa oba wordy nastavia na nulu. Toto je **saturácia počítadla dĺžky streamu**, nie saturácia PCM vzoriek.

Obe vetvy majú samostatné C++ rutiny a testy. Vonkajšia dispatch funkcia `5F17` a ostatné stream módové cesty (`01,02,03,09`) nie sú celé uzatvorené.

## 6. Priama krížová kontrola medzi DOS v1.9 a v2.0

Súbor `tools/compare_worx_versions_v014.py` porovnáva týchto šesť zafixovaných inštrukčných rozsahov v dvoch originálnych DOS EXE. Stará v1.9 oblasť zodpovedá v2.0 pri **image posune −0x3C**. V rámci týchto 6 rozsahov sa líši **41 bajtov** a každý je presne `old = new + 4` na nízkom bajte zodpovedajúceho adresného operandu. Iné rozdielne bajty v týchto rozsahoch neexistujú.

Presné mapovanie +4 navyše **potvrdzujú dva pôvodné `CALL FAR`** v N3D: pri inicializácii stará v1.9 volá `15BB:2E81` (image `11A2E`), kým v2.0 `15BF:2E7D` (image `11A6A`); pri shutdowne `15BB:2F6A` verzus `15BF:2F66`. Segmentový základ v1.9 sa teda znížil o `4 × 16 = 0x40` obrazových bajtov, zatiaľ čo offset vnútri WORX segmentu narástol o 4 bajty, čo dohromady dáva posun `−0x3C`.

Toto podporuje stabilitu skúmaných direct inštrukčných algoritmov naprieč verziami, **nie** identitu celého WORX runtime, dát, hardware alebo volaných subrutín.

## 7. Reprodukcia a hranica overenia

```
python tools/audit_audio_deep_v014.py N3D_DOS_v2.0_IDA.EXE --json output.json
python tools/compare_worx_versions_v014.py N3D_DOS_v1.9_IDA.EXE N3D_DOS_v2.0_IDA.EXE
cmake -S . -B build
cmake --build build --config Release
# Na Linuxe s pôvodnými súbormi:
WORX_N3D_V19_EXE=/path/to/v1.9.EXE WORX_N3D_V20_EXE=/path/to/v2.0.EXE ctest --test-dir build --output-on-failure
```

V tejto relácii bolo overené **6 čerstvých SHA256 machine-span dôkazov, 25 operačných opcode kotiev, 11 priamych vetiev a 41 rozdielnych byte operandov cross-version**, 8/8 CTest skupín GCC aj Clang, s oboma originálmi dostupnými. Nie je to 100 % audio parita ani hotový celý dispatcher 79 funkcií. **Počet doposiaľ známych API handler kontraktov zostáva 41/79 nenulových; v0.14 uzavrela vnútorné subkontrakty.**
