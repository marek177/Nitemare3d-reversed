# Nitemare 3D Win 1.10 — Ghidra 12.2, prechod 5

## Zistenie

Dokončil som ďalší statický prechod v skutočne spustenej Ghidre 12.2: rozšírenie message máp, obnovu inicializačných callbackov a chýbajúcich priamych callee, plus konkrétny model kopírovania VGA obrazu pri opustení priameho video režimu.

Výsledok obsahuje **1 535 interných funkčných vstupov**; počet neklasifikovaných bajtov kódových segmentov klesol na **2 316**. Pribudnutie funkčného vstupu stále nie je dôkaz úplnej sémantiky. Hra sa v tomto prechode nespúšťala a framebuffer/DAC parita nebola testovaná.

## Identita

Win16 EXE 230 400 B, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra 12.2 build 20261016; JDK 25.0.2; headless projekt `WIN110`. Adresy `1000/1008/1010/1018` označujú NE kódové segmenty 1–4; `1048` je inicializovaný DS segment 10. DOS a iné Win16 buildy sú mimo tohto dôkazu.

## 1. Presný video-copy výrez `1010:46F8`

### Dôkaz

| Status | Operácia | Zdroj a miesto | Istota |
|---|---|---|---|
| Confirmed | Cieľový selector sa načíta z `DS:51A0` do ES, cieľový offset je 0. | `4706–470B`, respektíve `4721–4726`. | High |
| Confirmed | Source DS selector je import `KERNEL!__A000H`. | NE seg3 relocation record #43, source chain sites `470F/472D`, type 5, flags 2 (import by name), module 1 = KERNEL, import-name offset `10h` = `__A000H`. | High |
| Confirmed | Pri `word46B6 == 10` kopíruje 32 000 wordov. | `46FE–471F`, `CX=7D00h`, `REP MOVSW`, source/destination offset 0. | High |
| Confirmed | Inak volí page base 0 alebo `4000h` podľa porovnania `word00C0 == A000h`. | `4732–473E`. | High |
| Confirmed | Nastaví VGA index portu `3CEh` na 4 a na `3CFh` zapisuje plane 0–3 pre jednotlivé stĺpce. | `4743–4755`, `4760–4769`. | High pre portové zápisy |
| Confirmed | Má 320 vonkajších a 200 vnútorných iterácií; normálne kroky sú source +80, destination +320. | `474C`, `4750`, `MOVSB` na `4756`, ADD `13Fh`/`4Fh`. | High, pre kladné kroky sa vyžaduje DF=0 |
| Confirmed / Inferred | Pri bežnom VGA read mode 0 sa výsledok skladá zo štyroch rovín podľa vzorca nižšie. | Binárna slučka a štandardná VGA read-map operácia. Funkcia sama read mode 0 nenastavuje. | High pre adresovanie, podmienené stavom VGA |

Hodnota `00BCh`, ktorú dekompilátor zobrazuje ako source selector, je Ghidra reprezentácia importu; **nie je pevnou runtime hodnotou Windows selectora**. Pôvodný EXE operand obsahuje relokačný link, nie výsledný selector. Dve offsetové nuly v C exporte tiež neznamenajú, že funkcia kopíruje z null pointera do null pointera: source DS a destination ES sú rôzne segmenty.

### Model použiteľný v implementácii

Za predpokladu **DF=0 a VGA read mode 0**:

```text
if word[46B6] == 10:
    destination[0:64000] = source_A000[0:64000]
else:
    pageBase = 0 if word[00C0] == A000h else 4000h
    destination[320*y + x] = plane[x & 3][pageBase + (x >> 2) + 80*y]
    # x = 0..319, y = 0..199
```

Plane sa mení po každom stĺpci. Source column sa zvýši po každej štvorici stĺpcov. Posledný zápis read-plane registra v planar vetve je 3; funkcia tento register neobnovuje. DS obnoví, ES ponechá nastavený na cieľ. DF ani VGA read mode funkcia sama nenastavuje. Palette/DAC konverzia je mimo tohto výrezu.

`scripts/win110_capture_model.py` obsahuje doslovný slučkový model aj nezávislý indexový vzorec. Overené sú oba page base varianty × tri deterministické vzory, spolu **384 000 planar bajtov**, a **64 000 bajtov lineárnej vetvy**. Navyše sa kontroluje 64 000 jedinečných source adries na obraz. Ide o test modelov podopretých raw inštrukciami, nie o zachytený framebuffer originálu.

## 2. Strata fokusu a klávesové masky

Potvrdená lokálna cesta je:

`CNite3wView WM_KILLFOCUS → 1010:0ABE → 1000:12BE → virtual default handler`, potom `1010:2D9C(4)`.

V `2D9C` sú úvodné guardy HWND slov `00B6/00B8/00BA/00BC`. Pri platnej ceste parametra 4 volá `2D58`, vypočíta rozmery a následne vykoná spoločnú obnovovaciu cestu. `2D58` pri `byte46B0 != 0` robí v poradí:

1. `A3B6(17h)`.
2. `46F8`, vyššie doložené kopírovanie obrazu.
3. Import na `1200:00D8` s hodnotami `0,0,4040h`.
4. `RELEASECAPTURE`.
5. `1018:3322(1)`.
6. `2C62(5)`.
7. Vždy nuluje `byte46B0`.

Samostatná funkcia **`1010:90C2`** preukázateľne nuluje byte `0108` a **word `3756`**, teda oba bajty `3756/3757`. Z focus-loss handlera k nej v exportovanom grafe **známych priamych volaní** nie je cesta; graf dosahuje 228 cieľov po vylúčení computed-call referencií. Toto **nepreukazuje**, že klávesy po focus loss zostanú stlačené. Graf neuzatvára virtuálne ciele, synchrónne callbacks externých Windows API, pointerové/bulk zápisy ani budúce správy okna.

Známe absolútne zápisy na tieto masky sú v `8CD2`, `90C2` a `90CE`; nie je to dôkaz úplného zoznamu všetkých nepriamych writerov. Runtime test keydown → strata fokusu → keyup mimo okna → návrat zostáva otvorený a má sledovať oba bajty, `0108` a ciele default procedúry.

## 3. Rozšírené message mapy

Koreňovú množinu som rozšíril z getterov, ktorých návraty ukazujú na štruktúru mapy. Výsledok je **20 jedinečných map records**, **173 neprázdnych entries** a **159 jedinečných handlerov**. Predtým bolo 13/131/118. Pribudlo sedem máp a 42 entries; iba dva ďalšie ciele nemali samostatný vstup: `1000:859E`, `1000:CAF8`.

| Nová mapa DS | Base | Entries | Počet |
|---|---|---|---:|
| `05E2` | `05A4` | `1000:7C9F` | 6 |
| `05F8` | `05E2` | `1000:7C4E` | 6 |
| `0614` | `05E2` | `1000:7CEF` | 6 |
| `0670` | `064A` | `1000:43EE` | 1 |
| `07CC` | `07A4` | `1008:015A` | 3 |
| `07E6` | `07CC` | `1000:AC96` | 19 |
| `0816` | `064A` | `1000:7D62` | 1 |

`verify_message_maps_extended.py` overuje všetky raw selectory/signatures/offsety, sentinely a **193 segmentových relokácií** (20 pointerov na tabuľky + 173 handler pointerov). Úplný význam všetkých handlerov sa týmto neuzatvára.

## 4. Inicializačný callback range a chýbajúce callee

V DS je doložený súvislý rozsah **`204A–20CD` s 33 far pointermi**. Na `1008:38BB/38BE` sa nastaví `SI=204Ah`, `DI=20CEh`; na `38C1` sa volá helper `3994`.

Helper implementuje:

```text
while unsigned(SI) < unsigned(DI):
    DI -= 4
    if word[DI] != 0 or word[DI+2] != 0:
        far_call([DI])
```

Pre daný range teda ide v presnom poradí od entry **`1048:20CA` → `1000:7C48`** až po **`1048:204A` → `1010:0458`**. Všetkých 33 selector wordov je podopretých NE type-2 reťazcami; poradie sa neodvodzuje zo sortovania mien ani adries funkcií.

Príklad posledného callbacku: `1010:0458` volá `0026`, potom `0448`. `0026` odovzdá adresu globálneho objektu `23E4` do `0006`; `0448` odovzdá far pointer `1010:043E` do `1008:73CC`. To podopiera inicializačný charakter cesty; presný širší kontrakt registrácie/terminácie a pomenovanie všetkých objektov zostávajú Partial.

Po obnovení 33 callback vstupov som sledoval chýbajúce ciele priamych callov z vlastnených funkcií. Dva priechody doplnili **98 + 13 = 111 ďalších vstupov**. Skript nevstupuje do EXTERNAL bloku, neprepisuje definované dáta a nevytvára nový vstup v tele už existujúcej funkcie. Každý nový vstup má uložený source call a source owner. Ich pomenovanie `CANDIDATE_CALL_*` nepredstiera úplnú sémantiku alebo správny ABI.

## Pokrytie

| Metrika | Pred prechodom 5 | Po prechode 5 |
|---|---:|---:|
| Interné funkčné vstupy | 1 389 | 1 535 |
| Dokončené interné dekompilácie | 1 389 | 1 535 |
| EXTERNAL položky | 310 | 310 |
| Inštrukčné bajty | 158 055 | 159 467 |
| Definované dáta v code segmentoch | 7 445 | 7 905 |
| Neklasifikované bajty | 4 188 | 2 316 |

Prírastok 146 vstupov je 2 mapové ciele + 33 callbackov + 111 callee. Čistý prírastok code dát je 460 B, inštrukcií 1 412 B. Niektoré nové vstupy už mali disassemblované telo bez samostatnej funkcie. Zvyšných 2 316 B zahŕňa aj možné tabuľky, stringy a padding, preto sa nemajú označiť za rovnaký objem chýbajúceho kódu.

## Reprodukcia a ďalší test

- `verify_message_maps_extended.py`: pôvodné bajty/relokácie pre 20 máp.
- `verify_init_table.py`: raw hranice a helper, 33 pointerov a explicitné poradie; baseline funkcií je uložený prechod 4.
- `N3DRecoverDirectCalls.java`: zaznamenaná obnova v dvoch rounds; kompletný TSV má 111 source-callee väzieb.
- `win110_capture_model.py`: raw inštrukčné guardy, import `KERNEL!__A000H`, šesť planar modelových testov a lineárna vetva.
- `focus_direct_reachability.json`: presný obmedzený graf a výslovné limity negatívneho výsledku.

Ďalší rozlišujúci runtime dôkaz má zachytiť `46F8` s DS/ES, DF, VGA read mode a read-map registrom, oba page base varianty a cieľových 64 000 B. Samostatne treba zmerať DAC/paletu a porovnať game frame s modernou implementáciou. Focus-loss trace musí sledovať reentrantné Windows správy, nie iba priame cally.

**Istota:** High pre rozsahy, lokálne inštrukcie, selector import, callback poradie a podmienený adresový model; Medium pre širšie frameworkové významy; Unknown pre úplnú sémantiku, runtime fokus a pixelovú/tickovú 1:1 paritu.
