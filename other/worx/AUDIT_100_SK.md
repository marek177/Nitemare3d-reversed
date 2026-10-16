# Dôkladný audit medzier WORX Toolkit 2.1 → 100 % 1:1

**Prísna stupnica dôkazu**

- **A / priamo doložené:** z predchádzajúceho binárneho auditu N3D DOS v2.0 a/alebo nezávisle potvrdeného N3D wrapper pseudokódu.
- **B / sekundárny dôkaz:** Ghidra pseudokód, ktorý môže zlyhávať pri overlapped code a real-mode far pointeroch.
- **C / cudzia verzia:** WORX v *In Search of Dr. Riptide* alebo *Dark Seed CD*, neplatí automaticky pre N3D.
- **U / otvorené:** nemáme priamy N3D machine-code proof alebo konformančnú stopu.

## 1. Identita a rozloženie

Podkladový audit N3D DOS v2.0 (Pass 23/28): plne rozbalený obraz `0x29D60` (171 360 B), MZ hlavička `0x1C00`, očakávaný SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

| Rozsah obrazu | Klasifikácia | Stav |
|---|---|---|
| `10BFC–11EE6` | 75 N3D→WORX obalov (4843 B) | A – štruktúra |
| `15BF7–17BFF` | inicializované dáta/buffery (0x80 od `15BFE` do `17BFF`, spolu 8194 B) | A – hranice, U – použitie každého bajtu |
| `17C00–18A04` | WORX statické tabuľky a konfig | A – oblasť, U – schémy všetkých tabuliek |
| `18A05–1BD92` | WORX kód premiešaný s krátkymi dátami | A – identita, U – každý algoritmus |
| `1BD93–1BDA1` | koncové dáta | A – hranica, U – každé pole |

Vstupy/obsluha: **init `0x18A6D`**, **shutdown `0x18B56`**, **INT63 handler `0x18CD6`**, **INT08 timer `0x19D40`**. Pri bajtovom audite sa používajú image offsety, nie fyzický offset EXE ani živý segment DOSBoxu. WORX `INT08` sa nesmie stotožniť s herným `INT70`.

**Dôležité:** premapovanie kódu na „WORX modulu patrí“ je dôkaz vlastníctva funkcie, nie dôkaz algoritmickej 1:1 rekonštrukcie.

## 2. Skutočne uzatvorený výsledok tejto analýzy

- **75/75 wrapperov** je v Pass 23 ohraničených, contiguous 4 843 B.
- `data/n3d_v20_wrappers.json`: **70 rozdielnych príkazov `AH`** explicitne pomenovaných v popisoch; najvyšší `51h`.
- **12 hodnôt AH** v rozsahu `00h–51h` nemá v inventári explicitne pomenovaný N3D wrapper: `00 03 19 24 26 2E 2F 30 46 4E 4F 50`. Ani jedna nesmie byť bez rozboru dispečera označená ako mŕtvy kód.
- **5 wrapperov** neuvádza v popise priamo kód AH: `10BFC` centrálne volanie, `10C5F` shutdown thunk, `10DC9` kompozitný resolver, `11392` resolver, `11A5D` init thunk.
- **9 príkazov s N3D call-site dokladom o konkrétnom účele:** `01`, `02`, `04`, `0D`, `15`, `1C`, `21`, `22`, `2C`. Toto nie je celkový počet potenciálne pochopiteľných príkazov; iba silnejšie priamo pomenované účely.
- Sekundárny Ghidra `.c` obsahuje **75/75 očakávaných funkcií**: **72 priamych volacích výrazov** do centrálneho obalu, **0 rozporov AH** oproti Pass 23, ale to nie je nezávislé strojové overenie — obidve informácie pochádzajú z tej istej hry. Vstup `0x1151C` s príkazom `43h` je Ghidrou označený ako `switchD_2000:33f7::switchdataD_2000_151c`, nie `FUN_2000_151c`; NESMIE byť zmazaný ako falošný code entry.
- Kompozitné obaly na `0x11CCD` a `0x11D33` volajú **dva príkazy v poradí** (`33→35`, resp. `41→35`); potrebné držať poradie a medzistavy/CF. Tento nález overuje sekundárny text voči invetáru, nie originálny beh.

## 3. Kľúčový rozdiel medzi dvoma WORX 2.1 buildmi — nový blocker

Reverzný listing WORX v hre *In Search of Dr. Riptide* (`xor2003/riptide-re`, `decomp/seg1c75.asm`) obsahuje `word_20950` so **79 16-bitovými položkami** od `AH=00h` po `AH=4Eh`. Handler vykonáva `xchg ah,al`, `shl ax,1`, `call cs:word_20950[si]`; nevidno kontrolu hornej hranice pred prístupom. Niektoré položky sú nulové.

N3D v2.0 však obsahuje wrapper `AH=51h` (`0x11EB9..0x11EE6`), ktorý leží **nad koncom zdokumentovanej Riptide tabuľky**. Z toho vyplýva:

- Nie je bezpečné prevziať **Riptide dispečerskú tabuľku** do N3D ani predpokladať, že rovnaké AH = rovnaký algoritmus v oboch buildoch.
- N3D má iný zostavený build, doplnené funkcie, inú schému alebo iné spracovanie pri konci tabuľky; presná príčina zostáva **U**.
- Výskyt `AH=51h` v wrapperi ešte sám o sebe neznamená, že ho hra počas bežného hrania skutočne volá. Vyžaduje call graph, konštantné podmienky alebo runtime stopu až v poslednom kroku.

Táto nekompatibilita sama o sebe môže poškodiť 1:1 aj pri identických zvukových dátach.

## 4. Mapa otvorených algoritmov (RE-first)

| Priorita | Mechanizmus a konkrétne neznáme | Ako uzavrieť **staticky** | Kedy runtime |
|---|---|---|---|
| P0 | **N3D dispečer `0x18CD6`: AH rozsah, 12 nenazvaných selektorov, fallback/nulové sloty, CF a AX/DX** | dekódovať skutočnú N3D jump table, indexovanie a bounds guard, linkovať každý slot na body+callers | iba spor, ktorú vetvu umožňuje vstup/hardware |
| P0 | **stavové bajty, mode/flags, sekvencia `AH=32h,34h,35h,4Fh,50h,51h`** | pre každé pole writer→reader, defaults, masks, invarianty; analyzovať `mode +2DBCh`, writer okolo `+3004h` vo vhodnom segmente | iba interakcia IRQ a driver-audio behu |
| P0 | **WORX init/shutdown a ISR**: obnova vektorov, tick rounding, reentrancia, nestabilné volania | CFG init `18A6D`, shutdown `18B56`, INT08 `19D40`, save/restore IVT, maskovanie IRQ, ochrana zdrojov | race/časové hrany, keď statika nerozlíši reálne správanie emulátora |
| P0 | **PCM mixer**: mix s/bez saturácie, 8-bit wrap, kanály, hlasitosť, interpolácia | inštrukčne prepísať `1B0F2..1BD92`, počiatočné 0x80 buffery, presný write order | len porovnanie výstupných bajtov pre viac hlasov |
| P0 | **digitized/SB DMA**: IRQ, DMA scheduling, DSP detekcia, začiatok/koniec sample | hodnoty portov, DMA page/base/count, `OUT/IN`, IRQ end-of-interrupt, DSP reset handshakes | potvrdiť zariadenie a poradie zápisov pri hre |
| P1 | **OPL/AdLib**: hráč bank, note allocation, freq, KSL, velocity, pitch/rhythm | porovnať N3D assembler proti cross-game ScummVM kandidátovi, extrahovať 128 instrumentov ak prítomné | OPL register log, ak statika necháva alternatívy |
| P1 | **MIDI/CMF/MT-32**: tempo/delta-time, running status, stop/loop, controller effects | rozobrať parser, event queue, tempo integer overflow, všetky controller switch-cases | timing / MIDI stream compare |
| P1 | **SND.DAT / PCM / WAV / VOC**: decoder, offsety, null zdroje, cykly | EXE→SND.DAT references, formát hlavičiek, endian a off-by-one | neočakávané poškodené dáta/hardvérové reakcie |
| P1 | **speaker/PIT**: frekvencia, gate, volume fallback, stop | `0x43/0x42/0x61` presný port model, časovač | porovnať toggles/cycles |
| P2 | **resources/XMS/far pointer**: EMS/XMS, prázdne tables, chyby | kontrolovať 16:16 adresáciu, segment overflow, heap lifetime | hardvérové zlyhanie/pamäťové konflikty |
| P2 | **joystick**: poradie štyroch 2Ch statusov, debouncing/polarita | volajúce N3D funkcie, register map | analog timing podľa reálneho zariadenia |
| P2 | **skryté/dead branch**: všetky dispečerské sloty a závislosti | call graph reachability, IF-masks, symbolické vetvenie, nepriamo dosiahnuteľné sloty | iba nedecidovateľný externý vstup alebo timing |

Význam `0x80 × 8194 B`: vysoko plausibilný unsigned PCM silent-init, ale **rozdiel 8194 vs. 8192 B** a presné spotrebiteľské pointery nie sú dokázané ako „8192 sample + 2 sentinel“; neodvodzujte takýto layout bez xref dôkazu.

## 5. Výslovné limity „100 %“

**Nehodnoťte tento balík ako 100 % WORX Toolkit.** Statická klasifikácia 25 003 B a 75 presne ohraničených wrapperov je značná znalosť štruktúry, ale bez rozboru inštrukčného kódu interného handlera, ISR, mixera a zariadenia nemožno dokázať exact behavior. Na 100 % sú potrebné nezávislé doklady:

1. **všetky príkazy a návratové registre** (vrátane error CF a zdrojových pointerov),
2. **všetky dosiahnuteľné vnútorné stavy** drivera a ich prechody,
3. **úplná sekvencia audio/MIDI I/O udalostí** s časovaním,
4. **bit-exact PCM samples / OPL registers** pre nastavenú cieľovú emuláciu,
5. **konformancia pri chybách a rare branches**,
6. porovnanie **originál DOS verzia vs. rekonštrukcia** na ekvivalentnom logovanom virtuálnom hardvéri.

**Dostupnosť podkladov tejto relácie:** pôvodné poznámky a sekundárne Ghidra `.c` boli dostupné; presný pôvodný N3D DOS v2.0 binary `N3D_DOS_v2.0_IDA.EXE` ako súbor na čítanie **nebol** dostupný. Preto v tejto relácii prebehlo overenie konzistencie existujúcich dokladov, nie nový úplný instruction-by-instruction audit originálu.

## 6. Súbory dokazujúce výsledky

- `data/n3d_v20_wrappers.json` — všetkých 75 vstupov, adresy, funkčný opis, príkazy.
- `data/n3d_v20_ghidra_secondary_calls.json` — 75 dekódovaných decompiler identít, 72 expressions, bez rozporov pri AH literáloch.
- `tools/audit_wrappers.py` — kontrola contiguous spans a chýbajúcich AH.
- `tools/audit_n3d_image.py` — keď bude dostupný exakt hashovaný DOS EXE, offline binárna kontrola.
- `tools/extract_ghidra_wrapper_calls.py` — reprodukovateľný parser Ghidra `.c`.
- `tools/compare_riptide_dispatch.py` — cross-game zistenie odlišnej veľkosti `INT63` tabuľky.

Zdrojové dokumenty: `Nitemare3D_RedOrangeYellow_closure_pass23_2026-10-03(1).md` a `...pass28...md` (osobné RE poznámky); zdroje z iných hier v `evidence/sources.json`.
