# WORX 2.1 — cesta k 1:1, striktne RE-first

Každý ďalší krok má mať **vstup → presný statický dôkaz → testovací kontrakt → identifikátor uzavretia**. Runtime iba keď statika ponecháva relevantnú neistotu.

## Pas A — pôvodný N3D binárny handler

**Vstup:** `N3D_DOS_v2.0_IDA.EXE`, image SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.

1. Spustiť `audit_n3d_image.py` a potvrdiť identitu súboru; nesmie sa akceptovať len rovnaký banner WORX.
2. V IDA Free 9.2 prepnúť na 16-bit REAL MODE; `15BF:30E6` = N3D **INT63 handler**. Identifikovať presné rozkúskovanie registra `AH/AL`, prvý/posledný slot, všetky skoky a nulové príkazy.
3. Pre 70 v inventári použitých selektorov, plus 12 nenazvaných, postaviť kompletný *dispatch matrix*: `AH, handler_image_offset, input_regs, output_regs, CF, state_reads, state_writes, callers`.
4. Pokryť všetky príkazy v jednom source module s explicitným `UNKNOWN` ak vetva nie je uzavretá, žiadne fiktívne štandardné návratové hodnoty.
5. V rámci reinštalácie a shutdown kontrolovať zachovanie pôvodných IVT entry pre `63h` a `08h`; zachytiť všetky mask/flag kúsky.

**Výstup:** identický `AH` dispečer + total typed command map; 100 % statické poznanie dispatcher path (nie ešte zvuku).

## Pas B — prerobiť N3D-facing wrappery do 1:1 C

1. Pre každú zo 75 originálnych funkcií získať jej 16-bit ASSEMBLY, argumenty `[BP+...]`, segmente a počet stack bajtov pri `RETF`.
2. Vytvoriť C/C++ funkciu so 16-bit word truncation, sign-extension, rozlíšením `near/far` pointerov, SIDE EFFECTS a presným poradím vnorených príkazov.
3. Pri `33→35` a `41→35` vypísať dvojicu volaní aj v stave chyby/CF; žiadne kompozitné "shortcut".
4. Pri `0x1151C` nezahodiť funkciu iba preto, že Ghidra ju označuje `switchdataD`.
5. Urobiť testy funkcia po funkcii; každá musí mať „má vlastný disasm“, „má presný register/stack contract“, „má unit regression“.

**Výstup:** 75 úplných telies, nielen dátový inventár. V tomto balíku zatiaľ implementovaný iba generický adaptér a 8 bezpečne typovaných ciest.

## Pas C — mixer & OPL/MIDI

- Výstupy OPL `388/389`, MIDI tempo a N3D bank sa musia odvodiť z N3D, nie bez porovnania z Dark Seed.
- PCM mixer prepísať inštrukciu po inštrukcii vrátane saturácie/wrap, interpolácie, aktualizácie cursorov a „tichého“ bufferu.
- Explicitne definovať `tick` jednotku, PIT konfiguráciu, ISR priority, vlastné audio timeouty a sekvenciu hlavného a IRQ threadu; register trace musí byť deterministický.
- Statické dôkazy aj pre boss/weapon/level eventy N3D, ktoré generujú WORX volania a zvuky.

**Výstup:** každá vetva zvuku vracia presné bajty a register/write sekvenciu pre definovanú virtuálnu konfiguráciu.

## Pas D — potvrdenie posledných nejednoznačností runtime

Ak statický obraz nedokáže jednoznačne určiť skutočný výsledok fyzického zariadenia/timeru, až potom DOSBox-X debugger s **originálnym DOS EXE**, nie s rozbaleným Ghidra pomocným obrazom:

```text
call_index,game_tick,caller_cs,caller_ip,ax_in,bx_in,cx_in,dx_in,si_in,di_in,
ax_out,bx_out,cx_out,dx_out,si_out,di_out,CF,driver_mode_before,driver_mode_after
```

Testovacie scenáre: init/shutdown, DOS config detekcia, menu music, level music, 1× SFX, 2× simultánny SFX, SFX replacement, muted SFX, music enable/disable, speaker fallback, posledná/prázdna vzorka, práca s poškodeným WAV/VOC, LOAD game, výstrel/hit, výmena levelu, reentrancia pri ISR, nevyriešené AH 13/32/34/4F/50/51.

Zvlášť ukladať portové udalosti `(tick,port,width,read/write,value)`, audio PCM output `SHA256`, OPL register diff a počet IRQ. Bez týchto stôp sa „100 % časovanie/vzorky“ nikdy nesmie deklarovať.

## Akceptačný záznam pre každé uzavretie

```text
ID: WORX-INT63-<AH> / WORX-PCM-<subsystem>
Dôkaz EXE: SHA256, image offset, ASSEMBLY byte range, CFG + data refs
Pseudokód: explicitné šírky (u8/u16/s16), flags, side effects, memory aliases
Implementácia: source file + function symbol
Kontrakt: input registers + state -> output registers + state + I/O
Testy: unit exact + static cross-reference + event trace, keď nevyhnutný
Stav: VERIFIED_STATIC / VERIFIED_RUNTIME / CANDIDATE / UNKNOWN
Výnimky: žiadne untested fallthrough pre 100%
```

**Prvé konkrétne miesto na pokračovanie:** `15BF:30E6` (N3D dispečer `INT63`), jeho skutočná tabuľka a `AH=51h`; až potom zamerať PCM `0x1B0F2..0x1BD92` a ISR `15BF:4150`. To minimalizuje riziko nesprávnej implementácie všetkých vyšších vrstiev.
